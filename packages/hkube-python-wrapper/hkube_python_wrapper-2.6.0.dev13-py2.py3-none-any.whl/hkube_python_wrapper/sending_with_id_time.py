from __future__ import print_function, division, absolute_import

import time

from hkube_python_wrapper import Algorunner

def start(args, hkubeapi):
    i = 0
    z = 0
    sent = 0
    rate = args["input"][0]["rate"]
    print("rate is" + str(rate))
    print("message format: image,trace,id,time")
    active = True
    while active:
        for _ in range(0, rate):
            if active:
                msg = {"image": bytearray(70),
                       "trace": [args["nodeName"]],
                       "id": str(sent),
                       "time": time.time()
                       }
                hkubeapi.sendMessage(msg)
            time.sleep(1)

def stop(a):
    print("at stop")
    Algorunner.active = False

def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start,stop=stop)



if __name__ == "__main__":
    main()