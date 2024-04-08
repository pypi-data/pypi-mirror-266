import time


def start(options, hkubeApi):
    active = True
    # pylint: disable=unused-argument
    # for i in range(0,100):
    #     print("do nothing")
    #     gevent.sleep(3)
    #     b.sendMessage("hello there " + str(i))
    i = 0
    rng = 10
    while (active):
        print("sending {rng} msg per second".format(rng=rng))
        for _ in range(0, rng):
            if(active):
                hkubeApi.sendMessage("hello there analyze" + str(i), flowName='analyze')
                hkubeApi.sendMessage("hello there master" + str(i))
                # hkubeApi.sendMessage("hello there complex" + str(i), flow='complex')
                # hkubeApi.sendMessage( bytearray(10))
                i += 1
            time.sleep(1)

