#!/bin/bash
#$ -N spinodal_opt
#$ -pe smp 12
#$ -j y
#$ -l h_rt=240:00:00
#$ -t 1

# Check if SGE_TASK_ID exists, else set to 0
if ! [ -n "${SGE_TASK_ID+1}" ]; then
  SGE_TASK_ID=0
else
  # Subtract 1 to convert from 1-based to 0-based indexing
  SGE_TASK_ID=$((SGE_TASK_ID - 1))
fi

JOB_ID=$(echo "${JOB_ID}" | sed 's/\[[^][]*\]//g')

module load use.own
module load anaconda3
module load matlab
module load abaqus/2020
cd $SGE_O_WORKDIR

# Here is where the application is started on the node
# Activating my conda environment:
source activate mfb_env

# Limiting number of threads
# OMP_NUM_THREADS=12
# export OMP_NUM_THREADS=12

# Check if SGE_TASK_ID exists, else set to 1
if ! [ -n "${SGE_TASK_ID}" ]; then
  SGE_TASK_ID=None
fi

# Executing my Python program
python main.py ++hpc.jobid=${SGE_TASK_ID} hydra.run.dir=outputs/$(date +%Y-%m-%d)/${JOB_ID} ++sge_jobid=${JOB_ID}
