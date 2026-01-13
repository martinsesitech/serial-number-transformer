#!/bin/bash

if [ "$1" == "build" ]; then
    docker compose build && docker compose run --rm serial-transformer
else
    docker compose run --rm serial-transformer
fi