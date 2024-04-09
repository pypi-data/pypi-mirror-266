import pandas as pd
from time import time

import logging
from time import time

import numpy as np
import pandas as pd
import tensorflow as tf

from kolibri.backend.bn.utils import print_summary, set_seed, rank_transform, mean_var_normalize


class NoTears:
    """
    NO-TEARS model with augmented Lagrangian gradient-based optimization
    """
    _logger = logging.getLogger(__name__)

    def __init__(self, seed=8, use_float64=False):
        self.print_summary = print_summary
        self.seed = seed
        set_seed(seed)
        self.tf_float_type = tf.dtypes.float64 if use_float64 else tf.dtypes.float32

        # Constants
        self.INIT_RHO = 1.0
        self.RHO_MULTIPLY = 10.0
        self.RHO_THRES = 1e+12
        self.INIT_ITER = 3
        self.ITER_STEP = 200
        self.MAX_ITER = 20

        # Placeholder vars
        tf.keras.backend.clear_session()
        self.n = None
        self.d = None
        self.l1_lambda = None
        self.rho = None
        self.alpha = None
        self.X = None
        self.W_prime = None

        self._logger.debug('Finished building NoTears model')

    @tf.function
    def loss(self):
        mse_loss = self.mse_loss()
        h = self.h()
        return 0.5 / self.n * mse_loss \
            + self.l1_lambda * tf.norm(tensor=self.W_prime, ord=1) \
            + self.alpha * h + 0.5 * self.rho * h * h

    @tf.function
    def h(self):  # Acyclicity
        return tf.linalg.trace(tf.linalg.expm(self.W_prime * self.W_prime)) - self.d

    @tf.function
    def mse_loss(self):
        X_prime = tf.matmul(self.X, self.W_prime)
        return tf.square(tf.linalg.norm(tensor=self.X - X_prime))

    def train(self, X, l1_lambda=0, learning_rate=1e-3,
              graph_thres=0.3, h_thres=0.25, h_tol=1e-8):
        self._initialize_vars(X, l1_lambda)
        train_opt = tf.keras.optimizers.Adam(learning_rate=learning_rate)

        self._logger.info(f'Started training for {self.MAX_ITER} iterations')
        print(f'Started training for {self.MAX_ITER} iterations')
        h, h_new = np.inf, np.inf
        iiii=0
        for epoch in range(1, self.MAX_ITER + 1):
            while self.rho.numpy() < self.RHO_THRES:
                print(iiii)
                iiii+=1

                self._logger.info(f'rho {self.rho.numpy():.3E}, alpha {self.alpha.numpy():.3E}')
                print(f'rho {self.rho.numpy():.3E}, alpha {self.alpha.numpy():.3E}')
                self._train_step(train_opt)
                h_new = self.h().numpy()
                if h_new > h_thres * h:
                    self.rho.assign(self.rho.numpy() * self.RHO_MULTIPLY)
                else:
                    break

            h = h_new
            self.alpha.assign_add(self.rho.numpy() * h)

            if h < h_tol and epoch > self.INIT_ITER:
                self._logger.info(f'Early stopping at {epoch}-th iteration')
                print(f'Early stopping at {epoch}-th iteration')
                break

        return self.W_prime.numpy()

    def _initialize_vars(self, X, l1_lambda):
        self.X = tf.convert_to_tensor(X, dtype=self.tf_float_type)
        self.n = tf.constant(self.X.shape[0], dtype=self.tf_float_type)
        self.d = tf.constant(self.X.shape[1], dtype=self.tf_float_type)
        self.l1_lambda = tf.constant(l1_lambda, dtype=self.tf_float_type)
        self.rho = tf.Variable(self.INIT_RHO, dtype=self.tf_float_type)
        self.alpha = tf.Variable(0.0, dtype=self.tf_float_type)
        W = tf.zeros([self.d, self.d], self.tf_float_type)
        self.W_prime = tf.Variable(self._preprocess_graph(W), dtype=self.tf_float_type, trainable=True)

    def _train_step(self, train_opt):
        for _ in range(self.ITER_STEP):
            train_opt.minimize(self.loss, [self.W_prime])

    def _preprocess_graph(self, W):
        return tf.linalg.set_diag(W, tf.zeros(W.shape[0], dtype=self.tf_float_type))


if __name__ == '__main__':
    data = pd.read_csv(
        "/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/criticality_agent/data/criticality_data2.csv")

    X = data.values.astype(np.float32)
    X = rank_transform(X)
    X = mean_var_normalize(X)

    n, d = X.shape
    tic = time()

    model = NoTears()
    W_est = model.train(X)
    time_span = time() - tic
    print(time_span)
    print(W_est)
    print('Finished training model')

