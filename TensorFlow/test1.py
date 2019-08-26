import tensorflow as tf
import numpy as np
import imageio
from matplotlib import pyplot as plt

mit_logo = np.array(imageio.imread("1280px-MIT_logo.png", as_gray = True))
plt.imshow(mit_logo)

h, w = mit_logo.shape
ww = np.random.rand(h,w)
W = np.where(ww > 0.95, 1, 0)

plt.imshow(W * mit_logo)

r = min(h, w)
