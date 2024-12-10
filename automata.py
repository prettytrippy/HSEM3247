import numpy as np
from scipy.signal import fftconvolve
from scipy.ndimage import gaussian_filter

class Automata:
    def __init__(self, n, beauty_factor=0.5):
        kernel_size = 31
        self.n = n
        self.kernel_size = kernel_size
        self.beauty_factor = beauty_factor
        self.feedback_factor = 0.9 + 0.1 * beauty_factor
        self.excitation = 0.1 + 0.1 * (1 - beauty_factor)
        self.noise_factor = 0.01 + 0.01 * (1 - beauty_factor)
        self.sigma = 1.0 + 1.0 * (1 - beauty_factor)
        self.kernel = self.init_kernel(kernel_size, self.sigma)
        self.grid = self.init_grid()

    def init_kernel(self, size, sigma):
        ax = np.linspace(-(size // 2), size // 2, size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        kernel = kernel - kernel.mean()
        return kernel / np.sum(np.abs(kernel))

    def init_grid(self):
        grid = np.random.rand(self.n, self.n)
        grid = gaussian_filter(grid, sigma=self.n // 10)
        grid = 2 * (grid - np.min(grid)) / (np.max(grid) - np.min(grid)) - 1
        return grid

    def generate_frame(self):
        convolved = fftconvolve(self.grid, self.kernel, mode='same')
        new_grid = (1 - self.feedback_factor) * convolved + self.feedback_factor * self.grid
        new_grid = np.tanh(new_grid)
        noise = gaussian_filter((np.random.rand(self.n, self.n) - 0.5) * self.noise_factor, sigma=self.n // 20)
        self.grid = new_grid + noise
        return self.grid

