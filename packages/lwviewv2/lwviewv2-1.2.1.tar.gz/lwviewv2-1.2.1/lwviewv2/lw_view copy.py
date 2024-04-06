# 5-6/22: major rework, on the fly slice interpolation
#   handle resize requests 
#
# 2/23/22: version 1.0 cleaned up naming, improved window level interface
# Todo
# change udate strategy to use 'canvas delete all'?
#
# smarter initial size
# resize mechanism
# recover from abnormal exit
###########################################################################

# Implements a minimalistic lightweight viewer for 3d volumes.
# See lw_view-doc.txt for info

import numpy as np
import platform
import scipy.ndimage as spndi
import tkinter as tk
from PIL import Image
from PIL import ImageTk
import lwview.lw_image as lwi
import sys

# creates a viewer object

class LwView:
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            print('nothing to display?')
            return
        # hook for 'command line' call back
        self.cmdhook_fun = None
        if 'cmdhook' in kwargs:
            self.cmdhook_fun = kwargs['cmdhook']
            del kwargs['cmdhook']
        # timeout feature
        self.timeout = 1000000 # quarter seconds
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout'] * 10
            del kwargs['timeout']
        # auto_size feature, default is to no do it
        self.do_auto_size = False
        if 'auto_size' in kwargs:
            self.do_auto_size = kwargs['auto_size']
            del kwargs['auto_size']
        #
        self.root = tk.Tk()
        self.root.title('Lightweight Viewer')
        self.exiting = False 
        def destroy_callback():
            self.exiting = True
            self.root.update() # call remaining stuff in queue
        self.root.protocol('WM_DELETE_WINDOW', destroy_callback)
        # build a frame and install the multi lw view widget
        self.frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.frame.grid()
        ####################################################
        # infrastructure for detecting user-initiated resizes driven by mouse
        # based on a state machine with 2 states: 
        #    'ready-and-waiting' and 'resize-pending'
        # uses an iterrupt driven clock
        self.resize_state = 'ready-and-waiting'
        self.last_resize_event_ticks = 1 
        # 
        self.ticks_at_resize = 1000000
        self.ticks = 0
        def clock():
            if self.exiting or self.ticks > self.timeout:   # don't reschedule
                self.exit()    # exit mainloop
                return
            self.ticks += 1
            # self.root.after(100, clock) # 1/10 sec
            # self.root.after(50, clock) # 1/20 sec
            # autosize feature
            if self.do_auto_size and self.ticks > 3:
                screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
                self.MLwVw.resize(self.old_frame_w, self.old_frame_h, screen_w, screen_h )
                self.do_auto_size = False
                self.ticks_at_resize = self.ticks
            # wait for things to settle down, then snap the outer window to just hold the contents
            if self.ticks > self.ticks_at_resize + 1:
                self.root.geometry('{}x{}'.format(self.frame.winfo_width(), self.frame.winfo_height()))
                self.ticks_at_resize = 1000000                
            self.old_frame_w, self.old_frame_h = self.frame.winfo_width(), self.frame.winfo_height()
            # if we are set to do resize (mouse is moving?), wait for movement to end, then do it
            if self.resize_state == 'resize-pending' and self.ticks - self.last_resize_event_ticks > 2:
                # if frame size has changed, do the resize
                if self.old_frame_w !=  self.resize_w or self.old_frame_h != self.resize_h:
                    self.MLwVw.resize(self.old_frame_w, self.old_frame_h, self.resize_w, self.resize_h)
                    self.ticks_at_resize = self.ticks
                self.resize_state = 'ready-and-waiting'
            self.root.after(100, clock) # 1/10 sec                
        # 
        clock() # start the clock
        #
        def handle_resize_events(event):
            self.resize_w, self.resize_h = event.width, event.height
            if self.resize_state == 'ready-and-waiting':
                if (event.widget == self.frame.winfo_toplevel() 
                    # and self.ticks - self.last_resize_event_ticks > 0):
                    and self.ticks - self.last_resize_event_ticks > 1):
                    # things have 'settled down' ?, (and we have received a resize event)
                    self.resize_state = 'resize-pending'
            self.last_resize_event_ticks = self.ticks
        self.root.bind("<Configure>", handle_resize_events)
        ####################################################
        # create a widget like object that can hold one or more volume displays
        self.MLwVw = MultiLwViewW(args, self.frame, self.root, **kwargs)
        # build command entry widget if wanted
        if self.cmdhook_fun:
            self.prompt = '? '  # initial value of command entry prompt
            self.cmd_str = tk.StringVar()
            self.cmd_str.set(self.prompt)
            self.entryW = tk.Entry(self.frame, textvariable=self.cmd_str)
            self.entryW.grid(row=1)
            # connect command hook activation to the return key
            self.root.bind('<Return>', self.return_key_wrapper)
        # start on top of other applications
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.after_idle(self.root.attributes,'-topmost',False)

        self.root.mainloop()
        # if a command called exit, then we need to destroy the root
        self.root.destroy()
        print('bye!')

    # detect typed 'commends' (if needed)
    def return_key_wrapper(self, event):
        s = self.cmd_str.get()
        # command hook function is called with LwView object as first arugment, and
        # entered command string as second argument, with prompt stripped.
        # the entry widget prompt string is set to
        # the return value of the command line hook function
        self.prompt = self.cmdhook_fun(self, s[len(self.prompt):])
        self.cmd_str.set(self.prompt) # clear and redisplay prompt
        self.entryW.icursor(len(self.prompt)) # cursor to end of prompt

    def exit(self):
        self.exiting = True
        self.root.quit() # cause exit of main loop, can call from command hook func.

