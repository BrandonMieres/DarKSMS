import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  startAutomation: (urls: string[], browserPath?: string) => ipcRenderer.invoke('start-automation', urls, browserPath),
  cancelAutomation: () => ipcRenderer.invoke('cancel-automation'),
  checkSystem: () => ipcRenderer.invoke('check-system'),
  onAutomationLog: (cb: (msg: string) => void) => {
    ipcRenderer.on('automation-log', (_e, msg) => cb(msg))
  },
  onAutomationProgress: (cb: (p: { current: number; total: number }) => void) => {
    ipcRenderer.on('automation-progress', (_e, p) => cb(p))
  },
  onAutomationEnd: (cb: () => void) => {
    ipcRenderer.on('automation-end', () => cb())
  },
  onAutomationComplete: (cb: () => void) => {
    ipcRenderer.on('automation-complete', () => cb())
  },
  // Window controls
  minimize: () => ipcRenderer.send('win-minimize'),
  maximize: () => ipcRenderer.send('win-maximize'),
  close:    () => ipcRenderer.send('win-close'),
})
