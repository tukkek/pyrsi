PyRsi is a unique RSI prevention tool. Instead of working with short and long rest intervals as most applications do, it simply keeps track of the time you've been using the computer since it was turned on and will periodically notify you that you should rest for that given time as well. It will then decrease the counter based on how much time you've spent away from your computer (or at least not interacting with it). PyRSI takes into account gamepad activity and the device being turned off or suspended.

It also offers 2:1. 1:1 and 1:2 options on startup if you want to be more lax or strict with your rest periods. This is meant to be used on the beginning of a work day (or work session) if your hands, wrists or arms are already feeling tired or if you have a lot of work to do and is willing to compromise having less time to rest.

While it should be easy to port over, PyRSI doesn't currently support Windows. Read the relevant section for a quick hack I put together for Windows users.

# Requirements

* Python 3 https://www.python.org/downloads/
* xprintidle
* python3-pyqt5

# Autostart

To have PyRsi run on login, consult your system's documentation. On Unix, it'll look like this:

1. Login command: `nice /path/to/launcher.py`
2. Logout command: `killall rsi.py`

Also make sure the scripts are executable with `chmod +x launcher.py rsi.py`.

# Windows script

The `winrsi.py` script contained in this repository is a very simple, stand-alone RSI tool that I cooked up in fifteen minutes pending fully suporting Windows on the main program. It runs on a console window so you can either setup a shortcut for it (something like `cmd /C python C:\path\to\winrsi.py`) or run it manually from the terminal (`python C:\path\to\winrsi.py`).

Usage: `python winrsi.py [minutes to rest]`.

## Requirements

* Python 3 https://www.python.org/downloads/
* pywin32 (`pip install pywin32`)

# Other RSI prevention tools

* RSIBreak (for Linux) - easy to find and install via your distribution's package manager
* Workrave (mainly for Windows) - http://www.workrave.org/download/
