#!/usr/bin/python3

import os
import sys
import time
from modules.install import check_and_use_venv, install_dependencies
from modules.run import setup_and_run_venv  # Nueva importación para manejar fallos en venv

# Verificación inicial para evitar ejecución con venv inexistente
venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
if os.path.normpath(sys.executable).lower().endswith(os.path.join("venv", "scripts", "python.exe").lower()) and not os.path.exists(venv_dir):
    print(f"❌ Error: Estás intentando usar el Python del entorno virtual ({sys.executable}), pero 'venv' no existe.")
    print(f"💡 Por favor, ejecuta el programa con el Python del sistema: python main.py")
    sys.exit(1)

# Intentar importar las dependencias necesarias
try:
    from colorama import Fore, Style, init
    from modules.sms import open_tabs
    from modules.adicional import install_additional_tools, use_additional_tools, clear_console
except ImportError as e:
    print(f"❌ Error: No se pudieron cargar las dependencias necesarias ({e}).")
    print("⚠️ Esto puede deberse a que faltan módulos como setuptools, colorama, undetected_chromedriver o los módulos personalizados.")
    while True:
        response = input("¿Deseas instalar las dependencias ahora? (s/n): ").strip().lower()
        if response in ['s', 'sí', 'si', 'y', 'yes']:
            venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
            os_name = sys.platform
            pip_bin = os.path.join(venv_dir, "bin", "pip") if os_name.startswith("linux") else os.path.join(venv_dir, "Scripts", "pip.exe")
            if install_dependencies(venv_dir, pip_bin):
                python_bin = os.path.join(venv_dir, "bin", "python") if os_name.startswith("linux") else os.path.join(venv_dir, "Scripts", "python.exe")
                print(f"🔄 Instalación completada. Por favor, ejecuta manualmente con: {python_bin} main.py")
                sys.exit(0)
            else:
                print("❌ No se pudo completar la instalación de dependencias. Saliendo...")
                sys.exit(1)
        elif response in ['n', 'no']:
            print("👋 Saliendo del programa...")
            sys.exit(1)
        else:
            print("❌ Opción no válida. Por favor, ingresa 's' o 'n'.")

# Inicializar colorama
init(autoreset=True)

# Colores
negro = '\033[30m'
rojo = '\033[31m'
verde = '\033[32m'
amarillo = '\033[33m'
azul = '\033[34m'
rosado = '\033[35m'
calipso = '\033[36m'
blanco = '\033[37m'
cierre = '\033[39m'

