from __future__ import print_function, division, absolute_import

import time

from hkube_python_wrapper import Algorunner


def start(options, hkubeApi):
    Algorunner.active = True
    # pylint: disable=unused-argument
    # for i in range(0,100):
    #     print("do nothing")
    #     gevent.sleep(3)
    #     b.sendMessage("hello there " + str(i))
    i = 0
    rng = 17

    print("sending {rng} msg per second".format(rng=rng))
    while (Algorunner.active):
        for _ in range(0, rng):
            if(Algorunner.active):
                hkubeApi.sendMessage({'time':time.time()}, 'analyze')
                hkubeApi.sendMessage({'time':time.time()}, 'master')
                # hkubeApi.sendMessage("hello there master" + str(i))
                # hkubeApi.sendMessage("hello there complex" + str(i), flow='complex')
                # hkubeApi.sendMessage( bytearray(10))
                i += 1
            time.sleep(0.001)
        # rng += 10

    # node "a",
    # flowInput = options.input[6]
    # node "b", options.input = ["@a", {"@C", "@flowInput"}]
    def onMessage(msg,origin):
        # flowInput
        # print(str(input:[@a, data.prop, @c], data:<any>,))
        print("msg:"+msg+';origin:'+origin)

def stop(a):
    Algorunner.active = False

def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start,stop=stop)



if __name__ == "__main__":
    main()