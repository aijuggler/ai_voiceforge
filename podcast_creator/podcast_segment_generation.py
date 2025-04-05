
from langchain_openai import AzureChatOpenAI
import json
import os

from services import logger, measure_time

@measure_time
def title_generator(extracted_data, llm: AzureChatOpenAI):
    logger.debug("Titile generating for Podcast")
    prompt_title = f"""
    You are an intelligent AI trained to generate concise and attention-grabbing podcast titles.

    Your goal is to create a title that reflects the essence of the podcast conversation based on the content provided below.
    
    The title should be:
    - Short (ideally under 12 words)
    - Relevant to the key themes and subject matter
    - Engaging and appealing for podcast listeners
    - Clear and free from vague or overly generic phrases
    - Avoid clickbait or overly dramatic wording
    - Title case formatted (capitalize major words)

    ### Content for which you have to generate title:
    {extracted_data}

    ### Instructions:
    - Read the provided content carefully
    - Identify the core topic(s) and themes
    - Generate **one** strong podcast title that captures the essence of the conversation

    Respond with **only the final title**, no explanation or bullet points. Provide the final output as per given format given below:

    {{
       
        "podcast_title" : "Generated Title for the podcast."
    
    }}

    """

    response = llm.invoke(prompt_title)
    response_content = response.content.strip().strip("```json").strip("```")
    parsed_response = json.loads(response_content)
    return parsed_response["podcast_title"]

@measure_time
def external_knowledge_on_topic(podcast_title, length, llm):
    logger.debug(f"External knowledge started for {podcast_title} and it will have {length} words.")
    prompt_knowldge = f"""  

    You are an expert content writer.

    Your task is to generate a detailed and well-structured podcast content script based on the following provided title:

    **Title:** "{podcast_title}"

    Please follow these guidelines:
    - Use your external knowledge to elaborate on the topic.
    - Include real-world examples, facts, or insights if relevant.
    - Keep the total content under {length} words.
    - Make sure it doesnot contain any real person's name or reference to any person.

    """
    response = llm.invoke(prompt_knowldge)
    return response.content



# Function to Invoke LLM with Text-based Response
@measure_time
def generate_podcast_plan(extracted_data, number_of_speakers, Length: str, llm: AzureChatOpenAI):
    logger.debug("Podcast key Ideas generation started.")
    logger.debug(f"Podcast planning idea generation started. Total Number of Speakers are: {number_of_speakers}")
    Podcast_key_idea_prompt = f"""
    You are tasked with analyzing the following content and generating a structured podcast plan. Your objectives are to extract key themes, propose a podcast title, create a detailed conversation outline tailored to the specified number of speakers, and develop discussion questions based on the identified themes.

    Content: 
    {extracted_data}

    Number of Speakers: 
    {number_of_speakers}

    Length of conversation:
    {Length}

    Your Objectives:

    1. Identify and List Key Ideas or Themes:
      - Analyze the provided content and extract between 10 to 25 main themes or key ideas.
      - Provide a suitable but engaging podcast title that captures the essence of the discussion.
      - Ensure themes are appropriate for the conversation length (e.g., for short discussions, limit complexity).

    2. Create a Structured Podcast Conversation Outline:
      - Assign distinct roles to each speaker (e.g., Host, Expert, Analyst).
      - Outline the flow of discussion in segments, ensuring a natural progression.
      - Indicate who speaks when and their contribution to the discussion.

    3. Develop Discussion Questions:
      - Create 3-8 engaging questions per theme that encourage deep discussion.
      - Ensure the questions match the conversation length (e.g., short sessions = concise questions).

    ---

    Example:

    Podcast Title: AI in Healthcare: Ethics, Innovations, and the Future

    1. Podcast Ideas:

    Podcast Idea 1: The Impact of AI in Modern Healthcare  
    Speakers:  
      Host (Moderator) – Guides the discussion  
      AI Researcher – Explains technological advancements  
      Medical Practitioner – Discusses real-world applications  

    Discussion Points:  
      The role of AI in diagnostics  
      Ethical concerns around AI-driven decisions  
      Future potential of AI in personalized medicine  

    Podcast Idea 2: The Challenges of Implementing AI in Hospitals  
    Speakers:  
      Healthcare IT Specialist – Talks about adoption barriers  
      AI Researcher – Discusses regulations and challenges  

    Discussion Points:  
      Data security concerns  
      Integration of AI with existing healthcare systems  

    2. Flow of Conversation:

    Segment: Introduction  
    Number of Conversations: 1  
    Content: Overview of the podcast and introduction of speakers.  

    Segment: The State of AI in Healthcare  
    Number of Conversations: 3  
    Content:  
      Host discusses the evolution of AI in healthcare.  
      AI Researcher shares statistics on AI’s impact.  
      Medical Practitioner discusses patient experiences.  

    3. Discussion Questions:

    AI in Healthcare:  
      What are the most promising AI applications in medicine?  
      What ethical dilemmas arise when AI makes healthcare decisions?  

    Challenges & Future of AI:  
      How can AI regulations balance innovation and safety?  
      What are the biggest hurdles in AI adoption for hospitals?  

    ---

    Now, generate the structured response strictly in following format.

    {{
        "podcast_idea" : "Generated podacst ideas as a structured bullet points in text format as provided in above example"
        
    }}
        
  
"""

    # Invoke LLM
    response = llm.invoke(Podcast_key_idea_prompt)
    
    # Clean and parse JSON response
    response_content = response.content.strip().strip("```json").strip("```")
    parsed_response = json.loads(response_content)


    return parsed_response["podcast_idea"] # Return text response
    # return response.content



