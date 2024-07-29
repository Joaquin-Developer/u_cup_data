#!/bin/bash

USER="admin"
PASSWORD="admin"
DATABASE="u_cup_2024"
BACKUP_DIR="/home/jparilla/Documents/personal/u_cup/database/backups"
DATE=$(date +%Y-%m-%d)
BACKUP_FILE="$BACKUP_DIR/$DATE.sql"

echo "- Deleting .sql & .gz files in Local folder"
rm -rf $BACKUP_DIR/*.*

mysqldump -u $USER -p$PASSWORD $DATABASE > $BACKUP_FILE
echo "- Backup finished: $BACKUP_FILE"

echo "- Compressing .sql to zip"
gzip $BACKUP_FILE

echo "- Load in Google Drive"
python3.10 backup.py
