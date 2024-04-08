

for ip in $(sudo masscan -p 80 192.168.86.0/24 2>&1|grep Discove|awk -F' on ' '{ print $2 }')
do
	curl http://$ip/debug/clip.html  >/tmp/hue/$ip.html
	if [[ $? == 0 ]];
	then
		echo $ip
	fi
done
