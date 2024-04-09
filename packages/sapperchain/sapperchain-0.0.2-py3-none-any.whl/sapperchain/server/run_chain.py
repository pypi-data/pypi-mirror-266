from collections import deque
from ..agent import ToolAgent, ManagerAgent
from ..agent.agent_property import ExternalAPI, LongTermMemory, ShortTermMemory, Request
from ..function_module.agent_executor import VariablesManager, PrePromptHandle, IExtractVariables, \
    PromptHandle, PostPromptHandle, UnitExecutor, ToolAgentExecutor, MagAgentExecutor, RequestSplitter, APIDispatcher
from ..function_module.memory_manager import MemoryManagerWindow
from ..function_module.rag_handler import DataViewDefiner
from ..tool import RefProcessUtility, ExternalAPIHandleUtility


class RunChain:
    def __init__(self, agent, agent_executor) -> None:
        self.agent = agent
        self.agent_executor = agent_executor

    @classmethod
    def create(cls, agent_data):
        prompt = agent_data['agent_form']
        chain = agent_data['agent_chain']
        api_base = {}
        for api in agent_data["api_base"].values():
            api_base[api["API_Name"]] = ExternalAPI(
                api_name=api["API_Name"],
                description=api["Description"],
                server_url=api["Server_Url"],
                header_info=api["Header_Info"],
                return_info=api["Return_Info"],
                api_parameter=api["API_Parameter"])

        agentModel = ExternalAPI(api_name="Chatbot",
                                 description="",
                                 server_url="https://api.rcouyi.com/v1/chat/completions",
                                 header_info={'Content-Type': 'application/json',
                                              "Authorization": "Bearer sk-VRZJipcSsramiTy30709BfAfC43c432cA7A32036Cd6938Fd"},
                                 return_info={"ReturnValue-Type": "Text",
                                              "Parse_Path": ["choices", 0, "message", "content"]},
                                 api_parameter={"model": "gpt-3.5-turbo",
                                                "messages": [{"role": "system", "content": ""},
                                                             {"role": "user", "content": "${TemporaryVariable}$"}]})

        if agent_data['agent_type'] == "ToolAgent":
            agent = ToolAgent(
                model=agentModel,
                name="Sapper",
                description="",
                prompt=prompt,
                api_base=api_base,
                ai_chain=deque(chain),
                long_term_memory=LongTermMemory(),
                short_term_memory=ShortTermMemory(),
            )
        else:
            agent = ManagerAgent(
                model=agentModel,
                name="Sapper",
                description="",
                prompt=prompt,
                api_base=api_base,
                ai_chain=deque(chain),
                long_term_memory=LongTermMemory(),
                short_term_memory=ShortTermMemory(),
            )
        data_view_definer = DataViewDefiner(storage_loc=agent.long_term_memory.views, data_loader=None)
        for view in agent_data["view_base"].values():
            data_view_definer.define_data(
                view["file_path"],
                view["data_source"],
                view["relation_db"],
                view['vector_db'],
                view['valid_field'],
                view['search_expression'],
                view['defView_name'],
                view['storage_form'],
                view['output_form'])

        variable_base = agent_data['variable_base']

        VariableManager = VariablesManager(database=variable_base,
                                           variable_matcher=IExtractVariables().extract_variables)

        pre_prompt_handle = PrePromptHandle(variable_matcher=IExtractVariables().extract_variables,
                                            variables_space=agent.short_term_memory.variables)

        prompt_handle = PromptHandle(
            ref_process_utility=RefProcessUtility(variables_space=agent.short_term_memory.variables,
                                                  views_space=agent.long_term_memory.views))

        post_prompt_handle = PostPromptHandle(variables_space=agent.short_term_memory.variables)
        unit_executor = UnitExecutor(pre_prompt_handle, prompt_handle, post_prompt_handle)
        if agent_data['agent_type'] == "ToolAgent":
            agent_executor = ToolAgentExecutor(VariableManager, unit_executor)
        else:
            Request_Splitter = RequestSplitter(external_api_handle_utility=ExternalAPIHandleUtility(agent.model))
            API_Dispatcher = APIDispatcher(api_base, external_api_handle_utility=ExternalAPIHandleUtility(agent.model))
            Memory_Manager = MemoryManagerWindow(agent.long_term_memory, agent.short_term_memory, agent.model)
            agent_executor = MagAgentExecutor(Request_Splitter, API_Dispatcher, VariableManager, unit_executor,
                                              Memory_Manager)

        return cls(agent, agent_executor)

    def run_chain(self, request):
        # try:
        response = self.agent_executor.get_result(self.agent, request)
        return response
        # except Exception as e:
        #     print(str(e))

