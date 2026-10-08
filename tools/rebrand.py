#!/usr/bin/env python3
# Copyright 2026 Cole Munz
# SPDX-License-Identifier: AGPL-3.0-only
"""Put the Wren name, bundle prefix and icon back after an upstream merge.

Usage: tools/rebrand.py [--check]
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / "tools" / "brand"
PREFIX = "io.github.munzzyy"
NAME = "Wren"

PBXPROJ = ROOT / "Signal.xcodeproj" / "project.pbxproj"
INFO_PLIST = ROOT / "Signal" / "Signal-Info.plist"
PREFIX_RE = re.compile(r"(SIGNAL_BUNDLEID_PREFIX = )[^;]+;")
PREFIX_COUNT = 4

ICON_FILES = {
    "logo.svg": ROOT / "Signal" / "AppIcons" / "AppIcon.icon" / "Assets" / "logo.svg",
    "icon.json": ROOT / "Signal" / "AppIcons" / "AppIcon.icon" / "icon.json",
    "preview-180.png": ROOT / "Signal" / "AppIcon.xcassets" / "AppIconPreview"
    / "default.imageset" / "Signal-180x180.png",
}


def plist_key_re(key):
    return re.compile(r"(<key>%s</key>\s*<string>)[^<]*(</string>)" % key)


def fix_pbxproj(text):
    found = len(PREFIX_RE.findall(text))
    if found != PREFIX_COUNT:
        raise SystemExit(
            f"expected {PREFIX_COUNT} SIGNAL_BUNDLEID_PREFIX settings, found {found}"
        )
    return PREFIX_RE.sub(rf"\g<1>{PREFIX};", text)


def fix_plist(text):
    for key in ("CFBundleDisplayName", "CFBundleName"):
        text, n = plist_key_re(key).subn(rf"\g<1>{NAME}\g<2>", text)
        if n != 1:
            raise SystemExit(f"{INFO_PLIST.name}: {key} not found exactly once")
    return text


def main(argv):
    check = "--check" in argv
    stale = []

    for path, fix in ((PBXPROJ, fix_pbxproj), (INFO_PLIST, fix_plist)):
        before = path.read_text(encoding="utf-8")
        after = fix(before)
        if before != after:
            stale.append(path)
            if not check:
                path.write_text(after, encoding="utf-8")

    for name, dest in ICON_FILES.items():
        src = BRAND / name
        if not dest.exists() or dest.read_bytes() != src.read_bytes():
            stale.append(dest)
            if not check:
                shutil.copyfile(src, dest)

    for path in stale:
        verb = "needs rebrand" if check else "rebranded"
        print(f"{verb}: {path.relative_to(ROOT)}")
    if check and stale:
        return 1
    if not stale:
        print("already rebranded")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
