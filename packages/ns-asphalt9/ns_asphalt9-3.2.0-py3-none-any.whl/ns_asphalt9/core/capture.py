import cv2

# 指定v4l2设备的路径，例如 '/dev/video0'
video_device = "/dev/video0"

# 创建VideoCapture对象
cap = cv2.VideoCapture(video_device)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FPS, 30)

# 检查视频是否成功打开
if not cap.isOpened():
    print("无法打开视频设备")
    exit()


# 定义一个函数，用于在按下指定按键时退出循环
def exit_on_key():
    return cv2.waitKey(1) & 0xFF == ord("q")


# 循环读取视频帧并显示
while not exit_on_key():
    # 读取一帧图像
    ret, frame = cap.read()

    # 如果正确读取帧，ret为True
    if not ret:
        print("无法获取视频帧")
        break

    # 显示帧
    cv2.imshow("Video", frame)

# 释放VideoCapture对象
cap.release()
# 关闭所有OpenCV窗口
cv2.destroyAllWindows()
