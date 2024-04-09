from ..agent.agent_property import Agent


class ManagerAgent(Agent):
    def __init__(self, name, description, model, prompt, api_base, ai_chain, long_term_memory, short_term_memory):
        super(ManagerAgent, self).__init__(name, description, model, prompt, api_base, ai_chain, long_term_memory,
                                           short_term_memory)


class ToolAgent(Agent):
    def __init__(self, name, description, model, prompt, api_base, ai_chain, long_term_memory, short_term_memory):
        super(ToolAgent, self).__init__(name, description, model, prompt, api_base, ai_chain, long_term_memory,
                                        short_term_memory)
