#!/bin/bash
# -------------------- Time tracking, signal trapping, and requeue functions  ------------------------ 
secs2timestr() {
 ((h=${1}/3600))
 ((m=(${1}%3600)/60))
 ((s=${1}%60))
 printf "%02d:%02d:%02d\n" $h $m $s
}

timestr2secs() {
echo $1| sed 's/-/:/' | awk -F: '{print $4, $3, $2, $1}'|awk '{print $1+60*$2+3600*$3+86400*$4}'
}

parse_job(){
    #set default
    if [[ -z $ckpt_overhead ]]; then let ckpt_overhead=60; fi
    if [[ -z $max_timelimit ]]; then let max_timelimit=172800; fi

    TOTAL_TIME=$(squeue -h -j $SLURM_JOB_ID -o %k)
    timeAlloc=$(squeue -h -j $SLURM_JOB_ID -o %l)

    fields=`echo $timeAlloc | awk -F ':' '{print NF}'`
    if [ $fields -le 2 ]; then
       timeAlloc=`echo 0:$timeAlloc`
    fi

    timeAlloc=`timestr2secs $timeAlloc`
    TOTAL_TIME=`timestr2secs $TOTAL_TIME`

    let remainingTimeSec=TOTAL_TIME-timeAlloc+ckpt_overhead
    if [ $remainingTimeSec -gt 0 ]; then
        remainingTime=`secs2timestr $remainingTimeSec`
        scontrol update JobId=$SLURM_JOB_ID Comment=$remainingTime

        let maxtime=`timestr2secs $max_timelimit`
        if [ $remainingTimeSec -gt $maxtime ]; then 
           requestTime=$max_timelimit
        else
           requestTime=$remainingTime
        fi
        echo time remaining \$remainingTime: $remainingTime
        echo next timelimit \$requestTime: $requestTime
    fi
}

requeue_job() {

    parse_job 

    if [ -n $remainingTimeSec ] && [ $remainingTimeSec -gt 0 ]; then
        func="$1" ; shift
        for sig ; do
            trap "$func $sig" "$sig"
        done
    else 
       echo no more job requeues,done!
    fi
}

func_trap() {
######################################################
# -------------- checkpoint application --------------
######################################################
    # insert checkpoint command here if any
    $ckpt_command 
    scontrol requeue ${SLURM_JOB_ID}
    scontrol update JobId=${SLURM_JOB_ID} TimeLimit=${requestTime}
    echo \$?: $?
}


#----------------------------- Set up DMTCP environment for a job ------------#
start_coordinator()
{
    fname=dmtcp_command.$SLURM_JOBID
    h=`hostname`

    check_coordinator=`which dmtcp_coordinator`
    if [ -z "$check_coordinator" ]; then
        echo "No dmtcp_coordinator found. Check your DMTCP installation and PATH settings."
        exit 0
    fi

    dmtcp_coordinator --daemon --exit-on-last -p 0 --port-file $fname $@ 1>/dev/null 2>&1

    while true; do
        if [ -f "$fname" ]; then
            p=`cat $fname`
            if [ -n "$p" ]; then
                break
            fi
        fi
    done
    export DMTCP_COORD_HOST=$h
    export DMTCP_COORD_PORT=$p
}

#wait for a process to complete
wait_pid () {
    pid=$1
    while [ -e /proc/$pid ]
    do
        sleep 5
    done
}

