from config import Config
from openai import OpenAI
from modules.google_search_old import PDFSearcherDownloader
import json
import os


def web_search(self, inp):
    search = PDFSearcherDownloader()
    return search.search_and_download(inp)

class ReportGenerator:
    def __init__(self,api_key=Config.OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key)
        path = "D:\portfolio\document_load_chat\\templates"
        steps_path = os.path.join(path,"steps.json")
        context_path = os.path.join(path,"context.txt")
        questions_path = os.path.join(path,"questions.json")
        with open(steps_path, "r") as file:
            self.data = json.load(file)

        with open(steps_path, "r") as file:
            self.context = json.load(file)

        with open(steps_path, "r") as file:
            self.questions = json.load(file)
        self.messages = []

    def build_tool(self):
        tool = [{
            "type": "function",
            "function":{
                "name": "web_search",
                "description": "Pass a search query to the google search and get some results and then download it",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "required": [
                        "query",
                        "count"
                    ],
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to put through to the search engine"
                        },
                        "count": {
                            "type": "integer",
                            "description": "The number of results to be returned to be saved. Defaults to a value of 10"
                        }
                    },
                    "additionalProperties": False
                }
            }
        }]
        return tool


    def build_prompt(self,role,message):
        return {"role": role, "content": message}

    def generate_response(self,model,prompt):
        completion = self.client.chat.completions.create(
            model="o1-preview",
            messages=prompt,
            tools=self.build_tool(),
            tool_choice="auto"
        )


rep =ReportGenerator()
prompt = f"You are an ESG expert. Your task is {rep.data['step_1']}. "
messages = [rep.build_prompt("Developer",prompt)]
messages.append(rep.build_prompt("User","The company name is solvay"))