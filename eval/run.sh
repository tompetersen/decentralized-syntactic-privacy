#!/bin/bash

max_number_of_parties=8

for method in securesum motion ;
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

	for dataset in medical adult ;
	do

		for ((p=8; p<=$max_number_of_parties; p++))
		do
			now=$(date +%Y%m%d_%H%M%S)
			echo $now
			logfile="runs_nw_$method/$dataset-$p-$now.txt"
                        touch $logfile

			for ((i=1; i<=p; i++))
			do
				echo "Starting $i..."
				python $boxpath $i $p --dataset $dataset > /dev/null &
			done

			echo "Starting central..."
			python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK BEFORE: ' + str(network) + '\n');" >> $logfile

			python $centralpath --number_of_boxes $p --dataset $dataset | tee -a $logfile

			python -c "import psutil,sys;network=psutil.net_io_counters(pernic=True);sys.stdout.write('NETWORK AFTER: ' + str(network) + '\n');" >> $logfile
		done

	done
done


