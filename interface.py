#!/usr/bin/env python3

from enum import Enum
import os
import time
import threading
import re
from queue import Queue
import tkinter as tk
import json


config_file = open('/home/pi/qwickly/CONFIG.json')
config = json.load(config_file)
config_file.close()


class State(Enum):
    UNCONFIGURED = 0
    IDLE = 1
    ACTIVE = 2


class Sound(threading.Thread):
    """
    Class for outputting sounds in a seperate thread as to not block
    other functions. Also prevents multiple sounds from playing at once.

    Attributes:
        q (Queue): queue of sounds waiting their turn to play

    """

    def __init__(self):
        self._stop = threading.Event()
        self.q = Queue()

        threading.Thread.__init__(self)
        self.name = 'Sound'
        self.start()


    def run(self):
        while not self._stop.is_set():
            while not self.q.empty():
                os.system('mpg321 ' + self.q.get())


    def queue(self, path):
        """
        Method for adding to queue
        """

        self.q.put(path)


    def stop(self):
        self._stop.set()


class Interface(tk.Tk):
    """
    Class for controlling visible behavior of the device. Manages all
    io threads and ui window

    Attributes:
        state (State): The current state of the interface. You can read
        this attribute but for writing set_unconfigured(), set_idle()
        and set_active() should be used
    """

    def __init__(self, connected=False):
        """
        Interface constructor. Starts io threads and creates instance
        of tkinter window.

        Parameters:
            connected (bool): initial state of interface is unconfigured
            if False or idle if True
        """
        
        # Start io threads
        self._sound = Sound()

        # don't want to announce usb connection over and over
        self.usb_connected = False

        # Set up tkinter window
        super().__init__()
        self.attributes('-fullscreen', True)
        self.configure(background='white')
        self.configure(cursor='none')

        self.card_code = tk.StringVar()
        self._card_entry = tk.Entry(self, textvariable=self.card_code, show='', borderwidth=0, highlightthickness=0)
        self._card_entry.pack(fill='x')
        self._card_entry.focus()

        self.on_close = None
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.bind('<Escape>', self.escape)
        
        # Load images
        self.images = {
            'logo': tk.PhotoImage(file='/home/pi/qwickly/images/logo.png'),
            'config': tk.PhotoImage(file='/home/pi/qwickly/images/config.png'),
            'active': tk.PhotoImage(file='/home/pi/qwickly/images/active.png'),
            'idle': tk.PhotoImage(file='/home/pi/qwickly/images/idle.png'),
            'pending': tk.PhotoImage(file='/home/pi/qwickly/images/pending.png'),
            'success': tk.PhotoImage(file='/home/pi/qwickly/images/success.png'),
            'fail': tk.PhotoImage(file='/home/pi/qwickly/images/fail.png')
        }
        
        if config['custom_idle_image']:
            self.images['idle'] = tk.PhotoImage(file='/home/pi/qwickly/images/' + config['custom_idle_image'])
        
        if config['custom_active_image']:
            self.images['active'] = tk.PhotoImage(file='/home/pi/qwickly/images/' + config['custom_active_image'])
        
        self.img = tk.Label(master=self, image=None, background='white')
        self.img.pack()
        
        # initial state can be unconfigured or idle
        if connected:
            self.state = State.IDLE

            self._sound.queue('/home/pi/qwickly/sounds/phrase8.mp3')

            self.img.configure(image=self.images['idle'])

            self.update_idletasks()
        else:
            self.state = State.UNCONFIGURED

            self._sound.queue('/home/pi/qwickly/sounds/phrase1.mp3')

            self.img.configure(image=self.images['config'])
            self.update_idletasks()


    def get_entry(self):
        """
        Gets text from card input then clears it for next entry

        Returns:
            str: The card code from input
        """

        code = self.card_code.get()
        self.card_code.set('')
        return code


    def set_on_entry(self, function):
        """
        Set a the function to be ran on card entry (enter key press)

        Parameters:
            function (function): The function to be ran on entry.
            Should take a tkinter event as a parameter and not have
            a return value.
        """

        self.bind('<Return>', function)


    def set_on_close(self, function):
        """
        Set a function to be ran on program exit or if a user interrupts.
        (Triggered by the 'WM_DELETE_WINDOW' event)

        Parameters:
            function (function): The function to be ran on exit.
            Should not take any parameters or return a value.
        """

        self.on_close = function


    def set_unconfigured(self):
        """ Set interface state to unconfigured """

        if self.state != State.UNCONFIGURED:
            self.state = State.UNCONFIGURED
            self._sound.queue('/home/pi/qwickly/sounds/phrase7.mp3')
            self.img.configure(image=self.images['config'])
            self.update_idletasks()


    def set_idle(self):
        """ Set interface state to idle """

        if self.state != State.IDLE:
            if config['announce_session_close'] and self.state == State.ACTIVE:
                self._sound.queue('/home/pi/qwickly/sounds/phrase5.mp3')
            
            if self.state == State.UNCONFIGURED:
                self._sound.queue('/home/pi/qwickly/sounds/phrase8.mp3')
                
            self.state = State.IDLE

            self.img.configure(image=self.images['idle'])

            self.update_idletasks()


    def set_active(self):
        """ Set interface state to active """

        if self.state != State.ACTIVE:
            self.state = State.ACTIVE

            if config['announce_session_open']:
                self._sound.queue('/home/pi/qwickly/sounds/phrase4.mp3')

            self.img.configure(image=self.images['active'])

            self.update_idletasks()


    def indicate_pending(self):
        """
        Indicate pending until either indicate_success or
        indicate_failure is called
        """

        self.img.configure(image=self.images['pending'])
        self.update_idletasks()


    def indicate_success(self):
        self.img.configure(image=self.images['success'])
        self.update_idletasks()

        self._sound.queue('/home/pi/qwickly/sounds/sound1.mp3')

        time.sleep(1.5)

        self.img.configure(image=self.images['active'])
        
        self.update_idletasks()


    def indicate_failure(self):
        self.img.configure(image=self.images['fail'])
        self.update_idletasks()

        self._sound.queue('/home/pi/qwickly/sounds/phrase6.mp3')

        time.sleep(1)

        # Resume previous state
        if self.state == State.IDLE:

            self.img.configure(image=self.images['idle'])

            self.update_idletasks()

        if self.state == State.ACTIVE:

            self.img.configure(image=self.images['active'])

            self.update_idletasks()

        if self.state == State.UNCONFIGURED:
            self.img.configure(image=self.images['config'])
            self.update_idletasks()


    def indicate_usb_connect(self):
        # Only announce usb config onece
        if not self.usb_connected:
            self._sound.queue('/home/pi/qwickly/sounds/phrase2.mp3')
            self.usb_connected = True

        self.img.configure(image=self.images['config'])
        self.update_idletasks()
    
    
    def indicate_no_usb(self):
        # Only perform once
        if self.usb_connected:
            self.usb_connected = False
            
            if self.state == State.UNCONFIGURED:
                self.set_unconfigured()
            
            if self.state == State.IDLE:
                self._sound.queue('/home/pi/qwickly/sounds/phrase8.mp3')

                self.img.configure(image=self.images['idle'])

                self.update_idletasks()
            
            if self.state == State.ACTIVE:
                if config['announce_session_open']:
                    self._sound.queue('/home/pi/qwickly/sounds/phrase4.mp3')

                self.img.configure(image=self.images['active'])

                self.update_idletasks()


    def indicate_reboot(self):
        self.img.configure(image=self.images['config'])
        self.update_idletasks()

        self._sound.queue('/home/pi/qwickly/sounds/phrase3.mp3')
    
    
    def indicate_update(self):
        self.img.configure(image=self.images['config'])
        self.update_idletasks()
        
        self._sound.queue('/home/pi/qwickly/sounds/phrase9.mp3')


    def escape(self, event):
        self.attributes('-fullscreen', False)
        self.configure(cursor='')


    def close(self):
        # Execute provided on_close function
        if self.on_close != None:
            self.on_close()

        # Stop all io threads
        self._sound.stop()

        # Close Window
        self.destroy()