def show_banner():
    """Muestra el banner principal de DarK SMS"""
    banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                              ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗███╗   ███╗███████╗{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝████╗ ████║██╔════╝{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██║  ██║███████║██████╔╝█████╔╝     ███████╗██╔████╔██║███████╗{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██║  ██║██╔══██║██╔══██╗██╔═██╗     ╚════██║██║╚██╔╝██║╚════██║{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██████╔╝██║  ██║██║  ██║██║  ██╗    ███████║██║ ╚═╝ ██║███████║{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝╚══════╝{Fore.RED}  ║
{Fore.RED}║                                                              ║
{Fore.RED}║              {Fore.YELLOW}⚡ Herramienta de SMS Automático ⚡{Fore.RED}             ║
{Fore.RED}║                   {Fore.CYAN}Versión 1.0 {Fore.RED}                               ║
{Fore.RED}║                                                              ║
{Fore.RED}╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{Fore.MAGENTA}┌─────────────────────────────────────────────────────────────┐
{Fore.MAGENTA}│  {Fore.WHITE}💀 Desarrollado por: {Fore.LIGHTGREEN_EX}DarK{Fore.WHITE}                                  {Fore.MAGENTA}│
{Fore.MAGENTA}│  {Fore.WHITE}🎯 Uso: {Fore.LIGHTCYAN_EX}Solo para propósitos educativos{Fore.WHITE}                    {Fore.MAGENTA}│
{Fore.MAGENTA}│  {Fore.WHITE}⚠️  Advertencia: {Fore.LIGHTYELLOW_EX}Usar de manera ética y legal{Fore.WHITE}               {Fore.MAGENTA}│
{Fore.MAGENTA}└─────────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
    print(banner)

def show_separator():
    """Muestra un separador visual"""
    print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")

def get_user_input(prompt):
    """
    Función mejorada para obtener input del usuario con mejor manejo
    """
    sys.stdout.flush()  # Asegurar que todo el output se muestre antes del input
    try:
        user_input = input(prompt).strip()
        return user_input
    except (KeyboardInterrupt, EOFError):
        return None

def additional_tools_menu():
    """Muestra el submenú para herramientas adicionales"""
    while True:
        clear_console()
        show_banner()
        show_separator()
        print(f"{Fore.LIGHTCYAN_EX}🛠️  HERRAMIENTAS ADICIONALES{Style.RESET_ALL}")
        show_separator()
        print()
        
        menu_options = [
            ("1", "🔧 Instalar herramientas adicionales", Fore.LIGHTGREEN_EX),
            ("2", "🚀 Usar herramientas adicionales", Fore.LIGHTBLUE_EX),
            ("99", "🔙 Volver al menú principal", Fore.LIGHTYELLOW_EX)
        ]
        
        for num, desc, color in menu_options:
            print(f"  {color}[{num}]{Fore.WHITE} {desc}{Style.RESET_ALL}")
        
        print()
        show_separator()

        choice = get_user_input(f"{Fore.LIGHTRED_EX}┌─[{Fore.WHITE}DarK-SMS{Fore.LIGHTRED_EX}]─[{Fore.WHITE}Herramientas{Fore.LIGHTRED_EX}]\n└──╼ {Fore.WHITE}")
        
        if choice is None:  # KeyboardInterrupt o EOFError
            print(f"{Fore.YELLOW}\n🔙 Volviendo al menú principal...{Style.RESET_ALL}")
            time.sleep(1)
            break

        if choice not in ["1", "2", "99"]:
            print(f"{Fore.RED}❌ Error: Opción no válida. Seleccione 1, 2 o 99.{Style.RESET_ALL}")
            time.sleep(2)
            continue

        if choice == "1":
            print(f"{Fore.LIGHTGREEN_EX}🔧 Instalando herramientas adicionales...{Style.RESET_ALL}")
            install_additional_tools()
        elif choice == "2":
            print(f"{Fore.LIGHTBLUE_EX}🚀 Iniciando herramientas adicionales...{Style.RESET_ALL}")
            use_additional_tools()
        elif choice == "99":
            break

def menu():
    """Menú principal de la aplicación"""
    while True:
        clear_console()
        show_banner()
        time.sleep(0.5)  # Pequeña pausa para asegurar que se muestre todo
        show_separator()
        print(f"{Fore.LIGHTMAGENTA_EX}📋 MENÚ PRINCIPAL{Style.RESET_ALL}")
        show_separator()
        print()
        
        menu_options = [
            ("1", "🌐 Abrir páginas (Chrome con User-Agent aleatorio)", Fore.LIGHTGREEN_EX),
            ("2", "ℹ️  Información de la herramienta", Fore.LIGHTBLUE_EX),
            ("3", "📖 Cómo usar", Fore.LIGHTYELLOW_EX),
            ("4", "🛠️  Herramientas adicionales", Fore.LIGHTCYAN_EX),
            ("5", "📦 Instalar dependencias", Fore.LIGHTMAGENTA_EX),
            ("99", "🚪 Salir", Fore.LIGHTRED_EX)
        ]
        
        for num, desc, color in menu_options:
            print(f"  {color}[{num}]{Fore.WHITE} {desc}{Style.RESET_ALL}")
        
        print()
        show_separator()

        d = get_user_input(f"{Fore.LIGHTRED_EX}┌─[{Fore.WHITE}DarK-SMS{Fore.LIGHTRED_EX}]─[{Fore.WHITE}Main-Menu{Fore.LIGHTRED_EX}]\n└──╼ {Fore.WHITE}")
        
        if d is None:  # KeyboardInterrupt o EOFError
            print(f"{Fore.YELLOW}\n👋 Saliendo...{Style.RESET_ALL}")
            time.sleep(1)
            break

        if d not in ["1", "2", "3", "4", "5", "99"]:
            print(f"{Fore.RED}❌ Error: Opción no válida. Seleccione 1, 2, 3, 4, 5 o 99.{Style.RESET_ALL}")
            time.sleep(2)
            continue

        if d == "1":
            print(f"{Fore.LIGHTGREEN_EX}🚀 Iniciando navegador con User-Agents aleatorios...{Style.RESET_ALL}")
            time.sleep(1)
            open_tabs()
        elif d == "2":
            clear_console()
            show_banner()
            print(f"{Fore.LIGHTCYAN_EX}ℹ️  INFORMACIÓN DE LA HERRAMIENTA{Style.RESET_ALL}")
            show_separator()
            info_text = """
📱 DarK SMS Tool es una herramienta avanzada para la automatización de SMS
   que utiliza múltiples servicios web para el envío masivo de mensajes.

🎯 Características principales:
   • User-Agents aleatorios para evitar detección
   • Soporte para múltiples plataformas SMS
   • Integración con herramientas adicionales
   • Interfaz de usuario mejorada

⚠️  IMPORTANTE: Esta herramienta debe usarse únicamente para propósitos
   educativos y de investigación. El uso indebido es responsabilidad
   del usuario.
"""
            print(f"{Fore.WHITE}{info_text}{Style.RESET_ALL}")
            
        elif d == "3":
            clear_console()
            show_banner()
            print(f"{Fore.LIGHTYELLOW_EX}📖 GUÍA DE USO{Style.RESET_ALL}")
            show_separator()
            usage_text = f"""
{Fore.LIGHTCYAN_EX}🔹 PASO 1:{Fore.WHITE} Ejecuta la opción 1 para abrir las páginas web

{Fore.LIGHTCYAN_EX}🔹 PASO 2:{Fore.WHITE} Se abrirán múltiples pestañas en Chrome con User-Agents 
          aleatorios extraídos de modules/ua.txt

{Fore.LIGHTCYAN_EX}🔹 PASO 3:{Fore.WHITE} Introduce el número de teléfono objetivo en las 
          casillas correspondientes de cada página

{Fore.LIGHTCYAN_EX}🔹 PASO 4:{Fore.WHITE} Acepta o continúa en cada página para enviar SMS

{Fore.LIGHTCYAN_EX}🔹 PASO 5:{Fore.WHITE} Utiliza las herramientas adicionales si es necesario:
          • spam-wa (WhatsApp)
          • TBomb (SMS/llamadas)  
          • SETSMS (SMS automatizado)

{Fore.LIGHTRED_EX}⚠️  RECORDATORIO:{Fore.WHITE} Usa estas herramientas de manera ética y legal.
                 ¡Respeta la privacidad y los términos de servicio!

{Fore.LIGHTGREEN_EX}💚 ¡Gracias por tu apoyo y uso responsable!{Style.RESET_ALL}
"""
            print(usage_text)
            time.sleep(5)
            
        elif d == "4":
            additional_tools_menu()
        elif d == "5":
            print(f"{Fore.LIGHTMAGENTA_EX}📦 Iniciando instalación de dependencias...{Style.RESET_ALL}")
            time.sleep(1)
            venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
            os_name = sys.platform
            pip_bin = os.path.join(venv_dir, "bin", "pip") if os_name.startswith("linux") else os.path.join(venv_dir, "Scripts", "pip.exe")
            install_dependencies(venv_dir, pip_bin)
        elif d == "99":
            clear_console()
            print(f"{Fore.LIGHTRED_EX}╔═══════════════════════════════════════╗")
            print(f"{Fore.LIGHTRED_EX}║{Fore.WHITE}     👋 ¡Gracias por usar DarK SMS!    {Fore.LIGHTRED_EX}║")
            print(f"{Fore.LIGHTRED_EX}║{Fore.WHITE}        🔒 Cerrando aplicación...      {Fore.LIGHTRED_EX}║")
            print(f"{Fore.LIGHTRED_EX}╚═══════════════════════════════════════╝{Style.RESET_ALL}")
            time.sleep(2)
            break

        # Pausa mejorada antes de volver al menú
        try:
            input(f"\n{Fore.LIGHTMAGENTA_EX}📌 Presiona Enter para continuar...{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            continue

if __name__ == "__main__":
    try:
        if not check_and_use_venv():
            print("⚠️ Fallo en la configuración del entorno virtual. Intentando recuperación automática...")
            if not setup_and_run_venv():
                print("❌ No se pudo recuperar el entorno virtual. Saliendo...")
                sys.exit(1)
        menu()
    except Exception as e:
        print(f"{Fore.RED}💥 Error crítico: {e}{Style.RESET_ALL}")
        try:
            input(f"{Fore.YELLOW}Presiona Enter para salir...{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            pass
        sys.exit(1)
