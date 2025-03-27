import cv2
import numpy as np
import math
from scipy.interpolate import interp1d

# 初始化窗口尺寸和点的列表
window_width = 600
window_height = 600
points = []
dragging_point = -1  # 标记当前正在拖动的点的索引，-1 表示没有拖动

# 获取起始和终点坐标
start_x = int(input("请输入起始点的 x 坐标: "))
start_y = int(input("请输入起始点的 y 坐标: "))
end_x = int(input("请输入终点的 x 坐标: "))
end_y = int(input("请输入终点的 y 坐标: "))

# 将输入的坐标转换为原点在左下角的坐标
start_y = window_height - start_y
end_y = window_height - end_y

# 添加起始和终点到点列表
points.append((start_x, start_y))
points.append((end_x, end_y))

# 鼠标回调函数
def mouse_callback(event, x, y, flags, param):
    global points, dragging_point
    if event == cv2.EVENT_LBUTTONDOWN:
        # 检查是否靠近已有点
        for i, p in enumerate(points[:-1]):
            distance = np.sqrt((x - p[0])**2 + (y - p[1])**2)
            if distance < 10:  # 设定一个距离阈值，例如 10 像素
                dragging_point = i
                break
        if dragging_point == -1:
            # 添加途径点，不进行坐标转换
            insert_index = len(points) - 1
            for i in range(len(points) - 1):
                if x < points[i][0]:
                    insert_index = i
                    break
            points.insert(insert_index, (x, y))
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_point = -1  # 释放鼠标，停止拖动
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        if dragging_point != -1:
            points[dragging_point] = (x, y)

# 创建窗口并设置鼠标回调函数
cv2.namedWindow('Bezier Curve Visualization')
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
    grid_size = 120  # 60cm * 2，因为 1m 假设对应 200 像素，60cm 对应 120 像素
    for i in range(0, window_width, grid_size):
        cv2.line(img, (i, 0), (i, window_height), (128, 128, 128), 1)  # 绘制垂直线
    for j in range(0, window_height, grid_size):
        cv2.line(img, (0, j), (window_width, j), (128, 128, 128), 1)  # 绘制水平线

    # 绘制点
    for p in points:
        cv2.circle(img, p, 5, (0, 0, 255), -1)

    # 绘制贝塞尔曲线
    if len(points) >= 4:
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

# 输出途径点坐标，进行坐标转换
waypoints = points[1:-1]
print("途径点坐标:")
for point in waypoints:
    x, y = point
    y = window_height - y
    print(f"({x}, {y})")