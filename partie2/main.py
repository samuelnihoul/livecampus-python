import json
import platform
import psutil
import pandas as pd
from datetime import datetime
import os
import socket
import time

def read_logs(file_path):
    """Read and process logs from JSON file"""
    with open(file_path, 'r') as f:
        logs = json.load(f)
    
    # Filter logs with warning or error level
    filtered_logs = []
    for log in logs:
        if log.get('log level', '').lower() in ['warning', 'error']:
            filtered_logs.append({
                'log level': log.get('log level', ''),
                'message': log.get('message', ''),
                'station': log.get('station', '')
            })
    
    # Sort logs to put errors first
    filtered_logs.sort(key=lambda x: x['log level'] == 'error', reverse=True)
    return filtered_logs

def get_system_info():
    """Collect system information"""
    # OS Information
    os_info = {
        'os': f"{platform.system()} {platform.release()}",
        'cpu': f"{psutil.cpu_percent()}% usage",
        'ram': f"{psutil.virtual_memory().percent}% usage ({psutil.virtual_memory().available / (1024**3):.2f} GB available)",
    }
    
    # Top 5 processes by CPU usage
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    os_info['top_processes'] = '\n'.join([f"{p['name']}: {p['cpu_percent']}%" for p in top_processes])
    
    # Environment variables
    os_info['env_vars'] = '\n'.join([f"{k}: {v}" for k, v in os.environ.items()])
    
    # Disk partitions and usage
    disk_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append(f"{partition.device}: {usage.percent}% used ({usage.free / (1024**3):.2f} GB free)")
        except PermissionError:
            continue
    os_info['disk_info'] = '\n'.join(disk_info)
    
    # Network interfaces
    interfaces = []
    for interface, addrs in psutil.net_if_addrs().items():
        interfaces.append(interface)
    os_info['network_interfaces'] = '\n'.join(interfaces)
    
    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    os_info['boot_time'] = boot_time.strftime("%H:%M:%S")
    
    return os_info

def export_to_excel(logs, system_info, output_file):
    """Export data to Excel file with two sheets"""
    # Create logs DataFrame
    logs_df = pd.DataFrame(logs)
    
    # Create system info DataFrame
    system_df = pd.DataFrame([system_info])
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        logs_df.to_excel(writer, sheet_name='logs', index=False)
        system_df.to_excel(writer, sheet_name='System status', index=False)

def main():
    # Read and process logs
    logs = read_logs('logs.json')
    
    # Get system information
    system_info = get_system_info()
    
    # Export to Excel
    export_to_excel(logs, system_info, 'system_report.xlsx')
    print("Report generated successfully!")

if __name__ == "__main__":
    main()
