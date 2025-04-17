const { app, BrowserWindow, ipcMain, Tray, Menu, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const dotenv = require('dotenv');
const url = require('url');
const fetch = require('node-fetch');

dotenv.config();

let loginWindow;
let tray;
let listeningWindow;
let pythonProcess;
let token = null;

// Ensure single instance of the app
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine) => {
    const deepLink = commandLine.find(arg => arg.startsWith('nuera_mvp://'));
    if (deepLink) handleDeepLink(deepLink);
  });

  function createLoginWindow() {
    loginWindow = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'), // Specify preload script
        contextIsolation: true,                      // Enable context isolation
        nodeIntegration: false                       // Disable node integration
      }
    });
    loginWindow.loadFile('index.html');
    loginWindow.on('closed', () => {
      if (!tray) app.quit();
    });
  }

  function createTray() {
    tray = new Tray(path.join(__dirname, 'icon.png')); // Replace with your icon
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Exit', click: () => {
        if (pythonProcess) pythonProcess.kill();
        app.quit();
      }}
    ]);
    tray.setContextMenu(contextMenu);
    tray.setToolTip('Nuera');
  }

  function createListeningWindow() {
    listeningWindow = new BrowserWindow({
      width: 200,
      height: 200,
      frame: false,
      alwaysOnTop: true,
      transparent: true,
      skipTaskbar: true,
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'), // Specify preload script
        contextIsolation: true,                      // Enable context isolation
        nodeIntegration: false                       // Disable node integration
      }
    });
    listeningWindow.loadFile('listening.html');
    listeningWindow.hide();
  }
  function startPythonProcess() {
    pythonProcess = spawn('python', ['main.py'], {
      env: process.env,
      cwd: __dirname
    });

    pythonProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message === 'START_LISTENING') {
        listeningWindow.show();
      } else if (message === 'STOP_LISTENING') {
        listeningWindow.hide();
      }
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      app.quit();
    });
  }

  function onAuthenticated() {
    loginWindow.hide();
    if (!tray) createTray();
    startPythonProcess();
  }

  async function handleDeepLink(deepLink) {
    const urlObj = new URL(deepLink);
    const code = urlObj.searchParams.get('code');
    if (!code) return;

    try {
      const response = await fetch('http://localhost:3000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      const data = await response.json();
      if (data.token) {
        token = data.token;
        onAuthenticated();
      } else {
        console.error('No token received');
      }
    } catch (err) {
      console.error('Authentication failed:', err);
    }
  }

  app.on('ready', () => {
    createLoginWindow();
    createListeningWindow();
    app.setAsDefaultProtocolClient('nuera');
  });

  app.on('window-all-closed', (e) => {
    e.preventDefault();
  });

  app.on('open-url', (event, url) => {
    event.preventDefault();
    handleDeepLink(url);
  });

  ipcMain.on('authenticated', () => {
    onAuthenticated();
  });

  ipcMain.on('open-external', (event, url) => {
    shell.openExternal(url);
  });
}