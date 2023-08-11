import numpy as np

# Compute the centroid of a point cloud
# points is a 3xN matrix
# Outputs a 3x1 vector representing the centroid
def getCentroid(points):
    return np.mean(points, 1)[:, np.newaxis] # Mean of column vectors
