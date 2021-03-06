import matplotlib.pyplot as plt
import numpy as np


class GP:

    def __init__(self,v=None,l=None,sigma=None,k_func=None):
        self.k_func = k_func
        self.v = v
        self.l = l
        self.sigma = sigma

        # Holder variables
        self.mean = 0
        self.cov = None
        self.X = None
        self.X_star = None
        self.Y = None
        self.noise = None

        # covariance matrices
        self.K_x_x = None
        self.K_x_x_inv = None
        self.K_s_s = None
        self.K_s_x = None

    def k_gauss(self,x1, x2, sigma=0.5):
        diff = x1 - x2
        return np.exp(-(np.dot(diff,diff))/ (2 * sigma))

    def k_mat(self,k, X, Y):
        '''
        allowing for N x M kernel for convience in GP problem
        :param k:
        :param X:
        :param Y:
        :return:
        '''

        N = X.shape[0]
        M = Y.shape[0]
        K = np.zeros((N, M))
        for i in range(0, N):
            for j in range(0, M):
                v = k(X[i], Y[j])
                K[i, j] = v
        return np.matrix(K)

    def plot_sample(self,mu, K, N):
        '''
        Func for plotting dist of functions
        :param mu: Array of functions describing the mean
        :param K: Covariant matrix
        :param N: number of samples
        :return:
        '''
        f = np.random.multivariate_normal(mu, K, N)
        plt.plot(f.T)
        plt.show()

    def sample_discreet_env(self,env, N):
        '''
        Function to randomly grab samples from
        the environment
        :param env: Gym object
        :return:
        '''

        min_pos = env.min_position
        max_pos = env.max_position
        max_speed = env.max_speed
        goal_position = env.goal_position

        samples = []

        for n in range(N):
            sample_pos = np.random.uniform(min_pos, max_pos)

            sample_vel = np.random.uniform(0, max_speed)

            s = (sample_pos, sample_vel)

            action = np.random.randint(3)

            env.env.state = s  # set gym environment to the state to sample from

            env.step(action)

            s_p = env.env.state  # new state from the environment

            samples.append((s, action, s_p))

        return samples

    def train(self,X,X_star,Y):

        self.X = X.copy()

        N = self.X.shape[0]

        if self.k_func is None:

            self.k_func = self.k_gauss

        self.noise = np.eye(N) * self.sigma

        self.K_x_x = self.k_mat(self.k_func,X,X)

        self.cov = self.K_x_x

        #f = np.random.multivariate_normal(np.zeros((N,)),self.K_x_x,1) # sample function

        if len(Y.shape) == 1:
            self.Y = np.matrix(Y.reshape((N,1)))
        else:
            self.Y = np.matrix(Y.reshape((N,Y.shape[1])))

        self.K_x_x_inv = np.linalg.inv(self.K_x_x + self.noise)

        self.K_s_s = self.k_mat(self.k_func, X_star, X_star)

        self.K_s_x = self.k_mat(self.k_func, X_star, self.X)

        self.mean = self.K_s_x * self.K_x_x_inv * self.Y

        self.cov = self.K_s_s - self.K_s_x * self.K_x_x_inv * self.K_s_x.T

    def plot(self):

        mean = np.array(self.mean)
        cov = np.array(self.cov)

        upper = mean + 2 * np.diag(cov).reshape((mean.shape[0], 1))
        lower = mean - 2 * np.diag(cov).reshape((mean.shape[0], 1))

        #plt.scatter(X, np.reshape(np.array(y), (N,)))

        plt.plot(self.X_star, mean, color='red')
        plt.plot(self.X_star, upper, color='blue')
        plt.plot(self.X_star, lower, color='blue')
        plt.show()

    def plot_predict(self,Y_actual):

        x_axis = [i for i in range(self.X_star.shape[0])]

        y_hat = np.array(self.mean)

        y_hat_pos = np.reshape(y_hat[:, 0], (len(self.mean),))
        y_hat_vel = np.reshape(y_hat[:, 1], (len(self.mean),))

        plt.plot(x_axis, Y_actual[:, ], color='red')
        plt.plot(x_axis, y_hat_pos, color='blue')

        MSE = ((Y_actual - y_hat) ** 2).mean()

        print('Sum squared error {}'.format(MSE))

        plt.show()

        plt.plot(x_axis, Y_actual[:, 1], color='red')
        plt.plot(x_axis, y_hat_vel, color='blue')

        plt.show()

        print('')

    def predict(self,X_star):

        #K_s_s = self.k_mat(self.k_func,X_star,X_star)

        K_s_x = self.k_mat(self.k_func,X_star,self.X)

        mean = K_s_x*self.K_x_x_inv*self.Y

        #cov = K_s_s - K_s_x*self.K_x_x_inv*K_s_x.T

        return np.array(mean)[0][0]






