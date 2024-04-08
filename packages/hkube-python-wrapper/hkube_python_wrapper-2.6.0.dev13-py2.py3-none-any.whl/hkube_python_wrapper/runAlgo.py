from __future__ import print_function, division, absolute_import
from hkube_python_wrapper import Algorunner
import time

Algorunner.active = True


def start(options, hkubeApi):
    Algorunner.active = True
    print('starting activity loop')
    while (Algorunner.active):
        time.sleep(1)
    print('leaving loop')
    return 7


def stop(options):
    while (Algorunner.active):
        Algorunner.active = False


def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start, stop=stop)


if __name__ == "__main__":
    main()
