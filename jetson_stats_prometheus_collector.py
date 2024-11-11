#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2021 Stefan von Cavallar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import atexit
import argparse
from jtop import jtop, JtopException
from prometheus_client.core import InfoMetricFamily, GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server


class CustomCollector(object):
    def __init__(self):
        atexit.register(self.cleanup)
        self._jetson = jtop()
        self._jetson.start()
        #for key, value in self._jetson.__dict__.items():
        #    print(f"{key}: {value}")
        #print(self._jetson.cpu)

    def cleanup(self):
        print("Closing jetson-stats connection...")
        self._jetson.close()

    def collect(self):
        if self._jetson.ok():
            # print('emc: ', self._jetson.emc)
            # print('iram: ', self._jetson.iram)
            # print('mts: ', self._jetson.mts)

            #
            # Board info 
            #
            i = InfoMetricFamily('jetson_info_board', 'Board sys info', labels=['board_info'])
            #print(self._jetson)
            i.add_metric(['info'], {
                'machine': self._jetson.board['platform']['Machine'], 
                'jetpack': self._jetson.board['hardware']['Jetpack'], 
                'l4t': self._jetson.board['hardware']['L4T']
                })
            yield i

            i = InfoMetricFamily('jetson_info_hardware', 'Board hardware info', labels=['board_hw'])                    
            i.add_metric(['hardware'], {
                'type': self._jetson.board['hardware']['Module'],
                'codename': self._jetson.board['hardware']['699-level Part Number'],
                'soc': self._jetson.board['hardware']['SoC'],
                'chip_id': self._jetson.board['hardware']['P-Number'],
                'module': self._jetson.board['hardware']['Module'],
                'board': self._jetson.board['hardware']['Model'],
                'cuda_arch_bin': self._jetson.board['hardware']['CUDA Arch BIN'],
                'serial_number': self._jetson.board['hardware']['Serial Number']
                })
            yield i

            #
            # NV power mode
            #
            i = InfoMetricFamily('jetson_nvpmode', 'NV power mode', labels=['nvpmode'])
            i.add_metric(['mode'], {'mode': self._jetson.nvpmodel.name})
            yield i

            #
            # System uptime 
            #
            g = GaugeMetricFamily('jetson_uptime', 'System uptime', labels=['uptime'])
            days = self._jetson.uptime.days
            seconds = self._jetson.uptime.seconds
            hours = seconds//3600
            minutes = (seconds//60) % 60
            g.add_metric(['days'], days)
            g.add_metric(['hours'], hours)
            g.add_metric(['minutes'], minutes)
            yield g

            #
            # CPU usage 
            #
            
            g = GaugeMetricFamily('jetson_usage_cpu', 'CPU % schedutil', labels=['cpu'])
            g.add_metric(['cpu_1'], self._jetson.cpu['cpu'][0]['user'])
            g.add_metric(['cpu_2'], self._jetson.cpu['cpu'][1]['user'])
            g.add_metric(['cpu_3'], self._jetson.cpu['cpu'][2]['user'])
            g.add_metric(['cpu_4'], self._jetson.cpu['cpu'][3]['user'])
            g.add_metric(['cpu_5'], self._jetson.cpu['cpu'][4]['user'])
            g.add_metric(['cpu_6'], self._jetson.cpu['cpu'][5]['user'])
            #g.add_metric(['cpu_7'], self._jetson.cpu['CPU7']['val'])
            #g.add_metric(['cpu_8'], self._jetson.cpu['CPU8']['val'])
            yield g

            # 
            # GPU usage
            #

            g = GaugeMetricFamily('jetson_usage_gpu', 'GPU % schedutil', labels=['gpu'])
            g.add_metric(['load'], self._jetson.gpu['gpu']['status']['load'])
            g.add_metric(['frq'], self._jetson.gpu['gpu']['freq']['cur'])
            # g.add_metric(['min_freq'], self._jetson.gpu['min_freq'])
            # g.add_metric(['max_freq'], self._jetson.gpu['max_freq'])
            yield g

            # 
            # RAM usage
            #
            g = GaugeMetricFamily('jetson_usage_ram', 'Memory usage', labels=['ram'])
            g.add_metric(['used'], self._jetson.memory['RAM']['used'])
            g.add_metric(['shared'], self._jetson.memory['RAM']['shared'])
            # g.add_metric(['total'], self._jetson.ram['tot'])
            # g.add_metric(['unit'], self._jetson.ram['unit'])
            yield g

            # 
            # Disk usage
            #
            g = GaugeMetricFamily('jetson_usage_disk', 'Disk space usage', labels=['disk'])
            g.add_metric(['used'], self._jetson.disk['used'])
            g.add_metric(['total'], self._jetson.disk['total'])
            g.add_metric(['available'], self._jetson.disk['available'])
            g.add_metric(['available_no_root'], self._jetson.disk['available_no_root'])
            yield g

            # 
            # Fan usage
            #
            g = GaugeMetricFamily('jetson_usage_fan', 'Fan usage', labels=['fan'])
            g.add_metric(['speed'], self._jetson.fan['pwmfan']['speed'][0])
            # g.add_metric(['measure'], self._jetson.fan['measure'])
            # g.add_metric(['auto'], self._jetson.fan['auto'])
            # g.add_metric(['rpm'], self._jetson.fan['rpm'])
            # g.add_metric(['mode'], self._jetson.fan['mode'])
            yield g

            # 
            # Swapfile usage
            #
            g = GaugeMetricFamily('jetson_usage_swap', 'Swapfile usage', labels=['swap'])
            g.add_metric(['used'], self._jetson.memory['SWAP']['used'])
            g.add_metric(['total'], self._jetson.memory['SWAP']['tot'])
            # g.add_metric(['unit'], self._jetson.swap['unit'])
            # g.add_metric(['cached_size'], self._jetson.swap['cached']['size'])
            # g.add_metric(['cached_unit'], self._jetson.swap['cached']['unit'])
            yield g

            # 
            # Sensor temperatures
            #
            g = GaugeMetricFamily('jetson_temperatures', 'Sensor temperatures', labels=['temperature'])
            g.add_metric(['gpu'], self._jetson.temperature['gpu']['temp'] if 'gpu' in self._jetson.temperature else 0)
            g.add_metric(['cpu'], self._jetson.temperature['cpu']['temp'] if 'cpu' in self._jetson.temperature else 0)
            
            g.add_metric(['soc0'], self._jetson.temperature['soc0']['temp'] if 'soc0' in self._jetson.temperature else 0)
            g.add_metric(['soc1'], self._jetson.temperature['soc1']['temp'] if 'soc1' in self._jetson.temperature else 0)
            g.add_metric(['soc2'], self._jetson.temperature['soc2']['temp'] if 'soc2' in self._jetson.temperature else 0)

            g.add_metric(['tj'], self._jetson.temperature['tj']['temp'] if 'tj' in self._jetson.temperature else 0)

            yield g

            # 
            # Power
            #
            print(self._jetson.power['rail'])
            g = GaugeMetricFamily('jetson_usage_power', 'Power usage', labels=['power'])

            #g.add_metric(['cv'], self._jetson.power['rail']['VDD_CPU_GPU_CV']['power'] if 'rail' in self._jetson.power['rail'] else 0)
            g.add_metric(['cpu'], self._jetson.power['rail']['VDD_CPU_GPU_CV']['power'] if 'rail' in self._jetson.power else 0)
            g.add_metric(['soc'], self._jetson.power['rail']['VDD_SOC']['power'] if 'rail' in self._jetson.power else 0)
            g.add_metric(['total'], self._jetson.power['tot']['power'] if 'tot' in self._jetson.power['rail'] else 0)

            g.add_metric(['sys5v'], self._jetson.power['tot']['volt'] if 'tot' in self._jetson.power else 0)
            g.add_metric(['total_avg'], self._jetson.power['tot']['avg'] if 'tot' in self._jetson.power else 0)
            yield g


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000, help='Metrics collector port number')

    args = parser.parse_args()

    start_http_server(args.port)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
