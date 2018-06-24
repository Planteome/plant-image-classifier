import math

def find_points(x1,y1,x2,y2,angle):
    xc = (x1+x2)/2
    yc = (y1+y2)/2

    p1x,p1y = rotate_transform(x1,y1,xc,yc,angle)
    p2x,p2y = rotate_transform(x1,y2,xc,yc,angle)
    p3x,p3y = rotate_transform(x2,y2,xc,yc,angle)
    p4x,p4y = rotate_transform(x2,y1,xc,yc,angle)

    return (p1x,p1y),(p2x,p2y),(p3x,p3y),(p4x,p4y)

def draw_rectangle(x1,y1,x2,y2,angle, w, color):
    xc = (x1+x2)/2
    yc = (y1+y2)/2

    p1x,p1y = rotate_transform(x1,y1,xc,yc,angle)
    p2x,p2y = rotate_transform(x1,y2,xc,yc,angle)
    p3x,p3y = rotate_transform(x2,y2,xc,yc,angle)
    p4x,p4y = rotate_transform(x2,y1,xc,yc,angle)

    p1 = w.create_line(p1x,p1y,p2x,p2y, width = 1,fill=color)
    p2 = w.create_line(p2x,p2y,p3x,p3y, width = 1,fill=color)
    p3 = w.create_line(p3x,p3y,p4x,p4y, width = 1,fill=color)
    p4 = w.create_line(p4x,p4y,p1x,p1y, width = 1,fill=color, dash=(3,3))

    #dist = -20
    #x1 += dist
    #x2 -= dist

    #xc = (x1+x2)/2
    #yc = (y1+y2)/2
    #p1xB,p1yB = rotate_transform(x1,y1,xc,yc,angle)
    #p2xB,p2yB = rotate_transform(x1,y2,xc,yc,angle)

    #line = w.create_line(p1xB, p1yB, p2xB, p2yB, fill="red", dash=(4, 4))
    #line = w.create_line(p1xB, p1yB, p2xB, p2yB, fill="red", dash=(4, 4))
    #line = w.create_line(p1xB, p1yB, p2xB, p2yB, fill="red", dash=(4, 4))

    return p1,p2,p3,p4

def transform_origin(x,y, origin_center, x_image, y_image): # take mouse coordinates and transform them to proper coordinate offsets
    x_new = x-origin_center[0]-x_image
    y_new = y-origin_center[1]-y_image
    return x_new, y_new

def reverse_transform_origin(x,y, origin_center, x_image, y_image):
    x_new = x+origin_center[0]+x_image
    y_new = y+origin_center[1]+y_image
    return x_new, y_new

def zoomed_transform_origin(x,y, zoom, optimal_zoom, origin_center, x_image, y_image):
    ox,oy = transform_origin(x,y, origin_center, x_image, y_image)
    return ox*(0.5**zoom)/optimal_zoom,(0.5**zoom)*oy/optimal_zoom

def reverse_zoomed_transform_origin(x,y, zoom, optimal_zoom, origin_center, x_image, y_image):
    ox,oy = x*optimal_zoom/(0.5**zoom),y*optimal_zoom/(0.5**zoom)
    ox,oy = reverse_transform_origin(ox,oy, origin_center, x_image, y_image)
    return ox,oy

def rotate_transform(x,y,c_x,c_y,a):
    # rotate x,y around center c by a radians
    s = math.sin(a)
    c = math.cos(a)
    x -= c_x
    y -= c_y
    xnew = x*c - y*s + c_x
    ynew = x*s + y*c + c_y
    return xnew,ynew


def dist_anchor(x_anchor,y_anchor,z,w, angle_bb): # x,y is the anchor point

    # convert second point, z, w by rotating around the first point (anchor)
    s,c = math.sin(-angle_bb),math.cos(-angle_bb)
    z -= x_anchor
    w -= y_anchor
    znew = z*c - w*s
    wnew = z*s + w*c
    z = znew+x_anchor
    w = wnew+y_anchor
    return abs(x_anchor-z),abs(y_anchor-w)
