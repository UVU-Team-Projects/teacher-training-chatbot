from typing import Annotated, Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool, BaseTool
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate


# Langgraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.graph.state import CompiledStateGraph # Used for typing
from langgraph.checkpoint.memory import MemorySaver
# Project file imports
# try:
#     from app import crud, models
# except ImportError:
#     import crud, models
#     from database import SessionLocal
import torch
from colorama import Fore, Style
from dotenv import load_dotenv
import os
import time
import sys

import pprint

# Load environment variables
load_dotenv()

# Get tavily search api key
if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

class RAG:
    def __init__(self, tools: list[BaseTool]):
        self.tools = tools
        self.tool_node = ToolNode(self.tools)
        self.model = ChatOllama(model="deepseek-r1:14b").bind_tools(self.tools)

        self.vector_store = FAISS.from_texts(texts=None, embedding=self.embeddings)
        self.retriever = self.vector_store.as_retriever()

    # Define the function that determines whether to continue or not
    def should_continue(self, state: MessagesState) -> Literal["tools", END]: # type: ignore
        messages = state['messages']
        last_message = messages[-1]
        # print(last_message)
        # If the LLM makes a tool call, then we route to the "tools" node
        if last_message.tool_calls:
            return "tools"
        # Otherwise, we stop (reply to the user)
        return END
        

    def retrieve(self, state: MessagesState):
        '''Retrieve relevant information to use'''
        context = self.retriever.get_relevant_documents(state['messages'])
        return {"context": context}
    
    # Define the function that calls the model
    def generate_response(self, state: MessagesState):
        '''Generate a response based on the context and user input'''
        prompt = ChatPromptTemplate.from_template("""
        You are a 2nd grader. Match your words and language to sound like one.
        The provided context can help you know how to act and respond. If the context doesn't contain relevant information, please decide how to best respond.
        The user is your teacher. Respond as if you are a 2nd grader talking to your teacher.
        Context: {context}
        Input: {input}                                    
        """)
        # Invoke model with the initial system message
        response = self.model.invoke({"context": state['context'], "input": state['messages'][-1].content}, prompt=prompt)
        return {"response": [response]}
    
    # def process_user_info(self, state: MessagesState):
    #     '''Pass initial user data and instructions into the agent'''
    #     message = state['messages'][-1].content
    #     if self.user:
    #         initial_message = [SystemMessage(content=f"You are a 2nd grader. Match your words and language to sound like one."
    #                                                 f"The provided context can help you know how to act and respond. If the context doesn't contain relevant information, please decide how to best respond. "
    #                                                 f"The user is your teacher. Respond as if you are a 2nd grader talking to your teacher."),
    #                             HumanMessage(content=message)]
    #     else:
    #         initial_message = [SystemMessage(content="You are a 2nd grader to help the user practice classroom managment. Match your words and language to sound like one. Respond and act correctly to the users input."),
    #                             HumanMessage(content=message)]
        
    #     # Invoke model with the initial system message
    #     response = self.model.invoke(initial_message)
    #     return {"messages": [response]}

    
    def ceate_agent(self):
        # Define a new graph
        workflow = StateGraph(MessagesState)
        # Add the nodes
        workflow.add_node('retrieve', self.retrieve)
        workflow.add_node('generate', self.generate_response)
        workflow.add_node('tools', self.tool_node)

        # Set the entrypoint as `retrieve`
        # This means that this node is the first one called
        workflow.set_entry_point("retrieve")
        workflow.add_edge('retrieve', 'generate')
        # Next call the agent and get ready

        # We now add a conditional edge
        workflow.add_conditional_edges(
            # First, we define the start node. We use `generate`.
            # This means these are the edges taken after the `generate` node is called.
            "generate",
            # Next, we pass in the function that will determine which node is called next.
            self.should_continue,
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        workflow.add_edge("tools", 'agent')

        # Initialize memory to persist state between graph runs
        checkpointer = MemorySaver()

        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable.
        # Note that we're (optionally) passing the memory when compiling the graph
        self.sousChef = workflow.compile(checkpointer=checkpointer)
        return self.sousChef

## Build the Agents tools
# @tool

tools = []
# add_recipe_to_db, get_pantry, add_to_pantry, remove_from_pantry

# Can build with these tools or call SousChef(tools) outside of this file to make a new agent with different tools
def llmPipeline() -> CompiledStateGraph:
    sousChef = RAG(tools).ceate_agent()
    return sousChef

# Function to print text with typing effect
def typing_effect(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Move to the next line after the text is printed

def main():
    ''' Setup the agent when ran locally '''
    # db = SessionLocal()
    sousChef: CompiledStateGraph = llmPipeline()
    print(Fore.GREEN + "Sous-Chef here! What can I help you with today? ")
    while True:
        print(Fore.RED + 'Enter "q" to quit.')
        query = input(Fore.GREEN + "Ask Sous-Chef: " + Style.RESET_ALL)
        if query == 'q':
            break
        # Use the Runnable
        final_state = sousChef.invoke(
            {"messages": [HumanMessage(content=query)]},
            config={"configurable": {"thread_id": 42}}
        )
        print(Fore.LIGHTBLUE_EX, end=" ")
        typing_effect(final_state["messages"][-1].content)
        print(Style.RESET_ALL)

if __name__ == "__main__":
    main()