
import time
from hkube_python_wrapper import Algorunner

def start(args, hkube_api):
    print("~~~~~~~~~starts~~~~~~~~~~~~")

    def handleMessage(msg, origin):
        # print('handling ' + str(msg['id']) + ' from ' + str(msg["trace"]))
        hkube_api.sendMessage(msg)



    hkube_api.registerInputListener(onMessage=handleMessage)
    hkube_api.startMessageListening()
    active = True
    while (active):

        time.sleep(10)
        stat = hkube_api.get_streaming_statistics()
        print(stat)

def main():
    print("starting algorithm runner")

    Algorunner.Debug("ws://test.hkube.io/hkube/debug/golan-get-send",start=start)


if __name__ == "__main__":
    main()