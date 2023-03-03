from time import sleep
from math import sqrt
from argparse import ArgumentParser
import frankx
from frankx import *


def estimate_duration(j_indx: int, full_dist: float) -> float:
    max_joint_velocity = [2.175, 2.175, 2.175,
                          2.175, 2.610, 2.610, 2.610]  # [rad/s]
    max_joint_acceleration = [15.0, 7.5, 10.0,
                              12.5, 15.0, 20.0, 20.0]  # [rad/s²]

    vel_rel = 0.4
    vel = max_joint_velocity[j_indx] * vel_rel
    acc = max_joint_acceleration[j_indx]

    time_to_accelerate = (vel)/acc

    dis_travel_during_acc = 0.5*acc*(time_to_accelerate**2)

    time_travel_at_full_speed = ((full_dist - 2*dis_travel_during_acc)/(vel))

    full_time = time_travel_at_full_speed + time_to_accelerate*2

    empiric_error = 0.17

    if dis_travel_during_acc > full_dist:
        full_time = sqrt((2*full_dist)/acc)

    return full_time + empiric_error


def find_joint_with_motion(joint_array_new: "list[float]", joint_array_old: "list[float]") -> "tuple[int,float]":
    for indx, joint in enumerate(joint_array_new):
        if joint != joint_array_old[indx]:
            return indx, abs(abs(joint) - abs(joint_array_old[indx]))
    return -1, -1


file = open("anime.txt", "r", encoding="utf-8")

parser = ArgumentParser()
parser.add_argument('--host', default='172.16.0.2', help='FCI IP of the robot')
args = parser.parse_args()

# Connect to the robot
robot = Robot(args.host)
robot.set_default_behavior()
robot.recover_from_errors()

# Reduce the acceleration and velocity dynamic
robot.set_dynamic_rel(0.4)
old_line = ""
old_joints = []
joints = []
error = False


for line in file:

    if line != old_line:
        line = line.replace("  ", " ")
        line = line.replace("\n", "")
        joints = line.split(" ")
        joints = [float(val) for val in joints]
        indx, dist = find_joint_with_motion(joints, old_joints)
        print(indx, dist)
        if indx == -1 and dist == -1:
            continue
        duration = estimate_duration(indx, dist)
        print(duration)
        robot.move_async(JointMotion(joints))

        sleep(0.09)
    old_joints = joints
    old_line = line
