"""ROS2 subscriber: maps incoming messages onto the telemetry repository."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry, Path
    from sensor_msgs.msg import Imu, NavSatFix
    from std_msgs.msg import Bool as BoolMsg
    from std_msgs.msg import String as StringMsg

from rclpy.node import Node

from app.domain.telemetry import (
    GpsReading,
    ImuReading,
    Nav2Header,
    Nav2Plan,
    Nav2Pose,
    OdometryReading,
    Quaternion,
    Vector3,
)
from app.repositories.telemetry_repository import TelemetryRepository

logger = structlog.get_logger(__name__)


class TelemetrySubscriber(Node):
    """Bridges ROS2 telemetry topics into the in-memory repository."""

    def __init__(self, repository: TelemetryRepository) -> None:
        super().__init__("telemetry_api_subscriber")
        self._repository = repository
        self._subscribe()

    def _subscribe(self) -> None:
        from geometry_msgs.msg import Twist
        from nav_msgs.msg import Odometry, Path
        from sensor_msgs.msg import Imu, NavSatFix

        self.create_subscription(Imu, "/imu/fixed_cov", self._on_imu, 10)
        self.create_subscription(Odometry, "/odometry/filtered", self._on_odometry, 10)
        self.create_subscription(NavSatFix, "/gps/fixed_cov", self._on_gps, 10)
        self.create_subscription(Twist, "/cmd_vel_nav", self._on_cmd_vel, 10)
        self.create_subscription(Path, "/plan", self._on_nav2_plan, 10)

        self.get_logger().info("Telemetry subscriber active on standard topics")

    # ─── callbacks ──────────────────────────────────────────────────────────
    def _on_imu(self, msg: Imu) -> None:
        try:
            x, y, z, w = (
                msg.orientation.x,
                msg.orientation.y,
                msg.orientation.z,
                msg.orientation.w,
            )
            roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
            sin_pitch = 2 * (w * y - z * x)
            pitch = (
                math.copysign(math.pi / 2, sin_pitch)
                if abs(sin_pitch) >= 1
                else math.asin(sin_pitch)
            )
            yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
            self._repository.set_imu(ImuReading(yaw=yaw, pitch=pitch, roll=roll))
        except (ValueError, ArithmeticError) as exc:
            logger.warning("imu_quaternion_error", error=str(exc))
            self._repository.set_imu(ImuReading())

    def _on_odometry(self, msg: Odometry) -> None:
        twist = msg.twist.twist
        pose = msg.pose.pose
        self._repository.set_odometry(
            OdometryReading(
                linear_velocity=Vector3(x=twist.linear.x, y=twist.linear.y, z=twist.linear.z),
                angular_velocity=Vector3(x=twist.angular.x, y=twist.angular.y, z=twist.angular.z),
                position=Vector3(x=pose.position.x, y=pose.position.y, z=pose.position.z),
            )
        )

    def _on_cmd_vel(self, msg: Twist) -> None:
        self._repository.set_cmd_vel(msg.linear.x, msg.angular.z)

    def _on_gps(self, msg: NavSatFix) -> None:
        self._repository.set_gps(
            GpsReading(
                latitude=msg.latitude,
                longitude=msg.longitude,
                altitude=msg.altitude,
            )
        )

    def _on_armed(self, msg: BoolMsg) -> None:
        self._repository.set_armed(bool(msg.data))

    def _on_mode(self, msg: StringMsg) -> None:
        self._repository.set_mode(str(msg.data))

    def _on_nav2_plan(self, msg: Path) -> None:
        try:
            poses = [
                Nav2Pose(
                    position=Vector3(x=p.pose.position.x, y=p.pose.position.y, z=p.pose.position.z),
                    orientation=Quaternion(
                        x=p.pose.orientation.x,
                        y=p.pose.orientation.y,
                        z=p.pose.orientation.z,
                        w=p.pose.orientation.w,
                    ),
                    header=Nav2Header(
                        frame_id=p.header.frame_id,
                        stamp=p.header.stamp.sec + p.header.stamp.nanosec * 1e-9,
                    ),
                )
                for p in msg.poses
            ]
            self._repository.set_nav2_plan(
                Nav2Plan(
                    header=Nav2Header(
                        frame_id=msg.header.frame_id,
                        stamp=msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9,
                    ),
                    poses=poses,
                    pose_count=len(poses),
                )
            )
        except (AttributeError, ValueError) as exc:
            logger.warning("nav2_plan_parse_error", error=str(exc))
            self._repository.set_nav2_plan(Nav2Plan())
