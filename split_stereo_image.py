import rosbag
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import argparse
import os

# 解析命令行参数
parser = argparse.ArgumentParser(description='将bag文件中的彩色图像分割为左右灰度图像')
parser.add_argument('input_bag', type=str, help='输入的bag文件路径')
parser.add_argument('--output_bag', type=str, help='输出的bag文件路径(可选)')
args = parser.parse_args()

# 设置输出bag文件名
if args.output_bag:
    output_bag_path = args.output_bag
else:
    input_filename = os.path.basename(args.input_bag)
    output_bag_path = f'split_{input_filename}'

# 打开输入的bag文件
input_bag = rosbag.Bag(args.input_bag, 'r')

# 创建新的bag文件用于保存分割后的图像
output_bag = rosbag.Bag(output_bag_path, 'w')

# 创建CvBridge对象
bridge = CvBridge()

for topic, msg, t in input_bag.read_messages():
    if topic == '/color_image':
        # 将ROS图像消息转换为OpenCV图像
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # 将彩色图像转换为灰度图
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 分割图像为左右两部分
        height, width = gray_image.shape
        left_image = gray_image[:, :width//2]
        right_image = gray_image[:, width//2:]
        
        # 确保左右图像的尺寸为1280x720
        left_image = cv2.resize(left_image, (1280, 720))
        right_image = cv2.resize(right_image, (1280, 720))
        
        # 将OpenCV图像转换回ROS图像消息
        left_msg = bridge.cv2_to_imgmsg(left_image, encoding='mono8')
        right_msg = bridge.cv2_to_imgmsg(right_image, encoding='mono8')
        
        # 如果msg.header.stamp是0的话就使用t，如果不是0就用它
        if msg.header.stamp == 0:
            print("时间戳为0")
            left_msg.header.stamp = t
            right_msg.header.stamp = t
        else:
            print("时间戳不为0")
            left_msg.header.stamp = msg.header.stamp
            right_msg.header.stamp = msg.header.stamp
        # 打印时间戳
        # print(f"修改后的左图像时间戳: {left_msg.header.stamp}")
        # print(f"修改后的右图像时间戳: {right_msg.header.stamp}")
        # print(f"当前图像时间戳: {msg.header.stamp}")
        # 写入新的bag文件
        output_bag.write('/left_gray_image', left_msg, t)
        output_bag.write('/right_gray_image', right_msg, t)
    else:
        # 对于其他话题,直接写入新的bag文件
        output_bag.write(topic, msg, t)

# 关闭bag文件
input_bag.close()
output_bag.close()

print(f"处理完成。分割后的灰度图像已保存到{output_bag_path}文件中。")
