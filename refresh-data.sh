#! /bin/bash

curl -X POST -d "@query.txt" -o new-data.json https://overpass-api.de/api/interpreter

lines=$(wc -l new-data.json | cut --delimiter=' ' --fields 1)

if [ $lines -gt 1000 ]; then
    mv new-data.json data.json
fi
