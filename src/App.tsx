import { useState, useEffect, useRef } from 'react'
import {
  Play, SquareTerminal, Crosshair, AlertTriangle,
  Zap, Minus, Square, X, Settings, Plus, Trash2, Globe, CheckCircle2
} from 'lucide-react'
import './index.css'

import { INITIAL_URLS } from './data/defaultUrls'

const BROWSER_OPTIONS = [
  { id: 'auto',  label: 'Auto-detectar Chrome', path: '' },
  { id: 'edge',  label: 'Microsoft Edge',        path: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe' },
  { id: 'firefox', label: 'Mozilla Firefox',     path: 'C:\\Program Files\\Mozilla Firefox\\firefox.exe' },
  { id: 'custom', label: 'Ruta personalizada',   path: '' },
]

function getDomain(url: string) {
  try { return new URL(url).hostname.replace('www.', '') }
  catch { return url.substring(0, 30) }
}

function now() {
  return new Date().toLocaleTimeString('es-ES', { hour12: false })
}

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const v = localStorage.getItem(key)
    return v ? JSON.parse(v) : fallback
  } catch { return fallback }
}

interface LogEntry  { time: string; msg: string }
interface Progress  { current: number; total: number }

export default function App() {
  // ── Core state ────────────────────────────────────────────────
  const [logs, setLogs]       = useState<LogEntry[]>([{ time: now(), msg: '[SISTEMA] DarK SMS v2.0 inicializado. Listo para operar.' }])
  const [running, setRunning] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [progress, setProgress] = useState<Progress>({ current: 0, total: 0 })
  const [isAppLoaded, setIsAppLoaded] = useState(false)
  const terminalRef = useRef<HTMLDivElement>(null)

  // ── Settings state ────────────────────────────────────────────
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [activeTab, setActiveTab]       = useState<'urls' | 'browser'>('urls')
  // Solo las URLs EXTRA que añade el usuario (las de INITIAL_URLS son siempre fijas)
  const [userUrls, setUserUrls]         = useState<string[]>(() => loadFromStorage('dark_user_urls', []))
  const [newUrl, setNewUrl]             = useState('')
  const [browserId, setBrowserId]       = useState<string>(() => loadFromStorage('dark_browser_id', 'auto'))
  const [customPath, setCustomPath]     = useState<string>(() => loadFromStorage('dark_custom_path', ''))
  const [saveFlash, setSaveFlash]       = useState(false)

  // Lista completa = fijas + extras del usuario (sin duplicados)
  const allUrls = [...INITIAL_URLS, ...userUrls.filter(u => !INITIAL_URLS.includes(u))]

  const addLog = (msg: string) => setLogs(prev => [...prev, { time: now(), msg }])

  // ── Auto-scroll terminal ──────────────────────────────────────
  useEffect(() => {
    if (terminalRef.current)
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
  }, [logs])

  // ── IPC listeners ─────────────────────────────────────────────
  useEffect(() => {
    if (!window.electronAPI) return
    window.electronAPI.onAutomationLog(msg => addLog(msg))
    window.electronAPI.onAutomationProgress(p => setProgress(p))
    window.electronAPI.onAutomationComplete(() => {
      setRunning(false)
      addLog('[SISTEMA] [OK] Todas las pestanas abiertas. Completa los formularios manualmente.')
    })
    window.electronAPI.onAutomationEnd(() => {
      setRunning(false)
      setProgress({ current: 0, total: 0 })
      addLog('[SISTEMA] Sesion finalizada.')
    })
  }, [])

  // ── Splash Screen & System Check ──────────────────────────────
  const [splashProgress, setSplashProgress] = useState(0)
  
  useEffect(() => {
    let isMounted = true
    const checkEnv = async () => {
      // Avanzar barra artificialmente un poco
      if (isMounted) setSplashProgress(30)
      
      // Simular algo de tiempo para que la pantalla se vea (mínimo 1.5s)
      await new Promise(r => setTimeout(r, 1500))
      
      if (!window.electronAPI) {
        if (isMounted) {
          addLog('[ERROR CRÍTICO] Entorno Electron no detectado. Modo fallback.')
          setSplashProgress(100)
          setTimeout(() => setIsAppLoaded(true), 500)
        }
        return
      }

      if (isMounted) setSplashProgress(60)

      try {
        const sys = await window.electronAPI.checkSystem()
        if (isMounted) {
          setSplashProgress(90)
          addLog(`[SISTEMA] OS detectado: ${sys.os}`)
          if (sys.chromeFound) {
            addLog(`[SISTEMA] Navegador detectado en: ${sys.chromePath}`)
          } else {
            addLog('[WARN] No se detectó Chrome/Edge nativo. Configura la ruta manualmente.')
          }
          
          await new Promise(r => setTimeout(r, 600)) // Pausa para leer el log visualmente
          setSplashProgress(100)
          setTimeout(() => setIsAppLoaded(true), 400)
        }
      } catch (e) {
        if (isMounted) {
          addLog(`[ERROR] Falla en checkSystem: ${e}`)
          setSplashProgress(100)
          setTimeout(() => setIsAppLoaded(true), 500)
        }
      }
    }
    
    checkEnv()
    return () => { isMounted = false }
  }, [])

  // ── Persist settings ──────────────────────────────────────────
  useEffect(() => { localStorage.setItem('dark_user_urls', JSON.stringify(userUrls)) }, [userUrls])
  useEffect(() => { localStorage.setItem('dark_browser_id', JSON.stringify(browserId)) }, [browserId])
  useEffect(() => { localStorage.setItem('dark_custom_path', JSON.stringify(customPath)) }, [customPath])

  // ── Helpers: URL management ───────────────────────────────────
  const handleAddUrl = () => {
    const trimmed = newUrl.trim()
    if (!trimmed) return
    if (allUrls.includes(trimmed)) { setNewUrl(''); return }  // ya existe
    try { new URL(trimmed) } catch { addLog('[WARN] URL no valida: ' + trimmed); return }
    setUserUrls(prev => [...prev, trimmed])
    setNewUrl('')
    addLog('[SISTEMA] URL añadida: ' + getDomain(trimmed))
  }

  const handleDeleteUserUrl = (idx: number) => {
    const removed = getDomain(userUrls[idx])
    setUserUrls(prev => prev.filter((_, i) => i !== idx))
    addLog('[SISTEMA] URL eliminada: ' + removed)
  }

  // ── Launch ────────────────────────────────────────────────────
  const getBrowserPath = () => {
    if (browserId === 'auto') return ''
    if (browserId === 'custom') return customPath
    return BROWSER_OPTIONS.find(b => b.id === browserId)?.path ?? ''
  }

  const handleLaunch = () => {
    if (!window.electronAPI) { addLog('[ERROR] Entorno Electron no detectado.'); return }
    if (allUrls.length === 0) { addLog('[WARN] No hay URLs configuradas.'); return }
    setRunning(true)
    setCancelling(false)
    setProgress({ current: 0, total: allUrls.length })
    addLog('━'.repeat(44))
    addLog('[>>] INICIANDO SECUENCIA DE AUTOMATIZACION')
    addLog('━'.repeat(44))
    window.electronAPI.startAutomation(allUrls, getBrowserPath())
  }

  const handleCancel = () => {
    if (!window.electronAPI) return
    setCancelling(true)
    addLog('[INFO] Cancelación solicitada por el usuario...')
    window.electronAPI.cancelAutomation()
    // La card se cierra suavemente: la animación dura 400ms y luego ocultamos
    setTimeout(() => {
      setRunning(false)
      setCancelling(false)
    }, 450)
  }

  // ── Save & close settings ─────────────────────────────────────
  const handleSaveSettings = () => {
    setSaveFlash(true)
    setTimeout(() => { setSaveFlash(false); setSettingsOpen(false) }, 900)
  }

  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0

  if (!isAppLoaded) {
    return (
      <div className="splash-screen">
        <div className="splash-content">
          <div className="splash-logo">
            <img src="./icono.ico" width={64} height={64} alt="logo" style={{ filter: 'drop-shadow(0 0 10px var(--neon))' }} />
          </div>
          <h1 className="splash-title">DarK SMS <span className="version">v2.0</span></h1>
          <p className="splash-subtitle">
            {splashProgress < 50 ? 'Inicializando entorno de automatización...' :
             splashProgress < 90 ? 'Verificando dependencias del sistema...' :
             'Entorno listo. Cargando interfaz...'}
          </p>
          <div className="splash-loader">
            <div className="splash-loader-bar" style={{ width: `${splashProgress}%`, transition: 'width 0.3s ease', animation: 'none' }}></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">

      {/* ── PROGRESS MODAL ── */}
      {running && (
        <div className="modal-overlay">
          <div className={`modal-card glass${cancelling ? ' modal-card--exit' : ''}`}>
            <AlertTriangle size={44} color="#ff3333" />
            <h2 className="modal-title">Abriendo URLs...</h2>
            <div className="modal-warning">
              ⚠️&nbsp; POR FAVOR NO CIERRES ESTA APLICACIÓN MIENTRAS SE CARGAN LAS URLS &nbsp;⚠️
            </div>
            <div className="progress-label">
              <span>{progress.current} / {progress.total} URLs abiertas</span>
              <span>{pct}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${pct}%` }} />
            </div>
            <p className="progress-sites">
              {progress.current > 0
                ? <><span>Cargando: </span><strong>{getDomain(allUrls[progress.current - 1] ?? '')}</strong></>
                : 'Iniciando navegador...'}
            </p>
            <button
              id="btn-cancel-automation"
              className="btn-cancel"
              onClick={handleCancel}
              disabled={cancelling}
            >
              {cancelling ? 'Cancelando...' : '✖ Cancelar proceso'}
            </button>
          </div>
        </div>
      )}

      {/* ── SETTINGS DRAWER ── */}
      {settingsOpen && (
        <div className="settings-overlay">
          <div className="settings-drawer glass" onClick={e => e.stopPropagation()}>

            {/* Header */}
            <div className="settings-header">
              <div className="settings-title-row">
                <Settings size={15} color="var(--neon)" />
                <span className="settings-title">CONFIGURACION</span>
              </div>
              <button className="settings-close" onClick={() => setSettingsOpen(false)}>
                <X size={14} />
              </button>
            </div>

            {/* Tabs */}
            <div className="settings-tabs">
              <button
                className={`settings-tab ${activeTab === 'urls' ? 'active' : ''}`}
                onClick={() => setActiveTab('urls')}
              >
                <Globe size={13} /> URLs
              </button>
              <button
                className={`settings-tab ${activeTab === 'browser' ? 'active' : ''}`}
                onClick={() => setActiveTab('browser')}
              >
                <Globe size={13} /> Navegador
              </button>
            </div>

            {/* Tab: URLs */}
            {activeTab === 'urls' && (
              <div className="settings-body">

                {/* Info block */}
                <div className="info-block">
                  <p className="info-block-title">¿Qué URLs debo añadir?</p>
                  <p className="info-block-text">
                    Añade URLs de páginas de <strong>inicio de sesión</strong>, <strong>recuperación de cuenta</strong>
                    o <strong>registro</strong> de cualquier plataforma. La herramienta abrirá
                    todas a la vez en pestañas del navegador para que puedas rellenar los formularios.
                  </p>
                  <div className="info-block-rules">
                    <div className="info-rule ok">
                      <span className="info-rule-icon">✓</span>
                      <span>Debe empezar por <code>https://</code> o <code>http://</code></span>
                    </div>
                    <div className="info-rule ok">
                      <span className="info-rule-icon">✓</span>
                      <span>Páginas de login, registro o recuperación</span>
                    </div>
                    <div className="info-rule bad">
                      <span className="info-rule-icon">✗</span>
                      <span>No pongas solo el dominio: <code>google.es</code></span>
                    </div>
                    <div className="info-rule bad">
                      <span className="info-rule-icon">✗</span>
                      <span>No pongas páginas de inicio genéricas</span>
                    </div>
                  </div>
                  <p className="info-block-example">
                    Ejemplo válido:<br />
                    <code>https://www.instagram.com/accounts/password/reset/</code>
                  </p>
                </div>

                <p className="settings-label">URLs por defecto ({INITIAL_URLS.length}) + añadidas ({userUrls.length})</p>

                {/* Add URL */}
                <div className="url-add-row">
                  <input
                    className="url-input"
                    type="text"
                    placeholder="https://..."
                    value={newUrl}
                    onChange={e => setNewUrl(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleAddUrl()}
                  />
                  <button className="btn-add" onClick={handleAddUrl} title="Añadir URL">
                    <Plus size={15} />
                  </button>
                </div>

                {/* URL list — default (read-only) + user-added (deletable) */}
                <div className="url-list">
                  {/* Default URLs - no borrable */}
                  {INITIAL_URLS.map((url, i) => (
                    <div key={`d-${i}`} className="url-item url-item-default">
                      <span className="url-item-domain">{getDomain(url)}</span>
                      <span className="url-item-full" title={url}>{url.substring(0, 42)}{url.length > 42 ? '…' : ''}</span>
                      <span className="url-item-lock" title="URL por defecto">🔒</span>
                    </div>
                  ))}
                  {/* User-added URLs - borrables */}
                  {userUrls.map((url, i) => (
                    <div key={`u-${i}`} className="url-item">
                      <span className="url-item-domain">{getDomain(url)}</span>
                      <span className="url-item-full" title={url}>{url.substring(0, 42)}{url.length > 42 ? '…' : ''}</span>
                      <button
                        className="btn-delete"
                        onClick={() => handleDeleteUserUrl(i)}
                        title="Eliminar"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab: Browser */}
            {activeTab === 'browser' && (
              <div className="settings-body">
                <p className="settings-label">Navegador a usar</p>
                <div className="browser-options">
                  {BROWSER_OPTIONS.map(opt => (
                    <label key={opt.id} className={`browser-option ${browserId === opt.id ? 'selected' : ''}`}>
                      <input
                        type="radio"
                        name="browser"
                        value={opt.id}
                        checked={browserId === opt.id}
                        onChange={() => setBrowserId(opt.id)}
                      />
                      <span className="browser-option-label">{opt.label}</span>
                      {opt.id !== 'auto' && opt.id !== 'custom' && (
                        <span className="browser-option-path">{opt.path.split('\\').pop()}</span>
                      )}
                    </label>
                  ))}
                </div>

                {browserId === 'custom' && (
                  <div className="custom-path-row">
                    <p className="settings-label">Ruta del ejecutable</p>
                    <input
                      className="url-input"
                      type="text"
                      placeholder="C:\Program Files\...\browser.exe"
                      value={customPath}
                      onChange={e => setCustomPath(e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Save button */}
            <div className="settings-footer">
              <button className={`btn-save ${saveFlash ? 'saved' : ''}`} onClick={handleSaveSettings}>
                {saveFlash ? <><CheckCircle2 size={14} /> GUARDADO</> : 'GUARDAR Y CERRAR'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── TITLEBAR ── */}
      <div className="titlebar">
        <div className="titlebar-drag">
          <img src="./icono.ico" width={16} height={16} alt="logo" style={{ filter: 'drop-shadow(0 0 3px var(--neon))' }} />
          <span className="titlebar-name">DarK SMS</span>
          <span className="titlebar-version">v2.0</span>
        </div>

        <div className="titlebar-status no-drag">
          <div className={`status-dot ${running ? 'active' : 'ready'}`} />
          <span>{running ? 'EJECUTANDO...' : 'SISTEMA LISTO'}</span>
        </div>

        <div className="win-controls no-drag">
          {/* Gear settings button */}
          <button
            className="win-btn settings-gear"
            onClick={() => setSettingsOpen(s => !s)}
            title="Configuracion"
          >
            <Settings size={13} />
          </button>

          <button className="win-btn" onClick={() => window.electronAPI?.minimize()} title="Minimizar">
            <Minus size={12} />
          </button>
          <button className="win-btn" onClick={() => window.electronAPI?.maximize()} title="Maximizar">
            <Square size={11} />
          </button>
          <button className="win-btn close" onClick={() => window.electronAPI?.close()} title="Cerrar">
            <X size={13} />
          </button>
        </div>
      </div>

      {/* ── TOP AREA ── */}
      <div className="top-area">

        {/* Targets Panel */}
        <div className="targets-panel glass">
          <p className="panel-title">
            <Crosshair size={13} />
            Objetivos cargados — {allUrls.length} URLs
          </p>
          <div className="targets-grid">
            {allUrls.map((url, i) => (
              <span key={i} className="target-chip">{getDomain(url)}</span>
            ))}
          </div>
        </div>

        {/* Action Panel */}
        <div className="action-panel glass">
          <p className="url-count">
            <span>{allUrls.length}</span> URLs listas para ejecutar
          </p>
          <button className="btn-launch" onClick={handleLaunch} disabled={running}>
            {running
              ? <><Zap size={18} /> EN EJECUCIÓN...</>
              : <><Play size={18} /> ABRIR TODAS LAS URLs</>}
          </button>
          <p className="btn-hint">La ventana permanecerá siempre al frente.</p>
        </div>
      </div>

      {/* ── TERMINAL ── */}
      <section className="terminal-area glass">
        <p className="panel-title">
          <SquareTerminal size={13} />
          Logs del sistema
        </p>
        <div className="terminal-box" ref={terminalRef}>
          {logs.map((entry, i) => (
            <div key={i} className="log-line">
              <span className="log-time">[{entry.time}]</span>
              <span className="log-msg">{entry.msg}</span>
            </div>
          ))}
          {running && <span className="log-cursor">█</span>}
        </div>
      </section>
    </div>
  )
}
