import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key not found in .env file.")
    st.stop()
genai.configure(api_key=api_key)

# Summarization prompt
prompt = """
You are a YouTube video summarizer. Summarize the video transcript into key points: """

# Extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        query = urlparse(youtube_video_url)
        video_id = parse_qs(query.query).get("v")
        if not video_id:
            raise ValueError("Invalid YouTube URL.")
        transcript = YouTubeTranscriptApi.get_transcript(video_id[0])
        return " ".join([i["text"] for i in transcript])
    except Exception as e:
        return f"Error: {str(e)}"

# Generate summary
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.models().get(name="models/gemini-pro")
        response = model.generate(input_text=prompt + transcript_text)
        return response["output"]
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app
st.title("YouTube Transcript Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    query = urlparse(youtube_link)
    video_id = parse_qs(query.query).get("v", [None])[0]
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    else:
        st.warning("Invalid YouTube URL.")

if st.button("Get Detailed Notes"):
    if youtube_link and video_id:
        transcript_text = extract_transcript_details(youtube_link)
        if "Error" in transcript_text:
            st.error(transcript_text)
        else:
            summary = generate_gemini_content(transcript_text, prompt)
            if "Error" in summary:
                st.error(summary)
            else:
                st.markdown("## Detailed Notes:")
                st.write(summary)
    else:
        st.warning("Enter a valid YouTube link.")
