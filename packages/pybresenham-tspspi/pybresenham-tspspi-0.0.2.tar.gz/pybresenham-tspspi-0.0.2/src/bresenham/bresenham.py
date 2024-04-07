import numpy as np

def trace_line(start, end, callback = None):
    if (len(start) != 2) or (len(end) != 2):
        raise ValueError("Start and end have to be 2-tuples or 2-lists")
    if (callback is not None) and (not callable(callback)):
        raise ValueError("A callback has to be callable")

    swap = False
    swapSign = 1
    try:
        slope = (end[1] - start[1]) / (end[0] - start[0])
    except ZeroDivisionError:
        swap = True

    if swap or (slope > 1) or (slope < -1):
        swap = True
        if start[1] > end[1]:
            swapSign = -1
        start = (start[1], start[0])
        end = (end[1], end[0])
    else:
        if start[0] > end[0]:
            swapSign = -1

    xvals = np.arange(int(start[0]), int(end[0]) + 1 * swapSign, np.sign(end[0] - start[0]))
    slope = (end[1] - start[1]) / (end[0] - start[0])
    yvals = start[1] + np.arange(0, len(xvals), 1) * slope * swapSign

    if swap:
        points = zip(yvals.astype(int), xvals.astype(int))
    else:
        points = zip(xvals.astype(int), yvals.astype(int))

    if callback is not None:
        for pt in points:
            callback(pt)
        return
    else:
        return points

def trace_line_it(start, end):
    points = trace_line(start, end)
    for pt in points:
        yield pt

def trace_line_antialiased(start, end, callback = None):
    if (len(start) != 2) or (len(end) != 2):
        raise ValueError("Start and end have to be a 2-list or 2-tuple")
    if (callback is not None) and (not callable(callback)):
        raise ValueError("A callback has to be a callable")

    swap = False
    swapSign = 1
    try:
        slope = (end[1] - start[1]) / (end[0] - start[0])
    except ZeroDivisionError:
        swap = True

    if swap or (slope > 1) or (slope < -1):
        swap = True
        if start[1] > end[1]:
            swapSign = -1
        start = (start[1], start[0])
        end = (end[1], end[0])
    else:
        if start[0] > end[0]:
            swapSign = -1

    xvals = np.arange(int(start[0]), int(end[0]) + 1 * swapSign, np.sign(end[0] - start[0]))
    slope = (end[1] - start[1]) / (end[0] - start[0])
    yvals = start[1] + np.arange(0, len(xvals), 1) * slope * swapSign
    weights = np.abs(yvals - yvals.astype(int))
    neighborDirection = np.sign(yvals - yvals.astype(int))
    neighborY = yvals + neighborDirection
    neighborWeights = 1.0 - weights
    neighborX = xvals.copy()

    xreal = np.empty((len(xvals)*2,))
    yreal = np.empty((len(xvals)*2,))
    wreal = np.empty((len(xvals)*2,))

    xreal[0::2], xreal[1::2] = xvals, neighborX
    yreal[0::2], yreal[1::2] = yvals, neighborY
    wreal[0::2], wreal[1::2] = weights, neighborWeights

    if swap:
        points = zip(yreal.astype(int), xreal.astype(int))
    else:
        points = zip(xreal.astype(int), yreal.astype(int))

    if callback is not None:
        for ipt, pt in enumerate(points):
            callback((pt, wreal[ipt]))
        return
    else:
        return points, wreal

def trace_line_antialiased_it(start, end):
    points, weights = trace_line_antialiased(start, end)
    for ipt, pt in enumerate(points):
        yield (pt, weights[ipt])

