#!/usr/bin/python3

import cv2, time
from flirpy.camera.boson_core_edited import Boson
import numpy as np
import struct
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def publish_image():
    rospy.init_node('thermal_image_publisher')
    pub = rospy.Publisher('boson_thermal_image', Image, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz
    bridge = CvBridge()

    with Boson() as camera:
        # set it to radiometric mode
        function_id = 0x000E000D  # sysctrlSetUsbVideoIR16Mode
        command = struct.pack(">H", 2)  # FLR_SYSCTRL_USBIR16_MODE_TLINEAR = 2
        res = camera._send_packet(function_id, data=command)

        # check mode
        function_id = 0x000E000E
        res = camera._send_packet(function_id)
        res = camera._decode_packet(res, receive_size=4)
    
        while not rospy.is_shutdown():
            # Load or capture an image using OpenCV
            img_original = camera.grab().astype(np.float32)
            img = img_original * 0.01

            img8 = (
                255
                * (img_original - img_original.min())
                / (img_original.max() - img_original.min())
            )
            
            # Convert the OpenCV image to a ROS Image message, encoding can be bgr8 too
            img_msg = bridge.cv2_to_imgmsg(img, encoding="passthrough")
            
            # Publish the message
            pub.publish(img_msg)
            
            rate.sleep()

if __name__ == '__main__':
    try:
        publish_image()
    except rospy.ROSInterruptException:
        pass