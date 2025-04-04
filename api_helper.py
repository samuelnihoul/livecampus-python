import requests

class GeoAPI:
    def __init__(self):
        # URL de base de l'API
        self.base_url = "https://geo.api.gouv.fr"

    def get_population(self, code):
        """
        Récupère la population en fonction du code de la commune ou du département.

        :param code: Le code INSEE ou le code département/commune
        :return: La population de la commune ou du département
        """
        code_str = str(code)

        # Vérifie si le code est pour une commune (5 chiffres)
        if len(code_str) == 5:
            url = f"{self.base_url}/communes/{code}?fields=population"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'population' in data:
                    return data['population']
                else:
                    return "Aucune donnée disponible pour ce code."
            else:
                return f"Erreur {response.status_code}: Impossible de récupérer les données."

        # Vérifie si le code est pour un département (2 ou 3 chiffres)
        elif len(code_str) in [2, 3]:
            # Récupère toutes les communes du département et additionne les populations
            url = f"{self.base_url}/departements/{code}/communes?fields=population"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    total_population = sum(commune.get('population', 0) for commune in data)
                    return total_population
                else:
                    return "Aucune donnée disponible pour ce code."
            else:
                return f"Erreur {response.status_code}: Impossible de récupérer les données."

        else:
            return "Code invalide. Veuillez entrer un code valide."
