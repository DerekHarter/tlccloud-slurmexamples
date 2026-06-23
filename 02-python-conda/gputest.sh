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
conda activate keras-tf-gpu
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
./gputest.py
echo "End time: `date`"
end=$(date +%s)
secs=($end-$start)
echo "Elapsed time: $((secs/1)) seconds"
printf 'Elapsed time: %d:%02d:%02d\n' $((secs/3600)) $((secs%3600/60)) $((secs%60))
