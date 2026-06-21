# Submitting Jobs

## A Simple Job from the Command Line

You can submit a job to the batching system wholly from the command line.  For example do the following:

```
sbatch --partition=debug --job-name=myjob --mem=1G --time=1:0 --output=myjob.slurm.log --wrap="hostname; date; echo 'Started myjob'; sleep 10; echo 'Finished myjob'; date"
```

If it is not clear, the `--wrap` flag is actually a list of command line commands.  When these are run, the `hostname` where the job is run on is displaeyed, then the current datetime, etc.  The job sleeps for 10 seconds and then finishes.  The command line flags used are:

- `--partition=<partition name>`: Default is debug partition currently on TLC slurm
  - Use `scontrol show partitions` to see a list of available partitions.
- `--job-name=<job name>`: A human-readable name for the job (Defaults to a random number if you don't specify a name).
- `--time=<days>-<hours>:<minutes>`: time limit, after which job will be killed.  TLC debug partition queue
  usually has a time limit of 8 hours, so you can't specify a larger time limit than this..
- `--mem=<size>`: can use `G` for GB or `M` for MB.  Default is currently `1000M` for job sizes on TLC, which may be too small 
  for your needs, thus you may need to determine and specify needed memory to get your jobs to run correctly.
- `--output=<filename>`: where to write STDOUT and STDERR, default is `slurm-<job_id>.out` if you don't specify.

Slurm has short versions of the flags for most all of these options.  So the previous command could be done equivalently as:

```
sbatch -p debug -J myjob --mem=1G -t 1:0 -o myjob.slurm.log --wrap="hostname; date; echo 'Started myjob'; sleep 10; echo 'Finished myjob'; date"
```

## A Simple Job from a bash Script

Usually you won't want to type in a whole long line to batch a job using slurm.  Instead you usually want to create a bash shell script
that spedifies all of the command line flags and the commands to run.  For example, in this directory is a file named `myjob.sh` that
contains the following lines:

```
#!/bin/bash
#SBATCH --partition=debug
#SBATCH --job-name=mjob
#SBATCH --mem=1G
#SBATCH --time=1-0:0
#SBATCH --output=myjob.slurm.log
hostname
date
echo 'Started myjob'
sleep 10
echo 'Finished myjob'
date
```

We can run the job using this script equivalently using the following:

```
sbatch myjob.sh
```

Not that you can use either short flag or long flag names after
SBATCH, though it is recommended that you use the long names (as shown
here) as these are more readable and obvious to someone else or your
future self on what options you are setting in your batch jobs.  You
will need to learn to use a simple terminal based editor to create and
modify these files.  The TLC slurm cluster has `nano`, `vi`, and
`emacs` available to use for editing files from the command line.

- [`nano` editor commands](https://www.nano-editor.org/dist/latest/cheatsheet.html)
- [`vi` editor commands](https://www.redhat.com/sysadmin/introduction-vi-editor)
- [`emacs` editor commands](https://ftp.gnu.org/old-gnu/Manuals/emacs-20.7/html_chapter/emacs_8.html)
