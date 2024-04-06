import nibabel as nb
import numpy as np
import numpy.linalg as npl
# from ortho_view import OrthoView
from lwviewv2.lw_view import LwView
from copy import deepcopy
from operator import add
from operator import sub

# for interactively generating or editing a collection of corresponding
# landmarks from a pair of volumes
# navigate both volumes to corresponding poings and add them to the
# list of landmark pairs
# foci can be locked or unlocked
# the 'left volume' (img_0) can be 'displacement corrected' to fix
# translational misregistration, by modifying it's affine
#   AFAIK - the argument image is not modified as orthoview
#   makes a new one via 'closest canonical'

# 'inputs' should be a 2 el tuple of stacks of rovecs
def edit_landmarks(img_0, img_1, mm_per_pixel=None, inputs=([],[])):
    # keep track of all displacement offsets applied to images and landmarks
    pnts_0 = list(inputs[0])
    pnts_1 = list(inputs[1])
    i = 0
    n = len(pnts_0)
    correction_offset = np.zeros(3) 
    locked = 'U'
    def update_foci(od):
        nonlocal i
        nonlocal n
        nonlocal pnts_0
        nonlocal pnts_1
        if n > 0:
                od.MLwVw.lw_view_wgts[0].zoom_scale_axi = 1
                od.MLwVw.lw_view_wgts[1].zoom_scale_axi = 1
                od.MLwVw.lw_view_wgts[0].zoom_scale_cor = 1
                od.MLwVw.lw_view_wgts[1].zoom_scale_cor = 1
                od.MLwVw.lw_view_wgts[0].zoom_scale_sag = 1
                od.MLwVw.lw_view_wgts[1].zoom_scale_sag = 1
                
                od.MLwVw.lw_view_wgts[0].update_focus_xyz( pnts_0[i][0], pnts_0[i][1], pnts_0[i][2], call_hook=False)
                od.MLwVw.lw_view_wgts[1].update_focus_xyz( pnts_1[i][0], pnts_1[i][1], pnts_1[i][2], call_hook=False)
    def cmd_hook(od, cmd):
        nonlocal i
        nonlocal n
        nonlocal pnts_0
        nonlocal pnts_1
        nonlocal correction_offset
        nonlocal locked
        # Append the curent pair of foci to the landmark list
        if cmd == 'a':   
            p0 = od.MLwVw.lw_view_wgts[0].get_focus_xyz()
            p1 = od.MLwVw.lw_view_wgts[1].get_focus_xyz()
            pnts_0.append(p0)
            pnts_1.append(p1)
        # Delete current landmark pair
        elif cmd == 'd': 
            if n > 0:
                del pnts_0[i]
                del pnts_1[i]
                n = len(pnts_0)
                i = min(i, n - 1)
                update_foci(od)
            else:
                print('nothing to delete')
        # Change index by entering a number
        elif cmd.isdigit(): 
            new_i = int(cmd)
            if (new_i < 0) or  (new_i >= n):
                print('point {} is not defined'.format(new_i))
            else:
                i = new_i
                update_foci(od)
        # Next
        elif cmd == 'n': 
            if  n == 0:
                print('no landmarks defined')
            else:
                if i < n - 1:
                    i += 1
                else:
                    i = 0
                update_foci(od)
        # Previous
        elif cmd == 'p':  
            if  n == 0:
                print('no landmarks defined')
            else:
                if i > 0:
                    i -= 1
                else:
                    i = n - 1
                update_foci(od)
                    
        # Lock foci
        elif cmd == 'l':
            od.MLwVw.lock_the_foci()
            locked = 'L'
        # Unlock Foci
        elif cmd == 'u':
            od.MLwVw.unlock_the_foci()
            locked = 'U'
        # print current focus displacement
        elif cmd == 'D':
            p0 = od.MLwVw.lw_view_wgts[0].get_focus_xyz()
            p1 = od.MLwVw.lw_view_wgts[1].get_focus_xyz()
            disp = p1 - p0
            print('current displacement: {}'.format(disp))
        # print average displacement
        elif cmd == 'DA':
            if n == 0:
                print('no landmarks in list')
            else:
                avg_disp = (sum(pnts_1) - sum(pnts_0)) / n
                print('average displacement: {}'.format(avg_disp))
        # Displacement Correct (hacks image 1 (the 'left' image) affine)
        # displaces by difference of current foci
        # also 'correct' the landmark list correspondingly
        elif cmd == 'DC':
            p0 = od.MLwVw.lw_view_wgts[0].get_focus_xyz()
            p1 = od.MLwVw.lw_view_wgts[1].get_focus_xyz()
            disp = p1 - p0
            displace_img(od.MLwVw.lw_view_wgts[0].input_img, disp)
            print('displacing image: {}'.format(disp))
            od.MLwVw.lw_view_wgts[0].update_images()
            od.MLwVw.lw_view_wgts[0].update_canvases()
            correction_offset += disp
            pnts_0 = list(map(lambda pnt: add(pnt, correction_offset), pnts_0))
        # Displacement Correct (hacks image 1 (the 'left' image) affine)
        # displaces by average displacement of landmarks
        # also 'correct' the landmark list correspondingly
        elif cmd == 'DCA':
            if n == 0:
                print('no landmarks in list')
            else:
                avg_disp = (sum(pnts_1) - sum(pnts_0)) / n
                displace_img(od.MLwVw.lw_view_wgts[0].input_img, avg_disp)
                print('displacing image: {}'.format(avg_disp))
                od.MLwVw.lw_view_wgts[0].update_images()
                od.MLwVw.lw_view_wgts[0].update_canvases()
                correction_offset += avg_disp
                pnts_0 = list(map(lambda pnt: add(pnt, correction_offset), pnts_0))
        # show reticles
        elif cmd == 'R':
            od.MLwVw.lw_view_wgts[0].reticles_on()
            od.MLwVw.lw_view_wgts[1].reticles_on()
        elif cmd == 'r':
            od.MLwVw.lw_view_wgts[0].reticles_off()
            od.MLwVw.lw_view_wgts[1].reticles_off()

        # Help
        elif cmd == 'h':
            print_help()
        # write left image out
        elif cmd[0] == 'w':
            fn = cmd.split()[1]
            print('saving image file {}...'.format(fn))
            img = od.MLwVw.lw_view_wgts[0].input_img
            nb.save(img, fn)
            print('done')
        # Quit
        elif cmd == 'q':  
            od.exit()
        ##############   end of command interp
        else:
            print('huh?: {}'.format(cmd))
        n = len(pnts_0)
        # Prompt
        if n == 0:
            prompt ='{} -> '.format(locked)
        else:
            prompt = '[i: {} of {}] {} -> '.format(i , n, locked)
        return(prompt)
   
    LwView(img_0, img_1, mm_per_pixel=mm_per_pixel, lock_focus=False, cmdhook=cmd_hook)
    if n > 0:
        # tuple of stack of rowvecs
        pnts_0 = list(map(lambda pnt: sub(pnt, correction_offset), pnts_0))
        return(np.vstack(pnts_0), np.vstack(pnts_1))
    else:
        return(None)

# destructively translate an image by hacking it's affine
def displace_img(img, displacement): # displacement is rowvec
    img.affine[0,3] += displacement[0]
    img.affine[1,3] += displacement[1]
    img.affine[2,3] += displacement[2]

    
def print_help():
    print('<an integer> : goto that item in landmark list')
    print('n: next item')
    print('p: previous item')
    print('a: append current foci to landmark list')
    # print('i: insert current foci into landmark list')
    print('d: delete current item in landmark list')
    print('l: lock the foci')
    print('u: unlock the foci')
    print('D: print current focus displacement')
    print('DA: print average displacement over landmark list')
    print('DC: displacement correct the left image by current difference between foci')
    print('DCA: displacement correct the left image by current average displacement of landmark list')
    print('R: show reticles')
    print("r: don't show reticles")
    print('q: quit')
    
