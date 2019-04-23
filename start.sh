#!/usr/bin/env bash
code()
{
    until python3 loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for start in {0..8}
do
    let st=$(($start * 500000))
    let end=$(( $(($start + 1)) * 500000))
    code "$st" "$end" &
#    echo $st, $end
done
