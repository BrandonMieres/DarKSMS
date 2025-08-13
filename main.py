#!/usr/bin/python3

import os
import sys
import time
import subprocess
import platform
import importlib.util

def print_basic(message, color_code="37"):
    """Función para imprimir con colores básicos sin depender de colorama"""
    print(f"\033[{color_code}m{message}\033[0m")

def clear_input_buffer():
    """Limpia el buffer de entrada para evitar inputs residuales"""
    try:
        # Limpiar buffer en Windows
        if os.name == 'nt':
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            # Limpiar buffer en Unix/Linux
            import termios, tty
            import select
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
        
        # Flush adicional
        if hasattr(sys.stdin, 'flush'):
            sys.stdin.flush()
            
    except Exception:
        # Si no se puede limpiar, continuar silenciosamente
        pass

def get_user_input_safe(prompt, valid_options=None, clear_buffer=True):
    """
    Función segura para obtener input del usuario
    - Limpia el buffer antes de solicitar entrada
    - Valida las opciones si se proporcionan
    - Maneja errores de entrada
    """
    if clear_buffer:
        clear_input_buffer()
        # Pequeña pausa para asegurar la limpieza
        time.sleep(0.1)
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Mostrar el prompt y obtener entrada
            user_input = input(prompt).strip()
            
            # Si no hay opciones válidas especificadas, devolver cualquier entrada
            if valid_options is None:
                return user_input
            
            # Convertir opciones válidas a strings para comparación consistente
            valid_str_options = [str(opt) for opt in valid_options]
            
            # Validar entrada si se especifican opciones
            if user_input in valid_str_options:
                return user_input
            else:
                if attempt < max_attempts - 1:
                    print_basic(f"❌ Opción inválida. Opciones válidas: {', '.join(valid_str_options)}", "31")
                    print_basic(f"⏳ Intento {attempt + 2}/{max_attempts}", "33")
                    clear_input_buffer()  # Limpiar después del error
                    time.sleep(1)
                continue
                
        except (KeyboardInterrupt, EOFError):
            print_basic("\n👋 Interrumpido por el usuario", "33")
            return None
        except Exception as e:
            print_basic(f"❌ Error al leer entrada: {e}", "31")
            if attempt < max_attempts - 1:
                clear_input_buffer()
                time.sleep(1)
            continue
    
    # Si llegamos aquí, se agotaron los intentos
    print_basic("❌ Demasiados intentos fallidos", "31")
    return None

def wait_for_enter(message="📌 Presiona Enter para continuar..."):
    """Función mejorada para esperar Enter del usuario"""
    clear_input_buffer()
    try:
        input(f"\n{message}")
    except (KeyboardInterrupt, EOFError):
        pass
    clear_input_buffer()

def is_dependency_available(module_name):
    """Verifica si un módulo está disponible sin importarlo"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except ImportError:
        return False

def check_critical_dependencies():
    """Verifica si las dependencias críticas están instaladas"""
    critical_deps = {
        'colorama': 'colorama',
        'undetected_chromedriver': 'undetected_chromedriver',
        'setuptools': 'setuptools',
        'requests': 'requests'
    }
    
    missing_deps = []
    available_deps = []
    
    for display_name, import_name in critical_deps.items():
        if is_dependency_available(import_name):
            available_deps.append(display_name)
        else:
            missing_deps.append(display_name)
    
    return missing_deps, available_deps

def is_in_correct_venv():
    """Verifica si estamos ejecutando desde el entorno virtual correcto"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    
    # Normalizar rutas para comparación
    current_python = os.path.normpath(sys.executable).lower()
    venv_path = os.path.normpath(venv_dir).lower()
    
    return current_python.startswith(venv_path)

