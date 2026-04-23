import json
import os
import subprocess
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

STATS_FILE = os.path.join(settings.BASE_DIR, 'stat_json.jsonl')
SCRIPT_PATH = r'C:/Users/vovav/OneDrive/Рабочий стол/monit_PC/mot_pc/main/scripts/monit_pc.py'

def get_latest_stats():
    if not os.path.exists(STATS_FILE):
        return None
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            if file_size == 0:
                return None
            block_size = 1024
            f.seek(max(file_size - block_size, 0))
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                return json.loads(last_line)
    except (json.JSONDecodeError, IOError):
        return None
    return None

@csrf_exempt
def bash_script(request):
    if request.method == 'POST':
        try:
            result = subprocess.run(
                ['python', SCRIPT_PATH],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            return JsonResponse({
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            })
        except subprocess.TimeoutExpired:
            return JsonResponse({'error': 'Script execution timed out'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

def dashboard(request):
    stats = get_latest_stats()
    return render(request, 'main/main.html', {'stats': stats})

def api_stats(request):
    stats = get_latest_stats()
    if stats:
        return JsonResponse(stats)
    else:
        return JsonResponse({'error': 'No data available'}, status=404)