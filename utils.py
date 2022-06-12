import cv2
import numpy as np

import clone


def crop_image(image, points):
    ## (1) Crop the bounding rect
    x, y, w, h = cv2.boundingRect(points)
    croped = image[y : y + h, x : x + w]

    ## (2) make mask
    points = points - points.min(axis=0)

    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)

    ## (3) do bit-op
    croped = cv2.cvtColor(croped, cv2.COLOR_BGR2BGRA)
    dst = np.where(
        np.repeat(mask[:, :, np.newaxis], 4, axis=2), croped, np.zeros_like(croped)
    )
    return dst, points

def resize_image(image, points, width, height):
    h, w, _ = image.shape
    fx = width / w
    fy = height / h
    image = cv2.resize(image, None, fx=fx, fy=fy)
    points = points * np.array([fx, fy])

    return image, points


def rotate_image(image, points, angle):
    height, width = image.shape[:2]  # image shape has 3 dimensions
    image_center = (
        width / 2,
        height / 2,
    )  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]
    image = cv2.warpAffine(
        image, rotation_mat, (bound_w, bound_h), borderMode=cv2.BORDER_REPLICATE
    )

    points = points - np.array([width * 0.5, height * 0.5])
    points = np.matmul(points, rotation_mat[:, :2].T) + np.array(
        [bound_w / 2, bound_h / 2]
    )
    return image, points.astype(int)


def trim_image(image, points):
    x, y, w, h = cv2.boundingRect(points)
    points = points - np.array([x, y])
    return image[y : y + h, x : x + w], points


def central_position(pos, w, h, rotate):
    theta = np.radians(-rotate)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    
    trans = np.matmul(R, (w/2, h/2)).astype(int)
    return pos + trans

if __name__ == '__main__':
    points = [{"x":41,"y":66.75},{"x":8,"y":106.75},{"x":24,"y":145.75},{"x":85,"y":169.75},{"x":178,"y":186.75},{"x":286,"y":185.75},{"x":358,"y":178.75},{"x":371,"y":144.75},{"x":361,"y":96.75},{"x":333,"y":51.75},{"x":283,"y":53.75},{"x":200,"y":50.75},{"x":122.5,"y":49.75}]
    points = np.array([[point['x'], point['y']] for point in points], dtype=int)

    theta = -30
    image = cv2.imread("static/images/src1.png")
    image, points = crop_image(image, points)
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    image, points = resize_image(image, points, 300, 200)
    image, points = rotate_image(image, points, theta)
    # image, points = trim_image(image, points)

    x, y = 1000, 200
    position = central_position((x, y), 300, 200, theta)
    position = np.flip(position)

    # test = image.copy()
    # for point in points:
    #     test = cv2.circle(test, point, 5, (255, 0, 0), 1)
    # cv2.imshow("test", test)
    # cv2.waitKey(0)

    cloner = clone.MVCCloner()
    img = image
    dest = cv2.imread('static/images/dst1.png')
    # dest, _ = resize_image(dest, np.array([[0,0]]), 1600, 898)
    
    poly = np.flip(points, axis=1)
    ret = cloner.clone(img, dest, poly, position)

    ret = cv2.circle(ret, (x,y), 5, (255, 0, 0), 1)
    ret = cv2.circle(ret, (position[1],position[0]), 5, (255, 0, 0), 1)

    cv2.imshow('result', ret)
    # cv2.imwrite("tmp.png", ret * 255)
    cv2.waitKey()
