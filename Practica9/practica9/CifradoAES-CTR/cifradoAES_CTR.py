# importing the module 
from getpass import getpass
from base64 import b64encode
from SecureString import clearmem
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
import MySQLdb, config, sys, ast
  
# reading the data from the file 
password = getpass()
with open('diagnosticos_tratamientos.txt') as f: 
    data = f.read()
    datos = ast.literal_eval(data)    
    for indice in range(len(datos)):
        name = datos[indice]['name']
        diagnosis = datos[indice]['diagnosis']
        treatment = datos[indice]['treatment']        

        # El algoritmo de derivación de llaves PBKDF2 necesita una salt,
        # por lo que generamos una secuencia pseudoaleatoria de 16 bytes. 
        passwordSalt = get_random_bytes(16)
        
        # En esta práctica emplearemos AES-256, por lo que necesitamos
        # que el algoritmo de derivación de llaves PBKDF2 nos proporcione
        # una llave 256 bits (32 bytes).
        key = PBKDF2(password, passwordSalt, 32, count=1000000, hmac_hash_module=SHA512)
        
        # Genera nonces únicos para cada cifrado
        diagnosis_nonce = get_random_bytes(8)
        treatment_nonce = get_random_bytes(8)
        diag_aes = AES.new(key, AES.MODE_CTR, nonce=diagnosis_nonce)
        treat_aes = AES.new(key, AES.MODE_CTR, nonce=treatment_nonce)
        
        # Cifra los campos considerados sensibles
        diagnosis_ciphertext = diag_aes.encrypt(bytes(diagnosis, 'utf-8'))
        treatment_ciphertext = treat_aes.encrypt(bytes(treatment, 'utf-8'))
        
        # Codifica en base 64 tanto la passwordSalt como el criptograma
        passwordSalt_enc = b64encode(passwordSalt)
        diagnosis_ciphertext_enc = b64encode(diagnosis_ciphertext)
        treatment_ciphertext_enc = b64encode(treatment_ciphertext)
        diagnosis_nonce_enc = b64encode(diagnosis_nonce)
        treatment_nonce_enc = b64encode(treatment_nonce)
     
        mydb = None
        # Guardar los datos en una base de datos relacional
        try:
            # Leemos las credenciales para la conexión del archivo config.py
            # El cifrado de la conexión se realizará en otra práctica
            mydb = MySQLdb.connect(user=config.user, password=config.password, database=config.dbname)
            cursor = mydb.cursor()   
        
            # Ejecutar la consulta SQL para insertar el paciente en la base de datos
            insert_query = """ INSERT INTO expediente (nombre, diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce) 
                                VALUES (%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (name, diagnosis_ciphertext_enc, treatment_ciphertext_enc, passwordSalt_enc, diagnosis_nonce_enc, treatment_nonce_enc)
            cursor.execute(insert_query, record_to_insert)

            mydb.commit()
            print("Records inserted successfully")

        except Exception as err:
            print(f"\nSomething went wrong: {err}")
            sys.exit()

        finally:
            if mydb:
                cursor.close()
                mydb.close()
                print("DBMS connection is closed")


        # Sobrescribir el contenido de las variables para evitar que se
        # puedan obtener los datos a través de un volcado de memoria RAM
        clearmem(key)        
        clearmem(diagnosis)
        clearmem(treatment) 

    clearmem(password)

