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


class CustomDynamoDBChatMessageHistory(DynamoDBChatMessageHistory):
    def add_ai_message(self, content, response_metadata=None):
        """
        Add an AI message with response metadata.
        """
        ai_message = AIMessage(
            content=content,
            response_metadata=response_metadata or {}
        )
        self.add_message(ai_message)  # Save the message to DynamoDB


# Configure the Boto3 client with retries and backoff
config = Config(
    retries={
        'max_attempts': 10,  # Number of retry attempts
        'mode': 'adaptive'   # Adaptive backoff strategy
    },
    region_name='us-east-1'
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
        store[session_id] = DynamoDBChatMessageHistory(table_name='SessionTable', session_id=session_id)
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

    dynamo_history = CustomDynamoDBChatMessageHistory(table_name="SessionTable", session_id=request.session_id)

    # Add the user query to the history manually
    user_message = HumanMessage(
        content=request.query,
        additional_kwargs={"query_metadata": {"session_id": request.session_id}}
    )
    dynamo_history.add_message(user_message)  # Add user message

    input_token_count  = count_anthropic_tokens(user_message.content)

    print(f"Input Tokens without Histroy: {input_token_count}")

    chat_history = get_session_history(session_id=request.session_id)
    #print("chat_history: ", chat_history)

    combined_text = print_chat_history(chat_history)

    input_token_count = count_anthropic_tokens(combined_text)

    print(f"Input Tokens of History: {input_token_count}")

    result = chain_with_history.invoke({"input": request.query},config={"configurable": {"session_id": request.session_id}})
   
     # Token counting for output
    output_token_count = count_anthropic_tokens(result["answer"])
    print(f"Output Tokens: {output_token_count}")

    #print("contextual output result", result)
    
    information_sources=format_ai_response_with_metadata(result)
    
    #print("Information Sources: ", information_sources)

    # Add the AI response to the history with metadata
    dynamo_history.add_ai_message(
        content=information_sources["content"],
        response_metadata={"sources": information_sources["metadata"]}
    )
    
    print("before Returning the chat response")
    
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
    if isinstance(chat_history, DynamoDBChatMessageHistory):
        messages = chat_history.messages
    else:
        raise ValueError("chat_history must be an instance of DynamoDBChatMessageHistory")

    combined_text = ""
    for message in messages:
        if hasattr(message, "type"):
            role = message.type.capitalize()
        else:
            role = "Unknown"

        content = getattr(message, "content", "No content")
        print(f"{role}: {content}")
        combined_text += f"{content}\n"

    return combined_text