import os

import subprocess
from pathlib import Path
from platform import architecture
import tempfile

# Avoid
# urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1124)>
# in some docker images
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def install_license(platform=None):
    if platform is None:
        if os.name == 'nt':
            if architecture()[0][:2] == '32':
                platform = 'win32'
            else:
                platform = 'x64'
        else:
            platform = 'linux'
    from urllib.request import Request, urlopen
    print("Starting license installation")
    p = Path('hawc2-%s' % platform.replace("x64", 'win64'))

    if 'CI_PRIVATE_PAT' in os.environ:
        CI_PRIVATE_PAT = os.environ['CI_PRIVATE_PAT']

    # Download the licensefile installer
    url = "http://gitlab.windenergy.dtu.dk/api/v4/projects/2447/jobs/artifacts/main/raw/"

    job, exe = {'win32': ('build-Windows', 'license_manager.exe'),
                'x64': ('build-Windows', 'license_manager.exe'),
                'linux': ('build-Linux', 'license_manager')}[platform]
    path = f"{exe}?job={job}"
    req = Request(url + path)
    req.add_header('PRIVATE-TOKEN', CI_PRIVATE_PAT)
    print(f"license_manager GET status:{urlopen(req).code}")

    with tempfile.TemporaryDirectory() as tmpdirname:
        exe = os.path.join(tmpdirname, exe)
        cfg = os.path.join(tmpdirname, "HAWC2-ci.cfg")
        with open(f"{exe}", 'wb+') as fid:
            fid.write(urlopen(req).read())
        if platform == "linux":
            os.chmod(exe, 0o755)

        # Download the keygen license file
        url = "http://gitlab.windenergy.dtu.dk/api/v4/projects/1203/jobs/artifacts/ci_runner/raw/"
        path = "keygen_license/HAWC2-ci.cfg?job=all_license_files"
        req = Request(url + path)
        req.add_header('PRIVATE-TOKEN', CI_PRIVATE_PAT)
        print(f"License file GET status:{urlopen(req).code}")
        with open(cfg, 'wb+') as fid:
            fid.write(urlopen(req).read())

        # Install license
        print(f"Installing license on {platform}")
        status = subprocess.run([os.path.abspath(exe), 'install', '-y', 'hawc2', cfg])
        print(f"Status: {status.returncode}")
        print(f"StdOut: {status.stdout}")
        print(f"StdErr: {status.stderr}")
        status = subprocess.run([os.path.abspath(exe), 'info', 'hawc2', 'installed'])
