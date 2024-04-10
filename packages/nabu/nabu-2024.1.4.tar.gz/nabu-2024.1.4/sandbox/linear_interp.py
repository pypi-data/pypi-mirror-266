import numpy as np

def linear_interp(arr, x, new_x):
    dx = np.diff(x)
    dy = np.diff(arr)
    if new_x[0] > x[0]:
        dx = np.hstack([dx, dx[-1]])
        dy = np.hstack([dy, dy[-1]])
    else:
        dx = np.hstack([dx[0], dx])
        dy = np.hstack([dy[0], dy])        
    return (dy / dx) * (new_x - x) + arr
    
  
