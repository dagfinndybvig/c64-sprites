#!/bin/bash

echo "Building C64 sprite program with latest design..."

# Clean previous build artifacts
rm -f final.prg final_sprite.o sprite_pokes.o

# Compile and link program + generated sprite data module
cl65 -t c64 -o final.prg final_sprite.c sprite_pokes.c

if [ $? -eq 0 ]; then
    echo "Build successful! final.prg is ready with your latest sprite design."
    echo "File size: $(stat -c%s final.prg) bytes"
else
    echo "Build failed!"
    exit 1
fi
