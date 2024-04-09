from . import k3s
import argparse
from kubernetes import client, config


def main():
    parser = argparse.ArgumentParser(description="ignite k3s", usage="ign8_k3s <action> \n\n \
               \
               version : 0.0.1 k3s  \n                                              \
               actions:\n                                                      \
               status        status on k3s \n\
               start         start and enable ignite k3s systemd daemon \n\
               stop          stop and disable ignite k3s systemd daemon \n\
               service       Run ignite k3s in terminal as a service\n\
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")


    if args.action[0] == "status":
        k3s.status()


    if args.action[0] == "start":
        k3s.start()
    
    if args.action[0] == "stop":
        k3s.stop()
        

    if args.action[0] == "service":
        k3s.service()