#!/usr/bin/env bash
code()
{
    until python3 loader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
for number in {9..15}
do
for start in {0..9}
do
    let st=$((1000000 * number + $(($start * 100000)) ))
    let end=$(( 1000000 * number + $(( $(($start + 1)) * 100000)) ))
    code "$st" "$end" &
#    echo $st, $end
done
done
