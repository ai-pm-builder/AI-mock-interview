# AI Mock Interview Assistant 🤖🎙️

An advanced AI-powered mock interview tool that uses voice for a realistic experience. It researches companies, generates targeted questions, and provides deep performance analysis.

## Features
- **Company Research**: Automatically analyzes the company and job description using Gemini.
- **Voice-First**: Listen to the interviewer speak and answer with your own voice.
- **Smart Analysis**: Get scores on preparedness, answer quality, and tailored feedback.
- **Transcript Storage**: Automatically saves your interview session to a file.

## Tech Stack
- Frontend: **Streamlit**
- Logic: **LangChain** (integrated with Gemini API)
- LLM: **Gemini 2.0 Flash**
- Voice: **gTTS** (Text-to-Speech) & **Gemini Multimodal** (Speech-to-Text)

## Setup
1. **API Key**: Create a `.env` file in the root directory and add your Google API Key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you encounter issues with `pyaudio`, you may need to install it via `conda` or download a pre-built wheel for Windows.*

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Enter the **Company Name** and **Job Description**.
2. Click **Generate Interview**.
3. Listen to the AI read the first question.
4. Use the **Mic Recorder** to record your answer.
5. Review the transcription and proceed to the next question.
6. After 5 questions, view your **Detailed Performance Report**.
