'''Run pyinstaller from your project directory, but call it as the full directory to the .exe like C:\PathTo\Pyinstaller.exe

so your cmd would look something like

C:\Users\user\PycharmProjects\myproject> C:\PathTo\pyinstaller.exe --onefile --windowed myprogram.py'''

import Tkinter as tk
import zipfile
import ImageTk
from PIL import Image
import StringIO
import tkFileDialog as fd
import tkMessageBox
import pickle
import os
import xml.etree.ElementTree as ET

# Tooltips

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

# Main windows

root = tk.Tk() # create a Tk root window
# Window variables
w = 800 # width for the Tk root
h = 690 # height for the Tk root
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

root.geometry('%dx%d+%d+%d' % (w, h, x, y)) # set the dimensions of the screen and where it is placed

pi = None
images = []
LENGTH = 0

memory = None
OPTIONS = [2,2,2,2,2,2,2]
OPTION_LABELS = ["Leaf","Leaf Type","Leaf Shape","Leaf base shape","Leaf tip shape","Leaf margin","Leaf venation","Species","Contributor"]
OPTION_NAMES = [["YES","NO"],["SIMPLE","COMPOUND"],["ACEROSE","AWL-SHAPED","GLADIATE","HASTATE","CORDATE","DELTOID","LANCEOLATE","LINEAR","ELLIPTIC","ENSIFORM","LYRATE",
                   "OBCORDATE","FALCATE","FLABELLATE","OBDELTOID","OBELLIPTIC","OBLANCEOLATE","OBLONG","PERFOLIATE","QUADRATE","OBOVATE","ORBICULAR",
                   "RENIFORM","RHOMBIC","OVAL","OVATE","ROTUND","SAGITTATE","PANDURATE","PELTATE","SPATULATE","SUBULATE"],
                   ["AEQUILATERAL","ATTENUATE","AURICULATE","CORDATE","CUNEATE","HASTATE","OBLIQUE","ROUNDED","SAGGITATE","TRUNCATE"],
                   ["CIRROSE","CUSPIDATE","ACUMINATE","ACUTE","EMARGINATE","MUCRONATE","APICULATE","ARISTATE","MUCRONULATE","MUTICOUS","ARISTULATE","CAUDATE","OBCORDATE","OBTUSE","RETUSE","ROUNDED","SUBACUTE","TRUNCATE"]
                   ,["BIDENTATE","BIFID","DENTATE","DENTICULATE","BIPINNATIFID","BISERRATE","DIGITATE","DISSECTED","CLEFT","CRENATE","DIVIDED","ENTIRE","CRENULATE","CRISPED","EROSE","INCISED","INVOLUTE","LACERATE","PEDATE","PINNATIFID","LACINIATE","LOBED","PINNATILOBATE","PINNATISECT","LOBULATE","PALMATIFID","REPAND","REVOLUTE","PALAMTISECT","PARTED","RUNCINATE","SERRATE"],["RETICULATE","PARALLEL"],["SPECIES FIELD"],["CONTRIBUTOR FIELD"]]
current_image = None
pi = None
autosave = False
current_file = None

def debug(o):
    print "debug: "+o

def show_image(f):
    global pi
    current_image = Image.open(f)
    current_image.thumbnail((400,500),Image.ANTIALIAS)
    pi = ImageTk.PhotoImage(current_image)
    sprite = w.create_image(400/2, 500/2, image=pi)

def load(img):
    images.append(img)

def try_to_save():
    global vars,string_vars, current_file
    # Iterate through all variables
    # obtain proper xml file and save everything, since there was a change
    debug("Trying to save to xml")
    # Vars and StringVars should be saved to xml, this is only called if autosave was enabled

    # Image name, var fields, string_var fields
    root = ET.Element("Image")
    f =  os.path.splitext(current_file)[0]
    ET.SubElement(root,"ImageFileName").text = os.path.basename(f+".jpg")
    for label in OPTION_LABELS:
        true_label = label.replace(" ","")
        print true_label
        if "FIELD" in OPTION_NAMES[OPTION_LABELS.index(label)][0]:
            ET.SubElement(root,true_label).text = str(string_vars[len(OPTION_LABELS)-1-OPTION_LABELS.index(label)].get())
        else:
            ET.SubElement(root,true_label).text = str(vars[OPTION_LABELS.index(label)].get())

    tree = ET.ElementTree(root)
    tree.write(f+".xml",encoding="utf-8", xml_declaration=True)

def selection(*args):
    global autosave
    if autosave:
        try_to_save()

def import_xml(xml_path):
    # Try to import from the xml path supplied
    # We need to construct vars and string vars from the fields
    e = ET.parse(xml_path).getroot()
    for atype in e:
        print atype.tag, atype.text
        for label in OPTION_LABELS:
            replaced_label = str(label)
            replaced_label = replaced_label.replace(" ","")
            if replaced_label == atype.tag:
                if "FIELD" in OPTION_NAMES[OPTION_LABELS.index(label)][0]:
                    string_vars[len(OPTION_LABELS)-1-OPTION_LABELS.index(label)].set(atype.text)
                else:
                    vars[OPTION_LABELS.index(label)].set(atype.text)

    pass

def check_image_with_pil(path):
     try:
         Image.open(path)
     except IOError:
         return False
     return True

