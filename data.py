import torch
import os
import math
import random
import numpy as np
import torchvision.transforms as transforms
from PIL import Image

IMG_EXTENSIONS = [
	'.jpg', '.JPG', '.jpeg', '.JPEG',
	'.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]

IMG_RESOLUTION = 64   #分辨率

def is_image_file(filename):
	return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)
	
def make_dataset(dir):
	images = []
	assert os.path.isdir(dir), '%s is not a valid directory' % dir

	for root, _, fnames in sorted(os.walk(dir)):	#os.walk()---文件遍历器
		for fname in fnames:
			if is_image_file(fname):
				path = os.path.join(root, fname)
				images.append(path)

	return images
	
def get_transform():
	transform_list = []
	transform_list.append(transforms.Pad(32, (255, 255, 255))) # 512x512 -> 640x640
	transform_list.append(transforms.Resize([IMG_RESOLUTION, IMG_RESOLUTION], Image.BICUBIC))
	transform_list += [transforms.ToTensor(),
					transforms.Normalize((0.5, 0.5, 0.5),
											(0.5, 0.5, 0.5))]
	return transforms.Compose(transform_list)

def get_edge_transform():
	transform_list = []
	transform_list.append(transforms.Resize([IMG_RESOLUTION, IMG_RESOLUTION], Image.BICUBIC))
	transform_list += [transforms.ToTensor(),
					transforms.Normalize((0.5, 0.5, 0.5),
											(0.5, 0.5, 0.5))]
	return transforms.Compose(transform_list)

class IconDataset(torch.utils.data.Dataset):
	def __init__(self, dataroot, batchSize=10):
		super(IconDataset, self).__init__()
		self.root = dataroot
		self.image_paths = make_dataset(self.root)
		self.image_paths = sorted(self.image_paths)
		self.image_size = len(self.image_paths)
		
		self.labels = np.load(os.path.join(self.root, "labels.npy"))
		self.cb_images = np.load(os.path.join(self.root, "combanation_image.npy"))
		self.k = max(self.labels)+1
		
		self.k_image_paths = []
		for k in range(self.k):
			self.k_image_paths.append([])
		for c, image_path in zip(self.labels, self.image_paths):
			self.k_image_paths[c].append(image_path)
		
		self.transform = get_transform()
		self.batchSize = batchSize
		self.semantic_idx = [0,4,8,12,16,20,24,28,32,36,40]
		
	#def __getitem__(self, index):
	#    bs = self.batchSize
	#    image_paths = self.image_paths[index*bs:(index+1)*bs]
	#    images = [Image.open(image_path).convert('RGB') for image_path in image_paths]
	#    icons = []
	#    for image in images:
	#        icons.append(self.transform(image))
	#    icon = torch.stack(icons, dim=0)
	#    #diff = self.get_diff(label)
	#    return {'icon': icon}
	
	def __getitem__(self, semantic):
		bs = self.batchSize
		start = self.semantic_idx[semantic]
		end = self.semantic_idx[semantic+1]
		n_cb = end - start
		n_image_each_cb = int(bs / n_cb + 0.5)
		#print("semantic {} start {} end {} n_cb {} n_image_each_cb {}".format(semantic, start, end, n_cb, n_image_each_cb))
		icons = []
		for idx in range(start, end):
			unique = np.unique(self.cb_images[idx])
			np.random.shuffle(unique)
			indexs = unique[:n_image_each_cb]
			image_paths = [self.image_paths[index] for index in indexs]
			images = [Image.open(image_path).convert('RGB') for image_path in image_paths]
			for image in images:
				icons.append(self.transform(image))
		icon = torch.stack(icons, dim=0)
	
		return {'icon': icon}
	
	def get_similar(self, labels):
		image_paths = []
		for label in labels:
			rand_idx = np.random.randint(len(self.k_image_paths[label]), size=1)
			image_paths.append(self.k_image_paths[label][int(rand_idx)])
		images = [Image.open(image_path).convert('RGB') for image_path in image_paths]
		icons = []
		for image in images:
			icons.append(self.transform(image))
		icon = torch.stack(icons, dim=0)
		return icon, image_paths
		return labels
		
	def __len__(self):
		return int(len(self.image_paths)/self.batchSize)
		
	def get_k(self):
		return self.k

	def name(self):
		return 'IconDataset'
		
def tensor2im(image_tensor, imtype=np.uint8):
	image_numpy = image_tensor.cpu().float().numpy()
	if image_numpy.shape[0] == 1:
		image_numpy = np.tile(image_numpy, (3, 1, 1))
	image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
	return image_numpy.astype(imtype)
	
def tensor2im_batch(image_tensor, imtype=np.uint8):
	image_numpy = image_tensor.cpu().float().numpy()
	if image_numpy.shape[1] == 1:
		image_numpy = np.tile(image_numpy, (1, 3, 1, 1))
	image_numpy = (np.transpose(image_numpy, (0, 2, 3, 1)) + 1) / 2.0 * 255.0
	return image_numpy.astype(imtype)
	
def save_image(image_numpy, image_path):
	n_images = image_numpy.shape[0]
	length = math.ceil(math.sqrt(n_images))
	
	horizons = []
	for i in range(length):
		horizon = np.hstack(image_numpy[i*length:(i+1)*length])
		horizons.append(horizon)
	cated = np.vstack(horizons)
	image_pil = Image.fromarray(cated)
	image_pil.save(image_path)
	return image_pil
