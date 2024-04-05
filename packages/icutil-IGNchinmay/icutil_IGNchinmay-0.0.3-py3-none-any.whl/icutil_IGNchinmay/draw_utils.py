# --------------------------------------------------------------------------
#                         Copyright © by
#           Ignitarium Technology Solutions Pvt. Ltd.
#                         All rights reserved.
#  This file contains confidential information that is proprietary to
#  Ignitarium Technology Solutions Pvt. Ltd. Distribution,
#  disclosure or reproduction of this file in part or whole is strictly
#  prohibited without prior written consent from Ignitarium.
# --------------------------------------------------------------------------
#  Filename    : draw_utils.py
# --------------------------------------------------------------------------
#  Description :
# --------------------------------------------------------------------------
"""To handle drawing operations on a given image such as writing text, drawing bbox on the image etc,."""
import unittest

import os
import cv2
import numpy as np
from termcolor import colored
from icutil_IGNchinmay.json_utils import read_json
from icutil_IGNchinmay.typehint_utils import CntrL

PATH = os.path.dirname(os.path.abspath(__file__))


def determine_text_size(height):
    """Takes height as input and changes it by a fraction (fraction_val)
    Returns the rescaled height
    """
    fraction_val = 2 / 2000
    new_text_ht = height * fraction_val
    # if new_text_ht < 1:
    #     new_text_ht = 1
    return new_text_ht


def print_colored(message, color="green"):
    """Prints messages with the mentioned colour on the console!
    Args:
    message (str): Message to displayed on console
    color (str): The color of the text displayed on console
    """
    print(colored(message, color))


def put_texts(
    img,
    test_tuple_list=None,
    txt_thickness=3,
    v_space=50,
    txt_color=(0, 255, 0),
    default_align=None,
    offsetval=0,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    draw_bg=True,
    bg_color=(0, 0, 0),
):
    """Given an image(img) and a list of texts(test_tuple_list),
    it displays the text on the image in the given position.
    Returns:
    img: image with text
    """
    if test_tuple_list is None:
        test_tuple_list = []
    ht, wd = img.shape[:2]
    l_ct = 1
    r_ct = 1
    align_left = None
    text_height = determine_text_size(ht)
    side_margin = 50

    # if not len(test_tuple_list):
    if len(test_tuple_list) == 0:
        return img

    for index, txt_tuple in enumerate(test_tuple_list):
        if isinstance(txt_tuple, str):
            text = txt_tuple
            if default_align is None:
                align_left = True
            if txt_color is None:
                txt_color = (255, 255, 255)

        elif isinstance(txt_tuple, bool):
            text = f"Oclusion {txt_tuple}"

        elif len(txt_tuple) == 3:
            text, txt_color, align_left = txt_tuple

        elif len(txt_tuple) == 0:
            break

        else:
            text = txt_tuple[0]
            if default_align is None:
                align_left = True
            if txt_color is None:
                txt_color = (255, 255, 255)
        text_size = cv2.getTextSize(text, fontFace=font, fontScale=text_height, thickness=txt_thickness)

        if align_left:
            y_ = v_space * (l_ct) + text_height
            if offsetval:
                y_ += int(offsetval[1])
                left_gap = int(offsetval[0])
            else:
                left_gap = side_margin
            l_ct += 1
        else:
            y_ = v_space * (r_ct) + text_height
            if offsetval:
                y_ += int(offsetval[1])
                left_gap = int(offsetval[0])
            else:
                left_gap = wd - text_size[0][0] - side_margin
            r_ct += 1
        put_text(
            text,
            img,
            left_gap,
            int(y_),
            txt_color,
            text_height,
            txt_thickness,
            font=font,
            draw_bg=draw_bg,
            bg_color=bg_color,
        )
    return img


