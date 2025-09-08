#!/usr/bin/env python3

import pygame
import pygame_gui

def test_pygame():
    print("Testing pygame initialization...")
    pygame.init()
    
    print("Creating window...")
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Test Window")
    
    print("Creating UI manager...")
    manager = pygame_gui.UIManager((400, 300))
    
    print("Creating button...")
    button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(150, 130, 100, 40),
        text="Test Button",
        manager=manager
    )
    
    clock = pygame.time.Clock()
    running = True
    
    print("Starting event loop...")
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button:
                    print("Button clicked!")
            
            manager.process_events(event)
        
        manager.update(time_delta)
        
        screen.fill((30, 30, 30))
        manager.draw_ui(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    print("Test completed successfully!")

if __name__ == "__main__":
    test_pygame()