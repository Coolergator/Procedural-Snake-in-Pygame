import pygame

class Segment:
    def __init__(self, image, x, y, angle):
        self.image = image
        self.pos = pygame.math.Vector2(x, y)
        self.angle = angle
        self.rotate = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.rotate.get_rect(center=(self.pos))
    
    def update(self):
        self.rotate = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.rotate.get_rect(center=(self.pos))

    def render(self, surface):
        surface.blit(self.rotate, self.rect)