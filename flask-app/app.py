from flask import Flask, render_template, request, jsonify
import json

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
    hex1 = "#ff0000"
    hex2 = "#0000ff"
    int1 = 28.
    int2 = 32.

    set_light('light1', color=hex1, intensity=int1)
    set_light('light2', color=hex2, intensity=int2)

    set_light('light3', color=hex2, intensity=int1)
    set_light('light4', color=hex1, intensity=int2)
    
    app.run(debug=True)