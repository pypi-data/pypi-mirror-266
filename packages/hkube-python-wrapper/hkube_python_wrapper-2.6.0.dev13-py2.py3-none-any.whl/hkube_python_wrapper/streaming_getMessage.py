from __future__ import print_function, division, absolute_import
from hkube_python_wrapper import Algorunner


def start(args, hkube_api):
    msg = args.get('streamInput')['message']
    print(msg)
    nodeName = args.get('nodeName')
    print("at " + nodeName)
    print("***" + str(msg))
    return str(msg) + "_" + nodeName


# def start(args, hkube_api):
#     # msg = args.get('streamInput')['message']
#     # msg["trace"].append(args["nodeName"])
#     # print('handling ' + str(msg['id']) + ' on ' + str(msg["trace"]))
#     # return msg
#     print ("do nothing")

def init(args):
    # print("in init" + str(args.input))
    # raise Exception('myError')
    print ("In INIT")

def main():
    print("starting algorithm runner")
    print(str(Algorunner))

    # Algorunner.Debug('ws://63.34.172.241/hkube/debug/golan4', start=start)
    Algorunner.Run(start=start, init=init)


if __name__ == "__main__":
    main()
