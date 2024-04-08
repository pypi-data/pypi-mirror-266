import time
from hkube_python_wrapper import Algorunner


def start(args, hkube_api):
    msg = args.get('streamInput')['message']
    nodeName = args.get('nodeName')
    print("at " + nodeName)
    print("***" + str(msg))
    print("going to sleep")
    # time.sleep(0.01)
    return msg


def init(args):
    print("in init" + str(args['input']))


def stop(args):
    print("in stop" + str(args))


def main():
    print("starting algorithm runner")
    print(str(Algorunner))

    # Algorunner.Debug('ws://63.34.172.241/hkube/debug/golan4', start=start)
    Algorunner.Run(start=start, init=init, stop=stop)


if __name__ == "__main__":
    main()
