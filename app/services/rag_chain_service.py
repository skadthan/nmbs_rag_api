import boto3
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_aws import ChatBedrock
from app.services.chat_session_history_service import ChatSessionHistory
from botocore.config import Config

# Set up the LLM
def get_llm():
    model_parameter = {"temperature": 0.0, "top_p": 0.5, "max_tokens_to_sample": 2000}
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    boto3_bedrock = boto3.client("bedrock",config=Config(region_name='us-east-1'))
    return ChatBedrock(
        model_id=model_id,
        client=boto3_bedrock,
        model_kwargs=model_parameter,
        beta_use_converse_api=True
    )

# Contextualized question prompt
def get_contextualized_question_prompt():
    contextualized_question_system_template = (
        "You are assisting in generating a comprehensive capabilities statement based on user queries and contextual information."
        "Given the chat history and the latest user query, rewrite the query to be a self-contained question,"
        "including any missing information required to answer it effectively. Ensure the question is framed professionally"
        "and aligns with the goal of constructing a detailed capabilities statement."
        "Do NOT answer the question—only reformulate it. If no reformulation is needed, return the query as is."
    )
    return ChatPromptTemplate.from_messages(
        [
            ("system", contextualized_question_system_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

# QA Prompt
def get_qa_prompt():
    qa_system_prompt = """You are an AI assistant tasked with providing detailed and relevant responses for generating a capabilities statement. \
    Using the retrieved documents and context, answer the user query as accurately and professionally as possible. \
    If the retrieved context does not contain sufficient information to answer the query, state: \
    "I do not have enough context to provide an answer."\

    Guidelines:\
    1. Provide answers that are factual and directly relevant to constructing a capabilities statement.\
    2. Use concise, professional language tailored to the capabilities domain.\
    3. Reference retrieved context explicitly when possible, such as contracts, proposals, or assessments.\

    {context}"""
    return ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

# Set up the RAG chain
def get_rag_chain(vectorstore):
    llm = get_llm()
    contextualized_question_prompt = get_contextualized_question_prompt()
    history_aware_retriever = create_history_aware_retriever(
        llm, vectorstore.as_retriever(), contextualized_question_prompt
    )
    qa_prompt = get_qa_prompt()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain

# Wrap RAG chain with message history
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatSessionHistory.get_session_history(self=ChatSessionHistory, user_session_id=session_id)
    return store[session_id]

def get_chain_with_history(rag_chain):
    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
