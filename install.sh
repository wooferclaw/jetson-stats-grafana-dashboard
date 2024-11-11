pip install prometheus-client
sudo cp jetson_stats_prometheus_collector.py /usr/local/bin/

# Install service for the current user
mkdir -p ~/.config/systemd/user
cp jetson_stats_prometheus_collector.service ~/.config/systemd/user/
sudo systemctl daemon-reload
sudo systemctl start jetson_stats_prometheus_collector
sudo systemctl status jetson_stats_prometheus_collector
