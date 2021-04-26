import dns.resolver
import requests
import sys
import os
import socket
import zipfile
import threading,time
import queue
import signal

state=1
q=queue.Queue()
count = 0
red ="\033[1;31;1m"
white = "\033[1;37;1m"
reset="\033[0m"

def banner():
    os.system("figlet 404-sites")

def remove_txt():
    for i in os.listdir('.'):
        if 'txt' in i.split('.'):
            os.remove(i)


def domain_alias(domain1,total_subDomains):
    global state,count,red,reset,pid
    time.sleep(0.1)
    while state:
        try:
            d=q.get()
            req = requests.get("http://"+d,allow_redirects=True)
            result = dns.resolver.resolve(d,"CNAME")
            code = req.status_code
            if code == 404 and domain1 not in str(result[0]).split('.'):
                print(red+"[+]"+d+" ("+str(code)+")"+white+" is alias of "+str(result[0])+reset+'(check out:https://github.com/EdOverflow/can-i-take-over-xyz )')
            else:
                print("[+]"+d+"("+str(code)+") is alias of " + str(result[0]))
        except Exception as e:
            pass
        finally:
            count+=1
            q.task_done()
            print("("+str(total_subDomains)+"/"+str(count)+")",end='\r',flush=True)
            if count == total_subDomains:
                remove_txt()
                os.kill(pid,signal.SIGTERM)


def start_threads(domain1,fl):
    global state
    threads = []

    for i in range(20):
        thread = threading.Thread(target=domain_alias ,args=(domain1,len(fl)),daemon=True)
        thread.start()
        threads.append(thread)
    
    for i in fl:
        q.put(i.strip( ))

    while not q.empty():
        pass
    state = 0
    for i in threads:
        i.join()
    


def get_subdomains(domain):
    domain1=domain.split('.')[0]
    print("[*] getting subdomains of "+domain+"\n")
    
    req = requests.get("https://chaos-data.projectdiscovery.io/"+domain1+'.zip',stream=True)
    if req.status_code == 200:
        with open(domain1+".zip",'wb+') as fl:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fl.write(chunk)

        with zipfile.ZipFile(domain1+".zip", 'r') as zip:
            zip.extractall()
            os.remove(domain1+'.zip')
            
        with open(domain+".txt",'r') as fl:
            fl = fl.readlines()
            with open('subdomains.lst','r') as f:
                f = f.readlines()
                for i in range(len(f)):
                    f[i]=f[i].strip()+'.'+domain.strip()
                fl=set(fl+f)
        start_threads(domain1,fl)
    else:
        get_subdomains_own(domain)


def get_subdomains_own(domain):
    with open('subdomains.lst','r') as f:
        fl = f.readlines()
        for i in range(len(fl)):
            fl[i]=fl[i].strip()+'.'+domain.strip()
        domain1=domain.split('.')[0]
        start_threads(domain1,fl)
        sys.exit()


if __name__=="__main__":
    banner()
    domain = input("Enter the domain name(example.com): ")
    pid = os.getpid()
    try:
        socket.gethostbyname(domain)
        get_subdomains(domain)
        sys.exit()

    except KeyboardInterrupt as e:
        remove_txt()
            
    except Exception as e:
        sys.exit(e)

