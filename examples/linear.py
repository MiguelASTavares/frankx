from argparse import ArgumentParser

from frankx import Affine, LinearRelativeMotion, Robot, JointMotion


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="172.16.0.2", help="FCI IP of the robot")
    args = parser.parse_args()

    lower_torque_thresholds_acceleration = [
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
    ]
    upper_torque_thresholds_acceleration = [
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
        150.0,
    ]
    lower_torque_thresholds_nominal = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
    upper_torque_thresholds_nominal = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
    lower_force_thresholds_acceleration = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
    upper_force_thresholds_acceleration = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
    lower_force_thresholds_nominal = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
    upper_force_thresholds_nominal = [150.0, 150.0, 150.0, 150.0, 150.0, 150.0]

    # Connect to the robot
    robot = Robot(args.host)
    robot.set_default_behavior(
        lower_torque_thresholds_acceleration,
        upper_torque_thresholds_acceleration,
        lower_torque_thresholds_nominal,
        upper_torque_thresholds_nominal,
        lower_force_thresholds_acceleration,
        upper_force_thresholds_acceleration,
        lower_force_thresholds_nominal,
        upper_force_thresholds_nominal,
    )
    robot.recover_from_errors()

    # Reduce the acceleration and velocity dynamic
    robot.set_dynamic_rel(0.15)

    joint_motion = JointMotion(
        [-1.811944, 1.179108, 1.757100, -2.14162, -1.143369, 1.633046, -0.432171]
    )
    robot.move(joint_motion)
