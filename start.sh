if [[ -n $RCLONE_CONFIG ]]; then
 echo "Rclone config detected"
 echo -e "$RCLONE_CONFIG" > /app/rclone.conf

elif

sed -i'' -e "/bt-tracker=/d" $(pwd)/aria.conf
tracker_list=`curl -Ns https://raw.githubusercontent.com/XIU2/TrackersListCollection/master/all.txt | awk '$1' | tr '\n' ',' | cat`
tracker_list=`curl -Ns https://trackerslist.com/all_aria2.txt | awk '$1' | tr '\n' ',' | cat`
tracker_list=`curl -Ns https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt | awk '$1' | tr '\n' ',' | cat`
tracker_list=`curl -Ns https://raw.githubusercontent.com/iamLiquidX/trackerlistx/main/trackers.txt | awk '$1' | tr '\n' ',' | cat`
echo -e "bt-tracker=$tracker_list" >> $(pwd)/aria.conf

fi
bash setup.sh; python3 -m tobrot
