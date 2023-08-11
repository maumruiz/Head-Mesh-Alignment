# WE WANT TO ALIGN SOURCE TO TARGET MESH
import numpy as np

# Compute the centroid of a point cloud
# points is a 3xN matrix
# Outputs a 3x1 vector representing the centroid
def getCentroid(points):
    return np.mean(points, 1)[:, np.newaxis] # Mean of column vectors

# Calculate the correspondences between points in two sets of 3D data points
# by performing a nearest neighbor search.
def getCorrespondences(X, Y, Cx, Cy, Rx):
    Xtransformed = np.dot(Rx, X-Cx)
    Ytransformed = Y - Cy

    # Calculate pairwise euclidean distance between points in X and Y
    xy = np.dot(Xtransformed.T, Ytransformed)
    xx = np.sum(Xtransformed*Xtransformed, 0)
    yy = np.sum(Ytransformed*Ytransformed, 0)
    D = (xx[:, np.newaxis] + yy[np.newaxis, :]) - 2*xy

    # Find nearest correspondences
    indexes = np.argmin(D, 1)
    return indexes