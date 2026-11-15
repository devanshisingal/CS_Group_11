import subprocess
import sys
import time


def main() -> None:
    commands = [
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "localhost", "--port", "8000"],
        [sys.executable, "-m", "uvicorn", "backend.attacker_lab:app", "--host", "127.0.0.1", "--port", "8001"],
    ]
    processes = []
    try:
        for command in commands:
            processes.append(subprocess.Popen(command))
        print("SecureBank: http://localhost:8000/login")
        print("Read-only CSRF threat model: http://127.0.0.1:8001/")
        while all(process.poll() is None for process in processes):
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            process.wait()


if __name__ == "__main__":
    main()
