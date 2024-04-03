import cv2
import numpy as np

cam = cv2.VideoCapture("Lane_Detection_Test_Video_01.mp4")

ret, frame = cam.read()
if ret:
    original_height, original_width = frame.shape[:2]

width = original_width // 3
height = original_height // 3


lower_left = (width * 0.00, height)
upper_left = (width * 0.45, height * 0.75)
upper_right = (width * 0.55, height * 0.75)
lower_right = (width , height)

points = np.array([upper_right,  upper_left, lower_left, lower_right], dtype=np.int32)
trapezoid_frame = np.zeros((height, width), dtype=np.uint8)

cv2.fillConvexPoly(trapezoid_frame, points, 1)


###############################################################5#############
trapezoid_bounds = np.array([lower_right, upper_right, upper_left, lower_left], dtype=np.float32)
trapezoid_bounds = np.array([upper_right,  upper_left, lower_left, lower_right], dtype=np.float32)

frame_bounds = np.array([[width, height], [width, 0], [0, 0], [0, height]], dtype=np.float32)
frame_bounds = np.array([[width, 0], [0, 0], [0, height], [width, height]], dtype=np.float32)
perspective_matrix = cv2.getPerspectiveTransform(trapezoid_bounds,  frame_bounds)

while True:
    ret, frame = cam.read()

    if ret is False:
        break

    resized_frame = cv2.resize(frame, (width, height))

    gray_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

    road_frame = gray_resized_frame * trapezoid_frame

    stretched_frame = cv2.warpPerspective(road_frame, perspective_matrix, (width, height))

    blur_frame = cv2.blur(stretched_frame, ksize=(7, 7))

    cv2.imshow("resized", resized_frame)
    cv2.imshow("grey", gray_resized_frame)
    cv2.imshow("Road", road_frame)
    cv2.imshow("streched", stretched_frame)
    cv2.imshow("blur-frame", blur_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()