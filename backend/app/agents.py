from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter
# from langchain_tavily import tavily_search
# from langchain.utilities import OpenWeatherMapAPIWrapper
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
# from langgraph import Node
from .tools import tavily_tool, weather_tool
from .config import GOOGLE_API_KEY

import logging

logging.basicConfig(level = logging.INFO)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    query:str
    decision:str
    answer:str



llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash", temperature = 0)


def weather_agent(state:AgentState):
    logger.info("Query received by the WeatherAgent")
    query = state["query"]
    city = query.split("in")[-1].strip() if "in" in query else "London"
    try:
        result = weather_tool.run(city)
    
    except Exception as e:
        return {"answer":f"Got the follwing error {e}"}
    
    return {"answer":result}

def web_search_agent(state:AgentState):

    logger.info("Query receieved by the WebSearchAgent")
    query = state["query"]
    logger.info("Making call to the tavily search tool")
    results = tavily_tool.invoke({"query":query})
    results = results["results"]
    all_text = "".join([r["content"] for r in results if r["content"]])
    logger.info("Creating Chunks")
    splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 100)
    
    docs = splitter.create_documents([all_text])

    map_prompt = ChatPromptTemplate.from_messages([
        ("human", "Write a concise summary of the following in 100 words:\n\n{context}")
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    summaries = [map_chain.invoke({"context": d.page_content}) for d in docs]

    reduce_prompt = ChatPromptTemplate([
        ("human", "The following is a set of summaries:\n\n{docs}\n\n Distill them into a concise final summary. Create a summary related to the user query i.e.{{query}}")
    ])

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    final_summary = reduce_chain.invoke({"docs": "\n".join(summaries)})
    logger.info("Summarized the content")
    return {"answer": final_summary}

def manager_agent(state:AgentState):
    
    query = state["query"]
    logger.info("Query recieved to the manager agent")
    prompt = f"""
    You are the manager deciding which specialized agent to invoke. if the user query relates weather, respond only with "WeatherAgent".
    Otherwise, respond only with "WebSearchAgent".

    Query: {query}
    """
    choice = llm.invoke(prompt).content.strip()

    if "weatheragent" in choice.lower():
        logger.info("Calling WeatherAgent")
        return {"decision":"WeatherAgent"}
    elif "websearchagent" in choice.lower():
        logger.info("Calling WebSearchAgent")
        return {"decision":"WebSearchAgent"}
    else:
        return {"decision":"None"}


graph = StateGraph(AgentState,name="AgenticWorkflowGraph")

graph.add_node("ManagerAgent",manager_agent)
graph.add_node("WeatherAgent",weather_agent)
graph.add_node("WebSearchAgent",web_search_agent)


graph.add_edge(START, "ManagerAgent")

graph.add_conditional_edges(
    "ManagerAgent",
    lambda state: state["decision"], {
        "WeatherAgent" : "WeatherAgent",
        "WebSearchAgent":"WebSearchAgent",
        "None": END
    }
)

graph.add_edge("WeatherAgent", END)
graph.add_edge("WebSearchAgent",END)

app = graph.compile()

def run_agentic_workflow(user_query):
    initial_state = {"query": user_query, "decision": "", "answer": ""}
    logger.info("Calling the manager Agent")
    final_state = app.invoke(initial_state)

    return final_state["answer"]