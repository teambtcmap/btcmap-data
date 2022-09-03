#! /bin/bash

curl -X POST -d "@query.txt" -o new-data.json https://overpass-api.de/api/interpreter

lines=$(wc -l new-data.json | cut --delimiter=' ' --fields 1)

if [ "$lines" -lt 1000 ]; then
    printf 'The response is too small (%s lines)\n' "$lines"
    rm new-data.json
    exit 0
fi

mv new-data.json data.json

insertions=$(git diff --numstat data.json | cut --fields=1)
deletions=$(git diff --numstat data.json | cut --fields=2)
printf 'Insertions: %s, deletions: %s\n' "$insertions" "$deletions"

if [ "$insertions" -eq 1 ] && [ "$deletions" -eq 1 ]; then
    printf 'The difference is too small\n'
    git checkout data.json
fi
