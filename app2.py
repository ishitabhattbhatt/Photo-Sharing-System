from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)
key = None

def generate_frames():
    global key
    while True:
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            if key == ord('c'):  # Capture photo when 'c' is pressed
                cv2.imwrite('captured_photo.jpg', frame)
                key = None  # Reset key
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_photo')
def capture_photo():
    global key
    key = ord('c')  # Set key to 'c' to capture photo
    return 'Photo captured!'

if __name__ == '__main__':
    app.run(debug=True)
