import matplotlib.pyplot as plt # type: ignore

from kython import *


def parse_timestamp(ts: str) -> Optional[datetime]: # TODO return??
    d = parse_date(ts)
    return d
    # TODO do more handling!


def mavg(timestamps, values, window):
    # TODO make more efficient
    def avg(fr, to):
        res = [v for t, v in zip(timestamps, values) if fr <= t <= to]
        # TODO zero len
        return sum(res) / len(res)
    return [avg(ts - window, ts) for ts in timestamps]


def plot_timestamped(timestamps, values, ratio=None, marker='o', timezone=None):
    timestamps, values = lzip(*((t, v) for t, v in zip(timestamps, values) if v is not None))
    # TODO report of filtered values?

    tss = lmap(parse_timestamp, timestamps)
    tz = None
    if timezone is not None:
        TODO()
    else:
        tz = pytz.utc
    tss = lmap(lambda d: d.astimezone(tz) if d.tzinfo is not None else d.replace(tzinfo=tz), tss)

    assert_increasing(tss)

    mavg5 = mavg(tss, values, timedelta(5))
    mavg14 = mavg(tss, values, timedelta(14))

    fig = plt.figure()

    if ratio is not None:
        fig.set_size_inches(ratio)

    axes = fig.add_subplot(1,1,1)
    axes.plot(tss, values, marker=marker, color='red')
    axes.plot(tss, mavg5 , marker=marker, color='blue')
    axes.plot(tss, mavg14, marker=marker, color='green')
    return fig
