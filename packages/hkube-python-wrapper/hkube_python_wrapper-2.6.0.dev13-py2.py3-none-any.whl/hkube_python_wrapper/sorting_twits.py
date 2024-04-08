import time

# my remark
def start(args, hkube_api):
    z = [0,0]

    def handleMessage(msg, origin):

        # print("msg[text]="+msg["text"])
        # print("===============================")
        # print("got massage from " + origin )
        # print("===============================")
        if (len(str(msg["text"])) > 100):
            z[0] += 1
            # print("len(msg)>100")
            hkube_api.sendMessage(msg["text"], flowName='analyze')
            print ("analyze " + str(z[0]))
        else:
            z[1] += 1
            # print("len(msg)<100")
            hkube_api.sendMessage(msg["text"])
            print ("master " + str(z[1]))
        # hkubeApi.sendMessage("hello there analyze" + str(i), flowName='analyze')
        # hkubeApi.sendMessage("hello there master" + str(i))
        # time.sleep(0.5)

    hkube_api.registerInputListener(onMessage=handleMessage)
    hkube_api.startMessageListening()
    active = True
    while (active):
        time.sleep(1)
