import math
import joblib
import mediapipe as mp
import cv2
import numpy as np
import threading
import time
import queue
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from utils import draw_landmarks_on_image, add_transparent_image

# Load the trained models
with open("archive/predictor_v1.pkl", "rb") as f:
    classifier = joblib.load(f)

with open("archive/scaler_v1.pkl", "rb") as f:
    scaler = joblib.load(f)

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult

# Global variables
predictions = []
drawn_frame = np.array([])
frame_queue = queue.Queue(maxsize=10)
prediction_queue = queue.Queue(maxsize=5)
camera_running = False
camera_ready = threading.Event()

# Game state variables
current_word = ""
current_letter_index = 0
completed_letters = set()
game_active = False
game_window_created = False

# Web console server variables
word_input_result = None
word_input_server = None
web_console_port = 8765

# Globals for one-hand-at-a-time logic
tracked_hand_index = None
no_hand_counter = 0
NO_HAND_THRESHOLD = 1  # Number of consecutive frames with no hands before resetting

class WebConsoleHandler(BaseHTTPRequestHandler):
    """HTTP handler for web-based game console"""
    
    def log_message(self, format, *args):
        """Suppress server logs"""
        pass
    
    def do_GET(self):
        """Serve the game console or API endpoints"""
        global word_input_result
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sign Language Game Console</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        overflow: hidden;
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }
                    .header h1 {
                        font-size: 32px;
                        margin-bottom: 10px;
                    }
                    .header p {
                        opacity: 0.9;
                        font-size: 16px;
                    }
                    .status-bar {
                        background: #f8f9fa;
                        padding: 20px 30px;
                        border-bottom: 2px solid #e9ecef;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .status-item {
                        flex: 1;
                        text-align: center;
                    }
                    .status-label {
                        font-size: 12px;
                        color: #6c757d;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        margin-bottom: 5px;
                    }
                    .status-value {
                        font-size: 24px;
                        font-weight: bold;
                        color: #333;
                    }
                    .game-area {
                        padding: 30px;
                    }
                    .word-display {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .word-letters {
                        display: flex;
                        justify-content: center;
                        gap: 10px;
                        flex-wrap: wrap;
                    }
                    .letter-box {
                        width: 60px;
                        height: 80px;
                        border: 3px solid #dee2e6;
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 36px;
                        font-weight: bold;
                        color: #adb5bd;
                        background: #f8f9fa;
                        transition: all 0.3s;
                    }
                    .letter-box.current {
                        border-color: #667eea;
                        background: #e7f0ff;
                        color: #667eea;
                        transform: scale(1.1);
                        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                    }
                    .letter-box.completed {
                        border-color: #38ef7d;
                        background: #d4f4e2;
                        color: #11998e;
                    }
                    .target-letter {
                        margin: 30px 0;
                        text-align: center;
                    }
                    .target-letter-label {
                        font-size: 14px;
                        color: #6c757d;
                        margin-bottom: 10px;
                    }
                    .target-letter-box {
                        display: inline-block;
                        width: 120px;
                        height: 120px;
                        border: 4px solid #667eea;
                        border-radius: 15px;
                        background: #e7f0ff;
                        font-size: 72px;
                        font-weight: bold;
                        color: #667eea;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .controls {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin-top: 30px;
                    }
                    button {
                        padding: 15px 25px;
                        font-size: 16px;
                        font-weight: bold;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: all 0.2s;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    .btn-primary {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .btn-success {
                        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                        color: white;
                    }
                    .btn-warning {
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        color: white;
                    }
                    button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    }
                    button:active {
                        transform: translateY(0);
                    }
                    .input-section {
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin-top: 20px;
                    }
                    input[type="text"] {
                        width: 100%;
                        padding: 12px;
                        font-size: 16px;
                        border: 2px solid #dee2e6;
                        border-radius: 8px;
                        margin-bottom: 10px;
                        text-transform: uppercase;
                    }
                    input[type="text"]:focus {
                        outline: none;
                        border-color: #667eea;
                    }
                    .message {
                        text-align: center;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 10px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    .message.success {
                        background: #d4f4e2;
                        color: #11998e;
                    }
                    .message.info {
                        background: #e7f0ff;
                        color: #667eea;
                    }
                    .inactive-message {
                        text-align: center;
                        color: #6c757d;
                        font-size: 18px;
                        padding: 40px 20px;
                    }
                    @keyframes pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.5; }
                    }
                    .pulsing {
                        animation: pulse 2s infinite;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1> Sign Language Game</h1>
                        <p>Practice ASL alphabet recognition</p>
                    </div>
                    
                    <div class="status-bar">
                        <div class="status-item">
                            <div class="status-label">Status</div>
                            <div class="status-value" id="game-status">Ready</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">Progress</div>
                            <div class="status-value" id="progress">0/0</div>
                        </div>
                        <div class="status-item">
                            <div class="status-label">Current Word</div>
                            <div class="status-value" id="current-word">-</div>
                        </div>
                    </div>
                    
                    <div class="game-area" id="game-area">
                        <div class="inactive-message">
                            Press a button below to start playing!
                        </div>
                    </div>
                    
                    <div style="padding: 0 30px 30px;">
                        <div class="controls">
                            <button class="btn-primary" onclick="startDefaultGame()">
                                Start (HELLO)
                            </button>
                            <button class="btn-warning" onclick="resetGame()">
                                Reset Game
                            </button>
                        </div>
                        
                        <div class="input-section">
                            <input type="text" id="custom-word" placeholder="Enter custom word (letters only)..." 
                                   pattern="[A-Za-z]+" maxlength="20">
                            <button class="btn-success" onclick="startCustomGame()" style="width: 100%;">
                                Start Custom Word
                            </button>
                        </div>
                    </div>
                </div>
                
                <script>
                    let currentGameState = null;
                    
                    function updateUI() {
                        fetch('/api/state')
                            .then(response => response.json())
                            .then(state => {
                                currentGameState = state;
                                
                                // Update status bar
                                document.getElementById('game-status').textContent = state.active ? 'Playing' : 'Ready';
                                document.getElementById('progress').textContent = state.completed + '/' + state.total;
                                document.getElementById('current-word').textContent = state.word || '-';
                                
                                // Update game area
                                const gameArea = document.getElementById('game-area');
                                
                                if (state.active && state.word) {
                                    let html = '<div class="word-display">';
                                    html += '<div class="word-letters">';
                                    
                                    for (let i = 0; i < state.word.length; i++) {
                                        let className = 'letter-box';
                                        if (i < state.current_index) {
                                            className += ' completed';
                                        } else if (i === state.current_index) {
                                            className += ' current';
                                        }
                                        html += '<div class="' + className + '">' + state.word[i] + '</div>';
                                    }
                                    
                                    html += '</div></div>';
                                    
                                    if (state.current_index < state.word.length) {
                                        html += '<div class="target-letter">';
                                        html += '<div class="target-letter-label">Show this sign:</div>';
                                        html += '<div class="target-letter-box pulsing">' + state.word[state.current_index] + '</div>';
                                        html += '</div>';
                                    }
                                    
                                    gameArea.innerHTML = html;
                                } else if (state.completed === state.total && state.total > 0) {
                                    gameArea.innerHTML = '<div class="message success"> Congratulations! You completed the word: ' + state.word + '</div>';
                                } else {
                                    gameArea.innerHTML = '<div class="inactive-message">Press a button below to start playing!</div>';
                                }
                            })
                            .catch(err => console.error('Error fetching state:', err));
                    }
                    
                    function startDefaultGame() {
                        fetch('/api/start/HELLO')
                            .then(response => response.json())
                            .then(() => updateUI());
                    }
                    
                    function startCustomGame() {
                        const word = document.getElementById('custom-word').value.trim().toUpperCase();
                        if (!word || !/^[A-Z]+$/.test(word)) {
                            alert('Please enter only letters!');
                            return;
                        }
                        fetch('/api/start/' + word)
                            .then(response => response.json())
                            .then(() => {
                                document.getElementById('custom-word').value = '';
                                updateUI();
                            });
                    }
                    
                    function resetGame() {
                        fetch('/api/reset')
                            .then(response => response.json())
                            .then(() => updateUI());
                    }
                    
                    // Allow Enter key to submit custom word
                    document.getElementById('custom-word').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            startCustomGame();
                        }
                    });
                    
                    // Update UI every 200ms
                    setInterval(updateUI, 200);
                    updateUI();
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/api/state':
            # Return current game state as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            state = {
                'active': game_active,
                'word': current_word,
                'current_index': current_letter_index,
                'completed': len(completed_letters),
                'total': len(current_word) if current_word else 0
            }
            
            import json
            self.wfile.write(json.dumps(state).encode())
            
        elif self.path.startswith('/api/start/'):
            # Start game with word from URL
            word = self.path.replace('/api/start/', '').upper()
            if word and word.isalpha():
                word_input_result = word
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
        elif self.path == '/api/reset':
            # Reset game
            word_input_result = 'RESET'
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
        else:
            self.send_response(404)
            self.end_headers()

