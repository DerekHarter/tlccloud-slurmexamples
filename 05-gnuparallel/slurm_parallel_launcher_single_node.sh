#!/bin/bash -l
#SBATCH --time=02:00:00
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1


# Just useful check
print_error_and_exit() { echo "***ERROR*** $*"; exit 1; }
hash parallel 2>/dev/null && test $? -eq 0 || print_error_and_exit "Parallel is not installed on the system"

# Increase the user process limit.
ulimit -u 10000

echo "Node: ${SLURM_NODELIST}"
echo "Executing ${SLURM_NTASKS} independant tasks at the same time"

# the --exclusive to srun makes srun use distinct CPUs for each job step
# -N1 -n1 single task with ${SLURM_CPUS_PER_TASK} cores
SRUN="srun  --exclusive -n1 -c ${SLURM_CPUS_PER_TASK:=1} --cpu-bind=cores"

HOSTNAME=$(hostname)
LOGS="logs/job_${SLURM_JOBID}"
RESUME=""
TASKFILE=""
NTASKS=""


#=======================
# Get Optional arguments
#=======================
while [ $# -ge 1 ]; do
    case $1 in
        -r | --resume)           shift; LOGS=$1; RESUME=" --resume ";;
        -n | --ntasks)           shift; NTASKS="$1"                            ;;
        -* | --*)                echo "[Warning] Invalid option $1"          ;;
        *)                       break                                       ;;
    esac
    shift
done

#=======================
# Get Mandatory  Options
#=======================

if [[ "$#" < 1 ]]; then
    print_error_and_exit "No tasks defined"
else
    TASKFILE="$1"
    TASKFILE_DIR=$(cd "$(dirname "${TASKFILE}")" && pwd)
    TASKFILE_NAME="$(basename "${TASKFILE}")"
fi

echo "Starting parallel worker initialisation on $(hostname)"

#=======================
# Set logs for resuming
#=======================

LOGS_DIR="${TASKFILE_DIR}/${LOGS}"
TASKFILE_MAINLOG="${LOGS_DIR}/${TASKFILE_NAME//sh/log}"
PARALLEL="parallel --delay 0.2 -j ${SLURM_NTASKS} --joblog ${TASKFILE_MAINLOG} ${RESUME}"


echo "Create logs directory if not existing"
mkdir -p ${LOGS_DIR}

# NOTE: the if part here handles when a file of separate commands to run is passed in
# we currently add a task number using awk as parallel parameter {1} and we have hardcoded
# the example to expect 4 comma separated parameters in the file
# python, script to run, datafile, n_clusters.  
# If there are more or less parameters this would have to be adjusted.
if [[ -z ${NTASKS} ]];then
    cat ${TASKFILE} |                                      \
    awk -v NNODE="$SLURM_NNODES" -v NODEID="$SLURM_NODEID" \
    'NR % NNODE == NODEID {printf "%d,%s\n", NR, $0}' |                               \
    ${PARALLEL} --colsep '\,' "${SRUN} {2} {3} {4} {5} > ${LOGS_DIR}/$(basename ${TASKFILE}).log.{1}"
# The else part handles when --ntasks is specified and we are simply executing the same 
# task NTASKS number of times
else
    echo  "$(seq 1 ${NTASKS})" |                             \
    awk -v NNODE="$SLURM_NNODES" -v NODEID="$SLURM_NODEID" \
    'NR % NNODE == NODEID' |                               \
    ${PARALLEL} "${SRUN} ${TASKFILE} > ${LOGS_DIR}/$(basename ${TASKFILE}).log.{1}"
fi