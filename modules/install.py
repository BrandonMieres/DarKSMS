#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import platform

def install_dependencies(venv_dir, pip_bin):
    """Instala las dependencias necesarias para el proyecto en un entorno virtual"""
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
        print(f"{Fore.LIGHTGREEN_EX}🔧 Instalando dependencias...{Style.RESET_ALL}")
    except ImportError:
        print("🔧 Instalando dependencias (sin colorama)...")

    # Actualizar pip en el entorno virtual
    try:
        print(f"🔄 Actualizando pip en el entorno virtual...")
        subprocess.check_call([pip_bin, "install", "--upgrade", "pip"])
        try:
            from colorama import Fore, Style
            print(f"{Fore.LIGHTGREEN_EX}✅ Pip actualizado correctamente.{Style.RESET_ALL}")
        except ImportError:
            print(f"✅ Pip actualizado correctamente.")
    except subprocess.CalledProcessError:
        try:
            from colorama import Fore, Style
            print(f"{Fore.RED}❌ Error al actualizar pip. Continuando con la instalación...{Style.RESET_ALL}")
        except ImportError:
            print(f"❌ Error al actualizar pip. Continuando con la instalación...")

    # Instalar dependencias individuales
    dependencies = ["setuptools", "colorama", "undetected_chromedriver"]
    for dep in dependencies:
        try:
            print(f"📦 Instalando {dep}...")
            subprocess.check_call([pip_bin, "install", "--no-cache-dir", dep])
            try:
                from colorama import Fore, Style
                print(f"{Fore.LIGHTGREEN_EX}✅ {dep} instalado correctamente.{Style.RESET_ALL}")
            except ImportError:
                print(f"✅ {dep} instalado correctamente.")
        except subprocess.CalledProcessError:
            try:
                from colorama import Fore, Style
                print(f"{Fore.RED}❌ Error al instalar {dep}. Verifica tu conexión o permisos.{Style.RESET_ALL}")
            except ImportError:
                print(f"❌ Error al instalar {dep}. Verifica tu conexión o permisos.")
        time.sleep(1)

    # Instalar dependencias desde requirements.txt si existe
    requirements_path = os.path.join("herramientas", "TBomb", "requirements.txt")
    if os.path.exists(requirements_path):
        try:
            print(f"📜 Encontrado requirements.txt en herramientas/TBomb. Instalando dependencias...")
            subprocess.check_call([pip_bin, "install", "--no-cache-dir", "-r", requirements_path])
            try:
                from colorama import Fore, Style
                print(f"{Fore.LIGHTGREEN_EX}✅ Dependencias de requirements.txt instaladas correctamente.{Style.RESET_ALL}")
            except ImportError:
                print(f"✅ Dependencias de requirements.txt instaladas correctamente.")
        except subprocess.CalledProcessError:
            try:
                from colorama import Fore, Style
                print(f"{Fore.RED}❌ Error al instalar dependencias de requirements.txt.{Style.RESET_ALL}")
            except ImportError:
                print(f"❌ Error al instalar dependencias de requirements.txt.")
    else:
        try:
            from colorama import Fore, Style
            print(f"{Fore.LIGHTYELLOW_EX}⚠️ No se encontró requirements.txt en herramientas/TBomb.{Style.RESET_ALL}")
        except ImportError:
            print(f"⚠️ No se encontró requirements.txt en herramientas/TBomb.")

    try:
        from colorama import Fore, Style
        print(f"{Fore.LIGHTGREEN_EX}🎉 Instalación de dependencias completada.{Style.RESET_ALL}")
    except ImportError:
        print(f"🎉 Instalación de dependencias completada.")
    time.sleep(2)
    return True

def check_and_use_venv():
    """Verifica si el entorno virtual existe y lo usa; si no, lo crea e instala dependencias"""
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "venv")
    os_name = platform.system()
    python_bin = sys.executable
    pip_bin = None

    # Configurar binarios según el sistema operativo
    if os_name == "Linux" or os_name == "Darwin":  # Agregado soporte para macOS
        python_bin = os.path.join(venv_dir, "bin", "python")
        pip_bin = os.path.join(venv_dir, "bin", "pip")
    elif os_name == "Windows":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        print(f"❌ Sistema operativo no soportado: {os_name}.")
        sys.exit(1)

    # Verificar si el entorno virtual existe
    if os.path.exists(venv_dir):
        print(f"✅ Entorno virtual encontrado en {venv_dir}.")
        # Verificar si setuptools está instalado
        try:
            subprocess.check_call([pip_bin, "show", "setuptools"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ Dependencias básicas (setuptools) ya instaladas.")
            # Evitar reinicio si ya usamos el Python del venv o estamos en depurador
            if "debugpy" in sys.argv[0] or os.path.normpath(sys.executable).lower().startswith(os.path.normpath(venv_dir).lower()):
                print(f"✅ Usando Python del entorno virtual: {sys.executable}")
                return True
            # Evitar reinicio si el script se ejecuta desde run.py (para prevenir bucles)
            if "run.py" in sys.argv[0]:
                print(f"✅ Ejecutado desde run.py, continuando sin reiniciar.")
                return True
            # Reiniciar con el Python del entorno virtual solo si es necesario
            print(f"🔄 Reiniciando con Python del entorno virtual: {python_bin}")
            time.sleep(1)
            os.execv(python_bin, [python_bin] + sys.argv)
        except subprocess.CalledProcessError:
            print(f"⚠️ Entorno virtual existe pero faltan dependencias (setuptools). Reinstalando...")
            return install_dependencies(venv_dir, pip_bin)
    else:
        print(f"📁 Creando entorno virtual en {venv_dir}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print(f"✅ Entorno virtual creado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al crear el entorno virtual: {e}.")
            print(f"💡 Asegúrate de que Python esté correctamente instalado y que tengas permisos para crear carpetas en {venv_dir}.")
            return False
        # Instalar dependencias en el entorno virtual
        return install_dependencies(venv_dir, pip_bin)