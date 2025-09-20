import os, time, platform
from contextlib import redirect_stdout, redirect_stderr
from BitSrunLogin.LoginManager import LoginManager

def is_connect_internet(testip: str) -> bool:
    if platform.system().lower() == "windows":
        cmd = f"ping -n 4 {testip} >nul 2>nul"
    else:
        cmd = f"ping -c 4 -i 0.5 {testip} >/dev/null 2>&1"
    return os.system(cmd) == 0

def always_login(username: str, password: str, testip: str, checkinterval: int,
                 max_auth_retries: int = 3, backoff_seconds: int = 2 * 60 * 60):
    lm = LoginManager()
    def silent_login():
        with open(os.devnull, "w") as fnull, redirect_stdout(fnull), redirect_stderr(fnull):
            lm.login(username=username, password=password)

    consecutive = 0
    last_auth_ts = 0

    while True:
        # time.sleep(checkinterval)
        if is_connect_internet(testip):
            consecutive = 0
            last_auth_ts = 0
            time.sleep(checkinterval)
            continue

        print("网络断开：", time.strftime("%Y-%m-%d %H:%M:%S"))
        # 断网：决定是否发起认证
        now = int(time.time())
        if consecutive <= max_auth_retries or (now - last_auth_ts) >= backoff_seconds:
            # 防止认证请求频率过高
            try:
                if not is_connect_internet(testip):
                    silent_login()
                else:
                    time.sleep(checkinterval)
                    continue
                if is_connect_internet(testip):
                    print("认证成功：", time.strftime("%Y-%m-%d %H:%M:%S"))
                    time.sleep(checkinterval)
                    continue
            except Exception:
                pass
            consecutive += 1
            last_auth_ts = now
        time.sleep(checkinterval)

if __name__ == "__main__":
    username = "1111111"
    password = "1111111"
    testip = "www.baidu.com"
    checkinterval = 5*60
    always_login(username, password, testip, checkinterval)
