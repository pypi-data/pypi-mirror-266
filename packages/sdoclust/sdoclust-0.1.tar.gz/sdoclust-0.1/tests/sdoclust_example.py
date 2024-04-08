from sklearn import datasets
import numpy as np
import sdoclust as sdo

np.random.seed(1)

# Generate data
x, y = datasets.make_circles(n_samples=5000, factor=0.3, noise=0.1)

# SDOclust clustering
p = sdo.SDOclust().fit_predict(x)

fig = plt.figure()
plt.scatter(x[:,0],x[:,1], s=10, cmap='coolwarm', c=p)
plt.title('SDOclust clustering', fontsize=14)
plt.show()
