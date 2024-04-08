from __future__ import print_function, division, absolute_import

import time

from hkube_python_wrapper import Algorunner

def start(args, hkubeapi):
    i = 0
    z = 0
    sent = 0
    # rng = args["input"][0]["rng"]
    # burst = args["input"][0]["burst"]
    # sleepTime = args["input"][0]["sleepTime"]
    # totalMsg = args["input"][0]["totalMsg"]
    # error = args["input"][0]["error"]
    rng = 5
    burst = 5
    sleepTime = [1,4]
    totalMsg = 600
    error = 5
# {"rng":1000,"burst":3,"sleepTime":60,"sleepTime":[1,1],"totalMsg":1000,"error":1}
    print("sleep every -" + str(sleepTime[0]) + "minutes")
    print("for -" + str(sleepTime[1]) + "seconds")
    msg = {"image": bytearray(70),
           "trace": [args["nodeName"]]
           }

    active = True

    r = rng
    print("xxxxxxxxxx")
    while active:
        for _ in range(0, r):
            if active:
                msg = {"image": bytearray(70),
                       "trace": [args["nodeName"]],
                       "id": str(sent),
                       "time": str(int(time.time() * 1000))
                       }

                hkubeapi.sendMessage(msg, flowName='analyze')
                hkubeapi.sendMessage(msg)
            sent += 1
        i += 1
        if i % 60 == 0:
            z += 1
            print("z=" + str(z))
            hkubeapi.resetQueue()
        if i % 600 == 0:
            print("******** start burst ********")
            r = rng * burst
        if i % 900 == 0:
            r = rng
            i = 0
            print("========== end burst ==========")
        if z > sleepTime[0]:
            z = 0
            print("======= start sleep ========")
            time.sleep(sleepTime[1])
            print("======= end sleep ========")
        if sent > totalMsg:
            if error:
                raise Exception("raise error for getting to " + sent)
            time.sleep(sleepTime[1])
            active = False
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