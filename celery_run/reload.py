import psutil
import os
import subprocess
import sys

list_ = psutil.pids()
kill = ('python.exe', 'flower.exe', 'celery.exe')

for i in list_:
    p = psutil.Process(i)
    if p.name() in kill and os.getpid() != p.pid:
        p.terminate()

subprocess.Popen('SCHTASKS /End /TN \celary\start_worker_celery', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celary\start_beat_celery', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /End /TN \celary\start_flower', shell=True, stdout=sys.stdout)

subprocess.Popen('SCHTASKS /Run /TN \celary\start_worker_celery', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celary\start_beat_celery', shell=True, stdout=sys.stdout)
subprocess.Popen('SCHTASKS /Run /TN \celary\start_flower', shell=True, stdout=sys.stdout)
