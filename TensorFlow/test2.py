import tensorflow as tf
import numpy as np
import imageio
from matplotlib import pyplot

mit_logo = np.array(imageio.imread("1280px-MIT_logo.png",as_gray=True))
pyplot.imshow(mit_logo)