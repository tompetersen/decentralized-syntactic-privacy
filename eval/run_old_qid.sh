#!/bin/bash

# old version not used anymore - try run_arb_qid.sh

number_of_parties=3
max_number_of_qids=6


for method in motion securesum ;
do
	if [ $method == "securesum" ]; then
		path="../orginal"
	else
		path="../ours"
	fi
	
	venvpath="../venv/bin/activate"
	boxpath="$path/run_box.py"
	centralpath="$path/run_central.py"

	source $venvpath

	for ((num_qid=1; num_qid<=$max_number_of_qids; num_qid++))
	do
		now=$(date +%Y%m%d_%H%M%S)
		echo $now
		logfile="data/runs_qid_$method/adult-$num_qid-$now.txt"
		mkdir -p "$(dirname "$logfile")" && touch "$logfile"

		for ((i=1; i<=$number_of_parties; i++))
		do
			echo "Starting $i..."
			python $boxpath $i $number_of_parties --dataset adult > /dev/null &
		done

		echo "Starting central..."
		python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK BEFORE: ' + str(network) + '\n');" >> $logfile

		python $centralpath --number_of_boxes $number_of_parties --dataset adult --number_of_qids $num_qid | tee -a $logfile

		python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK AFTER: ' + str(network) + '\n');" >> $logfile
	done

done