def get_python_and_pip_paths():
    """Obtiene las rutas de Python y pip según el sistema operativo"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    os_name = platform.system()
    
    if os_name in ["Linux", "Darwin"]:  # Linux o macOS
        python_bin = os.path.join(venv_dir, "bin", "python")
        pip_bin = os.path.join(venv_dir, "bin", "pip")
    else:  # Windows
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    
    return python_bin, pip_bin, venv_dir

def import_install_modules():
    """Intenta importar los módulos de instalación"""
    try:
        # Agregar el directorio actual al path si no está
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from modules.install import check_and_use_venv, install_dependencies, verify_python_installation
        from modules.run import setup_and_run_venv
        return check_and_use_venv, install_dependencies, verify_python_installation, setup_and_run_venv
    except ImportError as e:
        print_basic(f"❌ Error crítico: No se pueden cargar los módulos de instalación ({e})", "31")
        print_basic("💡 Verificando estructura de directorios...", "33")
        
        # Verificar si existe la carpeta modules
        modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")
        if not os.path.exists(modules_dir):
            print_basic(f"❌ La carpeta 'modules' no existe en: {modules_dir}", "31")
        else:
            print_basic("✅ Carpeta 'modules' encontrada.", "32")
            
            # Verificar archivos específicos
            required_files = ["install.py", "run.py", "sms.py", "adicional.py"]
            for file in required_files:
                file_path = os.path.join(modules_dir, file)
                if os.path.exists(file_path):
                    print_basic(f"✅ {file} encontrado.", "32")
                else:
                    print_basic(f"❌ {file} no encontrado.", "31")
        
        return None, None, None, None

def setup_environment_automatically():
    """Configura el entorno automáticamente detectando el estado actual"""
    print_basic("🔍 Analizando entorno actual...", "36")
    
    # Verificar dependencias críticas
    missing_deps, available_deps = check_critical_dependencies()
    
    if available_deps:
        print_basic(f"✅ Dependencias disponibles: {', '.join(available_deps)}", "32")
    
    if missing_deps:
        print_basic(f"⚠️ Dependencias faltantes: {', '.join(missing_deps)}", "33")
    
    # Verificar entorno virtual
    python_bin, pip_bin, venv_dir = get_python_and_pip_paths()
    venv_exists = os.path.exists(venv_dir) and os.path.exists(python_bin)
    in_correct_venv = is_in_correct_venv()
    
    print_basic(f"📁 Entorno virtual existe: {'Sí' if venv_exists else 'No'}", "36")
    print_basic(f"🔧 Usando venv correcto: {'Sí' if in_correct_venv else 'No'}", "36")
    
    # Determinar acción necesaria
    needs_venv_creation = not venv_exists
    needs_dependency_installation = len(missing_deps) > 0
    needs_venv_switch = venv_exists and not in_correct_venv
    
    # Importar módulos de instalación
    check_and_use_venv, install_dependencies, verify_python_installation, setup_and_run_venv = import_install_modules()
    
    if any([check_and_use_venv, install_dependencies, verify_python_installation, setup_and_run_venv]) is None:
        print_basic("❌ No se pueden cargar los módulos de instalación. Abortando...", "31")
        return False
    
    # Ejecutar acciones necesarias
    try:
        if needs_venv_creation:
            print_basic("🏗️ Creando entorno virtual...", "36")
            if not verify_python_installation():
                print_basic("❌ Problema con la instalación de Python.", "31")
                return False
            
            if not setup_and_run_venv():
                print_basic("❌ Error al crear el entorno virtual.", "31")
                return False
        
        if needs_venv_switch or needs_dependency_installation:
            print_basic("⚙️ Configurando entorno virtual...", "36")
            if not check_and_use_venv():
                print_basic("⚠️ Problema al configurar el entorno virtual.", "33")
                # Continuar, podría funcionar de todas formas
        
        # Verificar nuevamente después de la configuración
        missing_deps_after, _ = check_critical_dependencies()
        if missing_deps_after:
            print_basic(f"🔧 Instalando dependencias faltantes: {', '.join(missing_deps_after)}", "36")
            
            # Si seguimos sin venv, usar pip del sistema
            if not is_in_correct_venv():
                pip_bin = "pip3" if platform.system() != "Windows" else "pip"
            
            if not install_dependencies(venv_dir, pip_bin):
                print_basic("❌ Error al instalar dependencias.", "31")
                return False
        
        print_basic("✅ Entorno configurado correctamente.", "32")
        return True
        
    except Exception as e:
        print_basic(f"❌ Error durante la configuración: {e}", "31")
        return False

def handle_venv_mismatch():
    """Maneja el caso cuando se ejecuta con Python de venv inexistente"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    
    current_python = os.path.normpath(sys.executable).lower()
    
    # Verificar si estamos usando Python de venv que no existe
    venv_indicators = [
        os.path.join("venv", "scripts", "python.exe").lower(),
        os.path.join("venv", "bin", "python").lower()
    ]
    
    using_nonexistent_venv = any(current_python.endswith(indicator) for indicator in venv_indicators)
    
    if using_nonexistent_venv and not os.path.exists(venv_dir):
        print_basic("❌ Error: Estás intentando usar el Python del entorno virtual, pero 'venv' no existe.", "31")
        print_basic("🔧 Reconfigurando automáticamente...", "36")
        
        # Ejecutar con Python del sistema
        system_python = "python3" if platform.system() != "Windows" else "python"
        try:
            print_basic(f"🔄 Reiniciando con Python del sistema: {system_python}", "36")
            os.execvp(system_python, [system_python] + sys.argv)
        except Exception as e:
            print_basic(f"❌ Error al reiniciar: {e}", "31")
            print_basic("💡 Por favor, ejecuta el programa con: python main.py", "33")
            return False
    
    return True

