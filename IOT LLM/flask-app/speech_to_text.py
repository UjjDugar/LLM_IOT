import pyaudio
import wave
import tempfile
import os
from openai import OpenAI
import time

def record_audio(seconds=5):
    """Record audio from microphone for specified number of seconds"""
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    audio = pyaudio.PyAudio()
    
    print("Recording... Speak now")
    
    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    frames = []
    
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Recording finished")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the recorded data as a WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
        temp_filename = temp_audio_file.name
    
    wf = wave.open(temp_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return temp_filename

def transcribe_audio(api_key, audio_file_path):
    """Transcribe audio file using OpenAI's API"""
    client = OpenAI(api_key=api_key)
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        return f"Error during transcription: {str(e)}"
    finally:
        # Clean up the temp file
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

if __name__ == "__main__":

    with open('api_key.txt', 'r') as f:
        api_key = f.read()

    print(f'API key: {api_key}')

    while True:
        # Get recording duration
        try:
            seconds = float(input("Enter recording duration in seconds (or 0 to exit): "))
            if seconds <= 0:
                break
        except ValueError:
            print("Please enter a valid number")
            continue
        
        # Record audio
        audio_file_path = record_audio(seconds)
        
        # Transcribe audio
        print("Transcribing...")
        transcription = transcribe_audio(api_key, audio_file_path)
        
        # Output transcription
        print("\nTranscription:")
        print(transcription)
        print("\n" + "-"*50 + "\n")


