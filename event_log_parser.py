import win32evtlog
import xml.etree.ElementTree as ET
import csv
from datetime import datetime

def parse_event_logs(log_type="Security", output_file="event_logs.csv"):
    """Parse Windows event logs and save to CSV."""
    hand = win32evtlog.OpenEventLog(None, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = []
    
    while True:
        records = win32evtlog.ReadEventLog(hand, flags, 0)
        if not records:
            break
        for record in records:
            event = {
                "EventID": record.EventID & 0xFFFF,
                "TimeGenerated": record.TimeGenerated.Format(),
                "SourceName": record.SourceName,
                "Description": ""
            }
            if record.StringInserts:
                event["Description"] = " ".join(record.StringInserts)
            events.append(event)
    
    win32evtlog.CloseEventLog(hand)
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["EventID", "TimeGenerated", "SourceName", "Description"])
        writer.writeheader()
        writer.writerows(events)
    
    print(f"Parsed {len(events)} events to {output_file}")

if __name__ == "__main__":
    parse_event_logs()