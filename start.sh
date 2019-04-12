#!/usr/bin/env bash
code()
{
    until python3 loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for start in {0..19}
do
    let st=$((3000000 + $(($start * 100000)) ))
    let end=$(( 3000000 + $(( $(($start + 1)) * 100000)) ))
#    code "$st" "$end" &
    echo $st, $end
done
