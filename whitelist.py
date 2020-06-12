import os,sys

FILENAME='whitelist.cfg'
silent=False
configdir=False
whitelist=False

def update():
  silent.clear()
  with open(whitelist,'r') as f:
    for line in f.readlines():
      line=line[:-1]
      if len(line)>0 and line[0]!='#':
        silent.append(line)
          
def setup(silentprocesses):
  global silent,configdir,whitelist
  silent=silentprocesses
  try:
    import appdirs,shutil
    configdir=appdirs.AppDirs("pyrsi","tukkek").user_config_dir
    os.makedirs(configdir,exist_ok=True)
    whitelist=os.path.join(configdir,FILENAME)
    print(f'Reading external configuration: {whitelist}...')
    if not os.path.exists(whitelist):
      shutil.copyfile('whitelist-template.cfg',whitelist)
    update()
  except ModuleNotFoundError:
    print('appdirs module not found, ignoring external configuration...')
    return
  try:
    import watchdog,watchdog.observers,watchdog.events
    class Updater(watchdog.events.FileSystemEventHandler):
      def on_modified(self,event):
        if event.src_path==whitelist:
          update()
    o=watchdog.observers.Observer()
    o.schedule(Updater(),configdir)
    o.start()
  except ModuleNotFoundError:
    return
