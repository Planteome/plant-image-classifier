''' Assume windows has python. Make sure python has no pyinstaller (use pip uninstall pyinstaller for the windows python installation)
Then install pyinstaller in a virtualenvironment. Use the command pyinstaller with --windowed --onefile core.py
Plant image classifier v0.1
'''

from misc import *
import tkinter as tk
from PIL import ImageTk, Image

from tkinter import font as tkFont
from tkinter import filedialog as fd
from tkinter import messagebox as tkMessageBox
import os

import xml.etree.ElementTree as ET
from threading import Lock

def debug(o):
    print("debug: "+str(o))

# Determine which platform we are using
import platform

linux_flag = False
mac_flag = False
sysname = platform.system()
if sysname == "Linux":
    linux_flag = True
if sysname == "Mac" or "Darwin" in sysname:
    mac_flag = True

debug("Linux system : {} , Mac System : {} , Windows System : {}".format(linux_flag, mac_flag, (not linux_flag) and (not mac_flag)))

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
root.wm_title("Plant Image Classifier")
w = 1024 # width for the Tk root
h = 730 # height for the Tk root
tkFont.Font(family="Times", size=10, weight=tkFont.BOLD)
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y)) # set the dimensions of the screen and where it is placed

#### Label tags
OPTIONS = [2,2,2,2,2,2,2]
OPTION_LABELS = ["Leaf","Leaf Type","Leaf Shape","Leaf base shape","Leaf tip shape","Leaf margin","Leaf venation","Species","Contributor"]
OPTION_NAMES = [["YES","NO","NONE"],["SIMPLE","COMPOUND","NONE"],["ACEROSE","AWL-SHAPED","GLADIATE","HASTATE","CORDATE","DELTOID","LANCEOLATE","LINEAR","ELLIPTIC","ENSIFORM","LYRATE",
                   "OBCORDATE","FALCATE","FLABELLATE","OBDELTOID","OBELLIPTIC","OBLANCEOLATE","OBLONG","PERFOLIATE","QUADRATE","OBOVATE","ORBICULAR",
                   "RENIFORM","RHOMBIC","OVAL","OVATE","ROTUND","SAGITTATE","PANDURATE","PELTATE","SPATULATE","SUBULATE","NONE"],
                   ["AEQUILATERAL","ATTENUATE","AURICULATE","CORDATE","CUNEATE","HASTATE","OBLIQUE","ROUNDED","SAGITTATE","TRUNCATE","NONE"],
                   ["CIRROSE","CUSPIDATE","ACUMINATE","ACUTE","EMARGINATE","MUCRONATE","APICULATE","ARISTATE","MUCRONULATE","MUTICOUS","ARISTULATE","CAUDATE","OBCORDATE","OBTUSE","RETUSE","ROUNDED","SUBACUTE","TRUNCATE","NONE"]
                   ,["BIDENTATE","BIFID","DENTATE","DENTICULATE","BIPINNATIFID","BISERRATE","DIGITATE","DISSECTED","CLEFT","CRENATE","DIVIDED","ENTIRE","CRENULATE","CRISPED","EROSE","INCISED","INVOLUTE","LACERATE","PEDATE","PINNATIFID","LACINIATE","LOBED","PINNATILOBATE","PINNATISECT","LOBULATE","PALMATIFID","REPAND","REVOLUTE","PALMATISECT","PARTED","RUNCINATE","SERRATE","SERRULATE","SINUATE","TRIDENTATE","TRIFID","TRIPARTITE","TRIPINNATIFID","NONE"],["RETICULATE","PARALLEL","NONE"],["SPECIES FIELD"],["CONTRIBUTOR FIELD"]]

# Image manipulation variables
current_image = None
current_image_resized = None
pi = None
autosave = False
current_file = None

# Image view manipulation
open_once = False
resize_once = False
sprite = None
bb = None
circle = None
pA = None
pB = None
pSeg = None
p1,p2,p3,p4 = None,None,None,None
zoom = 0
x_image = 0
y_image = 0
optimal_zoom = 1

# Text widgets

loading_text_widget = False # make true while loading so it doesn't proc event

# Bounding box variables

bb_annotation = [0,0,0,0]
angle_bb = 0 # Always updated to be within 0 and 2*pi. Starts from 0 on a new box, and increases to 2*pi in a clockwise fashion
rectangle_size = (1,1)
horizontal_axis_scale = False # Horizontal or Vertical scaling side to change
horizontal_axis_cursor = False
positive_scaling = True # Whether the mouse was caught in the positive or negative side of the scaling tool.
show_annotation = True
mode = 0
pointA, pointB = None,None
segCounter = 0
draw_box_color = "white"

# Ribbon variables

button_images = []
button_image_paths = ["open","center","zoomin","zoomout","annotate","mode","qm","label","annotation_off"]

