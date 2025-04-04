from api_helper import GeoAPI


def main():
    print("Bienvenue dans le programme de consultation des populations des communes et départements.")

    # Demander à l'utilisateur d'entrer un code (commune ou département)
    code = input("Veuillez entrer un code (par exemple, 13 pour un département ou 13111 pour une commune) : ")

    try:
        # Convertir le code en entier
        code = int(code)
    except ValueError:
        print("Le code doit être un nombre entier. Essayez à nouveau.")
        return

    # Initialiser l'API
    geo_api = GeoAPI()

    # Obtenir la population pour le code donné
    population = geo_api.get_population(code)

    # Afficher la population
    print(f"La population correspondante est : {population}")


if __name__ == "__main__":
    main()
