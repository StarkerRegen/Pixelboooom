import os
import math
import torch
import numpy as np
from PIL import Image

# check file type
IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]
def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)

# gather image file paths
def make_dataset(dir):
    images = []
    assert os.path.isdir(dir), '%s is not a valid directory' % dir
    
    for root, _, fnames in sorted(os.walk(dir)):
        for fname in fnames:
            if is_image_file(fname):
                path = os.path.join(root, fname)
                images.append(path)
    
    return images

# load image
def loadImage(path, size=(512,512), flgShow=False):
    image_pil = Image.open(path).convert("RGBA")
    image_pil = image_pil.resize(size)
    image_np = np.array(image_pil)
    if flgShow:
        vis.image(image_np.transpose(2, 0, 1), opts=dict(title="Image"), win=0)
    return image_np

# remove background
def removeBackground(image_np):
    flatten_np = image_np.reshape((-1, 4))
    idx = np.argwhere(flatten_np[:,3]==0)
    result_np = np.delete(flatten_np, idx, axis=0)[:,:3]
    return result_np

def rgb2lab(RGB):
    RGB = RGB/255.
    
    # https://en.wikipedia.org/wiki/SRGB
    # http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    XYZ = np.zeros_like(RGB)
    XYZ[RGB>0.04045] = ((RGB[RGB>0.04045]+0.055)/(1.055))**2.4
    XYZ[RGB<=0.04045] = RGB[RGB<=0.04045]/12.92
    m = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    XYZ = np.matmul(m, XYZ.T).T
    
    # https://en.wikipedia.org/wiki/CIELAB_color_space
    # Observer= 2°, Illuminant= D65
    n = np.array([95.047, 100.0, 108.883]).reshape(1, 3)
    XYZ = XYZ * 100. / n
        
    # xyz = x/xn, y/yn, z/zn
    Lab = np.zeros_like(XYZ)
    Lab[XYZ>0.008856] = XYZ[XYZ>0.008856]**(1./3.)
    Lab[XYZ<=0.008856] = (7.787 * XYZ[XYZ<=0.008856]) + (4. / 29.)
    
    Lab = np.array([ 116. * Lab[:,1] - 16.,
                     500. * (Lab[:,0] - Lab[:,1]),
                     200. * (Lab[:,1] - Lab[:,2])]).T.round(decimals=4)
    return Lab

def lab2rgb(Lab):
    Lab = np.array([(Lab[:,0]+16.)/116. + (Lab[:,1]/500.),
                    (Lab[:,0]+16.)/116.,
                    (Lab[:,0]+16.)/116. - (Lab[:,2]/200.)]).T
    XYZ = np.zeros_like(Lab)
    XYZ[Lab>0.206897] = Lab[Lab>0.206897]**(3.)
    XYZ[Lab<=0.206897] = (0.128416 * (Lab[Lab<=0.206897] - 0.137931))
    
    n = np.array([95.047, 100.0, 108.883]).reshape(1, 3)
    XYZ = XYZ * n / 100.
    
    m = np.array([[3.2404542, -1.5371385, -0.4985314], [-0.9692660,  1.8760108,  0.0415560], [0.0556434, -0.2040259,  1.0572252]])
    XYZ = np.matmul(m, XYZ.T).T
    
    RGB = np.zeros_like(XYZ)
    RGB[XYZ>0.0031308] = 1.055 * (XYZ[XYZ>0.0031308]**(1./2.4)) - 0.055
    RGB[XYZ<=0.0031308] = 12.92 * XYZ[XYZ<=0.0031308]
    RGB[RGB<0] = 0.
    RGB[RGB>1] = 1.
    
    RGB = (RGB*255).astype(np.uint8)
    return RGB

