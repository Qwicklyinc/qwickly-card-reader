#!/usr/bin/env python3

import threading
import time

class Repeater(threading.Thread):
    """
    Class for performing a function repeatedly on a separate thread
    """
    
    def __init__(self, action, duration=1):
        """
        action - function to be performed
        duration - time in seconds to wait between function calls
        """
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.action = action
        self.duration = duration
    
    
    def run(self):
        while not self.stop.is_set():
            
            self.action()
            
            time.sleep(self.duration)

