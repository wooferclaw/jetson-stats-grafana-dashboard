pip install prometheus-client
sudo cp jetson_stats_prometheus_collector.py /usr/local/bin/

sudo cp jetson_stats_prometheus_collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start jetson_stats_prometheus_collector
sudo systemctl status jetson_stats_prometheus_collector
