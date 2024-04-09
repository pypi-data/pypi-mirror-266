RESOLUTION = 6


def truncate_float(x):
    return float(format(x, f'.{RESOLUTION}e'))

def truncate_float_args(func):
    def wrapper(*args, **kwargs):
        truncated_args = []
        for arg in args:
            if isinstance(arg, float):
                truncated_args.append(truncate_float(arg))
            else:
                truncated_args.append(arg)
        return func(*truncated_args, **kwargs)
    return wrapper