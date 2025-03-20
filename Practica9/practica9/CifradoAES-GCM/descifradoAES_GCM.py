from getpass import getpass
from base64 import b64decode, b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import mysql.connector
import config

# Función para derivar la clave de cifrado utilizando scrypt
def derive_key(password, salt):
    kdf = Scrypt(salt=salt, length=32, n=16384, r=8, p=1, backend=default_backend())
    return kdf.derive(password)

# Función para buscar y descifrar los datos de un paciente en la base de datos
def buscar_paciente(nombre, password):
    try:
        # Establecer conexión con la base de datos
        connection = mysql.connector.connect(user=config.user, password=config.password, database=config.dbname)
        cursor = connection.cursor()

        # Consulta SQL para obtener los datos cifrados del paciente
        query = "SELECT diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce, diag_tag, treat_tag FROM expediente2 WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        record = cursor.fetchone()

        if record:
            # Obtener datos cifrados y metadatos
            diagnosis_ciphertext, treatment_ciphertext, password_salt, diag_nonce, treat_nonce, diag_tag, treat_tag = record

            # Imprimir los datos recuperados antes de la decodificación
            print("Datos recuperados de la base de datos:")
            print("Diagnóstico: ", diagnosis_ciphertext.decode())
            print("Tratamiento: ", treatment_ciphertext.decode())

            # Decodificar los datos desde base64
            try:
                diagnosis_ciphertext = b64decode(diagnosis_ciphertext)
                treatment_ciphertext = b64decode(treatment_ciphertext)
                password_salt = b64decode(password_salt)
                diag_nonce = b64decode(diag_nonce)
                treat_nonce = b64decode(treat_nonce)
                diag_tag = b64decode(diag_tag)
                treat_tag = b64decode(treat_tag)
            except Exception as e:
                return

            # Derivar la clave de cifrado utilizando scrypt y la sal almacenada en la base de datos
            key = derive_key(password.encode(), password_salt)

            # Descifrar el diagnóstico utilizando AES-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(diag_nonce, diag_tag), backend=default_backend())
            decryptor = cipher.decryptor()
            diagnosis = decryptor.update(diagnosis_ciphertext) + decryptor.finalize()

            # Descifrar el tratamiento utilizando AES-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(treat_nonce, treat_tag), backend=default_backend())
            decryptor = cipher.decryptor()
            treatment = decryptor.update(treatment_ciphertext) + decryptor.finalize()

            
        else:
            print("Paciente no encontrado en la base de datos.")

    except mysql.connector.Error as e:
        print("Error al buscar paciente en la base de datos:", e)

    except Exception as e:
        print("Error al descifrar los datos:", e)

    finally:
        # Cerrar la conexión con la base de datos
        if connection.is_connected():
            cursor.close()
            connection.close()

# Solicitar al usuario el nombre del paciente a buscar
nombre_paciente = input("Ingrese el nombre del paciente: ")

# Solicitar la contraseña
password = getpass("Ingrese la contraseña para descifrar los datos: ")

# Buscar y descifrar los datos del paciente
buscar_paciente(nombre_paciente, password)
