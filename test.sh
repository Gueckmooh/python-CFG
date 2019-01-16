#!/bin/bash

if /home/brignone/Documents/Cours/M2/WCET/CFG-python/CFG-reconstruction -o output.dot tests/example5
then
    dot -Tpng output.dot -o output.png
    see output.png
fi
