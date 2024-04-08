import string as _str
import random as _ran
import psutil as _ps
import platform as _pf
import hashlib as _h
import sys as _sys
import os as _os
import uuid as _uuid
import time as _t
from . import jsons as _json

def get_mac_address():
    mac=_uuid.UUID(int = _uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
   
   
def getInfo():
    pythontype = _pf.python_implementation()
    ver = _pf.python_version()
    osver = _pf.release()
    systemtype = _pf.machine()
    osname = _pf.system()
    
    processes = []
    for pid in _ps.pids():
        process = _ps.Process(pid)
        process_info = {
            'PID':pid,
            'Name':process.name(),
            'CWD':process.cwd(),
            'FilePath':process.exe(),
            'Running':process.is_running(),
            'FDS':process.num_fds(),
            'Threads':process.num_threads(),
            'CmdLine':process.cmdline(),
            
        }
        processes.append(process_info)
         
    ua = {
        'Python':{
            'Version':ver,
            'Interpreter':pythontype,
            'BuildDate':_pf.python_build()[1],
            'BuildCompiler':_pf.python_compiler(),
            'BuildNo':_pf.python_build()[0],
            'SCM':_pf.python_branch(),
            'InterpreterConfig': {
                'PyCachePath':_sys.pycache_prefix,
                'RecursionLimit':_sys.getrecursionlimit(),
                'MaxSize':str(_sys.maxsize),
                'MaxUnicode':_sys.maxunicode,
                'Prefix':_sys.prefix,
                'C_API_Version':_sys.api_version,
                'ModulePath':_sys.path
            }
        },
        'OS':{
            'Name':osname,
            'Time':_t.time(),
            'NodeName':_pf.node(),
            'Version':osver,
            'Machine':systemtype,
            'Bit':_pf.architecture()[0],
            'Agrv':_sys.argv,
            'ENV':dict(_os.environ),
            'BootTime':_ps.users(),
            'Hardware':{
                'CPU':{
                    'Count':_ps.cpu_count(logical=False),
                    'CoreCount':_ps.cpu_count(),
                    'Frequency':_ps.cpu_freq(),
                    'Name':_pf.processor()
                },
                'Memory':{
                    'Total': _ps.virtual_memory()[0] / 1024  / 1024 ,
                    'SWAP':_ps.swap_memory()[0] / 1024 / 1024
                }
            },
            'Network':{
                'MAC':get_mac_address()
            },
            'MoYanDeviceID':getDeviceID(),
            'UUID_DeviceID':_uuid.getnode(),
            'Process':processes
            
        }
    }
    return ua
    
def genVerifiCode(wei: int = 4):
    """_summary_

    Keyword Arguments:
        wei -- 位数 (default: {4})

    Returns:
        生成的验证码
    """
    # 生成所有可能出现在验证码中的字符
    characters = _str.ascii_letters + _str.digits

    # 生成8位随机验证码
    verification_code = "".join(_ran.choice(characters) for _ in range(wei))

    return verification_code


def getDeviceID():
    # 获取设备ID
    system_name = _pf.platform()
    computer_name = _pf.node()
    computer_system = _pf.system()
    computer_bit = _pf.architecture()[0]
    cpu_count = _ps.cpu_count()
    mem = _ps.virtual_memory()
    mem_total = format(float(mem.total) / 1024 / 1024 / 1024)
    deviceid = (
        system_name
        + "_"
        + computer_name
        + "_"
        + computer_system
        + "_"
        + computer_bit
        + "_"
        + str(cpu_count)
        + "_"
        + mem_total
    )
    # 对id进行sha1
    hash_id = _h.sha1(deviceid.encode("utf-16be")).hexdigest()
    big_hash_id = str(hash_id).upper()
    return big_hash_id
