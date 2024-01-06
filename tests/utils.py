import subprocess

def sh(cmd, cwd="tests/data"):
    raw_out = subprocess.check_output(f'cd {cwd} && ' + cmd + ' 2>&1 | cat', stderr=subprocess.STDOUT, shell=True).decode()
    return [line[2:] if line.startswith("$ ") else line for line in raw_out.splitlines()]
