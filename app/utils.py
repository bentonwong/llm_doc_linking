import numpy as np

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
