from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import Config
from openai import OpenAI as AI
#client = OpenAI()

class KnowledgeRetriver:
    def __init__(self):
        self.llm = OpenAI()
        self.prompt_template = """
                                Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
                                <context>
                                {context}
                                </context

                                Question: {question}

                                Assistant:"""

    def retreive_context(self,vectorstore_faiss,question):
        PROMPT = PromptTemplate(
            template=self.prompt_template, input_variables=["context", "question"]
        )
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore_faiss.as_retriever(
                search_type="similarity", search_kwargs={"k": 3}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        return qa.invoke(question)

class OpenAIRetriver:
    def __init__(self):
        self.llm = AI()
        self.prompt_template = """
                                    Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
                                    <context>
                                    {context}
                                    </context

                                    Question: {question}

                                    Assistant:"""
    def retreive_context(self,question):
        response = self.llm.chat.completions.create(
            model="o1",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        return response
