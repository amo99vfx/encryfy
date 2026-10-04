from flask import Flask, request, jsonify, render_template_string
import cv2
import numpy as np
import base64

from reader import extract_encfry_data


app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ENCFRY Scanner</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4ead8;
            text-align: center;
            padding: 20px;
        }

        h1 {
            color: #4b3621;
        }

        .box {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }

        video {
            width: 100%;
            max-width: 500px;
            border-radius: 15px;
            background: black;
        }

        button {
            margin-top: 15px;
            padding: 14px 25px;
            font-size: 17px;
            border: none;
            border-radius: 10px;
            background: #6b4f2a;
            color: white;
        }

        button:active {
            transform: scale(0.97);
        }

        #status {
            margin-top: 20px;
            font-size: 18px;
        }

        #result {
            margin-top: 20px;
            padding: 15px;
            background: #f8f1e5;
            border-radius: 12px;
            display: none;
            white-space: pre-wrap;
            text-align: left;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🦊 ENCFRY Scanner</h1>

    <p>
        Point your phone camera at the ENCFRY image
        displayed on the laptop.
    </p>

    <video id="video" autoplay playsinline></video>

    <br>

    <button onclick="scanImage()">
        📷 Scan ENCFRY Image
    </button>

    <div id="status">
        Camera starting...
    </div>

    <div id="result"></div>

</div>

<canvas id="canvas" style="display:none;"></canvas>


<script>

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const status = document.getElementById("status");
const result = document.getElementById("result");


async function startCamera() {

    try {

        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: {
                    ideal: "environment"
                }
            },
            audio: false
        });

        video.srcObject = stream;

        status.innerText =
            "📷 Camera ready — point it at the ENCFRY image.";

    }

    catch(error) {

        status.innerText =
            "❌ Camera access failed: " + error;

    }
}


async function scanImage() {

    status.innerText = "🔍 Scanning...";

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    canvas.toBlob(async function(blob) {

        const formData = new FormData();

        formData.append(
            "image",
            blob,
            "camera.jpg"
        );

        try {

            const response = await fetch(
                "/scan",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if(data.success) {

                status.innerText =
                    "✅ ENCFRY image detected!";

                result.style.display = "block";

                result.innerText =
                    "Method: " + data.method +
                    "\\n\\nEncrypted data extracted successfully.\\n\\n" +
                    "Now enter the password on the laptop reader.";

            }

            else {

                status.innerText =
                    "❌ ENCFRY image not detected.";

                result.style.display = "block";

                result.innerText =
                    data.error;

            }

        }

        catch(error) {

            status.innerText =
                "❌ Scanner error.";

            result.style.display = "block";

            result.innerText =
                error.toString();

        }

    }, "image/jpeg", 0.95);
}


startCamera();

</script>

</body>
</html>
"""


@app.route("/")
def index():

    return render_template_string(HTML)


@app.route("/scan", methods=["POST"])
def scan():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image received."
        })

    file = request.files["image"]

    data = file.read()

    image_array = np.frombuffer(
        data,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        return jsonify({
            "success": False,
            "error": "Could not read camera image."
        })

    try:

        payload, method = extract_encfry_data(image)

        # Store payload temporarily for next step.
        app.config["LAST_PAYLOAD"] = payload

        return jsonify({
            "success": True,
            "method": method
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":

    print()
    print("=" * 55)
    print("              ENCFRY PHONE SCANNER")
    print("=" * 55)
    print()
    print("Starting secure HTTPS server...")
    print()
    print("On your phone open:")
    print()
    print("https://YOUR-LAPTOP-IP:5000")
    print()
    print("Phone and laptop must be on the SAME Wi-Fi.")
    print()
    print("=" * 55)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context="adhoc",
        debug=False
    )