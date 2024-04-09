# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

# CAVEAT: executes ONLY on windows !

import platform
import argparse
import termcolor
import requests
import shutil
import re
import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from piwiPre.pwpVersion import PwpVersion
from piwiPre.pwpLogoSmall import pwpLogo_png

import winreg
import getpass
import zipfile
import json
import subprocess

import tkinter
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.font

import ctypes
from ctypes import POINTER, c_ulong, c_char_p, c_int, c_void_p
from ctypes.wintypes import HANDLE, BOOL, DWORD, HWND, HINSTANCE, HKEY
from ctypes import windll

# Constant definitions

SEE_MASK_NOCLOSEPROCESS = 0x00000040        # noqa
SEE_MASK_NO_CONSOLE = 0x00008000

# Type definitions

PHANDLE = ctypes.POINTER(HANDLE)           # noqa
PDWORD = ctypes.POINTER(DWORD)             # noqa


class ShellExecuteInfo(ctypes.Structure):
    _fields_ = [
        ('cbSize',       DWORD),
        ('fMask',        c_ulong),
        ('hwnd',         HWND),
        ('lpVerb',       c_char_p),
        ('lpFile',       c_char_p),
        ('lpParameters', c_char_p),
        ('lpDirectory',  c_char_p),
        ('nShow',        c_int),
        ('hInstApp',     HINSTANCE),
        ('lpIDList',     c_void_p),
        ('lpClass',      c_char_p),
        ('hKeyClass',    HKEY),
        ('dwHotKey',     DWORD),
        ('hIcon',        HANDLE),
        ('hProcess',     HANDLE)]

    def __init__(self, **kw):
        super(ShellExecuteInfo, self).__init__()
        self.cbSize = ctypes.sizeof(self)
        for field_name, field_value in kw.items():
            setattr(self, field_name, field_value)


PShellExecuteInfo = POINTER(ShellExecuteInfo)


# Function definitions

ShellExecuteEx = windll.shell32.ShellExecuteExA
ShellExecuteEx.argtypes = (PShellExecuteInfo, )                  # noqa
ShellExecuteEx.restype = BOOL

WaitForSingleObject = windll.kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = (HANDLE, DWORD)                   # noqa
WaitForSingleObject.restype = DWORD

CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = (HANDLE, )                                # noqa
CloseHandle.restype = BOOL


# At last, the actual implementation!

# patch: execute the SAME python interpreter with the same cmdline arguments
#        so rely on orig_argv rather than argv
# patch: add --user username, to remember who was the user


def elevate(show_console=True):
    if windll.shell32.IsUserAnAdmin():
        return
    username = getpass.getuser()
    args = sys.orig_argv or sys.argv
    params = ShellExecuteInfo(
        fMask=SEE_MASK_NOCLOSEPROCESS | SEE_MASK_NO_CONSOLE,
        hwnd=None,
        lpVerb=b'runas',
        lpFile=args[0].encode('cp1252'),  # lpFile=sys.executable.encode('cp1252'),
        lpParameters=subprocess.list2cmdline(args[1:]+['--user', username]).encode('cp1252'),
        nShow=int(show_console))
    try:
        if not ShellExecuteEx(ctypes.byref(params)):
            raise ctypes.WinError()
    except OSError as e:
        print(f"OS Error {e}")
    handle = params.hProcess

    ret = DWORD()
    WaitForSingleObject(handle, -1)
    if windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(ret)) == 0:
        raise ctypes.WinError()
    CloseHandle(handle)
    sys.exit(ret.value)


