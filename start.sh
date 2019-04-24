#!/usr/bin/env bash
code()
{
#    until python3 loader.py --start $1 --end $2 ;do
    until python3 downloader.py --start $1 --end $2 ;do
        sleep 1;
    done
}
#for start in {0..20}
#do
#    let st=$(($start * 300000))
#    let end=$(( $(($start + 1)) * 300000))
#    code "$st" "$end" &
##    echo $st, $end

for start in {0..17}
do
    let st=$(($start * 30000))
    let end=$(( $(($start + 1)) * 30000))
    code "$st" "$end" &
#    echo $st, $end
done
done
