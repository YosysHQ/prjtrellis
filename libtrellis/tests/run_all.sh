#!/usr/bin/bash

# Run all Python scripts testing prjtrellis functions
# Script return codes: 0=success, 1=failure, 2=skipped
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export PYTHONPATH=../
total=0
pass=0
skipped=0
fail=0

mkdir -p ${DIR}/work

for f in ${DIR}/*.py; do
    python3 $f
    RC="$?"
    let total++
    if [[ "$RC" -eq 0 ]]; then
        echo "******** Test ${f} passed."
        let pass++
    elif [[ "$RC" -eq 1 ]]; then
        echo "******** Test ${f} failed."
        let fail++
    elif [[ "$RC" -eq 2 ]]; then
        echo "******** Test ${f} skipped."
        let skipped++
    fi

done

echo "${total} total, ${pass} passed, ${skipped} skipped, ${fail} failed"
