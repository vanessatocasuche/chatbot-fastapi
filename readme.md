0. Instalar python 
crt + sft + p
select interpreter 
elegir version de python
1. Crear un entorno virtual
Ubícate en la raíz de tu proyecto y ejecuta:

python -m venv venv


Esto crea una carpeta venv/ con el entorno aislado.

2. Activar el entorno

Windows (cmd o PowerShell):


venv\Scripts\activate


Mac / Linux:

source venv/bin/activate

3. Instalar dependencias desde tu archivo

Ahora sí puedes ejecutar:

pip install -r requirements.txt


Esto instalará solo dentro del entorno virtual las versiones que tengas listadas.

4. Ajusta tus variables de entorno

9. Corre la aplicacion

uvicorn src.main:app --reload