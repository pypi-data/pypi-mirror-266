from .agent.agent_property import ExternalAPI
import requests
import base64
import shutil
import tempfile
import json
from functools import reduce
from .function_module.rag_handler import DBGetter, DataRetriever


class ConvertTool:
    @staticmethod
    def json2spl(jsonData):
        result = []
        for item in jsonData:
            section_type = "@" + item["sectionType"]
            sub_sections = []

            for sub_item in item["section"]:
                sub_section_type = "@" + sub_item["subSectionType"]
                content = sub_item["content"]

                if sub_section_type == "@Name":
                    # Handling "Name" differently by appending the content directly to the section type
                    section_type += f" {content}"
                else:
                    if isinstance(content, list):
                        temp_content = []
                        for item in content:
                            temp_content.append(sub_section_type + " " + item)
                        content = '\n    '.join(temp_content)
                    elif isinstance(content, dict):
                        # Formatting the dictionary content with line breaks, avoiding backslashes in f-strings
                        formatted_content = []
                        for key, value in content.items():
                            # Indenting each line for 'input' and 'output'
                            if key in ['input', 'output']:
                                indented_value = '\n'.join(['            ' + line for line in value.split('\n')])
                            else:
                                indented_value = value
                            formatted_content.append(f"        @{key} {{\n{indented_value}\n        }}")
                        content = '\n'.join(formatted_content)

                    if '@input' in content:
                        sub_sections.append(f"    {sub_section_type} {{\n{content}\n    }}")
                    elif sub_section_type == '@Format':
                        sub_sections.append(f"    {sub_section_type} {{\n{content}\n    }}")
                    else:
                        sub_sections.append(f"    {content}\n    ")
            result.append(f"{section_type} {{\n" + "\n".join(sub_sections) + "}")
        Spl_prompt = "\n".join(result)
        return Spl_prompt

    @staticmethod
    def SPL2JSON():
        pass


