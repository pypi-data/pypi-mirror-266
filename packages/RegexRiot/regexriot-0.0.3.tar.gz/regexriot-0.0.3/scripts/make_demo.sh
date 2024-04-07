#! /bin/bash

echo "Removing the old stuff"
rm -r docs/build/html/demo/*
echo "Removed the old stuff"
echo "Making the new stuff"
jupyter lite build --output-dir docs/build/html/demo/ --contents src/
echo "Made the new stuff"