import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY","")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY","")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY","")