def sparse2cube(unique, counts, n_bins, flgNormalize=True):
    image_tensor = np.zeros((n_bins,n_bins,n_bins), dtype=float)
    counts_float = counts.astype(np.float32)
    ratio = counts_float/counts_float.sum()
    image_tensor[unique[:,0], unique[:,1], unique[:,2]] = ratio if flgNormalize else counts
    return image_tensor

def cube2sparse(image_tensor):
    r, g, b = np.where(image_tensor > 0)
    unique = np.stack([r,g,b], axis=1)
    counts = image_tensor[r, g, b]
    return unique, counts

def showImageTensor(vis, unique, counts, flgNormalize=True, title="Image tensor", win=1):
    if flgNormalize:
        ratio = 200.*counts
    else:
        counts_float = counts.astype(np.float32)
        ratio = 200.*counts_float/counts_float.sum()
    # show image tensor
    trace = dict(x=unique[:,0].tolist(), y=unique[:,1].tolist(), z=unique[:,2].tolist(), mode="markers", type='scatter3d',
                marker={'color': unique.tolist(), 'symbol': 'circle', 'size': ratio.tolist(), 'line': {'color': 'black'}},
                text=counts.tolist(), hoverinfo='x+y+z+text', name='1st Trace')
    layout = dict(title=title, height=512, width=512, 
                scene={'xaxis':{'title': 'R', 'range':[0,255], 'zeroline': True, 'zerolinewidth': 5},
                        'yaxis':{'title': 'G', 'range':[0,255], 'zeroline': True, 'zerolinewidth': 5},
                        'zaxis':{'title': 'B', 'range':[0,255], 'zeroline': True, 'zerolinewidth': 5}})
    vis._send({'data': [trace], 'layout': layout, 'win': win})

def produceGaussianKernel(kernel_size=3, sigma=0.75, channels=1):
    mean = (kernel_size - 1)/2.
    variance = sigma**2.
    channels = 1
    inputs = torch.zeros(1, 1, 3, 3, 3)
    inputs[..., 1, 1, 1] = 1.
    arange = torch.arange(kernel_size).float()
    gaussian_kernel = (1./(variance*(2.*math.pi)**(1/2))) * torch.exp(-((arange - mean)/variance)**2. / 2.)
    slice = torch.stack([torch.zeros(3), gaussian_kernel, torch.zeros(3)])
    cube = torch.stack([torch.zeros(3,3), slice, torch.zeros(3,3)])
    filter_x = cube.view(1, 1, 3, 3, 3)
    filter_y = cube.transpose(1,2).view(1, 1, 3, 3, 3)
    filter_z = cube.transpose(0,2).view(1, 1, 3, 3, 3)
    result = torch.nn.functional.conv3d(inputs, filter_x, padding=1)
    result = torch.nn.functional.conv3d(result, filter_y, padding=1)
    result = torch.nn.functional.conv3d(result, filter_z, padding=1)
    return result/result.sum()

def save_image(image_numpy, image_path):
  n_images = image_numpy.shape[0]
  length = math.ceil(math.sqrt(n_images))
  if n_images < length**2:
    pad = np.zeros((length**2-n_images, 64, 64, 4), dtype=np.uint8)
    images = np.concatenate((image_numpy, pad), axis=0)
  else:
    images = image_numpy
  
  horizons = []
  for i in range(length):
    horizon = np.hstack(images[i*length:(i+1)*length])
    horizons.append(horizon)
  cated = np.vstack(horizons)
  image_pil = Image.fromarray(cated)
  image_pil.save(image_path)  

class gaussian_blur():
    def __init__(self, gaussian_kernel):
        self.gaussian_filter = torch.nn.Conv3d(in_channels=1, out_channels=1, kernel_size=3, padding=1, groups=1, bias=False)
        self.gaussian_filter.weight.data = gaussian_kernel.double()
        self.gaussian_filter.weight.requires_grad = False
    
    def gaussian_blur(self, image_np):
        blurred_tensor = self.gaussian_filter(torch.from_numpy(image_np))
        return blurred_tensor.numpy()
