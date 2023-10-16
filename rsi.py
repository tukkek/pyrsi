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
    global exit
    popup.thread.cancel()
    exit=True
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

class Popup:
  def __init__(self):
    self.thread=False
    self.last=False
  
  def popup(self):
    if exit:
      return
    d=describe()
    print(d)
    if d!=self.last:
      lastpopup=d
      tray.icon.showMessage('PyRsi',d,msecs=5*1000)
    self.thread=threading.Timer(HOUR,self.popup)
    self.thread.start()

class Db:
  def __init__(self):
    self.parser=configparser.ConfigParser()
    self.path=pathlib.Path.home()/'.pyrsi.ini'
    self.lastsave=False

  def load(self):
    self.parser.read(self.path)
    if 'data' not in self.parser:
      return
    data=self.parser['data']
    global pool,lastupdate
    pool=float(data['pool'])
    lastupdate=float(data['lastupdate'])
      
  def save(self,now):
    if self.lastsave==False:
      self.lastsave=now
      return
    if now<self.lastsave+SAVE:
      return
    print(self.lastsave)
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
    while not exit:
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
window=False
pool=0
exit=False
lastupdate=False
popup=Popup()
db=Db()
gamepad=Gamepad()
tray=False

def update():
  if exit:
    return
  global pool,lastupdate,lastsave
  now=time.time()
  if lastupdate!=False and now-lastupdate>=10:#resume from INI
    pool-=now-lastupdate
  lastupdate=now
  idle=True
  if now-gamepad.lastupdate<=1:
    idle=False
  else:
    idle=int(subprocess.Popen('xprintidle', stdout=subprocess.PIPE).stdout.read()[:-1])>1000
  pool+=-1 if idle else +1
  if pool<0:
    pool=0
  text=describe()
  window.pool.setText(text)
  tray.icon.setToolTip(text)
  db.save(now)
  threading.Timer(1,update).start()

def toperiod(datetime):
  return PERIODS[3*math.floor(datetime.hour/3)]

def describe():
  now=datetime.datetime.now()
  until=now+datetime.timedelta(seconds=pool)
  now=toperiod(now)
  until=toperiod(until)
  return 'All rested up!' if now==until else f'Rest until {until.lower()}.'

if __name__=='__main__':
  db.load()
  window=Frame()
  threading.Timer(1,update).start()
  tray=Tray()
  popup.popup()
  sys.exit(app.exec_())
