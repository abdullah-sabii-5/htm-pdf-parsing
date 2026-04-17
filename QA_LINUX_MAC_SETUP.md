# QA Setup Guide — Linux & macOS (Local Run)

This guide is for non-technical QA users on Linux or macOS.

## 1) Install required apps (one time)

### macOS

1. Install **Homebrew** (package manager) if you don't have it — open Terminal and run:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python 3:

   ```bash
   brew install python
   ```

3. Install Google Chrome:
   - Download from: https://www.google.com/chrome/
   - Or via Homebrew: `brew install --cask google-chrome`

### Linux (Ubuntu / Debian)

1. Install Python 3 and venv support:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv -y
   ```

2. Install a browser (pick one):

   ```bash
   # Google Chrome
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo apt install ./google-chrome-stable_current_amd64.deb

   # OR Chromium (lighter, open-source)
   sudo apt install chromium-browser -y
   ```

### Linux (Fedora / RHEL)

1. Install Python 3:

   ```bash
   sudo dnf install python3 -y
   ```

2. Install Chromium:

   ```bash
   sudo dnf install chromium -y
   ```

---

## 2) Get the project code

Open a Terminal and run:

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_FOLDER>
```

---

## 3) Start the app (easiest way)

Make the startup script executable (first time only):

```bash
chmod +x start-ui.sh
```

Then launch it:

```bash
./start-ui.sh
```

What this does automatically:

- Creates a local Python environment (`.venv`) if missing
- Installs required packages
- Detects your installed browser
- Starts the web app
- Opens the browser at `http://127.0.0.1:5000`

---

## 4) Use the app

1. Upload a `.htm` or `.html` file.
2. Keep renderer as **Auto (recommended)**.
3. Click **Convert and Download PDF**.
4. PDF downloads to your normal Downloads folder (browser default).

---

## 5) Daily reuse (after first setup)

Just run `./start-ui.sh` again — it skips setup steps that are already done.

---

## 6) Quick troubleshooting

**Python not found:**
- macOS: run `brew install python`
- Linux: run `sudo apt install python3 python3-venv` (Ubuntu/Debian) or `sudo dnf install python3` (Fedora)

**Conversion fails with browser/renderer error:**
- Make sure Chrome or Chromium is installed (see step 1).
- You can also point to the browser manually before launching:

  ```bash
  # macOS
  export HTML2PDF_BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  ./start-ui.sh

  # Linux
  export HTML2PDF_BROWSER="/usr/bin/google-chrome"
  ./start-ui.sh
  ```

**Port already in use:**
- Find and stop whatever is using port 5000:

  ```bash
  # macOS / Linux
  lsof -ti :5000 | xargs kill -9
  ```

- Then rerun `./start-ui.sh`.

**Browser does not open automatically (Linux):**
- Install `xdg-utils`: `sudo apt install xdg-utils`
- Or manually open `http://127.0.0.1:5000` in your browser.
