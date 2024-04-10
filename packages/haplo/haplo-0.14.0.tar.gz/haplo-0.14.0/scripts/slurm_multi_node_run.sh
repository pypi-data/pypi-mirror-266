#!/bin/bash

#SBATCH --job-name="¯\\_(ツ)_/¯"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=40
#SBATCH --mem=600000
#SBATCH --time=1-00:00:00

session_name="base_old_version"
current_time=$(date "+%Y_%m_%d_%H_%M_%S")
export HAPLO_SESSION_DIRECTORY="sessions/${current_time}_${session_name}"
mkdir -p "${HAPLO_SESSION_DIRECTORY}"

nodes=( $( scontrol show hostnames $SLURM_JOB_NODELIST ) )
nodes_array=($nodes)
head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)

echo Node IP: $head_node_ip

export OMP_NUM_THREADS=11

srun torchrun \
--nnodes 1 \
--nproc_per_node 1 \
--rdzv_id $RANDOM \
--rdzv_backend c10d \
--rdzv_endpoint $head_node_ip:36484 \
scripts/example_train_session.py
