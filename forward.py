import torch
import os
import math
import data
import numpy as np
import torchvision.transforms as transforms
from adaptor import Adaptor
from PIL import Image, ImageChops

class forwardModel():
	def __init__(self):
		self.gan = Adaptor()
		self.dataloader = data.IconDataset("./datasets", batchSize=12)
		
		self.transform = data.get_transform()
		self.edge_transform = data.get_edge_transform()
		self.input = self.dataloader[0]
		
	def set_edge(self, edge):
		# replace edge
		edge_pil = Image.fromarray(edge)
		self.input['grad'] = self.edge_transform(edge_pil).unsqueeze(0)
		self.gan.set_input(self.input)
	
	def set_icon(self, icon):
		# replace icon
		icon_pil = Image.fromarray(icon)
		self.input['icon'] = self.transform(icon_pil)
		self.gan.set_input(self.input)
	
	def resample(self, semantic, fix_idx=[]):
		input = self.dataloader[semantic]
		for idx in fix_idx:
			input['icon'][idx] = self.input['icon'][idx]
		self.input['icon'] = input['icon']
		self.gan.set_input(self.input)
	
	def get_input(self):
		return self.input
	
	def forward(self):
		error = self.gan.test()
		images = self.gan.get_current_visuals()
		
		result_fake = []
		result_input = []
		for name, image in images.items():
			if name == "fake" or name == "fake_c":
				for img in image:
					result_fake.append(Image.fromarray(img))
				np_fake = image
			elif name == "icon":
				result_input = []
				for img in image:
					result_input.append(Image.fromarray(img))
				np_real = image
			if name == "fake_u":
				result_input = []
				for img in image:
					result_input.append(Image.fromarray(img))
		return result_fake, result_input, error, np_fake, np_real
		
	def get_k(self):
		return self.dataloader.get_k()


def align_image(image_numpy, n_user_icon):
	n_images = image_numpy.shape[0]
	length = math.ceil(math.sqrt(n_images))
	
	#if n_user_icon < length**2:
	#    pad = np.zeros((length**2-n_user_icon, 64, 64, 3), dtype=np.uint8)
	#    images = np.concatenate((image_numpy[:n_user_icon], pad), axis=0)
	#else:
	#    images = image_numpy
	
	images = image_numpy[16:]
	
	horizons = []
	for i in range(length-2):
		horizon = np.vstack(images[i*length:(i+1)*length])
		horizons.append(horizon)
	cated = np.hstack(horizons)
	image_pil = Image.fromarray(cated)
	return image_pil
		
def cat(list):
	return torch.cat(list)
