<div align="center">
  <img src="public/icono.ico" alt="DarK SMS Logo" width="150">
  
  # ⚡ DarK SMS v2.0
  
  **Automatización Concurrente Avanzada con Evasión de Anti-Bots**

  ![Electron](https://img.shields.io/badge/Electron-34.1.1-191970?style=for-the-badge&logo=electron&logoColor=9FEAF9)
  ![React](https://img.shields.io/badge/React-19.2-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
  ![TypeScript](https://img.shields.io/badge/TypeScript-5.0-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
  ![Puppeteer](https://img.shields.io/badge/Puppeteer_Stealth-24.2-40B5A4?style=for-the-badge&logo=puppeteer&logoColor=white)
</div>

---

**DarK SMS** es una aplicación de escritorio diseñada para **automatizar la apertura concurrente de múltiples sitios web**. Con una interfaz moderna y agresiva estilo **Cyber-Glass Neon-Grid** (fondos oscuros, cuadrículas 3D, efectos de escáner y terminales CRT), la herramienta facilita y acelera los flujos de trabajo que requieren interactuar con formularios, páginas de inicio de sesión o portales de recuperación de cuentas de forma masiva. Todo esto, empaquetado en un ejecutable de Windows optimizado y listo para producción con iconos de alta resolución generados por hardware.

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

> [!CAUTION]
> **Esta herramienta ha sido creada estrictamente con fines EDUCATIVOS y de INVESTIGACIÓN DE SEGURIDAD.**
> 
> El desarrollador de esta aplicación no aprueba, apoya ni se hace responsable bajo ninguna circunstancia del mal uso que se le pueda dar a este software. El usuario asume **toda la responsabilidad legal y ética** de sus acciones al utilizar esta herramienta. Cualquier uso para acoso, spam, phishing o cualquier actividad ilícita está **terminantemente prohibido**.

---

## 🚀 Características y Funcionalidades

### 🛡️ Evasión de Anti-Bots Avanzada
- Incorpora `puppeteer-extra-plugin-stealth` para simular tráfico orgánico.
- **Pool masivo de User-Agents**: Más de 100 *User-Agents* modernos y actualizados (Chrome 114–123, Edge y variantes en Windows, macOS y Linux).
- Rotación aleatoria en cada ejecución para maximizar la invisibilidad frente a firewalls (Cloudflare, Akamai, etc).

### ⚡ Automatización Concurrente
- Despliega decenas de URLs en paralelo con una sola acción.
- Control de retrasos aleatorios (1.5s - 2.5s) entre aperturas para simular comportamiento humano.
- Cancelación de procesos en tiempo real con cierre limpio de instancias.

### 🎯 Gestión Dinámica de Objetivos
- Más de **25 URLs pre-configuradas** (las principales redes sociales y operadoras).
- Interfaz intuitiva para añadir, guardar y eliminar URLs personalizadas.
- **Persistencia local**: La aplicación recuerda tus URLs y configuraciones entre sesiones automáticamente.

### 🖥️ Interfaz Reactiva y Control
- **Terminal integrada en tiempo real** para visualizar los logs del sistema, estado de progreso y alertas.
- Selección dinámica de navegador: Usa auto-detección (Chrome nativo), navegadores específicos (Edge, Firefox) o establece una ruta de ejecutable personalizada.

---

## ⚙️ Requisitos del Sistema

- **Sistema Operativo**: Windows 10 / 11 (Soporte prioritario).
- **Dependencias Internas**: Node.js v18 o superior.
- **Navegador Web**: Google Chrome, Microsoft Edge o Mozilla Firefox instalado en el sistema.

---

## 🛠️ Instalación y Uso (Desarrollo)

Si deseas clonar el proyecto para estudiarlo o modificar su código:

1. **Clonar e instalar dependencias:**
   ```bash
   npm install
   ```

2. **Ejecutar en modo Desarrollo (Hot-Reloading):**
   ```bash
   npm run dev
   ```

3. **Compilar para Producción (Crear Instalador):**
   ```bash
   npm run build
   ```
   > [!TIP]
   > Una vez finalizada la compilación, encontrarás el instalador `.exe` autónomo y optimizado dentro de la carpeta `release/`.

---

## 💻 Stack Tecnológico

| Entorno | Tecnologías |
|---------|-------------|
| **Frontend** | React 19, TypeScript, Vite, Vanilla CSS (Glassmorphism & Neumorphism) |
| **Backend** | Electron (IPC Main/Renderer), Puppeteer Core |
| **Seguridad**| Puppeteer Stealth Plugin |
| **Build** | Electron Builder (NSIS Installer) |

<br>

<div align="center">
  <i>DarK SMS v2.0 — Coded with ♥ for educational purposes.</i>
</div>