#____________________________________________________________________________________________________________________________
def podacast_segment_generator(podcast_title, podcast_keyideas, extracted_data, number_of_speakers, podcast_length:str, speaker_names:dict, llm:AzureChatOpenAI, external_kn_call=False):

    # logger.debug(f"Podcast Conversation segment generation started. Total Speakers are: {number_of_speakers}")
    # logger.debug(f"Configuring the podcast for Length: {podcast_length}")
    # logger.debug(f"Speaker details are : {speaker_names}")

    podcast_length = podcast_length.lower()
    
    if podcast_length == "short":
        conversation_type = (
            "Since this is a short-length podcast, each speaker's dialogue should be concise and to the point. However, ensure it remains engaging and conversational."
        )
        external_knowledge_length = "400-600 words"
        podcast_structure = {
            "introduction": "2-3 exchanges",
            "structured_discussion": "4-6 exchanges",
            "deep_dive": "4-6 exchanges",
            "interactive_discussions": "4-6 exchanges",
            "highlights_key_takeaways": "3-4 exchanges",
            "question_rounds": "2-3 exchanges",
            "closing_thoughts_and_outro": "3-4 exchanges"
        }

    elif podcast_length == "moderate":
        conversation_type = (
            "Since this is a moderately long podcast, each speaker's dialogue can be slightly longer with more detailed sentences. Still, ensure the conversation remains engaging and natural."
        )
        external_knowledge_length = "800-1000 words"
        podcast_structure = {
            "introduction": "3-5 exchanges",
            "structured_discussion": "8-10 exchanges",
            "deep_dive": "10-15 exchanges",
            "interactive_discussions": "10-15 exchanges",
            "highlights_key_takeaways": "8-10 exchanges",
            "question_rounds": "5-7 exchanges",
            "closing_thoughts_and_outro": "3-4 exchanges"
        }

    elif podcast_length == "long":
        conversation_type = (
            "Since this is a long-format podcast, each speaker's dialogue should be more extensive and composed of longer sentences. Yet, maintain a lively and conversational tone throughout."
        )
        external_knowledge_length = "2000-3000 words"
        podcast_structure = {
            "introduction": "3-5 exchanges",
            "structured_discussion": "15-20 exchanges",
            "deep_dive": "15-20 exchanges",
            "interactive_discussions": "15-20 exchanges",
            "highlights_key_takeaways": "15-20 exchanges",
            "question_rounds": "7-10 exchanges",
            "closing_thoughts_and_outro": "3-4 exchanges"
        }

    else:
        # logger.error(f"Unknown podcast length specified. Please check {podcast_length}")
        raise ValueError("Unknown podcast length specified.")
    
    if external_kn_call:
        external_knowledge = external_knowledge_on_topic(podcast_title=podcast_title, length=external_knowledge_length, llm=llm)
    else:
        external_knowledge = "Not Needed As User has not allowed to use any external knowledge. Keep the Podcast as per the topic."


    prompt = f"""  
    You are an intelligent AI Podcast Segment Generator. Your task is to generate a structured, conversational podcast segment among speakers that is both engaging and strictly compliant with the instructions below.

    Podcast title : {podcast_title}
    Podcast_keyideas : {podcast_keyideas}  
    Content : {extracted_data}
    Number of speakers : {number_of_speakers}
    Length of Podcast : {podcast_length}

    Instructions for Generating Podcast Segment:(Must Follow Everytime)

    1.  Content Creation & Speaker Roles
        - Expand the provided key ideas into a coherent, natural, and unique conversation, ensuring smooth transitions.  
        - Assign distinct roles to each speaker based on their relevance to the topic.
        - The number of speakers must match with provided number of speaker.
        - At the very beginning of the script, list speaker details for each speaker (from 1 to {number_of_speakers}) as follows:
          - Speaker 1: {speaker_names["speaker1"] if speaker_names["speaker1"] else "no speaker 1"}
          - Speaker 2: {speaker_names["speaker2"] if speaker_names["speaker2"] else "no speaker 2"}
          - Speaker 3: {speaker_names["speaker3"] if speaker_names["speaker3"] else "no speaker 3"}
          - Speaker 4: {speaker_names["speaker4"] if speaker_names["speaker4"] else "no speaker 4"}
          - Speaker 5: {speaker_names["speaker5"] if speaker_names["speaker5"] else "no speaker 5"}
          Present Names of those speakers which are present in speaker_names, if no speaker are there don't mention anything like("", no speaker, etc.)

    2.  Structure and Segmentation. 
        Ensure that the generated podcast script has outline the segments which are mentioned below, **in this exact order**, with the **exact number of textual exchanges** stated for each segment. 
          
        1. **Introduction** 
          - Number of Exchanges: {podcast_structure["introduction"]}
            
        2. **Structured Discussion** 
          - Number of Exchanges: {podcast_structure["structured_discussion"]}
          
        3. **Deep Dive**  
          - Number of Exchanges: {podcast_structure["deep_dive"]}
            
        4. **Interactive Discussions**  
          - Number of Exchanges: {podcast_structure["interactive_discussions"]}

        5. **Highlights Important Key Takeaway**  
          - Number of Exchanges: {podcast_structure["highlights_key_takeaways"]}
          
        6. **Some Question Rounds**
          - Number of Exchanges: {podcast_structure["question_rounds"]}

        7. **Closing Thoughts and Outro**
          - Number of Exchanges: {podcast_structure["closing_thoughts_and_outro"]}

        - Also strictly adhere to the conversation type as mentioned here: {conversation_type}  
        - Each speaker’s single response counts as ONE exchange.
        - **Strict Compliance Requirement**: 
          Before finalizing, perform a final compliance check to ensure that each segment contains exactly the specified number of exchanges. If any segment does not meet these numeric requirements, revise it until it does.
        - **IMPORTANT:** 
          Generate each segment in order. After generating each segment, perform a self-check: count the exchanges and verify that all required speaker names appear. If any segment is missing the correct number of exchanges or a speaker name, regenerate that segment.
        - If your full output exceeds token limits, clearly label additional parts as "Part 2", "Part 3", etc., and ensure that the continuation does not break any segment's integrity.



    3.  Flow, Tone, and Impact
        - Start with an engaging introduction explaining why the topic matters. 
        - Make sure the host speaker : {speaker_names['speaker1']} — must warmly welcome **all** speakers in **one** exchange, explicitly announcing each speaker's name, role, or expertise.
        example:- Hello and welcome to Gaming Goldmine, the show where we explore the most exciting trends shaping the future of tech and innovation. I’m your host, James White, and today we’re diving into one of the fastest-growing industries in India—gaming. From mobile apps to esports arenas, the Indian gaming sector is booming, and there’s a lot to unpack.To help us break it all down, I’m joined by two brilliant guests. First up, we have Andrew Smith, a seasoned market analyst who’s been tracking digital entertainment trends across Asia. Welcome, Andrew!
        - After the host introduces them in a single exchange, each guest can provide a brief greeting or follow-up remark in their own exchange, but **should not** repeat the entire role introduction. # <-- Added for clarity
        - Break down the main discussion into meaningful segments that reflect the key ideas.
        - Ensure that the conversation flows naturally. Include 1-2 additional lines that are impactful and provide deeper insights. When appropriate, allow for a touch of natural humor or light informal banter (such as laughter) to enhance the dialogue, but keep the overall tone professional and engaging.
        
    4. External Knowledge Integration
       - If external knowledge are needed as User has explicitly allowed to use any external knowledge, you are allowed to incorporate external knowledge into the conversation so that approximately 30% of the final content is derived from external sources.
       - If external knowledge not needed as User has not explicitly allowed to use any external knowledge. Keep the Podcast as per the topic., rely entirely on the provided content and key ideas (i.e., 100% content from the inputs).
       - Clearly integrate external knowledge only when permitted.
       External knowledge base: {external_knowledge}:
      
    5. Final Validation and Programmatic Compliance
       - After generating the full podcast segment, perform a final self-check and verify the following::
        - After generating each segment, ensure it has exactly {podcast_structure["introduction"]} or {podcast_structure["structured_discussion"]} etc. exchanges.
        - Ensure that no segment is skipped or merged, and that all speaker details are correctly included.
        - If any segment fails to meet the numeric requirements, if not, provide a follow-up continuation that corrects any discrepancies.
       

    6. Ensure that in the generated Podcast segment the Speaker Names are dynamically adjusted. Based on {number_of_speakers} and speaker details dictionary provided above.

    
    
    ** Most Important ** : 
       - Do not skip or merge segments. 
       - Maintain a clear label for each segment. 
       - For a longer or moderate podcast you must have to generate the podcast segment exactly as per the conversation exchanges mentioned in the Rule 2 above.
       - The output must adhere exactly to the structure of podcast and numeric requirements stated above. Any deviation from the exact numbers in each segment or the required JSON format is unacceptable and against compliance.
        
    
    ## Feedback Recieved(from the user of this app): 
       - User complained about podcast segment not having a strict pattern. Make sure podcast always follow pattern and rules mentioned above.
       - It will showcase the dialogue flow keeping the exact speaker name and respective dialogues. Avoid using words like host, guest speaker etc. There should not be presence of any other words like [INTRO MUSIC FADES IN],[INTRO MUSIC FADES OUT] etc. 
       
    
 
    7. Output Format for Each Segment (IMPORTANT)
       - For each segment, you must output valid JSON **with exactly two keys**:

         {{
            "dialogues": "Plain text dialogues for this segment",
            "markdown": "The same dialogues in Markdown format, with headings/speaker name in bold, etc."
         }}
       - Do NOT include any other keys or any extra text outside of that JSON object.

    Response:

    """

    # Define the segments in order for loop-based generation
    segments_order = [
        "introduction",
        "structured_discussion",
        "deep_dive",
        "interactive_discussions",
        "highlights_key_takeaways",
        "question_rounds",
        "closing_thoughts_and_outro"
    ]

    segment_outputs = {}
    max_attempts = 3

    for segment in segments_order:
        # CHANGED: Provide explicit instructions for the EXACT two-key JSON.
        seg_prompt = (
            prompt
            + f"\nNow, generate **only** the '{segment}' segment with exactly {podcast_structure[segment]} exchanges.\n"
            + "Return your response in **valid JSON** with exactly two keys: 'dialogues' and 'markdown'. "
            + "No other keys. No extra text. Comply strictly."
        )

        attempts = 0
        seg_parsed = None
        seg_response_content = ""

        while attempts < max_attempts:
            seg_response = llm.invoke(seg_prompt)
            seg_response_content = seg_response.content.strip().strip("```json").strip("```")

            # Attempt to parse as JSON
            try:
                parsed = json.loads(seg_response_content)
            except Exception:
                attempts += 1
                continue

            # Validate that it has only 'dialogues' and 'markdown'
            if isinstance(parsed, dict) and "dialogues" in parsed and "markdown" in parsed:
                # Also check it doesn't contain extra keys
                if len(parsed.keys()) == 2:
                    seg_parsed = parsed
                    break

            attempts += 1

        if seg_parsed is None:
            # Fallback if we never got a correct structure
            seg_parsed = {
                "dialogues": seg_response_content,
                "markdown": seg_response_content
            }

        segment_outputs[segment] = seg_parsed

    # Now combine them in final strings
    final_dialogues = ""
    final_markdown = ""

    for segment in segments_order:
        final_dialogues += (
            f"\n\n---\nSegment: {segment.replace('_', ' ').title()}\n"
            + segment_outputs[segment]["dialogues"]
        )
        final_markdown += (
            f"\n\n---\nSegment: {segment.replace('_', ' ').title()}\n"
            + segment_outputs[segment]["markdown"]
        )

    # CHANGED: This is our single final JSON
    final_output = {
        "podcast_script_dialogues_only": final_dialogues.strip(),
        "podcast_script_as_markdown": final_markdown.strip()
    }

    return final_output    


















