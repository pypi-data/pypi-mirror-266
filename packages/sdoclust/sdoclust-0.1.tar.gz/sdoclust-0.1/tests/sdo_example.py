from sklearn import datasets
import numpy as np
import sdoclust as sdo

np.random.seed(1)

# Generate data
x, y = datasets.make_circles(n_samples=5000, factor=0.3, noise=0.1)

# SDO outlier scoring
s = sdo.SDO().fit_predict(x)

# plotting results
import matplotlib.pyplot as plt
fig = plt.figure()
plt.scatter(x[:,0],x[:,1], s=10, cmap='coolwarm', c=s)
plt.colorbar(ticks=[np.min(s), np.max(s)])
plt.title('SDO outlierness scores')
plt.show()
