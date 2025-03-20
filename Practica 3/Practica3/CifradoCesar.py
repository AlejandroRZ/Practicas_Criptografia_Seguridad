def cesar(texto, desplazamientos):
    alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    texto_cifrado = ''

    for letra in texto:
        if letra.upper() in alfabeto:
            indice = (alfabeto.index(letra.upper()) + desplazamientos) % 26
            if letra.isupper():
                texto_cifrado += alfabeto[indice]
            else:
                texto_cifrado += alfabeto[indice].lower()
        else:
            texto_cifrado += letra

    return texto_cifrado


nombre_archivo = input("Ingrese el nombre del archivo de texto (incluyendo la extension .txt): ")

try:
    with open(nombre_archivo, 'r') as archivo:
        texto_original = archivo.read()
except FileNotFoundError:
    print("El archivo especificado no fue encontrado.")
    exit()


desplazamientos = int(input("Numero de desplazamientos: "))

print("\nALFABETO ORIGINAL:")
print("A,B,C,D,E,F,...Y,Z")


alfabeto_desplazado = ''.join([chr(((ord(letra) - 65 + desplazamientos) % 26) + 65) for letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'])
print("\nALFABETO CON DESPLAZAMIENTO DE", desplazamientos, "POSICIONES:")
print(alfabeto_desplazado)


texto_cifrado = cesar(texto_original, desplazamientos)


print("\nTexto cifrado:")
print(texto_cifrado)