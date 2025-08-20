#! /usr/bin/env python3

import argparse
import os
import subprocess


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
    parser.add_argument("-n", "--name", default="WeChat2", help="Name of the new WeChat app")
    return parser.parse_args()


def main():
    args = cli()
    name = args.name

    print(f"Creating new WeChat app with name {name}")

    print("\nStep 1: Ensure Xcode Command Line Tools is installed")
    if test_cmd("xcode-select -p"):
        print("Xcode Command Line Tools is already installed, skip")
    else:
        run_cmd("xcode-select --install")
    
    print("\nStep 2: Ensure no WeChat instance is running")
    yes = input("Close any WeChat instance, then press y to continue: ")
    if yes != "y":
        print("Aborted")
        return

    print("\nStep 3: Copy WeChat app")
    path = f"/Applications/{name}.app"
    if os.path.exists(path):
        print(f"{path} already exists, skip")
    else:
        run_cmd(f"sudo cp -R /Applications/WeChat.app {path}")

    print(f"\nStep 4: Setting App Identifier for {path}")
    identifier = f"com.tencent.xin{name}"
    plist_path = f"{path}/Contents/Info.plist"
    if test_cmd(f"grep {identifier} {plist_path}"):
        print(f"App Identifier for {path} is already set to {identifier}, skip")
    else:
        cmdline = f'sudo /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier {identifier}" {plist_path}' 
        run_cmd(cmdline)

    print(f"\nStep 5: Signing {path}")
    cmdline = f"sudo codesign --force --deep --sign - {path}"
    run_cmd(cmdline)

    print(f"\nDone! You can now run {name} from /Applications, enjoy!")


if __name__ == "__main__":
    main()