class PwpUi:
    def __init__(self, args, installer):
        self.installer = installer
        self.root = tkinter.Tk()
        self.root.title("piwiPre installer")
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.grid()
        self.args = args

        self.do_piwipre = tkinter.IntVar()
        self.do_mariadb = tkinter.IntVar()
        self.do_ffmpeg = tkinter.IntVar()
        self.do_mode = tkinter.StringVar()
        self.do_progress = tkinter.IntVar()
        self.do_msg = tkinter.StringVar()
        self.doc_url = "https://fabien_battini.gitlab.io/piwipre/html/"
        # self.piwipre_version = tkinter.StringVar()

        row = 0
        # CAVEAT: logo MUST be stored in an attribute, otherwise it is garbage collected !
        self.logo = pwpLogo_png.tk_photo()
        tkinter.Label(self.frm, image=self.logo).grid(column=0, row=row, sticky="W")

        title_font = tkinter.font.Font(size=15, family="Helvetica", weight="bold")
        lab = ttk.Label(self.frm, font=title_font,
                        text=f"------------- PiwiPre installer for Windows version {PwpVersion.spec} -------------\n")
        lab.grid(column=1, row=row, columnspan=5)

        row += 1
        ttk.Label(self.frm, text="Elevation enabled :", anchor="w", padding=4,
                  ).grid(column=0, row=row, columnspan=2, sticky="W")
        ttk.Label(self.frm, text=str(not self.installer.args.no_elevation), anchor="w",
                  ).grid(column=2, row=row, columnspan=2, sticky="W")

        row += 1
        ttk.Label(self.frm, text="Current Working Directory :", anchor="w", padding=4,
                  ).grid(column=0, row=row, columnspan=4, sticky="W")
        ttk.Label(self.frm, text=os.getcwd(), anchor="w",
                  ).grid(column=2, row=row, columnspan=2, sticky="W")

        row += 1
        ttk.Label(self.frm, text=f"Latest piwiPre version :", anchor="w", padding=4,
                  ).grid(column=0, row=row, columnspan=4, sticky="W")
        self.pwp_target_version = ttk.Label(self.frm, text=installer.piwipre_target_version)
        self.pwp_target_version.grid(column=2, row=row, columnspan=4, sticky="W")

        row += 1
        tkinter.Frame(self.frm, width=850, height=5, relief='sunken', background="#cccdddccc",
                      ).grid(column=0, row=row, columnspan=4)

        row += 1
        ttk.Label(self.frm, text=f"piwiPre EXE version in target dir:", anchor="w", padding=4,
                  ).grid(column=0, row=row, columnspan=4, sticky="W")
        self.pwp_version = ttk.Label(self.frm, text=installer.piwipre_version)
        self.pwp_version.grid(column=2, row=row, columnspan=4, sticky="W")

        row += 1
        ttk.Label(self.frm, text=f"ffmpeg installed version : ", anchor="w", padding=4,
                  ).grid(column=0, row=row, columnspan=4, sticky="W")
        self.ffmpeg_version = ttk.Label(self.frm, text=installer.ffmpeg_version, padding=4,)
        self.ffmpeg_version.grid(column=2, row=row, columnspan=4, sticky="W")

        row += 1
        ttk.Label(self.frm, text="piwiPre exe", anchor="w", padding=4,
                  ).grid(column=0, row=row, sticky="W")
        self.pwp_button = ttk.Checkbutton(self.frm, text="install", width=10,
                                          variable=self.do_piwipre)
        self.pwp_button.grid(column=1, row=row)

        self.pwp_path = ttk.Label(self.frm, text="",
                                  padding=4, width=90,  # background="light grey",
                                  anchor="w")
        self.pwp_path.grid(column=2, row=row)

        row += 1
        ttk.Label(self.frm, text="ffmpeg exe", anchor="w", padding=4,
                  ).grid(column=0, row=row, sticky="W")
        self.ffmpeg_button = ttk.Checkbutton(self.frm, text="install", width=10,
                                             variable=self.do_ffmpeg)
        self.ffmpeg_button.grid(column=1, row=row)

        self.ffmpeg_path = ttk.Label(self.frm, text="",
                                     padding=4,  width=90,  # background="light grey",
                                     anchor="w")
        self.ffmpeg_path.grid(column=2, row=row)

        row += 1
        ttk.Label(self.frm, text="MariaDB CC", anchor="w", padding=4,
                  ).grid(column=0, row=row, sticky="W")
        self.maria_button = ttk.Checkbutton(self.frm, text="install", width=10,
                                            variable=self.do_mariadb)
        self.maria_button.grid(column=1, row=row)

        row += 1
        tkinter.Frame(self.frm, width=850, height=10,
                      ).grid(column=0, row=row, columnspan=4)

        row += 1
        ttk.Radiobutton(self.frm, value="test", text="test", command=self.refresh_default_values,
                        variable=self.do_mode).grid(column=0, row=row, sticky="W")
        ttk.Radiobutton(self.frm, value="install", text="install", command=self.refresh_default_values,
                        variable=self.do_mode,).grid(column=1, row=row, sticky="W")

        tkinter.Button(self.frm, text="Run", command=self.run,
                       background="green", foreground="white",
                       activebackground="white", activeforeground="green"
                       ).grid(column=2, row=row, sticky="W")
        tkinter.Button(self.frm, text="  Quit  ", command=self.exit,
                       background="red", foreground="white",
                       activebackground="white", activeforeground="red").grid(column=3, row=row, sticky="W")

        row += 1
        tkinter.Frame(self.frm, width=850, height=10,
                      ).grid(column=0, row=row, columnspan=4)

        row += 1
        self.action = ttk.Label(self.frm, text="Downloader: idle", width=30, anchor="w", padding=4, )
        self.action.grid(column=0, row=row, columnspan=2, sticky="W")

        self.progress = ttk.Progressbar(self.frm, orient="horizontal", variable=self.do_progress,
                                        mode="determinate", length=550, maximum=100)
        self.progress.grid(column=2, row=row)
        self.action2 = tkinter.Label(self.frm, text="", width=30, anchor="w")
        self.action2.grid(column=3, row=row, columnspan=2, sticky="W")

        row += 1
        tkinter.Frame(self.frm, width=850, height=10,
                      ).grid(column=0, row=row, columnspan=4)
        row += 1
        ttk.Label(self.frm, text="Feedback from the installer",
                  padding=4,
                  anchor="w").grid(column=0, row=row, columnspan=5)

        row += 1
        font = tkinter.font.Font(size=10, family="Helvetica")
        self.msg = scrolledtext.ScrolledText(self.frm, background="#ccccccccc",
                                             padx=3, pady=3,
                                             font=font,
                                             width=100, height=10,
                                             )
        self.msg.grid(column=0, row=row, columnspan=5)
        self.msg.tag_config('warning', foreground="red")
        #
        row += 1
        tkinter.Frame(self.frm, width=850, height=5,
                      ).grid(column=0, row=row, columnspan=4)
        #
        row += 1
        ttk.Label(self.frm, text="Minimal help",
                  padding=4,
                  anchor="w").grid(column=0, row=row, columnspan=5)
        row += 1
        help_msg = """
        piwiPre Installer is available only for windows
        run piwiPreInstaller --help for the full help
        
        it can install:
        - piwiPre.exe, the application version of piwiPre that does NOT require python
          it will be installed in the system folders,
          and inserted in the PATH, so that you can run it from anywhere
        - ffmpeg.exe, the well-known tool used by piwiPre to manage VIDEO.
          If you do not need video, installing it is useless
        - MariaDB C Connector. It may be used is some cases to access to the remote SQL database of piwiGo.
          This is normally NOT required, unless piwiPre complains about its absence.
        
        In "test" mode, installation occurs in the current directory
        In "install" mode, installation proceeds normally
        
        """
        ttk.Label(self.frm, text=help_msg, width=100,).grid(column=0, row=row, columnspan=5)

        row += 1
        ttk.Label(self.frm, text="Documentation :", anchor="w",
                  ).grid(column=0, row=row, columnspan=2, sticky="W")

        ttk.Label(self.frm, text=self.doc_url, anchor="w",
                  ).grid(column=2, row=row, columnspan=2, sticky="W")
        tkinter.Button(self.frm, text="Copy URL", command=self.open_url,
                       activebackground="white", activeforeground="green"
                       ).grid(column=3, row=row, sticky="W")

        self.from_python_to_ui()

    def main_loop(self):
        self.root.mainloop()
        self.root.destroy()

    def refresh_default_values(self):
        self.from_ui_to_python()
        self.installer.compute_default_values()
        self.from_python_to_ui()

    def from_python_to_ui(self):
        self.installer.compute_default_values()
        self.do_piwipre.set(1 if self.installer.args.piwipre else 0)
        self.do_mariadb.set(1 if self.installer.args.mariadb else 0)
        self.do_ffmpeg.set(1 if self.installer.args.ffmpeg else 0)
        self.do_mode.set(self.installer.args.mode)

        self.pwp_button['text'] = "re install" if self.installer.piwipre_exists else "install"

        self.pwp_version['text'] = self.installer.piwipre_version or ''
        self.pwp_path['text'] = self.installer.piwipre_path

        if self.installer.ffmpeg_exists:
            self.ffmpeg_button['text'] = "re install"
        else:
            self.ffmpeg_button['text'] = "install"
        self.ffmpeg_version['text'] = self.installer.ffmpeg_version or ''
        self.ffmpeg_path['text'] = self.installer.ffmpeg_path
        self.do_progress.set(0)
        self.set_action("Downloader: idle", "")

    def from_ui_to_python(self):
        self.args.piwipre = self.do_piwipre.get() == 1
        self.args.ffmpeg = self.do_ffmpeg.get() == 1
        self.args.mariadb = self.do_mariadb.get() == 1
        self.args.mode = self.do_mode.get()
        pass

    def run(self):
        self.from_ui_to_python()
        self.installer.run()

    def add_msg(self, line, tag=None):
        if tag is None:
            self.msg.insert(tkinter.END, line)
        else:
            self.msg.insert(tkinter.END, line, tag)

    def exit(self):
        self.root.destroy()

    def set_action(self, line1, line2=""):
        self.action["text"] = line1
        self.action2["text"] = line2

    def set_progress(self, val):
        self.do_progress.set(int(val))
        self.root.update()
        self.root.update_idletasks()

    def open_url(self):
        self.frm.clipboard_clear()
        self.frm.clipboard_append(self.doc_url)
        self.frm.update()


