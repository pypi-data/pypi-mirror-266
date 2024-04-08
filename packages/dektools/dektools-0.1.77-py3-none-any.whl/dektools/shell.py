import os
import sys
import json
import shutil
import functools
import subprocess
from .file import write_file
from .yaml import yaml


def shell_wrapper(command, check=True, chdir=None):
    dir_last = None
    if chdir:
        dir_last = os.getcwd()
        os.chdir(chdir)
    err = os.system(command)
    if check and err:
        if dir_last:
            os.chdir(dir_last)
        raise ChildProcessError(command)
    if dir_last:
        os.chdir(dir_last)
    return err


def shell_output(command, error=True):
    return shell_result(command, error)[1]


def shell_exitcode(command, error=True):
    return shell_result(command, error)[0]


def shell_result(command, error=True):
    return getstatusoutput(command, error)


def getstatusoutput(cmd, error=True):
    try:
        data = subprocess.check_output(
            cmd, shell=True, text=True,
            stderr=subprocess.STDOUT if error else subprocess.DEVNULL)
        exitcode = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        exitcode = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return exitcode, data


def shell_with_input(command, inputs):
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    if isinstance(inputs, str):
        inputs = inputs.encode('utf-8')
    outs, errs = p.communicate(input=inputs)
    return p.returncode, outs, errs


def shell_stdout(command, write=None, env=None):
    proc = subprocess.Popen(command,
                            env=env,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True
                            )
    write = write or sys.stdout.write
    while proc.poll() is None:
        stdout = proc.stdout.readline()
        write(stdout)


def shell_tee(command, env=None):
    def write(s):
        nonlocal result
        result += s
        sys.stdout.write(s)

    result = ''
    shell_stdout(command, write=write, env=env)
    return result


def shell_command(command, sync=True, headless=False, quiet=False, ignore=False, env=None):
    result = None
    if os.name == 'nt' and headless:
        result = shell_command_nt_headless(command, sync)
    else:
        if not sync:
            command = _cmd_to_async(command)
        if quiet:
            shell_output(command)
        else:
            try:
                subprocess.run(command, check=True, shell=True, env=env)
            except subprocess.CalledProcessError as e:
                result = ChildProcessError((command, e))
    return None if ignore else result


def _cmd_to_async(command):
    if os.name == 'nt':
        command = 'start ' + command
    else:
        command = 'nohup ' + command + ' &'
    return command


def shell_command_nt_headless(command, sync=True, env=None):
    executor = 'wscript'
    if not env:
        env = os.environ.copy()
    if env.get('DEKSHELL_VBS_ENV') == 'true':  # As vbs call deep bug
        if sync:
            return shell_command(command, sync, headless=False, env=env)
        else:
            executor = 'start ' + executor
    env['DEKSHELL_VBS_ENV'] = "true"

    command = command.replace('"', '""')
    vbs = f"""
Dim Wsh
Set Wsh = WScript.CreateObject("WScript.Shell")
Wsh.Run "{command}",0,{'true' if sync else 'false'}
Set Wsh=NoThing
WScript.quit
    """
    fp = write_file('run.vbs', s=vbs, t=True)
    try:
        subprocess.run(f'{executor} {fp}', check=True, shell=True, env=env)
    except subprocess.CalledProcessError as e:
        return e
    return None


def show_win_msg(msg=None, title=None):
    if os.name == 'nt':
        import ctypes
        mb = ctypes.windll.user32.MessageBoxW
        mb(None, msg or 'Message', title or 'Title', 0)


class Cli:
    def __init__(self, *args):
        self.list = args

    @property
    @functools.lru_cache(None)
    def cur(self):
        s = set()
        for cli in self.list:
            if cli not in s and shutil.which(cli):
                return cli
            s.add(cli)


def output_data(data, out=None, fmt=None, prefix=None):
    if prefix:
        data = {f"{prefix}{k}": v for k, v in data.items()}
    fmt = fmt or 'env'
    if fmt == 'env':
        s = "\n".join(f'{k}="{v}"' for k, v in data.items())
    elif fmt == 'json':
        s = json.dumps(data)
    elif fmt == 'yaml':
        s = yaml.dumps(data)
    else:
        raise TypeError(f'Please provide a correct format: {fmt}')
    if out:
        write_file(out, s=s)
    else:
        out = write_file(f'.{fmt}', s=s, t=True)
        sys.stdout.write(out)
