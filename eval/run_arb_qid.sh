#!/bin/bash

number_of_parties=3

source venv/bin/activate
use_qids=$(python qid_power.py)

for method in motion securesum ;
do
	if [ $method == "securesum" ]; then
		path="../original"
	else
		path="../ours"
	fi
	
	venvpath="../venv/bin/activate"
	boxpath="$path/run_box.py"
	centralpath="$path/run_central.py"

	source $venvpath

	for qid in $use_qids ;
	do
		now=$(date +%Y%m%d_%H%M%S)
		echo $now
		logfile="data/runs_arb_qid_$method/adult-$qid-$now.txt"
		mkdir -p "$(dirname "$logfile")" && touch "$logfile"

		for ((i=1; i<=$number_of_parties; i++))
		do
			echo "Starting $i..."
			python $boxpath $i $number_of_parties --dataset adult > /dev/null &
		done

		echo "Starting central..."
		python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK BEFORE: ' + str(network) + '\n');" >> $logfile

		python $centralpath --number_of_boxes $number_of_parties --dataset adult --used_qids $qid | tee -a $logfile

		python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK AFTER: ' + str(network) + '\n');" >> $logfile
	done

done


