def cast_ray(x0, y0, x1, y1, arr, vis):
    """
    xo,yo    => start point
    x1,y1    => end point
    arr      => numpy array in which line is to be drawn
    """
    dx = abs(x1-x0)
    dy = abs(y1-y0) 
    if x0 < x1:
        sx = 1 
    else:
        sx = -1
    if y0 < y1:
        sy = 1
    else:
        sy = -1
    
    err = dx-dy

    while True:
        if arr[x0,y0] > 0:
            break
        vis[x0,y0] = 1
        if x0 == x1 and y0 == y1:
           break
        e2 = 2*err
        if e2 > -dy:
            err = err - dy
            x0 = x0 + sx
        
        if x0 == x1 and y0 == y1: 
            vis[x0,y0] = 1
            break
        
        if e2 <  dx: 
            err = err + dx
            y0 = y0 + sy
            
#    return vis