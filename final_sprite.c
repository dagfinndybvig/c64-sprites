#include <stdio.h>
#include <conio.h>
#include <peekpoke.h>
#include "sprite_pokes.h"

int main(void) {
    unsigned char x = 100;
    unsigned char y = 100;
    
    // Clear screen
    clrscr();
    
    // Copy sprite data to sprite memory using loop (reliable method)
    {
        int i;
        for (i = 0; i < 63; i++) {
            POKE(0x3000 + i, sprite_data[i]);
        }
    }
    
    // Set up sprite 0 to use memory at $3000
    POKE(0x07F8, 192);  // Sprite pointer to $3000 (192 * 64 = $3000)
    
    // Enable sprite 0 in multicolor mode with generated colors
    POKE(0xD015, 0x01);  // Enable sprite 0
    POKE(0xD01C, 0x01);  // Multicolor mode for sprite 0
    POKE(0xD025, sprite_multicolor_0);  // Shared multicolor 0
    POKE(0xD026, sprite_multicolor_1);  // Shared multicolor 1
    POKE(0xD027, sprite_color);         // Sprite-specific color
    POKE(0xD017, 0x01); POKE(0xD01D, 0x01);  // EASY TO FIND: double-size sprite 0 in Y and X
    
    // Set initial position (center of screen)
    POKE(0xD000, x);
    POKE(0xD001, y);
    
    // Blue border to indicate success
    POKE(0xD020, 0x06);  // Blue border
    POKE(0xD021, 0x07);  // EASY TO FIND: default yellow background
    
    // Main loop with WASD controls
    while (1) {
        // Read keyboard input
        if (kbhit()) {
            char key = cgetc();
            switch (key) {
                case 'a': x -= 2; break;  // Move left
                case 'd': x += 2; break;  // Move right
                case 'w': y -= 2; break;  // Move up
                case 's': y += 2; break;  // Move down
            }
            // Update sprite position
            POKE(0xD000, x);
            POKE(0xD001, y);
        }
    }
    
    return 0;
}
