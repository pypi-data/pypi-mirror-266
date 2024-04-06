# facility for importing NiBabel images as LwImage s

import nibabel as nb
import lwviewv2.lw_image as lwi
import platform

print(platform.system())

def load(fn):
    nibabel_image = nb.load(fn)
    lw_image = nibabel_image_to_lw_image(nibabel_image)
    lw_image.file_name = fn
    lw_image.display_name = lwi.get_basename(fn)
    return lw_image 

print(platform.node())

def nibabel_image_to_lw_image(nibabel_image):
    # if platform.system() == 'Linux' or platform.node() == 'sw-x1':
    if platform.system() == 'Linux':
        data = nibabel_image.get_fdata()
    else:
        # max headroom?
        data = nibabel_image.get_fdata()

    # print('data shape: ', data.shape)
        
    # if len(data.shape) != 3:
    #     # print('DATA SHAPE: ', data.shape)
    #     print('SHOWING FIRST IMAGE IN SEQUENCE OF LENGTH: ', data.shape[3] , ' (?)')
    #     data = data[:,:,:,0]
        
    affine = nibabel_image.affine
    lw_image = lwi.LwImage(data, affine)
    return lw_image

# my_img = load_image('./test-data/someones_anatomy.nii.gz')
