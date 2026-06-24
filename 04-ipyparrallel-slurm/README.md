# Using ipyparallel with SLURM (generic slurm script)

The following example is based on this tutorial:
[Parallel Machine Learning with scikit-learn](https://ulhpc-tutorials.readthedocs.io/en/latest/python/advanced/scikit-learn/)
and in general the other slurm examples and tutorials at that site may be
useful as well.

A common type of high performance computing is bag-of-task parallelism, or embarrassingly parallel
tasks.  A common one in machine learning that you may be familiar with is similar to the concept
of a hyper parameter search, that is supported by the 
[`scikit-learn` `GridSearchCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
and similar hyper parameter search methods you may have used from `scikit-learn`.

In this example we show a general framework for using the `ipyparallel` package to start
and manage a general pool of parallel worker process to perform a systematic parameter search
for a machine learning example.

## Dependencies

This example is continuing on using the `keras-tf-gpu` environment that was setup and used in the previous
examples 2 and 3.  If you have done those tutorials you probably already have `scikit-learn` and
`numpy` as part of your environment.  In any case, you should ensure that you have those as well as
`ipyparallel` and `joblib`:

```
conda activate keras-tf-gpu
conda install numpy scikit-learn ipyparallel joblib
```

## The ipyparrell Launcher Script example

In this example there is one `sbatch` script named `launcher.sh` that you will find in the
top level of this example directory.  In addition there is a subdirectory named
`unsupervised` that contains a `main.py` and a `some_funcs.py` example script / modules.

In this example, we are grid searching the number of clusters
`n_clusters` for a k-means clustering of some data.  The task is not
really the point here, you could provide a similar function with 1 or
more parameters as input to perform some computation on a set of
parameters that you want to compare with others in the parameter space.

The `launcher.sh` slurm script is responsible
for launching a single `ipyparallel` controller node, some number of
`ipyparallel` worker engines, and then a single instance of
a code scheduler task.  If you examine the launcher script you will notice that
it calls `srun` 3 times.  The `sbatch` command in a slurm system is responsible
for allocating resources for a computational job.  In this case we ask for room
for some number of tasks (`--ntasks`) on 2 nodes (`--nodes`).

The first `srun` launches the `ipyparallel` controller using the `ipcontroller` command.  This
process is set up to be forced to start on the first allocated node for the job, so that the
workers and code execution process can connect with it.  Only 1 controller process is started.

The next `srun` command launches some number of `ipyparallel` worker engines using the `ipengine`
command.  The `--ntasks=${NB_WORKERS}` controls the number of worker engines that are started.
These workers should run on any of the available nodes that are allocated for the slurm
batch allocation.

NOTE: in the current example we are having some issues with our TLC slurm.  Usually if you wanted
8 workers, you would start the batch job with `--ntasks=10` and then the launcher script would 
calculate `NB_WORKERS` as `ntasks - 2` to account for we need to launch the controller, the
code execution scheduler and the number of desired workers.  However for some reason, we need to
allocate space for additional tasks in our slurm batch to ensure that the `srun` do not pause waiting for
suitable task allocation on nodes.  

The third `srun` again launches only a single process within the batch allocation.  This is the hook
into the code in the `unsupervised/main.py` directory.  So to submit this example to the slurm
batch system, perform the following command:

```
sbatch launcher.sh unsupervised/main.py
```


## `unsupervised/main.py` Script to setup ipyparallel cluster

The `launch.sh` script is responsible for launching the controller process, 
some number of worker engines, and finally the code execution process.  The
code execution process main code is found in `unsupervised/main.py`.

This code does a couple of tasks, most all of which could be reused to perform
the same kind of hyper parameter search for other tasks.  This script
sets up logging.  It then configures ipyparallel communication, but creating a 
ipyparallel `Client` and connecting the client to the ipyparallel worker engines.
The passed in `profile` name is used to find the register ipyparallel controller.
The client is set up to perform load balancing scheduling on all of the available
worker engines.

After preparing the engines, the hyper parameter search space is set up.  This would
be different for each type of hyper parameter parallel search you would like to perform.
In this example, we have a simple parameter spaces of the number of `k` clusters
to try for a k-means clustering, ranging from trying 2 up to 20 clusters.
Also the common data to be used is created here, in another context you might
need to load your data from a file or database to use to fit a model with.

After the hyper parameter space is defined, the parallel execution scheduling is
performed for the ipyparallel cluster.  Basically a `kmeans()` function is run
in parallel on the ipyparallel cluster.  This function is passed in a few parameters, including
one of the n_clusters of the hyperparameter space being used.

Once all jobs are scheduled and finished, the last lines show an example of generating
some summary data results.  In this case the `kmeans()` function returns back 
an `inertia` measure of how good the clustering was for each parameter, which is written
out to a `.csv` file as an example of performing a final analysis on the data.

## `unsupervised/some_funcs.py` pre and post processing for a wrapped scikit-learn fit()

The primary purpose of the `some_funcs.py` module / script is as an example of how  you
might wrap a `scikit-learn` fit of a parameter for this type of parallel clustering.
The main example function `kmeans()` takes 3 input parameters, including the hyper 
parameter and the input data to fit.  This function returns the inertia result of 
performing the computation.  You could of course adjust inputs and return values here as
needed for a different hyper parameter search.  And for more complex cases, you could break
the work up into several functions and place them into a separate module file like this
file.

The first part of this example again sets up some logging output to help monitor the
task execution.  

The actual work is done in 2 lines of this function, to fit a k-means clustering algorithm
to the input data `X` using the given meta parameter for this run of the task in the 
hyper parameter search.  

The last part of this example again shows some more logging, as well as creating some
intermediate results (a figure in this case) of this particular run in the hyper
parameter search.