from hifitime import Epoch, TimeSeries, Unit, Duration
from datetime import datetime
import pickle


def test_strtime():
    """
    Tests both strp and strftime
    """
    epoch = Epoch("2023-04-13 23:31:17 UTC")
    dt = datetime(2023, 4, 13, 23, 31, 17)

    epoch_fmt = epoch.strftime("%A, %d %B %Y %H:%M:%S")
    dt_fmt = dt.strftime("%A, %d %B %Y %H:%M:%S")

    assert epoch_fmt == dt_fmt

    assert Epoch.strptime(dt_fmt, "%A, %d %B %Y %H:%M:%S") == epoch

    assert pickle.loads(pickle.dumps(epoch)) == epoch


def test_utcnow():
    epoch = Epoch.system_now()
    dt = datetime.utcnow()

    # Hifitime uses a different clock to Python and print down to the nanosecond
    assert dt.isoformat()[:20] == f"{epoch}"[:20]


def test_time_series():
    """
    Time series are really cool way to iterate through a time without skipping a beat.
    """

    nye = Epoch("2022-12-31 23:59:00 UTC")

    time_series = TimeSeries(
        nye,
        nye + Unit.Second * 10,
        Unit.Second * 1,
        inclusive=True,
    )
    print(time_series)

    assert pickle.loads(pickle.dumps(time_series)) == time_series

    for num, epoch in enumerate(time_series):
        print(f"#{num}:\t{epoch}")

    assert num == 10
    # Once consummed, the iterator in the time series will be different,
    # so the pickling will return something different
    assert pickle.loads(pickle.dumps(time_series)) != time_series


def test_duration_eq():
    """
    Checks that Duration comparisons work
    """

    assert Unit.Second * 0.0 == Duration("0 ns")
    assert Unit.Second * 1.0 >= Duration("0 ns")
    assert Unit.Second * 1.0 > Duration("0 ns")
    assert Duration("0 ns") <= Unit.Second * 1.0
    assert Duration("0 ns") < Unit.Second * 1.0

    dur = Duration("37 min 26 s")
    assert pickle.loads(pickle.dumps(dur)) == dur
