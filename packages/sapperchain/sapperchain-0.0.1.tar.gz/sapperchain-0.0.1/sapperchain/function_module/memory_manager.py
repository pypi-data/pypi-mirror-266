import os

from ..tool import ConvertTool, ReadTool
from abc import ABC, abstractmethod


class MemoryManager(ABC):
    def __init__(self, long_term_memory, short_term_memory, external_api_handle_utility):
        self.long_term_memory = long_term_memory
        self.short_term_memory = short_term_memory
        self.external_api_handle_utility = external_api_handle_utility

    @abstractmethod
    def add_session_into_memory(self, session):
        pass


class MemoryManagerCompression(MemoryManager):
    def __init__(self, long_term_memory, short_term_memory, external_api_handle_utility):
        super().__init__(long_term_memory, short_term_memory, external_api_handle_utility)

    def add_session_into_memory(self, session):
        if len(self.short_term_memory.chat_history) < self.short_term_memory.memory_depth:
            self.short_term_memory.chat_history.append(session)
        else:
            compress_prompt = f"{self.short_term_memory.chat_history}\nPlease chat histories the above into one sentence."
            compress_message = [
                {"role": "system", "content": "You are a Helpful assistant"},  # 这里需要换成SPL prompt
                {"role": "user", "content": compress_prompt},
            ]
            self.external_api_handle_utility.api.api_parameter["messages"] = compress_message
            compress_history = self.external_api_handle_utility.run()
            self.short_term_memory.chat_history.clear()
            self.short_term_memory.chat_history.append(compress_history)


class MemoryManagerWindow(MemoryManager):
    def __init__(self, long_term_memory, short_term_memory, external_api_handle_utility):
        super().__init__(long_term_memory, short_term_memory, external_api_handle_utility)
        self.base_path = os.path.dirname(__file__).replace('\\common', "").replace('/common', "").replace(
            "\\function_module", "").replace("/function_module", "")
        self.preference_prompt = ConvertTool.json2spl(ReadTool.read_json_file(self.base_path + "/prompt/Memory/Longmemory.json"))

    def add_session_into_memory(self, session):
        if len(self.short_term_memory.chat_history) < self.short_term_memory.memory_depth:
            self.short_term_memory.chat_history.append(session)
        else:
            if len(self.short_term_memory.chat_history) > self.long_term_memory.memory_depth:
                chat_history = ""
                for item in self.short_term_memory.chat_history:
                    chat_history += f"Q: {item.request.text}\nA: {item.response}"
                message = [
                    {"role": "system", "content": self.preference_prompt},
                    {"role": "user", "content": chat_history},
                ]

                self.external_api_handle_utility.api.api_parameter["messages"] = message
                preference_response = self.external_api_handle_utility.run()
                self.long_term_memory.preference = preference_response.strip()
            self.short_term_memory.chat_history.pop(0)
