import cv2
import numpy as np

cam = cv2.VideoCapture("Lane_Detection_Test_Video_01.mp4")

ret, frame = cam.read()
if ret:
    original_height, original_width = frame.shape[:2]


width = original_width // 4
height = original_height // 3

lower_left = (0.1, height*0.98)
upper_left = (width * 0.47, height * 0.76)
upper_right = (width * 0.55, height * 0.76)
lower_right = (width*0.99, height*0.98)

points = np.array([upper_right, upper_left, lower_left, lower_right], dtype=np.int32)
trapezoid_frame = np.zeros((height, width), dtype=np.uint8)

cv2.fillConvexPoly(trapezoid_frame, points, 1)

###############################################################5#############
trapezoid_bounds = np.array([upper_right, upper_left, lower_left, lower_right], dtype=np.float32)
frame_bounds = np.array([[width, 0], [0, 0], [0, height], [width, height]], dtype=np.float32)
perspective_matrix = cv2.getPerspectiveTransform(trapezoid_bounds, frame_bounds)

##########################################7####################################
sobel_vertical = np.float32([[-1, -2, -1],
                             [0, 0, 0],
                             [1, 2, 1]])
sobel_horizontal = sobel_vertical.T


####################################8################################

threshold_value = int(255 / 2)  # Initial threshold value

while True:
    ret, frame = cam.read()

    if ret is False:
        break

    resized_frame = cv2.resize(frame, (width, height))
    original_copy_frame = resized_frame.copy()

    gray_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

    road_frame = gray_resized_frame * trapezoid_frame

    stretched_frame = cv2.warpPerspective(road_frame, perspective_matrix, (width, height))

    blur_frame = cv2.blur(stretched_frame, ksize=(7, 7))

    stretched_frame_float32 = stretched_frame.astype(np.float32)

    sobel_matrix_vertical = cv2.filter2D(stretched_frame_float32, -1, sobel_vertical)

    sobel_matrix_horizontal = cv2.filter2D(stretched_frame_float32, -1, sobel_horizontal)

    result_sobel_matrix = np.sqrt(sobel_matrix_vertical**2 + sobel_matrix_horizontal**2)

    sobel_matrix = cv2.convertScaleAbs(result_sobel_matrix)
    _, binarized_frame = cv2.threshold(sobel_matrix, threshold_value, 255, cv2.THRESH_BINARY)

    #########################9###############################################

    frame_copy = binarized_frame.copy()

    height, width = frame_copy.shape[:2]
    num_columns = int(width * 0.05)
    frame_copy[:, :num_columns] = 0
    frame_copy[:, -num_columns:] = 0

    left_half = frame_copy[:, :width // 2]
    right_half = frame_copy[:, width // 2:]

    left_coordinates = np.argwhere(left_half > 1)

    right_coordinates = np.argwhere(right_half > 1)

    left_xs = left_coordinates[:, 1]
    left_ys = left_coordinates[:, 0]

    right_xs = right_coordinates[:, 1] + (width // 2)
    right_ys = right_coordinates[:, 0]


    left_line_coeffs = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
    right_line_coeffs = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)

    left_b, left_a = left_line_coeffs
    right_b, right_a = right_line_coeffs

    left_top = (0, 0)
    left_bottom = (0, height)
    right_top = (width//2, 0)
    right_bottom = (width//2, height)

    left_top_y = 0
    left_top_x = int((-left_b) / left_a)
    left_bottom_y = height
    left_bottom_x = int((height - left_b) / left_a)

    if -10**8 <= left_top_x <= 10**8:
        left_top = (left_top_x, left_top_y)
    else:
        print("found")
    if -10**8 <= left_bottom_x <= 10**8:
        left_bottom = (left_bottom_x, left_bottom_y)

    right_top_x = int((-right_b) / right_a)
    right_top_y = 0
    right_bottom_y = height
    right_bottom_x = int((height - right_b) / right_a)

    if -10**8 <= right_top_x <= 10**8:
        right_top = (right_top_x, right_top_y)
    if -10**8 <= right_bottom_x <= 10**8:
        right_bottom = (right_bottom_x, right_bottom_y)

    cv2.line(frame_copy, left_top, left_bottom, (200, 0, 0), 5)

    cv2.line(frame_copy, right_top, right_bottom, (100, 0, 0), 5)

    middle_top = (frame_copy.shape[1] // 2, 0)
    middle_bottom = (frame_copy.shape[1] // 2, frame_copy.shape[0])
    line_frame = cv2.line(frame_copy, middle_top, middle_bottom, (255, 0, 0), 1)


    #############################################ex11###################################################################

    blank_frame = np.zeros((height, width), dtype=np.uint8)

    left_part_frame = cv2.line(blank_frame, left_top, left_bottom, (255, 0, 0), 3)

    perspective_matrix2 = cv2.getPerspectiveTransform(frame_bounds, trapezoid_bounds)

    left_lines_frame = cv2.warpPerspective(blank_frame, perspective_matrix2, (width, height))

    left_coordinates = np.argwhere(left_lines_frame > 1)


    blank_frame = np.zeros((height, width), dtype=np.uint8)

    right_part_frame = cv2.line(blank_frame, right_top, right_bottom, (255, 0, 0), 3)

    perspective_matrix2 = cv2.getPerspectiveTransform(frame_bounds, trapezoid_bounds)

    right_lines_frame = cv2.warpPerspective(blank_frame, perspective_matrix2, (width, height))
    right_coordinates = np.argwhere(right_lines_frame > 1)


    for y, x in left_coordinates:
        original_copy_frame[y, x] = (0, 0, 255)
    for y, x in right_coordinates:
        original_copy_frame[y, x] = (0, 255, 0)


    cv2.imshow("resized", resized_frame)
    cv2.imshow("Trapezoid", trapezoid_frame * 255)
    cv2.imshow("grey", gray_resized_frame)
    cv2.imshow("Road", road_frame)
    cv2.imshow("stretched", stretched_frame)
    cv2.imshow("blur-frame", blur_frame)
    cv2.imshow("Sobel", sobel_matrix)
    cv2.imshow("binarized_frame", binarized_frame)
    cv2.imshow("line_frame", line_frame)
    cv2.imshow("left", left_lines_frame)
    cv2.imshow("right", right_lines_frame)
    cv2.imshow("final", original_copy_frame)



    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
