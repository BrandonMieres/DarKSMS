import undetected_chromedriver as uc
import random
import time
import os
from colorama import Fore

# Colores
rojo = '\033[31m'
verde = '\033[32m'
azul = '\033[34m'
cierre = '\033[39m'

# Lista de URLs a abrir
urls = [
    'https://www.instagram.com/accounts/password/reset/',
    'https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0',
    'https://www.paypal.com/es/welcome/signup/#/mobile_conf',
    'https://passport.yandex.com/auth?retpath=%2F%2Fyandex.com%2Fsupport%2Fid%2Fauthorization%2Fphone-number.html',
    'https://web.telegram.org/k/',
    'https://www.tiktok.com/signup/phone-or-email?redirect_url=https%3A%2F%2Fwww.tiktok.com%2Fupload%3Flang%3Des&lang=es',
    'https://help.steampowered.com/es/wizard/HelpWithLoginInfo?issueid=406',
    'https://account.live.com/username/recover?wreply=https://login.live.com/login.srf%3flc%3d3082%26mkt%3dES-ES%26wa%3dwsignin1.0%26rpsnv%3d13%26ct%3d1666198253%26rver%3d7.0.6737.0%26wp%3dMBI_SSL%26wreply%3dhttps%253a%252f%252foutlook.live.com%252fowa%252f0%252f%253fstate%253d1%2526redirectTo%253daHR0cHM6Ly9vdXRsb29rLmxpdmUuY29tL21haWwvMC8%2526RpsCsrfState%253df0538ed8-93f0-d07e-bf5a-7a46544e907d%26id%3d292841%26aadredir%3d1%26whr%3drevtxt.com%26CBCXT%3dout%26lw%3d1%26fl%3ddob%252cflname%252cwld%26cobrandid%3d90015%26contextid%3d5015B1DD9156F9A2%26bk%3d1666198254%26uaid%3d3969d24881894986a209dd5917148ab9&id=292841&cobrandid=90015&mkt=ES-ES&lc=3082&uaid=3969d24881894986a209dd5917148ab9&uiflavor=web',
    'https://tinder.com/es-ES',
    'https://badoo.com/landing',
    'https://id.vk.com/auth?app_id=7733222&response_type=silent_token&v=1.60.0&redirect_uri=https%3A%2F%2Fyoula.ru%2F&uuid=Albm6l5p2NTldu5afUCZh&redirect_state=vk-connect-auth-redirect&app_settings=eyJ2a2NfYmVoYXZpb3IiOiJ3aXRob3V0X3Bob25lIiwic2VydmljZV9ncm91cHMiOnsiZnVsbF9hdXRoX3ZpYV92a2Nvbm5lY3QiOiJleHAifSwiZXh0ZXJuYWxfZGV2aWNlX2lkIjoiNjRmNTNmMTM0YWNhNiJ9',
    'https://cloud.mail.ru',
    'https://oferta.vodafone.es/vodafone-one/?cid=1938872349:dt-20190501:cp-vdf_tol_continuidad:cn-sem:kw-13038396:cc-:cl-no_cliente:sp-Google:cr-:gk-marca:st-prospecting:ta-base:md-marca:ds-responsive:pr-blended:wn-tol:pl-/VDF-TOL-BrandPura-Def-BASEPC&gad=1&gclid=CjwKCAjw3dCnBhBCEiwAVvLcu0H8WOPPtSdwicQo0FH7g4yJ5uRQtO3oX1B7PegELZxDZmBPxtO6PxoCdTsQAvD_BwE',
    'https://www.finetwork.com/tarifas-movil?utm_campaign=8704888074&g_id=89205114442&utm_source=google&utm_term=compañias%20moviles%20españa&p_n=&utm_medium=paid_search&gad=1&gclid=CjwKCAjw3dCnBhBCEiwAVvLcu0ArRPJ92wEsEfiR7QNa13AWkbh7_kmumSquXDQhG1S47WwjRzGrGBoCzkUQAvD_BwE&gclsrc=aw.ds&adfcd=1693796996.LEq1fimdGkumeyMoC2Ludg.MjA4NTM5Niw3NzI1NjQ',
    'https://www.avatel.es/fibra/?gclid=CjwKCAjw3dCnBhBCEiwAVvLcu6z1ChJ3S-zAP9qcOx1LdtU9-0afNxm07Bz1AtH1xjI9c5R0WfuZ8BoCCKQQAvD_BwE'
]

