#!/usr/bin/env bash
code()
{
    until python3 loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for start in {0..10}
do
    let st=$(($start * 50000))
    let end=$(( $(($start + 1)) * 50000))
    code "$st" "$end" &
#    echo $st, $end
done
