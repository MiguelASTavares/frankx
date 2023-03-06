from argparse import ArgumentParser
from icecream import ic
from random import uniform
import frankx
from frankx import Affine, PathMotion, Robot, JointMotion


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--host', default='172.16.0.2',
                        help='FCI IP of the robot')
    args = parser.parse_args()

    # Connect to the robot
    robot = Robot(args.host)
    robot.set_default_behavior()
    robot.recover_from_errors()

    # Reduce the acceleration and velocity dynamic
    robot.set_dynamic_rel(0.3)
    error = False
    # Define and move forwards
    motion = PathMotion([
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.420234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05)),
        Affine(0.260234 + uniform(0, 0.05), -0.134435, 0.232778 + uniform(0, 0.03),
               1.959039 + uniform(0, 0.05), 0.618942 + uniform(0, 0.05), -1.547257 + uniform(0, 0.05))
    ], blend_max_distance=0.05)
    while True:
        try:
            robot_state = robot.get_state(read_once=True)
            print(robot.has_errors)
            if robot.has_errors and error:
                robot.recover_from_errors()
                robot.move(JointMotion([-2.398350603897606, 1.6803888841404588, 1.4827302141980003, -
                                        2.654339504860994, 2.362593559182102, 3.2450054641095636, -0.01750342280159829]))
                ic("joint")
            elif robot.has_errors:
                error = True
            else:
                error = False

        except frankx.InvalidOperationException:
            robot_state = robot.get_state(read_once=False)

        robot.move(motion)