#_____________________________________________________________________________________________________________________________
# OLD CODE

# @measure_time
# def podacast_segment_generator(podcast_title, podcast_keyideas, extracted_data, number_of_speakers, podcast_length:str, speaker_names:dict, llm:AzureChatOpenAI, external_kn_call=False):

#     logger.debug(f"Podcast Conversation segment generation started. Total Speakers are: {number_of_speakers}")
#     logger.debug(f"Configuring the podcast for Length: {podcast_length}")
#     logger.debug(f"Speaker details are : {speaker_names}")

#     podcast_length = podcast_length.lower()
    
#     if podcast_length == "short":
#         conversation_type = (
#             "Since this is a short-length podcast, each speaker's dialogue should be concise and to the point. However, ensure it remains engaging and conversational."
#         )
#         external_knowledge_length = "400-600 words"
#         podcast_structure = {
#             "introduction": "2-3 exchanges",
#             "structured_discussion": "4-6 exchanges",
#             "deep_dive": "4-6 exchanges",
#             "interactive_discussions": "4-6 exchanges",
#             "highlights_key_takeaways": "3-4 exchanges",
#             "question_rounds": "2-3 exchanges",
#             "closing_thoughts_and_outro": "3-4 exchanges"
#         }

#     elif podcast_length == "moderate":
#         conversation_type = (
#             "Since this is a moderately long podcast, each speaker's dialogue can be slightly longer with more detailed sentences. Still, ensure the conversation remains engaging and natural."
#         )
#         external_knowledge_length = "800-1000 words"
#         podcast_structure = {
#             "introduction": "3-5 exchanges",
#             "structured_discussion": "8-10 exchanges",
#             "deep_dive": "10-15 exchanges",
#             "interactive_discussions": "10-15 exchanges",
#             "highlights_key_takeaways": "8-10 exchanges",
#             "question_rounds": "5-7 exchanges",
#             "closing_thoughts_and_outro": "3-4 exchanges"
#         }