# With this lock, every time we load the application and set the field variables with set, the event triggered saturates with
# the locked text_loading_lock, which starts at 2 and goes back to 0. While it drops (during variable setting at load time)
# there is no saving of the xml file
# When it reaches zero, it means the user can now change the fields of contributor species, and actually trigger a save-xml event
# By setting the text_loading_lock to the number of fields, one can make sure that variable set events during creation do not affect the xmls

lock = Lock()
text_loading_lock = 0

# Create windows - canvas

current_toplevel = None
canvas_s = 655 # size of canvas in pixels in both directions
x_p, y_p, x, y = 0,0,0,0 # mouse coordinates in memory, x_p is the previous x
pressed = 0
pressedR = 0
rotateR = False
translateR = False
scaleR = False


# Image manipulation routines

def update_image():
    global root
    root.after(10,update_image)
    show_image(current_file)

def show_image(f):
    global bb_annotation, pi,canvas_s, zoom, x_image,y_image, current_image, current_image_resized, open_once, resize_once, button_image_paths, sprite,optimal_zoom,bb, circle, angle_bb, pA, pB, pSeg, segCounter
    global p1,p2,p3,p4

    w.delete(sprite)
    w.delete(bb)
    w.delete(circle)
    w.delete(p1)
    w.delete(p2)
    w.delete(p3)
    w.delete(p4)
    w.delete(pA)
    w.delete(pB)
    w.delete(pSeg)

    if open_once == False or current_image == None or not resize_once:

        try:
            current_image = Image.open(f)
            open_once = True
            cw, ch = current_image.size
            if cw >= ch:
                optimal_zoom = canvas_s*1.0/cw
            else:
                optimal_zoom = canvas_s*1.0/ch

            current_image_resized = current_image.resize((int(round(optimal_zoom*cw/(0.5**zoom))),int(round(optimal_zoom*ch/(0.5**zoom)))),Image.ANTIALIAS)
            pi = ImageTk.PhotoImage(current_image_resized)
            resize_once = True

        except:
            zoom = 0
            return
    else:

        cw, ch = current_image.size
        if cw >= ch:
                optimal_zoom = canvas_s*1.0/cw
        else:
                optimal_zoom = canvas_s*1.0/ch
        sprite = w.create_image(x_image+canvas_s/2, y_image+canvas_s/2, image=pi)

        if show_annotation and mode == 0 and abs(bb_annotation[2] - bb_annotation[0]) > 5 and abs(bb_annotation[3] - bb_annotation[1]) > 5:
            x1,y1 = reverse_zoomed_transform_origin(bb_annotation[0],bb_annotation[1], zoom, optimal_zoom, origin_center, x_image, y_image)
            x2,y2 = reverse_zoomed_transform_origin(bb_annotation[2],bb_annotation[3], zoom, optimal_zoom, origin_center, x_image, y_image)

            p1,p2,p3,p4 = draw_rectangle(x1,y1,x2,y2,angle_bb, w, draw_box_color)

            circle = w.create_oval((x1+x2)/2,(y1+y2)/2,(x1+x2)/2,(y1+y2)/2, outline="gray25",width = 3)
        
        if pointA != None and mode == 1 and show_annotation:
            
            p1 = reverse_zoomed_transform_origin(pointA[0],pointA[1], zoom, optimal_zoom, origin_center, x_image, y_image)
            dd = 10
            pA = w.create_oval((p1[0]-dd),(p1[1]-dd),(p1[0]+dd),(p1[1]+dd), outline="blue",width = 3)
        if pointB != None and mode == 1 and show_annotation:
      
            p1 = reverse_zoomed_transform_origin(pointB[0],pointB[1], zoom, optimal_zoom, origin_center, x_image, y_image)
            dd = 10
            pB = w.create_oval((p1[0]-dd),(p1[1]-dd),(p1[0]+dd),(p1[1]+dd), outline="red",width = 3)
        if segCounter == 2 and resize_once == True: 
            ppa = (pointA[0],pointA[1])
            ppb = (pointB[0],pointB[1])
            cw, ch = current_image.size
            ppa = (ppa[0] + cw / 2), (ppa[1] + ch / 2)
            ppb = (ppb[0] + cw / 2), (ppb[1] + ch / 2)
            segCounter = 0
            pic = current_image


