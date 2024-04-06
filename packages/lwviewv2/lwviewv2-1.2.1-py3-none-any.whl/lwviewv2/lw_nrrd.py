# facility for loading nrrd images as LwImage s

import numpy as np
import nrrd # pip install pynrrd
import lwviewv2.lw_image as lwi

def load(fn):
    nrrd_tuple = nrrd.read(fn)
    lw_image = nrrd_tuple_to_lw_image(nrrd_tuple)
    lw_image.file_name = fn
    lw_image.display_name = lwi.get_basename(fn)
    return lw_image

def nrrd_tuple_to_lw_image(nrrd_tuple):
    data = nrrd_tuple[0]
    header = nrrd_tuple[1]
    space_directions = header['space directions']
    space_origin = header['space origin']
    space_origin_cv = np.array([space_origin]).T
    if header['space'] != 'left-posterior-superior':
        raise Exception('expected an LPS space image')
    # is left-posterior-superior
    # from Andras:
    ijk_to_lps = np.vstack((np.hstack((space_directions.T, space_origin_cv)), [0, 0, 0, 1]))
    lps_to_ras = np.diag([-1, -1, 1, 1])
    ijk_to_ras = np.matmul(lps_to_ras, ijk_to_lps)
    lw_image = lwi.LwImage(data, ijk_to_ras)
    return lw_image



# def load(fn):
#     nrrd_tuple = nrrd.read(fn)
#     data = nrrd_tuple[0]
#     header = nrrd_tuple[1]
#     space_directions = header['space directions']
#     space_origin = header['space origin']
#     space_origin_cv = np.array([space_origin]).T
#     if header['space'] != 'left-posterior-superior':
#         raise Exception('expected an LPS space image')
#     # is left-posterior-superior
#     # from Andras:
#     ijk_to_lps = np.vstack((np.hstack((space_directions.T, space_origin_cv)), [0, 0, 0, 1]))
#     lps_to_ras = np.diag([-1, -1, 1, 1])
#     ijk_to_ras = np.matmul(lps_to_ras, ijk_to_lps)
#     lw_image = lwi.LwImage(data, ijk_to_ras)
#     lw_image.file_name = fn
#     lw_image.display_name = lwi.get_basename(fn)
#     return lw_image




    
