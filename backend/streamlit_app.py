import pandas as pd
import streamlit as st
import random
import numpy as np
import requests
import PyPDF2
from bs4 import BeautifulSoup
from langchain_openai import AzureChatOpenAI
import openai
import json
import os
import regex as re
from dotenv import load_dotenv, find_dotenv

from azure.cognitiveservices.speech import (
    AudioDataStream,
    SpeechConfig,
    SpeechSynthesizer,
    SpeechSynthesisOutputFormat,
)
import azure.cognitiveservices.speech as speechsdk
from services import logger, measure_time
from podcast_creator import (
    extract_text_from_pdf,
    extract_text_from_url,
    title_generator,
    generate_podcast_plan,
    podacast_segment_generator,
)
from audio_generation import generate_ssml_script, convert_to_audiov2


# Load environment variables from the .env file
load_dotenv()

# Audio Config
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
from pydub import AudioSegment
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

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
    api_version="2025-01-01-preview",
    temperature=0.6,
)

speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

st.set_page_config(layout="wide", page_title="Podcast App")


# Audio file saving in its folder.
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder created: {folder_path}")
    else:
        print(f"📁 Folder already exists: {folder_path}")
    return folder_path

# Example usage:
output_path = create_folder_if_not_exists("saved_audio")
# audio_file_path = os.path.join(output_path, "final_audio.mp3")

# Code to display clean podcast script.
def format_podcast_script(script_markdown: str) -> str:
    lines = script_markdown.split('\n')
    formatted_lines = []

    for line in lines:
        # Format Segment Headers
        if line.strip().lower().startswith("segment:"):
            segment_match = re.match(r"(Segment:\s*)(.*)", line.strip(), re.IGNORECASE)
            if segment_match:
                formatted_lines.append(f"\n### 🧩 **{segment_match.group(1)}{segment_match.group(2)}**\n")
            continue

        # Format Speaker Dialogues
        speaker_match = re.match(r"^(\w+\s\w+):", line.strip())
        if speaker_match:
            formatted_lines.append(f"**{line.strip()}**  \n")
        else:
            formatted_lines.append(line.strip() + "  \n")

    return '\n'.join(formatted_lines)


# Code to save files.
def sanitize_title(title):
    return title.replace(" ", "_").replace(":", "").replace("/", "-")

