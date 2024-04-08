from __future__ import print_function, division, absolute_import
import time
from hkube_python_wrapper import Algorunner

def start(args, hkubeapi):
    i = 0
    z = 0
    sent = 0
    burst = 1001 # args["input"][0]["burst"]
    burstCount = 200 #=  args["input"][0]["burstCount"]
    Algorunner.active = True
    print("xxxxxxxxxx")

    for _ in range(0, int(burstCount)):
        for _ in range(0, int(burst)):
            if Algorunner.active:
                msg = {"image": bytearray(70),
                       "trace": [args["nodeName"]],
                       "id": str(sent),
                       "time": str(int(time.time() * 1000))
                       }
                hkubeapi.sendMessage(msg)
                sent += 1
        time.sleep(1)
    time.sleep(1000)
    print("done")



def stop(a):
    Algorunner.active = False
    print("at close")

def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start,stop=stop)



if __name__ == "__main__":
    main()