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
