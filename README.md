# 人脸识别系统 / Face Recognition and Liveness Detection System

## 项目描述 / Project Description

本项目是一个基于 Flask 的人脸识别系统。系统使用摄像头捕捉图像并检测人脸。

This project is a Flask-based face recognition system. The system captures images from a camera to detect faces.

---

## 功能特性 / Features

1. **人脸识别 / Face Recognition**: 通过上传的图片或视频流进行人脸检测与识别。
2. **后台管理 / Admin Management**: 支持头像的增删查改功能。
3. **摄像头实时检测 / Real-Time Detection**: 实时视频流中的人脸框绘制和活体检测。

---

## 技术栈 / Tech Stack

- **后端 / Backend**: Flask, Python
- **图像处理 / Image Processing**: OpenCV, dlib, face_recognition, Pillow
- **前端 / Frontend**: HTML, JavaScript, CSS

---

## 安装步骤 / Installation Steps

1. **克隆项目 / Clone the Project**:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **安装依赖 / Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **运行项目 / Run the Project**:

   ```bash
   python app.py
   ```

4. **访问应用 / Access the Application**:
   打开浏览器并访问 `http://127.0.0.1:5000`。

   Open a browser and visit `http://127.0.0.1:5000`.

---

## 文件结构 / File Structure

```plaintext
<project-folder>
├── app.py                 # 主应用文件 / Main application file
├── static/                # 静态资源文件 / Static resources
├── requirements.txt       # 依赖库 / Dependency list
└── README.md              # 项目说明 / Project documentation
```

---

## API 接口 / API Endpoints

### 1. **人脸识别 / Face Recognition**

- **URL**: `/recognize`
- **方法 / Method**: POST
- **参数 / Parameters**:
  - `image` (Base64 编码的图像 / Base64 encoded image)
- **返回 / Response**:
  ```json
  {
    "success": true,
    "results": [
      {
        "name": "User1",
        "distance": 0.42,
        "location": {
          "top": 50,
          "left": 100,
          "bottom": 150,
          "right": 200
        }
      }
    ]
  }
  ```

---

## 注意事项 / Notes

- 确保设备已安装必要的依赖库，特别是 dlib 和 OpenCV。
- 摄像头权限需要在浏览器或操作系统中启用。
- 测试时请使用光线良好的环境。

Ensure that necessary dependencies, especially dlib and OpenCV, are installed. Camera permissions must be enabled in the browser or operating system. Test in a well-lit environment.

---

## 许可 / License

此项目基于 MIT 许可发布。

This project is licensed under the MIT License.
