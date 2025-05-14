import scapy.all as scapy
import time
from collections import defaultdict
import statistics

# Store packet sizes over time
traffic_history = defaultdict(list)

def analyze_packet(packet):
    """Analyze packet size and detect anomalies."""
    if packet.haslayer(scapy.IP):
        pkt_size = len(packet)
        src_ip = packet[scapy.IP].src
        current_time = int(time.time() // 60)  # Group by minute
        
        # Record packet size
        traffic_history[(src_ip, current_time)].append(pkt_size)
        
        # Analyze every 10 packets
        if len(traffic_history[(src_ip, current_time)]) >= 10:
            sizes = traffic_history[(src_ip, current_time)]
            mean = statistics.mean(sizes)
            stdev = statistics.stdev(sizes) if len(sizes) > 1 else 0
            
            # Flag anomaly if packet size deviates significantly
            latest_size = sizes[-1]
            if stdev > 0 and abs(latest_size - mean) > 3 * stdev:
                print(f"Anomaly detected from {src_ip}: Packet size {latest_size} (Mean: {mean}, StdDev: {stdev})")

def main():
    """Sniff network traffic and analyze packets."""
    print("Starting network traffic anomaly detector...")
    scapy.sniff(prn=analyze_packet, store=0)

if __name__ == "__main__":
    main()