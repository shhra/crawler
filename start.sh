#!/usr/bin/env bash
code()
{
    until python loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for start in {0..9}
do
    let st=$(($start * 100000))
    let end=$(( $(($start + 1)) * 100000))
    code "$st" "$end" &

done
