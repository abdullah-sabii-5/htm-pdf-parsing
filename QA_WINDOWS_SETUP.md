# QA Windows Setup Guide (Local Run)

This guide is for non-technical QA users on Windows laptops.

## 1) Install required apps (one time)

1. Install Git for Windows: https://git-scm.com/download/win
2. Install Python 3 (Windows): https://www.python.org/downloads/windows/
3. Install Google Chrome (or use Microsoft Edge already on Windows):
   - Chrome: https://www.google.com/chrome/
   - Edge: https://www.microsoft.com/edge

Important during Python install:

- Check the option **"Add Python to PATH"** before clicking install.

## 2) Get the project code

1. Open **Git Bash** (installed with Git).
2. Run:

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_FOLDER>
```

## 3) Start the app (easiest way)

1. In Windows Explorer, open the cloned project folder.
2. Double-click:

`start-ui-windows.bat`

What this does automatically:

- Creates a local Python environment (`.venv`) if missing
- Installs required packages
- Starts the web app
- Opens the browser at `http://127.0.0.1:5000`

## 4) Use the app

1. Upload a `.htm` or `.html` file.
2. Keep renderer as **Auto (recommended)**.
3. Click **Convert and Download PDF**.
4. PDF downloads to your normal Downloads folder (browser default).

## 5) Daily reuse (after first setup)

- Just double-click `start-ui-windows.bat` again.

## 6) Quick troubleshooting

1. Error says Python not found:
   - Reinstall Python and make sure **Add Python to PATH** is checked.
2. Conversion fails with browser/renderer error:
   - Install/update Chrome or Edge, then retry.
   - Re-run `start-ui-windows.bat` so dependencies are installed/updated.
   - If needed, set browser path manually before launch (Command Prompt):

```bat
set HTML2PDF_BROWSER=C:\Program Files\Google\Chrome\Application\chrome.exe
start-ui-windows.bat
```
3. Port already in use:
   - Close other app using `127.0.0.1:5000`, then rerun batch file.
