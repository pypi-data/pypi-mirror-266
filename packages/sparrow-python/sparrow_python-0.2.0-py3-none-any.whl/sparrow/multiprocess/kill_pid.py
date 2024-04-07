import os
from typing import Tuple, List, NamedTuple
import psutil
import subprocess


class ProcessInfo(NamedTuple):
    port: int
    process: psutil.Process


def get_processes(ports: List[int]) -> List[ProcessInfo]:
    processes = set()
    for process in psutil.process_iter():
        try:
            conns = process.connections(kind="inet")
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue

        for conn in conns:
            port = conn.laddr.port
            if port in ports:
                processes.add(ProcessInfo(port=port, process=process))

    return sorted(processes, key=lambda p: p.port)


def kill_ports(ports: Tuple[int], just_view: bool = False) -> int:
    processes = get_processes(list(ports))
    if not processes:
        print(f"🙃 No processes found for the given port: {ports}")
        return False

    for pinfo in processes:
        emoji = "👁️" if just_view else "☠️🔪"
        process = pinfo.process
        if not just_view:
            process.kill()
        print(
            f"{emoji}: {process.name()} (pid {process.pid}) "
            f"on port {pinfo.port}",
        )
    return True if processes else False


def get_pid(port):
    port = int(port)
    cmd = f'lsof -t -i:{port}'
    pid = None
    try:
        pid = subprocess.check_output(cmd, shell=True)
    except Exception as e:
        print("No process running on port {} by current user. Checking if root is running the proecess".format(port))
        if pid is None:
            cmd = 'sudo lsof -t -i:{0}'.format(port)
            pid = subprocess.check_output(cmd, shell=True)
    pids = pid.decode().split("\n")
    pids_int = []
    for pid in pids:
        if pid:
            pid = int(pid)
            pids_int.append(pid)
    return pids_int


def kill_port_by_lsof(port: int):
    pids = get_pid(port)
    for pid in pids:
        try:
            os.kill(pid, 9)
            emoji = "☠️🔪"
            print(
                f"{emoji}: pid {pid} on port {port}",
            )
        except Exception as e:
            print(
                f"kill: pid {pid} failed"
            )
