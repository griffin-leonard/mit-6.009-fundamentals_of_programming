#!/usr/bin/env python3
"""
6.009 Spring 19 Lab 10 GUI
"""
import io
import sys
import base64
import tkinter
import PIL.Image

from lab import download_file, files_from_sequence

root = tkinter.Tk()
tcl = tkinter.Tcl()

URL = sys.argv[1]
try:
    delta_t = int(sys.argv[2])
except:
    delta_t = 50


def text_viewer():
    d = download_file(URL)
    text = tkinter.Text(root, height=24, width=80)
    text.pack(fill='both', expand=True)

    if '-seq' in URL:
        d = files_from_sequence(d)

    def update_text():
        try:
            if '-seq' in URL:
                new_text = next(d)
            else:
                new_text = b''.join(d)
        except (RuntimeError, FileNotFoundError):
            root.destroy()
            raise
        if new_text:
            text.delete(1.0, tkinter.END)
            try:
                text.insert(tkinter.END, new_text.decode('utf-8'))
            except Exception:
                root.destroy()
                raise
        tcl.after(delta_t, update_text)
    tcl.after(0, update_text)


def image_viewer():
    d = download_file(URL)
    canvas = tkinter.Canvas(root, height=480, width=640)
    canvas.pack(fill='both', expand=True)

    if '-seq' in URL:
        d = files_from_sequence(d)

    def update_animation():
        try:
            if '-seq' in URL:
                frame = next(d)
            else:
                frame = b''.join(d)
            if (frame == b''):
                print("GUI done")
                return
        except (RuntimeError, FileNotFoundError):
            root.destroy()
            print("GUI done")
            raise
        b = io.BytesIO(frame)
        b2 = io.BytesIO()
        try:
            im = PIL.Image.open(b)
            im.save(b2, 'GIF')
            canvas.configure(height=im.size[1], width=im.size[0])
        except:
            print('Invalid image file', file=sys.stderr)
            root.destroy()
            raise
        canvas.img = tkinter.PhotoImage(data=base64.b64encode(b2.getvalue()))
        img = canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        tcl.after(delta_t, update_animation)

    tcl.after(0, update_animation)

if any(i in URL for i in ('.png', '.jpg', '.gif', '.bmp', '.ppm', '.pgm')):
    image_viewer()
else:
    text_viewer()
root.mainloop()
