from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import os
import json
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from podcast_creator import (
    extract_text_from_pdf,
    extract_text_from_url,
    title_generator,
    generate_podcast_plan,
    podacast_segment_generator,
)
from audio_generation import generate_ssml_script, convert_to_audiov2


  # assuming these are defined cleanly

from services.utils import sanitize_title, save_text_to_file, create_folder_if_not_exists
from dotenv import load_dotenv
load_dotenv("cred.env")
# Azure Speech Setup
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
)

# Set ffmpeg and ffprobe path for pydub
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

from langchain_openai import AzureChatOpenAI
llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            api_version="2024-05-01-preview",
            temperature=0.6,
        )


app = FastAPI()

@app.post("/generate_podcast")
def generate_podcast(
    input_method: str = Form(...),
    pdf_file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    speakers: str = Form(...),
    number_of_speakers: int = Form(...),
    length: str = Form(...)
):
    # Step 1: Extract the content
    if input_method == "pdf" and pdf_file is not None:
        with open("temp_uploaded.pdf", "wb") as f:
            f.write(pdf_file.file.read())
        extracted_data = extract_text_from_pdf("temp_uploaded.pdf")
        os.remove("temp_uploaded.pdf")
    elif input_method == "url" and url:
        extracted_data = extract_text_from_url(url)
    else:
        return {"error": "Invalid input_method or missing file/url"}

    if not extracted_data.strip():
        return {"error": "Extraction failed, no data returned."}

    # Step 2: Prepare speaker mapping
    try:
        speakers_list = json.loads(speakers)
    except json.JSONDecodeError:
        speakers_list = [s.strip() for s in speakers.split(",")]

    if len(speakers_list) < number_of_speakers:
        return {"error": f"Expected at least {number_of_speakers} speaker names, but got only {len(speakers_list)}"}

    # Build speaker_dict with 5 keys (speaker1 - speaker5), fill unused with empty string
    speaker_dict = {
        f"speaker{i+1}": speakers_list[i] if i < len(speakers_list) else ""
        for i in range(5)
    }
    # Determine actual speaker count excluding empty slots
    actual_speakers = [s for s in speakers_list if s.strip()]
    actual_speaker_count = len(actual_speakers)

    # Reduce number_of_speakers if you passed empty strings to avoid LLM assuming phantom guests
    number_of_speakers = actual_speaker_count
    # Step 3: Generate title, key ideas, script
    title = title_generator(extracted_data, llm)
    key_ideas = generate_podcast_plan(extracted_data, number_of_speakers, length, llm)
    podcast_data = podacast_segment_generator(
        podcast_title=title,
        podcast_keyideas=key_ideas,
        extracted_data=extracted_data,
        number_of_speakers=number_of_speakers,
        speaker_names=speaker_dict,
        podcast_length=length,
        llm=llm,
        external_kn_call=False
    )

    # Step 4: Generate SSML
    ssml_script = generate_ssml_script(
        podcast_conversation_script=podcast_data["podcast_script_dialogues_only"],
        speaker_details=speaker_dict,
        llm=llm
    )
    ssml_script = ssml_script.replace("&", "and")

    # Step 5: Convert to audio and save
    safe_title = sanitize_title(title)
    base_path = create_folder_if_not_exists("saved_audio")
    audio_filename = f"{safe_title}.mp3"
    audio_path = os.path.join(base_path, audio_filename)

    convert_to_audiov2(speech_config, ssml_script, audio_path)

    # Save SSML and script
    save_text_to_file(ssml_script, f"saved_podcast_data/ssml_files/{safe_title}.xml")
    save_text_to_file(podcast_data["podcast_script_as_markdown"], f"saved_podcast_data/segments/{safe_title}.txt")

    return {
        "podcast_title": title,
        "audio_path": audio_path,
        "message": "✅ Podcast generation successful",
        "ssml_saved_to": f"saved_podcast_data/ssml_files/{safe_title}.xml",
        "script_saved_to": f"saved_podcast_data/segments/{safe_title}.txt"
    }
