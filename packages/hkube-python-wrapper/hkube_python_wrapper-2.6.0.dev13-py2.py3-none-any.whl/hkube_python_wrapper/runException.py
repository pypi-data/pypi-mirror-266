from __future__ import print_function, division, absolute_import
from hkube_python_wrapper import Algorunner
import time

Algorunner.active = True


def start(options, hkubeApi):
    Algorunner.active = True
    # while (Algorunner.active):
    # time.sleep(1)
    # aaa = hkubeApi.getDataSource({"dataSourceId":"60efce8d76e4834c78d5cbdb"})
    # print(aaa)
    # aa =  hkubeApi.start_stored_subpipeline('simple1',{},True
    myVar = "Custom error message"
    raise RuntimeError(f"An error occurred: {myVar}")
    # while (True):
    #     time.sleep(1)


def init(options):
    raise RuntimeError(f"Error in init")


def stop(options):
    while (Algorunner.active):

        Algorunner.active = False


def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start,  stop=stop)


if __name__ == "__main__":
    main()
