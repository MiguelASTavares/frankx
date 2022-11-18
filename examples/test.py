from argparse import ArgumentParser
from cgi import test
from re import I
from geeteventbus.subscriber    import subscriber
from geeteventbus.eventbus      import eventbus
from geeteventbus.event         import event      
from time import sleep

import frankx
from frankx import *
from statistics import mean
import random


#Connect to the robot
host = "172.16.0.2"       
robot = Robot(host, repeat_on_error=False)
robot.set_dynamic_rel(0.6)
robot.set_default_behavior()
robot.recover_from_errors()

def save_values(file,robot):
       file_object = open(file, 'a')
   
            
       state = robot.read_once()
       print('\nPose: ', robot.current_pose())
       file_object.write('\n\nPose: ' +  str(robot.current_pose()))
       print('O_TT_E: ', state.O_T_EE)
       file_object.write('\nO_TT_E: ' + str(state.O_T_EE))
       print('Joints: ', state.q)
       file_object.write('\nJoints: ' + str(state.q))
       print('Elbow: ', state.elbow)
       file_object.write('\nElbow: ' +  str(state.elbow))
       
       sleep(0.3)
     
    


def to_animation(file_read, file_write):
   
    file = open(file_read, 'r')
    write_file = open(file_write,'w')
    temp = ""
    s = ""
    for line in file:

        if line.find('Joints') == 0:
            split_line = line.split(':')


            joint_values = split_line[1].split(",")
            
            j1 = '{:.4f}'.format(round(float(joint_values[0].split("[")[1]),4))
            j2 = '{:.4f}'.format(round(float(joint_values[1]),4))
            j3 = '{:.4f}'.format(round(float(joint_values[2]),4))
            j4 = '{:.4f}'.format(round(float(joint_values[3]),4))
            j5 = '{:.4f}'.format(round(float(joint_values[4]),4))
            j6 = '{:.4f}'.format(round(float(joint_values[5]),4))
            j7 = '{:.4f}'.format(round(float(joint_values[6].split("]")[0]),4))
            
            s = str(str(j1)) + " " + str(j2) + " " + str((j3)) + " " +  str(j4) + " " + str((j5)) + " " + str((j6)) + " " + str((j7))
            if s != temp:
                print("Saving...")
                write_file.write( s + "\n")
            
            temp = s
def move(robot, file):
   

    move_successful = robot.move_async(JointMotion([-0.0573, 1.1833, 0.0044, -0.6948, 2.7522, 2.8818, 2.7217 ]))

        
    move_successful.join()

def detect_hand(robot):
    hand = False
    torque = []
    x = []
    sleep(0.5)
    while not(hand):
        state = robot.read_once()
        torque = state.tau_J
       
        x.append(torque[5])
        val = round(mean(x),3)
        print(val)
        if torque[5] > val+0.2 or torque[5] <val -0.2:
            hand = True
        sleep(0.5)
    
    


    impedance_motion = ImpedanceMotion(90, 20) # This is where the human like behavior is initiated for the hand shake.
    

    robot.move_async(impedance_motion)
    #move_successful = robot.move_async(JointMotion([-1.0573, -0.6833, -0.6044, -2.3948, 0.07522, 1.8818, 2.7217 ]))

    val_f = 1000000000
    
    while True:
        try:
            state = robot.get_state(read_once=True)
            torque = state.tau_J
            
            print("Deu: " , torque)

        except frankx.InvalidOperationException :
            state = robot.get_state(read_once=False)
            torque = state.tau_J
            tt = torque[5] 
            
            if abs(abs(val_f) - abs(tt)) < 0.05:
                print(abs(abs(val_f) - abs(tt)))
                print("handshake has stoped")   
            #print("Não Deu: " , torque)

            val_f = tt
        
        sleep(0.2)

    print("aqui")
    input()
    print("aqui tbm")
    impedance_motion.finish()
    robot_thread.join() 


op = input()

if op == "s":
    save_values("test.txt",robot)
elif op == "m":
    move(robot, "test_p.txt")
    print("finish")
    detect_hand(robot)
    print("out")
else:
    to_animation("test.txt", "test_p.txt")
    


