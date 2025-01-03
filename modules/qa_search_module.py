import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory
#from langchain_google_community import GoogleSearchAPIWrapper
from langchain.utilities import GoogleSearchAPIWrapper
from langchain_community.retrievers.web_research import WebResearchRetriever
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from config import Config


class QuestionAnsweringSystem:
    def __init__(self):
        # Initialize components
        self.chat_model = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True,
                                     openai_api_key=Config.OPENAI_API_KEY)
        self.vector_store = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory="./chroma_db_oai")
        self.conversation_memory = ConversationSummaryBufferMemory(llm=self.chat_model, input_key='question',
                                                                   output_key='answer', return_messages=True)
        self.google_search = GoogleSearchAPIWrapper()
        self.web_research_retriever = WebResearchRetriever.from_llm(vectorstore=self.vector_store, llm=self.chat_model,
                                                                    search=self.google_search, allow_dangerous_requests=True)
        self.qa_chain = RetrievalQAWithSourcesChain.from_chain_type(self.chat_model,
                                                                    retriever=self.web_research_retriever)

    def answer_question(self, user_input_question):
        # Query the QA chain with the user input question
        result = self.qa_chain({"question": user_input_question})

        # Return the answer and sources
        return result["answer"], result["sources"]


# Example usage:
# qa_system = QuestionAnsweringSystem()
# user_input_question = input("Ask a question: ")
# answer, sources = qa_system.answer_question(user_input_question)
# print("Answer:", answer)
# print("Sources:", sources)