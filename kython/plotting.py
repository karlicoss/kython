import matplotlib.pyplot as plt # type: ignore
from matplotlib.ticker import MultipleLocator, FormatStrFormatter # type: ignore

from kython import *


def plot_timestamped(
        timestamps,
        values,
        ratio=None,
        marker='o',
        timezone=None,
        mavgs=[(5, 'blue'), (14, 'green')],
        ytick_size=None,
        ylimits=None,
        figure=None,
):
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

    mavgsc = [(mavg(tss, values, timedelta(m)), c) for m, c in mavgs]

    fig: plt.Figure
    if figure is None:
        fig = plt.figure()
    else:
        fig = plt.figure(figure)

    if ratio is not None:
        fig.set_size_inches(ratio)

    axes = fig.add_subplot(1,1,1)

    if ytick_size is not None:
        major_loc = MultipleLocator(ytick_size)
        axes.yaxis.set_major_locator(major_loc)

    if ylimits is not None:
        axes.set_ylim(ylimits)


    axes.plot(tss, values, marker=marker, color='red')
    for mv, c in mavgsc:
        axes.plot([m[0] for m in mv], [m[1] for m in mv], marker=marker, color=c)
    return fig
