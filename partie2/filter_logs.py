import os
import re

def parse_log_line(line):
    """Parse a single log line and extract relevant information"""
    pattern = r'\[(.*?)\] \[(.*?)\] (.*?) - (.*)'
    match = re.match(pattern, line)
    
    if match:
        timestamp, level, station, message = match.groups()
        return {
            'line': line.strip(),
            'level': level.lower()
        }
    return None

def filter_logs(input_file, output_file):
    """Filter logs and create a new file with only warning and error logs"""
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier '{input_file}' est introuvable.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(output_file, 'w', encoding='utf-8') as f_out:
            
            for line in f_in:
                log_entry = parse_log_line(line)
                if log_entry and log_entry['level'] in ['warning', 'error']:
                    f_out.write(log_entry['line'] + '\n')
            
        print(f"Fichier filtré créé avec succès : {output_file}")
        print(f"Les logs de niveau 'warning' et 'error' ont été extraits.")

    except Exception as e:
        print(f"Erreur lors du traitement des fichiers : {e}")

def main():
    # Définir les chemins des fichiers
    input_file = os.path.join(os.path.dirname(__file__), 'logs.json')
    output_file = os.path.join(os.path.dirname(__file__), 'filtered_logs.json')
    
    # Filtrer les logs
    filter_logs(input_file, output_file)

if __name__ == "__main__":
    main() 