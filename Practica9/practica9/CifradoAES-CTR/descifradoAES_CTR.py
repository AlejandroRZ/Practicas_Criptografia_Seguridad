import MySQLdb
import config
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
import base64
from base64 import b64decode
from Cryptodome.Hash import SHA512
from getpass import getpass

def obtener_datos_paciente(nombre):
    try:
        # Conectar a la base de datos
        mydb = MySQLdb.connect(user=config.user, password=config.password, database=config.dbname)
        cursor = mydb.cursor()

        # Ejecutar consulta SQL para obtener los datos del paciente
        consulta_sql = """SELECT diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce FROM expediente WHERE nombre = %s"""
        
        cursor.execute(consulta_sql, (nombre,))
        datos_paciente = cursor.fetchone() #Recuperamos el primer resultado de la consulta

        #Si logramos obtener de forma exitosa, los datos del paciente 
        #en cuestion
        if datos_paciente:
            
            diagnostico_base64 = datos_paciente[0].encode()
            tratamiento_base64 = datos_paciente[1].encode()
            passwordSalt_base64 = datos_paciente[2].encode()
            diag_nonce_base64 = datos_paciente[3].encode()
            trat_nonce_base64 = datos_paciente[4].encode()
            
        
            #Ejecutaremos el proceso inverso de encrypt
            #Primero decodificamos de base 64
            diagnostico = base64.b64decode(diagnostico_base64)
            tratamiento = base64.b64decode(tratamiento_base64)
            passwordSalt = base64.b64decode(passwordSalt_base64)
            diag_nonce = base64.b64decode(diag_nonce_base64)
            trat_nonce = base64.b64decode(trat_nonce_base64)
            
            #Utilizamos la misma password dada por el usuario en 
            #CifradoAES_CTR.py
            password = getpass()
            key = PBKDF2(password, passwordSalt, 32, count=1000000, hmac_hash_module=SHA512)
            
            # Descifrar los datos utilizando AES
            diag_aes = AES.new(key, AES.MODE_CTR, nonce=diag_nonce)
            treat_aes = AES.new(key, AES.MODE_CTR, nonce=trat_nonce)
           
            diag_decifrado = diag_aes.decrypt(diagnostico)
            diag_decifrado_texto = diag_decifrado.decode('utf-8')
            trat_decifrado = treat_aes.decrypt(tratamiento)
            trat_decifrado_texto = trat_decifrado.decode('utf-8')
            
            return diag_decifrado_texto, trat_decifrado_texto
        else:
            print(f"\nNo hay ningun paciente con nombre:{nombre} en la base de datos. Intenta de  nuevo.")
            return None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None

    finally:
        if mydb:
            #Cerramos el cursor y la conexion a la base de datos 
            cursor.close()
            mydb.close()
            
            

def main():
    nombre_paciente = input("Ingrese el nombre del paciente: ")

    diagnostico, tratamiento = obtener_datos_paciente(nombre_paciente)
    print("\n**Nombre del paciente: ",nombre_paciente)
    print("**Diagnóstico descifrado:", diagnostico)
    print("**Tratamiento descifrado:", tratamiento)

if __name__ == "__main__":
    main()

