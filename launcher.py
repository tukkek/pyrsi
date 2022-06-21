#!/usr/bin/python3
import os,pathlib,datetime

DIR=pathlib.Path(__file__).parent
TARGET=f'{DIR}/rsi.py'
LOG=f'{DIR}/log.txt'
EXIT=[
  0,#success
  36608,#sigterm
  35072,#sigkill
]

os.remove(LOG)
print(f'Logging to {LOG}.')
status=1
while status not in EXIT:
  print(f'Launching {TARGET},...',file=open(LOG,'a'))
  status=os.system(f'{TARGET} >> {LOG}')
  print(f'Exit code: {status}.',file=open(LOG,'a'))
