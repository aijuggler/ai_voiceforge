import azure.cognitiveservices.speech as speechsdk
import os
import time

from services import logger, measure_time
import time
import regex as re
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.etree import ElementTree as ET
from pydub import AudioSegment
from azure.cognitiveservices.speech import (
    AudioDataStream,
    SpeechSynthesizer,
    SpeechSynthesisOutputFormat,
    SpeechConfig,
)
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"


@measure_time
def split_ssml_preserve_format(ssml_output_form, max_characters=2000):
    """
    Splits an SSML string into smaller chunks, preserving the XML format and structure.
    """
    # Parse the SSML string
    root = ET.fromstring(ssml_output_form)
    namespace = root.tag.split('}')[0] + '}'  # Extract namespace
    speak_tag_name = root.tag.split('}')[-1]  # Extract the tag name without namespace

    # Collect all child elements under <speak>
    children = list(root)
    chunks = []
    current_chunk = []
    current_length = 0

    for child in children:
        serialized = ET.tostring(child, encoding="unicode")
        if current_length + len(serialized) > max_characters:
            # Save the current chunk
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
        current_chunk.append(child)
        current_length += len(serialized)

    if current_chunk:
        chunks.append(current_chunk)

    # Convert chunks back to valid SSML
    chunk_files = []
    for i, chunk in enumerate(chunks):
        # Create a new root element with the correct namespace
        chunk_root = ET.Element(f"{namespace}{speak_tag_name}", attrib={"xmlns": "https://www.w3.org/2001/10/synthesis"})
        chunk_root.attrib.update(root.attrib)  # Copy attributes from the original root

        # Add elements to the chunk root
        for element in chunk:
            chunk_root.append(element)

        # Serialize each chunk as a string
        chunk_files.append(ET.tostring(chunk_root, encoding="unicode"))

    return chunk_files



# ───────────────────────────────────────────────
def synthesize_chunk(speech_config, chunk, temp_file, retries=3):
    for attempt in range(retries):
        try:
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = synthesizer.speak_ssml_async(chunk).get()

            if result.reason != result.reason.SynthesizingAudioCompleted:
                raise Exception(result.cancellation_details.error_details)

            stream = AudioDataStream(result)
            stream.save_to_wav_file(temp_file)
            logger.debug(f"[Success] Saved: {temp_file}")
            return temp_file

        except Exception as e:
            logger.warning(f"[Attempt {attempt + 1}/{retries}] Failed to synthesize {temp_file}: {e}")
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))  # exponential backoff
            else:
                logger.error(f"[FINAL FAIL] Could not synthesize {temp_file} after retries.")
                return None

#______________________________________________________________________________________________________________________
def extract_part_number(file_name):
    """
    Extract the numeric part from filenames like '_part_1.mp3'
    """
    match = re.search(r"_part_(\d+)\.mp3$", file_name)
    return int(match.group(1)) if match else 0



# ───────────────────────────────────────────────
def concatenate_audio_files(audio_files, output_file):
    combined = AudioSegment.empty()
    valid_files = []

    # Sort files by part number: _part_1.mp3, _part_2.mp3, ..., _part_10.mp3
    audio_files_sorted = sorted(audio_files, key=extract_part_number)

    logger.debug(f"🔢 Merging {len(audio_files_sorted)} chunks in order:")
    for audio_file in audio_files_sorted:
        try:
            if not os.path.exists(audio_file):
                logger.warning(f"⚠️ Skipping missing file: {audio_file}")
                continue
            if os.path.getsize(audio_file) == 0:
                logger.warning(f"⚠️ Skipping zero-byte file: {audio_file}")
                continue

            logger.debug(f"   ↳ Merging: {audio_file} ({os.path.getsize(audio_file)} bytes)")
            segment = AudioSegment.from_file(audio_file)
            combined += segment
            valid_files.append(audio_file)

        except Exception as e:
            logger.error(f"❌ Failed to load chunk {audio_file}: {e}")

    if not valid_files:
        logger.error("❌ No valid audio chunks to merge. Final audio not generated.")
        return

    combined.export(output_file, format="mp3")
    logger.info(f"🎧 Final podcast audio saved to: {output_file}")
    logger.info(f"🕒 Final duration: {len(combined) / 1000:.2f} seconds")



# ───────────────────────────────────────────────
@measure_time
def convert_to_audiov2(speech_config: SpeechConfig, ssml_output_form: str, file_path: str):
    logger.debug("🟡 Starting audio generation process.")
    speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat["Riff24Khz16BitMonoPcm"])

    chunks = split_ssml_preserve_format(ssml_output_form, max_characters=1000)
    logger.info(f"🔹 Split into {len(chunks)} SSML chunks.")

    audio_files = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i, chunk in enumerate(chunks):
            temp_file = f"{file_path}_part_{i + 1}.mp3"    
            logger.debug(f"📝 Submitting chunk {i + 1} | Preview: {chunk[:150]}...")
            futures.append(executor.submit(synthesize_chunk, speech_config, chunk, temp_file))

        for future in as_completed(futures):
            result = future.result()
            if result:
                audio_files.append(result)

    if audio_files:
        concatenate_audio_files(audio_files, file_path)
    else:
        logger.error("❌ No audio files generated. Final output skipped.")
        return

    for f in audio_files:
        if os.path.exists(f):
            os.remove(f)
    logger.debug("🧹 Temporary audio chunks cleaned up.")













































#____________________________________________________________________________________________________________________________________________
# OLD CODE

# def convert_ssml_to_audio(ssml_content, azure_speech_key, azure_spech_region, output_audio_file="podcast_audio.mp3", max_retries=3):
#     """
#     Convert SSML text to speech using Azure TTS and save as an audio file.
    
#     Parameters:
#     - ssml_content (str): SSML formatted string.
#     - output_audio_file (str): Output file name for the generated speech.
#     - max_retries (int): Number of retry attempts on failure.
#     """
#     for attempt in range(1, max_retries + 1):
#         try:
#             print(f"\n🔁 Attempt {attempt} of {max_retries}")
#             print(f"📤 Sending SSML to Azure TTS...\n")

#             # Initialize Azure Speech config
#             speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_spech_region)
#             speech_config.set_speech_synthesis_output_format(
#                 speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
#             )

#             # Use file-based audio output for server-side reliability
#             audio_config = speechsdk.audio.AudioOutputConfig(filename=output_audio_file)

#             # Create a speech synthesizer with audio config
#             synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

#             # Convert SSML to speech
#             result = synthesizer.speak_ssml_async(ssml_content).get()

#             # Check the result
#             if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#                 print(f"✅ Podcast audio saved as: {output_audio_file}")
#                 return  # Exit after success

#             elif result.reason == speechsdk.ResultReason.Canceled:
#                 cancellation_details = result.cancellation_details
#                 print(f"❌ Speech synthesis canceled. Reason: {cancellation_details.reason}")
#                 if cancellation_details.reason == speechsdk.CancellationReason.Error:
#                     print(f"🔍 Error details: {cancellation_details.error_details}")

#         except Exception as e:
#             print(f"🚨 Exception occurred: {str(e)}")

#         # Backoff if not last attempt
#         if attempt < max_retries:
#             wait_time = 2 ** attempt
#             print(f"⏳ Waiting {wait_time} seconds before retrying...")
#             time.sleep(wait_time)

#     print("❗ Max retries reached. Failed to generate podcast audio.")


