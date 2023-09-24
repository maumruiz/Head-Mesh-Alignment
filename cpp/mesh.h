#ifndef _MESH_H_
#define _MESH_H_

#define _CRT_SECURE_NO_DEPRECATE //i won't use fopen_s; so, don't warn me

#include <iostream>
#include <vector>
#include <set>
//#include <queue>
using namespace std;

#include "Eigen/Dense" //dense matrices
//#include "Eigen/Sparse" //sparse matrices
using namespace Eigen;

//#include <time.h>

//#define KDTREE_FOR_CLOSEST_PNTS //use nlogm kd-tree for closest point search instead of the simple nm exhaustive search way b/w 2 pnt sets of sizes n & m

#define EXP							2.718281828f
#define PI							3.141592653f
#define INF							(float) 1e38 //100000000.0f //largest float is 3.4x10^38; 1e+38 (or 1e38) also works (1e39 makes overflow; prints 1.#INF) but then treats as a double and gives warning when i compare/assign w/ a float; solved using (float) casting
#define SMALL						(float) 0.5 //1e-2 //1e-5
//in ICPRansac(), compute MSE using either all vertices or all samples or current triplet
#define ALL_VERTS					1
#define ALL_SAMPLES					2
#define CURRENT_TRIPLET				3

struct Triangle
{
	// tris[idx] is this tri
	int idx;

	// idx to verts forming this tri
	int v1i, v2i, v3i;
	
	Triangle(int i, int i1, int i2, int i3) : idx(i), v1i(i1), v2i(i2), v3i(i3) {};
};

struct Vertex
{
	// verts[idx] is this vert
	int idx, closestVertIdx; //closest mesh vertex to this vert during the current ICP iteration

	// coordinates and descriptor value
	float* coords, desc, * color, * coordsOriginal, * coordsBest;

	// idx to vert neighbors of this vert (use set for efficient duplicate entry prevention)
	typedef set< int, std::less<int> > vertNeighborsIS; 
    vertNeighborsIS vertNeighborsSet;
	
	// idx to triangle (tris) neighbs and k nearest-neighbors
	vector< int > triNeighbors, kneighbs;

	// idx to edges incident to this vertex
	vector< int > edgeList, interiorEdgeList; //interior/invisible edges incident to this vert

	// auxiliary variables
	bool sample, processed;

	Vertex(int i, float* c) : idx(i), coords(c), sample(false) {};

	bool addVertNeighbor(int vertInd)
	{
		//add vertInd as a vert neighb of this vert if it won't cause a duplication

		pair< vertNeighborsIS::const_iterator, bool > pa;
		//O(log N) search for duplicates by the use of red-black tree (balanced binary search tree)
		pa = vertNeighborsSet.insert(vertInd);
		//pa.second is false if item already exists, and true if insertion succeeds
		return pa.second;
	}
	
	void removeVertNeighbor(int toBeRemoved)
	{
		//size_type erase (const key_type& x): Deletes all the elements matching x. Returns the 
		//number of elements erased. Since a set supports unique keys, erase will always return 1 or 0

		vertNeighborsSet.erase(toBeRemoved);
	}

	void removeTriNeighbor(int t)
	{
//this fnctn could've been used by contract/split/flip as well but i wrote it later; so, only createSphere() uses it

		unsigned int removeIdx;
		for (removeIdx = 0; removeIdx < triNeighbors.size(); removeIdx++)
			if (triNeighbors[removeIdx] == t)
				break;

		if (removeIdx == triNeighbors.size()) { cout << "tri" << t << " not in vert" << idx << ".triNeighbs!\n"; exit(0); }

		triNeighbors.erase(triNeighbors.begin() + removeIdx);
	}
};

struct Edge
{
	//edges[idx] is this edge
	int idx;

	//idx to endpnt verts of this edge
	int v1i, v2i;

	//distance between v1i & v2i
	float length;

	bool interior; //true if this is an interior edge, false if it is on the boundary (i.e. useful for geodesic computations)

	Edge(int i, int i1, int i2, float l, bool in) : idx(i), v1i(i1), v2i(i2), length(l), interior(in) {};
};

class Mesh
{
public:
	//triangular mesh stuff
	vector< Triangle* > tris;
	vector< Vertex* > verts;
	vector< Edge* > edges;
	vector< int > samples;
	float minEdgeLen, maxEdgeLen, edgeLenTotal, avgEdgeLen, minEucDist, maxEucDist;

	Mesh() {};
	
	float ICP(Mesh* mesh2, bool adaptiveScaling, int nMaxIters, bool oneToOne, float minDisplacement);
	// float ICPRansac(Mesh* mesh2, bool adaptiveScaling);

	bool loadPnt(char* meshFile);
	// bool loadPlyColor(char* meshFile);
	// void computeSamples(int n);
	// int getAnExtremeVert();

	void resultToFile(char* meshFile);
private:
	// int addVertex(float* v);
	// int addVertex(float x, float y, float z);
	void addVertex(float* c);
	// int addTriangle(int v1i, int v2i, int v3i);
	// int addTriangleTetmesh(int v1i, int v2i, int v3i, bool tetPartInMeshFile);
	// void addEdge(int v1i, int v2i, bool interiorEdge = false);
	// inline float calcTriArea(int t);
	// int* getTrianglesSharedBy(Edge* bigEdge, int v1i = -1, int v2i = -1);
	// void addTetrahedron(int v1i, int v2i, int v3i, int v4i);
	// int getEdgeSharedBy(int vi, int vj);
	// void computeNeighbors(int v, int k);
	// float computeMSE(Mesh* mesh2, bool mseUsingAllVerts, int fract = -1);
};

#endif
