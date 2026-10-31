"""
Windows Explorer shell folder skinner.
Applies portable relative desktop.ini + folder.ico bindings with correct file system attributes.
"""

import subprocess
from pathlib import Path


def is_folder_skinned(folder_path: Path) -> bool:
    """Check if folder already contains desktop.ini and folder.ico."""
    ini = folder_path / "desktop.ini"
    ico = folder_path / "folder.ico"
    return ini.exists() and ico.exists()


def apply_portable_skin(folder_path: Path, ico_path: Path) -> bool:
    """
    Bind folder icon to Windows Explorer folder using 100% portable configuration.
    
    Rules for Windows Shell Folder Icons:
    1. The directory itself must have the Read-Only attribute ('attrib +r <dir>') for Explorer to evaluate desktop.ini.
    2. desktop.ini must have Hidden and System attributes ('attrib +h +s desktop.ini').
    3. folder.ico is stored directly inside the directory with Hidden attribute ('attrib +h folder.ico').
    4. desktop.ini uses relative path: IconResource=folder.ico,0.
    
    This guarantees icons stay intact across drive letters, network mounts, and reboots.
    """
    try:
        folder_path = folder_path.resolve()
        local_ico = folder_path / "folder.ico"
        desktop_ini = folder_path / "desktop.ini"

        # Remove existing flags to permit write
        if local_ico.exists():
            subprocess.run(["attrib", "-h", "-s", str(local_ico)], capture_output=True)
        local_ico.write_bytes(ico_path.read_bytes())
        subprocess.run(["attrib", "+h", str(local_ico)], capture_output=True)

        if desktop_ini.exists():
            subprocess.run(["attrib", "-h", "-s", str(desktop_ini)], capture_output=True)

        ini_content = (
            "[.ShellClassInfo]\n"
            "IconResource=folder.ico,0\n"
            "[ViewState]\n"
            "Mode=\n"
            "Vid=\n"
            "FolderType=Generic\n"
        )
        desktop_ini.write_text(ini_content, encoding="utf-8")

        # Set critical Windows shell attributes
        subprocess.run(["attrib", "+r", str(folder_path)], capture_output=True)
        subprocess.run(["attrib", "+h", "+s", str(desktop_ini)], capture_output=True)
        return True
    except Exception as e:
        print(f"[-] Error applying skin to {folder_path.name}: {e}")
        return False
