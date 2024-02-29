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

STARTDIR=$(pwd)
DATA_DIR=${STARTDIR}/datastore/
SCRATCH=${STARTDIR}/scratch/
mkdir -p $SCRATCH/tst

chmod +x run*sh
echo "DATA_DIR = ${DATA_DIR}"
cat jobs | while read job; do
	./$job $SCRATCH $STARTDIR $DATA_DIR &
done
#eval ${SIMULATION} ${SCRATCH} ${STARTDIR} ${DATA_DIR}
cp job.slurm $DATA_DIR
cp jobs ${DATA_DIR}

echo "#### Finished. Have a nice day"









