# Using ipyparallel with SLURM (generic slurm script)

The following example is based on this tutorial:
[HPC Management of Sequential Embarrasingly Parallel Jobs using GNU Parallel](https://ulhpc-tutorials.readthedocs.io/en/latest/sequential/basics/)
and in general the other slurm examples and tutorials at that site may be
useful as well.

Embarrassingly parallel jobs, also known as "perfectly parallel" or "pleasingly parallel" jobs, refer to computational tasks that can be easily divided into smaller, independent sub-tasks that can be executed simultaneously without any need for communication or interaction between them. 

This example shows using the GNU parallel package to coordinate an embarassingly parallel task on a single
compute node, utilizing all of the cpu cores and memory of a single node.  The parallel package should
be available on all TLC worker nodes.  You can also distribute embarrasingly parallel jobs over multiple
hosts, but that is covered in other tutorials.  Also currently missing in this example is a way to
parameterize each job, so that they are doing the same task but each one potentially on a different
set of input parameters.

TODO: this example is not yet complete.  Need to finish example description here and adding in
some code features.