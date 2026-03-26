from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
import cv2
import shutil

app = FastAPI()

# 🎨 Anime Style (AI-like)
def anime_style(frame):
    img = cv2.bilateralFilter(frame, 9, 250, 250)
    return img

# 🎨 Comic Style
def comic_style(frame):
    return cv2.stylization(frame, sigma_s=60, sigma_r=0.6)

# 🎬 Video Processing
def process_video(input_path, output_path, style):
    cap = cv2.VideoCapture(input_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path,
                          cv2.VideoWriter_fourcc(*'mp4v'),
                          fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if style == "anime":
            result = anime_style(frame)
        else:
            result = comic_style(frame)

        out.write(result)

    cap.release()
    out.release()


# 🌐 Stylish UI (Embedded)
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Toon Magic AI</title>
        <style>
            body {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-align: center;
                font-family: Arial;
            }
            h1 {
                font-size: 40px;
            }
            button {
                padding: 12px 25px;
                font-size: 18px;
                border: none;
                border-radius: 10px;
                background: #ff7b00;
                color: white;
                cursor: pointer;
            }
            input, select {
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
        </style>
    </head>
    <body>

    <h1>🎬 Toon Magic AI</h1>
    <p>Turn Videos into Cartoon Magic 🎨</p>

    <input type="file" id="videoInput"><br><br>

    <select id="style">
        <option value="anime">Anime</option>
        <option value="comic">Comic</option>
    </select><br><br>

    <button onclick="uploadVideo()">Convert</button>

    <script>
    async function uploadVideo() {
        let file = document.getElementById("videoInput").files[0];
        let style = document.getElementById("style").value;

        let formData = new FormData();
        formData.append("file", file);
        formData.append("style", style);

        let res = await fetch("/upload/", {
            method: "POST",
            body: formData
        });

        let blob = await res.blob();
        let url = URL.createObjectURL(blob);

        let a = document.createElement("a");
        a.href = url;
        a.download = "toon_magic_output.mp4";
        a.click();
    }
    </script>

    </body>
    </html>
    """


# 📤 Upload API
@app.post("/upload/")
async def upload(file: UploadFile = File(...), style: str = Form(...)):
    input_path = "input.mp4"
    output_path = "output.mp4"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    process_video(input_path, output_path, style)

    return FileResponse(output_path, media_type="video/mp4", filename="toon_magic_output.mp4")
