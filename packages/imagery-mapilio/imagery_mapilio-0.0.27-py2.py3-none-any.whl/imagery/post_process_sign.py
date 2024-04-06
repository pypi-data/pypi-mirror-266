#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates.
from skimage.measure import find_contours
import numpy as np
from imagery.gms_python import GmsMatcher
from detectron2.structures import masks as mask_func
import operator
from itertools import combinations
import cv2


class Config:
    len_threshold = 60  # if prediction length is smaller than threshold algorithm will remove it
    match_threshold = 35  # feature-matching threshold
    iou_min_threshold = 0.15  # if iou lower than this value algorithm ignores it
    iou_max_threshold = 0.80  # if iou bigger than this value algorithm remove small mask


def matcher_sign(image_1, image_2):
    orb = cv2.ORB_create(10000)
    orb.setFastThreshold(0)
    if cv2.__version__.startswith('3'):
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    else:
        matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING)
    gms = GmsMatcher(orb, matcher)
    matches = gms.compute_matches(image_1, image_2)
    return matches


def reverse_index(lists_of_array: list):
    """
    --This function reverse array index 0-1--

    lists_of_array: list of polygon points as type array
    """
    for points in [points for arr in lists_of_array for points in arr]:
        points[0], points[1] = points[1], points[0]


def mask_position(bbox_list, index_1, index_2):
    """
    parameter bbox_list: list of bboxes
    parameter index_1: index_1 of combination
    parameter index_2: index_2 of combination
    return: position of smaller mask as string
    """
    mask1_x_min, mask1_x_max = bbox_list[index_1][0], bbox_list[index_1][2]
    mask2_x_min, mask2_x_max = bbox_list[index_2][0], bbox_list[index_2][2]

    dif_x_min_12 = abs(mask1_x_min - mask2_x_min)
    dif_x_max_12 = abs(mask1_x_max - mask2_x_max)
    return "right" if dif_x_min_12 > dif_x_max_12 else "left"


def calculate_area(mask1, mask2):
    """
    parameter mask1: array of binary mask
    parameter mask2: array of binary mask
    return: bigger mask name as string
    """
    mask1_area = np.count_nonzero(mask1 == 1)
    mask2_area = np.count_nonzero(mask2 == 1)
    return "mask2" if mask1_area > mask2_area else "mask1"


def is_updated(list_t, index_big, index_small, remove_list):
    """
    --This function if mask  updated before removes old mask--

    parameter list_t: list of updated small and big mask as tuple
    parameter index_big: index of big mask
    parameter index_small: index of small mask
    """
    for tuples in list_t:
        if tuples[1] == index_big:
            remove_list.append(tuples[0])
            remove_list.append(index_small)


def remove_list_index(index_to_removed, bbox_list, polygon_list, scores, class_id):
    """
    --This function remove mask and box arrays in given list of indexes--

    parameter index_to_removed: list of indexes to be removed
    parameter bbox_list: bbox list
    parameter polygon_list: polygon list
    """
    # get unique indexes to avoid to remove same index for more than once
    box_r_l = list(set(index_to_removed))
    box_r_l.sort()
    for index_fitter, index_r in enumerate(box_r_l):
        bbox_list.pop(index_r - index_fitter)
        scores.pop(index_r - index_fitter)
        class_id.pop(index_r - index_fitter)
        polygon_list.pop(index_r - index_fitter)


def intersection_ou(mask1, mask2):
    """
    parameter mask1: array of binary mask
    parameter mask2: array of binary mask
    return: intersection over union value
    """
    mask1_area = np.count_nonzero(mask1 == 1)  # I assume this is faster as mask1 == 1 is a bool array
    mask2_area = np.count_nonzero(mask2 == 1)
    intersection = np.count_nonzero(np.logical_and(mask1, mask2))
    iou = intersection / (mask1_area + mask2_area - intersection)
    return iou


def calc_box_w_h(leftover_box, small_box):
    """
    parameter big_box: Array of bbox points
    parameter small_box: Array of bbox points
    return: return boxes width, height and buffer width
    """
    dict_h_w: dict = {}
    for index, box in enumerate([leftover_box, small_box]):
        dict_h_w[f"{index}_w"] = box[2] - box[0]
        dict_h_w[f"{index}_h"] = box[3] - box[1]
    buffer_width = abs(dict_h_w["0_w"] - dict_h_w["1_w"])
    bigger_h = "leftover" if dict_h_w["0_h"] > dict_h_w["1_h"] else "small"
    return buffer_width, bigger_h, dict_h_w["0_w"], dict_h_w["1_w"]


def resize_box_border(position, buffer, leftover_box, small_box, bigger_w):
    """
    parameter position: position of small mask
    parameter buffer: width difference between leftover and small boxes
    parameter leftover_box: array of bbox points
    parameter small_box: array of bbox points
    parameter bigger_w: string of big width box name
    return: return updated boxes
    """
    box = leftover_box if bigger_w == "leftover" else small_box
    output = (box, small_box) if box.all == leftover_box.all else (leftover_box, box)
    if position == "left":
        box[0] += buffer
        return output
    else:
        box[2] -= buffer
        return output


