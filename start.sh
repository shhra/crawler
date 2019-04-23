#!/usr/bin/env bash
code()
{
    until python3 loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for start in {0..7}
do
    let st=$(($start * 300000))
    let end=$(( $(($start + 1)) * 300000))
#    code "$st" "$end" &
    echo $st, $end
done
