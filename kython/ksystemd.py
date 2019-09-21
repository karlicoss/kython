#!/usr/bin/env python3
import argparse

from pathlib import Path
import sys
from subprocess import check_call, run

SYSTEMD_CONFIG = """
[Unit]
Description={description}

[Install]
WantedBy=default.target

[Service]
ExecStart={exec_start}
Type=simple
Restart=always
RestartSec=10
"""


def systemd(*args, method=check_call):
    method([
        'systemctl', '--user', *args,
    ])

def setup(*, unit_name: str, exec_start: str, description: str=""):
    config = SYSTEMD_CONFIG.format(exec_start=exec_start, description=description)

    out = Path(f'~/.config/systemd/user/{unit_name}').expanduser()
    print(f"Writing systemd config to {out}", file=sys.stderr)

    out.write_text(config)

    try:
        systemd('stop' , unit_name, method=run) # ignore errors here if it wasn't running in the first place
        systemd('daemon-reload')
        systemd('enable', unit_name)
        systemd('start' , unit_name)
        systemd('status', unit_name)
    except Exception as e:
        print(f"Something has gone wrong... you might want to use 'journalctl --user -u {unit_name}' to debug", file=sys.stderr)
        raise e
