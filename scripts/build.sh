#!/usr/bin/env bash

pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --onefile --console --name "JiraBot" \
            --paths "src/jirabot" \
            -F "src/jirabot/main.py" \
            --copy-metadata magic_filter