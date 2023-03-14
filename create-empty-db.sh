#!/bin/sh
rm -rf database
mkdir -p database
echo '*' > database/.gitignore
cp devices.json database/
cp -r metadata/* database/
python3 tools/get_tilegrid_all.py
python3 tools/create_empty_bitdbs.py
