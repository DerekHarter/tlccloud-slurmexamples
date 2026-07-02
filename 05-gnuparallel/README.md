# Using ipyparallel with SLURM (generic slurm script)

The following example is based on this tutorial:
[HPC Management of Sequential embarrassingly Parallel Jobs using GNU Parallel](https://ulhpc-tutorials.readthedocs.io/en/latest/sequential/basics/)
and in general the other slurm examples and tutorials at that site may be
useful as well.

Embarrassingly parallel jobs, also known as "perfectly parallel" or "pleasingly parallel" jobs, refer to computational tasks that can be easily divided into smaller, independent sub-tasks that can be executed simultaneously without any need for communication or interaction between them. 

This example shows using the GNU `parallel` package to coordinate an embarrassingly parallel task on a single
compute node, utilizing all of the cpu cores and memory of a single node.  The parallel package should
be available on all TLC worker nodes.  You can also distribute embarrassingly parallel jobs over multiple
hosts, but that is covered in other tutorials.  Also currently missing in this example is a way to
parameterize each job, so that they are doing the same task but each one potentially on a different
set of input parameters.

## Stress Test using `stress-ng` Tool

We will first show an example of using GNU `parallel` to run an example bogus task.  The purpose of 
this example is to remind you that you should not run computational jobs on the main slurm controller
node, the node you are fist logged on to when you `ssh` into the TLC slurm system.  You should only 
submit batch and interactive jobs from the controller node using `sbatch` and `srun` respectively.

So if we need some tools for a parallel computation, you may need to use 
interactive `srun` sessions first to create and setup your tools.  We are going to download
and compile the `stress-ng` tool to use in our first example.  Start by requesting an interactive
session on a compute node.

```bash
slu@slurm:~/repos$ srun --pty bash
slu@cpu-1-01:~/repos$ 
```

In this example we were allocated resources to run on the `cpu-1-01` worker node, you may end up being
allocated some different node.

Once on a worker node we can set up our tooling.  Perform the following to clone the `stress-ng`
code, build the tool, and add it into our own local `bin` directory for use in parallel jobs:

```bash
slu@cpu-1-01:~/repos$ git clone https://github.com/ColinIanKing/stress-ng
Cloning into 'stress-ng'...
...

slu@cpu-1-01:~/repos$ cd stress-ng
slu@cpu-1-01:~/repos/stress-ng$ make
Compiler: gcc
...

slu@cpu-1-01:~/repos/stress-ng$ ln -s $(pwd)/stress-ng ~/bin/
slu@cpu-1-01:~/repos/stress-ng$ exit
slu@slurm:~/repos
```

The last command is for convenience.  It provides a symbolic link in our local
`bin` directory to the `stress-ng` tool that was just compiled.  The example below
will expect the tool in this location in order to run it.

Also note that we perform an `exit` once we are done with the interactive session.
As long as you are still in the session you launched with `srun` the node and resources
are allocated to your interactive session.  You should not launch additional tasks
while in an interactive session.  So make sure you `exit` the interactive session once done
using it and setting up tooling.  All batch submissions should be done from the
controller node.

## GNU `Parallel` Example Launcher Script

The script in this example named `slurm_parallel_launcher_single_node.sh` is a typical
bash / slurm script that can be used to launch an embarrassingly parallel task on a single
node.  The script is set up to be run using the `sbatch` command, and it will 
allocate a typical whole TLC slurm node as a resource (e.g. it asks for a
single node using `--nodes=1` and the `--exclusive` means it wants the whole node
allocated to this job).

The `--mem=0` along with the exclusive flag means that all of the
memory for the node will also be allocated for this job.  The TLC slurm cluster has nodes
with different amounts of main memory in the cpu batch partition, so these
settings will just allocate a single available node when one is available, regardless
of the amount of memory.  If you needed a particular minimum amount of memory per task,
you would want to multiply that by 8 and specify it for the memory requirement here.

Our typical TLC slurm worker nodes have 8 physical Intel cpus that support hyperthreading,
so they show up as 16 logical cpus in the system.  We discuss 8 physical cores vs 16
logical cores later on in this tutorial.  The default for the script is to ask for 8
tasks / cpus at a time on the node it is allocated, and each task runs on 1 of the
allocated cpus.

In this example script, you can launch an embarrassingly parallel task in one of two ways.

1. Either repeat a task `--ntasks` number of times.  We will show this first, in this case
   each task is identical (unless it figures out its own unique setting/parameters to run with).
2. Or provide a taskfile in which each line defines a command to run and the parameters to
   run this command on.  We show this method after the first one.

## Execution of the Same Task N Times

In our first example, we will use the `stress-ng` tool and execute it `--ntasks=300` number of
times.  GNU `parallell` will act as a job scheduler on the node allocated to it, keeping the
8 physical cpus busy, starting a new task each time one of the running one completes.

The file named `task.sh` in this example directory is used in this example.  If you examine
that file you will see that it basically calls the `${HOME}/bin/stress-ng` tool to run on 
a single cpu for 60 seconds.  This file is invoked by GNU `parallel` the number of tasks
times, which is 300 times in this example.

Submit the job using the following `sbatch` command:

```bash
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ sbatch slurm_parallel_launcher_single_node.sh --ntasks 300 "./task.sh"
Submitted batch job 103
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ squeue
             JOBID PARTITION     NAME     USER    STATE       TIME  NODES     CPUS MIN_MEMO TIME_LEF NODELIST(REASON)
               103       cpu slurm_pa      slu  RUNNING       0:03      1       16        0  1:59:57 cpu-1-01
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ 
```

In this example, the job was submitted and is allocated and running on the `cpu-1-01` worker
node.

You can join the allocation while it is running to, for example, monitor the cpu usage on the node
using something like the `htop` command:

```bash
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ srun --jobid 103 --overlap -w cpu-1-01 --pty bash -i
(base) slu@cpu-1-01:~/repos/tlccloud-slurmexamples/05-gnuparallel$ 

```

By using the `--overlap` option, we can get access to our previous allocation, even though we specified
`--exclusive` in the initial sbatch run.  Also you need to use the correct `jobid` here, e.g. when the batch
job was submitted it was assigned a `jobid` of 103, which you need to specify here in order to access
the running allocation.

You could use `htop` to for example see the current cpu and resource utilization on the node you were
allocated and are now running on.  You might notice that 8 cpu cores are usually being shown as being utilized
in `htop`, corresponding to the `--ntasks-per-node` we have set in the launcher script.

```bash
(base) slu@cpu-1-01:~/repos/tlccloud-slurmexamples/05-gnuparallel$ htop
```

~![Example of `htop` to montior parallel job resource allocation](../figures/htop-05-parallel-ntasks.png)

### Backup and Resume of Failed (or Stopped) Jobs

The launcher script also contains a mechanism to backup and resume from an incomplete `parallel` run
in the `log.timestamp` directory.  You will find a log file of the output of each of the `ntasks` 300
jobs, as well as a file named `task.log` in the log directory:

```
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ tree logs.20260701T112715/
logs.20260701T112715/
├── task.log
├── task.sh.log.1
├── task.sh.log.10
├── task.sh.log.100
├── task.sh.log.101
├── task.sh.log.102
├── task.sh.log.103
├── task.sh.log.104
├── task.sh.log.105
...
```

The `task.log` file here in particular records the status of each attempted job that parallel executes, including
the exit status code of the jobs.

```bash
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ cat logs.20260701T112715/task.log
Seq	Host	Starttime	JobRuntime	Send	Receive	Exitval	Signal	Command
1	:	1782923235.417	    60.155	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.1
2	:	1782923235.619	    60.143	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.2
3	:	1782923235.822	    60.147	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.3
4	:	1782923236.025	    60.134	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.4
5	:	1782923236.228	    60.152	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.5
6	:	1782923236.431	    60.148	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.6
7	:	1782923236.634	    60.151	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.7
8	:	1782923236.839	    60.161	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.8
9	:	1782923295.581	    60.217	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.9
10	:	1782923295.913	    60.122	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores ./task.sh > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs.20260701T112715/task.sh.log.10

```

Notice that the exact `srun` command that is performed within the allocation is recorded.  Also make note that by default the
`--cpu-bind=cores` is being used here, see the discussion about physical cores vs. logical hyperthreaded cores below.

If some of the tasks failed in a GNU `parallel` run, you can resume the job using this log file, and `parallel` will attempt to
rerun and complete any failed or unfinished jobs.  For example you you underestimate the amount of time you need and
your job is stopped early on the cluster, you can restart it using this method to get another allocation and complete
any unfinished jobs.

```bash
slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ sbatch slurm_parallel_launcher_single_node.sh --ntasks 300 -r "logs.20260701T112715" "./task.sh"

```

## Execution of a Taskfile with Parameters

As a second example, the launcher script can also accept a task file, where each line is expected to be
a command that should be run.  To use the launcher script this way, you should not specify the
number of tasks using the `--ntasks` flag.  The number of tasks run in parallel will come from the
number of tasks described on each line of the provided taskfile.

In this example we recreate performing a `scikit-learn` meta parameter search for k-means clustering,
the same task used in example 4 using an `ipyparallel` clustering.  This example is a bit
limited compared to that one, as it can only be run on a single node.  But it may be a bit simpler
to set up, and works well in a slurm system that has powerful single nodes with many cpus that you
would like to completely allocate for some time period to perform some embarrassingly parallel
calculation with.

A file named `taskfile.txt` has already been created, and there is a data file saved in
`data/blobs.csv`.  The taskfile and generated data were created by running the `setup_tasks.py`
function.

```bash
(keras-tf-gpu) slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ python unsupervised/setup_tasks.py 
generate the data to perform parameter search on for this example...
random number of centers we used when generating data:  5
save dataset to file 'data/blobs.csv' to be used in parallel example
create the taskfile to be given to the GNU parallel launcher
```

You would do this to generate an appropriate `taskfile.txt` with one task invocation per line
before perform the GNU `parallel` batch job.

To execute from a taskfile set of tasks, invoke the launcher like this:

```bash
(keras-tf-gpu) slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ sbatch slurm_parallel_launcher_single_node.sh taskfile.txt
Submitted batch job 135
(keras-tf-gpu) slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ squeue
             JOBID PARTITION     NAME     USER    STATE       TIME  NODES     CPUS MIN_MEMO TIME_LEF NODELIST(REASON)
               135       cpu slurm_pa      slu  RUNNING       0:02      1       16        0  1:59:58 cpu-1-01
```

In the example, the `testfile.txt` file has the following structure:

```bash
(base) slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ cat taskfile.txt 
python,unsupervised/some_funcs.py,data/blobs.csv,2
python,unsupervised/some_funcs.py,data/blobs.csv,3
python,unsupervised/some_funcs.py,data/blobs.csv,4
python,unsupervised/some_funcs.py,data/blobs.csv,5
python,unsupervised/some_funcs.py,data/blobs.csv,6
python,unsupervised/some_funcs.py,data/blobs.csv,7
python,unsupervised/some_funcs.py,data/blobs.csv,8
python,unsupervised/some_funcs.py,data/blobs.csv,9
python,unsupervised/some_funcs.py,data/blobs.csv,10
python,unsupervised/some_funcs.py,data/blobs.csv,11
python,unsupervised/some_funcs.py,data/blobs.csv,12
python,unsupervised/some_funcs.py,data/blobs.csv,13
python,unsupervised/some_funcs.py,data/blobs.csv,14
python,unsupervised/some_funcs.py,data/blobs.csv,15
python,unsupervised/some_funcs.py,data/blobs.csv,16
python,unsupervised/some_funcs.py,data/blobs.csv,17
python,unsupervised/some_funcs.py,data/blobs.csv,18
python,unsupervised/some_funcs.py,data/blobs.csv,19
python,unsupervised/some_funcs.py,data/blobs.csv,20
python,unsupervised/some_funcs.py,data/blobs.csv,21
python,unsupervised/some_funcs.py,data/blobs.csv,22
python,unsupervised/some_funcs.py,data/blobs.csv,23
python,unsupervised/some_funcs.py,data/blobs.csv,24
python,unsupervised/some_funcs.py,data/blobs.csv,25
python,unsupervised/some_funcs.py,data/blobs.csv,26
python,unsupervised/some_funcs.py,data/blobs.csv,27
python,unsupervised/some_funcs.py,data/blobs.csv,28
python,unsupervised/some_funcs.py,data/blobs.csv,29
python,unsupervised/some_funcs.py,data/blobs.csv,30
python,unsupervised/some_funcs.py,data/blobs.csv,31
python,unsupervised/some_funcs.py,data/blobs.csv,32
python,unsupervised/some_funcs.py,data/blobs.csv,33
python,unsupervised/some_funcs.py,data/blobs.csv,34
python,unsupervised/some_funcs.py,data/blobs.csv,35
python,unsupervised/some_funcs.py,data/blobs.csv,36
python,unsupervised/some_funcs.py,data/blobs.csv,37
python,unsupervised/some_funcs.py,data/blobs.csv,38
python,unsupervised/some_funcs.py,data/blobs.csv,39
python,unsupervised/some_funcs.py,data/blobs.csv,40
```

There are 4 comma separated parameters, where the first one is actually the python interpreter
we want to invoke on the other parameters in this task.  This will be resolved by the launcher 
script as a set of 39 srun commands, looking like:

```bash
(keras-tf-gpu) slu@slurm:~/repos/tlccloud-slurmexamples/05-gnuparallel$ cat logs/job_135/taskfile.txt
Seq	Host	Starttime	JobRuntime	Send	Receive	Exitval	Signal	Command
4	:	1782938284.340	     8.027	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores python unsupervised/some_funcs.py data/blobs.csv 5 > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs/job_135/taskfile.txt.log.4
5	:	1782938284.543	     8.332	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores python unsupervised/some_funcs.py data/blobs.csv 6 > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs/job_135/taskfile.txt.log.5
6	:	1782938284.752	     9.574	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores python unsupervised/some_funcs.py data/blobs.csv 7 > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs/job_135/taskfile.txt.log.6
8	:	1782938285.159	     9.199	0	0	0	0	srun  --exclusive -n1 -c 1 --cpu-bind=cores python unsupervised/some_funcs.py data/blobs.csv 9 > /home/slu/repos/tlccloud-slurmexamples/05-gnuparallel/logs/job_135/taskfile.txt.log.8
...
```

Each `srun` invoked by GNU `parallel` exeuctes the python `some_funcs.py` script, and passes the data file name and the
number of clusters parameter we are performing the clustering with.

## GNU `parallel` `--cpu-bind=cores` / CPU cores vs. Intel HyperThread logical CPUs

Some Intel cpu models use a technology called HyperThreading.  On our TLC slurm cluster nodes, we usually have
8 actual physical cores per node, where each cpu core is an Intel core that supports HyperThreading.  This appears
to the Linux kernel as two logical cores for each actual physical core.

The logical hyperthreaded cores can increase performance of tasks in some instances.  But often when performing
a compute bound computational task, the hyperthreading provides no benefit, or can even hurt performance a bit
because of switching overhead.

The launcher script in this example passes in the `--cpu-bind=cores` to the srun commands, which is usually what
you probably want to do when working with hyperthreaded core cpus.  If you are trying to parallelize I/O bound
tasks, sometimes using full hyperthreading can help a bit, since I/O bound tasks will be waiting around more than
computing, thus having more jobs potentially available to execute can potentially increase performance.  In that
case you can change to using `--cpu-bind=threads` and set the `--ntasks-per-node=16` to 16 in our typical TLC
slurm environment, to try and use all logical hyperthreading cores.

You can investigate the difference here using the original `stress-ng` task, which is very much a compute bound
stress test.  Upping the number of tasks to 500, and then running first with the original settings of
`--cpu-bind=cores` and `--ntasks-per-node=8`, then running a second time changing these in the launcher script
to `--cpu-bind=threads` and `--ntasks-per-node=16` gives the following results:

| Model                      | Total Time |
|----------------------------|------------|
| 8 cores, no hyperthreading |   3789 sec |
| 16 hyperthreaded cores     |   3788 sec |

In this example, since the task is embarrassingly parallel, we would expect about a 8x speedup in the
first case when we have 8 cpus.  So since each task is set to run for 60 seconds, and we have 500
tasks, we hope to get a time approaching $(500 \times 60) / 8 = 3750 \; \text{sec}$.  Of course
if we truly had 16 cpus (e.g we could spread this out over 2 nodes), you would expect an embarrassingly parallel task to
finish in half of that time.
However, you can see from this run that the performance was the same.  You can get some variation if you rerun
multiple times.  But on average there shouldn't really be much of a difference between
hyperthreading and not using it for this task simple computationally bound example task.


## Using GNU `parallel` Across Multiple Nodes

In a previous example using `ipyparallel` we demonstrated executing embarrassingly parallel jobs
across multiple nodes.  We did the same task in this example, to do a grid search on the parameter
search for a `scikit-learn` `k-means` parameter search, but this example using GNU `parallel`
was limited to a single node.  GNU `parallel` does support distribution of tasks across multiple
compute nodes.  However scaling GNU `parallel` across multiple nodes is **Not Recommended**.  
GNU `parallel` directly uses `ssh` to spawn tasks, bypassing slurm, which can cause issues.  See
other tutorials for better ways to scale across multiple nodes.