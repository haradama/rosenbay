import os
import sys
import cv2
import zbar
import zbar.misc

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from . import SenbayData


class Ros2senbayPublisher(Node):
    def __init__(self):
        super().__init__("ros2senbay_publisher")
        self.pub_lst = {
            "TIME":                     self.create_publisher(Float32, "TIME", 10),
            "RPM":                      self.create_publisher(Float32, "RPM", 10),
            "SPEED":                    self.create_publisher(Float32, "SPEED", 10),
            "COOLANT_TEMP":             self.create_publisher(Float32, "COOLANT_TEMP", 10),
            "DISTANCE_SINCE_DTC_CLEAR": self.create_publisher(Float32, "DISTANCE_SINCE_DTC_CLEAR", 10),
            "MAF":                      self.create_publisher(Float32, "MAF", 10),
            "INTAKE_TEMP":              self.create_publisher(Float32, "INTAKE_TEMP", 10)
        }

        self.title = "ros2senbay"
        self.fps = 10
        self.timer = self.create_timer(1 / self.fps, self.timer_callback)
        infile = "resource/video.m4v"
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            infile
        )
        self.cap = cv2.VideoCapture(filepath)
        self.scanner = zbar.Scanner()
        self.senbayData = SenbayData()

    def timer_callback(self):
        success, frame = self.cap.read()

        if success:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            codes = self.scanner.scan(gray)
            if codes != None and len(codes) > 0:
                senbayDict = self.senbayData.decode(
                    str(codes[0].data.decode("utf-8")))
                for key, pub in self.pub_lst.items():
                    msg = Float32()
                    msg.data = senbayDict[key]
                    pub.publish(msg)
                    self.get_logger().info("{0}: {1}".format(key, msg.data))

            cv2.imshow(self.title, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.destroyWindow(self.title)
                ros2senbay_publisher.destroy_node()
                rclpy.shutdown()
                sys.exit()

        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


def main():
    rclpy.init()
    ros2senbay_publisher = Ros2senbayPublisher()
    rclpy.spin(ros2senbay_publisher)


if __name__ == "__main__":
    main()
