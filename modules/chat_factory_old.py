import re
import json
from langchain_google_community import GoogleSearchAPIWrapper
from config import Config
from openai import AssistantEventHandler, OpenAI
from modules.google_search_old import PDFSearcherDownloader
import logging
import os

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from modules.vectorstore_factory import FaissVectorStore

websearch = PDFSearcherDownloader()
# class EventHandler(AssistantEventHandler):
#     @override
#     def on_text_created(self, text) -> None:
#         print(f"\nassistant > ", end="", flush=True)
#
#     @override
#     def on_tool_call_created(self, tool_call):
#         print(f"\nassistant > {tool_call.type}\n", flush=True)
#
#     @override
#     def on_message_done(self, message) -> None:
#         # print a citation to the file searched
#         message_content = message.content[0].text
#         annotations = message_content.annotations
#         for index, annotation in enumerate(annotations):
#             message_content.value = message_content.value.replace(
#                 annotation.text, f"[{index}]"
#             )
#         print(message_content.value)


class ChatWithAssistant:
    def __init__(self):
        """This function will load the assistant id and state variables
        required for continuous contextual chat with the assistant"""
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.assistant = Config.ASSISTANT_ID

    def create_thread(self,message_file=None):
        messages = [
            {
                "role": "user",
                "content": "Hi"
            }
        ]
        if message_file:
            messages[0]["attachments"]= [
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ],
        return self.openai_client.beta.threads.create(messages = messages).id

    def get_assistant(self):
        my_assistant = self.openai_client.beta.assistants.retrieve(self.assistant)
        return my_assistant
    def get_thread(self,thread_id):
        thread = self.openai_client.beta.threads.retrieve(thread_id)
        return thread
    def create_files(self,filename):
        file = self.openai_client.files.create(
            file=open(filename, "rb"),
            purpose="assistants"
        )
        return file
    def create_vectorstore(self):
        vector_store = self.openai_client.beta.vector_stores.create(name="Documents")
        return vector_store

    def upload_files_to_vectorstore(self,vector_store,file_streams):
        file_batch = self.openai_client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )
        return file_batch

    def add_vector_store(self,vector_store):
        assistant = self.openai_client.beta.assistants.update(
            assistant_id=self.assistant,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        return assistant

    def modify_assistant(self, instructions):
        my_updated_assistant = self.openai_client.beta.assistants.update(
            self.assistant,
            instructions=instructions
            # name="HR Helper",
            # tools=[{"type": "file_search"}],
            # model="gpt-4o"
        )
        return my_updated_assistant

    def delete_thread(self,thread_id):
        return self.openai_client.beta.threads.delete(thread_id)
    # def run_assistant_stream(self,message):
    #     # Create messages on the thread id
    #     self.openai_client.beta.threads.messages.create(
    #         thread_id=self.thread.id,
    #         role="user",
    #         content=message
    #         )
    #     with self.openai_client.beta.threads.runs.stream(
    #             thread_id=self.thread.id,
    #             assistant_id=self.assistant,
    #             event_handler=EventHandler()
    #     ) as stream:
    #         stream.until_done()
    #         return stream._current_message_content.text.value

    def submit_tool_outputs(self, thread,run):
        # Define the list to store tool outputs
        tool_outputs = []
        logging.info(run.required_action.submit_tool_outputs.tool_calls)

        # Loop through each tool in the required action section
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "web_search":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": websearch.search_and_download(tool.function.arguments)
                })

        run = self.openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        logging.info("Tool outputs submitted successfully.")

    def run_assistant(self, thread,message):
        # Create messages on the thread id
        self.openai_client.beta.threads.messages.create(
            thread_id=thread,
            role="user",
            content=message,
            metadata={"user_id":"user"}
        )

        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=thread,
            assistant_id=self.assistant,
            instructions="You are Jack. Look at the context and question." #Check if the answer is correct and then give an answer to the user's question"
        )
        if run.status == 'requires_action':
            self.submit_tool_outputs(thread,run)
        # elif run.status == 'completed':
        #     messages = self.openai_client.beta.threads.messages.list(
        #         thread_id=thread
        #     )
            # Reload messages and check for the latest messages
            messages = list(
                self.openai_client.beta.threads.messages.list(thread_id=thread, run_id=run.id))

            message_content = messages[0].content[0].text
            annotations = message_content.annotations
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            return message_content.value
        else:
            return(run.status)



# class Completions:
#     def __init__(self):
#         """This function will load the assistant id and state variables
#         required for continuous contextual chat with the assistant"""
#         self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
#
#     def generate_response(self, context):
#         """This function will call the completions api
#         to generate response for the questions asked"""
#         response = self.openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=context
#         )
#
#         # Extract the content of response
#         cont = response.choices[0].message.content
#
#         # Return the content
#         return cont
#
#     def extract_content(self, input_string, pattern):
#         match = re.search(pattern, input_string, re.DOTALL)
#
#         if match:
#             return match.group(1)
#         else:
#             return None
# def websearch(question,company):
#     """Search the web"""
#     search = GoogleSearchAPIWrapper(google_api_key=Config.GOOGLE_API_KEY,
#                                         google_cse_id=Config.GOOGLE_CSE_ID)
#     response = search.run(f"Find the resorces required to find the answer to the question:{question} about the company:{company}")
#     return response
