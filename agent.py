import os
import time
import socket
import platform
import psutil
import requests
from datetime import datetime

# Config: prefer environment variables for safety
API_KEY = os.environ.get("PROCESS_MONITOR_API_KEY",
                         "django-insecure-=402zvk_$qvoqrv2d7^6+mi7d_st#&md6y3_ft3m!e)lp@-3!2")
BACKEND_URL = os.environ.get("PROCESS_MONITOR_BACKEND", "http://127.0.0.1:8000/api/process-data/")
INTERVAL_SECONDS = int(os.environ.get("PROCESS_MONITOR_INTERVAL", "60"))  # Default 60 seconds
CPU_SAMPLE_DELAY = float(os.environ.get("PROCESS_MONITOR_CPU_SAMPLE_DELAY", "0.15"))  # short delay to measure cpu%

# Thresholds (for reference / logging only)
HIGH_CPU_THRESHOLD = float(os.environ.get("PROCESS_MONITOR_HIGH_CPU", "50.0"))
HIGH_MEM_MB_THRESHOLD = float(os.environ.get("PROCESS_MONITOR_HIGH_MEM_MB", "500.0"))

def get_system_info():
    vm = psutil.virtual_memory()
    du = psutil.disk_usage(os.path.abspath(os.sep))
    # platform.processor() often returns empty on Windows; use uname or platform.version if needed
    system = {
        "os": f"{platform.system()} {platform.release()}",
        "processor": platform.processor() or platform.machine() or "",
        "cores": psutil.cpu_count(logical=False) or 0,
        "threads": psutil.cpu_count(logical=True) or 0,
        "ram_gb": round(vm.total / (1024**3), 2),
        "used_ram_gb": round((vm.total - vm.available) / (1024**3), 2),
        "free_ram_gb": round(vm.available / (1024**3), 2),
        "storage_free_gb": round(du.free / (1024**3), 2),
        "storage_total_gb": round(du.total / (1024**3), 2),
        "storage_used_gb": round(du.used / (1024**3), 2),
    }
    return system

def sample_process_cpu(process_list):
    """
    To get a meaningful per-process cpu percent, we:
      1) call cpu_percent(None) for each process to initialize internal counters.
      2) sleep a short interval (CPU_SAMPLE_DELAY).
      3) call cpu_percent(None) again to obtain % since initialization.
    This avoids per-process blocking intervals.
    """
    for p in process_list:
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # small sleep to let psutil compute CPU deltas
    time.sleep(CPU_SAMPLE_DELAY)

    cpu_map = {}
    for p in process_list:
        try:
            cpu_map[p.pid] = p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # treat missing as 0.0
            cpu_map[p.pid] = 0.0
    return cpu_map

def get_processes():
    processes = []
    process_objects = []
    
    # First collect all process objects
    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'memory_info']):
        try:
            process_objects.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sample CPU usage for all processes
    cpu_map = sample_process_cpu(process_objects)
    
    # Now collect process information with proper CPU and memory data
    for proc in process_objects:
        try:
            info = proc.info
            memory_info = proc.memory_info()
            processes.append({
                "pid": info.get("pid"),
                "ppid": info.get("ppid"),
                "name": info.get("name", ""),
                "cpu": cpu_map.get(proc.pid, 0.0),
                "memory": round(memory_info.rss / (1024 * 1024), 2),  # Convert to MB
                "cmdline": " ".join(proc.cmdline()) if proc.cmdline() else "",
                "username": proc.username() if proc.username() else ""
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def build_payload():
    hostname = socket.gethostname()
    sysinfo = get_system_info()  # returns dict with os, processor, ram_gb, etc.
    payload = {
        "hostname": hostname,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "processes": get_processes(),
        **sysinfo,   # flatten system info here
    }
    return payload

def send_data():
    payload = build_payload()
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=15)
        # print helpful info
        print(f"[{datetime.utcnow().isoformat()}] Sent payload: processes={len(payload['processes'])}  status={r.status_code}")
        # optionally log body for debugging when non-2xx
        if not (200 <= r.status_code < 300):
            print("Response text:", r.text)
    except requests.RequestException as exc:
        print(f"[{datetime.utcnow().isoformat()}] Error sending data:", exc)

def main_loop():
    print("Process Monitoring Agent started")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            send_data()
            if INTERVAL_SECONDS > 0:
                time.sleep(INTERVAL_SECONDS)
            else:
                break  # Run once if interval is 0 or negative
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main_loop()
