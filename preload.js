const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  loadPage: (page) => ipcRenderer.invoke("load-page", page),
  openExternal: (url) => ipcRenderer.send("open-external", url),
  onAuthSuccess: (callback) =>
    ipcRenderer.on("auth-success", (event, token) => callback(token)),
  onAuthError: (callback) =>
    ipcRenderer.on("auth-error", (event, error) => callback(error)),
});