#     elif podcast_length == "long":
#         conversation_type = (
#             "Since this is a long-format podcast, each speaker's dialogue should be more extensive and composed of longer sentences. Yet, maintain a lively and conversational tone throughout."
#         )
#         external_knowledge_length = "2000-3000 words"
#         podcast_structure = {
#             "introduction": "3-5 exchanges",
#             "structured_discussion": "15-20 exchanges",
#             "deep_dive": "15-20 exchanges",
#             "interactive_discussions": "15-20 exchanges",
#             "highlights_key_takeaways": "15-20 exchanges",
#             "question_rounds": "7-10 exchanges",
#             "closing_thoughts_and_outro": "3-4 exchanges"
#         }

#     else:
#         logger.error(f"Unknown podcast length specified. Please check {podcast_length}")
#     #     raise ValueError("Unknown podcast length specified.")
    
#     # if external_kn_call:
#     #     external_knowledge = external_knowledge_on_topic(podcast_title=podcast_title, length=external_knowledge_length, llm=llm)
#     # else:
#     #     external_knowledge = "Not Needed As User has not allowed to use any external knowledge. Keep the Podcast as per the topic."


#     # prompt = f"""  
#     # You are an intelligent AI Podcast segment Generation. Your task is to generate structured conversational podcast segment between speaker relevant to the content.

