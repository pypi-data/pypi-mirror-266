from perf import track_total_runtime


@track_total_runtime
def normalize_interval(start, end, days=1):
    if end < start:
        end += 24
    end += 24 * (days - 1)
    return (start, end)
