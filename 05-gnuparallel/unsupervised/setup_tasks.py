"""setup GNU parallels data and taskfile

This script can be run to generate a set of data used in the
embarrassingly parallel example task, in this case a set of
data we want to determine the best number of k cluster to
perform k-means clustering with.  The data file is saved
into the `data` subdirectory, to be loaded by each task
that is run.  

This file also determines the set of grid parameters
to be searched, and creates an appropriate task file, running
a k-means clustering task on the data for each meta parameter
being searched.
"""
from sklearn.datasets import make_blobs
import numpy as np
import pandas as pd

# Generate a set of data that each task will use to perform the
# fitting task with.  Often you already have data you want to
# fit with different hyperparameters to explore with.
print("generate the data to perform parameter search on for this example...")
num_centers = np.random.randint(2,25)
print("random number of centers we used when generating data: ", num_centers)

X,_ = make_blobs(n_samples=20000, centers=num_centers)
df = pd.DataFrame(X)
df.columns = ['feature1', 'feature2']
datafile = 'data/blobs.csv'
df.to_csv(datafile, index=False)
print(f"save dataset to file '{datafile}' to be used in parallel example")


# Generate the taskfile with different hyperparameters for each task to
# fit.  You can change the parameter space here if want to explore different
# hyperparameter search
param_space = {
    'NCLUSTERS': np.arange(2,41)
}
taskfile = 'taskfile.txt'

print("create the taskfile to be given to the GNU parallel launcher")
with open(taskfile, 'w') as file:
    for n_clusters in param_space['NCLUSTERS']:
        cmd = f'python,unsupervised/some_funcs.py,{datafile},{n_clusters}\n'
        file.write(cmd)