def load_user_agents():
    """Carga los User-Agents desde el archivo ua.txt"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ua_file_path = os.path.join(script_dir, 'ua.txt')
        
        with open(ua_file_path, 'r', encoding='utf-8') as file:
            user_agents = [line.strip() for line in file if line.strip() and not line.startswith('http')]
        
        if not user_agents:
            print(rojo + "Error: El archivo ua.txt está vacío o no contiene User-Agents válidos." + cierre)
            return None
        
        print(verde + f"Cargados {len(user_agents)} User-Agents desde ua.txt" + cierre)
        return user_agents
    
    except FileNotFoundError:
        print(rojo + "Error: No se encontró el archivo ua.txt en la carpeta modules." + cierre)
        print(azul + "Continuando con User-Agent por defecto..." + cierre)
        return None
    except Exception as e:
        print(rojo + f"Error al leer ua.txt: {str(e)}" + cierre)
        print(azul + "Continuando con User-Agent por defecto..." + cierre)
        return None

def create_chrome_options(user_agent=None):
    """Crea una nueva instancia de ChromeOptions con la configuración necesaria"""
    options = uc.ChromeOptions()
    
    # Configuraciones básicas
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    
    # CRUCIAL: Desactivar bloqueador de popups para permitir nuevas pestañas
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Configurar User-Agent si se proporciona
    if user_agent:
        options.add_argument(f'--user-agent={user_agent}')
    
    return options

def setup_chrome_driver(user_agent=None):
    """Configura y retorna una instancia de Chrome driver"""
    print(azul + "Conectando con Chrome versión 138..." + cierre)
    
    try:
        options = create_chrome_options(user_agent)
        driver = uc.Chrome(options=options, version_main=138)
        print(verde + "¡Conexión exitosa!" + cierre)
        return driver
    except Exception as e:
        print(rojo + f"Error al conectar: {str(e)[:100]}..." + cierre)
        print(azul + "Soluciones:" + cierre)
        print(azul + "• Cierra todas las ventanas de Chrome" + cierre)
        print(azul + "• Actualiza: pip install --upgrade undetected-chromedriver" + cierre)
        return None

def open_tabs():
    """Función principal para abrir todas las URLs en pestañas separadas"""
    print(rojo + "Nota: No funciona con números virtuales." + cierre)
    print(azul + "Preparando para abrir todas las páginas en Google Chrome..." + cierre)
    
    # Cargar User-Agents
    user_agents = load_user_agents()
    selected_user_agent = random.choice(user_agents) if user_agents else None
    
    if selected_user_agent:
        print(verde + f"Usando User-Agent aleatorio: {selected_user_agent[:50]}..." + cierre)
    
    time.sleep(1)
    
    # Configurar Chrome driver
    driver = setup_chrome_driver(selected_user_agent)
    if not driver:
        print(rojo + "\nNo se pudo inicializar Chrome. Posibles soluciones:" + cierre)
        print(azul + "• Actualiza Chrome a la última versión" + cierre)
        print(azul + "• Actualiza undetected-chromedriver: pip install --upgrade undetected-chromedriver" + cierre)
        print(azul + "• Cierra todas las ventanas de Chrome antes de ejecutar" + cierre)
        print(azul + "• Reinicia tu sistema si el problema persiste" + cierre)
        input("\nPresiona Enter para volver al menú.")
        return
    
    try:
        print(verde + "¡Chrome iniciado correctamente!" + cierre)
        print(azul + f"Proceso: Abrir {len(urls)} páginas en pestañas separadas" + cierre)
        
        # Abrir la primera URL en la pestaña actual
        print(f"[1/{len(urls)}] Cargando en pestaña inicial: {urls[0][:60]}...")
        driver.get(urls[0])
        print(f"   ✓ Cargada en pestaña 1")
        time.sleep(2)
        
        # Verificar pestañas iniciales
        initial_tabs = len(driver.window_handles)
        print(verde + f"Pestaña inicial lista. Comenzando a crear nuevas pestañas..." + cierre)
        
        # Abrir las demás URLs en nuevas pestañas
        for i, url in enumerate(urls[1:], 1):
            try:
                print(f"[{i + 1}/{len(urls)}] Creando nueva pestaña para: {url[:60]}...")
                
                # Método 1: Usar window.open con target específico
                tab_name = f"tab_{i+1}"
                driver.execute_script(f"window.open('{url}', '{tab_name}');")
                
                # Esperar y verificar
                time.sleep(2.5)
                current_tabs = len(driver.window_handles)
                
                if current_tabs > i:
                    # ¡Éxito! Se creó la nueva pestaña
                    driver.switch_to.window(driver.window_handles[-1])
                    print(f"   ✓ Nueva pestaña creada - Total: {current_tabs}")
                else:
                    # Si no funciona, usar método alternativo con Selenium
                    print(f"   → Usando método alternativo...")
                    
                    # Método 2: Simular Ctrl+T con ActionChains
                    from selenium.webdriver.common.keys import Keys
                    from selenium.webdriver.common.action_chains import ActionChains
                    
                    # Crear nueva pestaña con shortcut
                    body = driver.find_element("tag name", "body")
                    body.send_keys(Keys.CONTROL + "t")
                    
                    # Esperar y verificar nueva pestaña
                    time.sleep(1.5)
                    current_tabs = len(driver.window_handles)
                    
                    if current_tabs > i:
                        # Cambiar a la nueva pestaña y navegar
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.get(url)
                        print(f"   ✓ Pestaña creada con Ctrl+T - Total: {current_tabs}")
                    else:
                        print(rojo + f"   ✗ No se pudo crear pestaña nueva" + cierre)
                
            except Exception as e:
                print(rojo + f"   ✗ Error: {str(e)[:50]}..." + cierre)
                continue
        
        final_tab_count = len(driver.window_handles)
        print(verde + f"\n¡PROCESO COMPLETADO!" + cierre)
        print(verde + f"✓ Total de pestañas creadas: {final_tab_count}" + cierre)
        print(verde + f"✓ URLs procesadas: {len(urls)}" + cierre)
        
        if final_tab_count == len(urls):
            print(verde + "✓ Todas las páginas se abrieron correctamente en pestañas separadas" + cierre)
        else:
            print(rojo + f"⚠ Advertencia: Se esperaban {len(urls)} pestañas, pero hay {final_tab_count}" + cierre)
        
        print(azul + "\nNavegación entre pestañas:" + cierre)
        print(azul + "• Ctrl+Tab: Siguiente pestaña" + cierre)
        print(azul + "• Ctrl+Shift+Tab: Pestaña anterior" + cierre)
        print(azul + "• Ctrl+1,2,3...: Ir a pestaña específica" + cierre)
        print(azul + "• O simplemente haz clic en las pestañas" + cierre)
        
        input(verde + "\nPresiona Enter para cerrar todas las pestañas y volver al menú." + cierre)
        
    except KeyboardInterrupt:
        print(rojo + "\nOperación cancelada por el usuario." + cierre)
    except Exception as e:
        print(rojo + f"Error durante la ejecución: {str(e)}" + cierre)
        print(azul + "Algunas páginas pueden haberse abierto correctamente." + cierre)
    finally:
        try:
            driver.quit()
            print(verde + "Navegador cerrado correctamente." + cierre)
        except:
            print(azul + "El navegador se cerró automáticamente." + cierre)

if __name__ == "__main__":
    open_tabs()