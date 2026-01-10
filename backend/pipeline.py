# pipeline.py - Corrected to save all intermediate files.

import os
import random
import requests
import PyPDF2
from bs4 import BeautifulSoup
from langchain_openai import AzureChatOpenAI
import openai
import json
import regex as re
from dotenv import load_dotenv
import base64

# Assuming your custom modules are in the same directory or accessible.
from services import logger, measure_time
from podcast_creator import (
    extract_text_from_pdf,
    extract_text_from_url,
    title_generator,
    generate_podcast_plan,
    podacast_segment_generator,
)
from audio_generation import generate_ssml_script, convert_to_audiov2

import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

# --- Configuration ---
load_dotenv()
# AudioSegment.converter = os.getenv("FFMPEG_PATH", "/opt/homebrew/bin/ffmpeg")
# AudioSegment.ffprobe = os.getenv("FFPROBE_PATH", "/opt/homebrew/bin/ffprobe")

# ------- New Code for pydub and ffmpeg fixation -------

# Load paths from env or use sensible Linux default
ffmpeg_path = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")
ffprobe_path = os.getenv("FFPROBE_PATH", "/usr/bin/ffprobe")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path
os.environ["PATH"] += os.pathsep + os.path.dirname(AudioSegment.converter)
import logging
logging.debug(f"Using ffmpeg at: {ffmpeg_path}")
logging.debug(f"Using ffprobe at: {ffprobe_path}")





# Azure Service Configurations
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# Initialize Azure LLM and Speech Clients
llm = AzureChatOpenAI(azure_deployment="gpt-4o-mini", api_version="2025-01-01-preview", temperature=0.6)
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

# --- Helper Functions ---
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder created: {folder_path}")
    return folder_path

def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")

def save_text_to_file(text, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 Text saved to: {file_path}")


# --- Core Pipeline Function (Corrected) ---
@measure_time
def create_podcast_pipeline(input_type: str, input_source: str, speaker_names: dict, podcast_length: str, base_output_dir: str = "generated_podcasts"):
    print("🚀 Starting podcast generation pipeline...")

    # Step 1: Extract Text
    extracted_data = ""
    if input_type == 'url':
        extracted_data = extract_text_from_url(input_source)
    elif input_type == 'pdf':
        if not os.path.exists(input_source): return None
        extracted_data = extract_text_from_pdf(input_source)
    if not extracted_data: return None
    print("✅ Text extraction complete.")

    # Step 2: Generate Podcast Content
    number_of_speakers = len([name for name in speaker_names.values() if name])
    print("🧠 Generating podcast title, plan, and script...")
    generated_title = title_generator(extracted_data=extracted_data, llm=llm)
    key_ideas = generate_podcast_plan(extracted_data=extracted_data, number_of_speakers=number_of_speakers, Length=podcast_length, llm=llm)
    podcast_segment_data = podacast_segment_generator(podcast_title=generated_title, podcast_keyideas=key_ideas, extracted_data=extracted_data, number_of_speakers=number_of_speakers, speaker_names=speaker_names, podcast_length=podcast_length, llm=llm, external_kn_call=False)
    
    script_markdown = podcast_segment_data["podcast_script_as_markdown"]
    script_dialogues_only = podcast_segment_data["podcast_script_dialogues_only"]
    print(f"✅ Podcast script generated for title: '{generated_title}'")
    
    # Step 3: Define Paths and Save Script
    safe_title = sanitize_title(generated_title)
    podcast_folder = os.path.join(base_output_dir, safe_title)
    create_folder_if_not_exists(podcast_folder)
    
    # **FIX:** Save the markdown script to a .txt file
    script_path = os.path.join(podcast_folder, f"{safe_title}_script.txt")
    save_text_to_file(script_markdown, script_path)

    # Step 4: Generate and Save SSML
    ssml_script = generate_ssml_script(podcast_conversation_script=script_dialogues_only, speaker_details=speaker_names, llm=llm)
    ssml_script = ssml_script.replace("&", "and")
    
    # **FIX:** Save the SSML script to an .xml file
    ssml_path = os.path.join(podcast_folder, f"{safe_title}.xml")
    save_text_to_file(ssml_script, ssml_path)
    
    # Step 5: Generate Audio from the saved SSML
    audio_path = os.path.join(podcast_folder, f"{safe_title}.mp3")
    print("🎤 Generating final audio file...")
    convert_to_audiov2(speech_config=speech_config, ssml_output_form=ssml_script, file_path=audio_path)
    print(f"✅ Audio generation complete! File saved at: {audio_path}")

    # Step 6: Read audio for response
    base64_audio_data = ""
    try:
        with open(audio_path, "rb") as audio_file:
            base64_audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        print("✅ Audio file encoded to Base64 for response.")
    except Exception as e:
        print(f"❌ ERROR: Could not read and encode audio file: {e}")
        return None

    print("🎉 Pipeline finished successfully!")

    # Step 7: Return final data for the API
    return {
        "title": generated_title,
        "podcast_script": script_markdown,
        "audio_data": base64_audio_data
    }
