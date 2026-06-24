#!/usr/bin/env bash
#SBATCH --partition=debug       # debug partition 
#SBATCH --job-name=ipy_engines  # job name
#SBATCH --nodes=2               # 2 nodes, you can increase it
#SBATCH --ntasks=20             # 10 tasks total, for some reason we need to overspecify tasks, if want X workers, try X+10 tasks
#SBATCH --cpus-per-task=1       # 1 cpu per task
#SBATCH --time=1:00:00          # Job is killed after 1h

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
echo "--------------------------------------------------"
echo ""

#create a new ipython profile appended with the job id number
profile=job_${SLURM_JOB_ID}

echo "Creating profile_${profile}"
ipython profile create ${profile}

# Number of tasks, the example script showed -2 here to account for the controller and the job
# executor, so if wanted 8 workers, started with ntasks 10
# But we are having some issue with srun not starting unless we give more than +2.  +10 is save,
# so here we want 10 workers so set ntasks to 20 and subtract fixed 10 overhead as number of
# workers to start.
export NB_WORKERS=$((${SLURM_NTASKS}-10))

LOG_DIR="$(pwd)/logs/job_${SLURM_JOBID}"
mkdir -p ${LOG_DIR}
DATA_DIR="$(pwd)/data/job_${SLURM_JOBID}"
mkdir -p ${DATA_DIR}

echo "NB_WORKERS: $NB_WORKERS"
echo "SLURM_NTASKS: $SLURM_NTASKS"
echo "LOG_DIR: $LOG_DIR"
echo "DATA_DIR: $DATA_DIR"
echo "--------------------------------------------------"
echo ""

# Record start time to display elapsed time of computation
echo "Start time: `date`"
start=$(date +%s)

# srun: runs ipcontroller -- forces to start on first node 
echo "Launching controller hostname: $(hostname) SLURM_CPUS_PER_TASK: $SLURM_CPUS_PER_TASK profile: $profile"
srun --nodelist=$(hostname) --output=${LOG_DIR}/ipcontroller-%j-workers.out --nodes=1 --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} ipcontroller --ip="*" --profile=${profile} &
sleep 10
echo ""

# srun: runs ipengine on each available core -- controller location first node
echo "Launching worker engines hostname: $(hostname) NB_WORKERS: $NB_WORKERS SLURM_CPUS_PER_TASK: $SLURM_CPUS_PER_TASK profile: $profile"
srun --output=${LOG_DIR}/ipengine-%j-workers.out --ntasks=${NB_WORKERS} --cpus-per-task=${SLURM_CPUS_PER_TASK} ipengine --profile=${profile} --location=$(hostname) &
sleep 25
echo ""

# srun: starts for the code exeuction.  This is the main.py script which simply requests jobs to be scheduled and run
# by the ipcontroller on the ipengine workers.  Notice that we do not background this final srun, the batch job finishes
# when the code executor performs all of its work and completes.
echo "Launching job for script $1 profile: $profile"
srun --output=${LOG_DIR}/code-%j-execution.out  --nodes=1 --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} python $1 --profile=${profile} 
echo ""

# Record end time to display elasped time of computation 
echo "End time: `date`"
end=$(date +%s)
secs=($end-$start)
echo "Elapsed time: $((secs/1)) seconds"
printf 'Elapsed time: %d:%02d:%02d\n' $((secs/3600)) $((secs%3600/60)) $((secs%60))
