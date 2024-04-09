import os
import re
from ..agent.agent_property import Variable
from abc import ABC
from ..agent.agent_property import Session
from ..tool import ReadTool, ConvertTool
import json


class AgentExecutor(ABC):
    def __init__(self, variables_manager, unit_executor):
        self.variables_manager = variables_manager
        self.unit_executor = unit_executor

    def save_variables(self, partial_spl_prompts, variables_space):
        for partial_spl_prompt in partial_spl_prompts:
            variables = self.variables_manager.extract_variable_names(str(partial_spl_prompt))
            for variable in variables:
                variable_info = self.variables_manager.get_variable_from_database(variable)
                self.variables_manager.save_variable(variable_info, variables_space)
        variable_info = self.variables_manager.get_variable_from_database("TemporaryVariable")
        self.variables_manager.save_variable(variable_info, variables_space)
        variable_info = self.variables_manager.get_variable_from_database("UserRequest")
        self.variables_manager.save_variable(variable_info, variables_space)

    def assign_user_input(self, input_user_info, variables_space):
        if input_user_info.file_path is not None:
            variables_space['UserRequest'].true_value = input_user_info.file_path
        elif input_user_info.text is not None:
            variables_space['UserRequest'].true_value = input_user_info.text

    def get_result(self, agent, request):
        res = ""
        self.save_variables(agent.ai_chain, agent.short_term_memory.variables)
        self.assign_user_input(request, agent.short_term_memory.variables)
        ai_chain_spl_prompt = agent.ai_chain
        while ai_chain_spl_prompt:
            unit = ai_chain_spl_prompt.popleft()
            res = self.unit_executor.get_res_from_unit(unit)
        return res


class ToolAgentExecutor(AgentExecutor):
    def __init__(self, agent_variable_initialization, unit_executor):
        super(ToolAgentExecutor, self).__init__(agent_variable_initialization, unit_executor)


class MagAgentExecutor(AgentExecutor):
    def __init__(self, request_splitter, api_dispatcher, variables_manager, unit_executor, memory_manager):
        super(MagAgentExecutor, self).__init__(variables_manager, unit_executor)
        self.request_splitter = request_splitter
        self.api_dispatcher = api_dispatcher
        self.memory_manager = memory_manager

    def get_result(self, agent, request):
        after_splitting_request = self.request_splitter.split_request(request)
        request.text = after_splitting_request["Context"]
        api_name = self.api_dispatcher.assign_api(after_splitting_request["Instruction"])
        if api_name == "None":
            exec_unit = self.prepare_chat_exec_unit(agent)
        else:
            api = agent.api_base[api_name]
            exec_unit = self.prepare_api_exec_unit(agent, api, api_name)
        # self.save_variables(agent.prompt, agent.short_term_memory.variables)
        self.assign_user_input(request, agent.short_term_memory.variables)

        res = self.unit_executor.get_res_from_unit(exec_unit)
        session = Session(request, res)
        self.memory_manager.add_session_into_memory(session)
        return res

    def prepare_chat_exec_unit(self, agent):
        analyze_message = [
            {"role": "system", "content": ConvertTool.json2spl(agent.prompt)},
            {"role": "user", "content": '${UserRequest}$'},
        ]
        agent.model.api_parameter["messages"] = analyze_message
        self.save_variables([agent.model.api_parameter], agent.short_term_memory.variables)
        return {
            "Input": "${UserRequest}$",
            "Output": "${TemporaryVariable}$",
            "References": [{
                "Output": "${TemporaryVariable}$",
                "Reference": {
                    "RefPackage": "NativeAPI",
                    "RefMethod": "ChatCompletion",
                    "RefProperties": self.extract_model_properties(agent.model)
                }
            }]
        }

    def prepare_api_exec_unit(self, agent, api, api_name):
        self.save_variables([api.api_parameter], agent.short_term_memory.variables)
        return {
            "Input": "${UserRequest}$",
            "Output": "${TemporaryVariable}$",
            "References": [{
                "Output": "${TemporaryVariable}$",
                "Reference": {
                    "RefPackage": "RefAPI",
                    "RefMethod": api_name,
                    "RefProperties": self.extract_api_properties(api)
                }
            }]
        }

    def extract_model_properties(self, model):
        return {
            "Name": model.api_name,
            "Description": model.description,
            "Server_Url": model.server_url,
            "Header_Info": model.header_info,
            "Return_Info": model.return_info,
            "API_Parameter": model.api_parameter
        }

    def extract_api_properties(self, api):
        return {
            "Name": api.api_name,
            "Description": api.description,
            "Server_Url": api.server_url,
            "Header_Info": api.header_info,
            "Return_Info": api.return_info,
            "API_Parameter": api.api_parameter
        }


