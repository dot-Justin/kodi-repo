#!/usr/bin/env python3
"""
generate_repo.py — Rebuild addons.xml and addons.xml.md5 for dotJustin's Kodi repo.

Run from the repo root:
    python3 tools/generate_repo.py

For each addon subdirectory that contains a zip, the script:
  1. Opens the latest zip (alphabetically last, so 1.0.9 < 1.0.10 won't matter
     as long as versions are zero-padded, but works fine for typical semver).
  2. Extracts the <addon> element from addon.xml inside the zip.
  3. Appends it to addons.xml.

The repository addon itself (repository.dotjustin) has no zip — its addon.xml
is read directly from the directory.
"""

import os
import sys
import zipfile
import hashlib
from xml.etree import ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDONS_XML = os.path.join(REPO_ROOT, 'addons.xml')
ADDONS_MD5 = os.path.join(REPO_ROOT, 'addons.xml.md5')
INDEX_HTML = os.path.join(REPO_ROOT, 'index.html')

# Directories to skip when scanning for addons
SKIP_DIRS = {'.github', 'tools', '.git'}


def get_addon_element_from_zip(zip_path):
    """Return the parsed <addon> Element from addon.xml inside a zip."""
    with zipfile.ZipFile(zip_path) as z:
        # addon.xml is at <addon_id>/addon.xml inside the zip
        candidates = [n for n in z.namelist() if n.endswith('addon.xml') and n.count('/') == 1]
        if not candidates:
            print(f'  WARNING: no addon.xml found in {zip_path}')
            return None
        content = z.read(candidates[0])
    return ET.fromstring(content.decode('utf-8'))


def get_addon_element_from_dir(dir_path):
    """Return the parsed <addon> Element from addon.xml directly in a directory."""
    xml_path = os.path.join(dir_path, 'addon.xml')
    if not os.path.isfile(xml_path):
        return None
    tree = ET.parse(xml_path)
    return tree.getroot()


def indent(elem, level=0):
    """Add pretty-print indentation in-place (ET doesn't do this natively < 3.9)."""
    pad = '\n' + '  ' * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = pad
    if not level:
        elem.tail = '\n'


def main():
    addon_elements = []
    zip_links = []  # (subdir/filename) paths for index.html

    entries = sorted(os.listdir(REPO_ROOT))
    for name in entries:
        full_path = os.path.join(REPO_ROOT, name)
        if not os.path.isdir(full_path):
            continue
        if name in SKIP_DIRS or name.startswith('.'):
            continue

        # Find zips in the directory
        zips = sorted([f for f in os.listdir(full_path) if f.endswith('.zip')])

        if zips:
            # Use the last zip (highest version when named addon_id-x.y.z.zip)
            latest = zips[-1]
            zip_path = os.path.join(full_path, latest)
            print(f'  {name}: reading from {latest}')
            elem = get_addon_element_from_zip(zip_path)
            zip_links.append(f'{name}/{latest}')
        else:
            # No zip — read addon.xml directly (e.g. repository addon)
            elem = get_addon_element_from_dir(full_path)
            if elem is not None:
                print(f'  {name}: reading from addon.xml directly')

        if elem is not None:
            addon_elements.append(elem)

    if not addon_elements:
        print('ERROR: no addons found — aborting')
        sys.exit(1)

    # Build addons.xml
    root = ET.Element('addons')
    for elem in addon_elements:
        root.append(elem)

    indent(root)
    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode').encode('utf-8')

    with open(ADDONS_XML, 'wb') as f:
        f.write(xml_bytes)
    print(f'\nWrote {ADDONS_XML}  ({len(xml_bytes)} bytes, {len(addon_elements)} addons)')

    # Write MD5
    md5 = hashlib.md5(xml_bytes).hexdigest()
    with open(ADDONS_MD5, 'w') as f:
        f.write(md5)
    print(f'Wrote {ADDONS_MD5}  ({md5})')

    # Build index.html — Kodi parses <a href="*.zip"> links to browse the source
    links_html = '\n'.join(f'<a href="{p}">{p}</a>' for p in zip_links)
    html = f'<!DOCTYPE html>\n{links_html}\n'
    with open(INDEX_HTML, 'w') as f:
        f.write(html)
    print(f'Wrote {INDEX_HTML}  ({len(zip_links)} zip(s)')


if __name__ == '__main__':
    print(f'Generating Kodi repo index from: {REPO_ROOT}\n')
    main()
