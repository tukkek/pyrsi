#!/usr/bin/python3
import time,threading,os,subprocess,sys
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QPushButton,QVBoxLayout,QRadioButton,QButtonGroup,QSystemTrayIcon,QMessageBox
from PyQt5.QtGui import QIcon

JOYSTICK='/dev/input/js0'
LENIENCY=[.5,1,2]

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
        normal.setChecked(True)
        leniency.addButton(normal)
        layout.addWidget(normal)
        severe=QRadioButton("Severe (1:2)")
        leniency.addButton(severe)
        layout.addWidget(severe)
        #close button
        close=QPushButton("Hide")
        layout.addWidget(close)
        close.clicked.connect(self.totray)
        self.setLayout(layout)
        #self.show()
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

joystick=os.open(JOYSTICK,os.O_RDONLY|os.O_NONBLOCK) if os.path.isfile(JOYSTICK) else False
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
tray=False

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
    global pool,lastupdate
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
        pool+=LENIENCY[leniency.buttons().index(leniency.checkedButton())]
    if pool<0:
        pool=0
    text=describe()
    poollabel.setText(text)
    tray.setToolTip(text)
    threading.Timer(1,update).start()

def describe():
    if pool==0:
        return 'All rested up!'
    if pool>=60*60:
        return 'Rest for '+str(int(pool/(60*60)))+' hour(s)'
    if pool>=60:
        return 'Rest for '+str(int(pool/60))+' minute(s)'
    return 'Rest for '+str(int(pool))+' second(s)'

def popup():
    if terminate:
        return
    tray.showMessage('PyRsi',describe(),msecs=5*1000)
    setpopup()
    
def setpopup():
    global popupthread
    popupthread=threading.Timer(5*60,popup)
    popupthread.start()
    
if joystickthread!=False:
    joystickthread=threading.Thread(target=watchjoystick)
    joystickthread.start()
window=Frame()
setpopup()
threading.Timer(1,update).start()
sys.exit(app.exec_())
