"""Dispatch once to an owned build-42926 loopback console with durable receipts."""
from pathlib import Path
import argparse
import base64
import json
import os
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]

def validate_owner(expected, actual):
    if int(expected['pid']) != int(actual['pid']):
        raise RuntimeError('Listener PID differs from the selected process')
    if os.path.normcase(os.path.abspath(expected['exe'])) != os.path.normcase(os.path.abspath(actual['exe'])):
        raise RuntimeError('Listener executable differs from the selected process')
    if str(expected['start_utc_ticks']) != str(actual['start_utc_ticks']):
        raise RuntimeError('Process creation time changed; the PID may have been reused')
    if Path(actual['exe']).name.lower() != 'ntop.exe':
        raise RuntimeError('The selected executable is not ntop.exe')

def verify_owner(session, port):
    if os.name != 'nt':
        raise RuntimeError('Process ownership verification requires Windows')
    port = int(port)
    if not 1 <= port <= 65535:
        raise ValueError('Invalid port')
    code = rf"""
$ErrorActionPreference='Stop'
$owners=@(Get-NetTCPConnection -State Listen -LocalPort {port} | Where-Object {{$_.LocalAddress -eq '127.0.0.1'}} | Select-Object -ExpandProperty OwningProcess -Unique)
if($owners.Count -ne 1){{throw 'Expected exactly one loopback listener'}}
$proc=Get-Process -Id $owners[0]
@{{pid=$proc.Id;exe=$proc.Path;start_utc_ticks=$proc.StartTime.ToUniversalTime().Ticks.ToString()}} | ConvertTo-Json -Compress
"""
    completed = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',code],
                               check=True, capture_output=True, text=True, timeout=15)
    actual = json.loads(completed.stdout)
    validate_owner(session, actual)
    return actual

def read_prompt(connection, timeout):
    """Require the entire fragmented initial prompt; never swallow a timeout."""
    deadline = time.monotonic() + timeout
    output = bytearray()
    while not output.endswith(b'py> '):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('No complete console prompt')
        connection.settimeout(remaining)
        chunk = connection.recv(4096)
        if not chunk:
            raise ConnectionError('Console closed before its prompt')
        output.extend(chunk)
        if len(output) > 1024*1024:
            raise RuntimeError('Unexpectedly large console banner')
    return bytes(output)

def make_runner(command, completion):
    # The runner writes a local receipt even if the TCP client disconnects.
    return f"""import json as _receipt_json, traceback as _receipt_tb
_receipt_result = {{'status':'completed'}}
try:
    exec(compile({command!r}, '<owned-notebook-command>', 'exec'), globals())
except BaseException:
    _receipt_result = {{'status':'failed', 'traceback':_receipt_tb.format_exc()}}
with open({str(completion)!r}, 'x', encoding='utf-8') as _receipt_file:
    _receipt_json.dump(_receipt_result, _receipt_file, indent=2)
"""

def dispatch(command, session, run_dir, *, port=2323, timeout=30.0, owner_check=verify_owner):
    if timeout <= 0:
        raise ValueError('Timeout must be positive')
    run_dir = Path(run_dir).resolve()
    if not run_dir.is_relative_to(ROOT / '.local'):
        raise ValueError('Keep TCP run directories beneath this checkout\'s .local folder')
    owner_check(session, port)
    # One unresolved dispatch per process for this checkout. Other clients must not send concurrently.
    lock = ROOT / '.local' / f"tcp-{int(session['pid'])}.pending.json"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        previous = json.loads(lock.read_text(encoding='utf-8'))
        prior_completion = Path(previous['completion'])
        if not prior_completion.is_file():
            raise RuntimeError(f'Prior dispatch outcome is unknown. Inspect {lock}')
        prior = json.loads(prior_completion.read_text(encoding='utf-8'))
        if prior.get('status') not in {'completed','failed'}:
            raise RuntimeError('Invalid prior completion; inspect it before continuing')
        lock.unlink()
    run_dir.mkdir(parents=True, exist_ok=False)
    completion = run_dir / 'completion.json'
    with lock.open('x',encoding='utf-8') as handle:
        json.dump({'completion':str(completion),'session':session},handle,indent=2)
    (run_dir/'command.py').write_text(command,encoding='utf-8')
    runner = make_runner(command, completion)
    (run_dir/'runner.py').write_text(runner,encoding='utf-8')
    # Base64 avoids quoting and newline ambiguity in the one-line console protocol.
    payload = base64.b64encode(runner.encode('utf-8')).decode('ascii')
    launch = f"exec(compile(__import__('base64').b64decode('{payload}'), '<receipt-runner>', 'exec'))\n"
    record = {'status':'not_dispatched','session':session,'port':port}
    transcript = bytearray()
    attempted = False
    try:
        with socket.create_connection(('127.0.0.1',port),timeout=timeout) as connection:
            transcript.extend(read_prompt(connection,timeout))
            owner_check(session,port)
            # A send error can still follow partial delivery. Do not retry it.
            attempted = True
            record['status'] = 'unknown'
            connection.sendall(launch.encode('ascii'))
            deadline = time.monotonic()+timeout
            while not completion.exists():
                remaining = deadline-time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Completion is unknown; inspect completion.json later. Do not resubmit.')
                connection.settimeout(min(remaining,0.25))
                try:
                    chunk=connection.recv(65536)
                    if not chunk:
                        raise ConnectionError('Console disconnected; inspect the completion file before any retry')
                    transcript.extend(chunk)
                except socket.timeout:
                    continue
            # A writer can create the file before its final bytes arrive.
            while True:
                try:
                    record.update(json.loads(completion.read_text(encoding='utf-8')))
                    break
                except json.JSONDecodeError:
                    if time.monotonic()>=deadline:
                        raise TimeoutError('Incomplete receipt; outcome requires inspection')
                    time.sleep(0.05)
    except Exception as exc:
        record['transport_error']=str(exc)
        raise
    finally:
        (run_dir/'transcript.txt').write_text(transcript.decode('utf-8',errors='replace'),encoding='utf-8')
        (run_dir/'dispatch.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        if not attempted or record['status'] in {'completed','failed'}:
            lock.unlink(missing_ok=True)
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session',type=Path,required=True)
    parser.add_argument('--file',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--port',type=int,default=2323)
    parser.add_argument('--timeout',type=float,default=30)
    args=parser.parse_args()
    result=dispatch(args.file.read_text(encoding='utf-8-sig'),json.loads(args.session.read_text(encoding='utf-8-sig')),
                    args.run_dir,port=args.port,timeout=args.timeout)
    print(json.dumps(result,indent=2))
    return result['status']!='completed'

if __name__=='__main__':
    raise SystemExit(main())