def print_result(result, output_image, timestamp_ms):
    try:
        landmarks_ls = result.hand_world_landmarks
        handedness_ls = result.handedness
        global predictions
        global drawn_frame
        global tracked_hand_index
        global no_hand_counter
        predictions = []

        if len(landmarks_ls) == 0:
            # No hands detected
            no_hand_counter += 1
            if no_hand_counter >= NO_HAND_THRESHOLD:
                tracked_hand_index = None
                drawn_frame = np.zeros_like(output_image.numpy_view())
            return
        else:
            no_hand_counter = 0

        # If only one hand is detected, always use that hand
        if len(landmarks_ls) == 1:
            tracked_hand_index = handedness_ls[0][0].index
            main_hand_idx = 0
        else:
            # Multiple hands detected
            # If no hand is tracked, pick the first detected hand
            if tracked_hand_index is None:
                tracked_hand_index = handedness_ls[0][0].index

            # Find the hand with the tracked index
            main_hand_idx = None
            for idx, handedness in enumerate(handedness_ls):
                if handedness[0].index == tracked_hand_index:
                    main_hand_idx = idx
                    break

            # If tracked hand not found, switch to the first available hand
            if main_hand_idx is None:
                tracked_hand_index = handedness_ls[0][0].index
                main_hand_idx = 0

        if main_hand_idx is not None:
            landmarks = np.array([[landmark.x, landmark.y, landmark.z] for landmark in landmarks_ls[main_hand_idx]]).flatten()
            handedness = handedness_ls[main_hand_idx][0].index
            data = scaler.transform(np.array([[handedness] + landmarks.tolist()]))
            prediction = classifier.predict(data)
            predictions.append(prediction[0])

            # Send prediction to main thread via queue (thread-safe)
            try:
                prediction_queue.put_nowait(prediction[0])
            except queue.Full:
                # If queue is full, remove oldest prediction and add new one
                try:
                    prediction_queue.get_nowait()
                    prediction_queue.put_nowait(prediction[0])
                except:
                    pass

            # Create a HandLandmarkerResult-like object with only the main hand
            class SingleHandResult:
                def __init__(self, hand_landmarks, handedness):
                    self.hand_landmarks = [hand_landmarks]
                    self.handedness = [handedness]
                    self.hand_world_landmarks = []
            main_result = SingleHandResult(result.hand_landmarks[main_hand_idx], result.handedness[main_hand_idx])
            drawn_frame = draw_landmarks_on_image(output_image.numpy_view(), main_result, predictions)
        else:
            # Tracked hand not found, do not update drawn_frame
            pass
    except Exception as e:
        print(f"Error in print_result: {e}")