def try_to_save(init_update=False):
    global vars,string_vars, current_file, angle_bb,bb_annotation, mac_right_click_drag

    if init_update:
        return

    if abs(bb_annotation[2] - bb_annotation[0]) < 5 or abs(bb_annotation[3] - bb_annotation[1]) < 5:
        bb_annotation = [0,0,0,0]
        angle_bb = 0

    # Iterate through all variables
    # obtain proper xml file and save everything, since there was a change
    # debug("Trying to save to xml")
    # Vars and StringVars should be saved to xml, this is only called if autosave was enabled

    # Image name, var fields, string_var fields
    myroot = ET.Element("Image")
    f =  os.path.splitext(current_file)[0]
    ET.SubElement(myroot,"ImageFileName").text = os.path.basename(f+".jpg")
    for label in OPTION_LABELS:
        true_label = label.replace(" ","")
        if "FIELD" in OPTION_NAMES[OPTION_LABELS.index(label)][0]:
            ET.SubElement(myroot,true_label).text = str(string_vars[(OPTION_LABELS.index(label)-len(OPTION_LABELS))].get())
        else:
            ET.SubElement(myroot,true_label).text = str(vars[OPTION_LABELS.index(label)].get())

    # Save the bbox annotation, but it has to be on local image coordinates, not scaled image coordinates.
    # bbox_annotation contains the scaled image coordinates, so we need a mapping from those to the local ones

    x1, y1 = reverse_zoomed_transform_origin(bb_annotation[0], bb_annotation[1],zoom, optimal_zoom, origin_center, x_image, y_image)
    x2, y2 = reverse_zoomed_transform_origin(bb_annotation[2], bb_annotation[3],zoom, optimal_zoom, origin_center, x_image, y_image)
    p1,p2,p3,p4 = find_points(x1,y1,x2,y2,angle_bb)

    # just find the 4 corner points of the image, and transform the points from global coordinates to local ones on the image by comparison
    # also save numbers when the box is rearranged

    if abs(bb_annotation[2] - bb_annotation[0]) > 5 and abs(bb_annotation[3] - bb_annotation[1]) > 5: # This is activated when the text widget is loaded
        # only save if annotation is big and meaningful

        p1 = zoomed_transform_origin(p1[0],p1[1],zoom, optimal_zoom, origin_center, x_image, y_image)
        p2 = zoomed_transform_origin(p2[0],p2[1],zoom, optimal_zoom, origin_center, x_image, y_image)
        p3 = zoomed_transform_origin(p3[0],p3[1],zoom, optimal_zoom, origin_center, x_image, y_image)
        p4 = zoomed_transform_origin(p4[0],p4[1],zoom, optimal_zoom, origin_center, x_image, y_image)
        cw, ch = current_image.size
        p1 = (p1[0]+cw/2),(p1[1]+ch/2)
        p2 = (p2[0]+cw/2),(p2[1]+ch/2)
        p3 = (p3[0]+cw/2),(p3[1]+ch/2)
        p4 = (p4[0]+cw/2),(p4[1]+ch/2)
        ET.SubElement(myroot,"BBox").text = "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f" % (p1[0],p1[1],p2[0],p2[1],p3[0],p3[1],p4[0],p4[1])
        ET.SubElement(myroot,"restore").text = "%.2f,%.2f,%.2f,%.2f,%.5f" % (bb_annotation[0],bb_annotation[1],bb_annotation[2],bb_annotation[3],angle_bb)
    else:
        # save None in the field
        ET.SubElement(myroot,"BBox").text = "None"
        ET.SubElement(myroot,"restore").text = "None"
        bb_annotation = [0,0,0,0]
        bb_angle = 0
        mac_right_click_drag = 1

    tree = ET.ElementTree(myroot)
    tree.write(f+".xml",encoding="utf-8", xml_declaration=True)

def selection(*args):
    global autosave
    if autosave:
        try_to_save()

def import_xml(xml_path):
    # Try to import from the xml path supplied
    # We need to construct vars and string vars from the fields
    global bb_annotation, angle_bb, rectangle_size, loading_text_widget, text_loading_lock, mac_right_click_drag
    e = ET.parse(xml_path).getroot()

    bb_annotation = [0,0,0,0]
    angle_bb = 0
    mac_right_click_drag = 0

    # Setting this to the number of fields in the application, so that the text_loading_lock tokens are consummed during the setting of the field variables
    # This way, during variable setting, the xml is not saved (with bad inialized variables)
    lock.acquire()
    text_loading_lock = 0
    for option in OPTION_NAMES:
        for name in option:
            if "FIELD" in name:
                text_loading_lock += 1
    lock.release()

    for atype in e:
        if atype.tag == "restore":
            if atype.text == "None":
                bb_annotation = [0,0,0,0]
                angle_bb = 0
                rectangle_size = (bb_annotation[2]-bb_annotation[0],bb_annotation[3]-bb_annotation[1])
                continue
            a1,a2,a3,a4,a5 = atype.text.split(",")
            bb_annotation = [int(round(float(a1))),int(round(float(a2))),int(round(float(a3))),int(round(float(a4)))]
            angle_bb = float(a5)

            rectangle_size = (bb_annotation[2]-bb_annotation[0],bb_annotation[3]-bb_annotation[1])

        for label in OPTION_LABELS:
            replaced_label = str(label)
            replaced_label = replaced_label.replace(" ","")
            if replaced_label == atype.tag:
                if "FIELD" in OPTION_NAMES[OPTION_LABELS.index(label)][0]:
                    string_vars[(OPTION_LABELS.index(label)-len(OPTION_LABELS))].set(atype.text)
                else:
                    vars[OPTION_LABELS.index(label)].set(atype.text)

