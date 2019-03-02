from scipy.sparse import coo_matrix
import numpy as np

import math_utils as mu


# import parity_polytope


class ADMM:
    def __init__(self, parity_mtx, max_iter):
        self.xx, self.yy = np.where(parity_mtx)
        self.var_deg = parity_mtx.sum(axis=0)
        self.mu = 1.
        eps = 1 / max_iter
        thresh = (eps ** 2) * parity_mtx.sum()
        self.is_close = lambda a_1, a_2: ((a_1 - a_2) ** 2).sum() < thresh
        self.coo = lambda d_: coo_matrix((d_, (self.xx, self.yy)), shape=parity_mtx.shape)
        self.sum_cols = lambda d_: mu.sum_axis(self.coo(d_), 0)

    def decode(self, y, gamma):
        xx, yy = self.xx, self.yy
        x_hat, z_old, lambda_vec = y, yy * 0., yy * 0.
        iter_count = 0

        while 1:
            # update x
            x_hat[:] = np.clip((self.sum_cols(z_old - lambda_vec / self.mu)
                                - gamma / self.mu) / self.var_deg, 0., 1.)
            x_hat_xx = x_hat[xx]

            # update z
            v_vec = x_hat_xx + lambda_vec / self.mu
            z_new = v_vec  # parity_polytope.proj_pp(v_vec_sparse)

            # update lambda
            lambda_vec[:] = lambda_vec + self.mu * (x_hat_xx - z_new)

            if self.is_close(x_hat_xx, z_new) and \
                    self.is_close(z_old, z_new): return mu.pseudo_to_real_cw(x_hat)
            z_old = z_new
            iter_count += 1
