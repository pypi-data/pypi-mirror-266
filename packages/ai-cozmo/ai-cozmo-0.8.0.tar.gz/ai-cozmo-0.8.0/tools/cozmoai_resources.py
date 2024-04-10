

import sys
import os
import urllib.request
import ssl
import zipfile
import argparse
import pathlib
import shutil

import cozmoai

ssl._create_default_https_context = ssl._create_unverified_context  # noqa


OBB_URL = "https://media.githubusercontent.com/media/cristobalraya/cozmo-archive/" \
          "master/applications/com.anki.cozmo_3.4.0-1204_plus_OBB.zip"


def download(fspec: pathlib.Path) -> bool:
    try:
        with urllib.request.urlopen(OBB_URL) as response, open(fspec, "wb") as f:
            while True:
                data = response.read(8192)
                if not data:
                    break
                f.write(data)
        return True
    except Exception: 
              
        return False


def extract(fspec: pathlib.Path, dspec: pathlib.Path) -> bool:
   
    try:
        os.makedirs(str(dspec))
    except FileExistsError:
        pass
    try:
        with zipfile.ZipFile(str(fspec), "r") as f:
            f.extractall(str(dspec))
        return True
    except Exception:   
        return False


def do_status() -> None:
    
    asset_dir = cozmoai.util.get_cozmo_asset_dir()
    if os.path.exists(asset_dir / "resources.txt"):
        print(f"found in {asset_dir}")
    else:
        print(f"not found in {asset_dir}")
        sys.exit(1)


def do_download() -> None:


    asset_dir = cozmoai.util.get_cozmo_asset_dir()
    resource_file = asset_dir / "obb.zip"

    
    if os.path.exists(asset_dir / "resources.txt"):
        print(f"already available in {asset_dir}")
        sys.exit(1)

    
    try:
        os.makedirs(asset_dir)
    except FileExistsError:
        pass

    print("downloading...")

    res = download(resource_file)
    if not res:
        print("error: Download failed.")
        sys.exit(2)

    print("Extracting...")

    res = extract(
        resource_file,
        asset_dir / "obb")
    if not res:
        print("ERROR: Extraction failed.")
        sys.exit(3)
    os.remove(str(resource_file))

    res = extract(
        asset_dir / "obb" / "Android" / "obb" / "com.anki.cozmo" / "main.1204.com.anki.cozmo.obb",
        asset_dir / "..")
    if not res:
        print("ERROR: Secondary extraction failed.")
        sys.exit(4)
    shutil.rmtree(asset_dir / "obb")

    res = extract(
        asset_dir / "cozmo_resources" / "sound" / "AudioAssets.zip",
        asset_dir / "cozmo_resources" / "sound")
    if not res:
        print("ERROR: Sound extraction failed.")
        sys.exit(5)

    print(f"Resources downloaded successfully in {asset_dir}")


def do_remove() -> None:
    

    asset_dir = cozmoai.util.get_cozmo_asset_dir()

    if not os.path.exists(asset_dir / "resources.txt"):
        print(f"Resources NOT available in {asset_dir}")
        sys.exit(1)

    shutil.rmtree(asset_dir)

    print(f"Resources successfully removed from {asset_dir}")


def parse_args() -> argparse.Namespace:
  
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.add_parser("status", help="show resource status")
    subparsers.add_parser("download", help="download and extract resources")
    subparsers.add_parser("remove", help="remove resources")
    args = parser.parse_args()
    if not args.cmd:
        print(parser.format_usage())
        sys.exit(1)
    return args


def main():

   
    args = parse_args()

    if args.cmd == "status":
        do_status()
    elif args.cmd == "download":
        do_download()
    elif args.cmd == "remove":
        do_remove()
    else:
        assert False


if __name__ == '__main__':
    main()
