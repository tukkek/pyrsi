#!/usr/bin/python3
import time,threading,os,subprocess,sys,configparser,datetime,math,pathlib,PyQt5.QtGui,PyQt5.QtWidgets

MINUTE=60
HOUR=60*MINUTE
INCREMENT=3*HOUR
SAVE=MINUTE
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

class Window(PyQt5.QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.exit=False
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
    
  def closeEvent(self,event):
    prompt='Are you sure you want to exit?'
    y=PyQt5.QtWidgets.QMessageBox.Yes
    if PyQt5.QtWidgets.QMessageBox.question(self,'Exit',prompt,y,PyQt5.QtWidgets.QMessageBox.No)!=y:
      event.ignore()
      return
    popup.thread.cancel()
    self.exit=True
    event.accept()
    app.quit()
      
  def activate(self):
    self.show()
    self.center()
    
  def center(self):
    g=self.frameGeometry()
    d=PyQt5.QtWidgets.QApplication.desktop()
    s=d.screenNumber(d.cursor().pos())
    c=d.screenGeometry(s).center()
    g.moveCenter(c)
    self.move(g.topLeft())

class Popup:
  def __init__(self):
    self.thread=False
    self.last=False
  
  def popup(self):
    if window.exit:
      return
    d=describe()
    print(d)
    if d!=self.last:
      lastpopup=d
      tray.icon.showMessage('PyRsi',d,msecs=3*1000)
    self.thread=threading.Timer(HOUR,self.popup)
    self.thread.start()

class Db:
  def __init__(self):
    self.parser=configparser.ConfigParser()
    self.path=pathlib.Path.home()/'.pyrsi.ini'
    self.lastsave=time.time()

  def load(self):
    self.parser.read(self.path)
    if 'data' not in self.parser:
      return
    global pool,lastupdate
    d=self.parser['data']
    pool=float(d['pool'])
    lastupdate=float(d['lastupdate'])
      
  def save(self):
    now=time.time()
    if now<self.lastsave+SAVE:
      return
    self.lastsave=now
    self.parser['data']={
      'pool':str(pool),
      'lastupdate':str(lastupdate)
    }
    with open(self.path,'w') as ini:
      self.parser.write(ini)

class Gamepad:#TODO test with gamepad plugged after refactoring into class
  def __init__(self):
    self.path='/dev/input/js0'
    self.device=os.path.exists(self.path) and os.open(self.path,os.O_RDONLY|os.O_NONBLOCK)
    self.lastupdate=time.time()
    if self.device:
      t=threading.Thread(target=self.listen)
      t.start()

  def listen():
    while not window.exit:
      try:
        os.read(device,8)
        self.lastupdate=time.time()
      except:#no new data
        time.sleep(1)
        
class Tray:
  def __init__(self):
    i=PyQt5.QtWidgets.QSystemTrayIcon(window)
    self.icon=i
    i.setIcon(PyQt5.QtGui.QIcon(os.path.join(sys.path[0],'clock.png')))
    i.setVisible(True)
    i.activated.connect(window.activate)

app=PyQt5.QtWidgets.QApplication(sys.argv)
lastupdate=False
gamepad=False
window=False
popup=False
tray=False
db=False
pool=0

def run(command):
  return subprocess.Popen(command,stdout=subprocess.PIPE).stdout.read()

def update():
  if window.exit:
    return
  global pool,lastupdate
  now=time.time()
  if lastupdate and now-lastupdate>MINUTE:#account for shutdown, hibernate...
    pool-=now-lastupdate
  lastupdate=now
  idle=now-gamepad.lastupdate>1 and int(run('xprintidle')[:-1])>1000
  pool+=-1 if idle else +1
  if pool<0:
    pool=0
  d=describe()
  window.pool.setText(d)
  tray.icon.setToolTip(d)
  db.save()
  threading.Timer(1,update).start()

def toperiod(datetime):
  return PERIODS[3*math.floor(datetime.hour/3)]

def describe():
  n=datetime.datetime.now()
  p=toperiod(n+datetime.timedelta(seconds=pool))
  return 'All rested up!' if toperiod(n)==p else f'Rest until {p.lower()}.'

db=Db()
db.load()
window=Window()
gamepad=Gamepad()
tray=Tray()
popup=Popup()
threading.Timer(1,update).start()
popup.popup()
sys.exit(app.exec_())
