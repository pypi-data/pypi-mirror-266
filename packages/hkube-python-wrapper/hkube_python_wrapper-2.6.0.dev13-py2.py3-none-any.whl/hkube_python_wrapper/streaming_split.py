from __future__ import print_function, division, absolute_import
from hkube_python_wrapper import Algorunner
from profile import Profiler

counter = [0]
profiler = Profiler()


def start(args, hkube_api):
    msg = args.get('streamInput')['message']
    nodeName = args.get('nodeName')
    print("at " + nodeName)
    print("***" + str(msg))
    hkube_api.sendMessage(str(msg) + "_" + nodeName, flowName='ContinuMaster')
    counter[0] = counter[0] + 1
    if (counter[0] % 100 == 0):
        profiler.printIncreased()

    return None


def main():
    print("starting algorithm runner")
    print(str(Algorunner))

    # Algorunner.Debug('ws://63.34.172.241/hkube/debug/golan4', start=start)
    Algorunner.Run(start=start)


if __name__ == "__main__":
    main()