def final_import_check():
    """Verificación final de importaciones antes de continuar"""
    print_basic("🔍 Verificación final de dependencias...", "36")
    
    try:
        # Intentar importar dependencias críticas
        import colorama
        from colorama import Fore, Style, init
        
        # Importar módulos del proyecto
        from modules.sms import open_tabs
        from modules.adicional import install_additional_tools, use_additional_tools, clear_console
        from modules.install import check_and_use_venv, install_dependencies
        from modules.run import setup_and_run_venv
        
        print_basic("✅ Todas las dependencias cargadas correctamente.", "32")
        return True, (colorama, Fore, Style, init, open_tabs, install_additional_tools, use_additional_tools, clear_console)
        
    except ImportError as e:
        print_basic(f"❌ Error crítico: Aún faltan dependencias después de la instalación ({e})", "31")
        print_basic("🔧 Esto puede indicar un problema con el entorno virtual o permisos.", "33")
        
        # Último intento de recuperación
        try:
            check_and_use_venv, install_dependencies, _, setup_and_run_venv = import_install_modules()
            if setup_and_run_venv and not setup_and_run_venv():
                print_basic("❌ No se pudo recuperar el sistema. Contacta al desarrollador.", "31")
                return False, None
        except:
            print_basic("❌ Fallo crítico en la recuperación del sistema.", "31")
            return False, None
        
        return False, None

# =============================================================================
# INICIO DEL PROGRAMA PRINCIPAL
# =============================================================================

def main():
    """Función principal con manejo completo de configuración automática"""
    print_basic("🚀 Iniciando DarK SMS...", "32")
    print_basic("🔧 Sistema de configuración automática activado", "36")
    
    # Paso 1: Manejar discrepancia de venv
    if not handle_venv_mismatch():
        sys.exit(1)
    
    # Paso 2: Configurar entorno automáticamente
    if not setup_environment_automatically():
        print_basic("❌ No se pudo configurar el entorno automáticamente.", "31")
        
        # Ofrecer configuración manual como fallback
        try:
            response = get_user_input_safe(
                "¿Deseas intentar la configuración manual? (s/n): ",
                valid_options=['s', 'si', 'sí', 'y', 'yes', 'n', 'no'],
                clear_buffer=True
            )
            
            if response and response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                print_basic("🔧 Iniciando configuración manual...", "36")
                check_and_use_venv, install_dependencies, _, _ = import_install_modules()
                if check_and_use_venv is None:
                    print_basic("❌ Módulos de instalación no disponibles.", "31")
                    sys.exit(1)
                
                python_bin, pip_bin, venv_dir = get_python_and_pip_paths()
                
                if install_dependencies(venv_dir, pip_bin):
                    print_basic(f"🔄 Instalación completada. Reiniciando con: {python_bin}", "32")
                    try:
                        os.execv(python_bin, [python_bin] + sys.argv)
                    except:
                        print_basic(f"💡 Por favor, ejecuta manualmente: {python_bin} main.py", "33")
                    sys.exit(0)
                else:
                    print_basic("❌ No se pudo completar la instalación. Saliendo...", "31")
                    sys.exit(1)
            else:
                print_basic("👋 Saliendo del programa...", "33")
                sys.exit(1)
        except Exception:
            print_basic("\n👋 Saliendo del programa...", "33")
            sys.exit(1)
    
    # Paso 3: Verificación final e importaciones
    success, imports = final_import_check()
    if not success:
        sys.exit(1)
    
    # Desempaquetar importaciones
    colorama, Fore, Style, init, open_tabs, install_additional_tools, use_additional_tools, clear_console = imports
    
    # Inicializar colorama
    init(autoreset=True)
    
    print(f"{Fore.LIGHTGREEN_EX}✅ Sistema configurado correctamente. Iniciando aplicación...{Style.RESET_ALL}")
    
    # Limpiar buffer antes de mostrar el menú
    clear_input_buffer()
    time.sleep(1)
    
    # Continuar con el menú principal
    show_main_menu(Fore, Style, open_tabs, install_additional_tools, use_additional_tools, clear_console)

