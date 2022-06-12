from flask import Flask, render_template, session, request, jsonify
import utils
import os
import cv2
import random
import numpy as np
import clone

async_mode = None
app = Flask(__name__)

app = Flask(__name__, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/user_data"
if not os.path.exists("static/user_data"):
    os.makedirs("static/user_data")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/upload-image', methods=['POST'])
def upload_image():
    file = request.files['image']
    image_id = f'{random.randint(0, 99):02d}'
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}.png")
    file.save(image_path)
    return image_id

@app.route('/crop', methods=['POST'])
def crop():
    req = request.get_json()
    image_id = req['image_id']
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}.png")
    image = cv2.imread(image_path)

    points = np.array([[point['x'], point['y']] for point in req['points']], dtype=int)
    cropped, points = utils.crop_image(image, points)

    np.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}_cropped.npy"), points)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], f"{image_id}_cropped.png"), cropped)
    return image_id + "_cropped"

@app.route('/clone', methods=['POST'])
def clone_image():
    req = request.get_json()
    source_id = req['source_id']
    dest_id = req['dest_id']
    fx, fy = req['fx'], req['fy']
    rotate = req['rotate']
    position = np.array([req['position']['y'], req['position']['x']])

    source_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{source_id}.png")
    source = cv2.imread(source_path)
    points = np.load(os.path.join(app.config['UPLOAD_FOLDER'], f"{source_id}.npy"))

    source, points = utils.resize_image(source, points, fx, fy)
    source, points = utils.rotate_image(source, points, rotate)

    # test = source.copy()
    # for point in points:
    #     test = cv2.circle(test, point, 5, (255, 0, 0), 1)
    # cv2.imwrite("tmp.png", test)

    dest_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{dest_id}.png")
    dest = cv2.imread(dest_path)

    cloner = clone.MVCCloner()
    poly = np.flip(points, axis=1)
    result = cloner.clone(source, dest, poly, position)

    result_id = f"{source_id}_{dest_id}"
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], f"{result_id}.png"), result * 255)

    return result_id

if __name__ == "__main__":
    app.run(app, debug=False, host="0.0.0.0", port=8000)
