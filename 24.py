import cv2
import whisper
import openai
import time

# Set up OpenCV to extract frames
def extract_frames(video_path, interval=1):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frames.append(frame)
        frame_count += 1
    cap.release()
    return frames

# Set up whisper for speech-to-text transcription
def transcribe_audio(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    return result["text"]

# Set up GPT-4 for summarizing content
def summarize_content(text):
    openai.api_key = "your-openai-api-key"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following text: {text}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Generate timestamps for key moments
def generate_timestamps(text, summary):
    sentences = text.split(". ")
    summary_sentences = summary.split(". ")
    timestamps = []
    for sentence in summary_sentences:
        for i, s in enumerate(sentences):
            if sentence in s:
                timestamps.append(f"{i+1}: {sentence}")
                break
    return timestamps

# Main function to summarize video
def summarize_video(video_path):
    frames = extract_frames(video_path)
    text = transcribe_audio(video_path)
    summary = summarize_content(text)
    timestamps = generate_timestamps(text, summary)
    
    print("Summary:")
    print(summary)
    print("\nTimestamps:")
    for timestamp in timestamps:
        print(timestamp)

# Example usage
video_path = "example_video.mp4"
summarize_video(video_path)