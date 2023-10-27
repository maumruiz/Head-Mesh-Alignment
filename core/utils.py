import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist

def calculateMaxEucDist(vertices):
    hull = ConvexHull(vertices)

    # Extract the points forming the hull
    hullpoints = vertices[hull.vertices,:]

    # Naive way of finding the best pair in O(H^2) time if H is number of points on hull
    hdist = cdist(hullpoints, hullpoints, metric='euclidean')

    # Get the farthest apart points
    bestpair = np.unravel_index(hdist.argmax(), hdist.shape)

    #Print them
    # print([hullpoints[bestpair[0]],hullpoints[bestpair[1]]])

    # Calculate the distance between the best pair
    v1 = hullpoints[bestpair[0]]
    v2 = hullpoints[bestpair[1]]
    maxDist = np.linalg.norm(v2-v1)
    return maxDist

def getCentroid(points):
    return np.mean(points, 0)[:, np.newaxis]