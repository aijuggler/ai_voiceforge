import pandas as pd
import numpy as np
import requests
import PyPDF2
from bs4 import BeautifulSoup
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
import openai
import json
import os
from dotenv import load_dotenv, find_dotenv

from services import logger, measure_time
from podcast_creator import (extract_text_from_pdf, extract_text_from_url, title_generator, generate_podcast_plan, 
                             podacast_segment_generator)


# Load environment variables from the .env file
load_dotenv("cred.env")

# Retrieve Azure OpenAI specific configuration from environment variables
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Initialize Azure LLM
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  
    api_version="2024-05-01-preview",
    temperature=0.4,  
    timeout=120,  
    max_retries=5,
)

@measure_time
def podcast_conversation_segment(extracted_data, podcast_length, number_speakers, speakers_names, llm:AzureChatOpenAI):
    title = title_generator(extracted_data=extracted_data, llm=llm)
    key_ideas = generate_podcast_plan(extracted_data=extracted_data, number_of_speakers=number_speakers, 
                                      Length=podcast_length, llm=llm)
    podcast_segment = podacast_segment_generator(podcast_title=title, podcast_keyideas=key_ideas,
                                                extracted_data=extracted_data, number_of_speakers=number_speakers,
                                                speaker_names=speakers_names, podcast_length=podcast_length, llm=llm)
    
    return podcast_segment




if __name__=="__main__":
    pass
    

