'''Run pyinstaller from your project directory, but call it as the full directory to the .exe like C:\PathTo\Pyinstaller.exe

so your cmd would look something like

C:\Users\user\PycharmProjects\myproject> C:\PathTo\pyinstaller.exe --onefile --windowed myprogram.py'''

#!/usr/bin/python

import Tkinter as tk
import zipfile
import ImageTk
from PIL import Image
import StringIO
from tkinter import filedialog as fd
root = tk.Tk() # create a Tk root window

w = 800 # width for the Tk root
h = 650 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
pi = None
images = []


def show_image(n):
    global pi
    img = images[n]
    ww, hh = img.size
    img.thumbnail((400,500),Image.ANTIALIAS)
    pi = ImageTk.PhotoImage(img)
    sprite = w.create_image(400/2, 500/2, image=pi)

def load(img):
    images.append(img)
def selection_2(*args):
    pass
def selection_3(*args):
    pass
def selection_4(*args):
    pass
def selection_5(*args):
    pass
def selection_6(*args):
    pass
def selection_7(*args):
    pass
def selection_1(*args):
    global memory, OPTIONS
    a = variable_1.get()
    for i,name in enumerate(OPTION_NAMES[0]):
        if name == a:
            break

    print i
    b = variable.get()
    memory[int(b)][0] = i

def selectionEvent(*args):
    global OPTION_NAMES,memory
    print "EVENT"#, int(variable.get())
    a = variable.get()
    if a == "":
        return
    show_image(int(a))
    # Load Image presets from memory

    print memory[int(a)][0]
    variable_1.set(OPTION_NAMES[0][memory[int(a)][0]])
    print memory

LENGTH = 0
def ask():

    global pi, args,memory, LENGTH, images
    images = []
    f = fd.askopenfilename()
    # Open zip file
    if f  == '':
        return
    with zipfile.ZipFile(f, 'r') as myzip:
        LENGTH = len(myzip.namelist())
        memory = [[0 for i in range(len(OPTIONS))] for k in range(LENGTH)]
    with zipfile.ZipFile(f, 'r') as myzip:
        for i in xrange(len(myzip.namelist())):
            file_in_zip = myzip.namelist()[i]
            if (".jpg" in file_in_zip or ".JPG" in file_in_zip):
                data = myzip.read(file_in_zip)
                dataEnc = StringIO.StringIO(data)
                img = Image.open(dataEnc)
                load(img)
        args = []
        r.option_clear()
        for i in range(len(myzip.namelist())):
            args.append(str(i))
        refresh(args)



def refresh(args):
    # Reset var and delete all old options
    variable.set('')
    r['menu'].delete(0, 'end')
    # Insert list of new options (tk._setit hooks them up to var)
    for choice in args:
        r['menu'].add_command(label=choice, command=tk._setit(variable, choice))
    variable.trace('w',selectionEvent)
    variable.set(args[0])

def next():
    a = variable.get()
    if int(a) < len(args)-1:
        variable.set(int(a)+1)

import pickle
def export():
    global memory
    # save options during events, export them in the end
    # when an image is loaded, its constituents are loaded from memory
    # when an image field changes, it is saved to memory
    # export all memory to csv
    pickle.dump(memory, open("save.p", "wb"))


    pass
l1 = tk.Label(root,  fg="white") # bg="black",
l1.pack(pady=0,fill=tk.X)
l2 = tk.Label(root,  fg="white")
l2.pack(fill=tk.BOTH,pady=5)

label_open = tk.Label(l2,  fg="white")
label_open.pack(fill=tk.BOTH,pady=5)

w = tk.Canvas(l1, width=400, height=500)
w.pack(side=tk.LEFT)
w.create_rectangle(0, 0, 400, 500, fill="black")
def pop_2():
    pop_1()
def pop_3():
    pop_1()

myimage = []
def pop_1():
    toplevel = tk.Toplevel()
    w = 300 # width for the Tk root
    h = 150 # height for the Tk root

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    toplevel.geometry('%dx%d+%d+%d' % (w, h+50, x, y))
    w1 = tk.Canvas(toplevel, width=w, height=h)
    w1.pack()
    w1.create_rectangle(0, 0, w/2, h, fill="gray")
    w1.create_rectangle(w/2, 0, w, h, fill="black")

    img = Image.open("leaf.jpg")
    ww,hh = img.size
    img.thumbnail((150,150),Image.ANTIALIAS)
    ip = ImageTk.PhotoImage(img)
    myimage.append(ip)
    img2 = Image.open("leaf2.jpg")
    ww,hh = img2.size
    img2.thumbnail((150,150),Image.ANTIALIAS)
    ip2 = ImageTk.PhotoImage(img2)
    myimage.append(ip2)
    w1.create_image(150/2,150/2,image=ip)
    w1.create_image(150+150/2,150/2,image=ip2)
    w2 = tk.Label(toplevel,text="Vascular Leaf")
    w2.pack(side=tk.LEFT)
    w2 = tk.Label(toplevel,text="Compound Leaf")
    w2.pack(side=tk.RIGHT)

