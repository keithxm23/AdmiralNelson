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
"""
class mainWindow():
        times=1
        timestart=time.clock()

        def __init__(self):

                from a_star import astar, vis_map
                self.astar = astar
                self.astar.process()
                self.vis_map = vis_map
                self.curr = astar.end
                self.starttile = astar.start

                blocks = np.array(self.vis_map)
                self.blocks = blocks.transpose()
                self.im = Image.fromarray(np.uint8(cm.gist_yarg(self.blocks)*255))


                self.root = Tkinter.Tk()
                self.frame = Tkinter.Frame(self.root, width=1024, height=768)
                self.frame.pack()
                self.canvas = Tkinter.Canvas(self.frame, width=1024,height=768)
                self.canvas.place(x=-2,y=-2)
                self.root.after(0,self.start) # INCREASE THE 0 TO SLOW IT DOWN
                self.root.mainloop()

        def start(self):
                try:
                    while self.curr is not self.starttile:
                        self.im.putpixel((self.curr.x, self.curr.y),(255,0,0))
                        self.curr = self.curr.parent

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