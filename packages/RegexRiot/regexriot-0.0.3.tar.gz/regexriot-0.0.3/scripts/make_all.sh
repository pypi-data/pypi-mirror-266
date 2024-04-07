#! /bin/bash

make -C docs/ html &
jupyter lite build --output-dir docs/build/html/demo/ --contents src/ &
wait