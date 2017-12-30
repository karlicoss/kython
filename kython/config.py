def trigger_run(cmd: str):
    """
       trigger program run, for instance, to create config
    """
    import subprocess
    import time
    p = subprocess.Popen(cmd, shell=True)
    time.sleep(2)
    p.kill()
    time.sleep(1) # wait till it dies
