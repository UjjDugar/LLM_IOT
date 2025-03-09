import pyaudio
import wave
import tempfile
import os
from openai import OpenAI
import time
from speech_to_text import record_audio, transcribe_audio
from light_control_llm import GPT
with open('api_key.txt', 'r') as f:
    api_key = f.read()

print(f'API key: {api_key}')

while True:
    print("Press Enter to start recording, and press 'q' to stop recording...")
    input()  # Wait for Enter to start
    
    # Initialize PyAudio
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    audio = pyaudio.PyAudio()
    
    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)
    
    print("Recording... Press 'q' to stop")
    
    frames = []
    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            
            # Check if 'q' was pressed (non-blocking)
            import sys, select
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = input()
                if line.lower() == 'q':
                    break
                
    except KeyboardInterrupt:
        pass
    
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
    
    audio_file_path = temp_filename
    
    # Transcribe audio
    print("Transcribing...")
    transcription = transcribe_audio(api_key, audio_file_path)
    
    # Output transcription
    print("\nTranscription:")
    print(transcription)
    print("\n" + "-"*50 + "\n")

    gpt = GPT(model_name="gpt-3.5-turbo")
    with open('prompt_start.txt', 'r') as f:
        prompt_start = f.read()
    
    prompt = prompt_start + transcription

    print(f'Prompt: {prompt}')

    print(gpt.get_response(prompt))

    break # remove this if want to run multiple times

