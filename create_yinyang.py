import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.Surface((WIDTH, HEIGHT))
screen.fill((255, 255, 255))

center = (WIDTH // 2, HEIGHT // 2)
radius = 200

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Großer Kreis schwarz
pygame.draw.circle(screen, BLACK, center, radius)

# Obere Hälfte weiß (Halbkreis)
rect_top = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius)
pygame.draw.ellipse(screen, WHITE, rect_top)

# Untere Hälfte schwarz (ist eh schon schwarz vom großen Kreis)

# Kleine weiße Kreise (je ein großer in jedem Halbkreis)
pygame.draw.circle(screen, WHITE, (center[0], center[1] - radius//2), radius//2)
pygame.draw.circle(screen, BLACK, (center[0], center[1] + radius//2), radius//2)

# Kleine Punkte
pygame.draw.circle(screen, BLACK, (center[0], center[1] - radius//2), radius//6)
pygame.draw.circle(screen, WHITE, (center[0], center[1] + radius//2), radius//6)

# Speichern
pygame.image.save(screen, "yin_yang_clean.png")
print("Sauberes Yin-Yang Bild gespeichert als 'yin_yang_clean.png'")
