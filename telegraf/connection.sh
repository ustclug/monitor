#!/bin/bash

port_list_input=${1//:/|}
port_list=${port_list_input:-"80:443"}
for type in CLOSE_WAIT CLOSING ESTABLISHED FIN_WAIT1 FIN_WAIT2 LAST_ACK SYN_RECV TIME_WAIT; do
	netstat -ntW  | grep $type | awk '{print $4}' | grep -P ":($port_list)\$" | sort | uniq -c | sort -k 2 | 
	while read line; do
		count=$(awk '{print $1}' <<< $line)
		socket=$(awk '{print $2}' <<< $line)
		address=${socket%:*}
		port=${socket##*:}
		echo "connection,protocol=tcp,port=$port,address=$address ${type,,}=$count"
	done
	netstat -ntW  | grep $type | awk '{print $4}' | awk -F: '{print $NF}' | grep -P "^($port_list)\$" | sort | uniq -c | sort -k 2 | awk "{printf(\"connection,protocol=tcp,port=%s,address=any ${type,,}=%s\n\",\$2,\$1);}"
done
