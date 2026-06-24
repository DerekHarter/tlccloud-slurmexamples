import argparse
import logging
import os
import sys
from sklearn.datasets import make_blobs
from joblib import Parallel, parallel_backend
from joblib import register_parallel_backend
from joblib import delayed
from joblib import cpu_count
from ipyparallel import Client
from ipyparallel.joblib import IPythonParallelBackend
import numpy as np
import datetime
# module in the same directory
from some_funcs import kmeans


print("main script entered...", flush=True)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(FILE_DIR)

# prepare the logger
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--profile", default="ipy_profile",
                 help="Name of IPython profile to use")
args = parser.parse_args()
profile = args.profile
logging.basicConfig(filename=os.path.join(FILE_DIR,profile+'.log'),
                    filemode='w',
                    level=logging.DEBUG)
logging.info("number of CPUs found: {0}".format(cpu_count()))
logging.info("args.profile: {0}".format(profile))

# prepare the engines
c = Client(profile=profile)
NB_WORKERS = int(os.environ.get("NB_WORKERS",1))

# wait for the engines
print("wait for engines...", flush=True)
c.wait_for_engines(NB_WORKERS)

# The following command will make sure that each engine is running in
# the right working directory to access the custom function(s).
c[:].map(os.chdir, [FILE_DIR]*len(c))
logging.info("c.ids :{0}".format(str(c.ids)))
bview = c.load_balanced_view()
register_parallel_backend('ipyparallel',
                          lambda : IPythonParallelBackend(view=bview))

# Create data
# prepare it for the custom function
X,_ = make_blobs(n_samples=20000, centers=np.random.randint(30))

# some parameters to test in parallel
param_space = {
    'NCLUSTERS': np.arange(2,40)
}

print("execute tasks", flush=True)

with parallel_backend('ipyparallel'):
    inertia = Parallel(n_jobs=len(c))(delayed(kmeans)(n_clusters,X,profile)
                               for n_clusters in param_space['NCLUSTERS'])


#write down the number of clusters and the total inertia in a file.
with open(os.path.join(FILE_DIR,'scores_kmeans.csv'), 'w') as f:
    f.write('n_clusters, inertia,\n')
    f.write("\n".join(','.join(str(c) for c in l) for l in inertia))
    f.write('\n')
c.shutdown()