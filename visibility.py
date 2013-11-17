import cPickle as pickle
import numpy as np
np.set_printoptions(threshold='nan')

def normalize(x):
    if x > 1.0:
        return 1.0
    elif x == 1.0:
        return 0.5
    else:
        return 0.0

#TODO once you figure out how to import numpy and scipy here, directly call functions instead of using pickles as intermediary
def get_visibility_map(blockHeights):
    gamedata = pickle.load(open('C:/gamedata.p', 'rb'))
    blockHeights = gamedata['blockHeights']

    width = len(blockHeights)
    height = len(blockHeights[0])

    blocks = np.array(blockHeights, dtype='f')

    #Normalize the block heights
    old_shape = blocks.shape
    blocks = blocks.reshape(-1)
    for i, v in enumerate(blocks):
        blocks[i] = normalize(v)
    blocks = blocks.reshape(old_shape)

    visibility_map = np.zeros((blocks.shape))

    # For each point in the grid
    xstep = ystep = 4
    xsidestep = ysidestep = 1
    for x in range(0,width,xstep):
        for y in range(0,height,ystep):
            this_visibility_map = np.zeros((blocks.shape))
            #Cast rays to every tile on the edges

            #First, top and bottom sides
            for endx in range(0,width,xsidestep):
                cast_ray(x,y,endx,0,blocks,this_visibility_map)
                cast_ray(x,y,endx,height-1,blocks,this_visibility_map)

            #The, left and right sides
            for endy in range(0,height,ysidestep):
                cast_ray(x,y,0,endy,blocks,this_visibility_map)
                cast_ray(x,y,width-1,endy,blocks,this_visibility_map)

            visibility_map = np.add(visibility_map, this_visibility_map)

    max_val = np.max(visibility_map)
    visibility_map = visibility_map/max_val #normalize
    return visibility_map


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