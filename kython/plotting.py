import matplotlib.pyplot as plt # type: ignore
from matplotlib.ticker import MultipleLocator, FormatStrFormatter # type: ignore

from kython import *


def plot_timestamped(
        timestamps,
        values,
        plabels=None,
        ratio=None,
        timezone=None,
        mavgs=[(5, 'blue'), (14, 'green')],
        ytick_size=None,
        ylimits=None,
        figure:plt.Figure=None,
        axes:plt.Axes=None,
        **rest
) -> plt.Figure:
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

    fig = figure
    if fig is None:
        fig = plt.figure()

    if ratio is not None:
        fig.set_size_inches(ratio)

    if axes is None:
        axes = fig.add_subplot(1,1,1)

    if ytick_size is not None:
        major_loc = MultipleLocator(ytick_size)
        axes.yaxis.set_major_locator(major_loc)

    if ylimits is not None:
        axes.set_ylim(ylimits)


    axes.plot(tss, values, color='red', **rest)
    # TODO ??
    if plabels:
        for t, v, l in zip(tss, values, plabels):
            axes.annotate(l, xy=(t, v))
    for mv, c in mavgsc:
        axes.plot([m[0] for m in mv], [m[1] for m in mv], **rest, color=c) # TODO hmm
    return fig
