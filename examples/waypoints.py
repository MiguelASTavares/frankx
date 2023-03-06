from argparse import ArgumentParser

from frankx import Affine, JointMotion, Robot, Waypoint, WaypointMotion

import time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--host', default='172.16.0.2',
                        help='FCI IP of the robot')
    args = parser.parse_args()

    # Connect to the robot
    robot = Robot(args.host, repeat_on_error=False)
    robot.set_default_behavior()
    robot.recover_from_errors()

    # Reduce the acceleration and velocity dynamic
    robot.set_dynamic_rel(0.7)

    joint_motion = JointMotion([-1.468450840017764, 0.0285228808740363, 2.726699447869984, -
                                1.5935590176327423, 0.20135763390871717, 1.5900819548765819, -0.688893088320891])
    robot.move(joint_motion)

    # Define and move forwards
    # motion_down = WaypointMotion([
    #    Waypoint(Affine(0.0, 0.0, -0.12), -0.2, Waypoint.Relative, 0.3),
    #    Waypoint(Affine(0.08, 0.0, 0.0), 0.0, Waypoint.Relative, 0.1),
    #    Waypoint(Affine(0.0, 0.1, 0.0, 0.0), 0.0, Waypoint.Relative, 0.4),
    # ])

    motion_down = WaypointMotion([
        Waypoint(Affine(0.150659, 0.523817, 0.594912), 0.1, 0.2),
        Waypoint(Affine(0.150659, 0.523817, 0.454912), 0.1, 0.2),
        Waypoint(Affine(0.150659, 0.523817, 0.304912), 0.1, 0,2),
    ])

    # You can try to block the robot now.
    robot.move(motion_down)

    time.sleep(3)

    joint_motion = JointMotion([-1.468450840017764, 0.0285228808740363, 2.726699447869984, -
                                1.5935590176327423, 0.20135763390871717, 1.5900819548765819, -0.688893088320891])
    robot.move(joint_motion)

    # TypeError: __init__(): incompatible constructor arguments. The following argument types are supported:
    # 1. _frankx.Waypoint()
    # 2. _frankx.Waypoint(zero_velocity: bool)
    # 3. _frankx.Waypoint(minimum_time: float)
    # 4. _frankx.Waypoint(affine: pyaffx.Affine, reference_type: _frankx.Waypoint.Waypoint = <Waypoint.Absolute: 0>, dynamic_rel: float = 1.0)
    # 5. _frankx.Waypoint(affine: pyaffx.Affine, elbow: float, reference_type: _frankx.Waypoint.Waypoint = <Waypoint.Absolute: 0>, dynamic_rel: float = 1.0)
    # 6. _frankx.Waypoint(affine: pyaffx.Affine, velocity_rel: float, blend_max_distance: float, elbow: Optional[float] = None)
