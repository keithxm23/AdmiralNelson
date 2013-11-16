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
from line import cast_ray

np.set_printoptions(threshold='nan')
class mainWindow():
        times=1
        timestart=time.clock()
       
        def __init__(self):
                gamedata = pickle.load(open('C:/gamedata.p', 'rb'))
                self.blocks = gamedata['blockHeights']
                
                self.x = 0
                self.y = 0
                self.width = len(self.blocks)-1
                self.height = len(self.blocks[0])-1
                
                
                #normalize block heights
                for a,x in enumerate(self.blocks):
                    for b,y in enumerate(x):
                        if self.blocks[a][b] > 1.0:
                            self.blocks[a][b] = 1.0
                        elif self.blocks[a][b] == 1.0:
                            self.blocks[a][b] = 0.5
                    
                self.blocks = np.array(self.blocks)
                self.visibility_map = np.zeros((self.blocks.shape))
                self.blocks = self.blocks.transpose()
                
                self.root = Tkinter.Tk()
                self.frame = Tkinter.Frame(self.root, width=1024, height=768)
                self.frame.pack()
                self.canvas = Tkinter.Canvas(self.frame, width=1024,height=768)
                self.canvas.place(x=-2,y=-2)
                self.root.after(0,self.start) # INCREASE THE 0 TO SLOW IT DOWN
                self.root.mainloop()

                
        def start(self):
                try:
                    for y in range(0,self.height+1):
                        this_visibility_map = np.zeros((self.visibility_map.shape))
                        seed = (self.x,y)
                        x=0
                        while (x < self.width) or (y < self.height):
    #                        print x, y
                            cast_ray(seed[0],seed[1],x,0,self.blocks.transpose(),this_visibility_map)
                            cast_ray(seed[0],seed[1],0,y,self.blocks.transpose(),this_visibility_map)
                            
                            cast_ray(seed[0],seed[1],self.width-x,self.height,self.blocks.transpose(),this_visibility_map)
                            cast_ray(seed[0],seed[1],self.width,self.height-y,self.blocks.transpose(),this_visibility_map)
                        
                            if x < self.width: x+=1
                            if y < self.height: y+=1
                        self.visibility_map = np.add(self.visibility_map, this_visibility_map)   
                    
                    
                    max = np.amax(self.visibility_map)
#                    print max
                    tmp = self.visibility_map/max
                    self.im = Image.fromarray(np.uint8(cm.gist_heat(tmp.transpose())*255))
                    self.im.putpixel(seed,(0,0,255))
                    
                    newy, newx = self.blocks.shape
                    scale = 8
                    self.im = self.im.resize((newx*scale, newy*scale))
                    
                    self.photo = ImageTk.PhotoImage(image=self.im)
                    self.canvas.create_image(0,0,image=self.photo,anchor=Tkinter.NW)
                    self.root.update()
                    
                    
                    self.times+=1
#                    if self.times%33==0:
#                            print "%.02f FPS"%(self.times/(time.clock()-self.timestart))
                    if self.x < self.width: 
                        self.x+=1
                        self.root.after(1,self.start)
                except Exception as e:
                    
                    print e
                    self.root.after(10,self.start)

if __name__ == '__main__':
    x=mainWindow()