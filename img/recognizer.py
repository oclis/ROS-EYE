import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal,QObject

class Signal(QObject):  
    msg_signal = pyqtSignal(str)

class featureMatcher:

    def __init__(self):
        self.bMode = False  
        self.report = Signal() 
        
    def get_corrected_img(self, img1, img2):
        MIN_MATCHES = 20
        self.report.msg_signal.emit('start processing')
        orb = cv2.ORB_create(nfeatures=500)
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        index_params = dict(algorithm=6,
                            table_number=6,
                            key_size=12,
                            multi_probe_level=2)
        search_params = {}
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        # Need to draw only good matches, so create a mask
        matchesMask = [[0,0] for i in range(len(matches))]
        self.report.msg_signal.emit('match =')
        # As per Lowe's ratio test to filter good matches
        # ratio test as per Lowe's paper
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.2*n.distance:
                matchesMask[i]=[1,0]
        draw_params = dict(matchColor = (0,255,0),
                        singlePointColor = (255,0,0),
                        matchesMask = matchesMask,
                        flags = 0)
        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)        

        self.report.msg_signal.emit('end processing')            
        return img3

def find_almost_similar_image_locations(im_search, im_source, threshold=0.8, rgb=True):
    return ImageMatching(im_search, im_source, threshold, rgb).find_best_result()