def check_image_with_pil(path):
     try:
         Image.open(path)
     except IOError:
         return False
     return True

def ask(): # Open image file and see if xml exists
    global current_image, autosave, vars, current_file,zoom, open_once, x_image, y_image, pressed, bb_annotation, angle_bb, rectangle_size

    autosave = False
    open_once = False

    pressed = 0


    f = fd.askopenfilename()
    # Open zip file
    try:
        open = check_image_with_pil(f)
        if not open:
            debug("File is not an image file")
            return
        else:

            root.title(str(f))

            bb_annotation = [0,0,0,0]
            angle_bb = 0

            for i in range(1,7):
                vars[i].set("NONE")
            string_vars[0].set("None")

            rectangle_size = (1,1)

            debug("File has been opened")
    except:
        debug("File is not an image file")
        return

    current_file = f
    xml_path = os.path.splitext(f)[0]+".xml"
    if os.path.isfile(xml_path):
        m = tkMessageBox.showwarning(message="Associated annotations already exist for this image, further modifications will overwrite the file.")
        x_image = 0
        y_image = 0
        zoom = 0

        debug("XML exists, overwriting")
        autosave = True
        import_xml(xml_path)

    else:
        x_image = 0
        y_image = 0
        zoom = 0
        debug("XML doesn't exist")
        autosave = True

    debug("After importing image, autosave is "+str(autosave))


    open_once = False

################## Ribbon / Tools

def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def resize(s):
    global zoom,resize_once, x_image, y_image, canvas_s, optimal_zoom
    resize_once = False
    if s == "zoomin":
        zoom += 1
    if s == "zoomout":
        zoom -= 1
    if zoom < -5:
        zoom = -5
    if zoom > 4:
        zoom = 4
    if s == "center":
        zoom = 0
        x_image = 0
        y_image = 0
        cw, ch = current_image.size
        if cw >= ch:
            optimal_zoom = canvas_s*1.0/cw
        else:
            optimal_zoom = canvas_s*1.0/ch

def toolkit(event,i,button):
    global show_annotation, mode
    if i == 0:
        button.after(200,ask)
    elif i == 6:
        about()
    elif i == 5:
        mode = 1-mode
    elif i == 4:

        if show_annotation:
            root.config(cursor="arrow")
            button.configure(image=button_images[len(button_images)-1])
        else:
            button.configure(image=button_images[4])


        show_annotation = not show_annotation
    else:
        resize(button_image_paths[i])


###################################
# There are 3 coordinates systems
# a) Original image coordinates, to save in the xml
# b) scaled image coordinates, so that image fits in the screen completely in at least one direction
# c) normalized coordinates, offset so that 0,0 is in the center of the image instead and uses original image coordinates.
# This is as close as it gets to a proper coordinate system for the original image.
###################################
#
# canvas main events
#
###
origin_center = [canvas_s/2, canvas_s/2]

def onAnyPressed(e):
    global pressed
    pressed = 1

def onAnyReleased(e):
    global pressed
    pressed = 0

def onPressR(e):
    global pointA,pointB,segCounter,positive_scaling, pressedR, bb_annotation, x_image, y_image, rotateR, angle_bb, translateR, scaleR, horizontal_axis_scale, horizontal_axis_cursor, appropriate_rectangle_size

    if not show_annotation:
        return

    original_origin_center = list(origin_center)
    if mode == 0:

        pressedR = 1
        # Transform canvas into global coordinates
        ex, ey = zoomed_transform_origin(x, y,zoom, optimal_zoom, origin_center, x_image, y_image)
        cx = (bb_annotation[0] + bb_annotation[2]) / 2
        cy = (bb_annotation[1] + bb_annotation[3]) / 2
        re = rotate_transform(ex, ey, cx, cy, -angle_bb)  # transform point to unrotated coordinates to compare
        dx = re[0] - cx
        dy = re[1] - cy
        rads = math.atan2(-dy, dx)  # + angle_bb
        rads %= 2 * math.pi
        degs = math.degrees(rads)
        bal = math.degrees(math.atan2(rectangle_size[1],rectangle_size[0])) # 0 - 90 degrees, box angle limit 

        xw, yh = dist_anchor(ex,ey,(bb_annotation[0]+bb_annotation[2])/2,(bb_annotation[1]+bb_annotation[3])/2, angle_bb)
        dist = 0
        if 0 < degs < bal or 180 - bal < degs < 180 + bal or 360 - bal < degs < 360:
            horizontal_axis_cursor = True
            dist = xw
            positive_scaling = True
            if 90 < degs < 270:
                positive_scaling = False
        else:
            horizontal_axis_cursor = False
            positive_scaling = True
            dist = yh
            if 180 < degs:
                positive_scaling = False

        appropriate_rectangle_size = 0
        if horizontal_axis_cursor:
            appropriate_rectangle_size = rectangle_size[0]
            dist = xw 
        else:
            appropriate_rectangle_size = rectangle_size[1]
            dist = yh

        if  dist < appropriate_rectangle_size*(1.0/6): # scales properly
            rotateR = True
            root.config(cursor="circle")
        elif dist < appropriate_rectangle_size*(2.0/6): # scales properly
            translateR = True
            root.config(cursor="dotbox")
        elif dist < appropriate_rectangle_size/2.0: # scales properly
            scaleR = True
            root.config(cursor="diamond_cross")
            

            horizontal_axis_scale = horizontal_axis_cursor

        if not rotateR and not translateR and not scaleR:
            angle_bb = 0
            bb_annotation = [ex,ey,ex,ey] # this will make the bb_annotation save in the xml as None

    else:
        ex,ey = zoomed_transform_origin(e.x,e.y,zoom, optimal_zoom, origin_center, x_image, y_image)
        if segCounter == 0:
            pointA = (ex,ey)
            segCounter += 1
        elif segCounter == 1:
            pointB = (ex,ey)
            segCounter += 1