# a widget-like object that holds one or more lightweight view 
# widget-like objects
# parent is the parent widget
# synchronization of foci accross multiple displays is accomplished
# by a hook function called "focus_hook", which may be called when
# a tp display changes its focus due to a mouse hit
#   the hook will insure that the focus is changed on all displays
# mm_per_pixel: millimeters per pixel
class MultiLwViewW:
    def __init__(self, input_images, parent, root, mm_per_pixel=1.0, lock_focus=True, ncols=1024, reticles=False, interpolation_order=1):
        self.mm_per_pixel = mm_per_pixel
        self.focus_is_locked = lock_focus
        parent.grid()
        self.n_frames = len(input_images)
        self.frames = []
        self.lw_view_wgts = []
        for i in range(self.n_frames):
            self.frames.append( tk.Frame(parent, bd=2, relief=tk.RIDGE))
            row, col = divmod(i, ncols)
            self.frames[i].grid(row=row, column=col)
            self.lw_view_wgts.append( LwViewW(input_images[i], self.frames[i], root, mm_per_pixel, reticles, interpolation_order))

        if self.n_frames > 1: # and lock_focus:
            def focus_hook(x,y,z):
                if self.focus_is_locked:
                    # should not be called on caller?
                    for i in range(self.n_frames):
                        self.lw_view_wgts[i].update_focus_xyz(x, y, z, call_hook=False)
            for i in range(self.n_frames):
                self.lw_view_wgts[i].focus_hook = focus_hook
            # intially sync focus  (if locked)
            if lock_focus:
                focus_0 = self.lw_view_wgts[0].get_focus_xyz()
                for i in range(1, self.n_frames):
                    self.lw_view_wgts[i].update_focus_xyz(focus_0[0], focus_0[1], focus_0[2], call_hook=False)

    def lock_the_foci(self):
        self.focus_is_locked = True

    def unlock_the_foci(self):
        self.focus_is_locked = False
    # handle a user initiated resize request
    def resize(self, old_w, old_h, resize_w, resize_h):
        # arguments are overall windows size (content size is smaller by padding)
        pad = 5 # was 4
        old_aspect_ratio = (old_w - pad) / (old_h - pad)
        resize_aspect_ratio = (resize_w - pad) / (resize_h - pad)
        if resize_aspect_ratio > old_aspect_ratio:
            new_h = resize_h # + pad
            new_w = (resize_h * old_aspect_ratio) # + pad
        else:
            new_w = resize_w # + pad
            new_h = (resize_w / old_aspect_ratio) # + pad
        # ratio = new_h / old_h
        ratio = (new_h - pad)/ (old_h - pad)
        # print('RATIO: {}:'.format(ratio))
        resize_mm_per_pixel = self.mm_per_pixel / ratio
        self.mm_per_pixel = resize_mm_per_pixel
        for i in range(self.n_frames):
            self.lw_view_wgts[i].update_mm_per_pixel(resize_mm_per_pixel)

