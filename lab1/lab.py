#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as PILImage

## NO ADDITIONAL IMPORTS ALLOWED!

class Image:
    def __init__(self, width, height, pixels):
        self.width = width
        self.height = height
        self.pixels = pixels

    def get_pixel(self, pixel):
        return self.pixels[pixel]
    
    def getPixelCorrelate(self,x,y):
        """
        takes an image and the x and y values of a pixel,
        returns the value (color) of that pixel
        """
        a,b=x,y
        if x<0:
            a=0
        elif x>=self.width:
            a=self.width-1
        if y<0:
            b=0
        elif y>=self.height:
            b=self.height-1
        return self.pixels[self.width*b+a]

    def set_pixel(self, pixel, newcolor):
        self.pixels[pixel] = newcolor

    def apply_per_pixel(self, func):
        result = Image.new(self.width, self.height)
        for x in range(result.width):
            for y in range(result.height):
                pixel = self.width*y+x
                color = self.get_pixel(pixel)
                newcolor = func(color)
                result.set_pixel(pixel, newcolor)
        return result

    def inverted(self):
        return self.apply_per_pixel(lambda c: 255-c)

    def blurred(self, n):
        kern = []
        for k in range(n):
            kern.append([1/(n**2) for x in range(n)])
        return clip(correlate(self,kern))

    def sharpened(self, n):
        blur = self.blurred(n)
        double = self.apply_per_pixel(lambda c: 2*c)
        result = Image.new(self.width,self.height)
        i=0
        for y in range(self.height):
            for x in range(self.width):
                dub = double.getPixelCorrelate(x,y)
                bl = blur.getPixelCorrelate(x,y)
                result.set_pixel(i,dub-bl)
                i+=1
        return clip(result)

    def edges(self):
        kx,ky = [[-1,0,1],[-2,0,2],[-1,0,1]],[[-1,-2,-1],[0,0,0],[1,2,1]]
        result = Image.new(self.width,self.height)
        resultx,resulty = correlate(self,kx),correlate(self,ky)
        i=0
        for y in range(self.height):
            for x in range(self.width):
                pixX = resultx.getPixelCorrelate(x,y)
                pixY = resulty.getPixelCorrelate(x,y)
                result.set_pixel(i,round(math.sqrt(pixX**2+pixY**2)))
                i+=1
        return clip(result)
        

    # Below this point are utilities for loading, saving, and displaying
    # images, as well as for testing.

    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('height', 'width', 'pixels'))

    def __repr__(self):
        return "Image(%s, %s, %s)" % (self.width, self.height, self.pixels)

    @classmethod
    def load(cls, fname):
        """
        Loads an image from the given file and returns an instance of this
        class representing that image.  This also performs conversion to
        grayscale.

        Invoked as, for example:
           i = Image.load('test_images/cat.png')
        """
        with open(fname, 'rb') as img_handle:
            img = PILImage.open(img_handle)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299*p[0] + .587*p[1] + .114*p[2]) for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Unsupported image mode: %r' % img.mode)
            w, h = img.size
            return cls(w, h, pixels)

    @classmethod
    def new(cls, width, height):
        """
        Creates a new blank image (all 0's) of the given height and width.

        Invoked as, for example:
            i = Image.new(640, 480)
        """
        return cls(width, height, [0 for i in range(width*height)])

    def save(self, fname, mode='PNG'):
        """
        Saves the given image to disk or to a file-like object.  If fname is
        given as a string, the file type will be inferred from the given name.
        If fname is given as a file-like object, the file type will be
        determined by the 'mode' parameter.
        """
        out = PILImage.new(mode='L', size=(self.width, self.height))
        out.putdata(self.pixels)
        if isinstance(fname, str):
            out.save(fname)
        else:
            out.save(fname, mode)
        out.close()

    def gif_data(self):
        """
        Returns a base 64 encoded string containing the given image as a GIF
        image.

        Utility function to make show_image a little cleaner.
        """
        buff = BytesIO()
        self.save(buff, mode='GIF')
        return base64.b64encode(buff.getvalue())

    def show(self):
        """
        Shows the given image in a new Tk window.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # if tk hasn't been properly initialized, don't try to do anything.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # highlightthickness=0 is a hack to prevent the window's own resizing
        # from triggering another resize event (infinite resize loop).  see
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        canvas = tkinter.Canvas(toplevel, height=self.height,
                                width=self.width, highlightthickness=0)
        canvas.pack()
        canvas.img = tkinter.PhotoImage(data=self.gif_data())
        canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        def on_resize(event):
            # handle resizing the image when the window is resized
            # the procedure is:
            #  * convert to a PIL image
            #  * resize that image
            #  * grab the base64-encoded GIF data from the resized image
            #  * put that in a tkinter label
            #  * show that image on the canvas
            new_img = PILImage.new(mode='L', size=(self.width, self.height))
            new_img.putdata(self.pixels)
            new_img = new_img.resize((event.width, event.height), PILImage.NEAREST)
            buff = BytesIO()
            new_img.save(buff, 'GIF')
            canvas.img = tkinter.PhotoImage(data=base64.b64encode(buff.getvalue()))
            canvas.configure(height=event.height, width=event.width)
            canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        # finally, bind that function so that it is called when the window is
        # resized.
        canvas.bind('<Configure>', on_resize)
        toplevel.bind('<Configure>', lambda e: canvas.configure(height=e.height, width=e.width))

        # when the window is closed, the program should stop
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)

def correlate(img, kern):
    """
    applies an abitrary kernel to an arbitrary image; returns a new image
    img: an image object
    kern: 2D array (list of lists) representing the kernel
    """
    result = Image.new(img.width,img.height)
    
    #create a 1D version of the kernel
    Dkern = []
    for i in range(len(kern)):
        for pix in kern[i]:
            Dkern.append(pix)
            
    for y in range(img.height):
        for x in range(img.width):
            patch = Image.new(len(kern),len(kern[0]))
            index = 0
            for b in range(len(kern)):
                for a in range(len(kern[0])):
                    patch.set_pixel(index, img.getPixelCorrelate(x-(len(kern)//2)+a,\
                                                         y-(len(kern[0])//2)+b))
                    index += 1
            newcolor = 0
            for pix in range(len(patch.pixels)):
                newcolor += patch.pixels[pix]*Dkern[pix]
            result.set_pixel(img.width*y+x,newcolor)
    return result

def clip(img):
    """
    clips invalid pixel values
    """
    for i,p in enumerate(img.pixels):
        img.set_pixel(i,int(round(p)))
        if p<0:
            img.set_pixel(i,0)
        elif p>255:
            img.set_pixel(i,255)
    return img

try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()
    def reafter():
        tcl.after(500,reafter)
    tcl.after(500,reafter)
except:
    tk_root = None
WINDOWS_OPENED = False

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
#    im = Image.load('test_images/bluegill.png')
#    imInverted = im.inverted()
#    imInverted.save('bluegill_inverted.png')
    
#    kernel = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
#    im = Image.load('test_images/pigbird.png')
#    imKernel = clip(correlate(img,kernel))
#    imKernel.save('pigbird_correlate.png')
    
#    im = Image.load('test_images/cat.png')
#    imBlurred = im.blurred(5)
#    imBlurred.save('cat_blurred.png')
    
#    im = Image.load('test_images/python.png')
#    imSharpen = im.sharpened(11)
#    imSharpen.save('python_sharped.png')

    im = Image.load('test_images/construct.png')
    imEdges = im.edges()
    imEdges.save('construct_edges.png')


    # the following code will cause windows from Image.show to be displayed
    # properly, whether we're running interactively or not:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()

