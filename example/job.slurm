#!/bin/bash
#SBATCH --job-name=job_gamma
#SBATCH --output=%x_%A_%a.out
#SBATCH --error=%x_%A_%a.err
#SBATCH --mail-user="k.a.e.keijzer@math.leidenuniv.nl"
#SBATCH --mail-type="BEGIN","END","FAIL"
#SBATCH --partition="cpu-short"
#SBATCH --time=0-03:00:00
#hSBATCH --ntasks=20
#SBATCH --mem-per-cpu=15G
#SBATCH --gpus=1
#SBATCH --array=1-9

echo "#### Starting"

echo "Taskid = ${SLURM_ARRAY_TASK_ID}"

source ~/tst-md-module-setup2.sh
module load parallel

if [ ${SLURM_ARRAY_TASK_ID} == ${SLURM_ARRAY_TASK_MIN} ]; then
	DATA_DIR=~/data1/axis
	chmod +x run*sh
	echo "I'm the first"
	((counter=1))
	temp_DATA_DIR=${DATA_DIR}
	while [ -d "$temp_DATA_DIR" ]; do
	temp_DATA_DIR=${DATA_DIR}${counter}
	((counter+=1))
	done
	DATA_DIR=${temp_DATA_DIR}
	echo "DATA_DIR = ${DATA_DIR}"
	mkdir $DATA_DIR
	echo $DATA_DIR > token.lock
else
       sleep 5s
       DATA_DIR=$(cat token.lock)
fi

echo "DATA_DIR = ${DATA_DIR}"
STARTDIR=$(pwd)
SCRATCH=/scratchdata/${SLURM_JOB_USER}/${SLURM_JOB_ID}
SIMULATION=./$(head -n ${SLURM_ARRAY_TASK_ID} jobs | tail -n 1) 
echo "Running ${SIMULATION}"

mkdir ${SCRATCH}/tst
eval ${SIMULATION} ${SCRATCH} ${STARTDIR} ${DATA_DIR}
cp *.{err,out} $DATA_DIR
cp job.slurm $DATA_DIR
cp jobs ${DATA_DIR}
cp config.py ${DATA_DIR}

if [ ${SLURM_ARRAY_TASK_ID} == ${SLURM_ARRAY_TASK_MAX} ]; then
        echo "I'm the last"
fi

echo "#### Finished. Have a nice day"








