#!/usr/bin/python3
import os,pathlib,datetime

DIR=pathlib.Path(__file__).parent
TARGET=f'{DIR}/rsi.py'
LOG=f'{DIR}/log.txt'

os.remove(LOG)
print(f'Logging to {LOG}.')
error=True
while error:
  print(f'Launching {TARGET},...',file=open(LOG,'a'))
  error=os.system(f'python3 {TARGET} >> {LOG}')!=0
