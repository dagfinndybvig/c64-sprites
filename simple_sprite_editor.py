#!/usr/bin/env python3

import numpy as np
import pygame
from pathlib import Path

SPRITE_HEIGHT = 21
SPRITE_WIDTH_MC = 12  # C64 multicolor sprite width (12 double-width pixels)

# C64 sprite color register values
SPRITE_MULTICOLOR_0 = 0x06  # Blue  -> $D025
SPRITE_MULTICOLOR_1 = 0x05  # Green -> $D026
SPRITE_COLOR = 0x02         # Red   -> $D027 (sprite-specific)


def create_empty_sprite():
    """Create an empty multicolor sprite (12x21, 2-bit color indices)."""
    return np.zeros((SPRITE_HEIGHT, SPRITE_WIDTH_MC), dtype=np.uint8)


def sprite_to_bytes(sprite):
    """Pack 12x21 multicolor pixels into 63 sprite bytes (3 bytes per row)."""
    sprite_bytes = []
    for row in range(SPRITE_HEIGHT):
        for byte_index in range(3):
            packed = 0
            for pixel_index in range(4):
                col = (byte_index * 4) + pixel_index
                color = int(sprite[row, col]) & 0x03
                packed = (packed << 2) | color
            sprite_bytes.append(packed)
    return sprite_bytes

def sprite_to_c_source(sprite):
    """Generate sprite_pokes.c content."""
    sprite_bytes = sprite_to_bytes(sprite)
    lines = []
    lines.append('#include "sprite_pokes.h"')
    lines.append("")
    lines.append(f"const unsigned char sprite_multicolor_0 = 0x{SPRITE_MULTICOLOR_0:02X};")
    lines.append(f"const unsigned char sprite_multicolor_1 = 0x{SPRITE_MULTICOLOR_1:02X};")
    lines.append(f"const unsigned char sprite_color = 0x{SPRITE_COLOR:02X};")
    lines.append("")
    lines.append("const unsigned char sprite_data[63] = {")
    for row in range(SPRITE_HEIGHT):
        i = row * 3
        lines.append(
            f"    0x{sprite_bytes[i]:02X}, 0x{sprite_bytes[i+1]:02X}, 0x{sprite_bytes[i+2]:02X}, /* Row {row} */"
        )
    lines.append("};")
    lines.append("")
    return "\n".join(lines)

def sprite_header():
    """Generate sprite_pokes.h content."""
    return (
        "#ifndef SPRITE_POKES_H\n"
        "#define SPRITE_POKES_H\n"
        "\n"
        "extern const unsigned char sprite_multicolor_0;\n"
        "extern const unsigned char sprite_multicolor_1;\n"
        "extern const unsigned char sprite_color;\n"
        "extern const unsigned char sprite_data[63];\n"
        "\n"
        "#endif\n"
    )

def save_sprite_module(sprite, c_filename="sprite_pokes.c", h_filename="sprite_pokes.h"):
    """Save sprite data as C source and header for separate compile/link."""
    output_dir = Path(__file__).resolve().parent
    c_path = output_dir / c_filename
    h_path = output_dir / h_filename
    with open(c_path, 'w') as f:
        f.write(sprite_to_c_source(sprite))
    with open(h_path, 'w') as f:
        f.write(sprite_header())
    print(f"Sprite module saved to {c_path} and {h_path}")

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up display
    cell_size = 30
    pixel_width = cell_size * 2
    width = SPRITE_WIDTH_MC * pixel_width
    height = SPRITE_HEIGHT * cell_size + 60  # Extra space for info
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Simple C64 Sprite Editor - Keyboard Only")
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)  # Lighter gray for better contrast
    
    # C64 multicolor sprite palette:
    # 0=transparent/off, 1=shared multicolor 0, 2=sprite color, 3=shared multicolor 1
    COLORS = [
        (0, 0, 255),   # Blue (1)
        (255, 64, 64), # Red (2)
        (64, 220, 64), # Green (3)
    ]
    
    # Create sprite
    sprite = create_empty_sprite()
    
    # Cursor position and color
    cursor_row, cursor_col = 10, 6  # Start in center
    current_color = 1  # Default to blue (color 1)
    
    # Main loop
    running = True
    while running:
        screen.fill(WHITE)
        
        # Draw sprite grid
        for row in range(SPRITE_HEIGHT):
            for col in range(SPRITE_WIDTH_MC):
                color_value = sprite[row, col]
                if color_value == 0:
                    color = GRAY
                else:
                    # Map color values 1-3 to multicolor palette
                    color_index = max(0, min(int(color_value) - 1, len(COLORS) - 1))
                    color = COLORS[color_index]
                
                pygame.draw.rect(screen, color, 
                                (col * pixel_width, row * cell_size, pixel_width, cell_size))
                pygame.draw.rect(screen, BLACK, 
                                (col * pixel_width, row * cell_size, pixel_width, cell_size), 1)
        
        # Draw cursor
        cursor_color = (255, 0, 255)  # Magenta cursor
        pygame.draw.rect(screen, cursor_color, 
                        (cursor_col * pixel_width, cursor_row * cell_size, pixel_width, cell_size), 3)
        
        # Draw info
        font = pygame.font.SysFont(None, 24)
        
        color_names = ["OFF", "Blue (D025)", "Red (D027)", "Green (D026)"]
        color_text = font.render(
            f"Multicolor 12x21  Position: ({cursor_col}, {cursor_row})  Color: {color_names[current_color]}",
            True,
            BLACK,
        )
        screen.blit(color_text, (20, SPRITE_HEIGHT * cell_size + 10))
        
        instr_text1 = font.render("Arrows: Move  SPACE: Toggle  1-3: Color  S: Save C module  Q: Quit", True, BLACK)
        screen.blit(instr_text1, (20, SPRITE_HEIGHT * cell_size + 40))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                
                # Arrow keys for navigation
                elif event.key == pygame.K_UP and cursor_row > 0:
                    cursor_row -= 1
                elif event.key == pygame.K_DOWN and cursor_row < SPRITE_HEIGHT - 1:
                    cursor_row += 1
                elif event.key == pygame.K_LEFT and cursor_col > 0:
                    cursor_col -= 1
                elif event.key == pygame.K_RIGHT and cursor_col < SPRITE_WIDTH_MC - 1:
                    cursor_col += 1
                
                # Space key to toggle pixel
                elif event.key == pygame.K_SPACE:
                    # Toggle pixel: 0->current_color, or cycle through colors
                    if sprite[cursor_row, cursor_col] == 0:
                        sprite[cursor_row, cursor_col] = current_color
                    else:
                        sprite[cursor_row, cursor_col] = 0  # Turn off
                
                # Color selection (1-3)
                elif event.key == pygame.K_1:
                    current_color = 1
                elif event.key == pygame.K_2:
                    current_color = 2
                elif event.key == pygame.K_3:
                    current_color = 3
                
                # Save
                elif event.key == pygame.K_s:
                    save_sprite_module(sprite)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
