from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_aws import ChatBedrock
import boto3
from app.utilities import vector_store as vs
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

boto3_bedrock = boto3.client("bedrock")
model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}
modelId = "anthropic.claude-3-sonnet-20240229-v1:0" #"anthropic.claude-v2"
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
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    #get_session_history,
    lambda session_id: DynamoDBChatMessageHistory(table_name='SessionTable', session_id=session_id),
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

def contexctual_chat_invoke(request):
    result = chain_with_history.invoke({"input": request.query},config={"configurable": {"session_id": request.session_id}})
    #print("contextual output result", result)
    return result