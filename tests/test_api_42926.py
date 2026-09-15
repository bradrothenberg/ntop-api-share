import base64
import builtins
import contextlib
import io
import json
import socket
from types import SimpleNamespace
import pytest
import ntop_api
import block_catalog
import agent
import ntop_tcp


def fake_api(new=False):
    names=['list_variables','list_available_blocks','import_recipe','export_as_recipe','get_block_input','save_notebook_as']
    if new: names+=list(ntop_api.FEATURES_42926)
    return SimpleNamespace(**{name:lambda *args:None for name in names})


def test_feature_detection_preserves_old_surface_and_does_not_claim_version():
    assert not any(ntop_api.check_api(fake_api())['features_42926'].values())
    with pytest.raises(RuntimeError,match='Missing build-42926'):
        ntop_api.check_api(fake_api(),require_42926=True)
    assert all(ntop_api.check_api(fake_api(True),require_42926=True)['features_42926'].values())


def test_versions_are_numeric_and_overloads_survive():
    ids=['sweep<point>[5.9.0]','sweep<point>[5.10.0]','sweep<vector>[1.0.0]','sphere<point,real>']
    assert block_catalog.newest_only(ids)==['sphere<point,real>','sweep<point>[5.10.0]','sweep<vector>[1.0.0]']
    with pytest.raises(ValueError,match='narrow'):
        block_catalog.lookup(SimpleNamespace(), 'core.var<')
    with pytest.raises(ValueError,match='narrow'):
        block_catalog.lookup(SimpleNamespace(list_available_blocks=lambda _:list(range(41))), 'sweep')


def test_state_records_units_without_assuming_literal_readability():
    n=SimpleNamespace(list_block_inputs=lambda _: [{'name':'Input','isReturnValue':False},{'name':'Output','isReturnValue':True}],
        get_block_input=lambda *args:25.4,get_block_input_units=lambda *args:'mm')
    assert agent._inputs(n,'v')==[{'name':'Input','isReturnValue':False,'value':25.4,'display_units':'mm'}]
    def connected(*args):raise RuntimeError('not a literal')
    n.get_block_input=connected
    assert agent._inputs(n,'v')[0]['value_error']=='not a literal'


class FragmentedSocket:
    def __init__(self,parts):self.parts=iter(parts)
    def settimeout(self,value):pass
    def recv(self,count):return next(self.parts)


def test_prompt_handles_telnet_banner_and_fragmentation():
    conn=FragmentedSocket([b'\xff\xfb\x01\xff\xfb\x03p',b'y',b'> '])
    assert ntop_tcp.read_prompt(conn,1).endswith(b'py> ')


def test_incomplete_prompt_is_not_a_success():
    with pytest.raises(ConnectionError):
        ntop_tcp.read_prompt(FragmentedSocket([b'py',b'']),1)
    class TimedSocket(FragmentedSocket):
        def recv(self,count):raise socket.timeout()
    with pytest.raises(socket.timeout):ntop_tcp.read_prompt(TimedSocket([]),1)


def test_pid_reuse_and_wrong_executable_are_rejected(tmp_path):
    expected={'pid':10,'exe':str(tmp_path/'ntop.exe'),'start_utc_ticks':'123'}
    ntop_tcp.validate_owner(expected,expected)
    for change in [{'pid':11},{'exe':str(tmp_path/'other.exe')},{'start_utc_ticks':'124'}]:
        with pytest.raises(RuntimeError):ntop_tcp.validate_owner(expected,{**expected,**change})


def test_runner_retains_traceback_and_unicode_in_paths(tmp_path):
    completion=tmp_path/"quoted ' folder completion.json"
    exec(ntop_tcp.make_runner("raise ValueError('measurement failed')",completion),{})
    result=json.loads(completion.read_text())
    assert result['status']=='failed' and 'measurement failed' in result['traceback']


def test_partial_send_is_never_retried_and_blocks_followup(tmp_path,monkeypatch):
    monkeypatch.setattr(ntop_tcp,'ROOT',tmp_path)
    monkeypatch.setattr(ntop_tcp,'verify_interpreter',lambda *args:42)
    sends=[]
    class PartialSocket(FragmentedSocket):
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def sendall(self,data):sends.append(data);raise OSError('partial send')
    monkeypatch.setattr(ntop_tcp.socket,'create_connection',lambda *args,**kwargs:PartialSocket([b'py> ']))
    session={'pid':42};run=tmp_path/'.local'/'run1';owner=lambda *args:None
    with pytest.raises(OSError):ntop_tcp.dispatch('print(1)',session,run,owner_check=owner)
    assert len(sends)==1 and json.loads((run/'dispatch.json').read_text())['status']=='unknown'
    with pytest.raises(RuntimeError,match='unknown'):
        ntop_tcp.dispatch('print(2)',session,tmp_path/'.local'/'run2',owner_check=owner)
    assert len(sends)==1


