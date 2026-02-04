mkdir /home/{reports_dir}/$(date -d "$(date) - 1 year" +"%Y")/
mv /home/{reports_dir}/*.csv /home/{reports_dir}/$(date -d "$(date) - 1 year" +"%Y")/
