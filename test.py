hola: str = "Jovany"


def prueba_hola():
    global hola
    print(f"este es el contenido de 'hola' {hola}")
    hola = "Jovany2"
    print(f"este es el nuevo contenido de 'hola' {hola}")


if __name__ == "__main__":
    prueba_hola()
