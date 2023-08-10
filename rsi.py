#!/usr/bin/python3
import time,threading,os,subprocess,sys,configparser,whitelist
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QRadioButton,QButtonGroup,QSystemTrayIcon,QMessageBox
from PyQt5.QtGui import QIcon
from pathlib import Path

SILENTPROCESSES=[]
JOYSTICK='/dev/input/js0'
LENIENCY=[.5,1,1.5,2]
PERIODSAVE=60
INCREMENT=60
MINUTE=60
HOUR=60*MINUTE

class Frame(QWidget):
    def __init__(self):
        global poollabel,leniency
        super().__init__()
        self.inittray()
        self.setWindowTitle('PyRsi')    
        layout=QVBoxLayout();
        #label
        poollabel=QLabel(describe())
        layout.addWidget(poollabel)
        #radio group
        leniency=QButtonGroup(self)
        lax=QRadioButton("Lax (2:1)")
        leniency.addButton(lax)
        layout.addWidget(lax)
        normal=QRadioButton("Normal (1:1)")
        leniency.addButton(normal)
        layout.addWidget(normal)
        normal.setChecked(True)
        cautious=QRadioButton("Cautious (2:3)")
        leniency.addButton(cautious)
        layout.addWidget(cautious)
        severe=QRadioButton("Severe (1:2)")
        leniency.addButton(severe)
        layout.addWidget(severe)
        if 'data' in config:
            leniency.buttons()[int(config['data']['leniency'])].setChecked(True)
        #add / remove time
        self.addbuton(f"Add {INCREMENT} minutes",layout,self.moretime)
        self.addbuton(f"Remove {INCREMENT} minutes",layout,self.lesstime)
        #hide to tray
        self.addbuton("Hide",layout,self.totray)
        self.setLayout(layout)
    def moretime(self):
        global pool
        pool+=INCREMENT*60
    def lesstime(self):
        global pool
        pool-=INCREMENT*60
        if pool<0:
            pool=0
    def addbuton(self,label,layout,action):
        b=QPushButton(label)
        layout.addWidget(b)
        b.clicked.connect(action)
        return b
    def closeEvent(self, event): #fired on window closed
        if QMessageBox.question(self,'Exit','Are you sure you want to disable PyRsi?', QMessageBox.Yes, QMessageBox.No)==QMessageBox.Yes:
            global terminate
            popupthread.cancel()
            terminate=True
            event.accept()
            app.quit()
        else:
            event.ignore()
    def totray(self):
        self.hide()
    def inittray(self):
        global tray
        tray=QSystemTrayIcon(self)
        tray.setIcon(QIcon(os.path.join(sys.path[0],'clock.png')))
        tray.setVisible(True)
        tray.activated.connect(self.activate)
    def activate(self):
        self.show()
        self.center()
    def center(self):
        frameGm = self.frameGeometry()
        d=QApplication.desktop()
        screen = d.screenNumber(d.cursor().pos())
        centerPoint = d.screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    def getleniency(self):
        return leniency.buttons().index(leniency.checkedButton())

joystick=os.open(JOYSTICK,os.O_RDONLY|os.O_NONBLOCK) if os.path.exists(JOYSTICK) else False
lastjoystick=time.time()
joystickthread=False

app = QApplication(sys.argv)
window = False
poollabel=False

pool=0
popupthread=False
terminate=False
leniency=False
lastupdate=False
lastsave=False
tray=False

config=configparser.ConfigParser()
ini=Path.home() / '.pyrsi.ini'

def watchjoystick():
    global lastjoystick
    while True:
        if terminate:
            return
        try:
            os.read(joystick,8)
            lastjoystick=time.time()
        except:#no new data to read
            time.sleep(1)

def update():
    if terminate:
        return
    global pool,lastupdate,lastsave
    now=time.time()
    if lastupdate!=False and now-lastupdate>=10:#resume from suspension
        pool-=now-lastupdate
    lastupdate=now
    idle=True
    if now-lastjoystick<=1:
        idle=False
    else:
        idle=int(subprocess.Popen('xprintidle', stdout=subprocess.PIPE).stdout.read()[:-1])>1000
    if idle:
        pool-=1
    else:
        pool+=LENIENCY[window.getleniency()]
    if pool<0:
        pool=0
    text=describe()
    poollabel.setText(text)
    tray.setToolTip(text)
    threading.Timer(1,update).start()
    if lastsave==False:
        lastsave=now
    elif now>=lastsave+PERIODSAVE:
        lastsave=now
        saveconfig()

def describe():
    if pool==0:
        return 'All rested up!'
    if pool>=60*60:
        return 'Rest for '+str(round(pool/(HOUR)))+' hour(s)'
    if pool>=60:
        return 'Rest for '+str(round(pool/MINUTE))+' minute(s)'
    return 'Rest for '+str(round(pool))+' second(s)'

def checkfullscreen():
    for name in SILENTPROCESSES:
        if os.system(f'pidof "{name}"')==0:
            return True
        if os.system(f'xprop -name {name}')==0:
            return True
    return False

def popup():
    if terminate:
        return
    state=describe()
    p=pool
    while p>=60:
        p/=60
    p=round(p)
    print(state)
    if (p<10 or p%10==0) and not checkfullscreen():
        tray.showMessage('PyRsi',state,msecs=5*1000)
    setpopup()
    
def setpopup():
    global popupthread
    popupthread=threading.Timer(10*MINUTE if pool==0 else MINUTE,popup)
    popupthread.start()
    
def loadconfig():
    config.read(ini)
    if 'data' in config:
        data=config['data']
        global pool,lastupdate
        pool=float(data['pool'])
        lastupdate=float(data['lastupdate'])
    whitelist.setup(SILENTPROCESSES)
        
def saveconfig():
    config['data']={}
    config['data']['pool']=str(pool)
    config['data']['lastupdate']=str(lastupdate)
    config['data']['leniency']=str(window.getleniency())
    config.write(open(ini,'w'))
    
if joystick!=False:
    joystickthread=threading.Thread(target=watchjoystick)
    joystickthread.start()
loadconfig()
window=Frame()
setpopup()
threading.Timer(1,update).start()
sys.exit(app.exec_())
