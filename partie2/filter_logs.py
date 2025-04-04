import os
import json

def filter_logs(input_file, output_file):
    """Filter logs and create a new file with only warning and error logs"""
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier '{input_file}' est introuvable.")
        return

    try:
        # Lire le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f_in:
            logs = json.load(f_in)
            logs=logs['hits']['hits']
        # Filtrer les logs (warning et error)
        if isinstance(logs, list):
            filtered_logs = [
                log for log in logs 
                if isinstance(log, dict) and 
                log.get('log level', '').lower() in ['warning', 'error']
            ]
        else:
            print("Erreur : Le fichier JSON ne contient pas une liste de logs")
            return

        # Écrire les logs filtrés dans un nouveau fichier
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(filtered_logs, f_out, indent=2, ensure_ascii=False)
            
        print(f"Fichier filtré créé avec succès : {output_file}")
        print(f"Nombre de logs filtrés : {len(filtered_logs)}")

    except json.JSONDecodeError as e:
        print(f"Erreur : Le fichier n'est pas un JSON valide : {e}")
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