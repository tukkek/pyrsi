import win32api,time,sys

MINUTE=60
HOUR=MINUTE*60

rest=0 if len(sys.argv)<2 else int(sys.argv[1])*60
last=False

def tick():
  global rest
  idle=(win32api.GetTickCount()-win32api.GetLastInputInfo())/1000
  rest+=1 if idle<1 else -1
  if rest<0:
    rest=0

def convert():
  if rest>=HOUR:
    return rest/HOUR,'hour'
  if rest>=MINUTE:
    return rest/MINUTE,'minute'
  return rest,'second'

def notify():
  global last
  units,unit=convert()
  units=round(units)
  if units!=1:
    unit+='s'
  output=f'{units} {unit}'
  if output!=last:
    print(output)
    last=output

while True:
  tick()
  notify()
  time.sleep(1)