#     # Podcast title : {podcast_title}
#     # Podcast_keyideas : {podcast_keyideas}  
#     # Content : {extracted_data}
#     # Number of speakers : {number_of_speakers}
#     # Length of Podcast : {podcast_length}

#     # Instructions for Generating Podcast Segment:  (Must Follow Everytime)

#     # 1. Use the Provided Key Ideas to Create a Coherent Podcast Segment  
#     #     - Expand the key ideas into a structured conversation, ensuring smooth transitions.  
#     #     - Generate unique content based on the inputs.  
#     #     - Assign distinct roles to each speaker based on their relevance to the topic.
#     #     - The number of speakers should align with provided number of speaker. 

#     # 2. Ensure a Logical Flow of Conversation 
#     #   - Start with an engaging introduction explaining why the topic matters. 
#     #   - Make sure the host speaker : {speaker_names['speaker1']} — must warmly welcome **all** speakers in **one** exchange, explicitly announcing each speaker's name, role, or expertise.
#     #     example:- Hello and welcome to Gaming Goldmine, the show where we explore the most exciting trends shaping the future of tech and innovation. I’m your host, James White, and today we’re diving into one of the fastest-growing industries in India—gaming. From mobile apps to esports arenas, the Indian gaming sector is booming, and there’s a lot to unpack.To help us break it all down, I’m joined by two brilliant guests. First up, we have Andrew Smith, a seasoned market analyst who’s been tracking digital entertainment trends across Asia. Welcome, Andrew!
#     #   - After the host introduces them in a single exchange, each guest can provide a brief greeting or follow-up remark in their own exchange, but **should not** repeat the entire role introduction. # <-- Added for clarity
#     #   - Break down the main discussion into meaningful segments that reflect the key ideas.  
#     #   - Conclude with thought-provoking questions and final insights.  