# a widget that holds an lightweight view of a volumetic image
# image layout: 
#  axi info
#  cor sag
# useful methods:
#    update_focus_ijk(...)
#    update_focus_xyz(...)
#
# parent is the parent 'widget'
class LwViewW:
    def __init__(self, input_img, parent, root, mm_per_pixel, reticles, interpolation_order):
       self.focus_hook = False
       self.show_green_dot = True
       self.show_reticles = reticles
       self.interpolation_order=interpolation_order
       self.input_img = input_img  
       self.root = root
       # make a virtual image that has scaled identity affine
       # slices are taken from the virtual image by interpolating from
       # input_img
       self.rect_v_img = lwi.make_rectified_container(self.input_img, mm_per_pixel)
       self.image_slicer = VirtualImageSlicer(self.rect_v_img, self.input_img, self.interpolation_order)       
       #
       self.display_name = input_img.display_name
       self.n_i, self.n_j, self.n_k = self.rect_v_img.shape
       #
       self.intensity_max = np.amax(self.input_img.data)
       self.intensity_min = np.amin(self.input_img.data)
       # set initial window and level
       self.window = self.intensity_max - self.intensity_min
       self.level = (self.intensity_max + self.intensity_min) / 2.0
       # 
       self.i_px_mm = self.rect_v_img.voxel_displacements[0]
       self.j_px_mm = self.rect_v_img.voxel_displacements[1]
       self.k_px_mm = self.rect_v_img.voxel_displacements[2]
       # for the images that get displayed
       # if mm_per_pixel is not specified, default to one pixel per input image pixel
       if mm_per_pixel:
           self.mm_per_pixel = mm_per_pixel
       else:
           self.mm_per_pixel = min(self.i_px_mm, self.j_px_mm, self.k_px_mm)
       # image sizes in mm
       self.i_img_width_mm = self.n_i * self.i_px_mm
       self.j_img_width_mm = self.n_j * self.j_px_mm
       self.k_img_width_mm = self.n_k * self.k_px_mm
       # image sizes in pixels, integer valued
       self.i_width_px = int(self.i_img_width_mm / self.mm_per_pixel)
       self.j_width_px = int(self.j_img_width_mm / self.mm_per_pixel)
       self.k_width_px = int(self.k_img_width_mm / self.mm_per_pixel)
       # set the focus coords to the center initially
       self.focus_i, self.focus_j, self.focus_k = round(self.n_i/2), round(self.n_j/2), round(self.n_k/2)
       #
       self.update_images()
       self.lw_widget = self.make_widgets(parent)

    def get_focus_xyz(self):   
        return self.rect_v_img.ijk_to_xyz(self.focus_i, self.focus_j, self.focus_k)

    def update_images(self):
        # get three orthogonal slilces from the virtual image
        # interpolating from the input image
        jk_slice, ik_slice, ij_slice = self.image_slicer.get_slices((self.focus_i, self.focus_j, self.focus_k))        
        # orient the slices for display radiological convention
        # previously was neurological, monkey with typewriter...
        self.axi_section = np.flip(np.flip(np.transpose(ij_slice), 0), 1)
        self.cor_section = np.flip(np.flip(np.transpose(ik_slice), 0), 1)
        self.sag_section = np.flip(np.flip(np.transpose(jk_slice), 0), 1)
        # transform the intensities according to window level so that the lowest corresponds to 0 and the max to 255
        self.axi_section_t = (((self.axi_section - self.level) / self.window) + .5) * 255.0
        self.cor_section_t = (((self.cor_section - self.level) / self.window) + .5) * 255.0
        self.sag_section_t = (((self.sag_section - self.level) / self.window) + .5) * 255.0
        # construct the PIL images, which are the required type for construction of Tk images
        self.axi_pilimg = Image.fromarray(self.axi_section_t)
        self.cor_pilimg = Image.fromarray(self.cor_section_t)
        self.sag_pilimg = Image.fromarray(self.sag_section_t)

    def make_widgets(self, parent):
        ###   convert the PIL images to Tk images
        self.axi_tk_img = ImageTk.PhotoImage(self.axi_pilimg)
        self.cor_tk_img = ImageTk.PhotoImage(self.cor_pilimg)
        self.sag_tk_img = ImageTk.PhotoImage(self.sag_pilimg)
        ### a container for the canvas widgets and info panel
        # self.frame = tk.Frame(parent, bd=2, relief=tk.RIDGE, bg='black')
        self.frame = tk.Frame(parent, bd=5, relief=tk.RIDGE, bg='black')
        self.frame.grid() 
        #
        ### make canvas widget and hook up callbacks
        self.canvas_axi = tk.Canvas(self.frame, bd=0, width=self.axi_tk_img.width(), height=self.axi_tk_img.height())
        self.canvas_axi.grid(row=0, column=0)
        self.canv_img_axi = self.canvas_axi.create_image(0,0, image=self.axi_tk_img,anchor='nw')
        self.canvas_axi.bind('<Button-1>', self.axi_callback)
        self.canvas_axi.bind('<Shift-Button-1>', self.axi_jog_callback)
        if sys.platform == 'darwin':
            self.canvas_axi.bind('<Button-2>', self.wl_callback)
        else:
            self.canvas_axi.bind('<Button-3>', self.wl_callback)
        #
        self.canvas_cor = tk.Canvas(self.frame, bd=0, width=self.cor_tk_img.width(), height=self.cor_tk_img.height())
        self.canvas_cor.grid(row=1, column=0, sticky = 'N')
        self.canv_img_cor = self.canvas_cor.create_image(0,0, image=self.cor_tk_img,anchor='nw')
        self.canvas_cor.bind('<Button-1>', self.cor_callback)
        self.canvas_cor.bind('<Shift-Button-1>', self.cor_jog_callback)
        #
        self.canvas_sag = tk.Canvas(self.frame, bd=0, width=self.sag_tk_img.width(), height=self.sag_tk_img.height())
        self.canvas_sag.grid(row=1, column=1, sticky = 'NW')
        self.canv_img_sag = self.canvas_sag.create_image(0,0, image=self.sag_tk_img,anchor='nw')
        self.canvas_sag.bind('<Button-1>', self.sag_callback)
        self.canvas_sag.bind('<Shift-Button-1>', self.sag_jog_callback)
        # sort out OS dependent mouse wheel bindings
        if platform.system() == 'Linux':
            self.canvas_axi.bind('<Button-4>', self.axi_mousewheel_callback)
            self.canvas_axi.bind('<Shift-Button-4>', self.axi_shift_mousewheel_callback)
            self.canvas_axi.bind('<Button-5>', self.axi_mousewheel_callback)
            self.canvas_axi.bind('<Shift-Button-5>', self.axi_shift_mousewheel_callback)
            self.canvas_cor.bind('<Button-4>', self.cor_mousewheel_callback)
            self.canvas_cor.bind('<Shift-Button-4>', self.cor_shift_mousewheel_callback)
            self.canvas_cor.bind('<Button-5>', self.cor_mousewheel_callback)
            self.canvas_cor.bind('<Shift-Button-5>', self.cor_shift_mousewheel_callback)
            self.canvas_sag.bind('<Button-4>', self.sag_mousewheel_callback)
            self.canvas_sag.bind('<Shift-Button-4>', self.sag_shift_mousewheel_callback)
            self.canvas_sag.bind('<Button-5>', self.sag_mousewheel_callback)
            self.canvas_sag.bind('<Shift-Button-5>', self.sag_shift_mousewheel_callback)
        else:
            self.canvas_axi.bind('<MouseWheel>', self.axi_mousewheel_callback)
            self.canvas_axi.bind('<Shift-MouseWheel>', self.axi_shift_mousewheel_callback)
            self.canvas_cor.bind('<MouseWheel>', self.cor_mousewheel_callback)
            self.canvas_cor.bind('<Shift-MouseWheel>', self.cor_shift_mousewheel_callback)
            self.canvas_sag.bind('<MouseWheel>', self.sag_mousewheel_callback)
            self.canvas_sag.bind('<Shift-MouseWheel>', self.sag_shift_mousewheel_callback)
        #
        self.make_annotations()
        ### info panel
        self.info_panel = tk.Frame(self.frame, bd=2, relief=tk.SUNKEN, bg='black')
        self.info_panel.grid(row=0, column=1, sticky = 'NW')        
        # display static stuff
        self.static_str = string_tail(self.display_name, 30)
        inp_shape = self.input_img.shape
        self.static_str += '\nraster: {}, {}, {}'.format(inp_shape[0], inp_shape[1], inp_shape[2])
        self.static_str += '\n{}'.format(type(self.input_img.data[0,0,0]))
        # inp_vxdsps = self.input_img.voxel_displacements
        self.static_str += '\nvoxel dims: {:.2f}, {:.2f}, {:.2f}\n'.format(self.input_img.voxel_sizes[0], self.input_img.voxel_sizes[0], self.input_img.voxel_sizes[0])
        self.info_str = tk.StringVar()
        self.info_w = tk.Label(self.info_panel, textvariable=self.info_str, fg='#aaaaaaaaa', bg='black')
        self.info_w.grid()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    def update_info(self):
        # update the string holding the focus on the info panel
        # format_string = 'i, j, k: {:.2f}, {:.2f}, {:.2f}\nx, y, z: {:.2f}, {:.3f}, {:.2f}\nval: {:.2f}'
        xyz = self.rect_v_img.ijk_to_xyz(self.focus_i, self.focus_j, self.focus_k)
        format_string = 'x, y, z: {:.2f}, {:.3f}, {:.2f}\nval: {:.2f}, mm_per_pixel: {:.2f}\nwindow: {:.2f}, level: {:.2f}'
        val = self.image_slicer.get_intensity((self.focus_i, self.focus_j, self.focus_k))
        # self.info_str.set(format_string.format(i, j, k, xyz[0], xyz[1], xyz[2], val))
        dpy_string = self.static_str + format_string
        self.info_str.set(dpy_string.format(xyz[0], xyz[1], xyz[2], val, self.mm_per_pixel, self.window, self.level))
       
    def update_focus_ijk(self, i, j, k, call_hook=True):
        self.focus_i, self.focus_j, self.focus_k = i, j, k
        # set focus and call hook if needed
        xyz = self.rect_v_img.ijk_to_xyz(self.focus_i, self.focus_j, self.focus_k)
        if (call_hook == True) and (self.focus_hook != False):
            self.focus_hook(*xyz)
        # Hackish:  undo effect of focus getting changed by hook function call to self to update...
        self.focus_i, self.focus_j, self.focus_k = i, j, k
        self.update_info()
        # DEBUG next line can check consistency of reported coordinates and image locations
        # self.rect_v_img.data[int(round(i)),int(round(j)),int(round(k))] = 0
        #
        self.update_images_and_canvases()
    
    def update_focus_xyz(self, x, y, z, call_hook=True):
        ijk = self.rect_v_img.xyz_to_ijk(x, y, z)
        self.update_focus_ijk(*ijk, call_hook)

    def update_canvases(self):
        self.axi_tk_img=ImageTk.PhotoImage(self.axi_pilimg)
        self.cor_tk_img=ImageTk.PhotoImage(self.cor_pilimg)
        self.sag_tk_img=ImageTk.PhotoImage(self.sag_pilimg)
        self.canvas_axi.itemconfig(self.canv_img_axi, image= self.axi_tk_img)
        self.canvas_cor.itemconfig(self.canv_img_cor, image= self.cor_tk_img)
        self.canvas_sag.itemconfig(self.canv_img_sag, image= self.sag_tk_img)
        self.delete_annotations()
        self.make_annotations()
        # print('CURRENT MM_PER_PIXEL: {}'.format(self.mm_per_pixel))

    def update_images_and_canvases(self):
        self.update_images()
        self.update_canvases()    
 
    def make_annotations(self):
        self.make_annotations_axi()
        self.make_annotations_cor()
        self.make_annotations_sag()

    def make_annotations_axi(self):
        # for indexing the 2d images
        focus_i_px = self.focus_i * self.i_width_px / self.n_i
        focus_j_px = self.focus_j * self.j_width_px / self.n_j
        focus_k_px = self.focus_k * self.k_width_px / self.n_k
        # complements
        focus_i_px_c = self.i_width_px - focus_i_px - 1
        focus_j_px_c = self.j_width_px - focus_j_px - 1 
        focus_k_px_c = self.k_width_px - focus_k_px - 1 
        h_pad, v_pad = 10, 12
        # windows seems to have a limited supply of dash patterns, many did not work
        self.axi_line_v = self.canvas_axi.create_line(focus_i_px_c, v_pad        , focus_i_px_c               , self.j_width_px - 1 - v_pad, fill='red', dash=(4,4))
        self.axi_line_h = self.canvas_axi.create_line(h_pad       , focus_j_px_c , self.i_width_px - 1 - h_pad, focus_j_px_c               , fill='red', dash=(4,4))
        ##
        self.axi_a_label = self.canvas_axi.create_text(focus_i_px_c                 , v_pad/2                      , text='A', fill='red')
        self.axi_p_label = self.canvas_axi.create_text(focus_i_px_c                 , self.j_width_px - 1 - v_pad/2, text='P', fill='red')
        self.axi_l_label = self.canvas_axi.create_text(h_pad/2                      , focus_j_px_c                 , text='R', fill='red')
        self.axi_r_label = self.canvas_axi.create_text(self.i_width_px - 1 - h_pad/2, focus_j_px_c                 , text='L', fill='red')
        #
        self.axi_items = [self.axi_line_v, self.axi_line_h, self.axi_a_label, self.axi_p_label, self.axi_l_label, self.axi_r_label]
        # paint the green dot that reflects window and level
        if self.show_green_dot:
            #  needs to be tested on negative intensities
            self.dot_x = self.i_width_px - ((self.window / (self.intensity_max - self.intensity_min)) * self.i_width_px) - 1
            # NOT GOOD FOR NEG
            # self.dot_y = (1.0 - (self.level / self.intensity_max)) * self.j_width_px
            # self.dot_y = (1.0 - ((self.level - self.intensity_min) / (self.intensity_max - self.intensity_min))) * self.j_width_px
            self.dot_y = self.j_width_px - ((1.0 - ((self.level - self.intensity_min) / (self.intensity_max - self.intensity_min))) * self.j_width_px) - 1
            self.axi_green_dot = self.canvas_axi.create_oval(self.dot_x - 5, self.dot_y - 5, self.dot_x + 5, self.dot_y + 5, fill='green')
        else:
            self.axi_green_dot = None
        self.axi_reticles = []
        if self.show_reticles:
            for i in range(-5,6):
                d = (10 * i) / self.mm_per_pixel
                self.axi_reticles.append(self.canvas_axi.create_line(focus_i_px_c - 3, focus_j_px_c + d, focus_i_px_c + 3, focus_j_px_c + d, fill='red'))
                self.axi_reticles.append(self.canvas_axi.create_line(focus_i_px_c + d, focus_j_px_c - 3, focus_i_px_c + d, focus_j_px_c + 3, fill='red'))

    def make_annotations_cor(self):
        # for indexing the 2d images
        focus_i_px = self.focus_i * self.i_width_px / self.n_i
        focus_j_px = self.focus_j * self.j_width_px / self.n_j
        focus_k_px = self.focus_k * self.k_width_px / self.n_k
        # complements
        focus_i_px_c = self.i_width_px - focus_i_px - 1
        focus_j_px_c = self.j_width_px - focus_j_px - 1 
        focus_k_px_c = self.k_width_px - focus_k_px - 1 
        h_pad, v_pad = 10, 12
        # windows seems to have a limited supply of dash patterns, many did not work
        self.cor_line_v = self.canvas_cor.create_line(focus_i_px_c, v_pad        , focus_i_px_c               , self.k_width_px - 1 - v_pad, fill='red', dash=(4,4))
        self.cor_line_h = self.canvas_cor.create_line(h_pad       , focus_k_px_c , self.i_width_px - 1 - h_pad, focus_k_px_c               , fill='red', dash=(4,4))
        ##
        self.cor_s_label = self.canvas_cor.create_text(focus_i_px_c                 ,                       v_pad/2, text='S', fill='red')
        self.cor_i_label = self.canvas_cor.create_text(focus_i_px_c                 , self.k_width_px - 1 - v_pad/2, text='I', fill='red')
        self.cor_l_label = self.canvas_cor.create_text(h_pad/2                      , focus_k_px_c                 , text='R', fill='red')
        self.cor_r_label = self.canvas_cor.create_text(self.i_width_px - 1 - h_pad/2, focus_k_px_c                 , text='L', fill='red')
        #
        self.cor_items = [self.cor_line_v, self.cor_line_h, self.cor_s_label, self.cor_i_label, self.cor_l_label, self.cor_r_label]
        self.cor_reticles = []
        if self.show_reticles:
            for i in range(-5,6):
                d = (10 * i) / self.mm_per_pixel
                self.cor_reticles.append(self.canvas_cor.create_line(focus_i_px_c + d, focus_k_px_c - 3, focus_i_px_c + d, focus_k_px_c + 3, fill='red'))
                self.cor_reticles.append(self.canvas_cor.create_line(focus_i_px_c - 3, focus_k_px_c + d, focus_i_px_c + 3, focus_k_px_c + d, fill='red'))

    def make_annotations_sag(self):
        # for indexing the 2d images
        focus_i_px = self.focus_i * self.i_width_px / self.n_i
        focus_j_px = self.focus_j * self.j_width_px / self.n_j
        focus_k_px = self.focus_k * self.k_width_px / self.n_k
        # complements
        focus_i_px_c = self.i_width_px - focus_i_px - 1
        focus_j_px_c = self.j_width_px - focus_j_px - 1 
        focus_k_px_c = self.k_width_px - focus_k_px - 1 
        h_pad, v_pad = 10, 12
        # windows seems to have a limited supply of dash patterns, many did not work
        self.sag_line_h = self.canvas_sag.create_line(h_pad       , focus_k_px_c , self.j_width_px - 1 - h_pad, focus_k_px_c               , fill='red', dash=(4,4))
        self.sag_line_v = self.canvas_sag.create_line(focus_j_px_c, v_pad        , focus_j_px_c               , self.k_width_px - 1 - v_pad, fill='red', dash=(4,4))
        ##
        self.sag_a_label = self.canvas_sag.create_text(h_pad/2                      , focus_k_px_c                 , text='A', fill='red')
        self.sag_p_label = self.canvas_sag.create_text(self.j_width_px - 1 - h_pad/2, focus_k_px_c                 , text='P', fill='red')
        self.sag_s_label = self.canvas_sag.create_text(focus_j_px_c                 , v_pad/2                      , text='S', fill='red')
        self.sag_i_label = self.canvas_sag.create_text(focus_j_px_c                 , self.k_width_px - h_pad/2    , text='I', fill='red')
        #
        self.sag_items = [self.sag_line_h, self.sag_line_v, self.sag_a_label, self.sag_p_label, self.sag_s_label, self.sag_i_label]
        self.sag_reticles = []
        if self.show_reticles:
            for i in range(-5,6):
                d = (10 * i) / self.mm_per_pixel
                self.sag_reticles.append(self.canvas_sag.create_line(focus_j_px_c - 3, focus_k_px_c + d, focus_j_px_c + 3, focus_k_px_c + d, fill='red'))
                self.sag_reticles.append(self.canvas_sag.create_line(focus_j_px_c + d, focus_k_px_c - 3, focus_j_px_c + d, focus_k_px_c + 3, fill = 'red'))

    def delete_annotations(self):
        self.delete_annotations_axi()
        self.delete_annotations_cor()
        self.delete_annotations_sag()

    def delete_annotations_axi(self):
        for item in self.axi_items:
            self.canvas_axi.delete(item)
        for seg in self.axi_reticles:
            self.canvas_axi.delete(seg)
        # green dot
        if self.axi_green_dot is not None:
            self.canvas_axi.delete(self.axi_green_dot)
    def delete_annotations_cor(self):
        for item in self.cor_items:
            self.canvas_cor.delete(item)
        for seg in self.cor_reticles:
            self.canvas_cor.delete(seg)
    def delete_annotations_sag(self):
        for item in self.sag_items:
            self.canvas_sag.delete(item)
        for seg in self.sag_reticles:
            self.canvas_sag.delete(seg)

    def update_annotations(self):
        self.delete_annotations()
        self.make_annotations()

    def update_annotations_axi(self):
        self.delete_annotations_axi()
        self.make_annotations_axi()
    def update_annotations_cor(self):
        self.delete_annotations_cor()
        self.make_annotations_cor()
    def update_annotations_sag(self):
        self.delete_annotations_sag()
        self.make_annotations_sag()

    def reticles_on(self):
        if not self.show_reticles:
            # self.make_reticles()
            self.show_reticles = True
            self.update_annotations()

    def reticles_off(self):
        if self.show_reticles:
            # self.delete_reticles()
            self.show_reticles = False
            self.update_annotations()

    def axi_callback(self, event):
        self.show_green_dot = False
        i,j = (self.i_width_px - event.x - 1) * self.n_i / self.i_width_px  , (self.j_width_px - event.y - 1) * self.n_j / self.j_width_px
        self.focus_i, self.focus_j = i, j
        self.update_annotations_axi()
        # self.our_update()
        self.root.update_idletasks()
        self.update_focus_ijk(i, j, self.focus_k)

    #################################################################################################
    # mouse wheel callbacks
    def event_wm_incr(self, event):
        if platform.system() == 'Linux':
            if event.num == 4:
                sgn = 1
            else:
                sgn = -1
        else:
            sgn = np.sign(event.delta)
        return sgn
    # 1 cm steps
    def axi_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        # self.focus_k = self.focus_k + 10.0 * sgn / self.k_px_mm
        self.focus_k = self.focus_k + 10.0 * sgn 
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    # 1 pixel steps
    def axi_shift_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        # self.focus_k = self.focus_k + sgn / self.k_px_mm
        self.focus_k = self.focus_k + sgn 
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    def cor_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        # self.focus_j = self.focus_j + 10.0 * sgn / self.j_px_mm
        self.focus_j = self.focus_j + 10.0 * sgn 
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    def cor_shift_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        self.focus_j = self.focus_j + sgn
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    def sag_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        self.focus_i = self.focus_i + 10.0 * sgn
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    def sag_shift_mousewheel_callback(self,event):
        sgn = self.event_wm_incr(event)
        self.focus_i = self.focus_i + sgn
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)

    #################################################################################################
    # respond to focus jogging
    def axi_jog_callback(self, event):
        self.show_green_dot = False
        i,j = (self.i_width_px - event.x - 1) * self.n_i / self.i_width_px  , (self.j_width_px - event.y - 1) * self.n_j / self.j_width_px
        di, dj = self.focus_i - i, self.focus_j - j  # which line are we closest to?
        if (abs(di) > abs(dj)):
            self.focus_i = self.focus_i - np.sign(di)
        else:
            self.focus_j = self.focus_j - np.sign(dj)
        self.update_annotations_axi()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)
    #
    def cor_callback(self, event):
        self.show_green_dot = False
        i,k = (self.i_width_px - event.x - 1) * self.n_i / self.i_width_px  , (self.k_width_px - event.y - 1) * self.n_k  / self.k_width_px
        self.focus_i, self.focus_k = i, k
        self.update_annotations_cor()
        self.root.update_idletasks()
        self.update_focus_ijk(i, self.focus_j, k)
    def cor_jog_callback(self, event):
        self.show_green_dot = False
        i,k = (self.i_width_px - event.x - 1) * self.n_i / self.i_width_px  , (self.k_width_px - event.y - 1) * self.n_k  / self.k_width_px
        di, dk = self.focus_i - i, self.focus_k - k  # which line are we closest to?
        if (abs(di) > abs(dk)):
            self.focus_i = self.focus_i - np.sign(di)
        else:
            self.focus_k = self.focus_k - np.sign(dk)
        self.update_annotations_cor()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k)
    #
    def sag_callback(self, event):
        self.show_green_dot = False
        j,k = (self.j_width_px - event.x - 1) * self.n_j / self.j_width_px  , (self.k_width_px - event.y - 1) * self.n_k  / self.k_width_px
        self.focus_j, self.focus_k = j, k
        self.update_annotations_sag()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i, j, k)
    def sag_jog_callback(self, event):
        self.show_green_dot = False
        j,k = (self.j_width_px - event.x - 1) * self.n_j / self.j_width_px  , (self.k_width_px - event.y - 1) * self.n_k  / self.k_width_px
        dj, dk = self.focus_j - j, self.focus_k - k  # which line are we closest to?
        if (abs(dj) > abs(dk)):
            self.focus_j = self.focus_j - np.sign(dj)
        else:
            self.focus_k = self.focus_k - np.sign(dk)
        self.update_annotations_sag()
        self.root.update_idletasks()
        self.update_focus_ijk(self.focus_i , self.focus_j, self.focus_k)

    # green dot
    # button three on an axi canvas for window level
    def wl_callback(self, event):
        if self.show_green_dot:
            # print('called!')
            self.window = ((self.i_width_px - event.x) / self.i_width_px) * (self.intensity_max - self.intensity_min) 
            self.level = (event.y / self.j_width_px) * (self.intensity_max - self.intensity_min) + self.intensity_min
            self.update_images()
            self.update_info()
            self.update_canvases()
        else:
            self.show_green_dot = True
            self.update_canvases()
    
    # for implementing resize requests...
    # this can also be used to force updates of image slicers if the mm_per_pixel_new is same as old
    def update_mm_per_pixel(self, mm_per_pixel_new):
        # print('updating from {} to {}'.format(self.mm_per_pixel, mm_per_pixel_new))
        focus_x, focus_y, focus_z = self.rect_v_img.ijk_to_xyz(self.focus_i, self.focus_j, self.focus_k)
        self.mm_per_pixel = mm_per_pixel_new
        self.rect_v_img = lwi.make_rectified_container(self.input_img, self.mm_per_pixel)
        self.image_slicer = VirtualImageSlicer(self.rect_v_img, self.input_img, self.interpolation_order)  
        self.n_i, self.n_j, self.n_k = self.rect_v_img.shape
        self.i_px_mm = self.rect_v_img.voxel_displacements[0]
        self.j_px_mm = self.rect_v_img.voxel_displacements[1]
        self.k_px_mm = self.rect_v_img.voxel_displacements[2]
        self.i_img_width_mm = self.n_i * self.i_px_mm
        self.j_img_width_mm = self.n_j * self.j_px_mm
        self.k_img_width_mm = self.n_k * self.k_px_mm
        # image sizes in pixels, integer valued
        self.i_width_px = int(self.i_img_width_mm / self.mm_per_pixel)
        self.j_width_px = int(self.j_img_width_mm / self.mm_per_pixel)
        self.k_width_px = int(self.k_img_width_mm / self.mm_per_pixel)
        # update the ijk focus
        self.focus_i, self.focus_j, self.focus_k = self.rect_v_img.xyz_to_ijk(focus_x, focus_y, focus_z)
        #
        self.update_images()
        self.axi_tk_img = ImageTk.PhotoImage(self.axi_pilimg)
        self.cor_tk_img = ImageTk.PhotoImage(self.cor_pilimg)
        self.sag_tk_img = ImageTk.PhotoImage(self.sag_pilimg)
        # resize the canvases appropriately
        self.canvas_axi.config(width=self.axi_tk_img.width(), height=self.axi_tk_img.height())
        self.canvas_cor.config(width=self.cor_tk_img.width(), height=self.cor_tk_img.height())
        self.canvas_sag.config(width=self.sag_tk_img.width(), height=self.sag_tk_img.height())
        #
        self.update_focus_ijk(self.focus_i, self.focus_j, self.focus_k, call_hook=False)
        # which calls: self.update_images_and_canvases()


