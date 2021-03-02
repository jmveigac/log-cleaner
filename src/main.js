const electron = require('electron');

const countdown = require('./scripts/countdown');

const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const ipc = electron.ipcMain;

let mainWindow;

app.on('ready', _ => {
  mainWindow = new BrowserWindow({
    height: 800,
    width: 800
  });

  mainWindow.loadURL(`file://${__dirname}/views/index.html`);

  mainWindow.on('closed', _ => {
    mainWindow = null;
  });
});

ipc.on('countdown-start', _ => {
  countdown(count => mainWindow.webContents.send('countdown', count));
});