def onReleaseR(e):
    global pressedR, bb_annotation, rotateR, translateR,scaleR, rectangle_size

    if not show_annotation:
        return

    if mode == 0:
        rotateR = False
        translateR = False
        scaleR = False
        root.config(cursor="arrow")
        if bb_annotation[3] < bb_annotation[1]:
            bb_annotation = [bb_annotation[0],bb_annotation[3],bb_annotation[2],bb_annotation[1]]
        if bb_annotation[2] < bb_annotation[0]:
            bb_annotation = [bb_annotation[2],bb_annotation[1],bb_annotation[0],bb_annotation[3]]
        rectangle_size = (bb_annotation[2]-bb_annotation[0]),(bb_annotation[3]-bb_annotation[1])
        pressedR = 0

        if autosave:
            try_to_save()

def left_canvas(event):
    root.config(cursor="arrow")

def xy_motion(event):
    global x,y,x_p,y_p, x_image, y_image, bb_annotation, angle_bb,rectangle_size,horizontal_axis_cursor, positive_scaling, appropriate_rectangle_size
    x, y = event.x, event.y

    if pressed:
        if x-x_p != 0:
            x_image += x-x_p
        if y-y_p != 0:
            y_image += y-y_p

    ex, ey = zoomed_transform_origin(x,y, zoom, optimal_zoom,origin_center, x_image, y_image)
    cx = (bb_annotation[0] + bb_annotation[2]) / 2
    cy = (bb_annotation[1] + bb_annotation[3]) / 2
    re = rotate_transform(ex, ey, cx, cy, -angle_bb) # transform point to unrotated coordinates to compare
    dx = re[0] - cx
    dy = re[1] - cy
    rads = math.atan2(-dy, dx) #+ angle_bb
    rads %= 2 * math.pi

    degs = math.degrees(rads)
    bal = math.degrees(math.atan2(rectangle_size[1],rectangle_size[0])) # 0 - 90 degrees, box angle limit 
    xw, yh = dist_anchor(ex,ey,(bb_annotation[0]+bb_annotation[2])/2,(bb_annotation[1]+bb_annotation[3])/2, angle_bb)
    dist = 0

    if 0 < degs < bal or 180 - bal < degs < 180 + bal or 360 - bal < degs < 360:
        horizontal_axis_cursor = True
        dist = xw
    else:
        horizontal_axis_cursor = False
        dist = yh

    meaningful_annotation = False
    for i in bb_annotation:
        if i != 0:
            meaningful_annotation = True

    if horizontal_axis_cursor:
        appropriate_rectangle_size = rectangle_size[0]
        dist = xw 
    else:
        appropriate_rectangle_size = rectangle_size[1]
        dist = yh

    if show_annotation and mode == 0 and current_image != None and meaningful_annotation:
        if not rotateR and not translateR and not scaleR:

            ex, ey = zoomed_transform_origin(x, y, zoom, optimal_zoom, origin_center, x_image, y_image)
            cx = (bb_annotation[0] + bb_annotation[2]) / 2
            cy = (bb_annotation[1] + bb_annotation[3]) / 2

            if dist < appropriate_rectangle_size*(1.0/6): # scales properly
                root.config(cursor="circle")
            elif dist < appropriate_rectangle_size*(2.0/6): # scales properly
                root.config(cursor="dotbox")
            elif dist < appropriate_rectangle_size/2.0: # scales properly
                root.config(cursor="diamond_cross")
            else:
                root.config(cursor="arrow")

        if pressedR and not rotateR and not translateR and not scaleR:
            xx,yy = zoomed_transform_origin(x,y,zoom, optimal_zoom, origin_center, x_image, y_image)
            bb_annotation = [bb_annotation[0],bb_annotation[1],xx,yy]
        elif rotateR:
            angle_bb += 0.01*(x-x_p)
            while angle_bb > 2*math.pi or angle_bb < 0:
                if angle_bb > 2*math.pi:
                    angle_bb -= 2*math.pi
                if angle_bb < 0:
                    angle_bb += 2*math.pi
        elif translateR:
            xa,ya  = ((x-x_p)*(0.5**zoom)/optimal_zoom,(y-y_p)*(0.5**zoom)/optimal_zoom)
            bb_annotation = [bb_annotation[0]+xa,bb_annotation[1]+ya,bb_annotation[2]+xa,bb_annotation[3]+ya]
        elif scaleR:
            rectangle_size = (bb_annotation[2]-bb_annotation[0]),(bb_annotation[3]-bb_annotation[1])

            xc = x-x_p
            yc = y-y_p



            # transform xc, yc to angle_bb coordinates, so that the amount of change depends on the rotation of the box

            s, c = math.sin(-angle_bb), math.cos(-angle_bb)
            znew = xc * c - yc * s
            wnew = xc * s + yc * c

            xc_transformed = znew*(0.5)**zoom/optimal_zoom
            yc_transformed = wnew*(0.5)**zoom/optimal_zoom

            if horizontal_axis_scale:
                if positive_scaling:

                    alpha = xc_transformed*(math.cos(angle_bb)-1)/2
                    beta = alpha+xc_transformed
                    gamma = xc_transformed*math.sin(angle_bb)/2

                    bb_annotation[0] += alpha
                    bb_annotation[2] += beta
                    bb_annotation[1] += gamma
                    bb_annotation[3] += gamma
                else:
                    alpha = xc_transformed*(math.cos(angle_bb)-1)/2
                    beta = alpha+xc_transformed
                    gamma = xc_transformed*math.sin(angle_bb)/2

                    bb_annotation[0] += beta
                    bb_annotation[2] += alpha
                    bb_annotation[1] += gamma
                    bb_annotation[3] += gamma
            else:
                if positive_scaling:
                    alpha = yc_transformed*(math.cos(angle_bb)-1)/2
                    beta = alpha+yc_transformed
                    gamma = -yc_transformed*math.sin(angle_bb)/2

                    bb_annotation[0] += gamma
                    bb_annotation[2] += gamma
                    bb_annotation[1] += beta
                    bb_annotation[3] += alpha
                else:
                    alpha = yc_transformed*(math.cos(angle_bb)-1)/2
                    beta = alpha+yc_transformed
                    gamma = -yc_transformed*math.sin(angle_bb)/2
                    bb_annotation[0] += gamma
                    bb_annotation[2] += gamma
                    bb_annotation[1] += alpha
                    bb_annotation[3] += beta

            if bb_annotation[3] < bb_annotation[1]:
                bb_annotation = [bb_annotation[0],bb_annotation[3],bb_annotation[2],bb_annotation[1]]
            if bb_annotation[2] < bb_annotation[0]:
                bb_annotation = [bb_annotation[2],bb_annotation[1],bb_annotation[0],bb_annotation[3]]
    x_p = x
    y_p = y

