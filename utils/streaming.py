import time
import pandas as pd
from datetime import datetime
import random

class ZESCODataStream:
    def __init__(self, meter_id):
        self.meter_id = meter_id
        self._running = False
    
    def start_stream(self):
        """Simulate real-time data stream"""
        self._running = True
        while self._running:
            yield self._generate_data_point()
            time.sleep(5)  # 5-second intervals
    
    def _generate_data_point(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'meter_id': self.meter_id,
            'consumption_kwh': random.uniform(0.5, 5.0),
            'voltage': random.uniform(220, 240),
            'current': random.uniform(5, 15)
        }
    
    def stop_stream(self):
        self._running = False

class StreamManager:
    def __init__(self):
        self.active_streams = {}
    
    def get_stream(self, meter_id):
        if meter_id not in self.active_streams:
            self.active_streams[meter_id] = ZESCODataStream(meter_id)
        return self.active_streams[meter_id]