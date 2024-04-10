#PBS -l select=1:ncpus=1:model=ivy
#PBS -l walltime=5:00:00
#PBS -j oe
#PBS -W group_list=s2853
#PBS -q debug@pbspl1
session_name="database_check"
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

python scripts/check_database.py