import subprocess
import os.path as op
from time import time, sleep
from datetime import datetime
from typing import Iterable, List, Union, Any
from .utils import MessageIntent, cprint
import sys
import traceback
# import signal 
# from subprocess import signal, Popen

# PREKILL_SLEEPING_TIME_SEC = 1

# class RuntimeManager:
#     stopped = False
#     current_subprocess: Popen = None

#     def __init__(self) -> None:
#         pass

#     def stop(self):
#         if self.current_subprocess:
#             print("runtimemanager: terminate not working")
#             # self.current_subprocess.send_signal(signal.SIGINT)
#             # # # Try to stop
#             # self.current_subprocess.terminate()
#             # self.current_subprocess.communicate()
#             # # # Wait to see if the process can be terminated
#             # # sleep(PREKILL_SLEEPING_TIME_SEC)
            
#             # # # If the process is still alive, kill it
#             # # print("runtimemanager: kill?")
#             # # if self.current_subprocess.poll() is None:
#             # #     print("runtimemanager: yes, kill")
#             # sleep(1)
#             # print("killing", self.current_subprocess.pid)
#             # self.current_subprocess.kill()
#             # self.current_subprocess.send_signal(signal.SIGTERM)
#             # # self.current_subprocess.join()
#         self.stopped = True
#         sys.exit()

#     def __setattr__(self, __name: str, __value: Any) -> None:
#         if __name == "current_subprocess":
#             print("Updating current subprocess to:", __value)
#             print(__value)
#         return super().__setattr__(__name, __value)


def write_log(log_f, *text: Union[str, List[str]]):
    """ Append text to the log text file. """
    # text = [text] if isinstance(text, str) else text
    with open(log_f, 'a+') as fp:
        fp.writelines(text)

def get_versions():
    return {
        "python": f"{sys.version[0]}.{sys.version[1]}"
    }


def versions_2_txt(versions:dict=None):
    txt = "### Versions:\n"
    if versions is not None:
        for k, v in versions.items():
            txt += f"{k}: {v}\n"
    txt += "#############\n"
    return txt
    

def run_cmd(cmd, title=None, log=None, versions:dict=None, raise_errors=True):
    """ Run a command in a sub process """
    splitted_cmd = cmd #cmd.split(' ')

    if title:
        cprint(f"Start {title}", intent=MessageIntent.INFO)
    cprint(cmd)
    tic = time()
    try:
        if log:
            write_log(log, 
                "\n",
                "#" * 80,
                f"\n####### {title} ######\n",
                versions_2_txt(versions),
                cmd,
                f"\n##########\nStarted at: {datetime.isoformat(datetime.now())}"
            )
            tic = time()
            output = _run_cmd(splitted_cmd)
            toc = time()
            write_log(log,
                output.decode("utf-8"),
                f"\nFinshed at: {datetime.isoformat(datetime.now())} - tooks {toc-tic:.03f}s",
                "\n#####\n\n\n"
            )
        else:
            _run_cmd(splitted_cmd)
    except Exception as e:
        tb = traceback.format_exc()
        cprint(f"An error occured while running: {cmd}", intent=MessageIntent.ERROR)
        if log:
            write_log(log,
                f"Errored at {datetime.isoformat(datetime.now())}:\n",
                str(e), "\n#####\n\n\n"
            )
        if raise_errors:
            raise e
        else:
            cprint(str(e), intent=MessageIntent.ERROR)
            cprint(tb, intent=MessageIntent.ERROR)
            return -1
    if log:
        cprint(f'Console outputs saved to:', log, intent=MessageIntent.INFO)
    if title:
        cprint(f"{title} tooks {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    else:
        cprint(f"done in {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    return 0

def _run_cmd(splitted_cmd):
    # output = subprocess.check_output(splitted_cmd, stderr=subprocess.STDOUT, shell=True)
    process = subprocess.Popen(splitted_cmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)# stderr=subprocess.STDOUT, shell=True)
    # if runtime_manager:
    #     if runtime_manager.stopped:
    #         sys.exit()
    #     runtime_manager.current_subprocess = process
    # else:
    #     print("not using runtime manager")
    process.wait()
    output = process.stdout.read()
    # if runtime_manager:
    #     runtime_manager.current_subprocess = None
    return output

def cached_run(cmd, out_files:List[str]=None, title=None, log=None, 
               versions:dict=None, raise_errors=True, verbose=False):
    """ Run the command only if one of the out_files is missing """
    if isinstance(out_files, str):
        out_files = [out_files]

    do_run = False
    if out_files is not None:
        for f in out_files:
            if not op.isfile(f) and not op.isdir(f):
                do_run = True
                break
    
    if do_run:
        return run_cmd(cmd, title, log, versions, raise_errors)
    if verbose:
        cprint('Using cached files for', title if title else cmd, intent=MessageIntent.WARNING)


def _run_func(func, args):
    if args is None:
        func()
    elif isinstance(args, dict):
        func(**args)
    elif isinstance(args, Iterable):
        func(*args)
    else:
        raise ValueError("arguments hould be either None, a list or a dict.")
 

def run_func(func, args, title=None, log=None, versions:dict=None, raise_errors=True):
    """ Run a command in a sub process """
    if title:
        cprint(f"Start {title}", intent=MessageIntent.INFO)
    cprint(func.__name__)
    cprint('args:\n')
    for arg in args:
        cprint('\t', arg)

    tic = time()
    try:
        if log:
            write_log(log, 
                "\n",
                "#" * 80,
                f"\n####### {title} ######\n",
                versions_2_txt(versions),
                func.__name__ if hasattr(func, '__name__') else func,
                f"\n##########\nStarted at: {datetime.isoformat(datetime.now())}"
            )
            tic = time()
            _run_func(func, args)
            toc = time()
            write_log(log,
                f"\nFinshed at: {datetime.isoformat(datetime.now())} - tooks {toc-tic:.03f}s",
                "\n#####\n\n\n"
            )
        else:
            _run_func(func, args)
    except Exception as e:
        tb = traceback.format_exc()
        cprint(f"An error occured while running: {func.__name__}", intent=MessageIntent.ERROR)
        cprint(str(e), intent=MessageIntent.ERROR)
        if log:
            write_log(log,
                f"Errored at {datetime.isoformat(datetime.now())}:\n",
                str(e), "\n#####\n\n\n"
            )
        if raise_errors:
            raise e
        else:
            cprint(str(e), intent=MessageIntent.ERROR)
            cprint(tb, intent=MessageIntent.ERROR)
            return -1
    if log:
        cprint(f'Console outputs saved to:', log, intent=MessageIntent.INFO)
    if title:
        cprint(f"{title} tooks {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    else:
        cprint(f"done in {time()-tic:.02f}s", intent=MessageIntent.SUCCESS)
    return 0


def cached_function_call(func, args, out_files:List[str]=None, title=None, log=None, 
                         versions:dict=None, raise_errors=True, verbose=False):
    """ Run python function only if one of the out_files is missing """
    if isinstance(out_files, str):
        out_files = [out_files]

    do_run = False
    if  out_files is not None:
        for f in out_files:
            if not op.isfile(f) and not op.isdir(f):
                do_run = True
                break
    
    if do_run:
        return run_func(func, args, title, log, versions, raise_errors)
    if verbose:
        cprint('Using cached files for', title if title else func.__name__, intent=MessageIntent.WARNING)


