from flask import Flask, send_file, session, request, jsonify
from flask_cors import CORS
import utils
import os
import cv2
import random
import numpy as np

import clone

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

    points = np.array([[point["x"], point["y"]] for point in req["points"]], dtype=int)
    cropped, points = utils.crop_image(image, points)

    np.save(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}_cropped.npy"), points
    )
    cv2.imwrite(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}_cropped.png"), cropped
    )
    return image_id + "_cropped"


@app.route("/clone", methods=["POST"])
def clone_image():
    req = request.get_json()
    print(req)
    source_info = req["source_info"]

    source_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{source_info['id']}.png")
    source = cv2.imread(source_path)
    points = np.load(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{source_info['id']}.npy")
    )

    rotate = -source_info["rotate"]
    source, points = utils.resize_image(
        source, points, source_info["width"], source_info["height"]
    )
    source, points = utils.rotate_image(source, points, rotate)

    x, y = int(source_info["position"]["x"]), int(source_info["position"]["y"])
    position = utils.central_position(
        (x, y), source_info["width"], source_info["height"], rotate
    )
    position = np.flip(position)

    dest_info = req["dest_info"]
    dest_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{dest_info['id']}.png")
    dest = cv2.imread(dest_path)
    dest, _ = utils.resize_image(
        dest, np.array([[0, 0]]), dest_info["width"], dest_info["height"]
    )

    cloner = clone.MVCCloner()
    poly = np.flip(points, axis=1)
    result = cloner.clone(source, dest, poly, position)

    # result = cv2.circle(result, (x, y), 5, (255, 0, 0), 1)

    result_id = f"{source_info['id']}_{dest_info['id']}"
    cv2.imwrite(
        os.path.join(app.config["UPLOAD_FOLDER"], f"{result_id}.png"), result * 255
    )

    return result_id


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
