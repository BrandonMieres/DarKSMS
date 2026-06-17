import { app, BrowserWindow, ipcMain } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import fs from 'node:fs'
import os from 'node:os'
import { runAutomation, closeAutomation, requestCancelAutomation, findChromePath } from './automation'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

process.env.APP_ROOT = path.join(__dirname, '..')

export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL
  ? path.join(process.env.APP_ROOT, 'public')
  : RENDERER_DIST

let win: BrowserWindow | null

function getPreloadPath(): string {
  // vite-plugin-electron puede generar .js o .mjs dependiendo de la config
  const candidates = [
    path.join(__dirname, 'preload.js'),
    path.join(__dirname, 'preload.mjs'),
  ]
  for (const p of candidates) {
    if (fs.existsSync(p)) return p
  }
  // fallback
  return path.join(__dirname, 'preload.js')
}

// IPC handler para iniciar la automatización
ipcMain.handle('start-automation', async (_event, urls: string[], browserPath?: string) => {
  try {
    if (win) await runAutomation(win, urls, browserPath)
  } catch (err) {
    console.error('[ERROR] en start-automation:', err)
    if (win) win.webContents.send('automation-end')
  }
})

// Endpoint para comprobar el sistema antes de cargar
ipcMain.handle('check-system', () => {
  const chromePath = findChromePath()
  return {
    os: os.platform(),
    chromeFound: !!chromePath,
    chromePath: chromePath
  }
})

// Limpiar listeners antiguos por si Vite recarga en caliente (HMR)
ipcMain.removeAllListeners('start-automation');
ipcMain.removeAllListeners('cancel-automation');
ipcMain.removeAllListeners('win-minimize');
ipcMain.removeAllListeners('win-maximize');
ipcMain.removeAllListeners('win-close');

// IPC handler para cancelar la automatizaci\u00f3n en curso
ipcMain.handle('cancel-automation', () => {
  requestCancelAutomation();
})

// IPC handlers para controlar la ventana desde React
ipcMain.on('win-minimize', () => {
  const target = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
  if (target) target.minimize();
});
ipcMain.on('win-maximize', () => {
  const target = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
  if (target) {
    if (target.isMaximized()) target.unmaximize();
    else target.maximize();
  }
});
ipcMain.on('win-close', () => {
  const target = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
  if (target) target.close();
});

function createWindow() {
  const preloadPath = getPreloadPath();
  console.log('[INFO] Preload path:', preloadPath);
  
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC || '', 'icono.ico'),
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: preloadPath,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
    frame: false,
    titleBarStyle: 'hidden',
    autoHideMenuBar: true,
    alwaysOnTop: true,
    backgroundColor: '#050a05',
    title: 'DarK SMS',
  })

  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', new Date().toLocaleString())
  })

  // En dev abre DevTools para ver errores
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }

  // Interceptar el cierre para limpiar recursos (browser de Puppeteer)
  let isClosing = false
  win.on('close', (e) => {
    if (isClosing) return
    e.preventDefault()
    isClosing = true
    closeAutomation().finally(() => {
      win?.destroy()
    })
  })

  win.on('closed', () => {
    win = null
  })
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(createWindow)
