import os
from time import time
from typing import Any
from random import randint  

import pygame


class Settings:
    WINDOW = pygame.rect.Rect((0, 0), (800, 600))
    FPS = 60
    DELTATIME = 1.0 / FPS
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.join(FILE_PATH, "images")
    DIRECTIONS = {"right": pygame.math.Vector2(20, 0), 
                  "left": pygame.math.Vector2(-20, 0), 
                  "up": pygame.math.Vector2(0, -20), 
                  "double": pygame.math.Vector2(0, -40),
                  "down": pygame.math.Vector2(0, 20)}
    
    GRAY = (128, 128, 128)
    ALPHA = 180


class Fox(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.image = pygame.image.load("images/fox.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = pygame.rect.FRect(self.image.get_rect())
        self.rect.centerx = Settings.WINDOW.centerx
        self.rect.bottom = Settings.WINDOW.bottom - 50
        self.direction = Settings.DIRECTIONS["right"]
        self.change_direction("right")
        self.change_direction("start")
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        if "direction" in kwargs.keys():
            direction = kwargs["direction"]
            if direction in Settings.DIRECTIONS.keys():
                self.direction = Settings.DIRECTIONS[direction]
                self.move_once()
        #self.check_win()
            
        #überprüfen ob rand berührt
        if self.rect.left < 0:
                self.rect.left = 0
        elif self.rect.right > Settings.WINDOW.width:
                self.rect.right = Settings.WINDOW.width
        if self.rect.top < 0:
                self.rect.top = 0
        elif self.rect.bottom > Settings.WINDOW.height:
                self.rect.bottom = Settings.WINDOW.height
                
        elif "direction" in kwargs.keys():
            self.change_direction(kwargs["direction"])

    def change_direction(self, direction: str) -> None:
        if direction in Settings.DIRECTIONS.keys():
            self.direction = Settings.DIRECTIONS[direction]
        # nur für lshift + r
        elif direction == "stop":
            self.speed = 0
        elif direction == "start":
            self.speed = 100
    
    def move_once(self) -> None:
        if self.direction:
            dx = self.direction.x * self.speed * Settings.DELTATIME
            dy = self.direction.y * self.speed * Settings.DELTATIME
            self.rect.move_ip(dx, dy)

    #def check_win(self):
        #if self.rect.top < Settings.WINDOW.height-520:
            #self.reset_pos()
            
    
    def reset_pos(self):
        self.rect.centerx = Settings.WINDOW.centerx
        self.rect.bottom = Settings.WINDOW.bottom - 50
            

class Enemy(pygame.sprite.Sprite):
     def __init__(self, speed, startheight):
        super().__init__()
        self.image = pygame.image.load("images/icebear.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = pygame.rect.FRect(self.image.get_rect())
        self.rect.topleft = (0, startheight)
        self.speed = speed

     def update(self, *args: Any, **kwargs: Any):
         self.rect = self.rect.move(self.speed, 0)
         if self.rect.left < 0 or self.rect.right > Settings.WINDOW.width:
            self.kill()
         if "direction" in kwargs.keys():
            self.change_direction(kwargs["direction"])

     def change_direction(self, direction: str):
         currspeed = self.speed
         if direction == "stop":
            self.speed = 0
         elif direction == "start":
            self.speed = currspeed
         


class Game(object):
     def __init__(self) -> None:
        # variablen
        self.highscore = 0
        self.current_score = 0
        self.lifes = 3
        self.spawn_intervall = 2500
        self.en_speedmin = 1
        self.en_speedmid = 2
        self.en_speedmax = 3
        self.pause = False
        self.esc_count = 0
        self.p_mode = False

        # -----------
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 50"
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.WINDOW.size)
        # Background wird geladen
        self.background_image = pygame.image.load(os.path.join(Settings.IMAGE_PATH, "background.jpg")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (Settings.WINDOW.width, Settings.WINDOW.height))
        self.clock = pygame.time.Clock()
        self.enemy_spawn_timer = 0
        # Fox Object wird geladen
        self.fox = pygame.sprite.GroupSingle(Fox())
        # Enemy Objekte mit speed und Starthöhe
        self.all_enemies = pygame.sprite.Group()
        self.all_enemies.add(Enemy(2, 360))

        # Caption
        pygame.display.set_caption("Foxxer")
        
        self.running = False

     def reset_pos(self):
         self.fox.sprite.rect.x = Settings.WINDOW.centerx
         self.fox.sprite.rect.y = (Settings.WINDOW.bottom-100)

     def ScoreDisplay(self):
        pygame.font.init()
        font = pygame.font.Font(None, 36)
        textscore = font.render("Score: " + str(self.current_score), True, (0,0,0))
        textscore_rect = textscore.get_rect()
        textscore_rect.topleft = (0, 0)
        texthghscore = font.render("High Score: " + str(self.highscore), True, (0,0,0))
        texthghscore_rect = textscore.get_rect()
        texthghscore_rect.topleft = (0, 25)
        textlifes = font.render("Lifes: " + str(self.lifes), True, (0,0,0))
        textlifes_rect = textlifes.get_rect()
        textlifes_rect.topleft = (0, 50)
        self.screen.blit(textscore, textscore_rect)
        self.screen.blit(texthghscore, texthghscore_rect)
        self.screen.blit(textlifes, textlifes_rect)
         
     def check_win(self):
         if self.fox.sprite.rect.top < (Settings.WINDOW.height-520):
             self.current_score += 1
             if self.current_score > self.highscore:
                self.highscore = self.current_score
             print(f"Highscore: {self.highscore}")
             print(f"Current Score: {self.current_score}")
             self.reset_pos()
             self.en_speedmin += 0.2
             self.en_speedmax += 0.2
             if self.spawn_intervall != 500:
                self.spawn_intervall -= 200
        
     def check_gameover(self):
        if self.lifes == 0:
            print("----game over----")
            print(f"Highscore: {self.highscore}")
            print(f"Your Score: {self.current_score}")
            print("----game over----")
            self.current_score = 0
            self.lifes = 3
            self.en_speedmax = 3
            self.en_speedmid = 2
            self.en_speedmin = 1
            self.spawn_intervall = 2500
            self.reset_pos()
     
     def run(self) -> None:
        time_previous = time()
        self.running = True
        while self.running:
            self.watch_for_events()
            if self.pause == False:
                self.update()
            self.draw()
            self.clock.tick(Settings.FPS) #60 fps
            time_current = time()
            Settings.DELTATIME = time_current - time_previous
            time_previous = time_current
        pygame.quit()

            
     def update(self) -> None:
         self.rdmlist = [(self.en_speedmin, 260),(self.en_speedmax, 150),(self.en_speedmid,360)]
         self.check_win()
         # reset fox if hit with enemy and - 1 life
         if pygame.sprite.spritecollide(self.fox.sprite, self.all_enemies, False):
             self.lifes -= 1
             print(f"Your Lifes: {self.lifes}")
             self.check_gameover()
             self.reset_pos()

        # enemy spawner
         if self.pause != True:
            self.enemy_spawn_timer += self.clock.get_time()
            if self.enemy_spawn_timer >= self.spawn_intervall:
                rdm = randint(0,2) 
                self.all_enemies.add(Enemy(self.rdmlist[rdm][0], self.rdmlist[rdm][1]))
                self.enemy_spawn_timer = 0

            self.fox.update(action="move")
            self.all_enemies.update()


     
     def draw(self) -> None:
        self.screen.blit(self.background_image, (0, 0))
        self.all_enemies.draw(self.screen)
        self.fox.draw(self.screen)
        self.ScoreDisplay()
        if self.p_mode:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((Settings.GRAY[0], Settings.GRAY[1], Settings.GRAY[2], Settings.ALPHA))  # Fülle das Overlay mit Grau und der gewünschten Deckkraft
            self.screen.blit(overlay, (0, 0))
        

        pygame.display.flip()

     def watch_for_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:          # Taste drücken, taste ist runter gedrückt worden 
                if event.key == pygame.K_ESCAPE:        
                    self.esc_count += 1
                    if self.esc_count == 2:
                        self.running = False
                        
                elif event.key == pygame.K_RIGHT:       # Pfeiltasten §\label{srcTastatur0005}§
                    self.fox.update(direction="right")
                elif event.key == pygame.K_LEFT:
                    self.fox.update(direction="left")
                elif event.key == pygame.K_UP:
                    self.fox.update(direction="up")
                elif event.key == pygame.K_DOWN:
                    self.fox.update(direction="down")
                elif event.key == pygame.K_SPACE:
                    self.fox.update(direction="double")
                elif event.key == pygame.K_p:
                    if self.p_mode == False:
                        self.fox.update(direction="stop")
                        self.pause = True
                        self.p_mode = True
                    else:
                        self.p_mode = False
                        
                        self.fox.update(direction="start")
                        self.pause = False


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()