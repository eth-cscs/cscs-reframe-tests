#!/bin/bash
# /users/jfavre/rc-submit.alps-pvserver.sh
# updated Thu Feb 17 08:49:14 AM CET 2022 for Eiger, version 5.10

# usage
#echo "Usage : %1:Session name ($1)"
#echo "        %2:Job Wall Time ($2)"
#echo "        %3:server-num-nodes ($3)"
#echo "        %4:server-num-tasks-per-node ($4)"
#echo "        %5:server-port ($5)"
#echo "        %6:login node ($6)"
#echo "        %7:Version number (5.9 with Mesa for mc-partition) ($7)"
#echo "        %8:Queue's name (normal or debug) ($8)"
#echo "        %9:Memory per Node (standard or high($9)"
#echo "        %10:Account (csstaff or other($10)"
#echo "        %11:Reservation ("" or other($11)"

# Create a temporary filename to write our launch script into
TEMP_FILE=`mktemp`
HOST_NAME=`hostname`
echo "Temporary FileName is :" $TEMP_FILE

nservers=$[$3 * $4]

# Create a job script
echo "#!/bin/bash -l"                              >> $TEMP_FILE
echo "#SBATCH --job-name=$1"                       >> $TEMP_FILE
echo "#SBATCH --nodes=$3"                          >> $TEMP_FILE
echo "#SBATCH --ntasks-per-node=$4"                >> $TEMP_FILE
echo "#SBATCH --ntasks=$nservers"                  >> $TEMP_FILE
echo "#SBATCH --time=$2"                           >> $TEMP_FILE
echo "#SBATCH --account=${10}"                     >> $TEMP_FILE
echo "#SBATCH --partition=$8"                      >> $TEMP_FILE
# only ask for a reservation if in the normal queue and no greater than 5 nodes
if [ "$8" = "normal" ];then
  if [ ! -z "${11}" ]; then
    if [ ! "$3" -gt "5" ]; then
      echo "#SBATCH --reservation=${11}"       >> $TEMP_FILE
    fi
  fi
fi

if [ "$9" = "high" ]; then
echo "#SBATCH --mem=497G"                    >> $TEMP_FILE
fi

if [[ "$6" == *"eiger"* ]]; then
  echo "#SBATCH --constraint=mc"                 >> $TEMP_FILE
  cpuspertask=$[72 / $4]
fi
if [[ "$6" == *"daint"* ]]; then
  cpuspertask=$[256 / $4]
fi

################## daint.alps 513 ##################################################
if [ "$7" = "5.13.2:v2" ]; then
  echo "#SBATCH --uenv=paraview/5.13.2:v2 --view=paraview"           >> $TEMP_FILE
  echo "#SBATCH --hint=nomultithread"            >> $TEMP_FILE
  echo "srun --cpus-per-task=${cpuspertask} /user-environment/ParaView-5.13/gpu_wrapper.sh /user-environment/ParaView-5.13/bin/pvserver --reverse-connection --client-host=$HOST_NAME --server-port=$5" >> $TEMP_FILE

elif [ "$7" = "Santis-5.13-uenv" ]; then
  echo "#SBATCH --uenv=paraview/5.13.2:v2 --view=paraview"           >> $TEMP_FILE
  echo "#SBATCH --hint=nomultithread"            >> $TEMP_FILE
  echo "srun --cpus-per-task=${cpuspertask} /user-environment/ParaView-5.13/gpu_wrapper.sh /user-environment/ParaView-5.13/bin/pvserver --reverse-connection --client-host=$HOST_NAME --server-port=$5" >> $TEMP_FILE
fi


cat $TEMP_FILE

# submit the job

sbatch $TEMP_FILE

# wipe the temp file
rm $TEMP_FILE
