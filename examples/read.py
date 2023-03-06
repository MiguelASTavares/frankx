from argparse import ArgumentParser
from time import sleep, time

from frankx import Affine, Robot


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--host', default='172.16.0.2', help='FCI IP of the robot')
    args = parser.parse_args()

    robot = Robot(args.host)
    robot.set_default_behavior()
    file = open("anime.txt", "w")
    
    while True:
        state = robot.read_once()
        print('\nPose: ', robot.current_pose())
        print('O_TT_E: ', state.O_T_EE)
        print('Joints: ', state.q)
        print('Elbow: ', state.elbow)
        jj = [round(val,4) for val in state.q]
        joint = str(jj)
        joint = joint.replace(",", " ")
        joint = joint.replace("[", "")
        joint = joint.replace("]", "")
        file.write(joint)
        file.write("\n")       
        sleep(0.05)
