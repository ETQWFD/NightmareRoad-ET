#!/usr/bin/env python3
"""Nightmare Road-ET Server 1.8.0 macOS launcher.

纯 Python 外壳：启动 sd-server、代理 /sdapi、提供 /admin 与 /healthz。
这样 macOS 包不需要 Mach-O 编译外壳，引擎仍使用官方 universal sd-server。
"""
import argparse, http.client, http.server, json, os, shlex, shutil, signal, socket
import subprocess, sys, tarfile, tempfile, threading, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "bin" / "sd-server"

def refresh_engine():
    global ENGINE
    for c in (ROOT / "bin" / "sd-server", ROOT / "engine" / "sd-server", ROOT / "sd-server", ROOT / "runtime" / "sd-server"):
        if c.exists():
            ENGINE = c
            return True
    return False
LIB = ROOT / "lib"
WEB = ROOT / "web"
DATA = ROOT / "data"
URL = "https://github.com/ETQWFD/NightmareRoad-ET/releases/download/server-1.8.0/NightmareRoad-ET-Server-1.8.0-engine-macos-universal.tar.gz"
VERSION = "1.8.0"
log_lock = threading.Lock()

def log(msg):
    line = f"[etserver] {time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    with log_lock:
        print(line, flush=True)
        try:
            (DATA / "logs").mkdir(parents=True, exist_ok=True)
            with (DATA / "logs" / "server.log").open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

def read_conf():
    conf = {"port": "4080", "inner_port": "17860", "threads": str(min(8, os.cpu_count() or 4)), "model_path": "", "engine_args": ""}
    p = DATA / "config" / "etserver.conf"
    if p.exists():
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = raw.strip()
            if not s or s.startswith("#") or "=" not in s: continue
            k, v = s.split("=", 1)
            conf[k.strip().lower()] = v.strip().strip('"').strip("'")
    return conf

def find_model(explicit):
    if explicit and Path(explicit).is_file(): return explicit
    if explicit and (ROOT / explicit).is_file(): return str(ROOT / explicit)
    for pat in ("*.safetensors", "*.ckpt", "*.gguf", "*.pt"):
        found = sorted((DATA / "models").rglob(pat))
        if found: return str(max(found, key=lambda p: p.stat().st_size))
    return ""

def install_engine():
    if refresh_engine(): return True
    log("未找到推理引擎，开始下载 macOS universal 引擎")
    tmp = Path(tempfile.mkdtemp(prefix="nret-mac-engine-"))
    try:
        archive = tmp / "engine.tar.gz"
        req = urllib.request.Request(URL, headers={"User-Agent": f"NightmareRoadET/{VERSION}"})
        with urllib.request.urlopen(req, timeout=30) as r, archive.open("wb") as out:
            total = int(r.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = r.read(262144)
                if not chunk: break
                out.write(chunk); done += len(chunk)
            if total and done != total: raise RuntimeError(f"下载不完整 {done}/{total}")
        if not tarfile.is_tarfile(archive): raise RuntimeError("引擎资产不是 tar.gz")
        with tarfile.open(archive, "r:*") as tf:
            for m in tf.getmembers():
                name = m.name.replace("\\", "/")
                if name.startswith("/") or ".." in Path(name).parts:
                    raise RuntimeError("引擎压缩包包含非法路径")
            tf.extractall(tmp / "unpacked")
        root = tmp / "unpacked"
        got = list(root.rglob("sd-server"))
        if not got: raise RuntimeError("下载包内没有 sd-server")
        ENGINE.parent.mkdir(parents=True, exist_ok=True); LIB.mkdir(parents=True, exist_ok=True)
        dest = ROOT / "bin" / "sd-server"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(got[0], dest); dest.chmod(0o755)
        refresh_engine()
        for d in list(root.rglob("*.dylib")):
            shutil.copy2(d, LIB / d.name)
        log(f"引擎安装完成：{ENGINE}")
        return True
    except Exception as exc:
        log(f"引擎自动下载失败：{exc}")
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

class State:
    def __init__(self):
        self.proc = None
        self.started = time.time()
        self.restarts = 0
        self.model = ""
        self.ready = False
        self.last_error = ""
        self.lock = threading.Lock()

state = State()

def engine_ready():
    try:
        c = http.client.HTTPConnection("127.0.0.1", state_inner, timeout=2)
        c.request("GET", "/")
        r = c.getresponse(); r.read(1024)
        return True
    except Exception:
        return False

def reader():
    p = state.proc
    if not p or not p.stdout: return
    for line in p.stdout:
        log("engine: " + line.rstrip())
    log(f"engine 退出，退出码 {p.poll()}")

def start_engine(model, inner, threads, args):
    state.model = model
    if not model:
        state.last_error = "没有找到模型，请把 .safetensors/.ckpt 放入 data/models"
        log(state.last_error); return
    cmd = [str(ENGINE), "--model", model, "--listen-ip", "127.0.0.1", "--listen-port", str(inner), "--threads", str(threads)]
    if args:
        cmd += shlex.split(args)
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = str(LIB) + (":" + env["DYLD_LIBRARY_PATH"] if env.get("DYLD_LIBRARY_PATH") else "")
    log("启动引擎：" + " ".join(cmd))
    try:
        state.proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1)
        threading.Thread(target=reader, daemon=True).start()
    except Exception as exc:
        state.last_error = f"引擎启动失败：{exc}"; log(state.last_error)

