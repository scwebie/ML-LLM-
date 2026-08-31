import numpy as np


def population_stability_index(reference:np.ndarray,current:np.ndarray)->float:
    edges=np.quantile(reference,np.linspace(0,1,11));edges[0]=-np.inf;edges[-1]=np.inf;r=np.histogram(reference,edges)[0]/len(reference);c=np.histogram(current,edges)[0]/len(current);r=np.clip(r,1e-6,None);c=np.clip(c,1e-6,None);return float(np.sum((c-r)*np.log(c/r)))