def run_camera_feed():
    """Run the camera feed in a separate thread"""
    global camera_running, frame_queue, camera_ready
    
    # Setup MediaPipe HandLandmarker
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path="./models/hand_landmarker.task"),
        running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        result_callback=print_result,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Initialize camera with AVFoundation backend for better performance on macOS
    cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    if not cam.isOpened():
        print("Error: Could not open camera")
        return

    # Set camera to highest FPS possible
    cam.set(cv2.CAP_PROP_FPS, 60)  # Request 60 FPS
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG codec for higher FPS
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce latency

    timestamp = 0
    frame_count = 0
    
    # Get actual camera FPS after configuration
    camera_fps = cam.get(cv2.CAP_PROP_FPS)
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera configured:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {camera_fps}")
    print(f"  Backend: AVFoundation")

    # FPS measurement variables
    fps_start_time = time.time()
    fps_frame_count = 0
    display_fps = 0.0
    last_fps_update = fps_start_time

    # Performance tracking
    processing_times = []
    mediapipe_times = []

    print("Starting camera feed...")
    camera_running = True
    camera_ready.set()  # Signal that camera is ready

    with HandLandmarker.create_from_options(options) as landmarker:
        while cam.isOpened() and camera_running:
            loop_start = time.time()
            
            ret, frame = cam.read()
            if not ret:
                print("Failed to read frame from camera")
                break

            # Generate timestamp in milliseconds for MediaPipe
            frame_count += 1
            fps_frame_count += 1
            timestamp = int(frame_count * (1000.0 / camera_fps))
            
            # Process every frame (no interval throttling)
            mp_start = time.time()
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            landmarker.detect_async(mp_img, timestamp)
            mp_time = (time.time() - mp_start) * 1000  # Convert to ms
            mediapipe_times.append(mp_time)

            # Add overlay
            if drawn_frame.size > 0:
                frame = add_transparent_image(frame, drawn_frame)

            # Calculate FPS every second
            current_time = time.time()
            if current_time - last_fps_update >= 1.0:
                display_fps = fps_frame_count / (current_time - last_fps_update)
                fps_frame_count = 0
                last_fps_update = current_time
                
                # Print performance metrics
                avg_mp_time = np.mean(mediapipe_times[-30:]) if mediapipe_times else 0
                avg_total_time = np.mean(processing_times[-30:]) if processing_times else 0
                print(f"FPS: {display_fps:.1f} | MediaPipe: {avg_mp_time:.1f}ms | Total: {avg_total_time:.1f}ms")
            
            # Draw FPS on frame
            cv2.putText(frame, f"FPS: {display_fps:.1f}", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Put frame in queue for main thread to display
            try:
                frame_queue.put_nowait(cv2.flip(frame, 1))
            except queue.Full:
                # If queue is full, remove oldest frame and add new one
                try:
                    frame_queue.get_nowait()
                    frame_queue.put_nowait(cv2.flip(frame, 1))
                except:
                    pass

            # Track total loop time
            loop_time = (time.time() - loop_start) * 1000
            processing_times.append(loop_time)

    print("\n" + "="*60)
    print("CAMERA PERFORMANCE SUMMARY:")
    print(f"  Average FPS: {len(processing_times) / (time.time() - fps_start_time):.1f}")
    print(f"  Avg MediaPipe time: {np.mean(mediapipe_times):.1f}ms")
    print(f"  Avg Total loop time: {np.mean(processing_times):.1f}ms")
    print(f"  Max loop time: {np.max(processing_times):.1f}ms")
    print("="*60)

    cam.release()
    camera_running = False
    print("Camera feed stopped")

def create_game_interface():
    """Deprecated - now using web console"""
    pass

def process_predictions():
    """Process predictions from the queue on the main thread"""
    global current_word, current_letter_index, completed_letters, game_active
    
    try:
        while not prediction_queue.empty():
            prediction = prediction_queue.get_nowait()
            
            if game_active and prediction and current_letter_index < len(current_word):
                target_letter = current_word[current_letter_index]
                if prediction.upper() == target_letter.upper():
                    # Correct letter detected
                    completed_letters.add(current_letter_index)
                    current_letter_index += 1
                    print(f"✅ Correct! '{prediction}' detected. Progress: {len(completed_letters)}/{len(current_word)}")
                    
                    if current_letter_index >= len(current_word):
                        print(f"🎉 Congratulations! You've completed the word: {current_word}")
                        game_active = False
                else:
                    # Wrong letter detected
                    print(f"❌ Detected '{prediction}' but expected '{target_letter}'")
    except queue.Empty:
        pass

def check_word_input():
    """Check if word was submitted via web console"""
    global word_input_result
    
    if word_input_result is not None:
        word = word_input_result
        word_input_result = None  # Reset
        
        if word == 'RESET':
            reset_game()
        else:
            start_custom_game(word)
            print(f"✅ Starting game with custom word: {word}")

def start_game():
    """Start a new game with a default word"""
    global current_word, current_letter_index, completed_letters, game_active
    current_word = "HELLO"  # Default word
    current_letter_index = 0
    completed_letters = set()
    game_active = True
    print(f"Game started! Practice the word: {current_word}")

def start_custom_game(word):
    """Start a new game with a custom word"""
    global current_word, current_letter_index, completed_letters, game_active
    current_word = word.upper()
    current_letter_index = 0
    completed_letters = set()
    game_active = True
    print(f"Game started! Practice the word: {current_word}")

def reset_game():
    """Reset the game"""
    global current_word, current_letter_index, completed_letters, game_active
    current_word = ""
    current_letter_index = 0
    completed_letters = set()
    game_active = False
    print("Game reset. Press 's' to start a new game.")

def enter_word_input_mode():
    """Deprecated - now handled by web console"""
    pass

def update_camera_display():
    """Update camera display from main thread"""
    global camera_running, frame_queue
    
    if camera_running:
        try:
            # Get frame from queue
            frame = frame_queue.get_nowait()
            
            # Add game status overlay if game is active
            if game_active and current_letter_index < len(current_word):
                # Add status text to frame
                status_text = f"Target: {current_word[current_letter_index]}"
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add progress text
                progress_text = f"Progress: {len(completed_letters)}/{len(current_word)}"
                cv2.putText(frame, progress_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Camera", frame)
            
            # Check for ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                camera_running = False
                return False
        except queue.Empty:
            pass
    
    return True

def main():
    global camera_running, word_input_server
    
    # Start web console server
    def run_server():
        """Run HTTP server in background"""
        global word_input_server
        try:
            word_input_server = HTTPServer(('localhost', web_console_port), WebConsoleHandler)
            print(f"🌐 Web console started at http://localhost:{web_console_port}")
            word_input_server.serve_forever()
        except Exception as e:
            print(f"Server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)  # Give server time to start
    
    # Open web console in browser
    webbrowser.open(f'http://localhost:{web_console_port}')
    
    # Display instruction image
    image_path = "/Users/leduckien/Downloads/handSignInstructions.png"
    try:
        image = cv2.imread(image_path)
        if image is not None:
            cv2.imshow("Hand Sign Instructions", image)
    except Exception as e:
        print(f"Could not load instruction image: {e}")
    
    # Start camera in a separate thread
    camera_thread = threading.Thread(target=run_camera_feed, daemon=True)
    camera_thread.start()
    
    # Wait for camera to be ready
    camera_ready.wait(timeout=5.0)
    
    print("\n" + "="*60)
    print("🤟 Sign Language Game Started!")
    print("="*60)
    print(f"📱 Web console: http://localhost:{web_console_port}")
    print("📸 Camera window showing hand detection")
    print("🎮 Use the web browser to control the game")
    print("⌨️  Press ESC in camera window to quit")
    print("="*60 + "\n")
    
    # Main game loop
    while camera_running:
        # Update camera display
        if not update_camera_display():
            break
        
        # Process predictions
        process_predictions()
        
        # Check for word input from web console
        check_word_input()
        
        # Handle keyboard input (only ESC to quit)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    
    # Cleanup
    camera_running = False
    if word_input_server:
        word_input_server.shutdown()
    cv2.destroyAllWindows()
    print("\n👋 Game ended. Thanks for playing!")

if __name__ == "__main__":
    main() 