#!/usr/bin/python3

import os
import platform
import subprocess
import time
import sys
from colorama import Fore, Style, init

# Inicializar colorama
init(autoreset=True)

# Colores básicos ANSI
negro = '\033[30m'
rojo = '\033[31m'
verde = '\033[32m'
amarillo = '\033[33m'
azul = '\033[34m'
rosado = '\033[35m'
calipso = '\033[36m'
blanco = '\033[37m'
cierre = '\033[39m'

def clear_console():
    """Limpiar la consola de manera multiplataforma"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def show_separator():
    """Muestra un separador visual elegante"""
    print(f"{Fore.RED}{'═'*70}{Style.RESET_ALL}")

def show_mini_separator():
    """Muestra un separador pequeño"""
    print(f"{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")

def show_tools_header():
    """Muestra el encabezado de herramientas adicionales"""
    header = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                                  ║
{Fore.RED}║        {Fore.LIGHTCYAN_EX}🛠️  HERRAMIENTAS ADICIONALES AVANZADAS  🛠️{Fore.RED}                  ║
{Fore.RED}║                  {Fore.YELLOW}Sistema de Instalación Automática{Fore.RED}               ║
{Fore.RED}║                                                                  ║
{Fore.RED}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(header)

def show_status_message(message, status_type="info"):
    """Muestra mensajes con formato consistente"""
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "error": "❌",
        "warning": "⚠️",
        "loading": "🔄",
        "install": "📦",
        "execute": "🚀",
        "venv": "🐍"
    }
    
    colors = {
        "info": Fore.LIGHTCYAN_EX,
        "success": Fore.LIGHTGREEN_EX,
        "error": Fore.LIGHTRED_EX, 
        "warning": Fore.LIGHTYELLOW_EX,
        "loading": Fore.LIGHTBLUE_EX,
        "install": Fore.LIGHTMAGENTA_EX,
        "execute": Fore.LIGHTGREEN_EX,
        "venv": Fore.LIGHTBLUE_EX
    }
    
    icon = icons.get(status_type, "•")
    color = colors.get(status_type, Fore.WHITE)
    
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def get_app_venv_paths():
    """Obtiene las rutas del entorno virtual de la aplicación principal"""
    # El directorio base es donde está main.py (un nivel arriba de modules)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_dir = os.path.normpath(os.path.join(base_dir, 'venv'))
    
    os_name = platform.system()
    if os_name in ["Linux", "Darwin"]:  # Linux o macOS
        python_bin = os.path.join(venv_dir, "bin", "python")
        pip_bin = os.path.join(venv_dir, "bin", "pip")
    else:  # Windows
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    
    return venv_dir, python_bin, pip_bin

def verify_app_venv():
    """Verifica que el entorno virtual de la aplicación esté disponible y funcional"""
    venv_dir, python_bin, pip_bin = get_app_venv_paths()
    
    show_status_message(f"Verificando entorno virtual: {venv_dir}", "venv")
    
    # Verificar existencia del directorio venv
    if not os.path.exists(venv_dir):
        show_status_message("Entorno virtual no encontrado", "error")
        return False, None, None
    
    # Verificar existencia de Python
    if not os.path.exists(python_bin):
        show_status_message(f"Python no encontrado en venv: {python_bin}", "error")
        return False, None, None
    
    # Verificar existencia de pip
    if not os.path.exists(pip_bin):
        show_status_message(f"Pip no encontrado en venv: {pip_bin}", "error")
        return False, None, None
    
    # Probar funcionalidad de Python
    try:
        result = subprocess.run([python_bin, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            python_version = result.stdout.strip()
            show_status_message(f"Python del venv funcional: {python_version}", "success")
        else:
            show_status_message("Error al verificar Python del venv", "error")
            return False, None, None
    except Exception as e:
        show_status_message(f"Error probando Python del venv: {e}", "error")
        return False, None, None
    
    # Probar funcionalidad de pip
    try:
        result = subprocess.run([pip_bin, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            pip_version = result.stdout.strip()
            show_status_message(f"Pip del venv funcional: {pip_version}", "success")
        else:
            show_status_message("Error al verificar pip del venv", "error")
            return False, None, None
    except Exception as e:
        show_status_message(f"Error probando pip del venv: {e}", "error")
        return False, None, None
    
    show_status_message("Entorno virtual verificado correctamente", "success")
    return True, python_bin, pip_bin

def is_running_in_app_venv():
    """Verifica si estamos ejecutando desde el entorno virtual de la aplicación"""
    venv_dir, python_bin, _ = get_app_venv_paths()
    current_python = os.path.normpath(os.path.abspath(sys.executable))
    expected_python = os.path.normpath(os.path.abspath(python_bin))
    
    running_in_venv = current_python == expected_python
    
    if running_in_venv:
        show_status_message("Ejecutándose desde el entorno virtual de la aplicación", "venv")
    else:
        show_status_message(f"No ejecutándose desde venv. Actual: {current_python}", "warning")
        show_status_message(f"Esperado: {expected_python}", "info")
    
    return running_in_venv

def install_with_app_venv(pip_bin, package_or_requirements, is_requirements_file=False, timeout=120, retries=2):
    """Instala paquetes usando específicamente el pip del entorno virtual de la aplicación"""
    package_name = os.path.basename(package_or_requirements) if is_requirements_file else package_or_requirements
    
    for attempt in range(retries):
        try:
            show_status_message(f"Intento {attempt + 1}/{retries} para instalar {package_name} (venv)", "loading")
            
            # Construir comando
            if is_requirements_file:
                if not os.path.exists(package_or_requirements):
                    show_status_message(f"Archivo requirements no encontrado: {package_or_requirements}", "error")
                    return False
                cmd = [pip_bin, "install", "-r", package_or_requirements, "--no-cache-dir"]
            else:
                cmd = [pip_bin, "install", package_or_requirements, "--no-cache-dir"]
            
            show_status_message(f"Ejecutando: {' '.join(cmd)}", "info")
            
            # Ejecutar comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                show_status_message(f"{package_name} instalado exitosamente en venv", "success")
                return True
            else:
                error_msg = result.stderr.strip()[:200] if result.stderr else "Error desconocido"
                show_status_message(f"Error instalando {package_name}: {error_msg}", "error")
                
                if attempt < retries - 1:
                    show_status_message("Reintentando en 2 segundos...", "loading")
                    time.sleep(2)
                continue
                
        except subprocess.TimeoutExpired:
            show_status_message(f"Timeout instalando {package_name}", "error")
            if attempt < retries - 1:
                time.sleep(2)
            continue
        except Exception as e:
            show_status_message(f"Error inesperado instalando {package_name}: {e}", "error")
            if attempt < retries - 1:
                time.sleep(2)
            continue
    
    show_status_message(f"No se pudo instalar {package_name} en el venv tras {retries} intentos", "error")
    return False

def install_with_fallback_methods(requirements_path, tool_name):
    """Instala dependencias usando métodos de fallback cuando el venv no está disponible"""
    show_status_message(f"Usando métodos de fallback para {tool_name}", "warning")
    
    # Método 1: pip con --user
    show_status_message("Probando instalación con --user", "loading")
    try:
        python_cmd = "python" if platform.system() == "Windows" else "python3"
        cmd = [python_cmd, "-m", "pip", "install", "--user", "-r", requirements_path, "--no-cache-dir"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            show_status_message(f"Dependencias de {tool_name} instaladas con --user", "success")
            return True
    except Exception as e:
        show_status_message(f"Error con --user: {e}", "warning")
    
    # Método 2: pip normal del sistema (último recurso)
    if platform.system() == "Linux":
        # En sistemas como Kali con PEP 668, preguntar al usuario
        show_status_message("Sistema Linux detectado - verificando restricciones PEP 668", "info")
        try:
            response = input(f"{Fore.LIGHTYELLOW_EX}⚠️  ¿Instalar en el sistema global con --break-system-packages? (s/n): {Style.RESET_ALL}").strip().lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                show_status_message("Instalando en sistema global (PEP 668 override)", "warning")
                python_cmd = "python3"
                cmd = [python_cmd, "-m", "pip", "install", "--break-system-packages", "-r", requirements_path, "--no-cache-dir"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    show_status_message(f"Dependencias de {tool_name} instaladas en sistema global", "success")
                    return True
            else:
                show_status_message("Instalación en sistema global cancelada por el usuario", "info")
        except Exception as e:
            show_status_message(f"Error con instalación global: {e}", "error")
    else:
        # Windows o macOS - intentar instalación normal
        show_status_message("Probando instalación normal del sistema", "loading")
        try:
            python_cmd = "python" if platform.system() == "Windows" else "python3"
            cmd = [python_cmd, "-m", "pip", "install", "-r", requirements_path, "--no-cache-dir"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                show_status_message(f"Dependencias de {tool_name} instaladas en sistema", "success")
                return True
        except Exception as e:
            show_status_message(f"Error con instalación del sistema: {e}", "error")
    
    return False

def install_dependencies_smart(requirements_path, tool_name):
    """
    Instala dependencias con la siguiente prioridad:
    1. Entorno virtual de la aplicación (preferido)
    2. Instalación con --user
    3. Sistema global (último recurso, con confirmación)
    """
    if not os.path.exists(requirements_path):
        show_status_message(f"No se encontró requirements.txt para {tool_name}", "warning")
        return True  # No es un error crítico si no hay requirements
    
    show_status_message(f"Instalando dependencias para {tool_name}...", "install")
    
    # PRIORIDAD 1: Usar el entorno virtual de la aplicación
    venv_available, python_bin, pip_bin = verify_app_venv()
    
    if venv_available:
        show_status_message(f"Usando entorno virtual de la aplicación para {tool_name}", "venv")
        if install_with_app_venv(pip_bin, requirements_path, is_requirements_file=True):
            return True
        else:
            show_status_message("Fallo al instalar en venv, probando métodos alternativos...", "warning")
    else:
        show_status_message("Entorno virtual no disponible, usando métodos alternativos", "warning")
    
    # PRIORIDAD 2-3: Métodos de fallback
    return install_with_fallback_methods(requirements_path, tool_name)

def create_temp_venv_for_tool(tool_dir, tool_name):
    """Crea un entorno virtual temporal específico para una herramienta"""
    show_status_message(f"Creando entorno virtual temporal para {tool_name}...", "loading")
    
    temp_venv_dir = os.path.join(tool_dir, f"venv_{tool_name.lower()}")
    
    try:
        # Crear venv temporal
        python_cmd = "python" if platform.system() == "Windows" else "python3"
        subprocess.run([python_cmd, "-m", "venv", temp_venv_dir], check=True, timeout=60)
        
        # Obtener rutas del venv temporal
        os_name = platform.system()
        if os_name in ["Linux", "Darwin"]:
            temp_python = os.path.join(temp_venv_dir, "bin", "python")
            temp_pip = os.path.join(temp_venv_dir, "bin", "pip")
        else:
            temp_python = os.path.join(temp_venv_dir, "Scripts", "python.exe")
            temp_pip = os.path.join(temp_venv_dir, "Scripts", "pip.exe")
        
        # Actualizar pip
        subprocess.run([temp_pip, "install", "--upgrade", "pip"], check=True, timeout=60)
        
        show_status_message(f"Venv temporal creado para {tool_name}: {temp_venv_dir}", "success")
        return temp_venv_dir, temp_python, temp_pip
        
    except Exception as e:
        show_status_message(f"Error creando venv temporal para {tool_name}: {e}", "error")
        return None, None, None

def install_additional_tools():
    """Instala herramientas adicionales (TBomb y SETSMS) en la carpeta herramientas"""
    clear_console()
    show_tools_header()
    show_separator()
    
    show_status_message("Iniciando instalación de herramientas adicionales...", "install")
    
    # Verificar estado del entorno virtual de la aplicación
    venv_available, venv_python, venv_pip = verify_app_venv()
    running_in_venv = is_running_in_app_venv()
    
    if venv_available and running_in_venv:
        show_status_message("🎯 Configuración óptima: ejecutándose desde venv de la aplicación", "success")
    elif venv_available:
        show_status_message("⚡ Venv disponible pero no ejecutándose desde él", "warning")
    else:
        show_status_message("🔧 Venv no disponible, usando métodos alternativos", "warning")
    
    print()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio SMS
    tools_dir = os.path.normpath(os.path.join(base_dir, 'herramientas'))
    
    # Crear la carpeta herramientas si no existe
    if not os.path.exists(tools_dir):
        show_status_message(f"Creando directorio: {tools_dir}", "loading")
        os.makedirs(tools_dir)
        show_status_message("Directorio de herramientas creado exitosamente", "success")
    else:
        show_status_message("Directorio de herramientas ya existe", "info")
    
    print()
    show_mini_separator()
    
    # Detectar comando de Python según el sistema operativo
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    
    # Lista de herramientas a instalar
    tools = [
        {
            'name': 'TBomb',
            'repo_url': 'https://github.com/TheSpeedX/TBomb.git',
            'run_cmd': f"{python_cmd} bomber.py",
            'main_file': 'bomber.py',
            'icon': '💣',
            'description': 'Herramienta de bombardeo SMS/Llamadas',
            'dir': os.path.normpath(os.path.join(tools_dir, 'TBomb'))
        },
        {
            'name': 'SETSMS',
            'repo_url': 'https://github.com/Darkmux/SETSMS.git',
            'run_cmd': 'bash SETSMS.sh',
            'main_file': os.path.join('SETSMS', 'SETSMS.sh'),
            'icon': '📱',
            'description': 'Sistema automático de envío SMS',
            'dir': tools_dir
        }
    ]
    
    for i, tool in enumerate(tools, 1):
        tool_name = tool['name']
        repo_url = tool['repo_url']
        tool_dir = os.path.normpath(tool['dir'])
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}┌─ {tool['icon']} INSTALANDO {tool_name.upper()} ({i}/{len(tools)})─────────────────────┐{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}│ {Fore.WHITE}{tool['description']:<45} {Fore.LIGHTMAGENTA_EX}  │{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}└{'─'*49}┘{Style.RESET_ALL}")
        
        try:
            # Clonar el repositorio si no existe
            if not os.path.exists(tool_dir):
                show_status_message(f"Clonando {tool_name} desde repositorio...", "loading")
                subprocess.run(['git', 'clone', repo_url, tool_dir], check=True)
                show_status_message(f"{tool_name} clonado exitosamente", "success")
            else:
                show_status_message(f"{tool_name} ya está disponible en el sistema", "info")
            
            # Cambiar al directorio de la herramienta
            original_dir = os.getcwd()
            os.chdir(tool_dir)
            
            # Instalar dependencias usando el método inteligente
            requirements_path = 'requirements.txt'
            if os.path.exists(requirements_path):
                show_status_message(f"Procesando dependencias de {tool_name}...", "loading")
                if not install_dependencies_smart(requirements_path, tool_name):
                    show_status_message(f"⚠️ Advertencia: No se pudieron instalar todas las dependencias de {tool_name}", "warning")
                    show_status_message("La herramienta podría no funcionar correctamente", "warning")
                else:
                    show_status_message(f"Dependencias de {tool_name} instaladas correctamente", "success")
            else:
                show_status_message(f"No se encontró requirements.txt para {tool_name}", "info")
            
            # Configurar permisos (solo necesario en sistemas Unix-like)
            if platform.system() != 'Windows':
                show_status_message(f"Configurando permisos para {tool_name}...", "loading")
                script_file = tool['main_file']
                if os.path.exists(script_file):
                    subprocess.run(['chmod', '+x', script_file], check=True)
                    show_status_message(f"Permisos configurados para {script_file}", "success")
                else:
                    show_status_message(f"Archivo principal {script_file} no encontrado", "warning")
            
            print(f"\n{Fore.LIGHTGREEN_EX}╔═══ ✅ {tool_name.upper()} INSTALADO CORRECTAMENTE ═════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}📍 Ubicación: {tool_dir:<35}                           {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}🚀 Comando: {tool['run_cmd']:<37}                                 {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}💡 Uso: cd {tool_dir} && {tool['run_cmd']:<20}{Fore.LIGHTGREEN_EX}      ║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}╚{'═'*83}╝{Style.RESET_ALL}")
            
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ❌ ERROR EN INSTALACIÓN ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Herramienta: {tool_name:<18} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Error: {str(e):<24} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*33}╝{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ❌ ERROR INESPERADO ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Herramienta: {tool_name:<15} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Error: {str(e):<21} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*30}╝{Style.RESET_ALL}")
        finally:
            # Volver al directorio principal (modules)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        if i < len(tools):
            print(f"\n{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTGREEN_EX}╔══════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.LIGHTGREEN_EX}║                                                                  ║")
    print(f"{Fore.LIGHTGREEN_EX}║        {Fore.WHITE}🎉 INSTALACIÓN DE HERRAMIENTAS COMPLETADA 🎉{Fore.LIGHTGREEN_EX}              ║")
    print(f"{Fore.LIGHTGREEN_EX}║                                                                  ║")
    print(f"{Fore.LIGHTGREEN_EX}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    # Mostrar información sobre el entorno usado
    if venv_available:
        print(f"\n{Fore.LIGHTBLUE_EX}╔═══ 🐍 INFORMACIÓN DEL ENTORNO ════╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}✅ Entorno virtual disponible     {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}🎯 Dependencias en venv de app    {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}📦 Instalación optimizada         {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLUE_EX}╚{'═'*35}╝{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.LIGHTYELLOW_EX}╔═══ ⚠️  INFORMACIÓN DEL ENTORNO ════╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}║ {Fore.WHITE}⚡ Venv no disponible             {Fore.LIGHTYELLOW_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}║ {Fore.WHITE}🔧 Métodos alternativos usados    {Fore.LIGHTYELLOW_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}║ {Fore.WHITE}📝 Revisa mensajes anteriores     {Fore.LIGHTYELLOW_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}╚{'═'*35}╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTRED_EX}╔═══ ⚠️  ADVERTENCIAS IMPORTANTES ⚠️ ════════╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Usa estas herramientas éticamente      {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Consulta los README respectivos        {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Respeta términos legales               {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}╚{'═'*42}╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTBLUE_EX}╔═══ 📋 NOTAS TÉCNICAS ═══════╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}TBomb: Solo India activo    {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}SETSMS: Requiere Git Bash   {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}Venv: Prioridad automática  {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╚{'═'*29}╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para continuar...{Style.RESET_ALL}", end="")
    input()

def use_additional_tools():
    """Muestra una lista de herramientas instaladas y ejecuta la seleccionada"""
    clear_console()
    
    print(f"{Fore.RED}╔══════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.RED}║                                                                  ║")
    print(f"{Fore.RED}║            {Fore.LIGHTGREEN_EX}🚀 EJECUTOR DE HERRAMIENTAS 🚀{Fore.RED}              ║")
    print(f"{Fore.RED}║                {Fore.YELLOW}Sistema de Lanzamiento Rápido{Fore.RED}                 ║")
    print(f"{Fore.RED}║                                                                  ║")
    print(f"{Fore.RED}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    # Verificar estado del entorno virtual
    venv_available, venv_python, venv_pip = verify_app_venv()
    if venv_available:
        show_status_message("Entorno virtual de la aplicación disponible para ejecución", "venv")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio SMS
    tools_dir = os.path.normpath(os.path.join(base_dir, 'herramientas'))
    modules_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    
    # Detectar comando de Python según el sistema operativo
    # Priorizar el Python del venv si está disponible
    if venv_available and venv_python:
        python_cmd = venv_python
        show_status_message(f"Usando Python del venv para ejecución: {python_cmd}", "venv")
    else:
        python_cmd = "python" if platform.system() == "Windows" else "python3"
        show_status_message(f"Usando Python del sistema: {python_cmd}", "warning")
    
    # Lista de herramientas conocidas y sus comandos de ejecución
    tools = [
        {
            'name': 'spam-wa',
            'run_cmd': f"{python_cmd} spam-wa.py",
            'main_file': 'spam-wa.py',
            'dir': modules_dir,
            'icon': '💬',
            'description': 'Spam automatizado WhatsApp',
            'requires_venv': False  # Esta herramienta puede ejecutarse sin venv específico
        },
        {
            'name': 'TBomb',
            'run_cmd': f"{python_cmd} bomber.py",
            'main_file': 'bomber.py',
            'dir': os.path.normpath(os.path.join(tools_dir, 'TBomb')),
            'icon': '💣',
            'description': 'Bombardero SMS/Llamadas',
            'requires_venv': True  # Esta herramienta se beneficia del venv
        },
        {
            'name': 'SETSMS',
            'run_cmd': 'bash SETSMS.sh',
            'main_file': os.path.join('SETSMS', 'SETSMS.sh'),
            'dir': tools_dir,
            'icon': '📱',
            'description': 'Sistema SMS automático',
            'requires_venv': False  # Script bash no necesita venv Python
        }
    ]
    
    show_separator()
    show_status_message("Escaneando herramientas disponibles...", "loading")
    time.sleep(1)
    
    # Filtrar herramientas que están instaladas
    available_tools = []
    for tool in tools:
        tool_dir = os.path.normpath(tool['dir'])
        main_file_path = os.path.normpath(os.path.join(tool_dir, tool['main_file']))
        
        show_status_message(f"Verificando {tool['name']}: {main_file_path}", "info")
        if os.path.exists(tool_dir) and os.path.exists(main_file_path):
            available_tools.append(tool)
            show_status_message(f"{tool['name']} encontrado y disponible", "success")
            
            # Verificar si necesita venv y está disponible
            if tool['requires_venv'] and venv_available:
                show_status_message(f"  🐍 {tool['name']} usará el entorno virtual", "venv")
            elif tool['requires_venv'] and not venv_available:
                show_status_message(f"  ⚠️ {tool['name']} se ejecutará sin venv (puede tener problemas)", "warning")
        else:
            show_status_message(f"{tool['name']} no disponible", "warning")
            if tool['name'] == 'spam-wa':
                show_status_message("Verifica que 'spam-wa.py' existe en modules/", "error")
            elif tool['name'] == 'TBomb':
                show_status_message("Verifica que 'bomber.py' existe en herramientas/TBomb/", "error")
            elif tool['name'] == 'SETSMS':
                show_status_message("Verifica que 'SETSMS.sh' existe en herramientas/SETSMS/", "error")
    
    if not available_tools:
        print(f"\n{Fore.LIGHTRED_EX}╔═══ ❌ NO HAY HERRAMIENTAS DISPONIBLES ═══╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}No se encontraron herramientas en:        {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Carpeta 'herramientas'                  {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Carpeta 'modules'                       {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}                                          {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}💡 Instala herramientas primero           {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}╚{'═'*42}╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para volver al submenú...{Style.RESET_ALL}", end="")
        input()
        return
    
    # Mostrar lista de herramientas disponibles
    print(f"\n{Fore.LIGHTCYAN_EX}🛠️  HERRAMIENTAS DISPONIBLES{Style.RESET_ALL}")
    show_separator()
    print()
    
    for i, tool in enumerate(available_tools, 1):
        # Indicador de estado mejorado
        if tool['requires_venv'] and venv_available:
            status_indicator = f"{Fore.LIGHTGREEN_EX}● Online (venv){Style.RESET_ALL}"
        elif tool['requires_venv'] and not venv_available:
            status_indicator = f"{Fore.LIGHTYELLOW_EX}● Online (sistema){Style.RESET_ALL}"
        else:
            status_indicator = f"{Fore.LIGHTGREEN_EX}● Online{Style.RESET_ALL}"
        
        print(f"  {Fore.LIGHTGREEN_EX}[{i}]{Fore.WHITE} {tool['icon']} {tool['name']:<12} {status_indicator}")
        print(f"      {Fore.CYAN}└─ {tool['description']}{Style.RESET_ALL}")
        print()
    
    print(f"  {Fore.LIGHTYELLOW_EX}[99]{Fore.WHITE} 🔙 Volver al submenú{Style.RESET_ALL}")
    print()
    show_separator()
    
    try:
        choice = input(f"{Fore.LIGHTRED_EX}┌─[{Fore.WHITE}DarK-SMS{Fore.LIGHTRED_EX}]─[{Fore.WHITE}Herramientas{Fore.LIGHTRED_EX}]\n└──╼ {Fore.WHITE}").strip()
        
        if choice == "99":
            show_status_message("Regresando al menú anterior...", "info")
            time.sleep(1)
            return
        
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(available_tools):
            show_status_message("Opción no válida. Selecciona un número de la lista", "error")
            time.sleep(2)
            return
        
        selected_tool = available_tools[choice_idx]
        tool_name = selected_tool['name']
        tool_dir = os.path.normpath(selected_tool['dir'])
        run_cmd = selected_tool['run_cmd']
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}╔═══ 🚀 INICIANDO {tool_name.upper()} ═══╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.WHITE}📍 Directorio: {tool_dir:<15} {Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.WHITE}⚡ Comando: {run_cmd:<19} {Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL}")
        
        # Mostrar información del entorno que se usará
        if selected_tool['requires_venv'] and venv_available:
            print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.WHITE}🐍 Entorno: venv de aplicación  {Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL}")
        elif selected_tool['requires_venv'] and not venv_available:
            print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.WHITE}⚠️  Entorno: sistema (sin venv)  {Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.WHITE}✅ Entorno: no requiere venv    {Fore.LIGHTMAGENTA_EX}║{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTMAGENTA_EX}╚{'═'*33}╝{Style.RESET_ALL}")
        
        # Verificar si es SETSMS en Windows
        if tool_name == 'SETSMS' and platform.system() == 'Windows':
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ⚠️  ADVERTENCIA WINDOWS ⚠️ ══════╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}SETSMS.sh no es ejecutable        {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}directamente en Windows            {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*35}╝{Style.RESET_ALL}")
            
            print(f"\n{Fore.LIGHTBLUE_EX}╔═══ 💡 OPCIONES DISPONIBLES ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Usar Git Bash: bash SETSMS.sh   {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Usar WSL para ejecutar          {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Ejecutar scripts en /tools      {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}╚{'═'*33}╝{Style.RESET_ALL}")
            
            tools_path = os.path.normpath(os.path.join(tool_dir, 'SETSMS', 'tools'))
            print(f"\n{Fore.LIGHTCYAN_EX}📍 Ruta tools: {tools_path}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTYELLOW_EX}📖 Consulta el README de SETSMS para más detalles{Style.RESET_ALL}")
            
            print(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para volver al submenú...{Style.RESET_ALL}", end="")
            input()
            return
        
        print(f"\n{Fore.LIGHTGREEN_EX}🔄 Ejecutando {tool_name}...{Style.RESET_ALL}")
        time.sleep(1)
        
        try:
            # Cambiar al directorio de la herramienta
            original_dir = os.getcwd()
            os.chdir(tool_dir)
            
            # Para herramientas que requieren venv, configurar el entorno
            env = os.environ.copy()
            if selected_tool['requires_venv'] and venv_available:
                # Añadir el venv al PATH para que use las dependencias del venv
                venv_dir, venv_python, venv_pip = get_app_venv_paths()
                venv_bin_dir = os.path.dirname(venv_python)
                env['PATH'] = f"{venv_bin_dir}{os.pathsep}{env['PATH']}"
                show_status_message("Configurado entorno virtual para la ejecución", "venv")
            
            # Ejecutar la herramienta
            subprocess.run(run_cmd, shell=True, check=True, env=env)
            
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ❌ ERROR DE EJECUCIÓN ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Herramienta: {tool_name:<14} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Código error: {str(e):<13} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*31}╝{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ❌ ERROR INESPERADO ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Herramienta: {tool_name:<12} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}Error: {str(e):<18} {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*29}╝{Style.RESET_ALL}")
        finally:
            # Volver al directorio principal (modules)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print(f"\n{Fore.LIGHTGREEN_EX}╔═══ ✅ EJECUCIÓN FINALIZADA ════════╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}{tool_name} ha terminado su proceso  {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}╚{'═'*34}╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para volver al submenú...{Style.RESET_ALL}", end="")
        input()
        
    except ValueError:
        show_status_message("Entrada no válida. Introduce un número", "error")
        time.sleep(2)
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTYELLOW_EX}🔄 Operación cancelada por el usuario{Style.RESET_ALL}")
        # Volver al directorio principal (modules) en caso de interrupción
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para volver al submenú...{Style.RESET_ALL}", end="")
        input()

if __name__ == "__main__":
    print(f"{Fore.LIGHTRED_EX}❌ Este módulo debe importarse desde main.py{Style.RESET_ALL}")
