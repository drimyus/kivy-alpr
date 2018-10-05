import cv2


def frame2buf(cvimg, size):
    cvimg = cv2.resize(cvimg, (int(size[0]), int(size[1])))
    cvimg = cv2.flip(cvimg, 0)
    buf = cvimg.tostring()
    return buf
