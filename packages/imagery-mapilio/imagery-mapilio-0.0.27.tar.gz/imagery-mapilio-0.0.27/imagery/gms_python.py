import math
from enum import Enum
import cv2
cv2.ocl.setUseOpenCL(False)
import numpy as np
from imagery.matcher_config import THRESHOLD_FACTOR, ROTATION_PATTERNS


class Size:
    def __init__(self, width, height):
        '''
        Class for the width,height parameters
        :param width:
        :param height:
        '''
        self.width = width
        self.height = height


class DrawingType(Enum):
    '''
    Type of drawings such line,color coded points
    '''
    ONLY_LINES = 1
    LINES_AND_POINTS = 2
    COLOR_CODED_POINTS_X = 3
    COLOR_CODED_POINTS_Y = 4
    COLOR_CODED_POINTS_XpY = 5


class GmsMatcher:
    """
    GMS feature matching is a motion based feature matching algorithm.
    GMS enables
    translation of high match numbers into high match quality. This provides a real-time, ultra-robust correspondence
    system. Evaluation on videos, with low textures, blurs and
    wide-baselines show GMS consistently out-performs other
    real-time matchers and can achieve parity with more sophisticated, much slower techniques.
    http://jwbian.net/Papers/GMS_CVPR17.pdf
    """
    def __init__(self, descriptor, matcher):
        '''
        main function, create empty list for matches
        :param descriptor: define type of descriptor such as;SIFT,SURF,ORB
        :param matcher: define the matcher such as cv2.NORM_HAMMING,cv2.NORM_L2,cv2.NORM_L1,cv2.NORM_HAMMING2
        '''
        self.scale_ratios = [1.0, 1.0 / 2, 1.0 / math.sqrt(2.0), math.sqrt(2.0), 2.0]
        # Normalized vectors of 2D points
        self.normalized_points1 = []
        self.normalized_points2 = []
        # Matches - list of pairs representing numbers
        self.matches = []
        self.matches_number = 0
        # Grid Size
        self.grid_size_right = Size(0, 0)
        self.grid_number_right = 0
        # x      : left grid idx
        # y      :  right grid idx
        # value  : how many matches from idx_left to idx_right
        self.motion_statistics = []

        self.number_of_points_per_cell_left = []
        # Inldex  : grid_idx_left
        # Value   : grid_idx_right
        self.cell_pairs = []

        # Every Matches has a cell-pair
        # first  : grid_idx_left
        # second : grid_idx_right
        self.match_pairs = []

        # Inlier Mask for output
        self.inlier_mask = []
        self.grid_neighbor_right = []

        # Grid initialize
        self.grid_size_left = Size(20, 20)
        self.grid_number_left = self.grid_size_left.width * self.grid_size_left.height

        # Initialize the neighboor of left grid
        self.grid_neighbor_left = np.zeros((self.grid_number_left, 9))

        self.descriptor = descriptor
        self.matcher = matcher
        self.gms_matches = []
        self.keypoints_image1 = []
        self.keypoints_image2 = []

    def empty_matches(self):
        '''
        create empty list for matching
        :return: points,matches,final result
        '''
        self.normalized_points1 = []
        self.normalized_points2 = []
        self.matches = []
        self.gms_matches = []

    def filter_matches_distance(self, matches, dist_threshold=0.75):
        filtered_matches = []
        for m, n in matches:
            if m.distance <= dist_threshold * n.distance:
                filtered_matches.append(m)

        return filtered_matches
    def compute_matches(self, img1, img2):
        '''
        find keypoints from matcher
        :param img1: input img
        :param img2: input img2
        :return:
        '''
        self.keypoints_image1, descriptors_image1 = self.descriptor.detectAndCompute(img1, np.array([]))
        self.keypoints_image2, descriptors_image2 = self.descriptor.detectAndCompute(img2, np.array([]))
        if not type(descriptors_image2) == np.ndarray:
            self.keypoints_image1, descriptors_image1 = self.descriptor.detectAndCompute(img2, np.array([]))
            self.keypoints_image2, descriptors_image2 = self.descriptor.detectAndCompute(img1, np.array([]))
        size1 = Size(img1.shape[1], img1.shape[0])
        size2 = Size(img2.shape[1], img2.shape[0])

        if self.gms_matches:
            self.empty_matches()

        matches = self.matcher.knnMatch(descriptors_image1, descriptors_image2, k=2)
        all_matches=self.filter_matches_distance(matches)
        self.normalize_points(self.keypoints_image1, size1, self.normalized_points1)
        self.normalize_points(self.keypoints_image2, size2, self.normalized_points2)
        self.matches_number = len(all_matches)
        self.convert_matches(all_matches, self.matches)
        self.initialize_neighbours(self.grid_neighbor_left, self.grid_size_left)

        mask, num_inliers = self.get_inlier_mask(False, False)
        for i in range(len(mask)):
            if mask[i]:
                self.gms_matches.append(all_matches[i])
        return self.gms_matches, num_inliers

    def normalize_points(self, kp, size, npts):
        '''
        normalize Key points to range (0-1)
        :param kp: keypoint list
        :param size:
        :param npts:
        :return:
        '''
        for keypoint in kp:
            npts.append((keypoint.pt[0] / size.width, keypoint.pt[1] / size.height))

    def clahe(self, img1):
        '''
        Adaptive Histogram Equalization
        :param img1: processing image
        :return: bgr-image
        '''
        hsv_img=cv2.cvtColor(img1,cv2.COLOR_BGR2HSV)
        h, s, v,=hsv_img[:,:,0],hsv_img[:,:,1],hsv_img[:,:,2]
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
        v=clahe.apply(v)
        hsv_img=np.dstack((h,s,v))
        self.bgr=cv2.cvtColor(hsv_img,cv2.COLOR_HSV2BGR)
        return self.bgr

    def convert_matches(self, vd_matches, v_matches):
        '''
        Convert OpenCV match to list of tuples
        :param vd_matches:
        :param v_matches:
        :return:
        '''
        for match in vd_matches:
            v_matches.append((match.queryIdx, match.trainIdx))

    def initialize_neighbours(self, neighbor, grid_size):
        '''
        Initialize the neighbour and grid Size
        :param neighbor:
        :param grid_size:
        :return:
        '''
        for i in range(neighbor.shape[0]):
            neighbor[i] = self.get_nb9(i, grid_size)

    def get_nb9(self, idx, grid_size):
        nb9 = [-1 for _ in range(9)]
        idx_x = idx % grid_size.width
        idx_y = idx // grid_size.width

        for yi in range(-1, 2):
            for xi in range(-1, 2):
                idx_xx = idx_x + xi
                idx_yy = idx_y + yi

                if idx_xx < 0 or idx_xx >= grid_size.width or idx_yy < 0 or idx_yy >= grid_size.height:
                    continue
                nb9[xi + 4 + yi * 3] = idx_xx + idx_yy * grid_size.width

        return nb9
    def resize(self,img1, img2):
        '''
        :param img1: input image from array
        :param img2: input image from array
        :return: resized images
        '''
        self.img1 = cv2.resize(img1, (600, 100))
        self.img2 = cv2.resize(img2, (600, 100))
        return self.img1, self.img2

    def get_image_name(self,img1,img2):
        '''
        get image name from array
        :param img1: index of array
        :param img2: index of array
        :return: image name
        '''
        self.image_name1=img1
        self.image_name2=img2
        return self.image_name1,self.image_name2

    def get_inlier_mask(self, with_scale, with_rotation):
        '''
        get mask with rotation and scale
        :param with_scale:
        :param with_rotation:
        :return:
        '''
        max_inlier = 0
        self.set_scale(0)

        if not with_scale and not with_rotation:
            max_inlier = self.run(1)
            return self.inlier_mask, max_inlier
        elif with_scale and with_rotation:
            vb_inliers = []
            for scale in range(5):
                self.set_scale(scale)
                for rotation_type in range(1, 9):
                    num_inlier = self.run(rotation_type)
                    if num_inlier > max_inlier:
                        vb_inliers = self.inlier_mask
                        max_inlier = num_inlier

            if vb_inliers != []:
                return vb_inliers, max_inlier
            else:
                return self.inlier_mask, max_inlier
        elif with_rotation and not with_scale:
            vb_inliers = []
            for rotation_type in range(1, 9):
                num_inlier = self.run(rotation_type)
                if num_inlier > max_inlier:
                    vb_inliers = self.inlier_mask
                    max_inlier = num_inlier

            if vb_inliers != []:
                return vb_inliers, max_inlier
            else:
                return self.inlier_mask, max_inlier
        else:
            vb_inliers = []
            for scale in range(5):
                self.set_scale(scale)
                num_inlier = self.run(1)
                if num_inlier > max_inlier:
                    vb_inliers = self.inlier_mask
                    max_inlier = num_inlier

            if vb_inliers != []:
                return vb_inliers, max_inlier
            else:
                return self.inlier_mask, max_inlier

    def set_scale(self, scale):
        '''
        Set Scales and Initialize the neighbour of right grid
        :param scale:
        :return:
        '''
        self.grid_size_right.width = self.grid_size_left.width * self.scale_ratios[scale]
        self.grid_size_right.height = self.grid_size_left.height * self.scale_ratios[scale]
        self.grid_number_right = self.grid_size_right.width * self.grid_size_right.height

        self.grid_neighbor_right = np.zeros((int(self.grid_number_right), 9))
        self.initialize_neighbours(self.grid_neighbor_right, self.grid_size_right)

    def run(self, rotation_type):
        '''
        run with rotation type
        :param rotation_type:
        :return:
        '''
        self.inlier_mask = [False for _ in range(self.matches_number)]

        # Initialize motion statistics
        self.motion_statistics = np.zeros((int(self.grid_number_left), int(self.grid_number_right)))
        self.match_pairs = [[0, 0] for _ in range(self.matches_number)]

        for GridType in range(1, 5):
            self.motion_statistics = np.zeros((int(self.grid_number_left), int(self.grid_number_right)))
            self.cell_pairs = [-1 for _ in range(self.grid_number_left)]
            self.number_of_points_per_cell_left = [0 for _ in range(self.grid_number_left)]

            self.assign_match_pairs(GridType)
            self.verify_cell_pairs(rotation_type)

            # Mark inliers
            for i in range(self.matches_number):
                if self.cell_pairs[int(self.match_pairs[i][0])] == self.match_pairs[i][1]:
                    self.inlier_mask[i] = True

        return sum(self.inlier_mask)

    def assign_match_pairs(self, grid_type):
        for i in range(self.matches_number):
            lp = self.normalized_points1[self.matches[i][0]]
            rp = self.normalized_points2[self.matches[i][1]]
            lgidx = self.match_pairs[i][0] = self.get_grid_index_left(lp, grid_type)

            if grid_type == 1:
                rgidx = self.match_pairs[i][1] = self.get_grid_index_right(rp)
            else:
                rgidx = self.match_pairs[i][1]

            if lgidx < 0 or rgidx < 0:
                continue
            self.motion_statistics[int(lgidx)][int(rgidx)] += 1
            self.number_of_points_per_cell_left[int(lgidx)] += 1

    def get_grid_index_left(self, pt, type_of_grid):
        x = pt[0] * self.grid_size_left.width
        y = pt[1] * self.grid_size_left.height

        if type_of_grid == 2:
            x += 0.5
        elif type_of_grid == 3:
            y += 0.5
        elif type_of_grid == 4:
            x += 0.5
            y += 0.5

        x = math.floor(x)
        y = math.floor(y)

        if x >= self.grid_size_left.width or y >= self.grid_size_left.height:
            return -1
        return x + y * self.grid_size_left.width

    def get_grid_index_right(self, pt):
        '''
        getting grid index
        :param
        :return:
        '''
        x = int(math.floor(pt[0] * self.grid_size_right.width))
        y = int(math.floor(pt[1] * self.grid_size_right.height))
        return x + y * self.grid_size_right.width

    def verify_cell_pairs(self, rotation_type):
        '''

        DMatch.distance - Distance between descriptors.The lower, the better it is.
        DMatch.trainIdx - Index of the descriptor in train descriptors
        DMatch.queryIdx - Index of the descriptor in query descriptors
        DMatch.imgIdx - Index of the train image.
        :param rotation_type:
        :return:
        '''
        current_rotation_pattern = ROTATION_PATTERNS[rotation_type - 1]

        for i in range(self.grid_number_left):
            if sum(self.motion_statistics[i]) == 0:
                self.cell_pairs[i] = -1
                continue
            max_number = 0
            for j in range(int(self.grid_number_right)):
                value = self.motion_statistics[i]
                if value[j] > max_number:
                    self.cell_pairs[i] = j
                    max_number = value[j]

            idx_grid_rt = self.cell_pairs[i]
            nb9_lt = self.grid_neighbor_left[i]
            nb9_rt = self.grid_neighbor_right[idx_grid_rt]
            score = 0
            thresh = 0
            numpair = 0

            for j in range(9):
                ll = nb9_lt[j]
                rr = nb9_rt[current_rotation_pattern[j] - 1]
                if ll == -1 or rr == -1:
                    continue

                score += self.motion_statistics[int(ll), int(rr)]
                thresh += self.number_of_points_per_cell_left[int(ll)]
                numpair += 1

            thresh = THRESHOLD_FACTOR * math.sqrt(thresh/numpair)
            if score < thresh:
                self.cell_pairs[i] = -2

    def draw_matches(self, src1, src2, drawing_type):
        '''

        :param src1: img1
        :param src2: img2
        :param drawing_type: select of 5 draw type
        :return:
        '''
        height = max(src1.shape[0], src2.shape[0])
        width = src1.shape[1] + src2.shape[1]
        output = np.zeros((height, width, 3), dtype=np.uint8)
        output[0:src1.shape[0], 0:src1.shape[1]] = src1
        output[0:src2.shape[0], src1.shape[1]:] = src2[:]

        if drawing_type == DrawingType.ONLY_LINES:
            for i in range(len(self.gms_matches)):
                left = self.keypoints_image1[self.gms_matches[i].queryIdx].pt
                right = tuple(sum(x) for x in zip(self.keypoints_image2[self.gms_matches[i].trainIdx].pt, (src1.shape[1], 0)))
                cv2.line(output, tuple(map(int, left)), tuple(map(int, right)), (0, 255, 255))

        elif drawing_type == DrawingType.LINES_AND_POINTS:
            for i in range(len(self.gms_matches)):
                left = self.keypoints_image1[self.gms_matches[i].queryIdx].pt
                right = tuple(sum(x) for x in zip(self.keypoints_image2[self.gms_matches[i].trainIdx].pt, (src1.shape[1], 0)))
                cv2.line(output, tuple(map(int, left)), tuple(map(int, right)), (255, 0, 0))

            for i in range(len(self.gms_matches)):
                left = self.keypoints_image1[self.gms_matches[i].queryIdx].pt
                right = tuple(sum(x) for x in zip(self.keypoints_image2[self.gms_matches[i].trainIdx].pt, (src1.shape[1], 0)))
                cv2.circle(output, tuple(map(int, left)), 1, (0, 255, 255), 2)
                cv2.circle(output, tuple(map(int, right)), 1, (0, 255, 0), 2)

        elif drawing_type == DrawingType.COLOR_CODED_POINTS_X or drawing_type == DrawingType.COLOR_CODED_POINTS_Y or drawing_type == DrawingType.COLOR_CODED_POINTS_XpY :
            _1_255 = np.expand_dims( np.array( range( 0, 256 ), dtype='uint8' ), 1 )
            _colormap = cv2.applyColorMap(_1_255, cv2.COLORMAP_HSV)

            for i in range(len(self.gms_matches)):
                left = self.keypoints_image1[self.gms_matches[i].queryIdx].pt
                right = tuple(sum(x) for x in zip(self.keypoints_image2[self.gms_matches[i].trainIdx].pt, (src1.shape[1], 0)))

                if drawing_type == DrawingType.COLOR_CODED_POINTS_X:
                    colormap_idx = int(left[0] * 256. / src1.shape[1] ) # x-gradient
                if drawing_type == DrawingType.COLOR_CODED_POINTS_Y:
                    colormap_idx = int(left[1] * 256. / src1.shape[0] ) # y-gradient
                if drawing_type == DrawingType.COLOR_CODED_POINTS_XpY:
                    colormap_idx = int( (left[0] - src1.shape[1]*.5 + left[1] - src1.shape[0]*.5) * 256. / (src1.shape[0]*.5 + src1.shape[1]*.5) ) # manhattan gradient

                color = tuple( map(int, _colormap[ colormap_idx,0,: ]) )
                cv2.circle(output, tuple(map(int, left)), 1, color, 2)
                cv2.circle(output, tuple(map(int, right)), 1, color, 2)

        _, num_inliers = self.get_inlier_mask(False, False)
        return num_inliers
