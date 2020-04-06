import torch
from collections import OrderedDict
import data
from network import Generator
import torchvision.utils as vutils

class Adaptor():
	def name(self):
		return 'Adaptor'

	def __init__(self):
		# net = Generator(ch_style=3, ch_content=1).cuda()
		# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		device = torch.device("cpu")
		net = Generator(ch_style=3, ch_content=1).to(device)
		net.load_state_dict(torch.load('model_weights/latest_G.pth', map_location=torch.device('cpu')))
		net.eval()
		self.net = net

	def set_input(self, inputs):
		self.input_icon = inputs['icon']
		self.input_grad = inputs['grad']
		self.icons = inputs['icon']
		self.grads = inputs['grad'][:, 0:1, :, :].repeat(12, 1, 1, 1)	#16--->10

	def test(self):
		pass

	def get_current_visuals(self):
		with torch.no_grad():
			# fake = self.net(self.icons.cuda(0), self.grads.cuda(0))
			# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
			device = torch.device("cpu")
			fake = self.net(self.icons.to(device), self.grads.to(device))
		# vutils.save_image(self.icons, 'input_style.png', normalize=True, range=(-1, 1))
		# vutils.save_image(self.grads, 'input_contour.png', normalize=True, range=(-1, 1))
		# vutils.save_image(fake, 'output.png', normalize=True, range=(-1, 1))
		# print(fake.shape)
		# input('pause')
		fake = data.tensor2im_batch(fake)

		icon = data.tensor2im_batch(self.icons)
		grad = data.tensor2im_batch(self.input_grad)
		ret_visuals = OrderedDict([('icon', icon), ('grad', grad), ('fake', fake)])
		return ret_visuals