def put_text(
    text,
    image,
    x,
    y,
    color=(255, 255, 255),
    font_scale=1,
    thickness=1,
    font=None,
    draw_bg=False,
    bg_color=(0, 0, 0),
    auto_align_h=True,
    auto_align_v=True,
):
    """Puts text on image. Given an image and the input text,
     it is displayed in the input position provided
    Args:
        text (str): text to put on image
        image (numpy.ndarray): input image
        x (int): x coordinate of text
        y (int): y coordinate of text
        color (tuple): color of text
        font_scale (float): font size of text
        thickness (int): thickness of text
        font (str): font of text
        draw_bg (bool): draw background or not
        bg_color (tuple): background color
    Returns:
    image: image with text
    """
    if font is None:
        font = cv2.FONT_HERSHEY_SIMPLEX
    (label_width, label_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    label_width, label_height = int(label_width), int(label_height)
    h, w = image.shape[:2]

    if auto_align_h:  # Adjust text to ensure it's enclosd within image
        if x + label_width > w:
            x = w - label_width
    if auto_align_v:
        if y + label_height > h:
            y = h - label_height

    if draw_bg:
        assert bg_color is not None, "bg_color should be given for draw bg"
        image = cv2.rectangle(
            image,
            (x, max(0, y - label_height)),
            (x + label_width, y + (label_height - baseline)),
            bg_color,
            -1,
        )
    image = cv2.putText(image, text, (int(x), int(y)), font, font_scale, color, thickness, cv2.LINE_AA)
    return image


def put_text_non_overlap(
    text,
    image,
    curr_box,
    text_box,
    color=None,
    font_scale=1,
    thickness=1,
    font=None,
    draw_bg=False,
    bg_color=(0, 0, 255),
):
    """Put text on image without overlap.
    Args:
        text (str): text to put on image
        x (int): x coordinate of text
        y (int): y coordinate of text
        color (list): color of text
        font_scale (float): font scale of text
        thickness (int): thickness of text
        font (str): font of text
        draw_bg (bool): draw background or not
        bg_color (list): background color
    Returns:
    image: image with text
    """
    [x, y, w, h] = curr_box
    [x1, y1, w1, h1] = text_box
    if font is None:
        font = cv2.FONT_HERSHEY_SIMPLEX

    if draw_bg:
        assert bg_color is not None, "bg_color should be given for draw bg"
        (label_width, label_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        image = cv2.rectangle(image, (x, y), (x + w, y + h), bg_color, thickness)

    # import pdb;pdb.set_trace()
    image = cv2.putText(
        image,
        text,
        (x, y + label_height),
        font,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )
    return image


def draw_polylines(image, points, color=None, fill=False, inner_contours=None, thickness=None):
    """Draw a filled polygon based on points.
    Returns:
        image: image with filled points drawn on it
    """
    points = np.around(points).astype(int).tolist()
    if color is None:
        color = [255, 255, 255]
    if thickness is None:
        H, W = image.shape[:2]
        thickness = int(min(W, H) / 1000)
    if fill is False:
        cv2.drawContours(image, [np.array(points)], 0, color, thickness)
    else:
        cv2.fillPoly(image, [np.array(points)], color)
        if isinstance(inner_contours, np.ndarray) or inner_contours:
            for cntrs in inner_contours:
                cv2.fillPoly(image, np.array([cntrs]), (0, 0, 0))
    return image


def draw_cntrs(contours: CntrL, img, color=(255, 0, 0), thickness=3, copy_flag=True):
    """Draw the input contours on the image
    Returns:
        image: image with contours drawn on it
    """
    print(contours)
    if copy_flag:
        img = img.copy()
    contours = np.array(contours).reshape((len(contours), -1, 1, 2)).astype(np.int32)  # type: ignore
    img = cv2.drawContours(img, contours, -1, color, thickness)
    return img


class TestDrawUtils(unittest.TestCase):
    """test draw utils"""

    @classmethod
    def setUpClass(cls):
        cls.image_ = cv2.imread("samples/Scopito_1.JPG")
        cls.json_dict_ = read_json("samples/Scopito_1.json")

    @classmethod
    def tearDownClass(cls):
        print("teardown")

    def test_put_texts(self):
        """testing put texts function"""
        img = put_texts(self.image_.copy(), test_tuple_list=["Sample text"], txt_thickness=3, txt_color=(255, 255, 255), default_align=None, offsetval=(50, 50))
        cv2.imwrite("samples/test_results/put_texts_image.jpg", img)
        assert img is not None, "No image returned"

    def test_draw_polylines(self):
        """testing draw polylines function"""
        for node_dict in self.json_dict_.get("shapes", []):
            if node_dict["label"] == "A1_scopito_wt":
                points = node_dict["points"]
        img = draw_polylines(self.image_.copy(), points, color=(0, 0, 255), thickness=5)
        cv2.imwrite("samples/test_results/draw_polylines_image.jpg", img)

    def test_draw_cntrs(self):
        """test draw contours function"""
        for node_dict in self.json_dict_.get("shapes", []):
            if node_dict["label"] == "A1_scopito_wt":
                points = node_dict["points"]
        image = draw_cntrs([points], self.image_, color=(255, 0, 0))
        cv2.imwrite("samples/test_results/draw_contours_image.jpg", image)


if __name__ == "__main__":
    test_obj = TestDrawUtils()
    test_obj.setUpClass()
    test_obj.test_put_texts()
    test_obj.test_draw_polylines()
    test_obj.test_draw_cntrs()
