import numpy as np


# https://stackoverflow.com/questions/52202014/how-can-i-plot-2d-fem-results-using-matplotlib
# converts quad elements into tri elements
def quads_to_tris(quads):
    tris = [[None for j in range(3)] for i in range(2 * len(quads))]
    for i in range(len(quads)):
        j = 2 * i
        n0 = quads[i][0]
        n1 = quads[i][1]
        n2 = quads[i][2]
        n3 = quads[i][3]
        tris[j][0] = n0
        tris[j][1] = n1
        tris[j][2] = n2
        tris[j + 1][0] = n2
        tris[j + 1][1] = n3
        tris[j + 1][2] = n0
    return tris


# https://gitlab.onelab.info/gmsh/gmsh/-/blob/master/Geo/gmshSurface.cpp#L88
def to_3d(x, y, R=1):
    lon = np.array(x)
    lat = np.array(y)
    # to 3D
    kx = np.cos(lat / 180 * np.pi) * np.cos(lon / 180 * np.pi) * R
    ky = np.cos(lat / 180 * np.pi) * np.sin(lon / 180 * np.pi) * R
    kz = np.sin(lat / 180 * np.pi) * R

    return kx, ky, kz
