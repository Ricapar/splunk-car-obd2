#!/bin/bash



echo "Deleting old entires..."
/Applications/Splunk/bin/splunk search "index=torque_summary | delete" 

for TripID in $(/Applications/Splunk/bin/splunk search "index=torque | stats count by trip_uuid | fields trip_uuid" -preview false -header false); do
	echo "TripID = [$TripID]"
	/Applications/Splunk/bin/splunk search "\`green_score($TripID)\` | eval trip_uuid=\"$TripID\" | collect index=torque_summary" -preview false -app obd2 
	
done


