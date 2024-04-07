import os
from list_all_files_recursively_short import get_short_path_name
import sys
import subprocess
from time import sleep
from ctrlchandler import set_console_ctrl_handler
import keyboard
import os

config = sys.modules[__name__]
config.restart_proc = True


def _switch_restart_proc():
    """
    Toggle the value of config.restart_proc and print the updated status.
    """
    config.restart_proc = not config.restart_proc
    print(f"restart: {config.restart_proc}")


def disable_restart_proc(disable_shortcut):
    """
    Function to disable the restart process with a specified shortcut.

    :param disable_shortcut: str - The shortcut used to disable the restart process.
    :return: None
    """
    keyboard.add_hotkey(disable_shortcut, _switch_restart_proc)


def newstartwhenctrlc(*args, **kwargs):
    """
    A function to handle the behavior when Ctrl+C is pressed. It checks if a process needs to be restarted, then generates a batch file for the restart process with necessary environment variables and commands. Finally, it starts the batch file in a new subprocess and exits the current process.
    """
    if not config.restart_proc:
        os._exit(1)
    sleep(1)
    cwd = os.getcwd()
    __tmlres = os.environ.get("script_tmpbat", kwargs.get("tmpbat", "__tmlres.bat"))
    sleeptime = int(os.environ.get("script_sleeptime", kwargs.get("sleeptime", 30)))
    short_path = get_short_path_name(cwd)
    sleep_before_restart = int(
        os.environ.get(
            "script_sleep_before_restart", kwargs.get("sleep_before_restart", 5)
        )
    )
    pythonexe = os.environ.get(
        "script_pythonexe", kwargs.get("pythonexe", sys.executable)
    )
    pythonexe = get_short_path_name(pythonexe)
    sleep_after_exit = int(
        os.environ.get("script_sleep_before_restart", kwargs.get("sleep_after_exit", 5))
    )
    batch_file_path = os.path.join(os.getcwd(), __tmlres)
    this_by_script = get_short_path_name(__file__)
    with open(batch_file_path, "w", encoding="utf-8") as batch_file:
        batch_file.write(
            rf"""
@echo off

set "pid={os.getpid()}"

:loop
rem Check if the process exists
tasklist /FI "PID eq %pid%" | find "%pid%" > nul

rem If the process exists, wait for a while and check again
if errorlevel 1 (
    echo Process with PID %pid% has disappeared.
    goto endloop
) else (
    echo Process with PID %pid% is still running.
    rem Adjust the timeout value (in seconds) as needed
    timeout /t {sleep_before_restart} /nobreak > nul
    goto loop
)

:endloop
echo Exiting loop.

"""
        )
        batch_file.write(f"call cd {short_path}\n")
        batch_file.write(f"call cd {short_path}\ncall sleep {sleeptime}\n")
        os.environ["script_tmpbat"] = __tmlres
        os.environ["script_sleeptime"] = str(sleeptime)
        os.environ["script_sleep_before_restart"] = str(sleep_before_restart)
        os.environ["script_pythonexe"] = pythonexe
        os.environ["script_sleep_before_restart"] = str(sleep_after_exit)
        env_dict = os.environ.copy()

        for key, value in env_dict.items():
            batch_file.write(f"call set {key}={value}\n")
        batch_file.write(f"call {pythonexe} " + " ".join(sys.argv))
    print("Batch file generated successfully!")
    short_path = get_short_path_name(batch_file_path)
    wholecommand = f'start /min "" "{batch_file_path}" {this_by_script}'
    invisibledict = {}
    p = subprocess.Popen(
        wholecommand, cwd=cwd, env=env_dict, shell=True, **invisibledict
    )
    sleep(sleep_after_exit)
    os._exit(0)
