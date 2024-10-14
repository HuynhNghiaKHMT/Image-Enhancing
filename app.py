import os
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import cv2
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép tất cả nguồn

UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'

# Đảm bảo thư mục tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Render trang HTML
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Trỏ đến file index.html ở thư mục hiện tại

# Upload ảnh
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Không có ảnh trong yêu cầu'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Không có file nào được chọn'}), 400
    
    # Lưu file vào thư mục uploads
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # Trả về đường dẫn của ảnh đã upload
    return jsonify({'file_path': '/' + file_path})

# Xử lý ảnh
@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    process_type = data.get('process_type')
    image_path = data.get('image_path').lstrip('/')

    image = cv2.imread(image_path)

    if process_type == 'gaussian_noise':
        image = add_gaussian_noise(image)
    elif process_type == 'salt_pepper_noise':
        image = add_salt_and_pepper_noise(image)

    elif process_type == 'denoise_mean':
        image = denoise_mean(image)
    elif process_type == 'denoise_median':
        image = denoise_median(image)

    elif process_type == 'sharpen_laplacian':
        image = sharpen_laplacian(image)
    elif process_type == 'sharpen_unsharp':
        image = sharpen_unsharp(image)
    elif process_type == 'sharpen_highpass':
        image = sharpen_highpass(image)

    elif process_type == 'edge_sobel':
        image = detect_sobel(image)
    elif process_type == 'edge_prewitt':
        image = detect_prewitt(image)
    elif process_type == 'edge_canny':
        image = detect_canny(image)

    # Lưu ảnh đã xử lý
    processed_image_path = os.path.join(PROCESSED_FOLDER, 'processed_' + os.path.basename(image_path))
    cv2.imwrite(processed_image_path, image)

    # Trả về đường dẫn của ảnh đã xử lý
    return jsonify({'processed_image_path': '/' + processed_image_path})

# Tải ảnh đã xử lý
@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

# Các hàm xử lý ảnh
def add_gaussian_noise(image):
    noise = np.random.normal(0, 20, image.shape)
    noisy_image = cv2.add(image.astype(np.float32), noise.astype(np.float32))
    return np.clip(noisy_image, 0, 255).astype(np.uint8)

def add_salt_and_pepper_noise(image):
    salt_prob = 0.02
    pepper_prob = 0.02
    noisy_image = np.copy(image)
    num_salt = np.ceil(salt_prob * image.size * 0.5)
    num_pepper = np.ceil(pepper_prob * image.size * 0.5)

    # Thêm nhiễu muối
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    noisy_image[coords[0], coords[1], :] = 255

    # Thêm nhiễu tiêu
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    noisy_image[coords[0], coords[1], :] = 0

    return noisy_image

def denoise_mean(image):
    return cv2.blur(image, (5, 5))

def denoise_median(image):
    return cv2.medianBlur(image, 5)

def sharpen_laplacian(image):
    image = image.astype(np.uint8)
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    laplacian = np.uint8(np.absolute(laplacian))
    sharpened = cv2.subtract(image, laplacian)
    
    return sharpened

def sharpen_unsharp(image):
    gaussian = cv2.GaussianBlur(image, (9, 9), 10.0)
    unsharp = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
    return unsharp

def sharpen_highpass(image):
    image = image.astype(np.float32)
    blurred = cv2.GaussianBlur(image, (9, 9), 10.0)
    high_pass = cv2.subtract(image, blurred)
    sharpened = cv2.add(image, high_pass)
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    return sharpened

def detect_sobel(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)
    return cv2.convertScaleAbs(sobel_combined)

def detect_prewitt(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
    kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
    prewitt_x = cv2.filter2D(gray, -1, kernelx)
    prewitt_y = cv2.filter2D(gray, -1, kernely)
    return cv2.convertScaleAbs(prewitt_x + prewitt_y)

def detect_canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, 100, 200)

if __name__ == '__main__':
    app.run(debug=True)