memory = None
OPTIONS = [2,2,2,2,2,2,2]
OPTION_NAMES = [["Yes","No"],["Simple","Compound"],["0","1"],["0","1"],["0","1"],["smoothed","toothed","lobbed"],["netlike","parallel"]]
################## Options

l_1 = tk.Label(l1,  fg="white", text="hello")
l_1.pack()
l_11 = tk.Label(l_1,  text="Vascular Leaf")
l_11.pack()

variable_1 = tk.StringVar(root)
variable_1.set(OPTION_NAMES[0][0]) # default value
args_1 = OPTION_NAMES[0]
r_1 = tk.OptionMenu(l_1, variable_1, *(args_1), command = selection_1)
r_1.config(width=30,height = 1)
r_1.pack(side=tk.LEFT)

b_1 = tk.Button(l_1, text="?", command=pop_1, width=2, height = 1)
b_1.pack(side=tk.RIGHT)

####

l_2 = tk.Label(l1,  fg="white")
l_2.pack()
l_11 = tk.Label(l_2,  text="Leaf type")
l_11.pack()

variable_2 = tk.StringVar(root)
variable_2.set(OPTION_NAMES[1][0]) # default value
args_2 = OPTION_NAMES[1]
r_2 = tk.OptionMenu(l_2, variable_2, *(args_2), command = selection_2)
r_2.config(width=30,height = 1)
r_2.pack(side=tk.LEFT)

b_2 = tk.Button(l_2, text="?", command=pop_2, width=2, height = 1)
b_2.pack(side=tk.RIGHT)


####

l_3 = tk.Label(l1,  fg="white")
l_3.pack()

l_11 = tk.Label(l_3,  text="Leaf Shape")
l_11.pack()
variable_3 = tk.StringVar(root)
variable_3.set(OPTION_NAMES[2][0]) # default value
args_3 = OPTION_NAMES[2]
r_3 = tk.OptionMenu(l_3, variable_3, *(args_3), command = selection_3)
r_3.config(width=30,height = 1)
r_3.pack(side=tk.LEFT)

b_3 = tk.Button(l_3, text="?", command=pop_1, width=2, height = 1)
b_3.pack(side=tk.RIGHT)


####

l_4 = tk.Label(l1,  fg="white")
l_4.pack()

l_11 = tk.Label(l_4,  text="Leaf base shape")
l_11.pack()
variable_4 = tk.StringVar(root)
variable_4.set(OPTION_NAMES[3][0]) # default value
args_4 = OPTION_NAMES[3]
r_4 = tk.OptionMenu(l_4, variable_4, *(args_4), command = selection_4)
r_4.config(width=30,height = 1)
r_4.pack(side=tk.LEFT)

b_4 = tk.Button(l_4, text="?", command=pop_1, width=2, height = 1)
b_4.pack(side=tk.RIGHT)
####

l_5 = tk.Label(l1,  fg="white")
l_5.pack()
l_11 = tk.Label(l_5,  text="Leaf tip shape")
l_11.pack()

variable_5 = tk.StringVar(root)
variable_5.set(OPTION_NAMES[4][0]) # default value
args_5 = OPTION_NAMES[4]
r_5 = tk.OptionMenu(l_5, variable_5, *(args_5), command = selection_5)
r_5.config(width=30,height = 1)
r_5.pack(side=tk.LEFT)

b_5 = tk.Button(l_5, text="?", command=pop_1, width=2, height = 1)
b_5.pack(side=tk.RIGHT)
####

l_6 = tk.Label(l1,  fg="white")
l_6.pack()
l_11 = tk.Label(l_6,  text="Leaf margin")
l_11.pack()

variable_6 = tk.StringVar(root)
variable_6.set(OPTION_NAMES[5][0]) # default value
args_6 = OPTION_NAMES[5]
r_6 = tk.OptionMenu(l_6, variable_6, *(args_6), command = selection_6)
r_6.config(width=30,height = 1)
r_6.pack(side=tk.LEFT)

b_6 = tk.Button(l_6, text="?", command=pop_1, width=2, height = 1)
b_6.pack(side=tk.RIGHT)
####

l_7 = tk.Label(l1,  fg="white")
l_7.pack()

l_11 = tk.Label(l_7,  text="Leaf venation")
l_11.pack()
variable_7 = tk.StringVar(root)
variable_7.set(OPTION_NAMES[6][0]) # default value
args_7 = OPTION_NAMES[6]
r_7 = tk.OptionMenu(l_7, variable_7, *(args_7), command = selection_7)
r_7.config(width=30,height = 1)
r_7.pack(side=tk.LEFT)

b_7 = tk.Button(l_7, text="?", command=pop_1, width=2, height = 1)
b_7.pack(side=tk.RIGHT)

##################

b = tk.Button(label_open, text="Open Image Zip File", command=ask, width=30, height = 1)
b.pack()
next_b = tk.Button(label_open, text="Next", command=next, width=30, height = 1)
next_b.pack()

variable = tk.StringVar(root)
variable.set("-") # default value
args = ["-"]
r = tk.OptionMenu(l2, variable, *(args), command = None)
r.config(width=30,height = 1)
r.pack()
next_b = tk.Button(label_open, text="Export", command=export, width=30, height = 1)
next_b.pack()

root.mainloop() # starts the mainloop
