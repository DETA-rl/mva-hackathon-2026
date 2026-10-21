"""Local replication viewer for the MVA analysis.

Run:  python3 replicate_ui.py   then open http://127.0.0.1:8765
Point the two folders at your data and work directories, then press Run on each step in order.
Only the steps in steps.json can run. Listens on 127.0.0.1 only. Standard library only.
"""
import gzip, http.server, json, os, pathlib, subprocess, threading, time, urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
STEPS = json.loads((HERE / "steps.json").read_text())
STATE = {}          # step id -> {"status", "log", "started", "ended"}
LOCK = threading.Lock()
CONFIG = {"data": os.environ.get("DATA", str(HERE / "data")), "work": os.environ.get("W", str(HERE / "work")),
          "repo": str(HERE.parent)}  # the folder that contains scripts/ (one level above ui/)

PAGE = """<!doctype html><meta charset="utf-8"><title>MVA replication</title>
<style>
body{font-family:-apple-system,system-ui,sans-serif;margin:24px auto;max-width:960px;color:#222}
h1{font-size:20px} .q{background:#f4f6f8;padding:10px 14px;border-radius:6px}
.step{border:1px solid #ddd;border-radius:6px;padding:12px 14px;margin:12px 0}
.phase{color:#666;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.st{font-weight:600} .ok{color:#1a7f37} .bad{color:#c62828} .run{color:#1f5f99} .wait{color:#888}
pre{background:#111;color:#ddd;padding:8px;max-height:220px;overflow:auto;font-size:12px;white-space:pre-wrap}
input{width:100%;padding:6px;margin:4px 0;font-family:monospace} button{padding:6px 14px}
.exp{color:#555;font-size:13px}
</style>
<h1>Replicar el analisis MVA</h1>
<div class="q" id="q"></div>
<p>Carpeta de datos: <input id="data"> Carpeta de trabajo: <input id="work"></p>
<div id="steps"></div>
<script>
async function load(){
  const r = await fetch('/api/steps'); const d = await r.json();
  document.getElementById('q').textContent = d.question;
  document.getElementById('data').value = d.config.data;
  document.getElementById('work').value = d.config.work;
  const box = document.getElementById('steps'); box.innerHTML='';
  for (const s of d.steps){
    const div = document.createElement('div'); div.className='step'; div.id='s_'+s.id;
    div.innerHTML = `<div class="phase">${s.phase}</div><div class="st">${s.title}</div>
      <div>${s.purpose}</div><div class="exp">Esperado: ${s.expect}</div>
      <div><button onclick="runStep('${s.id}')">Ejecutar</button> <span class="st wait" id="st_${s.id}">pendiente</span>
      <span class="exp">${s.minutes? '· ~'+s.minutes+' min' : ''}${s.optional? ' · opcional':''}</span></div>
      <pre id="log_${s.id}" style="display:none"></pre>`;
    box.appendChild(div);
  }
  poll();
}
async function runStep(id){
  const body = {id, data: document.getElementById('data').value, work: document.getElementById('work').value};
  await fetch('/api/run', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
}
async function poll(){
  const r = await fetch('/api/status'); const st = await r.json();
  for (const [id, s] of Object.entries(st)){
    const el = document.getElementById('st_'+id); if(!el) continue;
    const cls = {ok:'ok', fail:'bad', running:'run', pending:'wait'}[s.status] || 'wait';
    el.className = 'st '+cls;
    el.textContent = {ok:'OK', fail:'FALLO', running:'corriendo', pending:'pendiente'}[s.status] + (s.detail? ' · '+s.detail : '');
    const pre = document.getElementById('log_'+id); if (s.log){ pre.style.display='block'; pre.textContent = s.log; }
  }
  setTimeout(poll, 3000);
}
load();
</script>"""

def count_vcf(path):
    total = pas = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            if line[0] == "#":
                continue
            total += 1
            if line.split("\t", 7)[6] == "PASS":
                pas += 1
    return total, pas

def run_check(step, data, work):
    kind = step["kind"]
    if kind == "files":
        base = data if step["base"] == "data" else work
        missing = [f for f in step["files"] if not (pathlib.Path(base) / f).is_file() or (pathlib.Path(base) / f).stat().st_size == 0]
        return ("ok", "all present") if not missing else ("fail", "missing: " + ", ".join(missing))
    if kind == "check_vcf":
        path = pathlib.Path(work) / step["file"]
        if not path.is_file():
            return "fail", f"{step['file']} not found (run the DeepVariant step first)"
        total, pas = count_vcf(path)
        ok = total == step["records"] and pas == step["pass"]
        return ("ok" if ok else "fail"), f"records={total} PASS={pas} (expected {step['records']} / {step['pass']})"
    if kind == "check_sites":
        path = pathlib.Path(work) / step["file"]
        if not path.is_file():
            return "fail", "run the DeepVariant step first"
        found = []
        with gzip.open(path, "rt") as f:
            want = {(p, r, a) for p, r, a in step["sites"]}
            for line in f:
                if line[0] == "#":
                    continue
                c = line.rstrip("\n").split("\t")
                if c[0] != "chr15":
                    continue
                key = (int(c[1]), c[3], c[4])
                if key in want:
                    gt = dict(zip(c[8].split(":"), c[9].split(":"))).get("GT", "?")
                    found.append(f"{key[0]} {key[1]}>{key[2]} {c[6]} {gt}")
        ok = len(found) == len(want) and all(" PASS " in x for x in found)
        return ("ok" if ok else "fail"), "; ".join(found) or "not found"
    return "ok", ""

def run_command(step, data, work):
    env = dict(os.environ, W=work, DATA=data, DOCKER=os.environ.get("DOCKER", "docker"))
    cmd = step["cmd"]
    proc = subprocess.Popen(cmd, cwd=CONFIG["repo"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = []
    for line in proc.stdout:
        lines.append(line.rstrip())
        with LOCK:
            STATE[step["id"]]["log"] = "\n".join(lines[-80:])
    rc = proc.wait()
    return ("ok" if rc == 0 else "fail"), f"exit {rc}"

def worker(step, data, work):
    with LOCK:
        STATE[step["id"]].update(status="running", started=time.time(), detail="")
    try:
        if step["kind"] == "command":
            status, detail = run_command(step, data, work)
        elif step["kind"] == "note":
            status, detail = "ok", ""
        else:
            status, detail = run_check(step, data, work)
    except Exception as e:
        status, detail = "fail", repr(e)
    with LOCK:
        STATE[step["id"]].update(status=status, detail=detail, ended=time.time())

class Handler(http.server.BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/steps":
            self._json({"question": STEPS["question"], "steps": STEPS["steps"], "config": CONFIG})
        elif path == "/api/status":
            with LOCK:
                out = {s["id"]: dict(STATE.get(s["id"], {"status": "pending"})) for s in STEPS["steps"]}
            self._json(out)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/api/run":
            return self._json({"error": "not found"}, 404)
        n = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(n) or b"{}")
        step = next((s for s in STEPS["steps"] if s["id"] == req.get("id")), None)
        if step is None:
            return self._json({"error": "unknown step"}, 400)
        with LOCK:
            if STATE.get(step["id"], {}).get("status") == "running":
                return self._json({"error": "already running"}, 409)
            STATE[step["id"]] = {"status": "running", "log": ""}
        threading.Thread(target=worker, args=(step, req.get("data", CONFIG["data"]), req.get("work", CONFIG["work"])), daemon=True).start()
        self._json({"started": step["id"]})

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Open http://127.0.0.1:8765", flush=True)
    srv.serve_forever()
