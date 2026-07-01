"""some_funcs file/module

This is an example of a file that defines some function meant to be called
in a GNU parallel example.  This is a simplified version of the
ipyparallel example, doing the same thing but stripping out
the code to setup and tear down the ipyparallel communication.
"""
import os
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import  KMeans
from sklearn.metrics.pairwise import pairwise_distances_argmin
from matplotlib.cm import rainbow
import numpy as np
import pandas as pd
import socket
import time
import sys

# alias to the now function
now = datetime.datetime.now

# To know the location of the python script PARENT LOCATION
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kmeans(n_clusters, X):
    """
    Wrap scikit-learn kmeans clustering function. 

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
    # all output for GNU parallel is directed to log file for us
    t0 = now()
    print('job started on {0}'.format(socket.gethostname()))
    print('new task for n_clusters=' + str(n_clusters))
    print('Start clustering at {0}'.format(t0.isoformat()))

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
    print('Finished at {0} after '
          '{1}h {2}min {3:0.2f}s'.format(t1.isoformat(),h,m,s))
    print('n_clusters: {0}'.format(str(n_clusters)))
    print('inertia: {0:0.4f}'.format(k_means.inertia_))

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
    fig_file_path = os.path.join(ROOT_DIR, 'data', f'C{n_clusters:06}.png')
    plt.savefig(fig_file_path)
    return (n_clusters, k_means.inertia_)


if __name__ == "__main__":
    # expect 2 fixed command line args: datafile n_clusters
    if len(sys.argv) != 3:
        print("Error: expect arguments: some_func.py datafile n_clusters")
        sys.exit(1)

    # get the expected command line arguments
    datafile = sys.argv[1]
    n_clusters = int(sys.argv[2])

    # read the csv data file
    df = pd.read_csv(datafile)
    X = df.to_numpy()
    
    # invoke the function
    n_clusters, inertia = kmeans(n_clusters, X)

    # TODO: in previous example we gathered results into summary csv, would need to
    # add in post task to read the inertia out of log files to create summary csv
    print(f"job finished n_clusters: {n_clusters}  inertia: {inertia}")
