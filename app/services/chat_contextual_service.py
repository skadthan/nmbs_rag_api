from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_aws import ChatBedrock
import boto3
from app.utilities import vector_store as vs
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from botocore.config import Config
import json, re
from langchain.schema import AIMessage, HumanMessage
from boto3.dynamodb.conditions import Key
import uuid


class Message:
    def __init__(self, id, content, role, additional_kwargs=None, response_metadata=None):
        self.id = id
        self.content = content
        self.role = role  # 'user' or 'ai'
        self.additional_kwargs = additional_kwargs or {}
        self.response_metadata = response_metadata or {}



class CustomDynamoDBChatMessageHistory:
    def __init__(self, table_name, session_id):
        self.table_name = table_name
        self.session_id = session_id
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
        self.messages = self.fetch_messages()

    def fetch_messages(self):
        """
        Fetch all messages for the current session from DynamoDB.
        """
        response = self.table.get_item(Key={'SessionId': self.session_id})
        history = response.get('Item', {}).get('History', [])

        # Check if history exists and starts with a user message
        if not history or history[0].get('Role') != 'user':
            print("Session does not start with a user message.")
            return []
    
        return history


    def add_message(self, message):
        """
        Append a message to the chat history for the session in DynamoDB.
        """
        print("add message", message)
        self.table.update_item(
            Key={'SessionId': self.session_id},
            UpdateExpression="SET History = list_append(if_not_exists(History, :empty_list), :new_message)",
            ExpressionAttributeValues={
                ':empty_list': [],  # Initialize Messages attribute if it doesn't exist
                ':new_message': [{
                    'MessageId': str(uuid.uuid4()),  # Unique ID for the message
                    'Content': message.content,     # Message content
                    'Role': message.role,           # 'user' or 'ai'
                    'ResponseMetadata': message.response_metadata
                }]
            },
            ReturnValues="UPDATED_NEW"
        )


# Configure the Boto3 client with retries and backoff
config = Config(
    retries={
        'max_attempts': 10,  # Number of retry attempts
        'mode': 'adaptive'   # Adaptive backoff strategy
    }
)

# Initialize the Bedrock client
boto3_bedrock = boto3.client("bedrock", config=config)

model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}
modelId = "anthropic.claude-3-sonnet-20240229-v1:0" 
#"anthropic.claude-v2"
#anthropic.claude-3-sonnet-20240229-v1:0 (Previously Working)
#anthropic.claude-3-5-sonnet-20240620-v1:0
chatbedrock_llm = ChatBedrock(
    model_id=modelId,
    client=boto3_bedrock,
    model_kwargs=model_parameter, 
    beta_use_converse_api=True
)

# Initialize the RAG chain
vector_store = vs.get_es_vector_store()

contextualized_question_system_template = (
    "You are assisting in generating a comprehensive capabilities statement based on user queries and contextual information."
    "Given the chat history and the latest user query, rewrite the query to be a self-contained question,"
    "including any missing information required to answer it effectively. Ensure the question is framed professionally"
    "and aligns with the goal of constructing a detailed capabilities statement."
    "Do NOT answer the question—only reformulate it. If no reformulation is needed, return the query as is."
)

contextualized_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualized_question_system_template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    chatbedrock_llm, vector_store.as_retriever(), contextualized_question_prompt
)