def update_box_mask(position, small_box_default, index_big, bbox_list, contour, index_list, scores, class_id):
    """
    --This function update bbox and mask--

    parameter position: Position of small mask in bigger mask
    parameter small_box_default: default small mask's bbox list
    parameter index_big: index of big mask
    parameter bbox_list: Array of updated bbox points
    parameter contour: Array of updated polygon points
    parameter index_list: list is which contains index values to removed
    """
    list_append: list = []
    index_1, index_2 = (2, 0) if position == "left" else (0, 2)
    operation = operator.gt if position == "left" else operator.lt
    threshold = small_box_default[index_1]
    bbox = bbox_list[index_big].copy()
    bbox[index_2] = threshold
    bbox_list.append(bbox)  # update bbox
    index_list.append(index_big)  # add new index to remove list
    scores.append(scores[index_big])
    class_id.append(class_id[index_big])
    for contours in contour[index_big]:
        filter_op = np.array(list(filter(lambda p: operation(p[0], threshold), contours)))
        if len(filter_op) > 0:
            list_append.append(filter_op)
    contour.append(np.array(list_append))


def postprocess(bbox_list: list, mask_list: list, im, scores, class_id):
    # if zero prediction on image return empty list.
    if len(mask_list) == 0: return [], []

    # define lists to get prediction output variables
    updated_contours, index_to_removed, list_small_big_index = [], [], []

    # define height and width for converting polygon points to mask
    h, w, _ = im.shape

    for mask in mask_list:
        # find mask polygon points
        contour_base = find_contours(mask)

        # reverse element index in polygon points to fix [y, x] format
        reverse_index(contour_base)

        # append polygon points
        updated_contours.append(contour_base)

    # copy bbox_list for update bbox points to save original bbox list
    updated_bbox = bbox_list.copy()

    # combination of masks to calculate IOU
    combs_index = list((index_1, index_2) for ((index_1, _), (index_2, _))
                       in combinations(enumerate(mask_list), 2))

    for comb_index in combs_index:
        # to call index more clear and shorter
        index_1, index_2 = comb_index[0], comb_index[1]

        # iou calculation
        iuo = intersection_ou(mask_list[index_1], mask_list[index_2])

        if iuo > Config.iou_max_threshold:
            # area calculation to determine which mask is bigger
            small = calculate_area(mask_list[index_1], mask_list[index_2])

            # determine small mask index to remove it from list
            remove_index_small = index_1 if small == "mask1" else index_2

            # append small mask index to remove end of the process
            index_to_removed.append(remove_index_small)

        if Config.iou_min_threshold < iuo < Config.iou_max_threshold:
            # area calculation for define which mask is bigger
            small = calculate_area(mask_list[index_1], mask_list[index_2])

            # decide smaller mask position
            position = mask_position(bbox_list, index_1, index_2)

            # call bbox values from list as index
            mask1_bbox, mask2_bbox = bbox_list[index_1], bbox_list[index_2]

            bigger = mask2_bbox.copy() if small == "mask1" else mask1_bbox.copy()
            small_box = mask1_bbox.copy() if small == "mask1" else mask2_bbox.copy()

            small_box_default = small_box.copy()

            # determine bigger-small(leftover) mask bbox points
            index1, index2 = (0, 2) if position == "left" else (2, 0)
            bigger[index1] = small_box[index2]
            leftover_box = bigger.copy()

            # determine index of small mask and big mask
            index_small, index_big = (index_2, index_1) if small == "mask2" else (index_1, index_2)

            # determine small and big mask's box width difference
            buffer_x, bigger_h, w_leftover, w_small = calc_box_w_h(leftover_box, small_box)

            # if object is smaller than threshold remove object's mask + bbox
            if w_leftover < Config.len_threshold or w_small < Config.len_threshold:
                # append small mask index to remove end of the process
                index_to_removed.append(index_small)
                continue

            # getting max height of y values for feature matching
            big_h_box = leftover_box if bigger_h == "leftover" else small_box
            y_min, y_max = big_h_box[1], big_h_box[3]

            # define big-small(leftover) box border for feature-matching
            str_big_w = "leftover" if w_leftover > w_small else "small"
            leftover_box, small_box = resize_box_border(position, buffer_x, leftover_box, small_box, str_big_w)

            # buffer y values
            small_box[1], small_box[3] = y_min, y_max
            leftover_box[1], leftover_box[3] = y_min, y_max

            # extrack frames from images
            x_min, y_min, x_max, y_max = leftover_box
            leftover_sign = im[int(y_min):int(y_max), int(x_min):int(x_max)]

            x_min, y_min, x_max, y_max = small_box
            small_sign = im[int(y_min):int(y_max), int(x_min):int(x_max)]

            # matching frames
            out = matcher_sign(leftover_sign, small_sign)

            if len(out) < Config.match_threshold:
                # if mask updated remove old one
                is_updated(list_small_big_index, index_big, index_small, index_to_removed)

                # to check mask updated before or not
                list_small_big_index.append((index_small, index_big))

                # update box and mask
                update_box_mask(position, small_box_default, index_big, updated_bbox,
                                updated_contours, index_to_removed, scores, class_id)
            else:
                index_to_removed.append(index_small)

    # remove mask and box according to given indexes in list
    remove_list_index(index_to_removed, updated_bbox, updated_contours, scores, class_id)

    # convert list of polygon points format for convert it to mask
    converted_type = [np.ravel(bunch_arr[0]) for bunch_arr in updated_contours]

    # convert polygon to mask
    mask_list = [mask_func.polygons_to_bitmask([poly], h, w) for poly in converted_type]

    mask_list = np.array(mask_list)

    return mask_list, updated_bbox, scores, class_id
