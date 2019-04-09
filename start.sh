#!/usr/bin/env bash
until python loader.py; do
    sleep 1;
done