class APIDispatcher:
    def __init__(self, api_base, external_api_handle_utility):
        self.api_base = api_base
        self.external_api_handle_utility = external_api_handle_utility
        self.base_path = os.path.dirname(__file__).replace('\\common', "").replace('/common', "").replace(
            "\\function_module", "").replace("/function_module", "")
        self.api_assignment_prompt = ReadTool.read_txt_file(
            self.base_path + "/prompt/RequestAnalyze/Decompose.txt")

    def assign_api(self, user_instruction):
        api_calls = ""

        for api_name, api in self.api_base.items():
            api_calls += f"\n        @Term {api.api_name}: {api.description}"

        analyze_prompt = self.api_assignment_prompt.replace("{External_API}", api_calls)
        for _ in range(3):  # 尝试最多三次解析用户指令
            analyze_message = [
                {"role": "system", "content": analyze_prompt},
                {"role": "user", "content": user_instruction},
            ]
            self.external_api_handle_utility.API.api_parameter["messages"] = analyze_message

            analyze_result = self.external_api_handle_utility.run()
            try:
                analyze_json_result = json.loads(analyze_result)
                return analyze_json_result["API_Call"]
            except json.JSONDecodeError:  # 明确捕获预期的异常类型
                continue


class RequestSplitter:
    def __init__(self, external_api_handle_utility):
        self.external_api_handle_utility = external_api_handle_utility
        self.base_path = os.path.dirname(__file__).replace('\\common', "").replace('/common', "").replace(
            "\\function_module", "").replace("/function_module", "")
        self.split_prompt = ReadTool.read_txt_file(
            self.base_path + "/prompt/RequestAnalyze/Spilt.txt")

    def split_request(self, request):
        for _ in range(3):  # 尝试最多3次
            decompose_message = [
                {"role": "system", "content": self.split_prompt},
                {"role": "user", "content": request.text},
            ]
            self.external_api_handle_utility.API.api_parameter["messages"] = decompose_message

            split_result = self.external_api_handle_utility.run()
            try:
                json_decomposed_request = json.loads(split_result)
            except json.JSONDecodeError:
                # 直接创建一个包含原始文本的字典，而不是尝试加载一个字符串
                json_decomposed_request = {"Context": request.text, "Instruction": request.text}
            return json_decomposed_request


class UnitExecutor:
    def __init__(self, pre_prompt_handle, prompt_handle, post_prompt_handle):
        self.pre_prompt_handle = pre_prompt_handle
        self.prompt_handle = prompt_handle
        self.post_prompt_handle = post_prompt_handle

    def get_res_from_unit(self, unit_info):
        res = ""
        unit_statements = unit_info["References"]
        for unit_statement in unit_statements:
            unit_statement = self.pre_prompt_handle.assign_variable_value_to_unit(unit_statement)
            res = self.prompt_handle.handle_prompt(unit_statement)
            self.post_prompt_handle.assign_res_to_output_variables(unit_statement["Output"], res)
        return res


class PrePromptHandle:
    def __init__(self, variable_matcher, variables_space):
        self.variable_matcher = variable_matcher
        self.variables_space = variables_space

    def assign_variable_value_to_unit(self, unit_statement):
        temp = str(unit_statement["Reference"])
        variables = self.variable_matcher(temp)
        for variable in variables:
            replace_target_pattern = fr"\${{{variable}}}\$(?:~\w+\{{[^}}]*\}})*(?:\/\w+)?"
            replace_target = sorted(list(set(re.findall(replace_target_pattern, temp))), key=len, reverse=True)
            for target in replace_target:
                if self.variables_space[variable].true_value != "":
                    temp = temp.replace(target, self.variables_space[variable].true_value)
        unit_statement["Reference"] = eval(temp)
        return unit_statement


class PromptHandle:
    def __init__(self, ref_process_utility):
        self.ref_process_utility = ref_process_utility

    def handle_prompt(self, unit_statement):
        ref_api_utility = self.ref_process_utility.set_ref_utility(unit_statement["Reference"])
        res = self.ref_process_utility.execute_ref(ref_api_utility)
        return res


class PostPromptHandle:
    def __init__(self, variables_space):
        self.variables_space = variables_space

    def assign_res_to_output_variables(self, variable_name, res):
        output_name_pattern = r"\$\{(.*?)\}\$"
        output_variable_name = re.findall(output_name_pattern, str(variable_name))[0]
        self.variables_space[output_variable_name].true_value = res


class VariablesManager:
    def __init__(self, database, variable_matcher):
        self.database = database
        self.variable_matcher = variable_matcher

    def extract_variable_names(self, content):
        variables = self.variable_matcher(content)
        return variables

    def get_variable_from_database(self, variable_name):
        try:
            ref_info = self.database[variable_name]
        except Exception as e:
            ref_info = {
                "name": variable_name,
                "usage": "Prompt",
                "data_type": "String",
                "true_value": "",
                "show_value": "",
                "references": []
            }
        return ref_info

    def save_variable(self, variable_info, variables_space):
        variable = Variable(variable_info["name"],
                            variable_info["usage"],
                            variable_info["data_type"],
                            variable_info["true_value"],
                            variable_info["show_value"],
                            variable_info["references"])
        variables_space[variable_info["name"]] = variable
        variable_loc = variables_space[variable_info["name"]]
        return variable_loc


class IExtractVariables:
    def __init__(self):
        self.pattern = r'\$\{(.*?)\}\$'

    def extract_variables(self, content):
        variables = set(re.findall(self.pattern, str(content)))
        return list(variables)