class ReadTool:
    @staticmethod
    def read_json_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def read_txt_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class ExternalAPIHandleUtility():
    def __init__(self, API):
        self.API = API

    def run(self):
        API_URL = self.API.server_url

    #=============输入处理================
        if self.API.header_info["Content-Type"] == "application/json":
            data = json.dumps(self.API.api_parameter)

        elif self.API.header_info["Content-Type"] == "application/octet-stream":
            with open(self.API.api_parameter["FilePath"],'rb') as file:
                data = file.read()

    #========发送请求===================

        response = requests.post(API_URL,headers=self.API.header_info,data=data)
        Json_Result = response.json()
        Result = reduce(lambda d, k: d[k], self.API.return_info["Parse_Path"], Json_Result)
    #======处理======
        if self.API.return_info["ReturnValue-Type"] == "Text":
            return Result
        elif self.API.return_info["ReturnValue-Type"] == "Url":
            # with requests.get(Result, stream=True) as r:
            #     r.raise_for_status()
            #     with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            #         with open(temp_file.name, 'wb') as f:
            #             shutil.copyfileobj(r.raw, f)
            return Result
        elif self.API.return_info["ReturnValue-Type"] == "Speech_Url":
            with requests.get(Result, stream=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    with open(temp_file.name, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            return temp_file.name
        elif self.API.return_info["ReturnValue-Type"] == "Image_Binary_Data":
            with tempfile.NamedTemporaryFile(delete=False,suffix=".png") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write(Result)
            return temp_filename
        elif self.API.return_info["ReturnValue-Type"] == "Speech_Binary_Data":
            with tempfile.NamedTemporaryFile(delete=False,suffix=".wav") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write(Result)
            return temp_filename
        elif self.API.return_info["ReturnValue-Type"] == "Image_B64_Data":
            data = base64.b64decode(Result)
            with tempfile.NamedTemporaryFile(delete=False,suffix=".png") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write(data)
            return temp_filename
        elif self.API.return_info["ReturnValue-Type"] == "Speech_B64_Data":
            data = base64.b64decode(Result)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_filename = temp_file.name
                temp_file.write(data)
            return temp_filename


class DataUsageUtility:
    def __init__(self, def_view, db_getter, data_retriever):
        self.def_view = def_view
        self.db_getter = db_getter
        self.data_retriever = data_retriever

    def get_data(self):
        # self.data_retriever.search_expression_elements[0]["Logical_Operators"] = "AND"
        # self.data_retriever.search_expression_elements = self.def_view[
        #                                                   "SearchExpression_Elements"] + self.data_retriever.search_expression_elements
        Result = self.data_retriever.execute(self.def_view)
        return Result


class RefProcessUtility():
    def __init__(self, variables_space, views_space):
        self.variables_space = variables_space
        self.views_space = views_space

        self.ref_set = {
            "RefData": DataUsageUtility,
            "RefGuardrail":GuardrailUtility,
            "RefCheck": CheckUtility,
            "RefAPI":ExternalAPIHandleUtility,
            "NativeAPI": ExternalAPIHandleUtility
        }


    def set_ref_utility(self, reference):
        if reference["RefPackage"] in self.ref_set:
            if reference["RefPackage"] == "RefData":
                ref_utility = self.ref_set[reference["RefPackage"]](
                    def_view=self.views_space[reference["RefInfo"]["ViewName"]],
                    db_getter=DBGetter(),
                    data_retriever=DataRetriever(
                        valid_fields=reference["RefInfo"]["DataManagerParameter"]["Valid_Field"],
                        search_expression_elements=reference["RefInfo"]["DataManagerParameter"]["SearchExpression_Element"],
                        output_format=reference["RefInfo"]["DataManagerParameter"]["Output_Form"]))
                return ref_utility

            elif reference["RefPackage"] == "RefAPI" or reference["RefPackage"] == "NativeAPI":
                api = ExternalAPI(
                    api_name=reference["RefProperties"]["Name"],
                    description=reference["RefProperties"]["Description"],
                    server_url=reference["RefProperties"]["Server_Url"],
                    header_info=reference["RefProperties"]["Header_Info"],
                    return_info=reference["RefProperties"]["Return_Info"],
                    api_parameter=reference["RefProperties"]["API_Parameter"])
                ref_utility = self.ref_set[reference["RefPackage"]](API=api)
                return ref_utility

            elif reference["RefPackage"] == "RefGuardrail":
                ref_utility = self.ref_set[reference["RefType"]]()
                ref_utility.target_variable = reference["RefObject"]
                ref_utility.will_execute_guardrail_type = reference["RefInfo"]["guardrail_type_name"]
                return ref_utility

            elif reference["RefPackage"] == "RefCheck":
                ref_utility = self.ref_set[reference["RefType"]]()
                ref_utility.will_execute_check = reference["RefInfo"]["check_type_name"]
                return ref_utility

    def execute_ref(self, ref_utility):
        if isinstance(ref_utility, DataUsageUtility):
            result = ref_utility.get_data()
            return result
        elif isinstance(ref_utility, GuardrailUtility):
            guardrail = ref_utility.guardrail_set.get(ref_utility.will_execute_guardrail_type)
            if guardrail:
                guardrail()
        elif isinstance(ref_utility, CheckUtility):
            check = ref_utility.check_set.get(ref_utility.will_execute_check_type)
            if check:
                check()
        elif isinstance(ref_utility, ExternalAPIHandleUtility):
            result = ref_utility.run()
            return result


class GuardrailUtility():
    def __init__(self):
        self.GuardrailSet = {
            "AnonymityGuardrail": self.AnonymiryGuardrail
        }
        self.WillExcuteGuardrailType = ""
        self.TargetVariable = ""
    def AnonymiryGuardrail(self):
        self.TargetVariable.ShowValue = "*******"


class CheckUtility():
    def __init__(self):
        self.CheckSet = {
            "CheckIfValueNull": self.CheckIfValueNull
        }
        self.WillExcuteCheckType = ""
        self.TargeVariable = ""
    def CheckIfValueNull(self):
        if self.TargeVariable.TrueValue != None:
            return True
        return False

