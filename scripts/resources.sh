#!/bin/bash


directory_path="../results"


for folder in "$directory_path"/*; do
    if [ -d "$folder" ]; then
        echo "Execution on folder: $folder"
        python3 quantiles.py "$folder"
    fi
done
