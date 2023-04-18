import ast
import json
from langchain.chat_models import ChatOpenAI

from langchain.schema import HumanMessage, SystemMessage
from config import OPENAI_API_KEY
import datetime
from pathlib import Path

class LanguageExpert(dict):
    def __init__(self, name: str, system_message: str, description=None, example_input=None, example_output=None, model_params=None):
        self.name = name
        self.system_message = system_message
        self.description = description
        self.example_input = example_input
        self.example_output = example_output
        if model_params is None:
            model_params = {"model_name": "gpt-4", "temperature":  0.00, "frequency_penalty": 1.0, "presence_penalty":  0.5, "n": 1, "max_tokens":  512}
        self.model_params = model_params
        self.chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, **model_params)

    def serialize(self):
        return {
            "name": self.name,
            "system_message": self.system_message,
            "description": self.description,
            "example_input": self.example_input,
            "example_output": self.example_output,
            "model_params": self.model_params
        }

    def get_content(self):
        example_output = self.example_output
        example_input = self.example_input
        content = f'System Message: {self.system_message}\n\nExample Input: {example_input}\n\nExample Output: {example_output}'
        content  = SystemMessage(content=content)
        return content
    
    def generate(self, message):
        human_message = HumanMessage(content=message)
        request_message = [self.get_content(), human_message]
        response  = self.chat(request_message).content
        self.log(message, response)
        return response

    def log(self, message, response):
        now = datetime.datetime.now()
        filename = Path(f'./logs/{now.strftime("%Y-%m-%d_%H-%M-%S")}_{self.name}.txt')
        filename.parent.mkdir(parents=True, exist_ok=True)
        log = f'Expert Name:{self.name}\n\nReponse:{response}\n\noriginal message:{message}'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(log)
    
    def extract_texts_from_generations(self, generations):
        return [generation[0].text for generation in generations]

    def bulk_generate(self, messages:list):
        human_messages = [HumanMessage(content=message) for message in messages]
        request_messages = [[self.get_content(), human_message] for human_message in human_messages]
        responses = self.chat.generate(request_messages)
        responses = self.extract_texts_from_generations(responses.generations)
        self.log(messages, responses)
        return responses
    
    def __call__(self, message:str):
        return self.generate(message)

    def change_param(self, parameter_name, new_value):
        if parameter_name in ["model_name", "temperature", "frequency_penalty", "presence_penalty", "n", "max_tokens"]:
            self.__dict__["model_params"][parameter_name] = new_value
        else:
            self.__dict__[parameter_name] = new_value
        self.regen_chat()
    
    def regen_chat(self):
        self.chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, **self.model_params)
    
    def gen_from_file(self, infile):
        message = self.get_file_content(infile)
        return self(message)
    
    def get_file_content(self, infile):
        with open(infile, 'r', encoding='utf-8') as f:
            text = f.readlines()
            text = "".join(text)
        return text
    
class Manager(object):
    def __init__(self, infile=None):
        self.fname = infile
        if infile == None:
            self.experts = {}
        else:
            self.load(infile)

    def add_expert(self, expert: LanguageExpert):
        self.experts[expert.name] = expert.serialize()
        if self.fname != None:
            self.save(self.fname)

    def delete_expert(self, expert_name: str):
        del self.experts[expert_name]

    def __getitem__(self, key:str) -> dict:
        return self.create_expert(key)

    def get_expert(self, expert_name: str):
        return LanguageExpert(**self.experts[expert_name])

    def save(self, outfile):
        with open(outfile, 'w') as f:
            json.dump(self.experts, f)

    def load(self, infile):
        with open(infile, 'r') as f:
            self.experts = json.load(f)

def gen_prompt(manager):
    generator = manager.get_expert('PromptGeneratorV2')
    idea = manager.get_expert('PromptIdeaExpander')
    expandedIdea = idea.gen_from_file('./promptpad.txt')
    expandedIdea = f'Generate a prompt from the following proposal:\n{expandedIdea}'
    formattedPrompt = generator(expandedIdea)
    prompt = ast.literal_eval(formattedPrompt)
    expert = LanguageExpert(**prompt)
    manager.add_expert(expert)
    print(expert.name)
    print(expert.get_content().content)
    
def improve(target, manager):
    improver = manager.get_expert('PromptImproverV2')
    suggestion = manager.get_expert('PromptSuggestionIncorporator')
    content  = target.get_content().content
    recommendations = improver(content)
    base = str({k:target.__dict__[k] for k in ('name', 'system_message', 'description', 'example_input', 'example_output') if k in target.__dict__})
    prompt  = f'Base Prompt:\n{base}\n\n{recommendations}'
    new_expert = suggestion(prompt)
    print(recommendations)
    try:
        new_expert = ast.literal_eval(new_expert)
        new_expert = LanguageExpert(**new_expert)
    except:
        print('Failed to parse suggestion')
    print(new_expert)
    return new_expert