import json
import platform
import psutil
import pandas as pd
from datetime import datetime
import os
import re

def parse_log_line(line):
    """Parse a single log line and extract relevant information"""
    pattern = r'\[(.*?)\] \[(.*?)\] (.*?) - (.*)'
    match = re.match(pattern, line)

    if match:
        timestamp, level, station, message = match.groups()
        return {
            'log level': level.lower(),
            'message': message.strip(),
            'station': station.strip()
        }
    return None

def read_logs(file_path):
    """Read and process logs from text file"""
    if not os.path.exists(file_path):
        print(f" Erreur : Le fichier '{file_path}' est introuvable.")
        return []

    logs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                log_entry = parse_log_line(line)
                if log_entry:
                    logs.append(log_entry)

        # Filtrer uniquement les warnings et erreurs
        filtered_logs = [log for log in logs if log['log level'] in ['warning', 'error']]

        # Trier en mettant les erreurs en premier
        filtered_logs.sort(key=lambda x: x['log level'] == 'error', reverse=True)
        return filtered_logs

    except Exception as e:
        print(f" Erreur lors de la lecture du fichier : {e}")
        return []

def get_system_info():
    """Collect system information"""
    try:
        os_info = {
            'os': f"{platform.system()} {platform.release()}",
            'cpu': f"{psutil.cpu_percent()}% usage",
            'ram': f"{psutil.virtual_memory().percent}% ({psutil.virtual_memory().available / (1024**3):.2f} GB free)",
        }

        # Top 5 processus par utilisation CPU
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        os_info['top_processes'] = '\n'.join([f"{p['name']}: {p['cpu_percent']}%" for p in top_processes])

        # Variables d'environnement
        os_info['env_vars'] = '\n'.join([f"{k}: {v}" for k, v in os.environ.items()])

        # Infos disque
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(f"{partition.device}: {usage.percent}% used ({usage.free / (1024**3):.2f} GB free)")
            except PermissionError:
                continue
        os_info['disk_info'] = '\n'.join(disk_info)

        # Interfaces réseau
        interfaces = [interface for interface in psutil.net_if_addrs()]
        os_info['network_interfaces'] = ', '.join(interfaces)

        # Temps de démarrage du système
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        os_info['boot_time'] = boot_time.strftime("%H:%M:%S")

        return os_info

    except Exception as e:
        print(f" Erreur lors de la collecte des informations système : {e}")
        return {}

def export_to_excel(logs, system_info, output_file):
    """Export data to Excel file with two sheets"""
    try:
        logs_df = pd.DataFrame(logs)
        system_df = pd.DataFrame([system_info])

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            logs_df.to_excel(writer, sheet_name='Logs', index=False)
            system_df.to_excel(writer, sheet_name='System Status', index=False)

        print(f" Rapport généré avec succès : {output_file}")

    except Exception as e:
        print(f" Erreur lors de l'exportation du fichier Excel : {e}")

def main():
    # Définir le chemin du fichier log
    log_file_path = os.path.join(os.path.dirname(__file__), 'logs.json')

    # Lire et traiter les logs
    logs = read_logs(log_file_path)

    # Récupérer les informations système
    system_info = get_system_info()

    # Générer le rapport Excel
    export_to_excel(logs, system_info, 'system_report.xlsx')

if __name__ == "__main__":
    main()
