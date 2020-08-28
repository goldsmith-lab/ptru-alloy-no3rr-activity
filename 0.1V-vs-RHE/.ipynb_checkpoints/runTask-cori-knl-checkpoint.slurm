#!/bin/bash
#SBATCH --job-name=mkmcxx
#SBATCH --account=m3287
#SBATCH --qos=flex
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=66
#SBATCH --cpus-per-task=4
#SBATCH --core-spec=2
#SBATCH --constraint=knl
#SBATCH --time=48:00:00
#SBATCH --error=vt_vasp%j.err
#SBATCH --output=vt_vasp%j.out
#SBATCH --mail-user=samueldy@umich.edu
#SBATCH --mail-type=ALL
#
#SBATCH --comment=96:00:00
#SBATCH --time-min=2:00:00
#SBATCH --signal=B:USR1@250
#SBATCH --requeue
#SBATCH --open-mode=append
#SBATCH --export=ALL

#user setting
# export OMP_PROC_BIND=true
# export OMP_PLACES=threads
# export OMP_NUM_THREADS=4

#srun must execute in background and catch signal on wait command
module load parallel

# Execute simulations in parallel, restarting where necessary.
cat commands.txt | parallel -j66 --bar --resume --joblog ./joblog {}
# put any commands that need to run to continue the next job (fragment) here
ckpt_mkmcxx() {
set -x

echo "Going down for checkpoint."

# Quit the process cleanly so that the job requeues
PID_PARALLEL=$(pidof parallel)
kill $PID_PARALLEL

set +x
}

ckpt_command=ckpt_mkmcxx
max_timelimit=48:00:00
ckpt_overhead=250

# requeueing the job if remaining time >0
. ./vartime-setup.sh
requeue_job func_trap USR1

wait
