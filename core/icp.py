# WE WANT TO ALIGN SOURCE TO TARGET MESH
import numpy as np
from simpleicp import PointCloud, SimpleICP

MAX_ITERS = 200

# Compute the centroid of a point cloud
# points is a 3xN matrix
# Outputs a 3x1 vector representing the centroid
def getCentroid(points):
    return np.mean(points, 1)[:, np.newaxis] # Mean of column vectors

# Calculate the correspondences between points in two sets of 3D data points
# by performing a nearest neighbor search.
# INPUTS
# - X: 3 x M matrix
# - Y: 3 x N matrix
# - Cx and Cy: 3 x 1 vectors
# - Rx: 3 x 3 estimated rotation matrix for X
# OUTPUT:
# - indexes: an array N with correspondences
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

# Find the best fitting similarity transformation (rotation and translation) between two
# sets of 3D data points 'X' and 'Y' given a set of correspondence indices.
def getProcrustesAlignment(X, Y, idx):
    # Calculate centroids
    Cx = getCentroid(X)
    Cy = getCentroid(Y[:, idx])
    # Center the data
    X_ = X - Cx
    Y_ = Y[:, idx] - Cy
    # Compute Singular Value Decomposition
    (U, S, Vt) = np.linalg.svd(np.dot(Y_, X_.T)) 
    # Calculate the rotation by mutiplying the left singular vectors 'U' with the
    # transpose of the right singular vectors 'R'
    R = np.dot(U, Vt)
    return (Cx, Cy, R)

# Iteratively find corresponcences and compute procrustres alignment until convergence
def execICP(X, Y):
    CxUpdates = []
    CyUpdates = []
    RxUpdates = []
    Cx = getCentroid(X)
    Cy = getCentroid(Y)
    Rx = np.eye(3, 3)
    lastC = Cy
    counter = 1
    for i in range(MAX_ITERS):
        if(counter % 5 == 0):
            print(f'Computing iteration {counter}...')
        idx = getCorrespondences(X, Y, Cx, Cy, Rx)
        (Cx, Cy, Rx) = getProcrustesAlignment(X, Y, idx)
        CxUpdates.append(Cx)
        CyUpdates.append(Cy)
        RxUpdates.append(Rx)
        d = Cy - lastC
        if np.sum(d*d) < 0.000000001:
            break;
        lastC = Cy
    print(f"ICP converged after {len(CxUpdates)} iterations with an error of {np.sum(d*d)}")
    return (CxUpdates, CyUpdates, RxUpdates)

def execICP(X, Y):
    pc_fix = PointCloud(X, columns=["x", "y", "z"])
    pc_mov = PointCloud(Y, columns=["x", "y", "z"])

    icp = SimpleICP()
    icp.add_point_clouds(pc_fix, pc_mov)
    H, X_mov_transformed, rigid_body_transformation_params, distance_residuals = icp.run(max_overlap_distance=1)
    Rx = H[0:3, 0:3]
    tx =  H[0:3, 3][:, np.newaxis]
    return Rx, tx