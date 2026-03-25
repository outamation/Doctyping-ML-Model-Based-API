# FastAPI Deployment & Restart Checklist

**Server Details:**
- VM Location: `52.201.67.184`
- FastAPI Port: `8003`
- Project Directory: `/home/ubuntu/doc_classification_model_based_api`

---

## Step 1: Check Current Running Process

Before updating, verify the current FastAPI status:

```bash
ps aux | grep new_main.py
```

**Expected output:** Shows running `new_main.py` process (if running)

---

## Step 2: Extract New Codebase Zip or it can be tar

```bash
cd /home/ubuntu/doc_classification_model_based_api
unzip -o <new-zip-file.zip>
```

> **Note:** If needed, backup the current codebase first:
> ```bash
> cp -r /home/ubuntu/doc_classification_model_based_api /home/ubuntu/doc_classification_model_based_api.backup
> ```

---

## Step 3: Update Dependencies

Install/update Python dependencies using `uv pip`:

```bash
cd /home/ubuntu/doc_classification_model_based_api
uv pip install -r requirements.txt
```

> **Important:** This updates dependencies WITHOUT modifying or overwriting the `.venv` directory.

---

## Step 4: Stop Current FastAPI Process

Kill the existing FastAPI process:

```bash
sudo pkill -f new_main.py
```

**Verification:** Wait 2-3 seconds, then run:
```bash
ps aux | grep new_main.py
```

> Should show no `new_main.py` process (only grep itself in output)

---

## Step 5: Activate Virtual Environment

Activate the Python virtual environment:

```bash
source .venv/bin/activate
```

**Expected output:** Prompt should now show `(.venv)` prefix

---

## Step 6: Start FastAPI with New Code

Start FastAPI with auto-timestamped log file:

```bash
sudo nohup .venv/bin/python new_main.py > logs/new_main_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

This creates a log file with format: `new_main_20260303_143045.log`

---

## Step 7: Verify Deployment

Check that FastAPI is running:

```bash
ps aux | grep new_main.py
```

**Expected:** Should show running process

---

## Step 8: Verify Logs

Check the latest log file to confirm successful startup:

```bash
ls -lth logs/ | head -5
tail -f logs/new_main_*.log
```

> Press `Ctrl+C` to exit tail command

**Look for:**
- ✅ `Application startup complete` or similar success message
- ✅ No error stack traces
- ✅ API listening on `0.0.0.0:8000`

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Check running process | `ps aux \| grep fastapi_app.py` |
| Stop FastAPI | `sudo pkill -f fastapi_app.py` |
| Start FastAPI | `sudo nohup .venv/bin/python fastapi_app.py > logs/fast_api_app_$(date +%Y%m%d_%H%M%S).log 2>&1 &` |
| View latest logs | `tail -f logs/fast_api_app_*.log` |
| Update dependencies | `uv pip install -r requirements.txt` |

---

## Troubleshooting

**FastAPI won't start?**
- Check log file for errors: `tail logs/fast_api_app_*.log`
- Verify `.venv` exists: `ls -la .venv/`
- Check port availability: `sudo lsof -i :8000`

**Permission denied errors?**
- Ensure you're in the project directory: `cd /home/ubuntu/doc_classification_model_based_api`
- Use `sudo` for nohup and pkill commands

**Old processes still running?**
- Force kill: `sudo pkill -9 -f fastapi_app.py`

**File not found errors in logs?**
- Check if mounted storage is accessible:
  ```bash
  ls -la /mnt/dev
  ls -la /mnt/uat
  ```
- If directories don't exist or are inaccessible, mount them:

**Mount UAT Storage:**
```bash
sudo mount -t cifs //52.0.225.119/uat-ai-dev-docs /mnt/uat -o username=webhosting,password="Mahant=Pramukh@1",vers=2.0
```

**Mount DEV Storage:**
```bash
sudo mount -t cifs //52.0.225.119/ai-dev-docs /mnt/dev -o username=webhosting,password="Mahant=Pramukh@1",vers=2.0
```

- After mounting, restart FastAPI (see **Step 4** to **Step 6**)
- Verify mount was successful:
  ```bash
  mount | grep myshare
  ```

---

**Last Updated:** March 18, 2026
