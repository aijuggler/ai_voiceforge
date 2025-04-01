import azure.cognitiveservices.speech as speechsdk
import os
import time

from services import logger, measure_time


def convert_ssml_to_audio(ssml_content, azure_speech_key, azure_spech_region, output_audio_file="podcast_audio.mp3", max_retries=3):
    """
    Convert SSML text to speech using Azure TTS and save as an audio file.
    
    Parameters:
    - ssml_content (str): SSML formatted string.
    - output_audio_file (str): Output file name for the generated speech.
    - max_retries (int): Number of retry attempts on failure.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🔁 Attempt {attempt} of {max_retries}")
            print(f"📤 Sending SSML to Azure TTS...\n")

            # Initialize Azure Speech config
            speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_spech_region)
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
            )

            # Use file-based audio output for server-side reliability
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_audio_file)

            # Create a speech synthesizer with audio config
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            # Convert SSML to speech
            result = synthesizer.speak_ssml_async(ssml_content).get()

            # Check the result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"✅ Podcast audio saved as: {output_audio_file}")
                return  # Exit after success

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"❌ Speech synthesis canceled. Reason: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"🔍 Error details: {cancellation_details.error_details}")

        except Exception as e:
            print(f"🚨 Exception occurred: {str(e)}")

        # Backoff if not last attempt
        if attempt < max_retries:
            wait_time = 2 ** attempt
            print(f"⏳ Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)

    print("❗ Max retries reached. Failed to generate podcast audio.")


