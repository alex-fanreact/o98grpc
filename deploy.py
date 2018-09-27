from git import Repo
import subprocess, signal, sys, os, atexit, time

def curRepo():
    return Repo(".")

def fetchOrigin() -> None:
    #print("[deploy] fetching")
    r = curRepo()
    r.remotes.origin.fetch()

def isRecentCommit() -> bool:
    r = curRepo()
    if r.remotes.origin.refs.master.object.hexsha == r.head.object.hexsha:
        return True
    else:
        return False

def printLastCommit():
    r = curRepo()
    c = r.head.object
    date = c.committed_datetime
    msg = c.message.strip()
    print(f"[deploy] Current commit: {date.isoformat()} - {msg}")

def update() -> None:   
    print("[deploy] pulling recent changes")
    r = curRepo()
    r.remote().pull()
    
pid = 0

def run():
    print("[deploy] spawning service process")
    proc = subprocess.Popen([sys.executable, "main.py"])
    global pid
    pid = proc.pid

def kill():
    global pid
    if pid == 0: return
    print("[deploy] killing service process")
    os.kill(pid, signal.SIGKILL)

def quit_gracefully():
    print("[deploy] exiting")
    kill()

def restart():
    print("[deploy] restarting deploy")
    os.execlp(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
    atexit.register(quit_gracefully)
    printLastCommit()
    run()
    print(f'[deploy] service process pid={pid}')
    while True:
        time.sleep(30)
        fetchOrigin()
        #if isRecentCommit(): 
            #print("[deploy] version is recent")
        if isRecentCommit() == False: 
            print("[deploy] new changes detected")
            kill()
            update()            
            restart()
        continue