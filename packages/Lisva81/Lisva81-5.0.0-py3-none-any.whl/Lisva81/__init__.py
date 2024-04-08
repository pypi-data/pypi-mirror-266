from pathlib import Path
import requests
import os
import json
from colorama import Fore , init
import shutil
import ast
import os
from bs4 import BeautifulSoup
import platform
sistema_operativo = platform.system()
import urllib3
import urllib
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pymongo
from pymongo import MongoClient
#import dns.resolver
import time
import sys
sys.setrecursionlimit(1500)

#dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
#dns.resolver.default_resolver.nameservers = ['1.1.1.1']

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"}

if sistema_operativo == "Windows":
    cmd = "cls"
elif sistema_operativo == "Linux":
    cmd = "clear"

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def progress(filename,index,total):
    ifmt = sizeof_fmt(index)
    tfmt = sizeof_fmt(total)
    printl(f'{filename} {ifmt}/{tfmt}')
    pass

def printl(text):
    init()
    print(Fore.GREEN + text,end='\r')

def make_session(type,id):
    session = requests.Session()
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0","Upgrade-Insecure-Requests":"1"}
    if type=="rv":
        return session
    elif type=="rme":
    	host = "https://revmedicaelectronica.sld.cu/index.php/rme"
    	payload = {"source": "","username": "raydel0307","password": "R@ydel2022*","remember": "1"}
    	resp = session.post(f"{host}/login/signIn", data=payload, headers=headers)
    elif type=="apye":
        host = "https://apye.esceg.cu/index.php/apye/"
        resp = session.get(host + "login")
        soup = BeautifulSoup(resp.text, "html.parser")
        csrfToken = soup.find("input",attrs={"name":"csrfToken"})['value']
        url_post = host + 'login/signIn'
        payload = {}
        payload['csrfToken'] = csrfToken
        payload['source'] = ''
        payload['username'] = "carlosj99"
        payload['password'] = "Maikel2023*"
        payload['remember'] = '1'
        resp = session.post(url_post, data=payload)
    elif type=="uo":
        resp = requests.post("http://apiserver.alwaysdata.net/session",json={"type":type,"id":id},headers={'Content-Type':'application/json'})
        data = json.loads(resp.text)
        session.cookies.update(data)
    return session

