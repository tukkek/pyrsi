PyRsi is a unique RSI prevention tool. Instead of working with short and long rest intervals as most applications do, it simply keeps track of the time you've been using the computer since it was turned on and will periodically notify you that you should rest for that given time as well. It will then decrease the counter based on how much time you've spent away from your computer (or at least not interacting with it).

It also offers 2:1. 1:1 and 1:2 options on startup if you want to be more lax or strict with your rest periods. This is meant to be used on the beginning of a work day (or work session) if your hands, wrists or arms are already feeling tired or if you have a lot of work to do and is willing to compromise having less time to rest, etc.

This is currently a Linux-only tool and takes into consideration gamepad activity and time ellapsed while the computer is suspended. It should be easy to port to other systems as long as you have Qt installed - if you do so or need help doing it let me know and I'll happily add your changes to the main project for the benefit of others.

What packages you're going to need to have installed for this to work properly:

* Python 3 https://www.python.org/downloads/
* xprintidle
* python3-pyqt5
* python3-appdirs (optional: for using an external configuration file)
* python3-watchdog (optional: if installed, will watch said external configuration file for changes)

The optional external configuration file is located at `/home/USER/.config/pyrsi/whitelist.cfg` on Linux. Check the comments there (or in the template `whitelist-template.cfg`) for instructions on how to use it. For other platforms, the location will be shown when launching from console (or check [the appdirs module's documentation](https://github.com/ActiveState/appdirs/blob/master/README.rst)). 

This package doesn't have an installer so if you want it to start automatically when you log into your computer you'll have to set it up yourself. It should be pretty simple though, just make sure the script is executable (`chmod +x rsi.py` on Linux) and configure it to be called on system startup - how to go about doing it varies from system to system but all of them have an Autostart option which should be easy to set up (on KDE, for example just go to System Settings -> Startup and Shutdown -> Autostart). For other systems just do a quick search on Google or ask for help on your system's website, forum, mailing list or similar.

Other suggested RSI prevention tools, much more professional than PyRsi:

* RSIBreak (for Linux) - easy to find and install via your distribution's package manager
* Workrave (mainly for Windows) - http://www.workrave.org/download/

# Windows script

The `winrsi.py` script contained in this repository is a very simple, stand-alone RSI tool that I cooked up in fifteen minutes pending fully suporting Windows on the main program. It runs on a console window so you can either setup a shortcut for it (something like `cmd /C python C:\path\to\winrsi.py`) or run it manually from the terminal (`python C:\path\to\winrsi.py`).

Usage: `python winrsi.py [minutes to rest]`.

Requirements:

* Python 3 https://www.python.org/downloads/
* pywin32 (`pip install pywin32`)
