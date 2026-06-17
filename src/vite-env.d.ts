/// <reference types="vite/client" />

interface Window {
  electronAPI: {
    startAutomation: (urls: string[], browserPath?: string) => Promise<void>
    cancelAutomation: () => Promise<void>
    checkSystem: () => Promise<{os: string, chromeFound: boolean, chromePath?: string}>
    onAutomationLog: (cb: (msg: string) => void) => void
    onAutomationProgress: (cb: (progress: { current: number; total: number }) => void) => void
    onAutomationEnd: (cb: () => void) => void
    onAutomationComplete: (cb: () => void) => void
    minimize: () => void
    maximize: () => void
    close: () => void
  }
}
