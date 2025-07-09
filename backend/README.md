## 🎙️ Podcast Generator Application

### 🚀 Tagline:

**"Agentic AI-Powered Podcast Creation from Any Document or URL using LLMs and Azure TTS"**

---

### 🧾 Overview

This project is a **Generative AI-based Podcast Generator** that takes in any **PDF document or web URL**, extracts the content, and transforms it into a **multi-speaker podcast script** using a modular **agentic workflow** powered by **Azure OpenAI LLMs**. It then formats the script using SSML and finally converts it into high-quality **AI-narrated audio using Azure Text-to-Speech (TTS)**.

The app utilizes multiple **specialized agents**—each responsible for a specific sub-task in the pipeline, such as document parsing, title generation, podcast planning, dialogue scripting, SSML formatting, and audio synthesis. The entire pipeline is accessible via a **Streamlit UI** or a **FastAPI backend**.

---

### 🤖 Agentic Workflow

The system is built around **functional AI agents**, each encapsulated into its own function or module, enabling modularity, error isolation, and easier future expansion:

1. **Text Extraction Agent**

   * `extract_text_from_pdf` / `extract_text_from_url`
   * Converts document/URL into raw text

2. **Title Generator Agent**

   * `title_generator`
   * Generates an engaging podcast title using LLM

3. **Podcast Planner Agent**

   * `generate_podcast_plan`
   * Summarizes key ideas based on desired podcast length and speaker count

4. **Script Writer Agent**

   * `podacast_segment_generator`
   * Produces multi-speaker conversational script using the ideas and extracted content

5. **SSML Formatter Agent**

   * `generate_ssml_script`
   * Transforms the script into SSML format with tone, pitch, and pauses

6. **Audio Generator Agent**

   * `convert_to_audiov2`
   * Uses Azure TTS to synthesize final podcast audio from SSML

Each agent is invoked in sequence to simulate an **autonomous multi-agent pipeline**, orchestrated through modular scripts (`app.py`, `streamlit_app.py`, and `main_api.py`).

---

### 🔧 Key Features

* 📄 Accepts both **PDF files** and **URLs** as content sources
* 🧠 Uses **Azure OpenAI LLM (GPT-4o-mini)** to:

  * Generate podcast title
  * Plan key discussion points
  * Generate full speaker dialogues
* 🤖 Built on a **multi-agent workflow** for modular, extensible design
* 🗣️ Converts dialogues into **SSML format** for naturalistic speech
* 🔊 Uses **Azure Cognitive Services TTS** to generate multi-speaker podcast audio
* 🎛️ Clean and user-friendly **Streamlit frontend**
* 🌐 Synchronous **FastAPI backend** with endpoint: `/generate_podcast`
* 💾 Automatically saves podcast script, SSML, and audio

---

### 🛠️ Tools & Technologies Used

| Tool                         | Purpose                               | Why This Tool?                                    |
| ---------------------------- | ------------------------------------- | ------------------------------------------------- |
| **Python**                   | Main programming language             | Fast prototyping and extensive GenAI libraries    |
| **Streamlit**                | Frontend UI                           | Minimal setup, clean UI for showcasing GenAI apps |
| **FastAPI**                  | REST API backend                      | High-performance, async-friendly                  |
| **Azure OpenAI GPT-4o-mini** | LLM for text generation               | Powerful conversational capabilities              |
| **Azure Text-to-Speech**     | Voice synthesis                       | Supports SSML, realistic voice switching          |
| **LangChain**                | Prompt templating and LLM integration | Clean abstraction for chaining LLM calls          |
| **Pydub**                    | Audio post-processing                 | Supports MP3 merging and saving                   |
| **BeautifulSoup**            | Web scraping                          | For URL-based input extraction                    |
| **PyPDF2**                   | PDF parsing                           | Lightweight and simple for text extraction        |

---

### 🔄 Full Pipeline

1. **User Input**: Upload PDF or enter a URL
2. **Text Extraction Agent**: Extract raw text content
3. **Title Generator Agent**: Generate a creative episode title
4. **Podcast Planner Agent**: Derive discussion themes and flow
5. **Script Writer Agent**: Generate multi-speaker dialogue
6. **SSML Formatter Agent**: Format with voice modulation tags
7. **Audio Generator Agent**: Synthesize final audio via Azure TTS
8. **Output Storage**: Save `.mp3`, `.xml`, and `.txt`

---

### 📥 Inputs & 📤 Outputs

* **Inputs**:

  * PDF Document or Website URL
  * Number of Speakers (1 to 5)
  * Speaker Names
  * Desired podcast length: `short`, `moderate`, or `long`

* **Outputs**:

  * Podcast title
  * Full speaker-wise conversation (as markdown)
  * SSML XML file
  * Audio podcast in `.mp3`

---

### 💼 Real-World Applications

* 📰 **News summarization and narration**
* 📚 **Educational podcasting**
* ✍️ **Blog-to-audio** content repurposing
* 🧑‍🦯 **Accessibility use cases** for the visually impaired

---

### ⚙️ How to Run

```bash
# Clone the repo and setup virtual environment
pip install -r requirements.txt

# Set Azure credentials in 'cred.env'
AZURE_OPENAI_API_KEY=...
AZURE_SPEECH_KEY=...
...

# Run Streamlit app
streamlit run streamlit_app.py

# OR run FastAPI
uvicorn main_api:app --reload
```

---

### 🔮 Future Enhancements

* 🎞️ Add avatar-based video generation
* 🗣️ Custom voice cloning support
* 🌍 Multi-language podcasting
* 🧠 Reinforcement-based agent selection
* 📤 Cloud-based hosting (e.g., Azure App Service or Streamlit Cloud)

---

### 🙏 Acknowledgments

* [Azure Cognitive Services](https://azure.microsoft.com/en-in/products/cognitive-services/)
* [OpenAI via Azure](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)

---

