"""
Credits to Scott W Harden for parts of this script.
http://www.swharden.com/blog/2010-06-24-fast-tk-pixelmap-generation-from-2d-numpy-arrays-in-python/
"""

import Tkinter
from PIL import Image, ImageTk
from pylab import cm
import numpy as np
import time
import cPickle as pickle
from game_constants import gameplayDataFilepath

"""
Script to show real time state of the map with bot locations
"""
class mainWindow():
        times=1
        timestart=time.clock()
       
        def __init__(self):
                self.root = Tkinter.Tk()
                self.frame = Tkinter.Frame(self.root, width=1024, height=768)
                self.frame.pack()
                self.canvas = Tkinter.Canvas(self.frame, width=1024,height=768)
                self.canvas.place(x=-2,y=-2)
                self.root.after(0,self.start) # INCREASE THE 0 TO SLOW IT DOWN
                self.root.mainloop()
                
        def start(self):
                
                try:
                    gamedata = pickle.load(open(gameplayDataFilepath, 'rb'))
                    blocks = gamedata['blockHeights']
                    
                    #normalize block heights
                    for a,x in enumerate(blocks):
                        for b,y in enumerate(x):
                            if blocks[a][b] > 1.0:
                                blocks[a][b] = 1.0
                            elif blocks[a][b] == 1.0:
                                blocks[a][b] = 0.5
                    
                    blocks = np.array(blocks)
                    blocks = blocks.transpose()
                    
                    mapWidth = len(blocks)
                    mapHeight = len(blocks[0])

                    visibleNodes = gamedata['visibleNodes']

                    for x, y in visibleNodes:
                        blocks[y][x] = 0.2

                    self.im = Image.fromarray(np.uint8(cm.gist_yarg(blocks)*255))

                    #Set bot positions
                    for pos in gamedata['bot_positions']:
                        self.im.putpixel(pos,(0,0,255))

                    newy, newx = blocks.shape
                    scale = 8
                    self.im = self.im.resize((newx*scale, newy*scale))
                    
                    self.photo = ImageTk.PhotoImage(image=self.im)
                    self.canvas.create_image(0,0,image=self.photo,anchor=Tkinter.NW)
                    self.root.update()
                    self.times+=1
                    if self.times%33==0:
                            print "%.02f FPS"%(self.times/(time.clock()-self.timestart))
                    self.root.after(10,self.start)
                except Exception as e:
                    
                    print e
                    self.root.after(10,self.start)

if __name__ == '__main__':
    x=mainWindow()