import random
import string
import pandas as pd
import os
from urllib.parse import urlparse
import requests
import numpy as np
import cv2
import time


class Generator:
    @staticmethod
    def unique_matchId_generator(letter_count: int = 12, digit_count: int = 8) -> str:
        str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))
        str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))

        sam_list = list(str1)  # it converts the string to list.
        random.shuffle(sam_list)  # It uses a random.shuffle() function to shuffle the string.
        final_string = ''.join(sam_list)
        return final_string


class Utilities:
    @staticmethod
    def image_logger(url: str, file_id: str) -> bool:
        """

        Args:
            url: remote image url
            file_id: current processing task

        Returns: have not taken image false, otherwise true

        """
        df = pd.read_csv(os.path.join('Exports', file_id, 'images_list.csv'))

        url_check = df[df["ImagePath"] == url]
        if url_check.empty:
            url_parse = urlparse(url)
            image_name = os.path.basename(url_parse.path)
            df2 = {'ImagePath': url, 'ImageName': image_name}
            df2 = pd.DataFrame([df2])
            df = pd.concat([df, df2], ignore_index=False)
            df.to_csv(os.path.join('Exports', file_id, 'images_list.csv'), index=False)
            return False
        else:
            return True


class Convertor:

    @staticmethod
    def url_to_image(url: str) -> np.ndarray:
        """
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        :param url:
        :return:
        """
        number_of_tries = 3
        for _ in range(number_of_tries):
            try:
                resp = requests.get(url, stream=True).raw
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                if image is None:
                    return None
                return image
            except Exception:
                time.sleep(2)
        else:
            raise

    def get_rad(self, pitch, roll=0, yaw=0):
        return (self.deg_to_rad(float(pitch)),
                self.deg_to_rad(float(roll)),
                self.deg_to_rad(yaw))

    def deg_to_rad(self, deg):
        from math import pi
        return deg * pi / 180.0