class Installer:
    def __init__(self, arguments=None):
        self.progress_status = 0
        self.ui = None
        if platform.system() != "Windows":
            self.warning("--install-exe can be used only on Windows!")
            exit(-1)

        self.user_key = None
        arguments = arguments or []

        parser = argparse.ArgumentParser(description='install piwiPre on computer')
        parser.add_argument('--text-only',
                            help="does not display the graphical UI",
                            action='store_true')

        parser.add_argument('--user',
                            help="Install for user. This is for internal use only, not to be used by humans")
        parser.add_argument('--no-elevation',
                            help="Does not run privilege elevation, so install will probably fail",
                            action='store_true')
        parser.add_argument('--ffmpeg',
                            help="Install ffmpeg.exe",
                            action='store_true')
        parser.add_argument('--piwipre',
                            help="Install piwiPre.exe",
                            action='store_true')
        parser.add_argument('--mariadb',
                            help="Install mariaDb connector",
                            action='store_true')

        parser.add_argument('--force',
                            help="forces a new install of up to date packages (only for command-line)",
                            action='store_true')

        parser.add_argument('--mode',
                            help="test: run in separate dir, install: normal install",
                            action='store',
                            choices=['test', 'install'],
                            default="install")

        parser.add_argument('--chdir',
                            help="new directory to change to",
                            action='store')
        self.args = parser.parse_args(arguments)

        if self.args.chdir:
            self.makedirs(self.args.chdir)
            os.chdir(self.args.chdir)

        self.ffmpeg_path = None
        self.ffmpeg_exists = False
        self.ffmpeg_version = None

        self.piwipre_version = None
        self.piwipre_target_version = None
        self.piwipre_path = None
        self.piwipre_exists = False

        self.compute_default_values()

        if self.args.text_only:
            self.run()
        else:
            self.ui = PwpUi(self.args, installer=self)
            self.ui.main_loop()

    def compute_default_values(self):
        self.ffmpeg_version = None
        self.ffmpeg_path = os.getcwd() if self.args.mode == "test" else (os.environ['PROGRAMFILES(X86)'] + '\\ffmpeg')  # noqa

        self.ffmpeg_exists = (os.path.isfile(f"{self.ffmpeg_path}\\bin\\ffmpeg.exe") and
                              os.path.isfile(f"{self.ffmpeg_path}\\bin\\ffprobe.exe"))

        if self.ffmpeg_exists:
            self.action("Checking FFMPEG version", "ongoing")
            target = f"{self.ffmpeg_path}/bin/ffmpeg.exe"
            try:
                res = subprocess.run([target, "-version"], capture_output=True)
                buffer = res.stdout.decode('utf8')
                # ffmpeg version N-111004-g4893cbcaba-gb1c3d81e71+12 Copyright (c) 2000-2023 the FFmpeg developers  # noqa
                m = re.match(r".*ffmpeg version (.*) Copyright .*", buffer)
                if m:
                    self.ffmpeg_version = m.group(1)
            except subprocess.CalledProcessError as e:
                self.error(f"Error {e} while ffmpeg --version")

            if self.ui is None:
                self.msg(f"ffmpeg {self.ffmpeg_version} is already installed in '{self.ffmpeg_path}' ")
                if self.args.mode != "test":
                    self.msg("use --force to force new install")
                    self.args.ffmpeg = False
            self.action("", "")

        self.piwipre_path = os.getcwd() if self.args.mode == "test" else (os.environ['PROGRAMFILES(X86)'] + '\\piwiPre')  # noqa
        self.piwipre_exists = False
        self.piwipre_version = None

        if self.piwipre_target_version is None:
            pack = self.get_latest_package()
            self.piwipre_target_version = pack["version"]

        target = f"{self.piwipre_path}\\piwiPre.exe"

        if not os.path.isfile(target):
            return

        # HACK:
        # Do NOT ask me why!
        # when the exe is in "Program Files (x86)"
        # it is mandatory to have shell=True if we have stdout=subprocess.PIPE
        # otherwise run fails.
        # but, shell=True is NOT mandatory
        #   - if we do NOT have   stdout=subprocess.PIPE
        #   - OR if the exe is in a user directory
        # rather strange, and not so much documented.

        self.action("Checking PiwiPre installed version", "ongoing")
        try:
            res = subprocess.run([target, "--version", "--quiet"],
                                 stdout=subprocess.PIPE, shell=True,
                                 check=True, text=True)  # noqa
            buffer = res.stdout
            # current version: '0.17 at 03/30/2024 18:32:06'
            m = re.match(r"current version: '(.*)'", buffer)
            if m:
                self.piwipre_version = m.group(1)
        except OSError as e:
            self.warning(f"Error {e} while piwiPre --version")
            return False

        if self.piwipre_version is None:
            return
        self.action("", "")

        m = re.match(r"([\d.]*)", self.piwipre_version)
        self.piwipre_exists = m.group(1) >= self.piwipre_target_version

        if self.args.piwipre and self.ui is None:
            self.msg(f"piwiPre is already installed in '{self.piwipre_path}' " +
                     f" with version {self.piwipre_version}")
            if self.args.mode != "test":
                self.msg(f"use --force to force new install")
                self.args.piwipre = False

    def action(self, line1, line2=""):
        if self.ui:
            self.ui.set_action(line1, line2)

    def warning(self, line):
        if self.ui:
            self.ui.add_msg("WARNING: " + line + '\n', "warning")

        print(termcolor.colored("WARNING: " + line, color='red', force_color=True))

    def error(self, line):
        if self.ui:
            self.ui.add_msg("ERROR  : " + line + '\n', "warning")
        else:
            print(termcolor.colored("ERROR  : " + line, color='red', force_color=True))
            input("Close window after error?")
            exit(-1)

    def msg(self, line):
        if self.ui:
            self.ui.add_msg(line + "\n")
        print("msg     : " + line)

    @staticmethod
    def makedirs(path):
        if os.path.isdir(path):
            return
        os.makedirs(path)

    def get_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            strings = response.content.decode('utf-8')
            return strings.split('\n')
        self.error(f"Failed to download '{url}'")

    def progress_bar(self, filename, nb_chunk: int, chunk_size: int, total: int):
        fetched_kb = int(nb_chunk * chunk_size / 1024)
        if nb_chunk <= 1:
            self.progress_status = 0

        if self.ui:
            pc = int(100 * 1024 * fetched_kb / total)
            self.action(filename, f"{fetched_kb: 6} KB / {int(total / 1024)} KB")
            self.ui.set_progress(pc)

        pc = int(50 * 1024 * fetched_kb / total)
        print(f"\r[{'#' * pc}{'-' * (49 - pc)}]  {fetched_kb: 6} KB / {int(total / 1024)} KB", end="")

    def download(self, url, dest):
        self.msg(f"Starting to download'{url}' into '{dest}'")
        response = requests.get(url, stream=True)
        size = int(response.headers['Content-Length'])
        self.msg(f"Size = {int(size / 1024)} KB")
        if response.status_code == 200:
            nb_chunk = 0
            self.makedirs(os.path.dirname(dest))
            with open(dest, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    nb_chunk += 1
                    self.progress_bar(os.path.basename(dest), nb_chunk, 1024, size)

            self.progress_bar("", 0, 1024, size)
            self.action(os.path.basename(dest), "downloaded")
            self.msg(f"\ndownloaded successfully '{url}' into '{dest}' in {int(size / 1024)} KB")
        else:
            self.error(f"Failed to download '{url}' into '{dest}'.")

    # -----------------------------------------------------------------------------------------
    # ffmpeg

    def install_ffmpeg(self):
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

        self.msg(f"Downloading latest FFMPEG package version {url}")
        self.download(url, f"{self.ffmpeg_path}/ffmpeg.zip")
        root = None
        with zipfile.ZipFile(f"{self.ffmpeg_path}/ffmpeg.zip") as myzip:
            names = myzip.namelist()
            found_ffmpeg = False
            found_ffprobe = False
            for f in names:
                if root is None or len(f) < len(root):
                    root = f
                if "ffmpeg.exe" in f:
                    myzip.extract(f, self.ffmpeg_path)
                    found_ffmpeg = True
                    self.makedirs(f"{self.ffmpeg_path}/bin")
                    shutil.move(f"{self.ffmpeg_path}/{f}", f"{self.ffmpeg_path}/bin/ffmpeg.exe")
                if "ffprobe.exe" in f:
                    myzip.extract(f, self.ffmpeg_path)
                    found_ffprobe = True
                    self.makedirs(f"{self.ffmpeg_path}/bin")
                    shutil.move(f"{self.ffmpeg_path}/{f}", f"{self.ffmpeg_path}/bin/ffprobe.exe")

        os.remove(f"{self.ffmpeg_path}/ffmpeg.zip")
        shutil.rmtree(f"{self.ffmpeg_path}/{root}")
        if found_ffmpeg and found_ffprobe:
            self.msg(f"ffmpeg installed in '{self.ffmpeg_path}'")
        else:
            self.error('ffmpeg or ffprobe not found in archive')

        # useless: ffmpeg is called from absolute path
        # if not self.args.self_test:
        #     self.add_to_path(ffmpeg_path + '/bin')

    # -----------------------------------------------------------------------------------------
    # auto-install

    def get_json(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            res = json.loads(response.content)
            return res
        self.error(f"Failed to download json from '{url}'")

    def get_latest_package(self):
        """returns the latest package"""
        latest = None
        packages = self.get_json("https://gitlab.com/api/v4/projects/48915444/packages")
        for pack in packages:
            if latest is None:
                latest = pack
            elif pack['version'] > latest['version']:
                latest = pack

        return latest

    def install_piwipre(self):
        self.makedirs(self.piwipre_path)
        target = self.piwipre_target_version

        base = "https://gitlab.com/api/v4/projects/48915444/packages/generic/piwiPre"
        self.download(f"{base}/{target}/piwiPre-{target}.exe",
                      f"{self.piwipre_path}/piwiPre.exe")
        shutil.copy2(f"{self.piwipre_path}/piwiPre.exe",
                     f"{self.piwipre_path}/piwiPre-{target}.exe")

        self.warning(f"Latest package version '{target}' installed in {self.piwipre_path}")

        if not self.args.mode == "test":
            self.add_to_path(os.environ['PROGRAMFILES(X86)'] + '\\piwiPre')  # noqa

    def find_maria_db_url(self, bits: str):
        all_versions = self.get_html("https://dlm.mariadb.com/browse/c_connector/")
        url = None
        version = None
        for line in all_versions:
            #             <td><a href="/browse/c_connector/201/">C connector 3.3</a></td>
            #             <td><a href="/browse/c_connector/169/">C connector 3.2 (EOL)</a></td>
            m = re.match(r'\s*<td><a href="(.*)">C connector (.*)</a></td>', line)
            if m and m.group(2) and 'EOL' not in m.group(2):
                if version is None or m.group(2) > version:
                    version = m.group(2)
                    url = m.group(1)
        if url is None:
            self.error('Unable to find URL of current version in "https://dlm.mariadb.com/browse/c_connector/"')

        all_sub_versions = self.get_html("https://dlm.mariadb.com" + url)
        sub_url = None
        sub_version = None
        for line in all_sub_versions:
            #             <td><a href="/browse/c_connector/201/1294/">C connector 3.3.0</a></td>
            m = re.match(r'\s*<td><a href="(.*)">C connector (.*)</a></td>', line)
            if m and 'EOL' not in m.group(2):
                if sub_version is None or m.group(2) > sub_version:
                    sub_version = m.group(2)
                    sub_url = m.group(1)

        if sub_url is None:
            self.error(f'Unable to find current version in "https://dlm.mariadb.com/browse/c_connector{url}"')

        all_bins = self.get_html("https://dlm.mariadb.com" + sub_url)
        for line in all_bins:
            # <td><a href="https://dlm.mariadb.com/3677107/Connectors/c/connector-c-3.3.8/
            # mariadb-connector-c-3.3.8-win32.msi">connector-c-3.3.8/mariadb-connector-c-3.3.8-win32.msi</a></td>
            m = re.match(r'\s*<td><a href="(.*)">.*\.msi</a></td>', line)
            if m and bits in m.group(1):
                return m.group(1)
        self.error(f'Unable to {bits} in "https://dlm.mariadb.com{sub_url}"')

    def install_maria_db(self):
        archi = "64" if "64" in os.environ['PROCESSOR_ARCHITECTURE'] else '32'
        url = self.find_maria_db_url(archi)
        dest = f"{os.getcwd()}/mariadb.msi"
        self.download(url, dest)
        self.warning(f"maria_db for {archi} bits architecture is downloaded as '{dest}'")

        if self.args.mode == "test":
            self.warning("You should running it AS AN ADMINISTRATOR")
            #  os.system(dest)
        else:
            self.warning("test: NOT running it ")

    def install_for_python(self):
        """
        Used in a PYTHON context, for windows architectures
        helps the installation of ffmpeg and mariaDb
        :return:
        """
        if platform.system() != "Windows":
            self.error("--install-tools can be used only on Windows!")

        self.install_ffmpeg()
        self.install_maria_db()

    @staticmethod
    def get_user_from_key(key):
        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_USERS) as registry:
                with winreg.OpenKey(registry, key) as key2:
                    with winreg.OpenKey(key2, "Volatile Environment") as key3:
                        return winreg.QueryValueEx(key3, "USERNAME")[0]
        except OSError:
            return None

    @staticmethod
    def get_value(key, fid):
        try:
            return winreg.QueryValueEx(key, fid)[0]
        except OSError:
            return None

    def get_user_key(self, username):
        # How to find user registry ID?
        # look at all HKEY-USERS/key/Volatile Environmemt/USERNAME      # noqa
        with winreg.ConnectRegistry(None, winreg.HKEY_USERS) as registry:
            index = 0
            while True:
                try:
                    key = winreg.EnumKey(registry, index)
                    val = self.get_user_from_key(key)
                    if val == username:
                        return key
                    index += 1
                except OSError:
                    return None

    def add_to_path(self, value, master_key="Path"):
        if not windll.shell32.IsUserAnAdmin():
            self.error("INTERNAL ERROR: Not an admin")

        try:
            with winreg.ConnectRegistry(None, winreg.HKEY_USERS) as registry:
                with winreg.OpenKey(registry, self.user_key) as key2:
                    with winreg.CreateKey(key2, "Environment") as key3:  #
                        current = self.get_value(key3, master_key)
                        if current is None:
                            current = value + ";"
                            winreg.SetValueEx(key3, master_key, 0, winreg.REG_EXPAND_SZ, current)
                            winreg.FlushKey(key3)
                            self.msg(f"Created '{value}' to {master_key} environment variable")
                        elif value not in current:
                            if current[-1:] != ';':
                                current += ';'
                            current += value + ";"
                            winreg.SetValueEx(key3, master_key, 0, winreg.REG_EXPAND_SZ, current)
                            winreg.FlushKey(key3)
                            self.msg(f"Added '{value}' to {master_key} environment variable")
                        else:
                            self.msg(f"{master_key} already get '{value}' ")
        except Exception as e:
            self.error(f"Exception '{e}' ")

    def run_min_test(self):
        self.action("Minimal test", "Starting")
        test_dir = os.environ['PROGRAMFILES(X86)'] + '\\piwiPreTmp'   # noqa
        if os.path.isdir(test_dir):
            os.rmdir(test_dir)
            self.msg(f"Removed {test_dir}")
        else:
            os.makedirs(test_dir)
            self.msg(f"Created {test_dir}")
        self.add_to_path(str(datetime.datetime.now()), "PiwiPrePath")
        self.action("Minimal test", "Done")

    def run(self):
        self.action("Installation", "Starting")

        if self.args.user:
            self.user_key = self.get_user_key(self.args.user)
        elif self.args.no_elevation and self.args.mode == "test":
            pass   # this is normal
        else:
            self.error("user should have been passed on cmdline")

        if not self.args.piwipre and not self.args.ffmpeg and not self.args.mariadb:
            self.run_min_test()
        if self.args.piwipre:
            self.install_piwipre()
        if self.args.ffmpeg:
            self.install_ffmpeg()
        if self.args.mariadb:
            self.install_maria_db()
        self.action("Installation", "Done")
        if self.ui is None and self.args.mode == "install":
            # if no-elevation,
            input("Close window?")


def run_installer(arguments):
    if platform.system() != "Windows":
        print("runs only on windows")
        return
    if "--no-elevation" not in sys.argv:
        elevate(show_console="--text-only" in sys.argv)   # noqa
    try:
        Installer(arguments)
    except OSError as e:
        print(f"OS Error {e}")


if __name__ == "__main__":
    run_installer(sys.argv[1:])
