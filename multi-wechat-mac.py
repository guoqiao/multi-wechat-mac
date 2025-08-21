#! /usr/bin/env python3

import argparse
import os
import subprocess
from pathlib import Path


def run_cmd(cmdline: str):
    print(f"running cmd: {cmdline}")
    return subprocess.run(cmdline, shell=True, check=True)


def test_cmd(cmdline: str):
    print(f"testing cmd: {cmdline}")
    return subprocess.run(cmdline, shell=True, check=False).returncode == 0


def cli():
    parser = argparse.ArgumentParser(
        description="Multi WeChat Mac",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-n", "--name", default="WeChat2", help="Name for the new WeChat app")
    parser.add_argument("-i", "--icon", default="", help="Icon image for the new WeChat app in .icns format")
    return parser.parse_args()


def main():
    args = cli()
    name = args.name

    step = 0
    print(f"Creating new WeChat app with name {name}")

    step += 1
    print(f"\nStep {step}: Ensure Xcode Command Line Tools is installed")
    if test_cmd("xcode-select -p"):
        print("Xcode Command Line Tools is already installed, skip")
    else:
        run_cmd("xcode-select --install")
    
    step += 1
    print(f"\nStep {step}: Ensure no WeChat instance is running")
    yes = input("Close any WeChat instance, then press y to continue: ")
    if yes != "y":
        print("Aborted")
        return

    step += 1
    print(f"\nStep {step}: Copy WeChat app")
    path = f"/Applications/{name}.app"
    if os.path.exists(path):
        print(f"{path} already exists, skip")
    else:
        run_cmd(f"sudo cp -R /Applications/WeChat.app {path}")

    step += 1
    print(f"\nStep {step}: Change Icon")
    if args.icon:
        icon_path = Path(args.icon)
        assert icon_path.is_file(), f"Icon image {icon_path} does not exist"
        if icon_path.suffix.lower() == ".icns":
            icns_path = icon_path
        else:
            print(f"Converting {icon_path} to .icns format")
            icns_path = icon_path.with_suffix(".icns")
            cmdline = f"sips -s format icns {icon_path} --out {icns_path}"
            run_cmd(cmdline)

        app_icns_path = f"/Applications/{name}.app/Contents/Resources/AppIcon.icns"
        print(f"Copying {icns_path} to {app_icns_path}")
        cmdline = f"sudo cp {icns_path} {app_icns_path}"
        run_cmd(cmdline)
        # update app bundle
        run_cmd(f"sudo touch {path}")
    else:
        print("No icon image provided, skip")

    step += 1
    print(f"\nStep {step}: Setting App Identifier for {path}")
    identifier = f"com.tencent.xin{name}"
    plist_path = f"{path}/Contents/Info.plist"
    if test_cmd(f"grep {identifier} {plist_path}"):
        print(f"App Identifier for {path} is already set to {identifier}, skip")
    else:
        cmdline = f'sudo /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {identifier}" {plist_path}' 
        run_cmd(cmdline)

    step += 1
    print(f"\nStep {step}: Signing {path}")
    cmdline = f"sudo codesign --force --deep --sign - {path}"
    run_cmd(cmdline)

    print(f"\nDone! You can now run {name} from /Applications, enjoy!")


if __name__ == "__main__":
    main()
