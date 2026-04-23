#!/usr/bin/env python3
import json
import time
import psutil
from datetime import datetime

def get_cpu_load():
    load = psutil.getloadavg()
    return {"1 min": load[0], "5 min": load[1], "15 min": load[2]}

def memory(human=True):
    mem = psutil.virtual_memory()
    def fmt(val):
        return f"{val / (1024**3):.1f}G" if human else val
    return {
        "total": fmt(mem.total),
        "used": fmt(mem.used),
        "free": fmt(mem.free),
        "shared": "N/A",
        "buff_cache": fmt(mem.cached + mem.buffers) if hasattr(mem, 'cached') else "N/A",
        "available": fmt(mem.available)
    }

def cpu_freq():
    freq = psutil.cpu_freq()
    return freq.current if freq else None

def disk_usage(human=True):
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "filesystem": part.device,
                "size": f"{usage.total / (1024**3):.1f}G" if human else usage.total,
                "used": f"{usage.used / (1024**3):.1f}G" if human else usage.used,
                "avail": f"{usage.free / (1024**3):.1f}G" if human else usage.free,
                "use%": f"{usage.percent:.1f}%",
                "mount": part.mountpoint
            })
        except PermissionError:
            continue
    return disks

def collect_stats(human=True):
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_load": get_cpu_load(),
        "memory": memory(human),
        "cpu_freq_mhz": cpu_freq(),
        "disk_usage": disk_usage(human)
    }

def main():
    interval = 360
    log_file = "stat_json.jsonl"
    print(f"Мониторинг запущен. Лог: {log_file}. Остановка: Ctrl+C")
    try:
        while True:
            stats = collect_stats(human=True)
            if stats:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(stats, ensure_ascii=False) + '\n')
                cpu_1m = stats["cpu_load"]["1 min"]
                mem_used = stats["memory"]["used"]
                print(f"{stats['timestamp']} | CPU 1m: {cpu_1m} | Mem used: {mem_used}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")

if __name__ == "__main__":
    main()