
import time
from hkube_python_wrapper import Algorunner

def start(args, hkube_api):
    print("~~~~~~~~~starts~~~~~~~~~~~~")

    def handleMessage(msg, origin):
        print('handling ' + str(msg['id']) + ' from ' + str(msg["trace"]))
    hkube_api.registerInputListener(onMessage=handleMessage)
    hkube_api.startMessageListening()
    active = True
    while (active):
        time.sleep(10)

def stop(a):
    Algorunner.active = False
    print("at stop")

def main():
    print("starting algorithm runner")
    print(str(Algorunner))
    Algorunner.Run(start=start,stop=stop)



if __name__ == "__main__":
    main()