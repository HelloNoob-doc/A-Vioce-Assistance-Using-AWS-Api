import subprocess

def get_result(path) :
    
    p = subprocess.Popen('python  /home/ma-user/work/GOT/GOT/GOT/demo/run_ocr.py  --model-name  /home/ma-user/work/GOT/GOT/GOT_weights/  --image-file ' + path + ' --type  ocr', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = ''
    for line in iter(p.stdout.readline, b''):
        res += line.decode('utf-8')
    
    return res
