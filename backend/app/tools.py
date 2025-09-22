# from langchain.utilities import OpenWeatherMapAPIWrapper
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_tavily import TavilySearch
from .config import OPENWEATHERMAP_API_KEY

weather_tool = OpenWeatherMapAPIWrapper(openweathermap_api_key=OPENWEATHERMAP_API_KEY)

tavily_tool = TavilySearch(max_results = 5)