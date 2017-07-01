import matplotlib.pyplot as plt # type: ignore

from kython import *


def parse_timestamp(ts: str) -> Optional[datetime]: # TODO return??
    try:
        return parse_date(ts)
    except Exception as e:
        # TODO proper exception!
        return None
    # TODO do more handling!


def plot_timestamped(timestamps, values, marker='o'):
    tss = lmap(parse_timestamp, timestamps)
    fig = plt.figure()
    axes = fig.add_subplot(1,1,1)
    axes.plot(tss, values, marker=marker)
    return fig
