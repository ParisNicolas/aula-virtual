@echo off

REM Crea un entorno virtual en la carpeta 'venv'
python -m venv .venv
echo Entorno Virtual (.venv) creado exitosamente.


REM Activa el entorno virtual
call .venv/Scripts/activate.bat
echo Entorno Virtual Activado.

REM Instala los paquetes requeridos desde requirements.txt
echo Instalando paquetes...
echo ------
pip install -r requirements.txt


REM Crea el archivo .env
if not exist .env (
    type nul > .env
)
echo ------
echo Acuerdate de poner las variables de entorno!!!!