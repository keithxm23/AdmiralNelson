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


"""
Script to show real time state of the map with bot locations
NOT to be used in production bot code.
FOR ILLUSTRATION PURPOSES ONLY
"""

import cPickle as pickle
from visibility import get_visibility_map
from a_star import AStar

class mainWindow():
        times=1
        timestart=time.clock()

        def __init__(self):
                gamedata = pickle.load(open('C:/gamedata.p', 'rb'))
                blockHeights = gamedata['blockHeights']
                vis_map = get_visibility_map(blockHeights)
                astar = AStar(blockHeights, vis_map.tolist())
                start_point = (12,12)
                end_point = (22,25)
                path = astar.get_path(start_point[0],start_point[1],end_point[0],end_point[1])
                self.vis_map = vis_map
                self.curr = astar.end
                self.starttile = astar.start

                blocks = np.array(self.vis_map)
                self.blocks = blocks.transpose()
                self.im = Image.fromarray(np.uint8(cm.gist_yarg(self.blocks)*255))

                self.im.putpixel(start_point,(0,255,0))
                for x in path:
                    self.im.putpixel((x[0], x[1]),(255,0,0))
                self.im.putpixel(end_point,(0,0,255))


                self.root = Tkinter.Tk()
                self.frame = Tkinter.Frame(self.root, width=1024, height=768)
                self.frame.pack()
                self.canvas = Tkinter.Canvas(self.frame, width=1024,height=768)
                self.canvas.place(x=-2,y=-2)
                self.root.after(0,self.start) # INCREASE THE 0 TO SLOW IT DOWN
                self.root.mainloop()

        def start(self):
                try:

                    newy, newx = self.blocks.shape
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