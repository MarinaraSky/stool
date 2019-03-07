cd stool
git checkout master stormdrain.py

ssh root@10.40.7.130 'pkill -9 tmux; pkill -9 stormdrain.py;'
scp stormdrain.py root@10.40.7.130:~
ssh root@10.40.7.130 '~/start_listener.cron'

ssh root@10.40.7.66 'pkill -9 tmux; pkill -9 stormdrain.py;'
scp stormdrain.py root@10.40.7.66:~
ssh root@10.40.7.66 '~/start_listener.cron'

ssh root@10.40.7.235 'pkill -9 tmux; pkill -9 stormdrain.py;'
scp stormdrain.py root@10.40.7.235:~
ssh root@10.40.7.235 '~/start_listener.cron'

