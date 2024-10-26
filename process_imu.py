import rosbag
from sensor_msgs.msg import Imu
import argparse
import os

# 添加命令行参数解析
parser = argparse.ArgumentParser(description='处理IMU数据并缩放线性加速度')
parser.add_argument('input_bag', type=str, help='输入的bag文件路径')
parser.add_argument('--output_bag', type=str, help='输出的bag文件路径(可选)')
args = parser.parse_args()

# 设置比例因子
scale_factor = 9.80665 / 1000.0  # 例如,将加速度值放大1.5倍

# 设置输出bag文件名
if args.output_bag:
    output_bag_path = args.output_bag
else:
    input_filename = os.path.basename(args.input_bag)
    output_bag_path = f'processed_{input_filename}'

# 打开原始bag文件
input_bag = rosbag.Bag(args.input_bag, 'r')

# 创建新的bag文件用于保存修改后的数据
output_bag = rosbag.Bag(output_bag_path, 'w')

imu_counter = 0  # 添加计数器来跟踪IMU消息

for topic, msg, t in input_bag.read_messages():
    if topic == '/mavros/imu/data_raw':
        imu_counter += 1
        if imu_counter % 2 == 0:  # 只处理偶数编号的IMU消息
            # 创建新的Imu消息
            new_msg = Imu()
            new_msg.header = msg.header
            
            # 缩放线性加速度
            new_msg.linear_acceleration.x = msg.linear_acceleration.x * scale_factor
            new_msg.linear_acceleration.y = msg.linear_acceleration.y * scale_factor
            new_msg.linear_acceleration.z = msg.linear_acceleration.z * scale_factor
            
            # 保持其他数据不变
            new_msg.angular_velocity = msg.angular_velocity
            new_msg.orientation = msg.orientation
            
            # 将修改后的消息写入新的bag文件
            output_bag.write(topic, new_msg, t)
    else:
        # 对于非IMU数据,直接写入新的bag文件
        output_bag.write(topic, msg, t)

# 关闭bag文件
input_bag.close()
output_bag.close()

print(f"处理完成。修改后的数据已保存到{output_bag_path}文件中。")