## End of tkinter event section

### GUI creation

l1 = tk.Label(root)
l1.pack(pady=0,fill=tk.X)

frame_canvas = tk.Frame(l1,width=300, height=800,  colormap="new", relief=tk.SUNKEN ,borderwidth =4)
frame_canvas.pack(side=tk.LEFT,padx=20)

w = tk.Canvas(frame_canvas, width=canvas_s, height=canvas_s)

# Sunkable button, annotation on/off

# Read configurations
f=open("../settings.conf","r")
configurations = f.readlines()
if "mouse-1" in configurations[0]:
    binder = ["<ButtonPress-1>","<ButtonRelease-1>"]
if "mouse-2" in configurations[0]:
    binder = ["<ButtonPress-2>","<ButtonRelease-2>"]
if "mouse-3" in configurations[0]:
    binder = ["<ButtonPress-3>","<ButtonRelease-3>"]

if "mouse-1" in configurations[1]:
    binder2 = ["<ButtonPress-1>","<ButtonRelease-1>"]
if "mouse-2" in configurations[1]:
    binder2 = ["<ButtonPress-2>","<ButtonRelease-2>"]
if "mouse-3" in configurations[1]:
    binder2 = ["<ButtonPress-3>","<ButtonRelease-3>"]

if "white" or "grey" or "black" in configurations[2]:
    draw_box_color = configurations[2].strip('\n')


