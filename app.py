import streamlit as st
import os
import time
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from chains import research_company, generate_questions, analyze_interview
from voice_utils import text_to_speech, transcribe_audio

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="InterviewAI | Personal Mock Assistant",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #e0e0e0;
        font-family: 'Outfit', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 15px rgba(37, 117, 252, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 117, 252, 0.4);
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .question-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: -webkit-linear-gradient(#f8f9fa, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .feedback-card {
        background: rgba(40, 40, 60, 0.8);
        border-radius: 15px;
        padding: 1.5rem;
        border-left: 5px solid #2575fc;
        margin-top: 1rem;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        background: rgba(37, 117, 252, 0.2);
        color: #2575fc;
        font-weight: 800;
        border: 1px solid #2575fc;
    }
    h1, h2, h3 { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "step" not in st.session_state:
    st.session_state.step = "setup"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "transcript_file" not in st.session_state:
    # Ensure transcript is saved in the current directory
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    st.session_state.transcript_file = os.path.join(workspace_dir, f"interview_transcript_{int(time.time())}.txt")

# Check for API Key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("❌ GOOGLE_API_KEY not found in .env. Please add it to start the interview.")
    st.stop()

def save_answer(question, answer):
    with open(st.session_state.transcript_file, "a") as f:
        f.write(f"Question: {question}\nAnswer: {answer}\n\n")

# Header
st.title("🤖 InterviewAI")
st.markdown("### Master Your Mock Interview with Voice & AI")

# Sidebar
with st.sidebar:
    st.header("How it works")
    st.info("""
    1. Enter your Job Description & Company.
    2. We research the company and generate 5 targeted questions.
    3. Practice with Voice Input (STT) and AI Audio feedback (TTS).
    4. Get a deep performance analysis.
    """)
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- STEP 1: SETUP ---
if st.session_state.step == "setup":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Step 1: Preparation")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g. Google, OpenAI, Tesla")
    with col2:
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Software Engineer")
        
    jd = st.text_area("Job Description", height=200, placeholder="Paste the JD here...")
    
    if st.button("Generate Interview"):
        if company_name and jd:
            with st.spinner("Researching company and crafting questions..."):
                research = research_company(company_name, jd)
                st.session_state.questions = generate_questions(research, jd)
                st.session_state.step = "interview"
                st.session_state.current_q_idx = 0
                st.session_state.answers = []
                st.rerun()
        else:
            st.error("Please provide both the company name and job description.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- STEP 2: INTERVIEW ---
elif st.session_state.step == "interview":
    idx = st.session_state.current_q_idx
    questions = st.session_state.questions
    
    if idx < len(questions):
        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
        st.progress((idx) / len(questions))
        st.markdown(f"<p style='color: #888;'>Question {idx + 1} of {len(questions)}</p>", unsafe_allow_html=True)
        
        current_question = questions[idx]
        st.markdown(f"<h2 class='question-title'>{current_question}</h2>", unsafe_allow_html=True)
        
        # TTS for question (Voice Output)
        if f"played_q_{idx}" not in st.session_state:
            with st.spinner("AI is speaking..."):
                audio_path = text_to_speech(current_question)
                st.audio(audio_path, format="audio/mp3", autoplay=True)
                st.session_state[f"played_q_{idx}"] = True
        
        # Voice Input (STT)
        st.write("---")
        st.markdown("#### 🎤 Answer with your voice:")
        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            key=f"recorder_{idx}",
        )
        
        # Manual text input backup
        st.markdown("#### ⌨️ Or type your answer:")
        manual_answer = st.text_input("Transcription / Text Answer", key=f"text_{idx}")
        
        if audio:
            st.markdown("Processing your voice answer...")
            transcription = transcribe_audio(audio['bytes'])
            st.success(f"Transcribed: {transcription}")
            if st.button("Confirm Transcription", key=f"confirm_{idx}"):
                save_answer(current_question, transcription)
                st.session_state.answers.append(transcription)
                st.session_state.current_q_idx += 1
                st.rerun()
        elif manual_answer:
            if st.button("Submit Answer", key=f"submit_{idx}"):
                save_answer(current_question, manual_answer)
                st.session_state.answers.append(manual_answer)
                st.session_state.current_q_idx += 1
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.session_state.step = "analysis"
        st.rerun()

# --- STEP 3: ANALYSIS ---
elif st.session_state.step == "analysis":
    with st.spinner("Aggregating feedback and scoring your performance..."):
        feedback = analyze_interview(st.session_state.questions, st.session_state.answers)
        
    st.balloons()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🏆 Interview Performance Report")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Preparedness", f"{feedback['overall_preparedness_score']}/10")
    with col2:
        st.metric("Overall Answer Quality", f"{feedback['overall_answer_score']}/10")
    
    st.markdown("---")
    
    for i, item in enumerate(feedback['feedbacks']):
        with st.expander(f"Question {i+1}: {item['question'][:60]}..."):
            st.markdown(f"**Your Answer:** {item['user_answer']}")
            st.markdown(f"<div class='feedback-card'>", unsafe_allow_html=True)
            st.markdown(f"**💡 Feedback:** {item['feedback']}")
            st.markdown(f"**✨ Ideal Answer:** {item['ideal_answer']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Transcript Download
    with open(st.session_state.transcript_file, "r") as f:
        transcript_data = f.read()
    st.download_button("Download Full Transcript", transcript_data, file_name="transcript.txt")
    
    if st.button("Start New Mock Interview"):
        st.session_state.clear()
        st.rerun()
