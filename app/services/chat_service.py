from app.utilities.llm_client import get_bedrock_anthropic_claude_llm
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.load.dump import dumps
import json
import warnings
from app.utilities import vector_store as vs

warnings.filterwarnings('ignore')


def handle_chat(user_query: str) -> str:
    claudellm=get_bedrock_anthropic_claude_llm()
    prompt_template = """Human: Use the following pieces of context to provide a concise answer in English to the question at the end.
      If you don't know the answer, just say that you don't know, don't try to make up an answer. {context} Question: {question} Assistant:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    #docsearch = vs.get_es_vector_store()
    docsearch = vs.get_aoss_vector_store()
    qa_prompt = RetrievalQA.from_chain_type(
        llm=claudellm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )

    result = qa_prompt.invoke({"query": user_query})
    ai_response=dumps(result, pretty=True)
    ai_response=json.loads(ai_response)
    #print("ai_response: ",ai_response)
    return ai_response["result"]
    
