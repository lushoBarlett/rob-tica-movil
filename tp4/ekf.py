""" Written by Brian Hou for CSE571: Probabilistic Robotics (Winter 2019)
"""

import numpy as np

from utils import minimized_angle


class ExtendedKalmanFilter:
    def __init__(self, mean, cov, alphas, beta):
        self.alphas = alphas
        self.beta = beta

        self._init_mean = mean
        self._init_cov = cov
        self.reset()

    def reset(self):
        self.mu = self._init_mean
        self.sigma = self._init_cov

    def update(self, env, u, z, marker_id):
        """Update the state estimate after taking an action and receiving a landmark
        observation.

        u: action
        z: landmark observation
        marker_id: landmark ID
        """
        # Models
        g = lambda: env.forward(self.mu, u)
        h = lambda: env.observe(self.mu, marker_id)

        G = env.G(self.mu, u)
        H = env.H(self.mu, marker_id)

        rot1, trans, rot2 = u.ravel()

        a1, a2, a3, a4 = self.alphas

        M = np.array([
            a1 * rot1**2 + a2 * trans**2, 0, 0,
            0, a3 * trans**2 + a4 * (rot1**2 + rot2**2), 0,
            0, 0, a1 * rot2**2 + a2 * trans**2,
        ]).reshape(3, 3)

        V = env.V(self.mu, u)
        R = V @ M @ V.T
        Q = self.beta

        # Prediction step
        pmu = g()
        psigma = G @ self.sigma @ G.T + R

        K = (
            psigma @
            H.T @
            np.linalg.inv(H @ psigma @ H.T + Q)
        )

        # Correction step
        anglediff = minimized_angle(z[0][0] - h()[0][0])
        print("Rrl:",
              round(z[0][0] / np.pi * 180, 0),
              "\tPd:",
              round(h()[0][0] / np.pi * 180, 0),
              "\tE:",
              round(anglediff / np.pi * 180, 0))
        print("Correction", K * anglediff)
        self.mu = pmu + K * anglediff
        self.sigma = (np.eye(3) - K @ H) @ psigma

        return self.mu, self.sigma

