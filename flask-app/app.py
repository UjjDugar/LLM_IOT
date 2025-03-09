from flask import Flask, render_template, request, jsonify
import json
import pyaudio
import wave
import tempfile
import os
from openai import OpenAI
import time
from speech_to_text import record_audio, transcribe_audio
from light_control_llm import GPT

def parse_llm_response(llm_response, debug=False):
    # Find first hex code and intensity
    hex1_start = llm_response.find('#')
    hex1 = llm_response[hex1_start:hex1_start+7].lower()
    if debug: print(f"Hex1: {hex1}")
    i1 = float(next(c for c in llm_response[hex1_start+7:] if c.isdigit()))
    if debug: print(f"Intensity1: {i1}")

    # Find second hex code and intensity 
    hex2_start = llm_response[hex1_start+1:].find('#') + hex1_start + 1
    hex2 = llm_response[hex2_start:hex2_start+7].lower()
    if debug: print(f"Hex2: {hex2}")
    i2 = float(next(c for c in llm_response[hex2_start+7:] if c.isdigit()))
    if debug: print(f"Intensity2: {i2}")

    return hex1, i1, hex2, i2


with open('api_key.txt', 'r') as f:
    api_key = f.read()

app = Flask(__name__)

# Default light settings
light_settings = {
    "ambient": {"intensity": 0.3},
    "light1": {"intensity": 15., "position": {"x": 2, "y": 3, "z": 2}, "color": "#ffffff"},
    "light2": {"intensity": 15., "position": {"x": -2, "y": 3, "z": 2}, "color": "#ffffff"},
    "light3": {"intensity": 0, "position": {"x": 2, "y": 3, "z": -2}, "color": "#ffffff"},
    "light4": {"intensity": 0, "position": {"x": -2, "y": 3, "z": -2}, "color": "#ffffff"}
}


@app.route('/')
def index():
    # Pass light settings to template
    return render_template('index.html', light_settings=json.dumps(light_settings))

@app.route('/get_settings')
def get_settings():
    return jsonify(light_settings)

@app.route('/update_light', methods=['POST'])
def update_light():
    global light_settings
    data = request.json
    
    # Update the light settings
    if 'light' in data and data['light'] in light_settings:
        light_name = data['light']
        if 'intensity' in data:
            light_settings[light_name]['intensity'] = float(data['intensity'])
        if 'position' in data:
            light_settings[light_name]['position'] = data['position']
        if 'color' in data:
            light_settings[light_name]['color'] = data['color']
    
    return jsonify({"status": "success", "settings": light_settings})

# Function to programmatically control lights
def set_light(light_name, intensity=None, position=None, color=None):
    global light_settings
    
    if light_name in light_settings:
        if intensity is not None:
            light_settings[light_name]['intensity'] = float(intensity)
        if position is not None:
            light_settings[light_name]['position'] = position
        if color is not None:
            light_settings[light_name]['color'] = color
        
        return True
    return False


if __name__ == '__main__':

    intensity_factor = 5

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


    llm_response = gpt.get_response(prompt)

    print("\n GPT response:\n", llm_response+ "\n")


    hex1, i1, hex2, i2 = parse_llm_response(llm_response)
    i1 = i1 * intensity_factor
    i2 = i2 * intensity_factor
    print(f"Hex1: {hex1}, Intensity1: {i1}")
    print(f"Hex2: {hex2}, Intensity2: {i2}")

    set_light('light1', color=hex1, intensity=i1)
    set_light('light2', color=hex2, intensity=i2)

    set_light('light3', color=hex2, intensity=i1)      
    set_light('light4', color=hex1, intensity=i2)
    
    app.run(debug=False, port=5001)

