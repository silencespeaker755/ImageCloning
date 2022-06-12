from flask import Flask, send_file, session, request, jsonify
from flask_cors import CORS
import utils
import os
import cv2
import random
import numpy as np

async_mode = None
app = Flask(__name__)

app = Flask(
    __name__, static_folder="frontend/build/static", template_folder="frontend/build"
)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/user_data"
CORS(app)

if not os.path.exists("static/user_data"):
    os.makedirs("static/user_data")


@app.route("/", methods=["GET"])
def index():
    # return render_template("index.html")
    return None


@app.route("/upload-image", methods=["POST"])
def upload_image():
    file = request.files["image"]
    image_id = f"{random.randint(0, 99):02d}"
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}.png")
    file.save(image_path)
    return image_id


@app.route("/image", methods=["GET"])
def load_image():
    args = request.args
    image_id = args["image_id"]
    return send_file(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}.png"), "image/png"
    )


@app.route("/crop", methods=["POST"])
def crop():
    req = request.get_json()
    image_id = req["image_id"]
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}.png")
    image = cv2.imread(image_path)
    print(req["points"])
    cropped, points = utils.crop_image(image, req["points"])
    np.save(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}_cropped.npy"), points
    )
    cv2.imwrite(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}_cropped.png"), cropped
    )
    return image_id + "_cropped"


@app.route("/clone", methods=["POST"])
def clone():
    req = request.get_json()
    source_id = req["source_id"]
    source_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{source_id}.png")
    points = np.load(os.path.join(app.config["UPLOAD_FOLDER"], f"{source_id}.npy"))
    print(points)
    dest_id = req["dest_id"]
    dest_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{dest_id}.png")
    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
