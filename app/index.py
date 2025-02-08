from flask import Flask, render_template, jsonify, request
from collections import deque
from datetime import datetime
# import google.generativeai as genai
from statistics import mean
from threading import Lock
import time

app = Flask(__name__)

# Configure Gemini
# genai.configure(api_key='YOUR_GEMINI_API_KEY')
# model = genai.GenerativeModel('gemini-pro')

# Data storage
class SensorBuffer:
    def __init__(self, buffer_size=10):
        self.temperature_buffer = deque(maxlen=buffer_size)
        self.humidity_buffer = deque(maxlen=buffer_size)
        self.light_buffer = deque(maxlen=buffer_size)
        self.last_average_time = time.time()
        self.lock = Lock()
        self.last_personality = None
        self.buffer_size = buffer_size

    def add_reading(self, temp, humidity, light):
        with self.lock:
            self.temperature_buffer.append(temp)
            self.humidity_buffer.append(humidity)
            self.light_buffer.append(light)

    def get_averages(self):
        with self.lock:
            if len(self.temperature_buffer) < self.buffer_size:
                return None
            
            return {
                'temperature': mean(self.temperature_buffer),
                'humidity': mean(self.humidity_buffer),
                'light': mean(self.light_buffer)
            }

    def clear_buffers(self):
        with self.lock:
            self.temperature_buffer.clear()
            self.humidity_buffer.clear()
            self.light_buffer.clear()

# Initialize sensor buffer
sensor_buffer = SensorBuffer()

# Thresholds for sensor values
THRESHOLDS = {
    'temperature': {
        'good': (20, 25),
        'ok': (18, 28),
    },
    'humidity': {
        'good': (45, 55),
        'ok': (40, 60),
    },
    'light': {
        'good': (600, 800),
        'ok': (500, 1000),
    }
}

def get_status(value, sensor_type):
    """Determine status (good, ok, bad) for a sensor value"""
    good_range = THRESHOLDS[sensor_type]['good']
    ok_range = THRESHOLDS[sensor_type]['ok']
    
    if good_range[0] <= value <= good_range[1]:
        return 'good'
    elif ok_range[0] <= value <= ok_range[1]:
        return 'ok'
    else:
        return 'bad'

# def generate_personality(averages):
#     """Generate personality based on averaged sensor data"""
#     # Calculate overall status
#     statuses = {
#         'temperature': get_status(averages['temperature'], 'temperature'),
#         'humidity': get_status(averages['humidity'], 'humidity'),
#         'light': get_status(averages['light'], 'light')
#     }
    
#     health_score = sum(status == 'good' for status in statuses.values()) * 100 / 3

#     prompt = f"""
#     Based on my average readings over the last 10 seconds:
#     Temperature: {averages['temperature']:.1f}°C ({statuses['temperature']})
#     Humidity: {averages['humidity']:.1f}% ({statuses['humidity']})
#     Light: {averages['light']:.1f} lux ({statuses['light']})
#     Overall health: {health_score:.0f}%

#     Create a 2-3 sentence response that:
#     1. Expresses my personality and current mood based on these conditions
#     2. Provides financial advice that matches my state (good conditions = optimistic advice, poor conditions = conservative advice)
#     3. If any values are suboptimal, include a subtle hint about what I need
#     """

#     try:
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         app.logger.error(f"Error generating personality: {e}")
#         return "I'm feeling a bit quiet right now, but still monitoring things!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sensor-update', methods=['POST'])
def sensor_update():
    try:
        # Print incoming request data for debugging
        print("Received request data:", request.data)
        
        # Ensure we have JSON data
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        print("Parsed JSON data:", data)
        
        # Validate the data has required fields
        required_fields = ['temperature', 'humidity', 'light']
        if not all(field in data for field in required_fields):
            print("Missing required fields")
            return jsonify({"error": "Missing required sensor data"}), 400

        # Create response with status for each sensor
        # if data is not None:
        response_data = {
            'sensor_data': {
                'temperature': float(data['temperature']),
                'humidity': float(data['humidity']),
                'light': float(data['light'])
            },
            'status': {
                'temperature': 'good',
                'humidity': 'good',
                'light': 'good'
            },
            'personality': 'Test personality response'
        }
        
        print("Sending response:", response_data)
        return jsonify(response_data)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)