#     # 3. Adapt the Depth Based on Podcast Length(Strictly Follow): 
#     #   - Short (25-30 Exchanges): Keep discussions focused and impactful.  
#     #   - Moderate (40-80 Exchanges): Allow for expert opinions and deeper insights.  
#     #   - Long (Always More than 80 Exchanges): Include debates, audience engagement, and case studies.  

#     # 4. Ensure that in the generated Podcast segment the Speaker Names are dynamically adjusted. Based on {number_of_speakers} and speaker details dictionary provided above.

#     # 5. Speaker details to add in the dynamic podcast script. Make sure to add this information in the right place.
#     #     You should always add speaker detail in the beginning of the conversation. For each speaker i (from 1 to {number_of_speakers}), if the value in title_to_voice_model for that speaker is an empty string, then use "no speaker i". Otherwise, use the corresponding name from the dictionary. 
#     #     Example:
#     #         Speaker 1 : {speaker_names["speaker1"] if speaker_names["speaker1"] else "no speaker 1"}
#     #         Speaker 2 : {speaker_names["speaker2"] if speaker_names["speaker2"] else "no speaker 2"}
#     #         ... and so on for all speakers up to {number_of_speakers}.
#     #         You can get the information all of these speakers from the below dictionary:
#     #         {speaker_names}

