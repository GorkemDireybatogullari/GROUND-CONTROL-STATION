"""ROS2 integration: subscribers + lifecycle bridge.

Imports of ROS-only modules (e.g. ``subscribers``) are deferred to runtime —
this package must remain importable on machines without rclpy installed.
"""

from app.ros.bridge import RosBridge

__all__ = ["RosBridge"]
