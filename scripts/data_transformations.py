from __future__ import print_function, division

#import glob
#import os
## from scripts.Word2PHOC import build_phoc as PHOC
#from utils import globals


import numpy as np
from torchvision import transforms
from skimage.morphology import thin as skimage_thinner


#  Method to compute the padding odf the input image to the max image size
def get_padding(image, output_size):
    output_max_width = output_size[0]
    output_max_height = output_size[1]
    h = image.shape[0]
    w = image.shape[1]

    pad_width = output_max_width - w
    if pad_width<0 : print('MAX_IMAGE_WIDTH is smaller than expected, config_file'); exit(0)
    
    if pad_width < 2:
        pad_left = pad_width
        pad_right = 0
    else:
        if pad_width % 2 == 0:
            pad_left = int(pad_width / 2)
            pad_right = pad_left
        else:
            pad_left = int(pad_width / 2) + 1
            pad_right = pad_left - 1
    
    pad_height = output_max_height - h    
    if pad_height<0 : print('MAX_IMAGE_WIDTH is smaller than expected, see config_file'); exit(0)
    if pad_height < 2:
        pad_top = pad_height
        pad_bottom = 0
    else:
        if pad_height % 2 == 0:
            pad_top = int(pad_height / 2)
            pad_bottom = pad_top
        else:
            pad_top = int(pad_height / 2) + 1
            pad_bottom = pad_top - 1

    padding = (pad_left, pad_top, pad_right, pad_bottom)
    return padding



# Class to perform the padding
class PadImage(object):
    """Pad the image in a sample to the max size

    Args:
        output_size (tuple or int): Desired output size.
    """
    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        self.output_max_width = output_size[0]
        self.output_max_height = output_size[1]

    def __call__(self, image):
        padding = get_padding(image, (self.output_max_width, self.output_max_height))

        # tsfm = transforms.Pad(padding)        
        
        tsfm = transforms.Compose([ transforms.ToPILImage(),
                                    transforms.Pad(padding)])
        image = tsfm(image)
        image = np.array(image.getdata(),
                    np.uint8).reshape(image.size[1], image.size[0], 1)
        return image

# Class to perform the padding
class NoneTransform(object):
    """ Does nothing to the image, to be used instead of None
    
    Args:
        image in, image out, nothing is done
    """
        
    def __call__(self, image):       
        return image
    


def image_thinning(img, p):
    # thinned = skimage_thinner(image) 
    thin_iter_step  = 1   
    img=img.squeeze()
    ss = img.shape
    ss = ss[0]*ss[1]
    img_max_orig = img.max()
    for i in range(25): 
        img_max = img.max()
        sum_img = img.sum()/(img.size* img_max)
        if sum_img>p:
            img = skimage_thinner(img, max_iter= thin_iter_step)
            img = img.astype('uint8')
        else: 
            img= (img/img.max()).astype('uint8') # the thinning will result in a binary [0,1] 2dArray, hence we need to normalized the non thinned ones
            break
    
    img = img.reshape(img.shape[0], img.shape[1], 1)
    return img*img_max_orig # Now, bringing the normalization back to all images


class ImageThinning(object):
    """ Thin the image 
        To be used as part of  torchvision.transforms
    Args: p, a threshold value to determine the thinning
        
    """
    def __init__(self, p = 0.2):
       #  assert isinstance(output_size, (int, tuple))
        self.p = p                  
        
    def __call__(self, image):
        # image =self.image_thinning(image, self.p)                      
        image = image_thinning(image, self.p)                      
        return image

