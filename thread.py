import threading
import time
import application_view


class UpDateThread (threading.Thread):
    def __init__(self, name, parent_frame):
        threading.Thread.__init__(self)
        print("initializing")
        self.name = name
        self.parent_frame = parent_frame
        print("initialing...parent_frame: {}".format(self.parent_frame))
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        #self.lock.acquire(blocking=False)
        while self.running:
          print("in the run")
          print(self.parent_frame.tx_status.get())
          self.update()
        #self.lock.release()

    def terminate_run(self):
        self.running = False


    def update(self):

        print("in the update")
        print("before the first parent_frame access")
        print(self.parent_frame.tx_status.get())
        print("after the first parent_frame access")
        self.parent_frame.tx_status.set("Creating the tx")
        print("after the first")
        self.parent_frame.view.update()
        print("Creating the tx")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx .")
        self.parent_frame.view.update()
        print("Creating the tx .")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx ..")
        self.parent_frame.view.update()
        print("Creating the tx ..")
        time.sleep(1)
        self.parent_frame.tx_status.set("Creating the tx ...")
        self.parent_frame.view.update()
        print("Creating the tx ...")
        time.sleep(1)
        #parent_frame.after(0, self.update(parent_frame))
