def descifrar_cesar(texto_cifrado, desplazamiento):
    alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    texto_descifrado_derecha = ''
    texto_descifrado_izquierda = ''
    
    for letra in texto_cifrado:
        if letra.isalpha():
            mayuscula = letra.isupper()
            letra = letra.upper()
            if letra in alfabeto:
                indice_derecha = (alfabeto.index(letra) - desplazamiento) % 26
                indice_izquierda = (alfabeto.index(letra) + desplazamiento) % 26
                
                if not mayuscula:
                    texto_descifrado_derecha += alfabeto[indice_derecha].lower()
                    texto_descifrado_izquierda += alfabeto[indice_izquierda].lower()
                else:
                    texto_descifrado_derecha += alfabeto[indice_derecha]
                    texto_descifrado_izquierda += alfabeto[indice_izquierda]
            else:
                texto_descifrado_derecha += letra
                texto_descifrado_izquierda += letra
        else:
            texto_descifrado_derecha += letra
            texto_descifrado_izquierda += letra
    
    return texto_descifrado_derecha, texto_descifrado_izquierda

texto_cifrado = "junpan"
desplazamiento = 9

texto_descifrado_derecha, texto_descifrado_izquierda = descifrar_cesar(texto_cifrado, desplazamiento)

print("Texto descifrado hacia la derecha:", texto_descifrado_derecha)
print("Texto descifrado hacia la izquierda:", texto_descifrado_izquierda)