def show_main_menu(Fore, Style, open_tabs, install_additional_tools, use_additional_tools, clear_console):
    """Muestra el menú principal de la aplicación con manejo mejorado de input"""
    
    def show_banner():
        """Muestra el banner principal de DarK SMS"""
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════╗
{Fore.RED}║                                                          ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗███╗   ███╗███████╗{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝████╗ ████║██╔════╝{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██║  ██║███████║██████╔╝█████╔╝     ███████╗██╔████╔██║███████╗{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██║  ██║██╔══██║██╔══██╗██╔═██╗     ╚════██║██║╚██╔╝██║╚════██║{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}██████╔╝██║  ██║██║  ██║██║  ██╗    ███████║██║ ╚═╝ ██║███████║{Fore.RED}  ║
{Fore.RED}║  {Fore.LIGHTRED_EX}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝     ╚═╝╚══════╝{Fore.RED}  ║
{Fore.RED}║                                                          ║
{Fore.RED}║              {Fore.YELLOW}⚡ Herramienta de SMS Automático ⚡{Fore.RED}         ║
{Fore.RED}║                   {Fore.CYAN}Versión 1.0 {Fore.RED}                           ║
{Fore.RED}║                                                          ║
{Fore.RED}╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{Fore.MAGENTA}┌──────────────────────────────────────────────────────┐
{Fore.MAGENTA}│  {Fore.WHITE}👤 Desarrollado por: {Fore.LIGHTGREEN_EX}DarK{Fore.WHITE}                           {Fore.MAGENTA}│
{Fore.MAGENTA}│  {Fore.WHITE}🎯 Uso: {Fore.LIGHTCYAN_EX}Solo para propósitos educativos{Fore.WHITE}             {Fore.MAGENTA}│
{Fore.MAGENTA}│  {Fore.WHITE}⚠️  Advertencia: {Fore.LIGHTYELLOW_EX}Usar de manera ética y legal{Fore.WHITE}        {Fore.MAGENTA}│
{Fore.MAGENTA}└──────────────────────────────────────────────────────┘ {Style.RESET_ALL}
"""
        print(banner)

    def show_separator():
        """Muestra un separador visual"""
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")

    def additional_tools_menu():
        """Muestra el submenú para herramientas adicionales"""
        while True:
            clear_console()
            clear_input_buffer()  # Limpiar buffer al entrar al submenú
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

            choice = get_user_input_safe(
                f"{Fore.LIGHTRED_EX}┌─[{Fore.WHITE}DarK-SMS{Fore.LIGHTRED_EX}]─[{Fore.WHITE}Herramientas{Fore.LIGHTRED_EX}]\n└──╼ {Fore.WHITE}",
                valid_options=["1", "2", "99"],
                clear_buffer=True
            )
            
            if choice is None:
                print(f"{Fore.YELLOW}\n🔙 Volviendo al menú principal...{Style.RESET_ALL}")
                time.sleep(1)
                break

            if choice == "1":
                print(f"{Fore.LIGHTGREEN_EX}🔧 Instalando herramientas adicionales...{Style.RESET_ALL}")
                install_additional_tools()
                wait_for_enter()
            elif choice == "2":
                print(f"{Fore.LIGHTBLUE_EX}🚀 Iniciando herramientas adicionales...{Style.RESET_ALL}")
                use_additional_tools()
                wait_for_enter()
            elif choice == "99":
                break
            
            # Limpiar buffer después de cada operación
            clear_input_buffer()

    # Menú principal
    while True:
        clear_console()
        clear_input_buffer()  # Limpiar buffer al mostrar el menú principal
        show_banner()
        time.sleep(0.5)
        show_separator()
        print(f"{Fore.LIGHTMAGENTA_EX}📋 MENÚ PRINCIPAL{Style.RESET_ALL}")
        show_separator()
        print()
        
        menu_options = [
            ("1", "🌐 Abrir páginas (Chrome con User-Agent aleatorio)", Fore.LIGHTGREEN_EX),
            ("2", "ℹ️  Información de la herramienta", Fore.LIGHTBLUE_EX),
            ("3", "📖 Cómo usar", Fore.LIGHTYELLOW_EX),
            ("4", "🛠️  Herramientas adicionales", Fore.LIGHTCYAN_EX),
            ("5", "📦 Reinstalar dependencias", Fore.LIGHTMAGENTA_EX),
            ("99", "🚪 Salir", Fore.LIGHTRED_EX)
        ]
        
        for num, desc, color in menu_options:
            print(f"  {color}[{num}]{Fore.WHITE} {desc}{Style.RESET_ALL}")
        
        print()
        show_separator()

        choice = get_user_input_safe(
            f"{Fore.LIGHTRED_EX}┌─[{Fore.WHITE}DarK-SMS{Fore.LIGHTRED_EX}]─[{Fore.WHITE}Main-Menu{Fore.LIGHTRED_EX}]\n└──╼ {Fore.WHITE}",
            valid_options=["1", "2", "3", "4", "5", "99"],
            clear_buffer=True
        )
        
        if choice is None:
            print(f"{Fore.YELLOW}\n👋 Saliendo...{Style.RESET_ALL}")
            time.sleep(1)
            break

        if choice == "1":
            print(f"{Fore.LIGHTGREEN_EX}🚀 Iniciando navegador con User-Agents aleatorios...{Style.RESET_ALL}")
            time.sleep(1)
            clear_input_buffer()
            open_tabs()
            wait_for_enter()
            
        elif choice == "2":
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
   • Instalación automática de dependencias

⚠️  IMPORTANTE: Esta herramienta debe usarse únicamente para propósitos
   educativos y de investigación. El uso indebido es responsabilidad
   del usuario.
"""
            print(f"{Fore.WHITE}{info_text}{Style.RESET_ALL}")
            wait_for_enter()
            
        elif choice == "3":
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
            wait_for_enter()
            
        elif choice == "4":
            additional_tools_menu()
            
        elif choice == "5":
            print(f"{Fore.LIGHTMAGENTA_EX}🔧 Reinstalando todas las dependencias...{Style.RESET_ALL}")
            time.sleep(1)
            
            if setup_environment_automatically():
                print(f"{Fore.LIGHTGREEN_EX}✅ Dependencias reinstaladas correctamente.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Error al reinstalar dependencias.{Style.RESET_ALL}")
            
            wait_for_enter()
                
        elif choice == "99":
            clear_console()
            print(f"{Fore.LIGHTRED_EX}╔══════════════════════════════════════════╗")
            print(f"{Fore.LIGHTRED_EX}║{Fore.WHITE}     👋 ¡Gracias por usar DarK SMS!       {Fore.LIGHTRED_EX}║")
            print(f"{Fore.LIGHTRED_EX}║{Fore.WHITE}        🔒 Cerrando aplicación...         {Fore.LIGHTRED_EX}║")
            print(f"{Fore.LIGHTRED_EX}╚══════════════════════════════════════════╝{Style.RESET_ALL}")
            time.sleep(2)
            break

        # Limpiar buffer después de cada operación
        clear_input_buffer()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print_basic(f"💥 Error crítico: {e}", "31")
        try:
            input("Presiona Enter para salir...")
        except (KeyboardInterrupt, EOFError):
            pass
        sys.exit(1)