#     # 6. Segment to provided in the Podcast Script. 
#     #   Ensure that the generated podcast script has outline the segments which are mentioned below, **in this exact order**, with the **exact number of textual exchanges** stated for each segment. 
#     #   **Each speaker's single response counts as ONE exchange.** # <-- Emphasized
#     #   Please also strictly adhere to the conversation depth as mentioned here: {conversation_type}
        
#     #     1. **Introduction** 
#     #       - Number of Exchanges: {podcast_structure["introduction"]}
          
#     #     2. **Structured Discussion** 
#     #       - Number of Exchanges: {podcast_structure["structured_discussion"]}
        
#     #     3. **Deep Dive**  
#     #       - Number of Exchanges: {podcast_structure["deep_dive"]}
          
#     #     4. **Interactive Discussions**  
#     #       - Number of Exchanges: {podcast_structure["interactive_discussions"]}

#     #     5. **Highlights Important Key Takeaway**  
#     #       - Number of Exchanges: {podcast_structure["highlights_key_takeaways"]}
        
#     #     6. **Some Question Rounds**
#     #       - Number of Exchanges: {podcast_structure["question_rounds"]}

#     #     7. **Closing Thoughts and Outro**
#     #       - Number of Exchanges: {podcast_structure["closing_thoughts_and_outro"]}

#     # **Important**: 
#     # - Do not skip or merge segments. 
#     # - Maintain a clear label for each segment. 
#     # - If you provide fewer than the minimum number of exchanges for each segment, your response does not comply with the instructions. # <-- Added for clarity
#     # - For a longer or moderate podcast you must have to generate the podcast segment precisely as per the conversation exchanges mentioned in the Rule 6 above.
#     # - You can utilise external knowledge source to extend the conversation to make it more intuitive and lengthy. But it depends on the user if he want to use it or not. If you can see there is no external knowledge source then stick to the provided content. 

#     # Below is the external knowledge base helpful to extend the podcast and make it follow the precise number of conversation exchange mentioned in Rule 6.
#     # External knowledge base: {external_knowledge}: May not be Needed.

#     # NOTE:
#     # The podcast should have atleast 70 percentage from the provided content and remaining 30 percentage from external sources(If available otherwise 100% stick to provided content and Key Ideas.). External sources are just for extending the segment when the podcast length is moderate and long. And it will be used only for adhering to the number of exchanges mentioned in rule 6.

#     # ### Feedback Recieved(from the user of this app): 
#     # - User complained about podcast segment not having a strict pattern. Make sure podcast always follow pattern and rules mentioned above.
#     # - It will showcase the dialogue flow keeping the exact speaker name and respective dialogues. Avoid using words like host, guest speaker etc. There should not be presence of any other words like [INTRO MUSIC FADES IN],[INTRO MUSIC FADES OUT] etc. 
#     # NON ADHERENCE TO ABOVE RULES ARE AGAINST COMPLIANCE WHICH ARE NOT ACCEPTABLE.



#     # Output Format: 
#     # Generate the output in the following JSON format:
    
#     # {{
#     #     "podcast_script_dialogues_only": "Generated podcast segment as a form of dialogues between various speakers mentioned above."
#     #     "podcast_script_as_markdown": "Generated Podcast script as markdown showcasing the segment wise dialogues between the speakers."

#     # }}

#     # Response:

#     # """

#     # response = llm.invoke(prompt)
#     # # Clean and parse JSON response
#     # response_content = response.content.strip().strip("```json").strip("```")
#     # parsed_response = json.loads(response_content)
#     # return parsed_response
