import xml.etree.ElementTree as ET
import json

from services import logger, measure_time

@measure_time
def generate_ssml_script(podcast_conversation_script, speaker_details, llm):

    """
    Converts a text-based podcast script into a valid SSML script using Azure LLM.

    Args:
        podcast_conversation_script (str): The podcast script in text format.
        speaker_details (dict): A dictionary of speaker placeholders and names.

    Returns:
        str: The generated SSML script.
    """
    title_to_voice_model = {
        "Ava Smith": "en-US-Ava:DragonHDLatestNeural",
        "Brian Stark": "en-US-Brian:DragonHDLatestNeural",
        "Steffan Johnson": "en-US-Steffan:DragonHDLatestNeural",
        "Adam Brown": "en-US-AdamMultilingualNeural",
        "Andrew White": "en-US-Andrew:DragonHDLatestNeural",
        "Amanda Turner": "en-US-AmandaMultilingualNeural",
        "Emma Clark": "en-US-Emma:DragonHDLatestNeural",
        "Nancy Roberts": "en-US-NancyMultilingualNeural",
        "Natasha Cook": "en-US-SerenaMultilingualNeural",
        "Davis Hall": "en-US-Davis:DragonHDLatestNeural",
        "Dustin": "en-US-DustinMultilingualNeural"
    }

    nested_speakers = {}

    # Build the nested mapping
    for speaker_key, speaker_name in speaker_details.items():
        if speaker_name and speaker_name in title_to_voice_model:
            nested_speakers[speaker_key] = {
                "Name": speaker_name,
                "Voice_model": title_to_voice_model[speaker_name]
            }

    ssml_prompt = f"""
You are an expert in speech synthesis markup language (SSML) and responsible for converting a text-based podcast script into a properly formatted SSML script.

Below are the Inputs:
Original Podcast conversation Segment(Textual format) : {podcast_conversation_script}
Speaker details(provided as nested dictionary) : {nested_speakers}
                    

# Instructions(Strictly follow):

1. Speaker Differentiation:
- The conversation includes multiple speakers. Identify each speaker and assign a distinct voice based on the inputs provided above respectively for each speaker and its corresponding voice model.

2. SSML Formatting:
- Wrap the entire response in `<speak>` tags with the required XML namespace.
- Use `<voice>` tags to specify the speaker.
- Use `<p>` tags for paragraphs to ensure proper speech pauses.
- Use `<break time="500ms"/>` where necessary to add natural pauses.
- Apply emphasis to important figures, numbers, and industry-specific terms using `<emphasis level="moderate">` or `<emphasis level="strong">`.
- Use styles for tone variations:
    - `style="cheerful"` for enthusiastic or introductory parts.
    - `style="calm"` for neutral explanations.
    - `style="thoughtful"` for deeper analytical discussions.
    - Carefully detect genuinely funny, light-hearted, or informal moments (e.g., stories about pets, funny personal anecdotes).
    - ONLY in those moments, apply:
        - <mstts:express-as style="cheerful"> or style="excited"
        - Simulate giggle or laughter tone using pacing and prosody (e.g., <prosody pitch="+10%" rate="fast">).
        - Insert <break time="200ms"/> where laughter or surprise would naturally occur.
    - Do NOT simulate laughter or cheerful tone for merely upbeat or energetic lines unless the **content is clearly funny or casual**.
    - Avoid literal words like “Haha” unless already part of the speaker's actual script.
- Please Always include styles and breaks wherever applicable to make the podcast sound as natural as possible.


    
3. Template for the SSML SCRIPT(Just for reference only):

    "
    <speak version="1.0" 
       xmlns="http://www.w3.org/2001/10/synthesis" 
       xml:lang="en-US">

        <voice name="en-US-AvaMultilingualNeural" effect="cheerful">
            Good morning! I hope you're feeling fresh and ready for a new day.
        </voice>

        <voice name="en-US-AndrewMultilingualNeural" effect="friendly">
            Good morning to you too, Ava! It's going to be a great day, I can feel it!
        </voice>

        <voice name="en-US-AvaMultilingualNeural" effect="excited">
            Absolutely! Let's get started with a big smile!
        </voice>

    </speak>

    "
    

4. Expected Output:
- DO NOT modify the content or meaning of the script. Your role is only to enhance the delivery using SSML.                    
- Ensure the final SSML is valid, well-structured, and ready to be processed by a Text-to-Speech engine.

5. Completion Guarantee:-
- Do not truncate or shorten the SSML under any circumstances, even if you have already provided a partial response. It must contain the entire podcast conversation, including **Closing Thoughts and Outro**.
- Your response must contain the complete conversation.
- If needed, optimize formatting to fit long text without cutting. Split long paragraphs but don’t drop segments.
- NEVER treat earlier parts as final output. Wait till **all segments are processed**, including the last one.

6. Speaker Identification:
- Only Include the Speaker dialogues in the SSML script. Donot use Segment sections names like Structured Discussion, Deep Dive etc in the ssml.
- Do not rewrite the content. For each line, detect the speaker from the text before the colon. Use the dictionary to select the correct voice. Output each line in <voice name="...">...</voice>.
                    



The final output should strictly be in the following Format:

{{
    
    "ssml_script": <Generated ssml script from the provided podcast segment>

}}

Response:

"""

    

    

    # Use your own prompt template and LLM (assumes `ssml_prompt` & `llm` are declared elsewhere)
    response = llm.invoke(ssml_prompt)

    # Parse the returned SSML JSON
    ssml_output = response.content.strip().strip("```json").strip("```")
    ssml_json = json.loads(ssml_output)
    xml_script = ssml_json["ssml_script"]
    return xml_script
