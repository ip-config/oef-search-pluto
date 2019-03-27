import numpy as np

try:
    from scipy.spatial.distance import cosine
except Exception:
    def cosine(a, b):
        return 1-np.dot(a, b)/np.linalg.norm(a)/np.linalg.norm(b)