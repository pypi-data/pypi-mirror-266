#PBS -l select=8:model=mil_a100:ncpus=40:ngpus=4:mem=250GB
#PBS -l place=scatter:excl
#PBS -l walltime=5:00:00
#PBS -j oe
#PBS -W group_list=s2853
#PBS -q gpu_long@pbspl4
session_name="8_node_ssh_no_in_mem"
current_time=$(date "+%Y_%m_%d_%H_%M_%S")
export HAPLO_SESSION_DIRECTORY="sessions/${current_time}_${session_name}"
mkdir -p "${HAPLO_SESSION_DIRECTORY}"
qalter -o "${HAPLO_SESSION_DIRECTORY}/${PBS_JOBID}.log" $PBS_JOBID

source /usr/local/lib/init/global.profile

module use -a /swbuild/analytix/tools/modulefiles
module load miniconda3/v4
source activate haplo_env

module load mpi-hpe/mpt

head_node_hostname=`/bin/hostname -s`

export MPI_SHEPHERD=true
export MPI_DSM_DISTRIBUTE=0

random_rdzv=$RANDOM

NODES=($( cat $PBS_NODEFILE | uniq ))

echo "cd haplo; sh scripts/pbs_multi_node_run_ssh_sub.sh $HAPLO_SESSION_DIRECTORY $random_rdzv $head_node_hostname"
for node in ${NODES[@]}
do
  if [[ $node != $(eval hostname) ]]
  then
    ssh -A -o StrictHostKeyChecking=no $node "cd haplo; sh scripts/pbs_multi_node_run_ssh_sub.sh $HAPLO_SESSION_DIRECTORY $random_rdzv $head_node_hostname" &
  fi
done
#
python -m torch.distributed.run --nnodes 8 --nproc_per_node 4 --rdzv_id $random_rdzv --rdzv_backend c10d --rdzv_endpoint $head_node_hostname scripts/example_train_session.py
