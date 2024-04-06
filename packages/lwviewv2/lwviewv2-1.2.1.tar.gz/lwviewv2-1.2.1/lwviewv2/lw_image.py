import numpy as np
import numpy.linalg as npl
import scipy.ndimage as spndi


# A class for light weight virtual images:
# keep it simple, and this has the geometric essentials
# (but has no data)

class LwVirtualImage:
    def __init__(self, shape, affine):
        self.shape = shape
        self.affine = affine
        self.inv_affine = npl.inv(affine)
        # xyz displacements that correspond to one voxel displacements
        self.voxel_displacements = apply_affine(self.affine, np.array([1,1,1])) - apply_affine(self.affine, np.array([0,0,0]))
        self.voxel_sizes = np.array([
            np.linalg.norm(apply_affine(self.affine, np.array([1,0,0])) - apply_affine(self.affine, np.array([0,0,0]))),
            np.linalg.norm(apply_affine(self.affine, np.array([0,1,0])) - apply_affine(self.affine, np.array([0,0,0]))),
            np.linalg.norm(apply_affine(self.affine, np.array([0,0,1])) - apply_affine(self.affine, np.array([0,0,0])))
        ])
        # print('voxel sizes {}'.format(self.voxel_sizes))
        self.filename = None
        self.display_name = None
    # next two return rowvecs (1d numpy arrays) (CRUFT ALERT!: .T).T[0] )
    def ijk_to_xyz(self, i,j,k):
        # return apply_affine(self.affine, np.array([[i,j,k]]).T).T[0]
        return apply_affine(self.affine, np.array([i,j,k]))
    def xyz_to_ijk(self, x,y,z):
        # return apply_affine(self.inv_affine, np.array([[x,y,z]]).T).T[0]
        return apply_affine(self.inv_affine, np.array([x,y,z]))
    def make_real(self, data):
        return LwImage(data, self.affine)

# A light weight class for images, inherits from
# virtual one above
class LwImage(LwVirtualImage):
    def __init__(self, data, affine):
        LwVirtualImage.__init__(self, data.shape, affine)
        self.data = data

# Operates on and returns a row of colvecs
def apply_affine_aux(affine_t, points):
    rotation_t = affine_t[:3,:3]
    translation_t = affine_t[:3,3:4]
    rotated = np.dot(rotation_t, points)
    result = rotated + translation_t
    return result

# Operates on and returns a row of colvecs
# or same on single rowvecs
# .. couldn't this be automaiclly done?
def apply_affine(affine_t, points):
    if len(points.shape) == 1:
        return apply_affine_aux(affine_t, np.array([points]).T).T[0]
    else:
        return apply_affine_aux(affine_t, points)


# reformat the input image so that in the resulting
# image, the xyz axes are aligned with the ijk 'axes',
# i.e., the affine rotation part is a scaled identity matrix
# useful to fix a shortcoming in LwView
# def make_rectified_image(input_img, mmpv):
#     result_v_image = make_rectified_container(input_img, mmpv)
#     composite_affine = np.matmul(input_img.inv_affine, result_v_image.affine)
#     print('making coordinates...', end='')
#     # colvec of rovecs that are a 'list' of all the indices in the result image
#     uvw_coords = make_coordinates(result_v_image.shape)
#     print('transforming coordinates...', end='')
#     ijk_coords = apply_affine_alt(composite_affine, uvw_coords)
#     result_img = reformat(input_img, result_v_image, ijk_coords)
#     result_img.display_name = input_img.display_name + '_R'
#     return result_img

def make_rectified_image(input_img, mmpv):
    result_v_image_template = make_rectified_container(input_img, mmpv)
    new_img = reformat(input_img, result_v_image_template)
    return new_img

# this constructs a virtual image such that
# the xyz axes are aligned with the ijk 'axes',
# i.e., the affine rotation part is a scaled identity matrix,
# and the containter contains the full xyz extent of the data of the input_img.
def make_rectified_container(input_img, mmpv):
    # First figure out affine for the new image
    # want data array to map to oriented box in xyz so that it
    # exactly holds the maximum extent of xyz in the input image
    # coord convention: ijk index into input image
    #                   uvw index into the result image
    ijk_corners = get_corners(input_img.shape)
    xyz_corners = apply_affine(input_img.affine, ijk_corners).T
    min_xyzs, max_xyzs = np.min(xyz_corners, axis=0), np.max(xyz_corners, axis=0)
    xyz_ranges = max_xyzs - min_xyzs
    # shape of new data array
    result_shape = int(np.ceil(xyz_ranges[0] / mmpv)), int(np.ceil(xyz_ranges[1] / mmpv)), int(np.ceil(xyz_ranges[2] / mmpv))
    # the new affine is a scaled identity for the 'rotation' part, and has a translation
    # that is the min_xyzs (which corresponds to indices 000)
    result_affine = np.array([[mmpv,0,0,min_xyzs[0]],[0,mmpv,0,min_xyzs[1]], [0,0,mmpv,min_xyzs[2]],[0,0,0,1]])
    return LwVirtualImage(result_shape, result_affine)
    

# returns a new image containing the contents
# of the source image reformatted into the geometry
# specified by the destination virtual image
def reformat(src_img, dest_v_img_template):
    composite_affine = np.matmul(src_img.inv_affine, dest_v_img_template.affine)
    print('making coordinates...', end='')
    # colvec of rovecs that are a 'list' of all the indices in the result image
    uvw_grids = np.mgrid[0:dest_v_img_template.shape[0], 0:dest_v_img_template.shape[1], 0:dest_v_img_template.shape[2]]
    flat_shape = (dest_v_img_template.shape[0] * dest_v_img_template.shape[1] * dest_v_img_template.shape[2],)
    uvw_coords = np.array([uvw_grids[0].reshape(flat_shape), uvw_grids[1].reshape(flat_shape), uvw_grids[2].reshape(flat_shape)])
    print('transforming coordinates...', end='')
    ijk_coords = apply_affine(composite_affine, uvw_coords)
    print('interpolating...', end='')
    interpolated_values = spndi.map_coordinates(src_img.data, ijk_coords, order=1)
    print('done...', end='')
    new_img_data = interpolated_values.reshape(dest_v_img_template.shape)
    new_img = dest_v_img_template.make_real(new_img_data)
    new_img.display_name = src_img.display_name + '_R'
    return new_img


# returns a stacking of rowvecs of the coords of the corners of a shape
def get_corners(input_shape):
    p000 = np.array([                 0,                  0, 0])
    p001 = np.array([                 0,                  0, input_shape[2] - 1])
    p010 = np.array([                 0, input_shape[1] - 1, 0])
    p011 = np.array([                 0, input_shape[1] - 1, input_shape[2] - 1])
    p100 = np.array([input_shape[0] - 1,                  0, 0])
    p101 = np.array([input_shape[0] - 1,                  0, input_shape[2] - 1])
    p110 = np.array([input_shape[0] - 1, input_shape[1] - 1, 0])
    p111 = np.array([input_shape[0] - 1, input_shape[1] - 1, input_shape[2] - 1])
    result = np.array([p000, p001, p010, p011, p100, p101, p110, p111]).T
    return result


###########################################################################
# Get basename of a path
def get_basename(path):
    return path.split('/')[-1]