w.pack()
w.bind('<Motion>', xy_motion)
w.bind(binder[0], onAnyPressed)
w.bind(binder[1], onAnyReleased)
w.bind(binder2[0],onPressR)
w.bind(binder2[1],onReleaseR)
w.bind("<Leave>", left_canvas)
w.create_rectangle(0, 0, canvas_s, canvas_s, fill="black")
w.pack_propagate(False)

def createButton(i,canvas):
    global button_images
    true_size_button = 49
    if button_image_paths[i] == "label":
        label = tk.Label(canvas,text="Autosave is enabled",pady=6)
        label.pack(pady=0)
        '''if linux_flag:
            canvas.create_window(87*i+10-100,10,anchor=tk.NW,window=label)
        else:
            canvas.create_window(87*i+10-100,10, anchor=tk.NW,window=label)'''
        return

    if button_image_paths[i] == "annotation_off":
        try:
            img = Image.open("../utils/"+button_image_paths[i]+".jpg")
        except:
            img = Image.open("../utils/"+button_image_paths[i]+".png")
        button_images.append(ImageTk.PhotoImage(img.resize((25,25),Image.ANTIALIAS)))
        return

    button = tk.Button(canvas)
    try:
        img = Image.open("../utils/"+button_image_paths[i]+".jpg")
    except:
        img = Image.open("../utils/"+button_image_paths[i]+".png")

    img = img.resize((25,25),Image.ANTIALIAS)
    ip = ImageTk.PhotoImage(img)
    button_images.append(ip)
    button.config(image=ip)
    button.pack(padx=0,pady=1,fill=tk.NONE,side=tk.LEFT,ipadx=0,ipady=0)
    #canvas.create_window(true_size_button*i+10,10, anchor=tk.NW, window=button)
    button.bind("<Button-1>",lambda event,options=i,myself=button: toolkit(event,options,myself))

frame_in_canvas = tk.Frame(w,width=canvas_s-50-1, height=25,  colormap="new" , relief=tk.GROOVE,borderwidth =4) # Right side frame
frame_in_canvas.pack(pady=5)

for i in range(len(button_image_paths)):
    createButton(i,frame_in_canvas)

frame = tk.Frame(l1,width=300, height=300,  colormap="new", relief=tk.RIDGE ,borderwidth =4) # Right side frame
frame.pack(pady=30,padx=10,fill=tk.BOTH)

# Hover effect
popup_canvas = None

# Popup selection window
popup_images = None

def update(selection,option):
    # Close box
    global current_toplevel, vars,autosave
    current_toplevel.destroy()
    current_toplevel = None
    vars[option].set(OPTION_NAMES[option][selection])
    if autosave:
        try_to_save()

def popup_command(selection,options):
    # Update the option
    update(selection,options)

def closed_popup():
    global current_toplevel
    current_toplevel.destroy()
    current_toplevel = None

