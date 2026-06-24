"""some_funcs file/module

This is an example of a file that defines one or more functions meant to be
imported by a main function/script.  The function given in this example
will be called in an environment that is performing bag-of-task parallelism
In this example we use ipyparallel to create a controller and multiple
worker engines to execute computation in parallel on a slurm cluster.

In general you could implement 1 or more functions as shown here, and invoke
the main function as needed for parallel execution.  In this example, we
are grid searching the number of clusters n_clusters for a k-means
clustering of some data.  The task is not really the point here, you could
provide a similar function with 1 or more parameters as input to perform
some computation on a set of parameters that you want to compare with
others in the parameter space.

The main thing being illustrated here is how we can wrap the computation
in pre and post processing steps, in order to log the session and generate
output as needed.  In this example, we log the session information
being done into the log/profile/cjobid.log file, and we generate data
files, like figures, of the results in the data/profile/cjobid.png files.
"""
import os
import datetime
# Library to generate plots
import matplotlib as mpl
# Define Agg as Backend for matplotlib when no X server is running
mpl.use('Agg')
import matplotlib.pyplot as plt
# Importing scikit-learn functions
from sklearn.cluster import  KMeans
from sklearn.metrics.pairwise import pairwise_distances_argmin
from matplotlib.cm import rainbow
# Import the famous numpy library
import numpy as np
# We import socket to have access to the function gethostname()
import socket
import time

# alias to the now function
now = datetime.datetime.now

# To know the location of the python script PARENT LOCATION
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kmeans(n_clusters, X, profile):
    """
    Wrapt scikit-learn kmeans clustering function.  We add pre and post
    processing so that we can execute this function in a bag-of-task
    parallel environment (using ipyparallel engine workers).

    Basically this example performs a k-means clustering for the asked for
    number of clusters, and plots the results and returns the resulting
    inertia measure obtained by the clustering.

    Parameters
    ----------
    n_clusters : int
        The number of clusters to perform k-means clustering with.

    X : (num_samples, 2) shaped array / dataframe
        The input data to cluster.  We assume 2 feature dimenstions so we can plot
        the resulting clustering.

    profile : IPY / ipyparallel profile
        The name of the ipyparallel profile being used.  In this script this name is only
        used to give unique output names to logging and data files
    
    Returns
    -------
    n_clusters : int
        The number of clusters that were processed are returned for ease of use
        in the caller to produce a summary of the clustering results.
    inertia : float
        The result parameter we are interested in measuring in this bag-of-tasks parallel
        search.  Here for clustering, usually the lower the inertia, the closer the
        number of clusters used comes to being ideal in clustering the data.
    """
    # We create a log for the clustering task
    log_file_path = os.path.join(ROOT_DIR, 'logs', profile, f'C{n_clusters:06}.log')

    # logging will not work from the HPC engines
    # need to write into a file manualy.
    t0 = now()
    with open(log_file_path, 'a+') as f:
        f.write('job started on {0}\n'.format(socket.gethostname()))
        f.write('new task for n_clusters=' + str(n_clusters)+'\n')
        f.write('Start clustering at {0}\n'.format(t0.isoformat()))

    # Original scikit-learn kmeans, this is the actual computation on
    # the parameter we want to perform.
    k_means = KMeans(init='k-means++', n_clusters=n_clusters, n_init=100)
    k_means.fit(X)

    # After clustering has been performed, we record information to 
    # the log file
    t1 = now()
    h = (t1-t0).total_seconds()//3600
    m = (t1-t0).total_seconds()//60 - h*60
    s = (t1-t0).total_seconds() -m*60 - h*60
    with open(log_file_path, 'a+') as f:
        f.write('Finished at {0} after '
                '{1}h {2}min {3:0.2f}s\n'.format(t1.isoformat(),h,m,s))
        f.write('n_clusters: {0}\n'.format(str(n_clusters)))
        f.write('inertia: {0:0.4f}\n'.format(k_means.inertia_))

    # We sort the centers
    k_means_cluster_centers = np.sort(k_means.cluster_centers_, axis=0)

    # We assign the labels
    k_means_labels = pairwise_distances_argmin(X, k_means_cluster_centers)

    # The previous part is useful in order to keep the same color for
    # the different clustering
    t_batch = (t1 - t0).total_seconds()

    # We generate a plot in 2D
    colors = rainbow(np.linspace(0, 1, n_clusters))
    fig=plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for k, col in zip(range(n_clusters), colors):
        my_members = k_means_labels == k
        cluster_center = k_means_cluster_centers[k]
        ax.plot(X[my_members, 0], X[my_members, 1], 'w',
            markerfacecolor=col, marker='.')
        ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
            markeredgecolor='k', markersize=6)
        ax.set_title('KMeans')
        ax.set_xticks(())
        ax.set_yticks(())
    plt.text(-3.5, 1.8,  'clustering time: %.2fs\ninertia: %f' % (t_batch, k_means.inertia_))

    # We save the figure in png
    fig_file_path = os.path.join(ROOT_DIR, 'data', profile, f'C{n_clusters:06}.png')
    plt.savefig(fig_file_path)
    return (n_clusters, k_means.inertia_)
