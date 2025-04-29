import cv2
import numpy as np
import math
from scipy.interpolate import interp1d

# 初始化窗口尺寸和点的列表
window_width = 360
window_height = 360
points = []
dragging_point = -1  # 标记当前正在拖动的点的索引，-1 表示没有拖动

# 计算窗口中心坐标
center_x = window_width // 2
center_y = window_height // 2

# 获取起始和终点坐标
start_x = int(input("请输入起始点的 x 坐标: "))
start_y = int(input("请输入起始点的 y 坐标: "))
end_x = int(input("请输入终点的 x 坐标: "))
end_y = int(input("请输入终点的 y 坐标: "))

# 将输入的坐标转换为图像上的坐标，以窗口中心为原点
start_x_actual = center_x + start_x
start_y_actual = center_y - start_y
end_x_actual = center_x + end_x
end_y_actual = center_y - end_y

# 添加起始和终点到点列表
points.append((start_x_actual, start_y_actual))
points.append((end_x_actual, end_y_actual))

# 鼠标回调函数
def mouse_callback(event, x, y, flags, param):
    global points, dragging_point
    # 直接使用鼠标点击的坐标作为图像上的坐标
    click_x = x
    click_y = y

    if event == cv2.EVENT_LBUTTONDOWN:
        # 检查是否靠近已有点
        for i, p in enumerate(points):
            distance = np.sqrt((click_x - p[0])**2 + (click_y - p[1])**2)
            if distance < 10:  # 设定一个距离阈值，例如 10 像素
                dragging_point = i
                break
        if dragging_point == -1:
            # 添加控制点，插入到起点和终点之间
            points.insert(-1, (click_x, click_y))
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = -1  # 释放鼠标，停止拖动
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        if dragging_point != -1 and 0 < dragging_point < len(points) - 1:
            points[dragging_point] = (click_x, click_y)

# 创建窗口并设置鼠标回调函数
cv2.namedWindow('Bezier Curve Visualization', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Bezier Curve Visualization', window_width, window_height)
cv2.setMouseCallback('Bezier Curve Visualization', mouse_callback)

def bezier_curve(points, t):
    n = len(points) - 1
    result = np.zeros(2)
    for i in range(n + 1):
        binomial_coefficient = math.factorial(n) // (math.factorial(i) * math.factorial(n - i))
        result += binomial_coefficient * ((1 - t) ** (n - i)) * (t ** i) * np.array(points[i])
    return result

while True:
    # 创建空白图像
    img = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    # 绘制网格线
    grid_size = 60
    for i in range(0, window_width, grid_size):
        cv2.line(img, (i, 0), (i, window_height), (128, 128, 128), 1)  # 绘制垂直线
    for j in range(0, window_height, grid_size):
        cv2.line(img, (0, j), (window_width, j), (128, 128, 128), 1)  # 绘制水平线

    # 绘制点
    for p in points:
        cv2.circle(img, (p[0], p[1]), 5, (0, 0, 255), -1)

    # 绘制贝塞尔曲线
    if len(points) >= 3:
        t_values = np.linspace(0, 1, 100)
        curve_points = [bezier_curve(points, t) for t in t_values]
        curve_points = np.array(curve_points, dtype=np.int32)
        for i in range(len(curve_points) - 1):
            cv2.line(img, tuple(curve_points[i]), tuple(curve_points[i + 1]), (0, 255, 0), 2)

    # 显示图像
    cv2.imshow('Bezier Curve Visualization', img)

    # 监听键盘事件
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('a') and len(points) > 2:
        # 删除上一个控制点（除起始点和终点外）
        points.pop(-2)

# 释放资源
cv2.destroyAllWindows()

# 输出途径点（控制点）坐标，转换回以窗口中心为原点的逻辑坐标
waypoints = points[1:-1]
print("控制点坐标:")
for point in waypoints:
    x = point[0] - center_x
    y = center_y - point[1]
    print(f"({x}, {y})")