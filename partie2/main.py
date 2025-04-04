import json
import platform
import psutil
import pandas as pd
from datetime import datetime
import os
import re
from filter_logs import filter_logs



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
    filtered_logs_path = os.path.join(os.path.dirname(__file__), 'filtered_logs.json')

    # Filtrer les logs
    filter_logs(log_file_path, filtered_logs_path)

    # Lire et traiter les logs filtrés
    with open(filtered_logs_path, 'r', encoding='utf-8') as f:
        logs = json.load(f)

    # Récupérer les informations système
    system_info = get_system_info()

    # Générer le rapport Excel
    export_to_excel(logs, system_info, 'system_report.xlsx')

if __name__ == "__main__":
    main()
