import requests
import os
import platforms

def descargar_archivo_desde_url(url, nombre_archivo):
    sistema_operativo = platforms.system()
    print(f"Sistema Operativo: {sistema_operativo}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(nombre_archivo, 'wb') as file:
                file.write(response.content)
            print(f"¡Descarga de '{url}' exitosa! Archivo guardado como '{nombre_archivo}'")
        else:
            print(f"Error al descargar el archivo de '{url}'. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")

print("Conectado")
print(10)
user,passw = decript("176039357-252/60751-60752-60753-60754-60755-60756-60757-60758-60759-60760-60761-60762/2/aHR0cHM6Ly9yZXZnYWNldGFlc3R1ZGlhbnRpbC5zbGQuY3UvaW5kZXgucGhwL2dtZQ@-dGVjaGRldjM#-QEExYTJhM21v-MjUy")