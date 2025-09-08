#!/usr/bin/env python3

import sys
print(f"Python version: {sys.version}")

try:
    print("Importing pygame...")
    import pygame
    print(f"Pygame version: {pygame.version.ver}")
    
    print("Importing pygame_gui...")
    import pygame_gui
    print("pygame_gui imported successfully")
    
    print("Initializing pygame...")
    pygame.init()
    print("Pygame initialized")
    
    print("Getting display info...")
    info = pygame.display.Info()
    print(f"Display size: {info.current_w}x{info.current_h}")
    
    print("Creating test window...")
    screen = pygame.display.set_mode((400, 300))
    print("Window created")
    
    print("Setting caption...")
    pygame.display.set_caption("Debug Test")
    
    print("Creating UI manager...")
    manager = pygame_gui.UIManager((400, 300))
    print("UI manager created")
    
    print("Running for 2 seconds...")
    import time
    start = time.time()
    clock = pygame.time.Clock()
    
    while time.time() - start < 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            manager.process_events(event)
        
        manager.update(0.016)
        screen.fill((30, 30, 30))
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(60)
    
    print("Test completed successfully!")
    pygame.quit()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()