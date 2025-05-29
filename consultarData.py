import requests

def resolver_rompecabezas():
    print("=== RESOLVER ROMPECABEZAS ===")
    try:
        piece_id = int(input("Ingresa el ID de la pieza inicial: "))
    except ValueError:
        print("El ID debe ser un número entero.")
        return

    url = f"http://localhost:5000/assemble/full/{piece_id}"

    print(f"\nConsultando pasos desde la pieza {piece_id}...\n")
    try:
        response = requests.get(url)
        response.raise_for_status()
        pasos = response.json()

        if not pasos:
            print("No se encontraron pasos, revise las relaciones desde esta pieza.")
            return

        print("=== PASOS PARA RESOLVER ===\n")
        count = 1
        for paso in pasos:
            if "ADVERTENCIA" in paso or "NO está disponible" in paso:
                print(f"{paso}")
            else:
                print(f"{count}. {paso}")
                count += 1

    except requests.exceptions.ConnectionError:
        print("No se pudo conectar al servidor Flask. ¿Está corriendo?")
    except Exception as e:
        print("Error al consultar los pasos:", e)

if __name__ == "__main__":
    resolver_rompecabezas()