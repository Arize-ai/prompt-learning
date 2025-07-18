# 🚀 BigBench Hard Environment Setup

## Quick Setup (Python Virtual Environment)

### 1. Run the setup script:
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### 2. Activate the environment:
```bash
source bbh_venv/bin/activate
```

### 3. Test the setup:
```bash
python test_import.py
python test_bbh_download.py
```

## Manual Setup (if you prefer)

### 1. Create virtual environment:
```bash
python3 -m venv bbh_venv
source bbh_venv/bin/activate
```

### 2. Install packages:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Test imports:
```bash
python test_import.py
```

## For VS Code Users

After running the setup:

1. **Open Command Palette** (`Cmd+Shift+P`)
2. **Select "Python: Select Interpreter"**
3. **Choose** `./bbh_venv/bin/python`

This ensures VS Code uses the clean environment without conflicts.

## Environment Details

- **Name**: `bbh_venv`
- **Python Version**: 3.9+
- **Location**: `./bbh_venv/`
- **No conflicts** with local Phoenix installations

## Troubleshooting

### If you get import errors:
1. Make sure environment is activated: `source bbh_venv/bin/activate`
2. Check Python path: `which python` should show `./bbh_venv/bin/python`
3. Reinstall if needed: `rm -rf bbh_venv && ./setup_venv.sh`

### VS Code not using the right Python:
1. Open any `.py` file
2. Look at bottom-left corner for Python version
3. Click it and select `./bbh_venv/bin/python`

---

✅ **This setup eliminates all Phoenix conflicts and creates a clean environment!** 