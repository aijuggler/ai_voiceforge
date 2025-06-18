## 🎙️ Podcast Generator Application

### 🚀 Tagline:

**"AI-Powered Podcast Creation from Any Document or URL using LLMs and Azure TTS"**

---

### 🧾 Overview

This project is a **Generative AI-based Podcast Generator** that takes in any **PDF document or web URL**, extracts the content, and transforms it into a **human-like podcast script** using **Azure OpenAI LLMs**. It then formats the script using SSML and finally converts it into high-quality **AI-narrated audio using Azure Text-to-Speech (TTS)**.

The app supports multiple speakers, realistic conversation formatting, and allows generation of podcasts with a few clicks via a **Streamlit UI** or **FastAPI backend**.

---

### 🔧 Key Features

* 📄 Accepts both **PDF files** and **URLs** as content sources.
* 🧠 Uses **Azure OpenAI LLM (GPT-4o-mini)** to:

  * Generate podcast title
  * Plan key discussion points
  * Generate full speaker dialogues
* 🗣️ Converts dialogues into **SSML format** for realistic tone, pauses, and voice inflections.
* 🔊 Uses **Azure Cognitive Services TTS** to generate multi-speaker podcast audio.
* 🎛️ Clean and user-friendly **Streamlit frontend**.
* 🌐 Synchronous **FastAPI backend** with endpoint: `/generate_podcast`
* 💾 Automatically saves podcast script, SSML, and audio.

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

### 🔄 Project Workflow

1. **Input Selection**: User uploads a PDF or enters a URL.
2. **Text Extraction**: Content extracted via PyPDF2 or BeautifulSoup.
3. **LLM Script Generation**:

   * Title generation
   * Key ideas summarization
   * Multi-speaker podcast script creation
4. **SSML Conversion**: Script is converted to SSML with speaker-specific styles.
5. **Audio Synthesis**: Azure TTS generates MP3 podcast.
6. **Output Saved**:

   * `.mp3` file
   * `.xml` SSML file
   * `.txt` podcast script

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

### 📂 Folder Structure (Simplified)

```
ai_voiceforge/
├── app.py                    # Podcast script generation logic
├── main_api.py              # REST API endpoint
├── streamlit_app.py         # Web frontend
├── audio_generation.py      # SSML + Audio synthesis logic
├── podcast_creator.py       # LLM-based content generation
├── saved_audio/             # Output MP3s
├── document_store/          # Sample inputs
├── saved_podcast_data/      # Generated SSML/XML/Text
├── cred.env                 # Azure credentials (not committed)
```

---

### 🔮 Future Enhancements

* 🎞️ Add avatar-based video generation
* 🗣️ Custom voice cloning support
* 🌍 Multi-language podcasting
* 📤 Cloud-based hosting (e.g., Azure App Service or Streamlit Cloud)

---

### 🙏 Acknowledgments

* [Azure Cognitive Services](https://azure.microsoft.com/en-in/products/cognitive-services/)
* [OpenAI via Azure](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)

---

### 📄 License

MIT License

---

This README was auto-generated based on full code analysis of the `ai_voiceforge` project. All descriptions match the implementation logic and architecture found in the uploaded repository.