# Virtual Image Slicer
# Makes an object that
# extracts three orthogonal xyz axis aligned cross sestions from the virtual image 'v_image'.
# The cross sections  intersect at the 3d point 'focus' (floating point).
# The image data is supplied by 'source_image'.
# which is assumed to be in the same xyz space as v_image.
# Scipy 'map_coordinates' is used to do the interpolation from 'source_image'
# The semantics are similar to the following (which does not interpolate):
# def extract_slices(image, focus):
#     jk_slice = source_img.data[int(round(focus[0])),:,:]
#     ik_slice = source_img.data[:,int(round(focus[1])),:]
#     ij_slice = source_img.data[:,:,int(round(focus[2]))]
#     return jk_slice, ik_slice, ij_slice
#
# also can interpolate the intensity at a specified location
class VirtualImageSlicer:
    def __init__(self, v_image, source_image, interpolation_order):
        self.v_image = v_image
        self.source_image = source_image
        self.interpolation_order = interpolation_order
        #
        self.jk_shape = (v_image.shape[1], v_image.shape[2])
        self.jk_flat_shape = (self.jk_shape[0] * self.jk_shape[1],)
        self.i_coords = np.zeros(self.jk_flat_shape[0])
        self.jk_grid = np.mgrid[0:self.jk_shape[0], 0:self.jk_shape[1]]
        self.jk_coords = np.array([self.jk_grid[0].reshape(self.jk_flat_shape), self.jk_grid[1].reshape(self.jk_flat_shape)])
        # 
        self.ik_shape = (v_image.shape[0], v_image.shape[2])
        self.ik_flat_shape = (self.ik_shape[0] * self.ik_shape[1],)
        self.j_coords = np.zeros(self.ik_flat_shape[0])
        self.ik_grid = np.mgrid[0:self.ik_shape[0], 0:self.ik_shape[1]]
        self.ik_coords = np.array([self.ik_grid[0].reshape(self.ik_flat_shape), self.ik_grid[1].reshape(self.ik_flat_shape)])
        # 
        self.ij_shape = (v_image.shape[0], v_image.shape[1])
        self.ij_flat_shape = (self.ij_shape[0] * self.ij_shape[1],)
        self.k_coords = np.zeros(self.ij_flat_shape[0])
        self.ij_grid = np.mgrid[0:self.ij_shape[0], 0:self.ij_shape[1]]
        self.ij_coords = np.array([self.ij_grid[0].reshape(self.ij_flat_shape), self.ij_grid[1].reshape(self.ij_flat_shape)])
        #
        self.focus_previous = np.array([-1,-1,-1])
        self.jk_slice_previous, self.ik_slice_previous , self.ij_slice_previous = None, None, None
    # extract the three orthogonal slices
    def get_slices(self, focus):
        composite_affine = np.matmul(self.source_image.inv_affine, self.v_image.affine)
        ################################################################
        if focus[0] == self.focus_previous[0]:
            jk_slice = self.jk_slice_previous
        else:
            self.i_coords.fill(focus[0])
            ijk_coords = np.array([self.i_coords, self.jk_coords[0], self.jk_coords[1]])
            ijk_coords_trn = lwi.apply_affine(composite_affine, ijk_coords)
            interpolated_values = spndi.map_coordinates(self.source_image.data, ijk_coords_trn, order=self.interpolation_order)
            jk_slice = interpolated_values.reshape(self.jk_shape)
            self.jk_slice_previous = jk_slice
        ################################################################
        if focus[1] == self.focus_previous[1]:
            ik_slice = self.ik_slice_previous
        else:
            self.j_coords.fill(focus[1])
            ijk_coords = np.array([self.ik_coords[0], self.j_coords, self.ik_coords[1]])
            ijk_coords_trn = lwi.apply_affine(composite_affine, ijk_coords)
            interpolated_values = spndi.map_coordinates(self.source_image.data, ijk_coords_trn, order=self.interpolation_order)
            ik_slice = interpolated_values.reshape(self.ik_shape)
            self.ik_slice_previous = ik_slice
        ################################################################
        if focus[2] == self.focus_previous[2]:
            ij_slice = self.ij_slice_previous
        else:
            self.k_coords.fill(focus[2])
            ijk_coords = np.array([self.ij_coords[0], self.ij_coords[1], self.k_coords])
            ijk_coords_trn = lwi.apply_affine(composite_affine, ijk_coords)
            interpolated_values = spndi.map_coordinates(self.source_image.data, ijk_coords_trn, order=self.interpolation_order)
            ij_slice = interpolated_values.reshape(self.ij_shape)
            self.ij_slice_previous = ij_slice
        ################################################################
        self.focus_previous = np.copy(focus)
        return jk_slice, ik_slice, ij_slice
    # interpolate the intensity at the specified focus (a tuple)
    def get_intensity(self, focus):
        composite_affine = np.matmul(self.source_image.inv_affine, self.v_image.affine)
        ijk_coords = np.array([[focus[0], focus[1], focus[2]]]).T
        ijk_coords_trn = lwi.apply_affine(composite_affine, ijk_coords)
        interpolated_values = spndi.map_coordinates(self.source_image.data, ijk_coords_trn, order=self.interpolation_order)
        return interpolated_values[0]
         
        
def string_tail(strn, length):
    if len(strn) > length:
        strn = '...' + strn[len(strn) - length:]
    return strn
