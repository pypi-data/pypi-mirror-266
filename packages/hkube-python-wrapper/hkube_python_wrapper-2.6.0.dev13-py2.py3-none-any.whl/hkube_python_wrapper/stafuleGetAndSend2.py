
import time


def start(args, hkube_api):
    print("~~~~~~~~~starts~~~~~~~~~~~~")

    def handleMessage(msg, origin):
        #addToOrign(dic,origin)
        hkube_api.sendMessage(msg)



    hkube_api.registerInputListener(onMessage=handleMessage)
    hkube_api.startMessageListening()
    active = True
    while (active):

        time.sleep(10)
        stat = hkube_api.get_streaming_statistics()
        print(stat)

