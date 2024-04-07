# Restarts process (Windows only)

## Tested against Windows / Python 3.11 / Anaconda

### pip install restartprocwithvars

```py
from restartprocwithvars import (
    set_console_ctrl_handler,
    newstartwhenctrlc,
    disable_restart_proc,
)
from time import sleep
from functools import partial
import sys

disable_restart_proc(
    "ctrl+alt+w",
)
set_console_ctrl_handler(
    returncode=1,
    func=partial(
        newstartwhenctrlc,
        sleeptime=30,
        sleep_before_restart=5,
        sleep_after_exit=5,
        pythonexe=sys.executable,
    ),
)
while True:
    sleep(1)
    print("test")
sleep(10)


# def _switch_restart_proc():
#     """
#     Toggle the value of config.restart_proc and print the updated status.
#     """

# def disable_restart_proc(disable_shortcut):
#     """
#     Function to disable the restart process with a specified shortcut.

#     :param disable_shortcut: str - The shortcut used to disable the restart process.
#     :return: None
#     """

# def newstartwhenctrlc(*args, **kwargs):
#     """
#     A function to handle the behavior when Ctrl+C is pressed. It checks if a process needs to be restarted, then generates a batch file for the restart process with necessary environment variables and commands. Finally, it starts the batch file in a new subprocess and exits the current process.
#     """
```