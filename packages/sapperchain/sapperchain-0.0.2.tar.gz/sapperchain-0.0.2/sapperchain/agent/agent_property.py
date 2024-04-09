from abc import ABC


class Agent(ABC):
    def __init__(self, name, description, model, prompt, api_base, ai_chain, long_term_memory, short_term_memory):
        self.name = name
        self.description = description
        self.model = model
        self.prompt = prompt
        self.api_base = api_base
        self.ai_chain = ai_chain
        self.long_term_memory = long_term_memory
        self.short_term_memory = short_term_memory


class LongTermMemory:
    def __init__(self):
        self.memory_depth = 10
        self.preference = ""
        self.views = {}


class ShortTermMemory:
    def __init__(self):
        self.memory_depth = 1
        self.chat_history = []
        self.variables = {}


class Variable:
    def __init__(self, name, usage, data_type, true_value, show_value, refs):
        self.name = name
        self.usage = usage
        self.data_type = data_type
        self.true_value = true_value
        self.show_value = show_value
        self.refs = refs


class ExternalAPI(ABC):
    def __init__(self, api_name, description, server_url, header_info, return_info, api_parameter):
        self.api_name = api_name
        self.description = description
        self.server_url = server_url
        self.header_info = header_info
        self.return_info = return_info
        self.api_parameter = api_parameter


class Request:
    def __init__(self, text, file_path=None):
        self.text = text
        self.file_path = file_path


class Session:
    def __init__(self, request, response):
        self.request = request
        self.response = response