def ask(): # Open image file and see if xml exists
    global current_image, autosave, vars, current_file

    autosave = False
    f = fd.askopenfilename()
    # Open zip file
    open = check_image_with_pil(f)
    if not open:
        debug("File is not an image file")
    else:
        debug("File has been opened")
    current_file = f
    xml_path = os.path.splitext(f)[0]+".xml"
    if os.path.isfile(xml_path):
        # prompt user
        # if user says overwrite file, set autosave
        # if user doesn't want to overwrite, only import it without autosave
        result = tkMessageBox.askquestion("Delete", "Xml file for this image already exists. Do you want to overwrite it?", icon='warning')
        if result == "yes":
            autosave = True
            debug("XML exists, overwrite")
        else:
            # IMPORT XML
            debug("XML exists, only import (READ ONLY)")
            import_xml(xml_path)

    else:
        debug("XML doesn't exist")
        autosave = True

    debug("After importing image, autosave is "+str(autosave))
    show_image(f)


def export(): # Export a single file in xml format
    global memory
    # save options during events, export them in the end
    # when an image is loaded, its constituents are loaded from memory
    # when an image field changes, it is saved to memory
    # export all memory to csv
    pickle.dump(memory, open("save.p", "wb"))

##################

# Create windows
current_toplevel = None

l1 = tk.Label(root) # bg="black",
l1.pack(pady=0,fill=tk.X)

w = tk.Canvas(l1, width=400, height=550)
w.pack(side=tk.LEFT)
w.create_rectangle(0, 0, 400, 550, fill="black")

frame = tk.Frame(l1,width=300, height=800, bg="gray", colormap="new", relief=tk.GROOVE ,borderwidth =4)
frame.pack(pady=0,fill=tk.BOTH)
# Open Image File
label_button =  tk.Label(l1, width=50)
b = tk.Button(frame, text="Open Image File", command=ask, width=14, height = 1)
b.pack(pady=20)

# Hover effect
popup_canvas = None

# Popup selection window
popup_images = None

def update(selection,option):
    # Close box
    global current_toplevel, vars,autosave
    debug("EXITED with options")
    current_toplevel.destroy()
    current_toplevel = None
    vars[option].set(OPTION_NAMES[option][selection])
    if autosave:
        try_to_save()

def popup_command(selection,options):
    # Update the option
    update(selection,options)
    debug(OPTION_NAMES[options][selection])

def closed_popup():
    global current_toplevel
    debug("EXITED without options")
    current_toplevel.destroy()
    current_toplevel = None

def fce(myX):
    def pop(x_option=myX): # With this wrapper we have variable arguments for pop
        global popup_images, popup_canvas, current_toplevel

        true_width = 155
        true_height = 145
        popup_images = []
        toplevel = tk.Toplevel()
        current_toplevel = toplevel
        toplevel.protocol("WM_DELETE_WINDOW", closed_popup)
        # We need 150x150 per image. First we obtain the length of images from the option names
        n = len(OPTION_NAMES[x_option])
        # We want a grid that has at most 6 entries, thus if the length is larger than 8, we set wn to six
        wn = min(8,n)
        hn = ((n-1)/8)+1
        # Thus if we have 8 images only then do we have another line
        w = true_width*wn # width for the Tk root
        h = true_height*hn # height for the Tk root

        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        toplevel.geometry('%dx%d+%d+%d' % (w, h, x, y))
        popup_frame = tk.Frame(toplevel, width=w, height=h, bg="grey", colormap="new", relief=tk.FLAT, borderwidth=4)
        popup_frame.pack()
        #w1.create_rectangle(0, 0, w/2, h, fill="gray")
        #w1.create_rectangle(w/2, 0, w, h, fill="black")

        # Create all the images in the locations that are appropriate. wn and hn decide length and height
        for xx in range(wn):
            for yy in range(hn):
                if xx+wn*yy >= n:
                    break

                img = Image.open("leaf.jpg")
                img.thumbnail((150,150),Image.ANTIALIAS)
                ip = ImageTk.PhotoImage(img)
                popup_images.append(ip)
                label = tk.Label(popup_frame, image=ip)
                label.pack()
                label.grid(row=yy,column=xx)
                label.bind("<Button-1>",lambda event,options=x_option,e=xx+wn*yy: popup_command(e,options))
                createToolTip(label, OPTION_NAMES[x_option][xx+wn*yy])

    return pop

def enter_field(sv):
    pass

################## Fields
labels = []
buttons = []
vars = []
string_vars = []

def field(event,option):
    global autosave
    debug("Trying to save from text entry capture, autosave is "+str(autosave))
    if autosave:
        try_to_save()

for i in range(9):#len(OPTIONS)):

    myframe = tk.Frame(l1, width=300, height=800, bg="grey", colormap="new", relief=tk.GROOVE, borderwidth=4)
    myframe.pack(pady=0, fill=tk.BOTH)
    label_part = tk.Label(myframe,  text=OPTION_LABELS[i])
    label_part.pack()

    if "FIELD" in OPTION_NAMES[i][0]:
        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: enter_field(sv))
        string_vars.append(sv)
        e = tk.Entry(myframe,textvariable=sv)
        e.bind("<Return>",lambda event,field_option=i:field(event,field_option))
        e.pack()
        # Create a text field
    else:
        var = tk.StringVar(root)
        var.set(OPTION_NAMES[i][0]) # default value
        vars.append(var)
        args_1 = OPTION_NAMES[i]
        myframe_field = tk.Frame(myframe, width=300, height=800, bg="grey", colormap="new", relief=tk.GROOVE, borderwidth=4)
        myframe_field.pack(pady=0, fill=tk.Y)

        r = tk.OptionMenu(myframe_field, var, *(args_1), command = selection)
        r.config(width=30,height = 1)
        r.pack(side=tk.LEFT)
        b = tk.Button(myframe_field, text="Pick", command=fce(i), width=3, height = 1)
        b.pack(side=tk.RIGHT)

root.mainloop() # starts the mainloop
