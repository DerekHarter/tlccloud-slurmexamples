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
do this as needed.  For example, if you decide you also need `scikit-learn` machine learning pakcages in this environment
you can install them in your current environment.  The `conda install` command will install or manage
packages for the current active environment:

```
conda install scikit-learn
```

## Example slurm Batch Job Submission with Python and Conda

We can create a slurm script that activates a conda/python environment and runs a python program.  For
example, given the following slurm batch script called `gputest.sh`:

```
#!/bin/bash
#SBATCH --job-name=gputest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=3G
#SBATCH --output=gputest-%5A.out
#SBATCH --gpus=1
echo "Compute node: `hostname`"
echo "Project directory: `pwd`"
echo "Start time: `date`"
start=$(date +%s)
source activate keras-tf-gpu
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
./gputest.py
echo "End time: `date`"
end=$(date +%s)
secs=($end-$start)
echo "Elapsed time: $((secs/1)) seconds"
printf 'Elapsed time: %d:%02d:%02d\n' $((secs/3600)) $((secs%3600/60)) $((secs%60))
```

We talk in more detail about allocating gpu and other resources later in this tutorial.  This slurm batch
script allocates a single cpu and gpu on some available node to run.  Notice that we use

```
source activate keras-tf-gpu
```

in the script before executing the actual python script to activate the needed conda environment.  You use
`conda activate` to activate an environment by hand at the terminal but `source activate` inside
of a batch script (for reasons that are unimportant).

The file `gputest.py` can contain any Python code/script needed, and since we activate the
`keras-tf-gpu` environment before calling it, it will have available the `keras`, `tensorflow`
and any other libraries installed in that environment.

The `gputest.py` file given as an example in this tutorial directory simply trains
a small neural network using `keras/tensorflow` and using the allocated gpu it was given
by slurm.

To run this example/test job on the slurm batching system, we would invoke it as follows:

```
$ sbatch gputest.sh
```

## Additional Resources

- [Conda User Guide: Managing Environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [How to run python experiments with Slurm and Conda](Python and Conda Environments in Slurm Jobs)
