from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import AgentAction, AgentFinish, HumanMessage
from typing import List, Union
import re
import logging

logging.basicConfig(level=logging.INFO)

class CustomToolsAgent:
    def __init__(self):
        """
        Initialize the custom tools agent.
        """
        # Define your functions
        self.tools = self._define_tools()
        self.prompt = self._set_prompt()
        self.llm = ChatOpenAI(temperature=0)
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.output_parser = self._set_output_parser()
        self.agent = self._set_agent()
        self.agent_executor = self._set_agent_executor()

    def _define_tools(self):
        """
        Define which tools the agent can use to answer user queries.
        """
        def dummy_tool_func():
            """
            This is a placeholder function as func is a required parameter for Tool.
            """
            return "this function is just because I need to put something in func parameter"
        
        tools = [
            Tool(
                name="show_manga_list",
                func=dummy_tool_func,
                description="useful for when you need to answer questions related to manga",
                return_direct=True,
            ),
            Tool(
                name="show_anime_list",
                func=dummy_tool_func,
                description="useful for when you need to answer questions related to anime",
                return_direct=True,
            ),
            Tool(
                name="database_search",
                func=dummy_tool_func,
                description="useful for when you need to answer questions related to database knowledge, like books or something",
                return_direct=True,
            ),
            Tool(
                name="add_event_to_calendar",
                func=dummy_tool_func,
                description="useful for when you need to answer questions related to adding event to calendar",
                return_direct=True,
            ),
            Tool(
                name="retrieve_event_from_calendar",
                func=dummy_tool_func,
                description="useful for when you need to answer questions related to retrieving event from calendar(when user asks you about schedule for the day)",
                return_direct=True,
            ),
        ]
        return tools

    def _set_prompt(self):
        """
        Set up a prompt template.
        """
        template = """
        Complete the objective as best you can. You have access to the following tools:
        {tools}
        Use the following format:
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Thought: I now know the final answer
        Final Answer: Name of the tool. ONLY NAME OF TOOL TO USE.
        Begin!
        Question: {input}
        {agent_scratchpad}"""

        class CustomPromptTemplate(BaseChatPromptTemplate):
            template: str
            tools: List[Tool]

            def format_messages(self, **kwargs) -> str:
                intermediate_steps = kwargs.pop("intermediate_steps")
                thoughts = ""
                for action, observation in intermediate_steps:
                    thoughts += action.log
                    thoughts += f"\nObservation: {observation}\nThought: "
                kwargs["agent_scratchpad"] = thoughts
                kwargs["tools"] = "\n".join(
                    [f"{tool.name}: {tool.description}" for tool in self.tools]
                )
                kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
                formatted = self.template.format(**kwargs)
                return [HumanMessage(content=formatted)]

        prompt = CustomPromptTemplate(
            template=template,
            tools=self.tools,
            input_variables=["input", "intermediate_steps"],
        )

        return prompt

    def _set_output_parser(self):
        """
        Set up the output parser for the agent.
        """
        class CustomOutputParser(AgentOutputParser):
            def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
                final_answer_search = re.search("Final Answer: (\w+)", llm_output)

                if final_answer_search is not None:
                    final_answer = final_answer_search.group(1)
                    logging.info(f'Final Answer: {final_answer}')
                    return AgentFinish(
                        return_values={"output": final_answer},
                        log=llm_output,
                    )
                regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
                match = re.search(regex, llm_output, re.DOTALL)
                if not match:
                    raise ValueError(f"Could not parse LLM output: `{llm_output}`")
                action = match.group(1).strip()
                action_input = match.group(2)
                return AgentAction(
                    tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
                )

        return CustomOutputParser()

    def _set_agent(self):
        """
        Set up the agent for the application.
        """
        tool_names = [tool.name for tool in self.tools]
        agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            output_parser=self.output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names,
        )
        return agent

    def _set_agent_executor(self):
        """
        Set up the agent executor for the application.
        """
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent, tools=self.tools, verbose=True
        )
        return agent_executor

    def run(self, query: str):
        """
        Run the agent executor with the given query.
        """
        raw_result = self.agent_executor.run(query)
        final_answer = raw_result.split()[-1]  # Split the string into words and get the last one
        return final_answer
