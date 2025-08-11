#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import time
from .install import install_dependencies  # Importamos la función de install.py para reutilizarla

def setup_and_run_venv():
    """Crea o configura el entorno virtual si hay un fallo, instala dependencias y ejecuta main.py."""
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "venv")  # Ajustado para estar en modules
    os_name = platform.system()
    
    # Configurar binarios según el sistema operativo (agregado soporte para macOS)
    if os_name == "Linux" or os_name == "Darwin":  # Darwin es macOS
        python_bin = os.path.join(venv_dir, "bin", "python")
        pip_bin = os.path.join(venv_dir, "bin", "pip")
    elif os_name == "Windows":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        print(f"❌ Sistema operativo no soportado: {os_name}.")
        sys.exit(1)

    # Verificar si el entorno virtual existe; si no, crearlo
    if not os.path.exists(venv_dir):
        print(f"📁 Creando entorno virtual en {venv_dir}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print(f"✅ Entorno virtual creado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al crear el entorno virtual: {e}. Verifica que 'venv' esté disponible en tu instalación de Python.")
            sys.exit(1)

    # Actualizar pip antes de instalar dependencias
    print(f"🔄 Actualizando pip en el entorno virtual...")
    try:
        subprocess.check_call([pip_bin, "install", "--upgrade", "pip"])
        print(f"✅ Pip actualizado correctamente.")
    except subprocess.CalledProcessError:
        print(f"❌ Error al actualizar pip. Continuando con la instalación...")

    # Instalar dependencias usando la función de install.py
    if not install_dependencies(venv_dir, pip_bin):
        print(f"❌ Fallo al instalar dependencias. Saliendo...")
        sys.exit(1)

    # Verificar si ya estamos usando el Python del venv
    if os.path.normpath(sys.executable).lower().startswith(os.path.normpath(venv_dir).lower()):
        print(f"✅ Ya estamos usando el Python del entorno virtual: {sys.executable}")
        # Si se llama desde main.py, no ejecutamos main.py de nuevo para evitar bucle
        return True

    # Ejecutar main.py con el Python del entorno virtual
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "main.py")  # Ajustado para modules
    print(f"🚀 Reiniciando main.py con Python del entorno virtual: {python_bin}")
    try:
        os.execv(python_bin, [python_bin, main_path] + sys.argv[1:])
    except Exception as e:
        print(f"❌ Error al reiniciar main.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_and_run_venv()