def bootstrap(model, inner, threads, args):
    if not install_engine():
        state.last_error = "推理引擎缺失且自动下载失败"; return
    start_engine(model, inner, threads, args)

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "NightmareRoadET/1.8.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):
        log("http: " + (fmt % a))

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k, v in extra.items(): self.send_header(k, v)
        self.end_headers()
        if body: self.wfile.write(body)

    def health(self):
        ready = engine_ready()
        state.ready = ready
        js = {"status": "ready" if ready else "loading", "engine": str(ENGINE), "model": Path(state.model).name if state.model else "", "model_path": state.model, "engine_restarts": state.restarts, "engine_pid": state.proc.pid if state.proc else 0, "version": VERSION, "uptime": int(time.time() - state.started)}
        if state.last_error: js["error"] = state.last_error
        self._send(200 if ready else 503, json.dumps(js, ensure_ascii=False).encode())

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/healthz", "/api/status"): return self.health()
        if path in ("/", "/admin", "/admin/"):
            body = (WEB / "admin.html").read_bytes()
            return self._send(200, body, "text/html; charset=utf-8")
        if path.startswith("/web/"):
            f = (WEB / path[5:]).resolve()
            if WEB in f.parents and f.is_file():
                ct = "text/html" if f.suffix == ".html" else "application/octet-stream"
                return self._send(200, f.read_bytes(), ct + "; charset=utf-8" if ct == "text/html" else ct)
        if path == "/favicon.ico": return self._send(204)
        if path.startswith("/sdapi/"):
            return self.proxy("GET", path, None)
        self._send(404, b'{"detail":"not found"}')

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        if path.startswith("/sdapi/"):
            return self.proxy("POST", path, body)
        if path == "/api/restart":
            if state.proc:
                try: state.proc.terminate()
                except Exception: pass
            state.restarts += 1; state.last_error = ""
            threading.Thread(target=bootstrap, args=(state.model or find_model(""), state_inner, state_threads, state_args), daemon=True).start()
            return self._send(202, b'{"status":"restarting"}')
        self._send(404, b'{"detail":"not found"}')

    def proxy(self, method, path, body):
        try:
            c = http.client.HTTPConnection("127.0.0.1", state_inner, timeout=600)
            headers = {"Content-Type": self.headers.get("Content-Type") or "application/json"}
            if self.headers.get("Authorization"): headers["Authorization"] = self.headers["Authorization"]
            c.request(method, path, body, headers)
            r = c.getresponse(); data = r.read()
            self.send_response(r.status)
            self.send_header("Content-Type", r.getheader("Content-Type") or "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
        except Exception as exc:
            self._send(502, json.dumps({"detail": f"引擎不可用：{exc}"}, ensure_ascii=False).encode())

def main():
    global state_inner, state_threads, state_args
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int); ap.add_argument("--inner-port", type=int)
    ap.add_argument("--model", default=""); ap.add_argument("--no-wizard", action="store_true"); ap.add_argument("--no-gui", action="store_true")
    a = ap.parse_args()
    conf = read_conf()
    port = a.port or int(conf.get("port") or 4080)
    state_inner = a.inner_port or int(conf.get("inner_port") or 17860)
    state_threads = int(conf.get("threads") or 4); state_args = conf.get("engine_args") or ""
    model = find_model(a.model or conf.get("model_path") or "")
    refresh_engine()
    if not install_engine():
        log("警告：引擎缺失，服务仍会启动并自动重试下载")
    threading.Thread(target=bootstrap, args=(model, state_inner, state_threads, state_args), daemon=True).start()
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    log(f"管理界面 http://127.0.0.1:{port}/admin ；引擎内部端口 {state_inner}")
    def stop(sig, frame):
        if state.proc:
            try: state.proc.terminate()
            except Exception: pass
        srv.shutdown()
    signal.signal(signal.SIGTERM, stop); signal.signal(signal.SIGINT, stop)
    srv.serve_forever()

if __name__ == "__main__":
    main()
