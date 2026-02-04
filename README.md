# strip-zsnd
Strip consecutive zero samples in WAV files to mitigate audio issues such as buffer underflow during recording.

For detailed usage information, run:

    python ./strp-zsnd.py --help

---

## 🚀 venv Setup

### 1. Clone repo.
```bash
git clone https://github.com/YamimakiReru/strip-zsnd
cd strip-zsnd
```

### 2. Create venv environment
```bash
python3 -m venv .venv
```

### 3. Activate venv environment

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows（PowerShell）**
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. 📦 Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Run
```bash
python ./strip-zsnd.py damaged.wav [stripped.wav]
```
---

## 🧹 Exit from venv environment
```bash
deactivate
```

## License

This project is licensed under the MIT License.  
See the LICENSE.txt file for details.
