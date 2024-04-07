# Simple Bresenham implementation

This is a very simple Bresenham implementation for enumerating pixels along a line
including a very simple anti aliased version. It's the felt infinite implementation
out there and has been implemented during enhancement of a tomography reconstruction
library for personal use.

![](https://raw.githubusercontent.com/tspspi/pybresenham/master/example/lines01.png)

## Dependencies

* ```numpy >= 1.25```

## Installation

```
pip install pybresenham-tspspi
```

## Usage

### Simple lines

```
import matplotlib.pyplot as plt
import numpy as np

from bresenham.bresenham import trace_line

fig, ax = plt.subplots()

img = np.zeros((51, 21))
for pt in trace_line((-25,-10),(10,10)):
    img[int(pt[0]) + 25, int(pt[1]) + 10] = 1
ax.imshow(img)
```

### Simple lines using callbacks

```
from bresenham.bresenham import trace_line

def mycallback(point):
    print(f"Point at {point[0]} x {point[1]}")

trace_line((-25,-10),(10,10),mycallback)
```

### Antialiased lines

```
import matplotlib.pyplot as plt
import numpy as np
from bresenham.bresenham import trace_line_antialiased_it

fig, ax = plt.subplots()

imgaa = np.zeros((51, 21))
for pt, weight in trace_line_antialiased_it((-25,-10),(10,10)):
    imgaa[int(pt[0]) + 25, int(pt[1]) + 10] = weight
ax.imshow(imgaa)
```

### Antialiased lines using callbacks

```
from bresenham.bresenham import trace_line_antialiased

def mycallback(point, weight):
    print(f"Point at {point[0]} x {point[1]} with weight {weight}")

trace_line_antialiased((-25,-10),(10,10),mycallback)
```
