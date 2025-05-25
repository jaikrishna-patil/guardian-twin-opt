#!/bin/bash

#SBATCH --job-name=gt
#SBATCH -N 1            # number of nodes
#SBATCH -c 1            # number of cores
#SBATCH -t 4:00:00   # time in d-hh:mm:ss
#SBATCH --partition=highmem
#SBATCH --qos=grp_pshakari
#SBATCH -e slurm.%j.err # file to save job's STDERR (%j = JobId)
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH --mail-user="jpatil14@asu.edu"
#SBATCH --export=NONE   # Purge the job-submitting shell environment
#SBATCH --mem=200GB
#-------------------------------------------------------------------------
#cd ~/scratch/jpatil14/pyreason-experiments/anyBurl_experiments

# Initialize conda environment
module load mamba/latest
echo Checking if env_gt_pr3 conda environment exists
if conda env list | grep ".*env_gt_pr3.*" >/dev/null 2>&1
then
    echo env_gt_pr3 environment exists
    source activate env_gt_pr3
else
    echo Creating env_gt_pr3 conda environment
    conda create -n env_gt_pr3 python=3.9
    source activate env_gt_pr3
    echo Installing necessary packages
    pip install -r requirements.txt
    pip install git+https://github.com/lab-v2/pyreason.git@refs/pull/43/head
    pip install argparse
fi


# Run pyreason
python3 create_data_samples_new.py
#-------------------------------------------------------------------------