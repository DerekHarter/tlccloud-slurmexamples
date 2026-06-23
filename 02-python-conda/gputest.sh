#!/bin/bash
#SBATCH --job-name=gputest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
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
