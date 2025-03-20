from getpass import getpass
from base64 import b64encode

from os import urandom
from getpass import getpass
from base64 import b64encode
#from SecureString import clearmem
from Cryptodome.Protocol.KDF import PBKDF2
#from Crypto.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import mysql.connector
import config
import sys

import json
import ast

# Se obtiene la contraseña para cifrar los datos
password = getpass()

# La idea es que estos datos vengan de otro lado como parte
# de una app más completa.
name = 'John Connor'
diagnosis = bytes('Heridas por ataque de T-800', 'utf-8')
treatment = bytes('Paracetamol cada 8 hrs', 'utf-8')

# Datos de entrada
passwd = b'p@$Sw0rD~7'
salt1 = b'aa1f2d3f4d23ac44e9c5a6c3d8f9ee8c'

# Utilizamos scrypt para derivar una clave
kdf_scrypt = Scrypt(salt=salt1, length=32, n=16384, r=8, p=1, backend=default_backend())
key= kdf_scrypt.derive(passwd)

print("Derived key using scrypt:", key.hex())

# Se generan nonces únicos para GCM
diagnosis_nonce = urandom(12)
treatment_nonce = urandom(12)

# Se cifran los datos utilizando AES en modo GCM
cipher = Cipher(algorithms.AES(key), modes.GCM(diagnosis_nonce), backend=default_backend())
encryptor = cipher.encryptor()
diagnosis_ciphertext = encryptor.update(diagnosis) + encryptor.finalize()
diagnosis_tag = encryptor.tag

cipher = Cipher(algorithms.AES(key), modes.GCM(treatment_nonce), backend=default_backend())
encryptor = cipher.encryptor()
treatment_ciphertext = encryptor.update(treatment) + encryptor.finalize()
treatment_tag = encryptor.tag


# Se codifica en base64 tanto la salt como el criptograma y el tag para guardarlos en la base de datos
salt = b64encode(salt1)
diagnosis_ciphertext = b64encode(diagnosis_ciphertext)
treatment_ciphertext = b64encode(treatment_ciphertext)
diagnosis_nonce = b64encode(diagnosis_nonce)
treatment_nonce = b64encode(treatment_nonce)
diagnosis_tag = b64encode(diagnosis_tag)
treatment_tag = b64encode(treatment_tag)

# Print de la información cifrada y codificada
print('Diagnosis:', diagnosis)
print('Medical treatment:', treatment)
print('PasswordSalt:', salt)
print('AES encryption key:', key.hex())
print(f"Nonces:- diagnosis:{diagnosis_nonce.decode()}; treatment:{treatment_nonce.decode()}")
print('Diagnosis encrypted:', diagnosis_ciphertext)
print('Treatment encrypted:', treatment_ciphertext)

# Definimos una función para guardar la información en la base de dato
# Definir la función para leer los registros del archivo
def leer_registros_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as file:
            content = file.read()
            registros = eval(content)  # Utilizamos eval para interpretar el contenido como un diccionario
            return registros
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None

# Definir la función para procesar y guardar los registros en la base de datos
def procesar_y_guardar_registros(registros):
    if registros:
        for key, value in registros.items():
            try:
                # Establecer la conexión a la base de datos
                mariadb = mysql.connector.connect(user=config.user, password=config.password, database=config.dbname)
                cursor = mariadb.cursor()
                
                query = "INSERT INTO expediente2 (nombre, diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (value['name'], value['diagnosis'], value['treatment'], salt, diagnosis_nonce.decode(), treatment_nonce.decode() ) )

                                # Guardar los cambios en la base de datos
                mariadb.commit()
                print("Registro guardado exitosamente en la base de datos.")

            except Exception as e:
                print("Error al guardar el registro en la base de datos:", e)
                # En caso de error, revertir los cambios
                mariadb.rollback()

            finally:
                # Cerrar la conexión a la base de datos
                mariadb.close()

# Leer los registros del archivo
registros = leer_registros_desde_archivo("diagnosticos_tratamientos.txt")

# Procesar y guardar los registros en la base de datos
procesar_y_guardar_registros(registros)

del password
del key
