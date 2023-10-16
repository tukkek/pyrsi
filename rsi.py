#!/usr/bin/python3
#TODO refactor modules for joystick, popup, tray...
import time,threading,os,subprocess,sys,configparser,datetime,math,pathlib,PyQt5.QtGui,PyQt5.QtWidgets

JOYSTICKPATH='/dev/input/js0'
MINUTE=60
HOUR=60*MINUTE
INCREMENT=3*HOUR
PERSIST=MINUTE
PERIODS={
  0:'Night',
  3:'Late night',
  6:'Morning',
  9:'Late morning',
  12:'Afternoon',
  15:'Late afternoon',
  18:'Evening',
  21:'Late evening',
}
CONFIG=configparser.ConfigParser()
INI=pathlib.Path.home()/'.pyrsi.ini'
JOYSTICK=os.open(JOYSTICKPATH,os.O_RDONLY|os.O_NONBLOCK) if os.path.exists(JOYSTICKPATH) else False

class Frame(PyQt5.QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('RSI')  
    l=PyQt5.QtWidgets.QVBoxLayout();
    self.pool=PyQt5.QtWidgets.QLabel(describe())
    l.addWidget(self.pool)
    self.create(f"Rest more",l,lambda:self.rest(+INCREMENT))
    self.create(f"Rest less",l,lambda:self.rest(-INCREMENT))
    self.create("Hide",l,self.hide)
    self.setLayout(l)
    
  def rest(self,amount):
    global pool
    pool+=amount
    if pool<0:
      pool=0
      
  def create(self,label,layout,action):
    b=PyQt5.QtWidgets.QPushButton(label)
    layout.addWidget(b)
    b.clicked.connect(action)
    return b
    
  def closeEvent(self, event):
    prompt='Are you sure you want to disable PyRsi?'
    y=PyQt5.QtWidgets.QMessageBox.Yes
    if PyQt5.QtWidgets.QMessageBox.question(self,'Exit',prompt,y,PyQt5.QtWidgets.QMessageBox.No)!=y:
      event.ignore()
      return
    global terminate
    popupthread.cancel()
    terminate=True
    event.accept()
    app.quit()
      
  def activate(self):
    self.show()
    self.center()
    
  def center(self):
    frameGm=self.frameGeometry()
    d=PyQt5.QtWidgets.QApplication.desktop()
    screen=d.screenNumber(d.cursor().pos())
    c=d.screenGeometry(screen).center()
    frameGm.moveCenter(c)
    self.move(frameGm.topLeft())

lastjoystick=time.time()
joystickthread=False
app=PyQt5.QtWidgets.QApplication(sys.argv)
window=False
pool=0
popupthread=False
terminate=False
lastupdate=False
lastsave=False
tray=False
lastpopup=False

def watchjoystick():
  global lastjoystick
  while True:
    if terminate:
      return
    try:
      os.read(JOYSTICK,8)
      lastjoystick=time.time()
    except:#no new data to read
      time.sleep(1)

def update():
  if terminate:
    return
  global pool,lastupdate,lastsave
  now=time.time()
  if lastupdate!=False and now-lastupdate>=10:#resume from INI
    pool-=now-lastupdate
  lastupdate=now
  idle=True
  if now-lastjoystick<=1:
    idle=False
  else:
    idle=int(subprocess.Popen('xprintidle', stdout=subprocess.PIPE).stdout.read()[:-1])>1000
  pool+=-1 if idle else +1
  if pool<0:
    pool=0
  text=describe()
  window.pool.setText(text)
  tray.setToolTip(text)
  if lastsave==False:
    lastsave=now
  elif now>=lastsave+PERSIST:
    lastsave=now
    persist()
  threading.Timer(1,update).start()

def toperiod(datetime):
  return PERIODS[3*math.floor(datetime.hour/3)]

def describe():
  now=datetime.datetime.now()
  until=now+datetime.timedelta(seconds=pool)
  now=toperiod(now)
  until=toperiod(until)
  return 'All rested up!' if now==until else f'Rest until {until.lower()}.'

def popup():
  if terminate:
    return
  global lastpopup,popupthread
  d=describe()
  print(d)
  if d!=lastpopup:
    lastpopup=d
    tray.showMessage('PyRsi',d,msecs=5*1000)
  popupthread=threading.Timer(HOUR,popup)
  popupthread.start()
  
def restore():
  CONFIG.read(INI)
  if 'data' in CONFIG:
    data=CONFIG['data']
    global pool,lastupdate
    pool=float(data['pool'])
    lastupdate=float(data['lastupdate'])
    
def persist():
  CONFIG['data']={
    'pool':str(pool),
    'lastupdate':str(lastupdate)
  }
  CONFIG.write(open(INI,'w'))
  
def minimize():
  global tray
  tray=PyQt5.QtWidgets.QSystemTrayIcon(window)
  tray.setIcon(PyQt5.QtGui.QIcon(os.path.join(sys.path[0],'clock.png')))
  tray.setVisible(True)
  tray.activated.connect(window.activate)

if JOYSTICK!=False:
  joystickthread=threading.Thread(target=watchjoystick)
  joystickthread.start()
restore()
window=Frame()
minimize()
popup()
threading.Timer(1,update).start()
sys.exit(app.exec_())
