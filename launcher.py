"""One-click Windows launcher. Setup is isolated; existing models and games are kept."""
import datetime
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parent
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def environment_python(root):
    return root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def has_interface(python):
    try:
        return subprocess.run(
            [str(python), '-c', 'from PySide6 import QtWidgets, QtMultimedia, QtSvg'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=NO_WINDOW, timeout=30,
        ).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def prepare_environment(root, run, status):
    """Reuse an installed interface; only install when it cannot import."""
    python = environment_python(root)
    if not python.exists():
        status('1 of 2 · Preparing your private app environment…')
        run([sys.executable, '-m', 'venv', str(root / '.venv')])
    if not has_interface(python):
        status('2 of 2 · Installing the interface. First setup needs internet…')
        run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
             '--progress-bar', 'off', '-r', str(root / 'requirements.txt')])
        if not has_interface(python):
            raise RuntimeError('The desktop interface could not load. See startup.log for details.')
    return python


def install_game_support(root, python, run, status):
    status('1 of 3 · Installing CPU sports-review packages. This can take several minutes…')
    run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
         '--progress-bar', 'off', 'torch', 'torchvision',
         '--index-url', 'https://download.pytorch.org/whl/cpu'])
    status('2 of 3 · Installing video and speech support…')
    run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
         '--progress-bar', 'off', '-r', str(root / 'requirements-local.txt')])
    status('3 of 3 · Downloading pretrained game files…')
    run([str(python), '-u', '-c',
         'from local_ai import download_models; download_models(print)'])


def desktop_shortcut(root, log):
    """Point the Windows desktop shortcut at this folder; paths are data, not PS code."""
    if os.name != 'nt':
        return
    env = os.environ.copy()
    env['LAMATNA_FOLDER'] = str(root)
    script = (
        "$ErrorActionPreference='Stop'; "
        "$desktop=[Environment]::GetFolderPath('Desktop'); "
        "if (-not $desktop) { exit 0 }; "
        "$shell=New-Object -ComObject WScript.Shell; "
        "$shortcut=$shell.CreateShortcut((Join-Path $desktop 'Lamatna.lnk')); "
        "$shortcut.TargetPath=Join-Path $env:LAMATNA_FOLDER 'Lamatna.bat'; "
        "$shortcut.WorkingDirectory=$env:LAMATNA_FOLDER; "
        "$shortcut.Description='Family sport, together'; "
        "$shortcut.Save()"
    )
    try:
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                       env=env, stdout=log, stderr=log, creationflags=NO_WINDOW, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        log.write('\nDesktop shortcut unavailable; Lamatna.bat still works.\n')


def main():
    import tkinter as tk
    from tkinter import ttk, messagebox
    window = tk.Tk()
    window.title('Lamatna · Family sport, together')
    window.geometry('540x320')
    window.resizable(False, False)
    window.configure(bg='#F7F3EB')
    events = queue.Queue()
    cancelled = threading.Event()
    process = [None]
    opened = [False]
    tk.Label(window, text='Lamatna  ·  لمّتنا', font=('Segoe UI', 23, 'bold'),
             fg='#234D42', bg='#F7F3EB').pack(pady=(25, 5))
    tk.Label(window, text='Family sport, together.', font=('Segoe UI', 12),
             fg='#68786D', bg='#F7F3EB').pack()
    status = tk.StringVar(value='Getting your game day ready…')
    tk.Label(window, textvariable=status, wraplength=490, font=('Segoe UI', 11),
             fg='#243F36', bg='#F7F3EB').pack(padx=20, pady=16)
    progress = ttk.Progressbar(window, mode='indeterminate', length=460)
    progress.pack()
    progress.start(12)
    detail = tk.StringVar(value='Your installed packages, models and saved games are kept.')
    tk.Label(window, textvariable=detail, font=('Segoe UI', 9), fg='#68786D',
             bg='#F7F3EB', wraplength=490).pack(pady=12)

    def close():
        if opened[0]:
            window.destroy()
            return
        if messagebox.askyesno('Cancel setup?', 'Stop preparing Lamatna? You can open it again later.'):
            cancelled.set()
            if process[0] is not None:
                process[0].terminate()
            window.destroy()
    window.protocol('WM_DELETE_WINDOW', close)

    def worker():
        try:
            (ROOT / '.local').mkdir(exist_ok=True)
            with (ROOT / '.local/startup.log').open('a', encoding='utf-8') as log:
                log.write('\n--- Lamatna start ' + datetime.datetime.now().isoformat() + ' ---\n')
                log.flush()

                def run(args):
                    if cancelled.is_set():
                        raise RuntimeError('Setup cancelled.')
                    process[0] = subprocess.Popen(args, cwd=str(ROOT), stdout=log,
                                                  stderr=log, stdin=subprocess.DEVNULL,
                                                  creationflags=NO_WINDOW)
                    result = process[0].wait()
                    process[0] = None
                    if result:
                        raise RuntimeError('Setup could not finish. Check your internet connection and startup.log, then try again.')

                python = prepare_environment(ROOT, run, lambda value:events.put(('status', value)))
                if '--install-game-support' in sys.argv:
                    install_game_support(ROOT, python, run, lambda value:events.put(('status', value)))
                if cancelled.is_set():
                    return
                desktop_shortcut(ROOT, log)
                events.put(('status', 'Opening your family sports hub…'))
                process[0] = subprocess.Popen([str(python), str(ROOT / 'app.py')],
                    cwd=str(ROOT), stdout=log, stderr=log, creationflags=NO_WINDOW)
                events.put(('opened', ''))
                result = process[0].wait()
                process[0] = None
                if result:
                    raise RuntimeError('Lamatna closed with an error. Open .local/startup.log for the details.')
                events.put(('done', ''))
        except Exception as exc:
            if not cancelled.is_set():
                events.put(('error', str(exc)))

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'status':
                    status.set(value)
                elif kind == 'opened':
                    opened[0] = True
                    window.withdraw()
                elif kind == 'done':
                    window.destroy()
                    return
                elif kind == 'error':
                    window.deiconify()
                    progress.stop()
                    status.set('We could not open Lamatna yet.')
                    detail.set(value)
                    messagebox.showerror('Lamatna needs attention', value)
                    ttk.Button(window, text='Open setup log', command=lambda:os.startfile(str(ROOT / '.local/startup.log'))).pack()
                    opened[0] = True
        except queue.Empty:
            pass
        window.after(150, poll)
    threading.Thread(target=worker, daemon=True).start()
    poll()
    window.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(error), 'Lamatna could not start', 0x10)
        else:
            raise
