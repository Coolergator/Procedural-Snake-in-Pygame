import pygame
import sys
import math
import random
import json

from segment import Segment

def point_collision(point_1, point_2, radius):
    return point_1.distance_to(point_2) < radius

def constrain_distance(point, anchor, distance):
    diff = point - anchor
    offset = diff.length()

    if offset == 0:
        return point, 0
    
    direction = diff.normalize()
    angle = math.degrees(math.atan2(direction.y, direction.x))
    pos = direction * distance + anchor

    return pos, angle

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Procedural Snake')
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()

        self.assets = {
            'icon': pygame.image.load('assets/images/Procedural Snake_icon.png').convert_alpha(),
            'sky': pygame.image.load('assets/images/sky_blue_background.png').convert_alpha(),
            'grid': pygame.image.load('assets/images/grid_background.png').convert_alpha(),
            'head': pygame.image.load('assets/images/snake_head.png').convert_alpha(),
            'dead': pygame.image.load('assets/images/snake_head_dead.png').convert_alpha(),
            'win': pygame.image.load('assets/images/snake_head_win.png').convert_alpha(),
            'body': pygame.image.load('assets/images/snake_body.png').convert_alpha(),
            'tail': pygame.image.load('assets/images/snake_tail.png').convert_alpha(),
            'apple': pygame.image.load('assets/images/apple.png').convert_alpha(),
        }

        self.sfx = {
            'success': pygame.mixer.Sound('assets/sfx/success.wav'),
            'failure': pygame.mixer.Sound('assets/sfx/failure.wav'),
        }

        self.sfx['success'].set_volume(.2)
        self.sfx['failure'].set_volume(.2)

        pygame.display.set_icon(self.assets['icon'])

        self.score_font = pygame.font.Font(None, 48)
        self.highscore_font = pygame.font.Font(None, 36)
        self.control_text_font = pygame.font.Font(None, 26)

        self.speed = 10
        self.distance = 30
        self.score = 0
        self.screenshake = 0
        self.start_game = False
        self.game_over = False
        self.eaten_apple = False
        self.got_new_score = False

        self.head = Segment(self.assets['head'], 150, 250, 0)
        self.body = Segment(self.assets['body'], 0, 250, 0)
        self.tail = Segment(self.assets['tail'], 0, 250, 0)
        self.apple_pos = pygame.math.Vector2(350, 250)

        self.segments = [self.head, self.body, self.tail]

        with open('assets/highscore.json', 'r') as f:
            self.highscore = json.load(f)

    def run(self):
        while True:
            self.dt = self.clock.tick(60) / 100
            self.screenshake = max(0, self.screenshake - 1)

            self.keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(self.assets['sky'])
            pygame.draw.rect(self.screen, (100, 100, 100), (45, 45, 410, 410), 5)
            self.assets['grid'].set_alpha(180)
            self.screen.blit(self.assets['grid'], (50, 50))

            # Start Game
            if self.keys[pygame.K_SPACE]:
                if not self.start_game:
                    self.start_game = True
                if self.start_game:
                    self.game_over = False
                    self.score = 0
                    self.segments[0].pos.x, self.segments[0].pos.y = 150, 250
                    self.segments[1].pos.x, self.segments[1].pos.y = 0, 250
                    self.segments[2].pos.x, self.segments[2].pos.y = 0, 250
                    self.apple_pos = pygame.math.Vector2(350, 250)
                    self.segments[0].angle = 0
                    self.segments[1].angle = 0
                    self.segments[2].angle = 0
                    self.segments = [self.head, self.body, self.tail]

            # Scoreboard
            self.scoreboard = self.score_font.render(f'Score: {self.score}', True, ('black'))
            self.screen.blit(self.scoreboard, (50, 10))

            self.highscore_board = self.highscore_font.render('Highscore: ' + str(self.highscore['highscore']), True, ('black'))
            self.screen.blit(self.highscore_board, (305, 13))

            self.new_score = self.highscore_font.render('New', True, ('black'))
            
            if not self.game_over:
                if self.start_game:
                    if self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
                        self.segments[0].angle += 3
                    if self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
                        self.segments[0].angle -= 3

                    radians = math.radians(self.head.angle)

                    self.segments[0].pos.x += self.speed * math.cos(radians) * self.dt 
                    self.segments[0].pos.y += self.speed * math.sin(radians) * self.dt

                # Collisions
                if point_collision(self.segments[0].pos, self.apple_pos, 20) and not self.eaten_apple:
                    self.eaten_apple = True

                    last = self.segments[-1]
                    new_segment = Segment(self.assets['body'], last.pos.x, last.pos.y, last.angle)
                    self.segments.pop()
                    self.segments.append(new_segment)
                    self.segments.append(self.tail)

                    self.apple_pos = pygame.math.Vector2(random.randint(70, 430), random.randint(70, 430))
                    self.sfx['success'].play()

                    # Score Logic
                    self.score += 1

                    if self.score > self.highscore['highscore']:
                        self.highscore['highscore'] += 1
                        with open('assets/highscore.json', 'w') as f:
                            json.dump(self.highscore, f)
                        self.got_new_score = True
                    self.eaten_apple = False

                if self.got_new_score:
                    self.screen.blit(self.new_score, (245, 13))
                
                for i in range(2, len(self.segments)):
                    if point_collision(self.segments[0].pos, self.segments[i].pos, 15):
                        self.screenshake = max(8, self.screenshake)
                        self.sfx['failure'].play()
                        self.game_over = True

                self.grid_bounds = pygame.Rect(50, 50, 400, 400)
                if not self.grid_bounds.collidepoint(self.segments[0].pos):
                    self.screenshake = max(8, self.screenshake)
                    self.sfx['failure'].play()
                    self.game_over = True

                self.apple_rect = self.assets['apple'].get_rect(center=self.apple_pos)
                self.screen.blit(self.assets['apple'], self.apple_rect)

                for i in range(1, len(self.segments)):
                    pos, angle = constrain_distance(self.segments[i].pos, self.segments[i - 1].pos, self.distance)

                    self.segments[i].pos = pos
                    self.segments[i].angle = angle

                self.segments[-1].angle += 180
                self.head.image = self.assets['head']

            elif self.game_over and self.score < 40:
                self.head.image = self.assets['dead']
                self.game_over_text = self.score_font.render(f'Game Over', True, ('black'))
                self.screen.blit(self.game_over_text, (158, 460))

            # Win Con
            if self.score == 40:
                self.game_over = True
                self.head.image = self.assets['win']
                self.game_over_text = self.score_font.render(f'You Win!', True, ('black'))
                self.screen.blit(self.game_over_text, (178, 460))

            # Render Snake
            self.segments[0].render(self.screen)
            self.segments[0].update()
            for i in range(1, len(self.segments) - 1):
                self.segments[i].render(self.screen)
                self.segments[i].update()
            self.segments[-1].render(self.screen)
            self.segments[-1].update()

            if not self.start_game:
                self.start_text = self.highscore_font.render('Press Space to Start or Reset!', True, ('black'))
                self.control_text = self.control_text_font.render('A and D or Left and Right Arrow Keys to turn', True, ('black'))
                self.screen.blit(self.start_text, (77, 105))
                self.screen.blit(self.control_text, (67, 130))

            self.screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.screen, self.screen.get_size()), self.screenshake_offset)

            pygame.display.update()

Game().run()