def save_text_to_file(text, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    # st.title("Podcast Generator")

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Input Options")

    # 1) File Upload or URL feed
    input_method = st.sidebar.radio(
        "Choose input method:",
        ("Upload a PDF", "Enter a URL")
    )

    extracted_data = ""

    if input_method == "Upload a PDF":
        uploaded_file = st.sidebar.file_uploader(
            "Upload PDF",
            type=["pdf"]
        )
        if uploaded_file is not None:
            # Save uploaded PDF to a temporary file for reading
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())
            extracted_data = extract_text_from_pdf("temp_uploaded.pdf")

    else:  # "Enter a URL"
        url_feed = st.sidebar.text_input("Enter URL:")
        if url_feed:
            extracted_data = extract_text_from_url(url_feed)

    # 2) Number of speakers
    number_of_speakers = st.sidebar.number_input(
        "Number of Speakers",
        min_value=1,
        max_value=5,
        step=1,
        value=2
    )

    # 3) Dynamically show speaker selection for each speaker
    #    Use session state to avoid re-shuffling on every script re-run
    initial_speaker_list = [
        'Ava Smith',
        'Brian Stark',
        'Steffan Johnson',
        'Adam Brown',
        'Andrew White',
        'Amanda Turner',
        'Emma Clark',
        'Nancy Roberts',
        'Natasha Cook',
        'Davis Hall',
        'Dustin'
    ]

    if "shuffled_speaker_list" not in st.session_state:
        # Shuffle only once and store in session state
        st.session_state.shuffled_speaker_list = initial_speaker_list[:]
        random.shuffle(st.session_state.shuffled_speaker_list)

    speaker_list = st.session_state.shuffled_speaker_list

    chosen_speakers = []
    for i in range(number_of_speakers):
        speaker_name = st.sidebar.selectbox(
            f"Select speaker {i + 1} name:",
            speaker_list,
            key=f"speaker_{i}"
        )
        chosen_speakers.append(speaker_name)

    # Create the dictionary with up to 5 speakers
    speaker_details = {
        "speaker1": chosen_speakers[0] if number_of_speakers >= 1 else "",
        "speaker2": chosen_speakers[1] if number_of_speakers >= 2 else "",
        "speaker3": chosen_speakers[2] if number_of_speakers >= 3 else "",
        "speaker4": chosen_speakers[3] if number_of_speakers >= 4 else "",
        "speaker5": chosen_speakers[4] if number_of_speakers >= 5 else "",
    }
    # st.write(speaker_details)

    # 4) Select podcast length
    length_options = ["short", "moderate", "long"]
    podcast_length = st.sidebar.selectbox(
        "Select the podcast length:",
        length_options
    )

    # --- PODCAST SEGMENT GENERATION BUTTON ON SIDEBAR ---
    if st.sidebar.button("Generate Podcast Segment"):
        if not extracted_data.strip():
            st.sidebar.warning("Please provide either a PDF or a URL before generating.")
            return

        with st.spinner("Generating podcast conversation..."):
            # Use your existing logic exactly as is
            generated_title = title_generator(extracted_data=extracted_data, llm=llm)
            key_ideas = generate_podcast_plan(
                extracted_data=extracted_data,
                number_of_speakers=number_of_speakers,
                Length=podcast_length,
                llm=llm
            )

            podcast_segment = podacast_segment_generator(
                podcast_title=generated_title,
                podcast_keyideas=key_ideas,
                extracted_data=extracted_data,
                number_of_speakers=number_of_speakers,
                speaker_names=speaker_details,  # Pass the dictionary
                podcast_length=podcast_length,
                llm=llm,
                external_kn_call=False
            )

        # Replace spaces in title for file naming
        safe_title = generated_title.replace(" ", "_")

        # Store in session state so we can use it on the main page
        st.session_state["podcast_title"] = generated_title
        st.session_state["podcast_safe_title"] = safe_title
        st.session_state["podcast_segment"] = podcast_segment["podcast_script_as_markdown"]
        st.session_state["podcast_script_dialogues_only"] = podcast_segment["podcast_script_dialogues_only"]

        # Cleanup temporary file
        if os.path.exists("temp_uploaded.pdf"):
            os.remove("temp_uploaded.pdf")

        st.sidebar.success("Podcast Segment Generated!")
        st.sidebar.write("Check the main page to see details.")

    # --- MAIN CONTENT ---

    # Display the generated text if it exists
    if "podcast_title" in st.session_state and "podcast_segment" in st.session_state:
        st.markdown(f"## 🎙️ Podcast Title : {st.session_state['podcast_title']}")


        formatted_script = format_podcast_script(st.session_state["podcast_segment"])
        st.markdown(formatted_script)
        # st.markdown(st.session_state["podcast_segment"])
        safe_title = sanitize_title(st.session_state["podcast_title"])
        base_folder = "saved_podcast_data"
        segment_folder = os.path.join(base_folder, "segments")
        segment_path = os.path.join(segment_folder, f"{safe_title}.txt")
        save_text_to_file(st.session_state["podcast_segment"], segment_path)

    # BUTTON TO GENERATE AUDIO FROM SSML
    if st.button("Generate Audio from SSML"):
        if "podcast_segment" not in st.session_state:
            st.warning("No podcast script found. Please generate a segment first.")
            return

        # Generate SSML
        with st.spinner("Converting script to SSML..."):
            ssml_script = generate_ssml_script(
                podcast_conversation_script=st.session_state["podcast_script_dialogues_only"],
                speaker_details=speaker_details,
                llm=llm
            )
        ssml_script = ssml_script.replace("&", "and")
        ssml_folder = os.path.join(base_folder, "ssml_files")
        ssml_path = os.path.join(ssml_folder, f"{safe_title}.xml")
        save_text_to_file(ssml_script, ssml_path)
        # Convert SSML to Audio
        with st.spinner("Generating audio file..."):
            safe_title = st.session_state["podcast_safe_title"]
            audio_filename = f"{safe_title}.mp3"
            audio_full_path = os.path.join(output_path, audio_filename)

            convert_to_audiov2(
                speech_config=speech_config,
                ssml_output_form=ssml_script,
                file_path=audio_full_path
            )

        st.success("Audio generated successfully!")
        st.audio(audio_full_path, format="audio/mp3")


if __name__ == "__main__":
    main()

    
