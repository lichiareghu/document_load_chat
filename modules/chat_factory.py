import re
import json
from config import Config
# from modules.functions_factory import query_database
#from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from modules.vectorstore_factory import FaissVectorStore


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
        self.thread = ""
    def create_thread(self):
        self.thread = self.openai_client.beta.threads.create().id
        return self.thread

    def get_assistant(self):
        my_assistant = self.openai_client.beta.assistants.retrieve(self.assistant)
        return my_assistant

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

    def run_assistant(self, message):
        # Create messages on the thread id
        self.openai_client.beta.threads.messages.create(
            thread_id=self.thread,
            role="user",
            content=message,
            metadata={"user_id":"user"}
        )

        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=self.thread,
            assistant_id=self.assistant,
            instructions="You are Jack. Look at the context and question. Check if the answer is correct and then give an answer to the user's question"
        )
        if run.status == 'completed':
            messages = self.openai_client.beta.threads.messages.list(
                thread_id=self.thread
            )
            # Reload messages and check for the latest messages
            messages = list(
                self.openai_client.beta.threads.messages.list(thread_id=self.thread, run_id=run.id))

            message_content = messages[0].content[0].text
            annotations = message_content.annotations
            for index, annotation in enumerate(annotations):
                message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
                print(message_content.value)
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
