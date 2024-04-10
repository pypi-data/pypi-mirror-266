
source /usr/local/lib/init/global.profile

module use -a /swbuild/analytix/tools/modulefiles
module load miniconda3/v4
source activate haplo_env

export HAPLO_SESSION_DIRECTORY=$1
echo $1
echo $2
echo $3
python -m torch.distributed.run --nnodes 8 --nproc_per_node 4 --rdzv_id $2 --rdzv_backend c10d --rdzv_endpoint $3 scripts/example_train_session.py
