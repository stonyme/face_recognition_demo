from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
import json
import time
import dlib
import cv2

app = Flask(__name__)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


# Liveness detection function (optimized)
def detect_blink(eye_points, facial_landmarks):
    left = (
        facial_landmarks.part(eye_points[0]).x,
        facial_landmarks.part(eye_points[0]).y,
    )
    right = (
        facial_landmarks.part(eye_points[3]).x,
        facial_landmarks.part(eye_points[3]).y,
    )
    top = (
        facial_landmarks.part(eye_points[1]).x,
        facial_landmarks.part(eye_points[1]).y,
    )
    bottom = (
        facial_landmarks.part(eye_points[5]).x,
        facial_landmarks.part(eye_points[5]).y,
    )

    # Calculate the aspect ratio of the eye
    horizontal_distance = np.linalg.norm(
        np.array([right]) - np.array([left])
    )  # Euclidean distance
    vertical_distance = np.linalg.norm(
        np.array([top]) - np.array([bottom])
    )  # Euclidean distance

    ratio = horizontal_distance / vertical_distance

    # Output debug information
    print(
        f"Horizontal distance: {horizontal_distance}, Vertical distance: {vertical_distance}, Ratio: {ratio}"
    )

    # Return True if blink detected (ratio < threshold), False otherwise
    return ratio < 0.2  # Threshold adjusted to be more lenient


@app.route("/liveness", methods=["POST"])
def liveness_detection():
    try:
        # Step 1: 接收和解码图片数据
        data = request.get_json()
        if "image" not in data:
            return jsonify({"success": False, "message": "No image data provided."})

        # 解码 Base64 图片数据
        image_data = data["image"].split(",")[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = np.array(image)

        # Step 2: 转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)  # 使用 dlib 检测人脸

        if not faces:
            return jsonify(
                {"success": False, "message": "No faces detected in the image."}
            )

        # Step 3: 遍历检测到的人脸，检查是否有活体
        blink_detected = False
        for face in faces:
            landmarks = predictor(gray, face)

            # 定义眼睛的特征点
            left_eye = [36, 37, 38, 39, 40, 41]
            right_eye = [42, 43, 44, 45, 46, 47]

            # 检测眨眼
            if detect_blink(left_eye, landmarks) or detect_blink(right_eye, landmarks):
                blink_detected = True
                break

        # Step 4: 根据检测结果返回数据
        if blink_detected:
            return jsonify(
                {
                    "success": True,
                    "liveness": True,
                    "message": "Liveness detected (blink).",
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "liveness": False,
                    "message": "No liveness detected. Please blink or adjust environment.",
                }
            )

    except Exception as e:
        # Step 5: 捕获异常，返回详细错误信息
        return jsonify(
            {"success": False, "message": f"Error during liveness detection: {str(e)}"}
        )


UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# In-memory database (for demo purposes only)
users = {}
next_user_id = 1
last_recognition_time = 0
RECOGNITION_INTERVAL = 1.0  # Minimum interval between recognition requests in seconds


def get_all_users():
    return [
        (user_id, user["name"], user["encoding"]) for user_id, user in users.items()
    ]


def get_user(user_id):
    return users.get(user_id)


def delete_user_from_db(user_id):
    if user_id in users:
        del users[user_id]


def update_user_name(user_id, new_name):
    if user_id in users:
        users[user_id]["name"] = new_name


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global next_user_id

    if "image" not in request.files or "name" not in request.form:
        return (
            jsonify({"success": False, "message": "Image and name are required."}),
            400,
        )

    image_file = request.files["image"]
    name = request.form["name"]

    if image_file.filename == "":
        return jsonify({"success": False, "message": "No selected file."}), 400

    filename = secure_filename(image_file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{next_user_id}.jpg")
    image_file.save(save_path)

    # Process image for face encoding
    image = face_recognition.load_image_file(save_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        os.remove(save_path)
        return (
            jsonify({"success": False, "message": "No face detected in the image."}),
            400,
        )

    users[next_user_id] = {"name": name, "encoding": json.dumps(encodings[0].tolist())}
    next_user_id += 1

    return jsonify({"success": True, "message": "Image uploaded successfully."})


@app.route("/gallery", methods=["GET"])
def gallery():
    user_list = [
        {
            "id": user_id,
            "name": user["name"],
            "image": f"/{UPLOAD_FOLDER}/{user_id}.jpg",
        }
        for user_id, user in users.items()
    ]
    return jsonify({"users": user_list})


@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Delete from database and file system
    delete_user_from_db(user_id)
    image_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.jpg")
    if os.path.exists(image_path):
        os.remove(image_path)

    return jsonify({"message": "User deleted successfully"})


@app.route("/edit_user/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    new_name = request.form["name"]
    user = get_user(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    update_user_name(user_id, new_name)
    return jsonify({"message": "User updated successfully"})


@app.route("/recognize", methods=["POST"])
def recognize():
    global last_recognition_time

    current_time = time.time()
    if current_time - last_recognition_time < RECOGNITION_INTERVAL:
        return (
            jsonify({"message": "Recognition request too frequent, please wait."}),
            429,
        )

    last_recognition_time = current_time

    # 获取图像数据
    data = request.get_json()
    image_data = data["image"].split(",")[1]
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    image = np.array(image)

    # 检测人脸位置和特征
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)

    recognition_results = []

    for encoding, location in zip(encodings, face_locations):
        best_match = None
        best_distance = float("inf")  # 初始化为无限大
        threshold = 0.6  # 相似度阈值，越小越严格

        # 遍历所有用户，计算相似度
        for user_id, user in users.items():
            known_encoding = np.array(json.loads(user["encoding"]))
            distance = np.linalg.norm(known_encoding - encoding)  # 欧几里得距离
            if distance < best_distance and distance < threshold:
                best_distance = distance
                best_match = {
                    "id": user_id,
                    "name": user["name"],
                    "location": {
                        "top": location[0],
                        "right": location[1],
                        "bottom": location[2],
                        "left": location[3],
                    },
                    "distance": best_distance,
                }

        # 如果有匹配结果，添加到结果列表
        if best_match:
            recognition_results.append(best_match)

    return jsonify({"results": recognition_results})


if __name__ == "__main__":
    app.run(debug=True)