class ImageMatching(object):

    FILTER_RATIO = 0.59

    def __init__(self, im_search, im_source, threshold=0.8, rgb=True):
        super(ImageMatching, self).__init__()
        self.im_source = im_source
        self.im_search = im_search
        self.threshold = threshold
        self.rgb = rgb

    def find_best_result(self):
        if not _check_image_valid(self.im_source, self.im_search):
            return None
        self.kp_sch, self.kp_src, self.good = self._get_key_points()


        if len(self.good) in [0, 1]:              
            return None
        elif len(self.good) in [2, 3]:

            if len(self.good) == 2:
                origin_result = self._handle_two_good_points(self.kp_sch, self.kp_src, self.good)
            else:
                origin_result = self._handle_three_good_points(self.kp_sch, self.kp_src, self.good)

            if origin_result is None:
                return origin_result
            else:
                middle_point, pypts, w_h_range = origin_result
        else:
            middle_point, pypts, w_h_range = self._many_good_pts(self.kp_sch, self.kp_src, self.good)

        # Find the credibility of the result based on the recognition area, and return the result:
        # Check the rationality of the recognition result: if it is less than 5 pixels,
        # or if it is zoomed more than 5 times, it will be regarded as illegal and raised.
        self._target_error_check(w_h_range)
        # Scale screenshots and recognition results to the same size, ready to calculate credibility
        x_min, x_max, y_min, y_max, w, h = w_h_range
        target_img = self.im_source[y_min:y_max, x_min:x_max]
        resize_img = cv2.resize(target_img, (w, h))
        confidence = self._cal_confidence(resize_img)

        best_match = _generate_result(middle_point, pypts, confidence)
        return best_match if confidence >= self.threshold else None

    def _cal_confidence(self, resize_img):
        """Calculation confidence."""
        if self.rgb:
            confidence = _cal_rgb_confidence(self.im_search, resize_img)
        else:
            confidence = _cal_ccoeff_confidence(self.im_search, resize_img)
        confidence = (1 + confidence) / 2
        return confidence

    def init_detector(self):
        """Init keypoint detector object."""
        self.detector = cv2.KAZE_create()
        # create BFMatcher object:
        self.matcher = cv2.BFMatcher(cv2.NORM_L1)  # cv2.NORM_L1 cv2.NORM_L2 cv2.NORM_HAMMING(not useable)

    def get_keypoints_and_descriptors(self, image):
        """Get image feature points and descriptors."""
        keypoints, descriptors = self.detector.detectAndCompute(image, None)
        return keypoints, descriptors

    def match_keypoints(self, des_sch, des_src):
        """Match descriptors (Eigenvalue matching)."""
        # Match the feature point set in the two pictures,
        # k = 2 means that each feature point takes out the 2 best matching corresponding points:
        return self.matcher.knnMatch(des_sch, des_src, k=2)

    def _get_key_points(self):
        """According to the incoming image, calculate all the feature points of the image,
         and get matching feature point pairs."""
        # Preparation: Initialization operator
        self.init_detector()
        # Step 1: Get the feature point set and match the feature point pairs: Return value good, pypts, kp_sch, kp_src
        kp_sch, des_sch = self.get_keypoints_and_descriptors(self.im_search)
        kp_src, des_src = self.get_keypoints_and_descriptors(self.im_source)
        # When apply knnmatch , make sure that number of features in both test and
        #       query image is greater than or equal to number of nearest neighbors in knn match.
        if len(kp_sch) < 2 or len(kp_src) < 2:
            print("Not enough feature points in input images !")
        # match descriptors (Eigenvalue matching)
        matches = self.match_keypoints(des_sch, des_src)

        #
        # Good is the result of the preliminary selection of feature points,
        # and the first two feature points that are too close are eliminated,
        # and the feature points that are not unique and excellent are directly filtered
        # (multi-target recognition is not applicable directly)
        good = []
        for m, n in matches:
            if m.distance < self.FILTER_RATIO * n.distance:
                good.append(m)
        # Good points need to remove the duplicates. (Set the source image can not have duplicate points)
        # When deduplication, find the duplicate points in the src image.
        # Deduplication strategy: Allows one-to-many mapping of feature points of the search image to the source image,
        # and does not allow many-to-one repetition
        # (ie, one point on the energy image corresponds to multiple points of the search image)
        good_diff, diff_good_point = [], [[]]
        for m in good:
            diff_point = [int(kp_src[m.trainIdx].pt[0]), int(kp_src[m.trainIdx].pt[1])]
            if diff_point not in diff_good_point:
                good_diff.append(m)
                diff_good_point.append(diff_point)
        good = good_diff

        return kp_sch, kp_src, good

    def _handle_two_good_points(self, kp_sch, kp_src, good):
        """Dealing with two pairs of feature points."""
        pts_sch1 = int(kp_sch[good[0].queryIdx].pt[0]), int(kp_sch[good[0].queryIdx].pt[1])
        pts_sch2 = int(kp_sch[good[1].queryIdx].pt[0]), int(kp_sch[good[1].queryIdx].pt[1])
        pts_src1 = int(kp_src[good[0].trainIdx].pt[0]), int(kp_src[good[0].trainIdx].pt[1])
        pts_src2 = int(kp_src[good[1].trainIdx].pt[0]), int(kp_src[good[1].trainIdx].pt[1])

        return self._get_origin_result_with_two_points(pts_sch1, pts_sch2, pts_src1, pts_src2)

    def _handle_three_good_points(self, kp_sch, kp_src, good):
        """Dealing with three pairs of feature points."""
        # Take out the two points of sch and src (point 1) and (midpoint of point 2 and point 3)，
        # Then post-processing according to the two-point principle (note ke_sch and kp_src and queryIdx and trainIdx):
        pts_sch1 = int(kp_sch[good[0].queryIdx].pt[0]), int(kp_sch[good[0].queryIdx].pt[1])
        pts_sch2 = int((kp_sch[good[1].queryIdx].pt[0] + kp_sch[good[2].queryIdx].pt[0]) / 2), int(
            (kp_sch[good[1].queryIdx].pt[1] + kp_sch[good[2].queryIdx].pt[1]) / 2)
        pts_src1 = int(kp_src[good[0].trainIdx].pt[0]), int(kp_src[good[0].trainIdx].pt[1])
        pts_src2 = int((kp_src[good[1].trainIdx].pt[0] + kp_src[good[2].trainIdx].pt[0]) / 2), int(
            (kp_src[good[1].trainIdx].pt[1] + kp_src[good[2].trainIdx].pt[1]) / 2)
        return self._get_origin_result_with_two_points(pts_sch1, pts_sch2, pts_src1, pts_src2)

    def _many_good_pts(self, kp_sch, kp_src, good):
        """The number of feature point matching point pairs is> = 4,
           and a single matrix mapping can be used to find the identified target area."""
        sch_pts, img_pts = np.float32([kp_sch[m.queryIdx].pt for m in good]).reshape(
            -1, 1, 2), np.float32([kp_src[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # M is the transformation matrix
        M, mask = self._find_homography(sch_pts, img_pts)
        matches_mask = mask.ravel().tolist()
        # Filter out more accurate points from the good
        # (assuming that most of the points in good are correct, guaranteed by ratio = 0.7)
        selected = [v for k, v in enumerate(good) if matches_mask[k]]

        # Calculate a more accurate transformation matrix M for all selected points.
        sch_pts, img_pts = np.float32([kp_sch[m.queryIdx].pt for m in selected]).reshape(
            -1, 1, 2), np.float32([kp_src[m.trainIdx].pt for m in selected]).reshape(-1, 1, 2)
        M, mask = self._find_homography(sch_pts, img_pts)
        # Calculate the coordinates of the four corner matrix transformations,
        # that is, the coordinates of the vertices of the target area in the large image:
        h, w = self.im_search.shape[:2]
        h_s, w_s = self.im_source.shape[:2]
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # trans numpy arrary to python list: [(a, b), (a1, b1), ...]
        def cal_rect_pts(dst):
            return [tuple(npt[0]) for npt in dst.astype(int).tolist()]

        pypts = cal_rect_pts(dst)
        # Note: Although it is possible for the 4 corner points to exceed the boundary of the source graph,
        # (according to the precise mapping single mapping matrix M linear mechanism)
        # the midpoints will not exceed the boundary
        lt, br = pypts[0], pypts[2]
        middle_point = int((lt[0] + br[0]) / 2), int((lt[1] + br[1]) / 2)
        # Considering that the calculated target matrix may be flipped, it must be processed once to ensure that
        # the "upper left corner" after the mapping is also the upper left corner point in the picture:
        x_min, x_max = min(lt[0], br[0]), max(lt[0], br[0])
        y_min, y_max = min(lt[1], br[1]), max(lt[1], br[1])

        x_min, x_max = int(max(x_min, 0)), int(max(x_max, 0))
        x_min, x_max = int(min(x_min, w_s - 1)), int(min(x_max, w_s - 1))
        y_min, y_max = int(max(y_min, 0)), int(max(y_max, 0))        
        y_min, y_max = int(min(y_min, h_s - 1)), int(min(y_max, h_s - 1))

        pts = np.float32([[x_min, y_min], [x_min, y_max], [
            x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        pypts = cal_rect_pts(pts)

        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]

    def _get_origin_result_with_two_points(self, pts_sch1, pts_sch2, pts_src1, pts_src2):
        """Returns the recognition results in the case of two pairs of valid matching feature points."""
        # First calculate the center point (coordinates in self.im_source)：
        middle_point = [int((pts_src1[0] + pts_src2[0]) / 2), int((pts_src1[1] + pts_src2[1]) / 2)]
        pypts = []
        # If the feature point is the same as the x-axis or the same y-axis (in either src or sch),
        # the target rectangular area cannot be calculated. At this time, the return value is the same as good = 1
        if pts_sch1[0] == pts_sch2[0] or pts_sch1[1] == pts_sch2[1] or pts_src1[0] == pts_src2[0] or pts_src1[1] == \
                pts_src2[1]:
            return None
        # Calculate the x and y scales: x_scale, y_scale, expand the target area from the middle point:
        # (note that integer calculations must be converted to floating point results!)
        h, w = self.im_search.shape[:2]
        h_s, w_s = self.im_source.shape[:2]
        x_scale = abs(1.0 * (pts_src2[0] - pts_src1[0]) / (pts_sch2[0] - pts_sch1[0]))
        y_scale = abs(1.0 * (pts_src2[1] - pts_src1[1]) / (pts_sch2[1] - pts_sch1[1]))
        # After getting the scale, the middle_point needs to be corrected, not the midpoint of the feature point,
        # but the midpoint of the mapping matrix.
        sch_middle_point = int((pts_sch1[0] + pts_sch2[0]) / 2), int((pts_sch1[1] + pts_sch2[1]) / 2)
        middle_point[0] = middle_point[0] - int((sch_middle_point[0] - w / 2) * x_scale)
        middle_point[1] = middle_point[1] - int((sch_middle_point[1] - h / 2) * y_scale)
        # Beyond the left boundary, take 0 (the upper left corner of the image is 0,0)
        middle_point[0] = max(middle_point[0], 0)
        middle_point[0] = min(middle_point[0], w_s - 1)  # Take w_s-1 beyond the right boundary
        middle_point[1] = max(middle_point[1], 0)  # 0 beyond the upper boundary
        middle_point[1] = min(middle_point[1], h_s - 1)  # Take h_s-1 beyond the lower boundary

        # Calculate the order of the corners of the rectangle:
        # upper left corner-> lower left corner-> lower right corner-> upper right corner
        # 0 beyond the left boundary, w_s-1 beyond the right boundary, 0_ beyond the lower boundary,
        # h_s-1 beyond the upper boundary
        x_min, x_max = int(max(middle_point[0] - (w * x_scale) / 2, 0)), int(
            min(middle_point[0] + (w * x_scale) / 2, w_s - 1))
        y_min, y_max = int(max(middle_point[1] - (h * y_scale) / 2, 0)), int(
            min(middle_point[1] + (h * y_scale) / 2, h_s - 1))
        # The corners of the target rectangle are in the order of upper left, lower left, lower right, and upper right:
        # (x_min, y_min) (x_min, y_max) (x_max, y_max) (x_max, y_min)
        pts = np.float32([[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]).reshape(-1, 1, 2)
        for npt in pts.astype(int).tolist():
            pypts.append(tuple(npt[0]))

        return middle_point, pypts, [x_min, x_max, y_min, y_max, w, h]

    def _find_homography(self, sch_pts, src_pts):
        """When multiple sets of feature points are paired, obtain a unidirectional matrix."""
        try:
            M, mask = cv2.findHomography(sch_pts, src_pts, cv2.RANSAC, 5.0)
        except Exception:
            import traceback
            traceback.print_exc()
            print("OpenCV error in _find_homography()...")
        else:
            if mask is None:
                print("In _find_homography(), find no transfomation matrix...")
            else:
                return M, mask

    def _target_error_check(self, w_h_range):
        """Check whether the recognition result area is consistent with common sense."""
        x_min, x_max, y_min, y_max, w, h = w_h_range
        tar_width, tar_height = x_max - x_min, y_max - y_min

        if tar_width < 5 or tar_height < 5:
            print("In src_image, Taget area: width or height < 5 pixel.")
        # If the width and height of the rectangular recognition area are more than 5 times the width
        # and height of sch_img (the screen pixel difference cannot be 5 times), it is considered as a recognition error
        if tar_width < 0.1 * w or tar_width > 5 * w or tar_height < 0.2 * h or tar_height > 5 * h:
            print("Target area is 5 times bigger or 0.2 times smaller than sch_img.")


def _check_image_valid(im_source, im_search):
    """Check if the input images valid or not."""
    if im_source is not None and im_source.any() and im_search is not None and im_search.any():
        return True
    else:
        return False


def _generate_result(middle_point, pypts, confi):
    """Format the result: Define the image recognition result format."""
    ret = dict(result=middle_point,
               rectangle=pypts,
               confidence=confi)
    return ret


def _img_mat_rgb_2_gray(img_mat):
    """
    Turn img_mat into gray_scale, so that template match can figure the img data.
    "print(type(im_search[0][0])")  can check the pixel type.
    """
    assert isinstance(img_mat[0][0], np.ndarray), "input must be instance of np.ndarray"
    return cv2.cvtColor(img_mat, cv2.COLOR_BGR2GRAY)


def _cal_ccoeff_confidence(im_source, im_search):
    """To get the credibility of the two pictures, use the TM_CCOEFF_NORMED method."""
    im_source, im_search = _img_mat_rgb_2_gray(im_source), _img_mat_rgb_2_gray(im_search)
    res = cv2.matchTemplate(im_source, im_search, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    confidence = max_val
    return confidence


def _cal_rgb_confidence(img_src_rgb, img_sch_rgb):
    """Calculate similarity for color images of the same size."""
    # BGR three-channel psychology weights:
    weight = (0.114, 0.587, 0.299)
    src_bgr, sch_bgr = cv2.split(img_src_rgb), cv2.split(img_sch_rgb)

    # Calculate the BGR three-channel confidence and store it in bgr_confidence:
    bgr_confidence = [0, 0, 0]
    for i in range(3):
        res_temp = cv2.matchTemplate(src_bgr[i], sch_bgr[i], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res_temp)
        bgr_confidence[i] = max_val

    # Weighted confidence
    weighted_confidence = bgr_confidence[0] * weight[0] + bgr_confidence[1] * weight[1] + bgr_confidence[2] * weight[2]

    return weighted_confidence
