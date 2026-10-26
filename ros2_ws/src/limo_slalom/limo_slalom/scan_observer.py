"""Publish a simple lidar diagnostic for the slalom starter environment."""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class ScanObserver(Node):
    """Report the minimum valid distance in a configurable frontal sector."""

    def __init__(self):
        super().__init__('scan_observer')
        self.declare_parameter('half_angle_deg', 15.0)
        self._front_distance_publisher = self.create_publisher(
            Float32, '/slalom/front_distance', 10)
        self.create_subscription(LaserScan, '/scan', self._scan_callback, 10)

    def _scan_callback(self, scan):
        half_angle = math.radians(
            self.get_parameter('half_angle_deg').get_parameter_value().double_value)
        valid_ranges = [
            distance
            for index, distance in enumerate(scan.ranges)
            if abs(scan.angle_min + index * scan.angle_increment) <= half_angle
            and math.isfinite(distance)
            and scan.range_min <= distance <= scan.range_max
        ]
        if valid_ranges:
            self._front_distance_publisher.publish(Float32(data=min(valid_ranges)))


def main(args=None):
    rclpy.init(args=args)
    node = ScanObserver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
