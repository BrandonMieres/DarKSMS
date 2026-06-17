import puppeteer from 'puppeteer-extra';
import { MODERN_USER_AGENTS } from './userAgents';
import type { Browser } from 'puppeteer';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import { BrowserWindow } from 'electron';
import os from 'os';
import fs from 'fs';

let activeBrowser: Browser | null = null;
let cancelRequested = false;

// Add stealth plugin
puppeteer.use(StealthPlugin());

export function findChromePath(): string | undefined {
  const platform = os.platform();
  if (platform === 'win32') {
    const paths = [
      process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe',
      process.env.PROGRAMFILES + '\\Google\\Chrome\\Application\\chrome.exe',
      process.env['PROGRAMFILES(X86)'] + '\\Google\\Chrome\\Application\\chrome.exe'
    ];
    for (const p of paths) {
      if (fs.existsSync(p)) return p;
    }
  } else if (platform === 'darwin') {
    return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  } else if (platform === 'linux') {
    return '/usr/bin/google-chrome';
  }
  return undefined;
}

export async function runAutomation(mainWindow: BrowserWindow, urls: string[], browserPath?: string) {
  cancelRequested = false;
  
  const log = (msg: string) => {
    mainWindow.webContents.send('automation-log', msg);
    console.log(msg);
  };

  log('Iniciando proceso de automatización...');
  
  const executablePath = findChromePath();
  if (!executablePath && !browserPath) {
    log('[ERROR] No se pudo encontrar Google Chrome instalado en el sistema.');
    mainWindow.webContents.send('automation-end');
    return;
  }

  const finalPath = browserPath || executablePath!;
  log(`[OK] Usando navegador en: ${finalPath}`);

  try {
    const browser = await puppeteer.launch({
      executablePath: finalPath,
      headless: false,
      args: [
        '--start-maximized',
        '--disable-popup-blocking',
        '--disable-blink-features=AutomationControlled'
      ],
      defaultViewport: null
    });
    
    activeBrowser = browser;

    log('Navegador inicializado con evasion activada.');

    // Selección aleatoria de un UA moderno del pool de 100+
    const randomUA = MODERN_USER_AGENTS[Math.floor(Math.random() * MODERN_USER_AGENTS.length)];
    log(`[INFO] Usando User-Agent: ${randomUA.slice(0, 60)}...`);

    const pages = await browser.pages();
    const initialPage = pages.length > 0 ? pages[0] : await browser.newPage();
    await initialPage.setUserAgent(randomUA);

    log(`[1/${urls.length}] Cargando en pestana inicial: ${urls[0].substring(0, 40)}...`);
    mainWindow.webContents.send('automation-progress', { current: 1, total: urls.length });
    await initialPage.goto(urls[0], { waitUntil: 'domcontentloaded', timeout: 15000 });
    log(`   [OK] Cargada en pestana 1`);
    
    // Abrir el resto
    for (let i = 1; i < urls.length; i++) {
      // Comprobar cancelación antes de cada nueva pestaña
      if (cancelRequested) {
        log('[INFO] Cancelación solicitada — deteniendo proceso.');
        break;
      }
      await new Promise(r => setTimeout(r, 1500 + Math.random() * 1000));
      if (cancelRequested) break; // Comprobar también tras el delay
      log(`[${i + 1}/${urls.length}] Creando nueva pestana para: ${urls[i].substring(0, 40)}...`);
      mainWindow.webContents.send('automation-progress', { current: i + 1, total: urls.length });
      const newPage = await browser.newPage();
      await newPage.setUserAgent(randomUA);
      await newPage.goto(urls[i], { waitUntil: 'domcontentloaded', timeout: 15000 }).then(() => {
        log(`   [OK] Nueva pestana creada y cargada`);
      }).catch(e => {
        log(`   [WARN] Timeout o error cargando: ${e.message}`);
      });
    }

    if (cancelRequested) {
      cancelRequested = false;
      log('[INFO] Proceso cancelado por el usuario. Cerrando navegador...');
      await closeAutomation();
      mainWindow.webContents.send('automation-end');
      return;
    }

    // Registrar desconexión ANTES de enviar el complete
    browser.on('disconnected', () => {
      activeBrowser = null;
      log('Navegador cerrado por el usuario.');
      mainWindow.webContents.send('automation-end');
    });

    log('\n[OK] PROCESO COMPLETADO!');
    log('Las pestanas estan listas. Por favor completa los formularios manualmente.');
    log('El navegador no se cerrara automaticamente, cierralo cuando termines.');
    mainWindow.webContents.send('automation-complete'); // Señal de éxito

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    log(`[ERROR] Error durante la ejecucion: ${errorMsg}`);
    mainWindow.webContents.send('automation-end');
  }
}

export async function closeAutomation() {
  if (activeBrowser) {
    try {
      await activeBrowser.close();
      activeBrowser = null;
    } catch (e) {
      console.error('[ERROR] Error cerrando Puppeteer:', e);
    }
  }
}

export function requestCancelAutomation() {
  cancelRequested = true;
}
