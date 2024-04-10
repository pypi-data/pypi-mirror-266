#PBS -l select=2:model=mil_a100:ncpus=40:ngpus=4:mem=250GB
#PBS -l place=scatter:excl
#PBS -l walltime=0:05:00
#PBS -j oe
#PBS -W group_list=s2853
#PBS -q gpu_debug@pbspl4

source /usr/local/lib/init/global.profile

module use -a /swbuild/analytix/tools/modulefiles
module load miniconda3/v4
source activate haplo_env

module load mpi-hpe/mpt

export MPI_SHEPHERD=true
export MPI_DSM_DISTRIBUTE=0

unset CUDA_VISIBLE_DEVICES
mpiexec -perhost 1 echo $CUDA_VISIBLE_DEVICES
mpiexec -perhost 1 python -c "import torch; print(torch.cuda.is_available())"
mpiexec -perhost 1 sh scripts/gpu_sub_check.sh