def wait_download(url,ichunk=0,index=0,file=None,session=None):
    init()
    printl(Fore.RED + 'Iniciando sesion...')
    dl = url
    if "api.download.cu" in dl:
        data = dl.split("api.download.cu/")[1].split("/")
        total_size = int(data[0])
        ids = data[1]
        filename = data[2].split("?")[-1]
        values = data[2].split("?"+filename)[0].split("?")
        type = "r"
        id = ""
        host = f"https://cujae.edu.cu/index.php/r/$$$call$$$/api/file/file-api/download-file?submissionFileId=*&submissionId={ids}&stageId=1"
    elif "revinformatica.sld.cu" in dl:
        value = dl.split("rcim/")[1].split("/")
        url = f"https://nube.uo.edu.cu/remote.php/dav/uploads/{value[0]}/web-file-upload-{value[1]}/.file"
        filename = value[3]
        total_size = int(value[2])
        type = "uo"
        id = "11"
    elif "apye.esceg.cu" in dl:
        value = dl.split("apye/")[1].split("/")
        filename = value[3]
        total_size = int(value[1])
        type = "apye"
        id = value[2]
        url = f"https://apye.esceg.cu/index.php/apye/$$$call$$$/api/file/file-api/download-file?submissionFileId=^&submissionId={value[0]}&stageId=1"
    elif "revmedicaelectronica" in dl:
        value = dl.split("rme/")[1].split("/")
        filename = value[3]
        total_size = int(value[1])
        type = "rme"
        id = value[2]
        url = f"https://revmedicaelectronica.sld.cu/index.php/rme/author/download/{value[0]}/^"
    elif "nube.uo.edu.cu" in dl:
        url = dl.split("{")[0]+".file"
        filename = dl.split("/")[-1]
        id = dl.split("{")[1].split("}")[0]
        total_size = int(dl.split("}/")[1].split("/")[0])
        type = "uo"
    else:
    	printl(Fore.BLUE + 'URL no permitida ... !!!')
    	return

    if not session:
        session = make_session(type,id)
    if session:
        init()
        os.system(cmd)
        printl(Fore.BLUE + 'Sesion Iniciada ... !!!')
    else:
        init()
        os.system(cmd)
        printl(Fore.RED + 'Error al iniciar sesion ... !!!')
    state = 'ok'
    i = ichunk
    l = 1
    j = str(l)
    chunk_por = index
    filet = 'Downloading: ' + filename
    if os.path.exists(filename):
        os.unlink(filename)
    if len(filet) > 30:
        filet = 'Downloading ... '
    f = open(filename,"wb") 
    os.system(cmd)
    fnl = []
    totals = total_size
    parte = 0
    if "apye.esceg.cu" in dl:
        values = id.split("-")
        for v in values:
            url = url.replace("^",v)
            resp = session.get(url,headers=headers,stream=True,verify=False)
            for chunk in resp.iter_content(chunk_size=8192):
                chunk_por += len(chunk)
                f.write(chunk)
                progress(f'{filet} ',chunk_por,total_size)
    elif "revmedicaelectronica" in dl:
        values = id.split("-")
        for v in values:
            url = url.replace("^",v)
            resp = session.get(url,headers=headers,stream=True,verify=False)
            for chunk in resp.iter_content(chunk_size=1024*1024):
                chunk_por += len(chunk)
                f.write(chunk)
                progress(f'{filet} ',chunk_por,total_size)
    elif "api.download.cu" in dl:
        for v in values:
            url = host.replace("*",v)
            resp = session.get(url,headers=headers,stream=True,verify=False)
            for chunk in resp.iter_content(chunk_size=8192):
                chunk_por += len(chunk)
                f.write(chunk)
                progress(f'{filet} ',chunk_por,total_size)
    else:
        while total_size > chunk_por:
            resp = session.get(url,headers=headers,stream=True,verify=False)
            for chunk in resp.iter_content(chunk_size=8192):
                chunk_por += len(chunk)
                f.write(chunk)
                progress(f'{filet} ',chunk_por,total_size)
            l+=1
            i+=1
            if parte==totals:
                total_size = chunk_por
    f.close()
    if os.path.exists('Lisva81/' + filename):
        os.unlink('Lisva81/' + filename)
    shutil.move(filename,'Lisva81/'+filename)
    if "revgacetaestudiantil.sld" in dl or "revmedicaelectronica" in dl:
        with open('Lisva81/dwnl' + filename, "wb") as filet:
            filet.write(open(f, "rb").read().replace(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82",b''))
        os.unlink(f)
    os.system(cmd)
    printl('Descarga Finalizada !!! Archivos Guardados en ./Downloads. Envie 0 y luego Enter para salir o pulse solo Enter para continuar')
    state = 'finish'
    a = input()
    if a == '0':
        if state == 'finish':
            return False,i,chunk_por,file,session
    else:
        return True,i,chunk_por,file,session

def initi():
    while (True):
        ichunk = 0
        index = 0
        file = None
        session = None
        init()
        print(Fore.YELLOW + '> Bienvenido a Lisva81 <')
        print(Fore.YELLOW + 'Ingrese su enlace')
        url = input()
        if os.path.exists('Lisva81/'):
            pass
        else:
            os.mkdir('Lisva81/')
        wait,ichunk,index,file,session = wait_download(url,ichunk,index,file,session)
        if not wait:
            break
                
initi()

#https://nube.uo.edu.cu/remote.php/dav/uploads/E88DF8CD-154A-4B85-A255-B162C8632F3A/web-file-upload-de3v9ttpv4azdp5gkkbeupn3ifj2z1zl-2531925677/{1}/1806431279/SITERESRSEVid.mp4