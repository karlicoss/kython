from typing import Any

def trigger_run(cmd: str):
    """
       trigger program run, for instance, to create config
    """
    import os
    import signal
    import subprocess
    import time
    p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setpgrp)
    time.sleep(2)
    os.killpg(os.getpgid(p.pid), signal.SIGTERM) # in case it forks
    time.sleep(1) # wait till it dies

def patch_py(path, property, new_value):
    cmd = "'s/^{} = .*/{} = {}/g'".format(property, property, new_value)
    print(cmd)
    import subprocess
    subprocess.check_call(' '.join(['sed', '-i', cmd, path]), shell=True)


def gsettings_encode(value: Any):
    if type(value) == list:
        encoded = [gsettings_encode(i) for i in value]
        return "[" + ', '.join(encoded) + "]"
    if type(value) == tuple:
        encoded = [gsettings_encode(i) for i in value]
        return "(" + ', '.join(encoded) + ")"
    elif type(value) == str:
        return "'{}'".format(value)
    elif type(value) == int:
        return f"{value}"
    elif type(value) == bool:
        return "true" if value else "false"
    else:
        raise RuntimeError("Unexpected type: {}".format(type(value)))

# TODO eh, that doesnt really work, what is more, read doesnt always work
 # dconf read -d /org/mate/power-manager/button-lid-ac
def get_default(key: str):
    from subprocess import check_output
    return check_output(['dconf', 'read', '-d', key]).decode('utf-8')

def set_dconf(key: str, value: Any, check_schema=True):
    # TODO ugh
    from subprocess import call, DEVNULL, check_call
    if "/" in key:
        sp = key.split('/')
        assert sp[0] == ''
        del sp[0]
        kname = sp[-1]
        gschema = '.'.join(sp[:-1])
    if check_schema:
        code = call(['gsettings', 'describe', gschema, kname], stdout=DEVNULL)
        if code != 0:
            raise RuntimeError(f"{gschema}:{kname} doesn't exist!")

    # TODO use gsettings set for that??
    command = ['dconf', 'write', key, gsettings_encode(value)]
    print(command)
    check_call(command)

def set_gsettings(schema: str, key: str, value: Any):
    from subprocess import check_call
    command = ['gsettings', 'set', schema, key, gsettings_encode(value)]
    print(command)
    check_call(command)
