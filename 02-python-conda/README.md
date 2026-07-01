# Python and Conda Environments in Slurm Jobs

Using Python for machine learning and deep learning tasks is a common need for many users.  The TLC Slurm cluster supports and recommends
using the conda package manager to create and manage python environments and python packages for running Python scientific stack
applications on the slurm cluster.  The conda package manager reference is provided below and can be used as a general reference.

## Example `conda` Environment for gpu/keras/tensorflow Library Usage

As a quick example, if we need a python environment with `keras`, `tensorflow` and gpu support, we can use the `conda` command
as follows to create an environment and install packages we need.

First if you have not yet used conda, you have to initilize your account to setup for conda usage:

```
conda init
conda config --append channels conda-forge
```

You may need to log out of your shell/terminal session and log back in to pick up changes from the conda
initialization.

Appending additional source channels is optional here.  You may need to add in other channels if you need specific packages or
libraries.  The `conda-forge` channel often has more recent versions of scientific python packages than the default channel, and I
find I often need it.  This initialization only needs to be done once, though you can append additional channels whenever
needed.  The init will create a default `base` environment that you can use, which only has basic python packages in it.

You can create an environment named `keras-tf-gpu` with `keras` and `tensorflow`package as follows:

NOTE: if you want gpu support enabled for `tensorflow` use the `tensorflow[and-cuda]` package.  Also you need to actually
be logged into the `gpu-1-01` or suitable node that has the nvidia and cuda packages available, so that the conda environemnt will be
created and setup correctly to use cuda tools to access the gpu from tensorflow.


```
ssh gpu-1-01
conda create -n keras-tf-gpu keras tensorflow[and-cuda]
```

Once successfully created, you can activate the environment with the installed packages like this:

```
(base) $ conda activate keras-tf-gpu
(keras-tf-gpu) $ 
```

Notice that we were in the base (default) environment before activating the new `keras-tf-gpu` environment here.

If you forgot to install a package, or need to add or remove packages from an existing environment, you can always
do this as needed.  For example, if you decide you also need `numpy` `scikit-learn` `pandas` and `matplotlib`
pakcages in this environment you can install them in your currently active environment. (The script we run
next needs these, so you do need to install these in the active environment).)
The `conda install` command will install or manage packages for the current active environment:

```
conda install numpy scikit-learn pandas matplotlib
```

Once you have an environment set up, it is often a good idea to check that the packages
are installed and available for use when your environment is active.  For example, there is
a python script called `versions.py` which you can run to test that all of the packages we need
are available, as well as seeing which computing devices are visible to tensorflow.  Run it like
this:

```
$ python versions.py
Python version    :  3.13.14 | packaged by Anaconda, Inc. | (main, Jun 17 2026, 20:12:46) [GCC 14.3.0]
numpy version     :  2.4.6
scikit-learn  vers:  1.9.0
matplotlib version:  3.10.9
pandas version    :  3.0.3
tensorflow version:  2.21.0
Physical Devices  :  [PhysicalDevice(name='/physical_device:CPU:0', device_type='CPU')]
Available Devices :  [LogicalDevice(name='/device:CPU:0', device_type='CPU')]

```

Notice that only a CPU device was shown as available on this node.  We ran this command on a node
without any gpu devices.  If you were to run the command on a node that has GPU devices, you should
also see those as available devices in addition to having CPU available for compute.

## Example slurm Batch Job Submission with Python and Conda

We can create a slurm bash script that activates a conda/python environment and runs a python program.  For
example, look at the following slurm batch script called `gputest.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=gputest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --output=gputest-%5A.out
#SBATCH --gpus=1

# Display node and directory that was assigned and that we are running the job from.
echo "Compute node: `hostname`"
echo "Project directory: `pwd`"

# Setup conda profile and ensure we are using the correct conda environment
# for the following computation.
# Note: you may need to adjust the path to the conda profile shell script and
# the name of the conda environment you wish to activate here.
. /home/miniconda3/etc/profile.d/conda.sh
conda activate keras-tf-gpu
echo "PATH: $PATH"
echo "python path: `which python`"
echo "conda path: `which conda`"
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
echo "--------------------------------------------------"
echo ""

# Can setup other needed configuration such as environment variable
# settings that may be needed by the computation.
# For example, reduce tensorflow warning log level as these warning
# are not really useful.
export TF_CPP_MIN_LOG_LEVEL=3

# Record start time to display elapsed time of computation
echo "Start time: `date`"
start=$(date +%s)

# Run the actual computation by invoking python script or executable
python gputest.py

# Record end time to display elapsed time of computation
echo "End time: `date`"
end=$(date +%s)
secs=($end-$start)
echo "Elapsed time: $((secs/1)) seconds"
printf 'Elapsed time: %d:%02d:%02d\n' $((secs/3600)) $((secs%3600/60)) $((secs%60))
```

We talk in more detail about allocating gpu and other resources later in this tutorial.  This slurm batch
script allocates a single cpu and gpu on some available node to run.  Notice that we use

```
conda activate keras-tf-gpu
```

in the script before executing the actual python script to activate the needed conda environment.
Just above activating our conda environment, we setup and initialize the conda system.  This setup
is normally done in your `.bashrc` file each time you log into the slurm system, but by default your
bashrc is not loaded when slurm batch jobs are run like this, so we need to initialize conda by hand
before we can activate an environment.  Also as noted in the comments, your environment name and
the location of the conda initialization may change.  If you are creating and managing your own conda
environment, you will want to set the name of the environment here appropriately.

Also notice that after we initialize the conda environment, we display some information like path to the
conda and python executables.  This is a good practice to ensure that you are correctly using the correct
environment you setup for the scripts you run on the slurm cluster.

The file `gputest.py` can contain any Python code/script needed, and since we activate the
`keras-tf-gpu` environment before calling it, it will have available the `keras`, `tensorflow`
and any other libraries installed in that environment.  As mentioned this script also uses `numpy`
`pandas` and `matplotlib`, so those packages need to be installed in the active conda environment.

The `gputest.py` file given as an example in this tutorial directory simply trains
a small neural network using `keras/tensorflow` and using the allocated gpu it was given
by slurm.

To run this example/test job on the slurm batching system, we would invoke it as follows:

```
$ sbatch gputest.sh
```

If the jobs starts successfully running, you should see that it is now active on a slurm partiton.  For
example use the `squeue` command to see which jobs are currently in the slurm partition queues:

```
$ squeue
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
                40     debug  gputest      slu  R       0:02      1 gpu-1-01
```

This shows that the job is currently running on the debug partition queue.  It was assigned a job id of 40, and
it was allocated some resources on the `gpu-1-01` machine.

While running, output from the script will be put into a file named `gputest-XXXXX.out`, where `XXXXX` will
be replaced by the slurm job batch number that was assigned to your job when it was placed onto the slurm
queue, e.g. `gputest-00040.out`.  You should look at this file during or after running this test.  You will see that
the correct conda environment was activated, and that the job is actually executing on the assigned node, like `gpu-1-01`,
that has a gpu resource that was allocated for the job to use while running.

## Additional Resources

- [Conda User Guide: Managing Environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [How to run python experiments with Slurm and Conda](https://hiteshuv.medium.com/how-to-run-python-experiments-with-slurm-and-conda-fcd6f2f31840)
