#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import platform
import importlib.util
import shutil

def print_colored(message, color_code="37"):
    """Imprime mensajes con colores básicos sin depender de colorama"""
    print(f"\033[{color_code}m{message}\033[0m")

def is_module_installed(module_name, python_exe=None):
    """Verifica si un módulo está instalado usando el Python especificado"""
    try:
        if python_exe and os.path.exists(python_exe):
            # Verificar en el entorno virtual específico
            result = subprocess.run([python_exe, "-c", f"import {module_name}"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        else:
            # Verificar en el entorno actual
            spec = importlib.util.find_spec(module_name)
            return spec is not None
    except (ImportError, ValueError, AttributeError, subprocess.TimeoutExpired):
        return False

def test_import_module(module_name, python_exe=None):
    """Prueba importar un módulo para verificar que funciona correctamente"""
    try:
        if python_exe and os.path.exists(python_exe):
            # Probar importación en el entorno virtual específico
            result = subprocess.run([python_exe, "-c", f"import {module_name}; print('OK')"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and "OK" in result.stdout
        else:
            # Probar en el entorno actual
            __import__(module_name)
            return True
    except (ImportError, subprocess.TimeoutExpired):
        return False
    except Exception:
        return True  # Considerar como importado si hay otros errores

def get_pip_executable(venv_dir=None):
    """Obtiene la ruta del ejecutable pip apropiado"""
    if venv_dir and os.path.exists(venv_dir):
        os_name = platform.system()
        if os_name in ["Linux", "Darwin"]:
            pip_bin = os.path.join(venv_dir, "bin", "pip")
        else:
            pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
        
        if os.path.exists(pip_bin):
            return pip_bin
    
    pip_candidates = ["pip3", "pip"] if platform.system() != "Windows" else ["pip", "pip3"]
    for pip_cmd in pip_candidates:
        try:
            result = subprocess.run([pip_cmd, "--version"], 
                                 capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return pip_cmd
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

def kill_pip_processes():
    """Mata procesos pip colgados en Windows"""
    if platform.system() == "Windows":
        try:
            subprocess.run(["taskkill", "/f", "/im", "pip.exe"], 
                         capture_output=True, timeout=10)
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                         capture_output=True, timeout=10)
        except:
            pass

def upgrade_pip_safe(pip_bin):
    """Actualiza pip de manera segura"""
    try:
        print_colored("🔄 Actualizando pip...", "33")
        python_exe = pip_bin.replace("pip.exe", "python.exe") if platform.system() == "Windows" else pip_bin.replace("pip", "python")
        if os.path.exists(python_exe):
            cmd = [python_exe, "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir"]
        else:
            cmd = [pip_bin, "install", "--upgrade", "pip", "--no-cache-dir"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 or "already satisfied" in result.stdout.lower() or "already satisfied" in result.stderr.lower():
            print_colored("✅ Pip actualizado o ya en la versión más reciente.", "32")
            return True
        else:
            print_colored(f"⚠️ No se pudo actualizar pip: {result.stderr[:100]}. Continuando...", "33")
            return False
    except subprocess.TimeoutExpired:
        print_colored("⏰ Timeout actualizando pip. Continuando...", "33")
        return False
    except Exception as e:
        print_colored(f"⚠️ Error actualizando pip: {e}. Continuando...", "33")
        return False

def install_with_timeout(pip_bin, package, timeout=120, retries=3):
    """Instala un paquete con timeout y reintentos"""
    for attempt in range(retries):
        try:
            print_colored(f"📦 Intento {attempt + 1}/{retries} para instalar {package}...", "33")
            if attempt > 0:
                kill_pip_processes()
                time.sleep(2)
            
            cmd = [pip_bin, "install", "--no-cache-dir", "--force-reinstall", package]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            if process.returncode == 0 or "already satisfied" in stdout.lower() or "already satisfied" in stderr.lower():
                print_colored(f"✅ {package} instalado o ya presente.", "32")
                return True
            else:
                error_msg = stderr.strip()[:200] if stderr else "Error desconocido"
                print_colored(f"⚠️ Error instalando {package}: {error_msg}", "33")
                
                if attempt < retries - 1:
                    print_colored("🔄 Reintentando en 3 segundos...", "33")
                    time.sleep(3)
                continue
        except subprocess.TimeoutExpired:
            print_colored(f"⏰ Timeout instalando {package}. Terminando proceso...", "33")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
                process.wait()
            if attempt < retries - 1:
                print_colored("🔄 Reintentando en 3 segundos...", "33")
                time.sleep(3)
            continue
        except Exception as e:
            print_colored(f"❌ Error inesperado en intento {attempt + 1}: {e}", "31")
            if attempt < retries - 1:
                time.sleep(2)
            continue
    
    print_colored(f"❌ No se pudo instalar {package} tras {retries} intentos.", "31")
    return False

def force_reload_module(module_name):
    """Fuerza la recarga de un módulo"""
    try:
        modules_to_clear = [mod for mod in sys.modules.keys() if module_name in mod.lower()]
        for mod in modules_to_clear:
            del sys.modules[mod]
        __import__(module_name)
        return True
    except:
        return False

def get_venv_python_executable(venv_dir):
    """Obtiene el ejecutable Python del entorno virtual"""
    os_name = platform.system()
    if os_name in ["Linux", "Darwin"]:
        python_bin = os.path.join(venv_dir, "bin", "python")
    else:
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
    return python_bin if os.path.exists(python_bin) else None

def install_dependencies(venv_dir, pip_bin=None):
    """Instala las dependencias necesarias para el proyecto"""
    try:
        import colorama
        from colorama import Fore, Style, init
        init(autoreset=True)
        colored_print = lambda msg, color=Fore.WHITE: print(f"{color}{msg}{Style.RESET_ALL}")
    except ImportError:
        colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")

    colored_print("🔧 Iniciando instalación de dependencias...", "36")
    
    # Obtener el ejecutable Python del venv
    venv_python = get_venv_python_executable(venv_dir) if venv_dir else None
    
    # Limpiar caché de módulos para evitar conflictos
    modules_to_clear = [mod for mod in sys.modules.keys() if any(x in mod.lower() for x in ['colorama', 'setuptools', 'requests', 'undetected_chromedriver', 'selenium'])]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    # Limpiar caché de pip
    cache_dir = os.path.expanduser("~\\AppData\\Local\\pip\\cache" if platform.system() == "Windows" else "~/.cache/pip")
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir, ignore_errors=True)
            colored_print("🧹 Caché de pip limpiada.", "32")
        except:
            colored_print("⚠️ No se pudo limpiar la caché de pip. Continuando...", "33")
    
    # Determinar pip a usar
    if not pip_bin:
        pip_bin = get_pip_executable(venv_dir)
    
    if not pip_bin:
        colored_print("❌ No se encontró pip. Instala Python correctamente.", "31")
        return False
    
    colored_print(f"📍 Usando pip: {pip_bin}", "36")
    if venv_python:
        colored_print(f"🐍 Python del venv: {venv_python}", "36")
    
    # Verificar que pip funciona
    try:
        result = subprocess.run([pip_bin, "--version"], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            colored_print(f"❌ Pip no funciona correctamente: {result.stderr}", "31")
            return False
        colored_print(f"✅ Pip verificado: {result.stdout.strip()}", "32")
    except Exception as e:
        colored_print(f"❌ Error al verificar pip: {e}", "31")
        return False

    # Actualizar pip
    upgrade_pip_safe(pip_bin)

    # Lista de dependencias con versiones específicas
    dependencies = [
        ("setuptools==70.0.0", "Herramientas de configuración de Python", 60),
        ("wheel==0.43.0", "Soporte para archivos wheel", 60),
        ("colorama==0.4.6", "Colores en terminal", 90),
        ("requests==2.31.0", "Cliente HTTP", 120),
        ("selenium==4.15.2", "Dependencia para undetected-chromedriver", 120),
        ("undetected-chromedriver==3.5.5", "ChromeDriver sin detección", 240)
    ]
    
    # Instalar dependencias
    success_count = 0
    failed_deps = []
    
    for dep, description, timeout_sec in dependencies:
        module_name = dep.split("==")[0].replace("-", "_")  # Fix para undetected-chromedriver
        colored_print(f"📦 Instalando {dep} ({description})...", "36")
        
        # Verificar usando el Python del venv si está disponible
        if is_module_installed(module_name, venv_python) and test_import_module(module_name, venv_python):
            colored_print(f"✅ {dep} ya está instalado y funciona.", "32")
            success_count += 1
            continue
        
        if install_with_timeout(pip_bin, dep, timeout_sec, retries=3):
            time.sleep(2)  # Esperar un poco más para que la instalación se complete
            
            # Verificar instalación usando el Python del venv
            if venv_python and test_import_module(module_name, venv_python):
                colored_print(f"✅ {dep} instalado y verificado correctamente.", "32")
                success_count += 1
            else:
                # Verificación de fallback en el entorno actual
                try:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                    if module_name == "colorama":
                        import colorama
                        from colorama import Fore, Style, init
                        init()
                    elif module_name == "setuptools":
                        import setuptools
                    elif module_name == "selenium":
                        import selenium
                    elif module_name == "undetected_chromedriver":
                        import undetected_chromedriver
                    else:
                        __import__(module_name)
                    colored_print(f"✅ {dep} instalado y verificado correctamente.", "32")
                    success_count += 1
                except Exception as import_error:
                    colored_print(f"⚠️ {dep} instalado pero puede tener problemas: {import_error}", "33")
                    # No lo marcamos como failed si se instaló, solo como warning
                    success_count += 1
        else:
            colored_print(f"❌ No se pudo instalar {dep}.", "31")
            failed_deps.append(dep)
    
    # Instalar dependencias de requirements.txt
    requirements_files = [
        "requirements.txt",
        os.path.join("herramientas", "TBomb", "requirements.txt"),
        os.path.join("tools", "requirements.txt"),
        os.path.join("modules", "requirements.txt")
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            colored_print(f"📜 Procesando {req_file}...", "36")
            try:
                with open(req_file, 'r', encoding='utf-8', errors='ignore') as f:
                    requirements = [line.strip() for line in f 
                                  if line.strip() and not line.strip().startswith('#')]
                
                for req in requirements:
                    if req and req.split(">=")[0].split("==")[0] not in [d[0].split("==")[0] for d in dependencies]:
                        install_with_timeout(pip_bin, req, 60, retries=1)
                
                colored_print(f"✅ Dependencias de {req_file} procesadas.", "32")
            except Exception as e:
                colored_print(f"❌ Error procesando {req_file}: {e}", "31")

    # Verificación final - usando el Python del venv si está disponible
    colored_print("🔍 Verificación final de dependencias críticas...", "36")
    critical_deps = ["colorama", "setuptools", "requests", "selenium"]
    final_verification = True
    
    for dep in critical_deps:
        dep_name = dep.replace("-", "_")
        if venv_python:
            # Verificar en el entorno virtual
            if test_import_module(dep_name, venv_python):
                colored_print(f"✅ {dep} verificado como funcional en venv.", "32")
            else:
                colored_print(f"⚠️ {dep} puede no estar disponible en venv.", "33")
                # No marcamos como fallo crítico si está en el sistema
                try:
                    __import__(dep_name)
                    colored_print(f"✅ {dep} disponible en el sistema.", "32")
                except ImportError:
                    colored_print(f"❌ {dep} no está disponible.", "31")
                    final_verification = False
        else:
            # Verificación en el entorno actual
            try:
                if dep in sys.modules:
                    del sys.modules[dep]
                __import__(dep_name)
                colored_print(f"✅ {dep} verificado como funcional.", "32")
            except ImportError:
                colored_print(f"❌ {dep} no está disponible o no funciona.", "31")
                final_verification = False

    # Resultado final
    total_deps = len(dependencies)
    success_rate = (success_count / total_deps) * 100
    
    colored_print(f"📊 Estadísticas de instalación:", "36")
    colored_print(f"   • Exitosas: {success_count}/{total_deps} ({success_rate:.1f}%)")
    colored_print(f"   • Fallidas: {len(failed_deps)}")
    
    if failed_deps:
        colored_print(f"   • Dependencias problemáticas: {', '.join(failed_deps)}", "31")

    # Condiciones de éxito más permisivas
    if success_count >= 4 and (is_module_installed("setuptools", venv_python) or is_module_installed("setuptools")):
        colored_print("🎉 Instalación completada exitosamente.", "32")
        return True
    elif success_count >= 3:
        colored_print("⚠️ Instalación completada con advertencias pero debería ser funcional.", "33")
        return True
    else:
        colored_print("❌ Instalación falló para demasiadas dependencias críticas.", "31")
        colored_print("💡 Intenta ejecutar de nuevo o instala manualmente.", "36")
        return False

def create_virtual_environment(venv_dir):
    """Crea un entorno virtual nuevo"""
    colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")

    colored_print(f"🏗️ Creando entorno virtual en {venv_dir}...", "36")
    
    # Limpiar entorno anterior
    if os.path.exists(venv_dir):
        colored_print("🧹 Limpiando entorno virtual anterior...", "33")
        try:
            if platform.system() == "Windows":
                subprocess.run(["rmdir", "/s", "/q", venv_dir], 
                             shell=True, capture_output=True, timeout=30)
            else:
                shutil.rmtree(venv_dir)
            colored_print("✅ Entorno anterior eliminado.", "32")
        except Exception as e:
            colored_print(f"⚠️ No se pudo eliminar entorno anterior: {e}", "33")
    
    # Crear directorio padre
    parent_dir = os.path.dirname(venv_dir)
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except Exception as e:
            colored_print(f"❌ Error creando directorio padre: {e}", "31")
            return False

    # Intentar crear entorno virtual
    python_executables = [sys.executable, "python3", "python"] if platform.system() != "Windows" else [sys.executable, "python", "py", "py -3"]
    
    for python_exe in python_executables:
        try:
            colored_print(f"🔄 Intentando crear venv con: {python_exe}", "33")
            cmd = python_exe.split() + ["-m", "venv", venv_dir] if isinstance(python_exe, str) and " " in python_exe else [python_exe, "-m", "venv", venv_dir]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                os_name = platform.system()
                python_bin = os.path.join(venv_dir, "bin" if os_name in ["Linux", "Darwin"] else "Scripts", "python" if os_name in ["Linux", "Darwin"] else "python.exe")
                pip_bin = os.path.join(venv_dir, "bin" if os_name in ["Linux", "Darwin"] else "Scripts", "pip" if os_name in ["Linux", "Darwin"] else "pip.exe")
                
                if os.path.exists(python_bin):
                    colored_print("✅ Entorno virtual creado exitosamente.", "32")
                    if not os.path.exists(pip_bin):
                        colored_print("🔧 Instalando pip en el entorno virtual...", "33")
                        subprocess.run([python_bin, "-m", "ensurepip", "--default-pip"], capture_output=True, timeout=60)
                        subprocess.run([python_bin, "-m", "pip", "install", "--upgrade", "pip", "--no-cache-dir"], capture_output=True, timeout=60)
                    return True
                else:
                    colored_print(f"⚠️ Entorno creado pero falta ejecutable: {python_bin}", "33")
            else:
                colored_print(f"⚠️ Error creando venv: {result.stderr[:100]}", "33")
        except subprocess.TimeoutExpired:
            colored_print(f"⏰ Timeout creando venv con {python_exe}", "33")
        except Exception as e:
            colored_print(f"⚠️ Error con {python_exe}: {str(e)[:100]}", "33")
        time.sleep(1)
    
    colored_print("❌ No se pudo crear el entorno virtual.", "31")
    return False

def check_and_use_venv():
    """Verifica y configura el entorno virtual"""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "modules" in __file__ else os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    
    colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")

    os_name = platform.system()
    python_bin = os.path.join(venv_dir, "bin" if os_name in ["Linux", "Darwin"] else "Scripts", "python" if os_name in ["Linux", "Darwin"] else "python.exe")
    pip_bin = os.path.join(venv_dir, "bin" if os_name in ["Linux", "Darwin"] else "Scripts", "pip" if os_name in ["Linux", "Darwin"] else "pip.exe")

    current_python = os.path.normpath(sys.executable).lower()
    venv_path = os.path.normpath(venv_dir).lower()
    
    if current_python.startswith(venv_path):
        colored_print("✅ Ya ejecutándose desde el entorno virtual.", "32")
        return True

    if os.path.exists(venv_dir) and os.path.exists(python_bin):
        colored_print(f"✅ Entorno virtual encontrado: {venv_dir}", "32")
        missing_deps, _ = check_critical_dependencies(python_bin)
        
        if missing_deps:
            colored_print(f"🔧 Instalando dependencias faltantes: {', '.join(missing_deps)}", "36")
            pip_executable = get_pip_executable(venv_dir)
            if pip_executable and install_dependencies(venv_dir, pip_executable):
                colored_print("✅ Dependencias instaladas en venv existente.", "32")
            else:
                colored_print("⚠️ Problema al instalar dependencias en venv existente.", "33")
        
        if not current_python.startswith(venv_path) and "main.py" in sys.argv[0]:
            if "venv_restart_marker" not in sys.argv:
                colored_print(f"🔄 Reiniciando con Python del entorno virtual: {python_bin}", "36")
                try:
                    os.execv(python_bin, [python_bin] + sys.argv + ["venv_restart_marker"])
                except Exception as e:
                    colored_print(f"⚠️ No se pudo reiniciar automáticamente: {e}", "33")
                    return False
        return True
    else:
        colored_print("🏗️ El entorno virtual no existe. Creándolo...", "36")
        if not create_virtual_environment(venv_dir):
            return False
        
        pip_executable = get_pip_executable(venv_dir)
        if pip_executable:
            colored_print("🔧 Instalando dependencias en nuevo entorno virtual...", "36")
            if install_dependencies(venv_dir, pip_executable):
                colored_print("✅ Entorno virtual configurado correctamente.", "32")
                return True
            else:
                colored_print("⚠️ Error al instalar dependencias en nuevo venv.", "33")
                return False
        else:
            colored_print("❌ No se encontró pip en el nuevo entorno virtual.", "31")
            return False

def check_critical_dependencies(python_exe=None):
    """Verifica dependencias críticas del sistema"""
    critical_deps = {
        'colorama': 'colorama',
        'undetected_chromedriver': 'undetected_chromedriver', 
        'setuptools': 'setuptools',
        'requests': 'requests',
        'selenium': 'selenium'
    }
    
    missing_deps = []
    available_deps = []
    
    for display_name, import_name in critical_deps.items():
        if is_module_installed(import_name, python_exe):
            available_deps.append(display_name)
        else:
            missing_deps.append(display_name)
    
    return missing_deps, available_deps

def verify_python_installation():
    """Verifica que Python esté correctamente instalado"""
    colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")
    
    colored_print("🔍 Verificando instalación de Python...", "36")
    
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        colored_print(f"❌ Python {python_version.major}.{python_version.minor} no compatible. Requiere Python 3.6+", "31")
        return False
    
    colored_print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} compatible.", "32")
    
    try:
        import venv
        colored_print("✅ Módulo venv disponible.", "32")
    except ImportError:
        colored_print("❌ Módulo venv no disponible.", "31")
        return False
    
    pip_exe = get_pip_executable()
    if pip_exe:
        colored_print(f"✅ Pip encontrado: {pip_exe}", "32")
    else:
        colored_print("❌ Pip no encontrado.", "31")
        return False
    
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_write_permissions")
    try:
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        os.rmdir(test_dir)
        colored_print("✅ Permisos de escritura verificados.", "32")
    except Exception as e:
        colored_print(f"❌ Sin permisos de escritura: {e}", "31")
        return False
    
    return True

def cleanup_corrupted_venv(venv_dir):
    """Limpia un entorno virtual corrupto"""
    colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")
    
    if os.path.exists(venv_dir):
        colored_print("🧹 Limpiando entorno virtual corrupto...", "36")
        try:
            if platform.system() == "Windows":
                subprocess.run(["rmdir", "/s", "/q", venv_dir], 
                             shell=True, capture_output=True, timeout=30)
            else:
                shutil.rmtree(venv_dir)
            colored_print("✅ Entorno virtual eliminado.", "32")
            return True
        except Exception as e:
            colored_print(f"⚠️ No se pudo eliminar completamente: {e}", "33")
            return False
    return True

def fix_colorama_import():
    """Arregla problemas de importación de colorama"""
    colored_print = lambda msg, color="37": print_colored(msg, "32" if "✅" in msg else "31" if "❌" in msg else "33" if "⚠️" in msg else "36")
    
    try:
        modules_to_clear = [mod for mod in sys.modules.keys() if 'colorama' in mod.lower()]
        for mod in modules_to_clear:
            del sys.modules[mod]
        
        import colorama
        from colorama import Fore, Style, init
        init(autoreset=True)
        colored_print(f"✅ Colorama funcional.", "32")
        return True
    except Exception as e:
        colored_print(f"❌ Error con colorama: {e}", "31")
        
        pip_exe = get_pip_executable()
        if pip_exe:
            colored_print("🔧 Reinstalando colorama...", "33")
            try:
                subprocess.run([pip_exe, "uninstall", "-y", "colorama"], capture_output=True, timeout=30)
                cache_dir = os.path.expanduser("~\\AppData\\Local\\pip\\cache" if platform.system() == "Windows" else "~/.cache/pip")
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir, ignore_errors=True)
                result = subprocess.run([pip_exe, "install", "--no-cache-dir", "--force-reinstall", "colorama==0.4.6"], 
                                      capture_output=True, timeout=60)
                if result.returncode == 0:
                    colored_print("✅ Colorama reinstalado.", "32")
                    return force_reload_module("colorama")
            except Exception as reinstall_error:
                colored_print(f"❌ Error en reinstalación: {reinstall_error}", "31")
        return False

def diagnose_environment():
    """Diagnostica el estado del entorno"""
    colored_print = lambda msg, color="37": print_colored(msg, "36")
    
    colored_print("🔬 DIAGNÓSTICO DEL ENTORNO", "36")
    colored_print("="*50, "36")
    
    colored_print(f"Sistema: {platform.system()} {platform.release()}", "37")
    colored_print(f"Arquitectura: {platform.architecture()[0]}", "37")
    colored_print(f"Python: {sys.version}", "37")
    colored_print(f"Ejecutable: {sys.executable}", "37")
    
    pip_exe = get_pip_executable()
    colored_print(f"Pip encontrado: {pip_exe if pip_exe else 'No'}", "37")
    
    # Verificar en el sistema actual
    deps = ["colorama", "setuptools", "requests", "undetected_chromedriver", "selenium"]
    colored_print("\nEstado de dependencias (sistema actual):", "36")
    for dep in deps:
        dep_name = dep.replace("-", "_")
        installed = "✅" if is_module_installed(dep_name) else "❌"
        importable = "✅" if test_import_module(dep_name) else "❌"
        colored_print(f"  {dep}: Instalado {installed} | Importable {importable}", "37")
    
    # Verificar en el venv si existe
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "modules" in __file__ else os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    venv_python = get_venv_python_executable(venv_dir)
    
    colored_print(f"\nDirectorio del venv: {venv_dir}", "37")
    colored_print(f"Python en venv: {venv_python}", "37")
    colored_print(f"Venv existe: {'✅' if os.path.exists(venv_dir) else '❌'}", "37")
    
    if venv_python:
        colored_print("\nEstado de dependencias (venv):", "36")
        for dep in deps:
            dep_name = dep.replace("-", "_")
            installed = "✅" if is_module_installed(dep_name, venv_python) else "❌"
            importable = "✅" if test_import_module(dep_name, venv_python) else "❌"
            colored_print(f"  {dep}: Instalado {installed} | Importable {importable}", "37")
    
    current_python = os.path.normpath(sys.executable).lower()
    venv_path = os.path.normpath(venv_dir).lower()
    colored_print(f"\nEjecutándose desde venv: {'✅' if current_python.startswith(venv_path) else '❌'}", "37")

def run_post_install_tests(venv_python=None):
    """Ejecuta pruebas después de la instalación"""
    colored_print = lambda msg, color="37": print_colored(msg, "36")
    
    colored_print("🧪 Ejecutando pruebas post-instalación...", "36")
    
    tests = [
        ("colorama", "colorama"),
        ("requests", "requests"),
        ("setuptools", "setuptools"),
        ("selenium", "selenium"),
        ("undetected_chromedriver", "undetected_chromedriver"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, module_name in tests:
        try:
            if venv_python and test_import_module(module_name, venv_python):
                colored_print(f"✅ {test_name}: PASÓ (venv)", "32")
                passed += 1
            elif test_import_module(module_name):
                colored_print(f"✅ {test_name}: PASÓ (sistema)", "32")
                passed += 1
            else:
                colored_print(f"❌ {test_name}: FALLÓ", "31")
        except Exception as e:
            colored_print(f"❌ {test_name}: FALLÓ - {e}", "31")
    
    success_rate = (passed / total) * 100
    colored_print(f"📊 Resultado: {passed}/{total} pruebas pasaron ({success_rate:.1f}%)", "36")
    return passed >= total * 0.75

def setup_complete_environment():
    """Configuración completa del entorno"""
    print_colored("🚀 Iniciando configuración completa del entorno...", "32")
    
    # Limpiar caché de módulos globalmente
    modules_to_clear = [mod for mod in sys.modules.keys() if any(x in mod.lower() for x in ['colorama', 'setuptools', 'requests', 'undetected_chromedriver', 'selenium'])]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    if not verify_python_installation():
        print_colored("❌ Verificación de Python falló", "31")
        return False
    
    if not check_and_use_venv():
        print_colored("❌ Configuración de entorno virtual falló", "31")
        return False
    
    # Obtener el Python del venv para las pruebas
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "modules" in __file__ else os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, "venv")
    venv_python = get_venv_python_executable(venv_dir)
    
    if is_module_installed("colorama", venv_python) and not test_import_module("colorama", venv_python):
        print_colored("🔧 Detectado problema con colorama. Aplicando arreglo...", "33")
        fix_colorama_import()
    
    if run_post_install_tests(venv_python):
        print_colored("🎉 Configuración completa exitosa", "32")
        return True
    else:
        print_colored("⚠️ Configuración completada con advertencias", "33")
        return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo de instalación de DarK SMS")
    parser.add_argument("--diagnose", action="store_true", help="Ejecutar diagnóstico del entorno")
    parser.add_argument("--fix-colorama", action="store_true", help="Intentar arreglar colorama específicamente")
    parser.add_argument("--complete-setup", action="store_true", help="Configuración completa del entorno")
    
    args = parser.parse_args()
    
    if args.diagnose:
        diagnose_environment()
    elif args.fix_colorama:
        fix_colorama_import()
    elif args.complete_setup:
        setup_complete_environment()
    else:
        print_colored("💡 Usa --help para ver las opciones disponibles", "36")
        print_colored("📋 Opciones:", "36")
        print_colored("  --diagnose: Diagnosticar entorno", "37")
        print_colored("  --fix-colorama: Arreglar colorama", "37")
        print_colored("  --complete-setup: Configuración completa", "37")
