#!/bin/bash

#SBATCH --job-name="¯\\_(ツ)_/¯"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=4
#SBATCH --cpus-per-task=40
#SBATCH --mem=600000
#SBATCH --time=5-00:00:00

nodes=( $( scontrol show hostnames $SLURM_JOB_NODELIST ) )
nodes_array=($nodes)
head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)

#export LOGLEVEL=INFO
#export TORCH_CPP_LOG_LEVEL=INFO
#export TORCH_DISTRIBUTED_DEBUG=DETAIL
export CUDA_LAUNCH_BLOCKING=1

srun torchrun \
--nnodes 1 \
--nproc_per_node gpu \
--rdzv_id $RANDOM \
--rdzv_backend c10d \
--rdzv_endpoint $head_node_ip:36484 \
scripts/quick.py
