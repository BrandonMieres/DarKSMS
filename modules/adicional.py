
#!/usr/bin/python3

import os
import platform
import subprocess
import time
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
{Fore.RED}║        {Fore.LIGHTCYAN_EX}🛠️  HERRAMIENTAS ADICIONALES AVANZADAS  🛠️{Fore.RED}          ║
{Fore.RED}║                  {Fore.YELLOW}Sistema de Instalación Automática{Fore.RED}              ║
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
        "execute": "🚀"
    }
    
    colors = {
        "info": Fore.LIGHTCYAN_EX,
        "success": Fore.LIGHTGREEN_EX,
        "error": Fore.LIGHTRED_EX, 
        "warning": Fore.LIGHTYELLOW_EX,
        "loading": Fore.LIGHTBLUE_EX,
        "install": Fore.LIGHTMAGENTA_EX,
        "execute": Fore.LIGHTGREEN_EX
    }
    
    icon = icons.get(status_type, "•")
    color = colors.get(status_type, Fore.WHITE)
    
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def install_additional_tools():
    """Instala herramientas adicionales (TBomb y SETSMS) en la carpeta herramientas"""
    clear_console()
    show_tools_header()
    show_separator()
    
    show_status_message("Iniciando instalación de herramientas adicionales...", "install")
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
            'install_cmd': [python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            'run_cmd': f"{python_cmd} bomber.py",
            'main_file': 'bomber.py',
            'icon': '💣',
            'description': 'Herramienta de bombardeo SMS/Llamadas',
            'dir': os.path.normpath(os.path.join(tools_dir, 'TBomb'))
        },
        {
            'name': 'SETSMS',
            'repo_url': 'https://github.com/Darkmux/SETSMS.git',
            'install_cmd': [python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'],
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
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}┌─ {tool['icon']} INSTALANDO {tool_name.upper()} ({i}/{len(tools)}) ─┐{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}│ {Fore.WHITE}{tool['description']:<45} {Fore.LIGHTMAGENTA_EX}│{Style.RESET_ALL}")
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
            os.chdir(tool_dir)
            
            # Verificar si existe requirements.txt antes de instalar dependencias
            requirements_path = 'requirements.txt'
            if os.path.exists(requirements_path):
                show_status_message(f"Instalando dependencias para {tool_name}...", "loading")
                subprocess.run(tool['install_cmd'], check=True)
                show_status_message(f"Dependencias de {tool_name} instaladas", "success")
            else:
                show_status_message(f"No se encontró requirements.txt para {tool_name}", "warning")
            
            # Configurar permisos (solo necesario en sistemas Unix-like)
            if platform.system() != 'Windows':
                show_status_message(f"Configurando permisos para {tool_name}...", "loading")
                script_file = tool['main_file']
                if os.path.exists(script_file):
                    subprocess.run(['chmod', '+x', script_file], check=True)
                    show_status_message(f"Permisos configurados para {script_file}", "success")
                else:
                    show_status_message(f"Archivo principal {script_file} no encontrado", "warning")
            
            print(f"\n{Fore.LIGHTGREEN_EX}╔═══ ✅ {tool_name.upper()} INSTALADO CORRECTAMENTE ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}📍 Ubicación: {tool_dir:<35} {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}🚀 Comando: {tool['run_cmd']:<37} {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}💡 Uso: cd {tool_dir} && {tool['run_cmd']:<20} {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}╚{'═'*53}╝{Style.RESET_ALL}")
            
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
        
        # Volver al directorio principal (modules)
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        if i < len(tools):
            print(f"\n{Fore.CYAN}{'─'*50}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTGREEN_EX}╔══════════════════════════════════════════════════════════════════╗")
    print(f"{Fore.LIGHTGREEN_EX}║                                                                  ║")
    print(f"{Fore.LIGHTGREEN_EX}║        {Fore.WHITE}🎉 INSTALACIÓN DE HERRAMIENTAS COMPLETADA 🎉{Fore.LIGHTGREEN_EX}         ║")
    print(f"{Fore.LIGHTGREEN_EX}║                                                                  ║")
    print(f"{Fore.LIGHTGREEN_EX}╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTRED_EX}╔═══ ⚠️  ADVERTENCIAS IMPORTANTES ⚠️  ═══╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Usa estas herramientas éticamente      {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Consulta los README respectivos        {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}• Respeta términos legales               {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}╚{'═'*41}╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTBLUE_EX}╔═══ 📋 NOTAS TÉCNICAS ═══╗{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}TBomb: Solo India activo    {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}SETSMS: Requiere Git Bash   {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}Windows: Usa WSL si es req. {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}╚{'═'*27}╝{Style.RESET_ALL}")
    
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
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Directorio SMS
    tools_dir = os.path.normpath(os.path.join(base_dir, 'herramientas'))
    modules_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    
    # Detectar comando de Python según el sistema operativo
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    
    # Lista de herramientas conocidas y sus comandos de ejecución
    tools = [
        {
            'name': 'spam-wa',
            'run_cmd': f"{python_cmd} spam-wa.py",
            'main_file': 'spam-wa.py',
            'dir': modules_dir,
            'icon': '💬',
            'description': 'Spam automatizado WhatsApp'
        },
        {
            'name': 'TBomb',
            'run_cmd': f"{python_cmd} bomber.py",
            'main_file': 'bomber.py',
            'dir': os.path.normpath(os.path.join(tools_dir, 'TBomb')),
            'icon': '💣',
            'description': 'Bombardero SMS/Llamadas'
        },
        {
            'name': 'SETSMS',
            'run_cmd': 'bash SETSMS.sh',
            'main_file': os.path.join('SETSMS', 'SETSMS.sh'),
            'dir': tools_dir,
            'icon': '📱',
            'description': 'Sistema SMS automático'
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
        
        # Depuración: listar archivos en el directorio para todas las herramientas
        if os.path.exists(tool_dir):
            try:
                files_in_dir = [f for f in os.listdir(tool_dir) if os.path.isfile(os.path.join(tool_dir, f))]
                show_status_message(f"Archivos en {tool_dir}: {', '.join(files_in_dir)}", "info")
            except Exception as e:
                show_status_message(f"Error listando archivos en {tool_dir}: {str(e)}", "warning")
        
        show_status_message(f"Verificando {tool['name']}: {main_file_path}", "info")
        if os.path.exists(tool_dir) and os.path.exists(main_file_path):
            available_tools.append(tool)
            show_status_message(f"{tool['name']} encontrado y disponible", "success")
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
        status_indicator = f"{Fore.LIGHTGREEN_EX}● Online{Style.RESET_ALL}"
        print(f"  {Fore.LIGHTGREEN_EX}[{i}]{Fore.WHITE} {tool['icon']} {tool['name']:<12} {status_indicator}")
        print(f"      {Fore.CYAN}└─ {tool['description']}{Style.RESET_ALL}")
        print()
    
    print(f"  {Fore.LIGHTYELLOW_EX}[99]{Fore.WHITE} 🔙 Volver al submenú{Style.RESET_ALL}")
    print()
    show_separator()
    
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
        print(f"{Fore.LIGHTMAGENTA_EX}╚{'═'*33}╝{Style.RESET_ALL}")
        
        # Verificar si es SETSMS en Windows
        if tool_name == 'SETSMS' and platform.system() == 'Windows':
            print(f"\n{Fore.LIGHTRED_EX}╔═══ ⚠️  ADVERTENCIA WINDOWS ⚠️  ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}SETSMS.sh no es ejecutable        {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}║ {Fore.WHITE}directamente en Windows            {Fore.LIGHTRED_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTRED_EX}╚{'═'*35}╝{Style.RESET_ALL}")
            
            print(f"\n{Fore.LIGHTBLUE_EX}╔═══ 💡 OPCIONES DISPONIBLES ═══╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Usar Git Bash: bash SETSMS.sh   {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Usar WSL para ejecutar          {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}║ {Fore.WHITE}• Ejecutar scripts en /tools      {Fore.LIGHTBLUE_EX}║{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLUE_EX}╚{'═'*33}╝{Style.RESET_ALL}")
            
            tools_path = os.path.normpath(os.path.join(tool_dir, 'SETSMS', 'tools'))
            print(f"\n{Fore.LIGHTCYAN_EX}📁 Ruta tools: {tools_path}{Style.RESET_ALL}")
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
            
            # Ejecutar la herramienta
            subprocess.run(run_cmd, shell=True, check=True)
            
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
        
        print(f"\n{Fore.LIGHTGREEN_EX}╔═══ ✅ EJECUCIÓN FINALIZADA ═══╗{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}║ {Fore.WHITE}{tool_name} ha terminado su proceso  {Fore.LIGHTGREEN_EX}║{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}╚{'═'*33}╝{Style.RESET_ALL}")
        
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