qa_system_prompt = """You are an AI assistant tasked with providing detailed and relevant responses for generating a capabilities statement. \
Using the retrieved documents and context, answer the user query as accurately and professionally as possible. \
If the retrieved context does not contain sufficient information to answer the query, state: \
"I do not have enough context to provide an answer."\

Guidelines:\
1. Provide answers that are factual and directly relevant to constructing a capabilities statement.\
2. Use concise, professional language tailored to the capabilities domain.\
3. Reference retrieved context explicitly when possible, such as contracts, proposals, or assessments.\

{context}"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])
question_answer_chain = create_stuff_documents_chain(chatbedrock_llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

#- Wrap the rag_chain with RunnableWithMessageHistory to automatically handle chat history:
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    #print(session_id)
    if session_id not in store:
        store[session_id] = DynamoDBChatMessageHistory(table_name='UserChatSessionHistoryTable', session_id=session_id)
        #print("store[session_id]: ",store[session_id])
    return store[session_id]




chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: get_session_history(session_id=session_id),
    #lambda session_id: DynamoDBChatMessageHistory(table_name='SessionTable', session_id=session_id),
    #lambda session_id: CustomDynamoDBChatMessageHistory(table_name="SessionTable", session_id=session_id),
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer"
)

def contexctual_chat_invoke(request):

    dynamo_history = CustomDynamoDBChatMessageHistory(table_name="UserChatSessionHistoryTable", session_id=request.session_id)

    # Add the user query to the history manually
    user_message_id = str(uuid.uuid4())
    user_message = HumanMessage(
        id=user_message_id,
        content=request.query,
        role="user",
        additional_kwargs={"query_metadata": {"session_id": request.session_id}}
    )
    dynamo_history.add_message(user_message)  # Add user message
   
    # Fetch chat history for the session
    full_history = dynamo_history.fetch_messages()
    #print("dynamo_history.full_history: ",full_history)
    # Format the history into the input expected by `rag_chain`
    formatted_history = format_chat_history_for_chain(full_history)
    #print("dynamo_history.formatted_history: ",formatted_history)
    
    input_token_count  = count_anthropic_tokens(user_message.content)

    print(f"Input Tokens without Histroy: {input_token_count}")

    #chat_history = get_session_history(session_id=request.session_id)
    #print("chat_history: ", chat_history)

    combined_text = print_chat_history(full_history)

    input_token_count = count_anthropic_tokens(combined_text)

    print(f"Input Tokens of History: {input_token_count}")

    #result = chain_with_history.invoke({"input": request.query},config={"configurable": {"session_id": request.session_id}})
    #Combine the formatted history with the user query
    chain_input = {
        "input": request.query,
        "chat_history": formatted_history
    }
    #print("chain_input: ",chain_input)
    # Invoke the RAG chain with the constructed input
    result = rag_chain.invoke(chain_input)
    #print("AI result", result)
    
    # Token counting for output
    output_token_count = count_anthropic_tokens(result["answer"])
    print(f"Output Tokens: {output_token_count}")
    
    ai_message_id = str(uuid.uuid4())
    information_sources = format_ai_response_with_metadata(result)
    ai_message = Message(
        id=ai_message_id,
        content=information_sources["content"],
        role="ai",
        response_metadata={"sources": information_sources["metadata"], "token_counts": {"input": input_token_count, "output": output_token_count}}
    )
   
   
    #print("contextual output result", result)
    
    #information_sources=format_ai_response_with_metadata(result)
    
    #print("Information Sources: ", information_sources)

    # Add the AI response to the history with metadata
    #dynamo_history.add_ai_message(content=information_sources["content"],response_metadata={"sources": information_sources["metadata"]})
    #dynamo_history.add_ai_message(ai_message, response_metadata={"sources": information_sources["metadata"]})
    dynamo_history.add_message(ai_message)
    
    #print("before Returning the chat response")
    
    return result

def format_ai_response_with_metadata(ai_response):
    """
    Formats the AI response to include metadata (sources and page content).
    """
    context_documents = []

    # Iterate over the documents in "context"
    for doc in ai_response.get("context", []):
        # Ensure doc is not None and has the required attributes
        if doc is not None:
            metadata = getattr(doc, "metadata", {})  # Safely access metadata
            page_content = getattr(doc, "page_content", "")  # Safely access page_content

            # Append the structured metadata and page content to context_documents
            context_documents.append({
                "source": metadata.get("source", "unknown"),
                "page_content": page_content,
            })

    # Combine answer and metadata
    information_sources = {
        "content": ai_response.get("answer", "No answer provided."),  # Main response
        "metadata": context_documents,  # Extracted metadata
    }
    return information_sources


    # Define a dummy tokenizer function for illustration
def count_anthropic_tokens(text: str) -> int:
    """
    Approximates the number of tokens for Anthropic models like Claude.
    This is not exact but provides a close estimate.

    Args:
        text (str): Input text for which to count tokens.

    Returns:
        int: Approximate token count.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected a string but got {type(text)}")
    
    if not text:
        return 0

    # Split by word boundaries and include special characters
    word_tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    
    # Count newlines as separate tokens
    newline_tokens = text.count('\n')
    
    # Total token count
    total_tokens = len(word_tokens) + newline_tokens
    
    return total_tokens

def print_chat_history(chat_history):
    """
    Prints and processes the chat history content for human and AI messages.
    """
    if not isinstance(chat_history, list):
        raise ValueError("chat_history must be a list of message dictionaries")

    combined_text = ""
    for message in chat_history:
        role = message.get('Role', 'Unknown').capitalize()
        content = message.get('Content', 'No content')
        #print(f"{role}: {content}")
        combined_text += f"{content}\n"

    return combined_text

def format_chat_history_for_chain(messages):
    """
    Converts chat messages into a format suitable for `rag_chain`.
    """
    formatted_history = []
    for message in messages:
        if message['Role'] == 'user':
            formatted_history.append({"role": "user", "content": message['Content']})
        elif message['Role'] == 'ai':
            formatted_history.append({"role": "assistant", "content": message['Content']})
    return formatted_history


def generate_message_id():
    return str(uuid.uuid4())

def get_application_config(application_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('AIApplicationConfig')

    response = table.scan(
        FilterExpression=Key('ApplicationName').eq(application_id)
    )

    if 'Items' not in response or not response['Items']:
        raise ValueError(f"No configuration found for application: {application_id}")

    return response['Items'][0]
