import os
import numpy as np
import cv2

from imagery.utilities import Generator
from imagery.pixel import Pixel
from imagery.postprocessor import PostProcessor
from addict import Dict
from skimage import measure


class Operation:

    @staticmethod
    def image_write(outPath: str, image: np.ndarray, name: str):
        cv2.imwrite(os.path.join(outPath, name), image, [cv2.IMWRITE_JPEG_QUALITY, 80])

    @staticmethod
    def image_action(**kwargs) -> (str, np.ndarray, float):
        """

        Args:
            image:
            finalBox: detected object bounding box
            class_name: detected objects category name
            writePaths: where will it write
            rgb_mask:
            copyImage:
            config:
            score:
            file_id: specif prediction dir id

        Returns:
            write local directory, detected objects as a array, pca angle
        """
        params = Dict(kwargs)
        xmin, ymin, xmax, ymax = [int(item) for item in params.finalBox]
        detectedObject = params.copyImage[ymin:ymax, xmin:xmax]  # if detectedObject dont want color open this
        # if len(params.mask_boundary):
        #     cv2.polylines(params.image, [params.mask_boundary], True, (0, 255, 0), 3)
        #     # TODO mask deprecated
        #     # image_pca, image_rgb = PostProcessor.image_coloring(params.image, params.rgb_mask)
        #     # detectedObject_pca = image_pca[ymin:ymax, xmin:xmax]
        #     # detectedObject = image_rgb[ymin:ymax, xmin:xmax]
        #     # del image_pca
        #     # angle_pca = Pixel.get_angle_pca(detectedObject_pca)

        if params.config.processedimageWrite:
            cX = int((xmin + xmax) / 2)
            cY = int((ymin + ymax) / 2)

            cv2.putText(params.image, params.class_code, (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(params.image, str(params.score), (cX + 10, cY + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(params.image, params.objectId, (cX + 20, cY + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            cv2.rectangle(params.image, (xmin, ymin), (xmax, ymax), (255, 0, 255), thickness=2)
            Operation.draw_poly_line_mask(params.image, params.mask_boundary)

        imageNumber = os.path.basename(params.writePaths[1]).split(".")[0]
        imageSaveType = os.path.basename(params.writePaths[1]).split(".")[1]
        saveName = imageNumber + "_{}.".format(Generator.unique_matchId_generator()) + imageSaveType

        detectedObjectPath = os.path.join("Exports", params.file_id, "ObjectsImage", saveName)
        cv2.imwrite(detectedObjectPath, detectedObject)

        del params.copyImage

        return detectedObjectPath, params.image

    @staticmethod
    def image_read_rgb(detectedObjectPath: str) -> np.ndarray:
        return cv2.imread(detectedObjectPath)

    @staticmethod
    def image_read_rgb_as_gray(detectedObjectPath: str) -> np.ndarray:
        return cv2.imread(detectedObjectPath, 0)

    @staticmethod
    def binary_mask_to_polygon(binary_mask: np.ndarray, tolerance: int = 0) -> np.ndarray:
        def close_contour(contour: np.ndarray) -> np.ndarray:
            if not np.array_equal(contour[0], contour[-1]):
                contour = np.vstack((contour, contour[0]))
            return contour

        polygons = []
        # pad mask to close contours of shapes which start and end at an edge
        padded_binary_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
        contours = measure.find_contours(padded_binary_mask, 0.5)
        contours = np.subtract(contours, 1)
        for contour in contours:
            contour = close_contour(contour)
            contour = measure.approximate_polygon(contour, tolerance)
            if len(contour) < 3:
                continue
            contour = np.flip(contour, axis=1)
            segmentation = contour.ravel().tolist()
            # after padding and subtracting 1 we may get -0.5 points in our segmentation
            segmentation = [0 if i < 0 else i for i in segmentation]
            polygons.append(segmentation)

        return polygons

    @staticmethod
    def draw_circle(point: list, image: list, color: tuple):
        """
        :param point: List of contain a point's coordinates value
        :param image: Array list of image pixels
        :param color: Tuple of contain RGB values
        :return: Draws circle to given point
        """
        cv2.circle(image, (int(point[0]), int(point[1])), radius=0, color=color, thickness=3)

        return image

    @staticmethod
    def draw_poly_line_mask(image: np.ndarray, polygon_points: list):
        """
        :param polygon_points: List of contain a point's coordinates value
        :param image: Array list of image pixels
        :return: Draws line to between given two point
        """
        for x in range(0, len(polygon_points), 1):
            if x == len(polygon_points) - 1:
                cv2.line(image, (int(polygon_points[-1][0]), int(polygon_points[-1][1])), (int(polygon_points[0][0]),
                                                                                           int(polygon_points[0][1])),
                         (255, 0, 0), 2)
            else:
                cv2.line(image, (int(polygon_points[x][0]), int(polygon_points[x][1])), (int(polygon_points[x + 1][0]),
                                                                                         int(polygon_points[x + 1][1])),
                         (255, 0, 0), 2)