def test_completed_socket_runner_is_reported_and_failed_script_is_not_success(tmp_path,monkeypatch):
    monkeypatch.setattr(ntop_tcp,'ROOT',tmp_path)
    monkeypatch.setattr(ntop_tcp,'verify_interpreter',lambda *args:42)
    class RunningSocket(FragmentedSocket):
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def sendall(self,data):exec(data.decode(),{})
    monkeypatch.setattr(ntop_tcp.socket,'create_connection',lambda *args,**kwargs:RunningSocket([b'py> ']))
    result=ntop_tcp.dispatch('raise ValueError("native failure")',{'pid':42},tmp_path/'.local'/'run',owner_check=lambda *args:None)
    assert result['status']=='failed'
    assert not (tmp_path/'.local/tcp-42.pending.json').exists()


class ConsoleSocket:
    """Execute the real probe and runner against a controlled fake interpreter."""
    def __init__(self,pid,identity='valid',fragment=False):
        self.pid=pid;self.identity=identity;self.fragment=fragment
        self.pending=[b'py> '];self.sent=[];self.closed=False
    def __enter__(self):return self
    def __exit__(self,*args):self.closed=True
    def settimeout(self,value):pass
    def recv(self,count):
        if self.identity=='timeout' and self.sent:raise socket.timeout()
        return self.pending.pop(0) if self.pending else b''
    def sendall(self,data):
        self.sent.append(data)
        original_import=builtins.__import__
        def controlled_import(name,*args,**kwargs):
            return SimpleNamespace(getpid=lambda:self.pid) if name=='os' else original_import(name,*args,**kwargs)
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(data.decode('ascii'),{'__builtins__':{**vars(builtins),'__import__':controlled_import}})
        response=output.getvalue().encode()
        if len(self.sent)==1:
            if self.identity=='duplicate':response+=response
            if self.identity=='echo_only':response=b''
            if self.identity=='stale':response=b'NTOP_SESSION_previous_PID_42\n'
        response=data+response+b'py> '
        self.pending.extend([response[i:i+3] for i in range(0,len(response),3)] if self.fragment else [response])


@pytest.mark.parametrize('actual_pid,identity',[(43,'valid'),(42,'duplicate'),(42,'echo_only'),(42,'stale'),(42,'timeout')])
def test_socket_identity_failure_never_sends_notebook_command(tmp_path,monkeypatch,actual_pid,identity):
    monkeypatch.setattr(ntop_tcp,'ROOT',tmp_path)
    conn=ConsoleSocket(actual_pid,identity=identity)
    connections=[]
    def connect(*args,**kwargs):connections.append(conn);return conn
    monkeypatch.setattr(ntop_tcp.socket,'create_connection',connect)
    forbidden=tmp_path/'wrong-session-mutation.txt'
    with pytest.raises((RuntimeError,socket.timeout)):
        ntop_tcp.dispatch(f"open({str(forbidden)!r},'w').write('changed')",{'pid':42},tmp_path/'.local'/'run',owner_check=lambda *args:None)
    assert not forbidden.exists()
    assert len(connections)==1 and len(conn.sent)==1 and conn.closed
    receipt=json.loads((tmp_path/'.local/run/dispatch.json').read_text())
    assert receipt['status']=='not_dispatched'
    assert not (tmp_path/'.local/run/completion.json').exists()
    assert not (tmp_path/'.local/tcp-42.pending.json').exists()


def test_socket_identity_and_notebook_command_use_one_connection(tmp_path,monkeypatch):
    monkeypatch.setattr(ntop_tcp,'ROOT',tmp_path)
    conn=ConsoleSocket(42,fragment=True)
    connections=[];owner_checks=[]
    def connect(*args,**kwargs):connections.append(conn);return conn
    monkeypatch.setattr(ntop_tcp.socket,'create_connection',connect)
    def owner(*args):owner_checks.append(len(conn.sent))
    result=ntop_tcp.dispatch('print("model command completed")',{'pid':42},tmp_path/'.local'/'run',owner_check=owner)
    assert result['status']=='completed' and result['interpreter_pid']==42
    assert len(connections)==1 and len(conn.sent)==2 and conn.closed
    assert owner_checks==[0,1]
    assert not (tmp_path/'.local/tcp-42.pending.json').exists()


def test_host_owner_change_after_socket_probe_rejects_notebook_command(tmp_path,monkeypatch):
    monkeypatch.setattr(ntop_tcp,'ROOT',tmp_path)
    conn=ConsoleSocket(42)
    monkeypatch.setattr(ntop_tcp.socket,'create_connection',lambda *args,**kwargs:conn)
    def owner(*args):
        if conn.sent:raise RuntimeError('Process creation time changed')
    with pytest.raises(RuntimeError,match='creation time'):
        ntop_tcp.dispatch('print("must not run")',{'pid':42},tmp_path/'.local'/'run',owner_check=owner)
    assert len(conn.sent)==1 and conn.closed
