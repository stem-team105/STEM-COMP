"""Build a reviewable source ZIP without packages, private data, keys or recordings."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
ALLOWED_SUFFIXES={'.py','.pyw','.md','.txt','.bat','.svg','.png','.ico'}


def build(destination):
    destination=Path(destination).resolve();destination.parent.mkdir(parents=True,exist_ok=True)
    files=[p for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES]
    files+=sorted(p for p in (ROOT/'assets').rglob('*') if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES)
    manifest={}
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(files):
            relative=p.relative_to(ROOT).as_posix();data=p.read_bytes();manifest[relative]=hashlib.sha256(data).hexdigest();archive.writestr('Lamatna/'+relative,data)
        archive.writestr('Lamatna/SOURCE-MANIFEST.json',json.dumps({'algorithm':'SHA-256','files':manifest},indent=2))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:raise RuntimeError('ZIP verification failed.')
        required={'Lamatna/app.py','Lamatna/README.md','Lamatna/Open-Lamatna.pyw','Lamatna/launcher.py','Lamatna/core.py','Lamatna/local_ai.py'}
        if not required.issubset(archive.namelist()):raise RuntimeError('A required source file is missing.')
    return {'path':str(destination),'files':len(files),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}


if __name__=='__main__':
    target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'.local/submission/Lamatna-Prototype-Team105.zip'
    print(json.dumps(build(target),indent=2))
