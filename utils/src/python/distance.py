import numpy as np

try:
    from scipy.spatial.distance import cosine
except Exception:
    def cosine(a, b):
        return 1-np.dot(a, b)/np.linalg.norm(a)/np.linalg.norm(b)


def geo_distance(l1, l2):
    return np.sqrt(np.power(l1.lat-l2.lat, 2) + np.power(l1.lon-l2.lon, 2))
