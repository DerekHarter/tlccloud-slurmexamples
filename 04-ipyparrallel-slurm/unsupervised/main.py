"""main ipyparallels code execution

This is an example of how to execute a bag-of-tasks parallel task
to perform a parameter search over a set of parameters for a 
mcahine learning task.  

In this example, we are grid searching the number of clusters
n_clusters for a k-means clustering of some data.  The task is not
really the point here, you could provide a similar function with 1 or
more parameters as input to perform some computation on a set of
parameters that you want to compare with others in the parameter space.

In this example of a main script, we setup ipyparallel communication
and execution.  This script only runs as a single executable, a
client to a set of ipyparallel worker engines and a ipyparallel
controller.

Besides the setup to use the ipyparallel controller/worker, the main
work is done where we create a set of data to perform a parameter search
on (using scikit-learn make_blobs()).  Then we define a 
parameter search space (param_space dictionary).  The call to Parallel
then will schedule calls to the kmeans function imported from the
some_funcs file/module.  The kmeans is invoked with a parameter and the
data to fit using that meta parameter.  ipyparallel handles scheduling
the workers and keeping track of when a worker is idle to schedule
another job for it.
"""
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


print("main code execution script entered...")

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(FILE_DIR)
ROOT_DIR = os.path.dirname(FILE_DIR)

# prepare the logger
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--profile", default="ipy_profile",
                 help="Name of IPython profile to use")
args = parser.parse_args()
profile = args.profile
logging.basicConfig(filename=os.path.join(ROOT_DIR, 'logs', profile, profile+'.log'),
                    filemode='w',
                    level=logging.DEBUG)
logging.info("number of CPUs found: {0}".format(cpu_count()))
logging.info("args.profile: {0}".format(profile))

# prepare the engines, note we expect that the NB_WORKERS environment
# variable has been set in our environment by the sbatch script to indicate
# number of worker engines that should be available in the ipyparallel pool
c = Client(profile=profile)
NB_WORKERS = int(os.environ.get("NB_WORKERS",1))

# wait for the engines
print("wait for worker engines to be available...")
c.wait_for_engines(NB_WORKERS)

# The following command will make sure that each engine is running in
# the right working directory to access the custom function(s).
# TODO: is this necessary?  Workers are probably in correct cwd I would think.
print("ensure all worker engines are expected directory as its working directory...")
c[:].map(os.chdir, [FILE_DIR]*len(c))
logging.info("c.ids :{0}".format(str(c.ids)))
bview = c.load_balanced_view()
register_parallel_backend('ipyparallel',
                          lambda : IPythonParallelBackend(view=bview))

# Create data
# prepare it for the custom function
# by default make_blobs will create data with 2 feature dimensions here, which
# we need so we can visualize results ad 2d plots 
print("generate the data to perform parameter search on for this example...")
num_centers = np.random.randint(2,25)
print("random number of centers we used when generating data: ", num_centers)
X,_ = make_blobs(n_samples=20000, centers=num_centers)

# some parameters to test in parallel
param_space = {
    'NCLUSTERS': np.arange(2,40)
}

print("execute tasks...")

with parallel_backend('ipyparallel'):
    inertia = Parallel(n_jobs=len(c))(delayed(kmeans)(n_clusters, X, profile)
                               for n_clusters in param_space['NCLUSTERS'])


#write down the number of clusters and the total inertia in a file.
print("write final inertia results")
with open(os.path.join(ROOT_DIR, 'data', profile, 'scores_kmeans.csv'), 'w') as f:
    f.write('n_clusters, inertia,\n')
    f.write("\n".join(','.join(str(c) for c in l) for l in inertia))
    f.write('\n')
c.shutdown()