def fce(myX):
    def pop(x_option=myX): # With this wrapper we have variable arguments for pop
        global popup_images, popup_canvas, current_toplevel

        true_width = 155
        true_height = 154.5
        popup_images = []
        toplevel = tk.Toplevel()

        toplevel.resizable(width=False, height=False)
        current_toplevel = toplevel
        toplevel.protocol("WM_DELETE_WINDOW", closed_popup)
        # We need 150x150 per image. First we obtain the length of images from the option names
        n = len(OPTION_NAMES[x_option])
        # We want a grid that has at most 6 entries, thus if the length is larger than 8, we set wn to six
        wn = min(8,n)
        hn = ((n-1)//8)+1
        # Thus if we have 8 images only then do we have another line
        w = true_width*wn # width for the Tk root
        h = true_height*hn # height for the Tk root

        h += 6

        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws//2) - (w//2)
        y = (hs//2) - (h//2)

        toplevel.geometry('%dx%d+%d+%d' % (w, h, x, y))
        popup_frame = tk.Frame(toplevel, width=w, height=h, bg="grey", colormap="new", relief=tk.FLAT, borderwidth=4)
        popup_frame.pack()
        #w1.create_rectangle(0, 0, w/2, h, fill="gray")
        #w1.create_rectangle(w/2, 0, w, h, fill="black")

        # Create all the images in the locations that are appropriate. wn and hn decide length and height
        for xx in range(int(wn)):
            for yy in range(int(hn)):
                if xx+wn*yy >= n:
                    break

                # If in certain group, append 2 to certain category
                if (x_option == 3 and str(OPTION_NAMES[x_option][xx+wn*yy]) == "CORDATE"):
                    img = Image.open("../labels/"+str(OPTION_NAMES[x_option][xx+wn*yy]+"2.jpg"))
                elif (x_option == 3 and str(OPTION_NAMES[x_option][xx+wn*yy]) == "ROUNDED"):
                    img = Image.open("../labels/"+str(OPTION_NAMES[x_option][xx+wn*yy]+"2.jpg"))
                elif (x_option == 4 and str(OPTION_NAMES[x_option][xx+wn*yy]) == "TRUNCATE"):
                    img = Image.open("../labels/"+str(OPTION_NAMES[x_option][xx+wn*yy]+"2.jpg"))
                else:
                    img = Image.open("../labels/"+str(OPTION_NAMES[x_option][xx+wn*yy]+".jpg"))

                # If option name is the pre-selected one, put a nice red box around it


                img = img.resize((150,150),Image.ANTIALIAS)
                ip = ImageTk.PhotoImage(img)
                popup_images.append(ip)
                if OPTION_NAMES[x_option][xx+wn*yy] ==  vars[x_option].get():
                    label = tk.Label(popup_frame, image=ip, bg="red")
                else:
                    label = tk.Label(popup_frame, image=ip)

                label.grid(row=yy,column=xx)
                label.bind("<Button-1>",lambda event,options=x_option,e=xx+wn*yy: popup_command(e,options))
                #createToolTip(label, OPTION_NAMES[x_option][xx+wn*yy]) # to remove tooltips

    return pop

def enter_field(name,index, mode, sv):
    global autosave, loading_text_widget, text_loading_lock

    lock.acquire()
    #debug("Trying to save from text entry capture, autosave is "+str(autosave))
    if autosave and not loading_text_widget:
        try_to_save(init_update=(text_loading_lock != 0)) # make false only if the text has been changed by the user, not the application !!!!
    if text_loading_lock > 0:
        text_loading_lock -= 1

    lock.release()

#### Help - About, popup

about_text = "Steps for annotating an image\n" \
             "1) Using the 'Open' button from the top left corner, import your image file\n" \
             "2) Either select values from the drop down menus to the right, or use the '+' symbol\n" \
             "to open a window for visual selection of the leaf features\n" \
             "3) Optionally insert contributor and species name\n" \
             "4) The autosave feature is enabled, meaning that any changes are automatically saved\n\n" \
             "Created by Dimitrios Trigkakis in association with Justin Preece and Pankaj Jaiswal"

def about():
    global popup_images, popup_canvas, current_toplevel, about_text

    w = 512 # approximate values for screen location after taking screen size into account
    h = 256

    toplevel = tk.Toplevel()

    toplevel.resizable(width=False, height=False)

    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    w_about = root.winfo_width()
    h_about = root.winfo_height()

    toplevel.geometry('%dx%d+%d+%d' % (w_about/2, h_about/4, x, y))

    popup_frame = tk.Frame(toplevel,  bg="grey", colormap="new", relief=tk.FLAT, borderwidth=4)
    popup_frame.pack(expand=True, fill="both")
    w = tk.Label(popup_frame, text=about_text,borderwidth = 5)
    w.pack(expand=True,fill="both")


################## Fields
labels = []
buttons = []
vars = []
string_vars = []

def field(event,option):
    pass
    '''global autosave
    debug("Trying to save from text entry capture, autosave is "+str(autosave))
    if autosave:
        try_to_save()'''

for i in range(9):#len(OPTIONS)):

    myframe = tk.Frame(frame, width=300, height=800,  colormap="new", relief=tk.FLAT, borderwidth=4)
    myframe.pack(pady=0, fill=tk.BOTH)
    label_part = tk.Label(myframe,  text=OPTION_LABELS[i],font=tkFont.Font(family="Calibri", size=12))
    label_part.pack()

    if "FIELD" in OPTION_NAMES[i][0]:
        sv = tk.StringVar()
        sv.set("None") # default value
        sv.trace("w", lambda name, index, mode, sv=sv: enter_field(name,index, mode,sv))
        string_vars.append(sv)
        e = tk.Entry(myframe,textvariable=sv)
        e.bind("<Return>",lambda event,field_option=i:field(event,field_option))
        e.pack(pady=5)
        # Create a text field
    else:
        var = tk.StringVar(root)
        var.set(OPTION_NAMES[i][0]) # default value
        vars.append(var)
        args_1 = OPTION_NAMES[i]
        myframe_field = tk.Frame(myframe, width=300, height=800,  colormap="new", relief=tk.FLAT, borderwidth=4)
        myframe_field.pack(pady=0, fill=tk.Y)

        r = tk.OptionMenu(myframe_field, var, *(args_1), command = selection)
        width_frame = 0
        if linux_flag:
            width_frame = 22
        else:
            width_frame = 25

        r.config(width=width_frame,height = 1,font=tkFont.Font(family="Calibri", size=11))
        r.pack(side=tk.LEFT)
        if i != 0:
            b = tk.Button(myframe_field, text="+", command=fce(i), width=2, height = 1)
            b.pack(side=tk.RIGHT)

#### Finalize window

root.after(30,update_image)
root.resizable(width=False, height=False)
root.title("")

root.mainloop() # starts the mainloop
