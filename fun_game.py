import pygame
from util import *
import math
import time
import random

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fighter Jet")

clock = pygame.time.Clock()


def write(text, font, fontsize, color, location):
    myFont = pygame.font.SysFont(font, fontsize)
    score_display = myFont.render(str(text), 1, color)
    screen.blit(score_display,location)

def info(lives, score):
    for i in range(lives):
        screen.blit(FULL_HEART, (i*HEART_WIDTH+HEARTS_PADDING, HEARTS_PADDING))

    for j in range(MAX_LIVES - lives):
        screen.blit(EMPTY_HEART, ((lives+j)*HEART_WIDTH+HEARTS_PADDING, HEARTS_PADDING))

    write(text=score, font="Times New Roman", fontsize=30, color=(0,0,0), location=((3 * (HEART_WIDTH + HEARTS_PADDING) / 2) - (len(str(score)) * 30) / 2, HEART_HEIGHT + HEARTS_PADDING))

class EnemyMissile():
    def __init__(self, y):
        self.y = y
        self.width = MISSILE_WIDTH
        self.height = MISSILE_HEIGHT
        self.body = MISSILE
        self.x = random.randint(-100-self.width, -self.width)
        self.destroyed = False
        self.vx = 500

    def update(self, dt):
        if not self.destroyed:
            self.vx += 4  * ACCELERATION * dt
        else:
            self.vy = 0
            self.vx = -1000
        self.x += self.vx * dt

        if not self.destroyed:
            if collision(player, self, plane=True):
                self.destroyed = True
                player.kill()
                game.add_object(Explosion(player.x + player.width * 0.6, player.y))

            for enemy in game.enemies:
                if collision(self, enemy):
                    self.destroyed = True
                    enemy.destroyed = True
                    game.add_object(Explosion(enemy.x, enemy.y))
                    game.score += enemy.score
        
    def render(self):
        if not self.destroyed:
            screen.blit(self.body, (self.x, self.y))

class Warning():
    
    def __init__(self, y):
        self.x = 0
        self.y = y
        self.body = WARNING
        self.height = WARNING_HEIGHT
        self.width = WARNING_WIDTH
        self.time = 0
    
    def update(self, dt):
        self.time += dt
        if self.time >= WARNING_TIME / (game.level() / 2):
            game.warning = False
            game.last_fired = game.time
            game.objects.remove(self)
            game.objects.append(EnemyMissile(self.y))
        self.vy = player.vy * 0.68
        self.y += self.vy * dt
    
    def render(self):
        if not player.destroyed:
            screen.blit(self.body, (self.x, self.y))


class Explosion():
    def __init__(self, x, y):
        self.explosion = random.choice(EXPLOSIONS)
        self.x = x
        self.y = y - (self.explosion["height"] / 2)
        self.vx = -1000

    def update(self, dt):
        self.x += self.vx * dt

    def render(self):
        screen.blit(self.explosion["body"], (self.x, self.y))

class Cloud():
    def __init__(self, right = 0):
        self.vx = 0
        self.vy = 0
        self.x = random.randint(screen.get_width(), screen.get_width() + 50)
        self.y = random.randint(0, screen.get_height() * 0.75)
        self.cloud = random.choice(CLOUDS)
        self.visible = True

    def update(self, dt):
        self.vx = -1000
        self.x += self.vx * dt
        if self.x + self.cloud["width"] < 0:
            self.x = random.randint(screen.get_width(), screen.get_width() + 50)
            self.y = random.randint(0, screen.get_height() * 0.75)
            self.cloud = random.choice(CLOUDS)

    def render(self):
        screen.blit(self.cloud["body"], (self.x, self.y))

class Missle():
    def __init__(self, x, y, vx, vy, angle):
        self.x = x + PLAYER_FLYING_WIDTH / 2
        self.y = y + PLAYER_FLYING_HEIGHT / 2
        self.vx = 0
        self.vy = vy
        self.angle = angle
        self.height = MISSILE_HEIGHT
        self.width = MISSILE_WIDTH
        self.body = pygame.transform.rotate(MISSILE, angle)
        self.destroyed = False

    def update(self, dt):
        if not self.destroyed:
            self.vy += -4.5 * ACCELERATION * math.sin(radian(self.angle)) * dt
            self.vx += 4.5  * ACCELERATION * math.cos(radian(self.angle)) * dt
        else:
            self.vy = 0
            self.vx = -1000
        self.y += self.vy * dt
        self.x += self.vx * dt

        if not self.destroyed:
            for enemy in game.enemies:
                if collision(self, enemy):
                    self.destroyed = True
                    enemy.destroyed = True
                    game.add_object(Explosion(enemy.x, enemy.y))
                    game.score += enemy.score
        
    def render(self):
        if not self.destroyed:
            screen.blit(self.body, (self.x, self.y))

class Enemy():
    def __init__(self):
        self.height = DRONE_HEIGHT
        self.width = DRONE_WIDTH
        self.body = DRONE
        self.x = screen.get_width() + random.randint(0, screen.get_width() / 2)
        self.y = random.randint(0, screen.get_height() - self.height)
        self.vx = -1000 +random.randint(700, 900)
        self.destroyed = False
        self.score = DRONE_SCORE

    def update(self, dt):
        if self.destroyed:
            self.vx = -1000
        self.x += self.vx * dt

        if self.x < -self.width:
            game.enemies.append(Enemy())
            game.enemies.remove(self)
            if not self.destroyed:
                game.lives = max(game.lives-1, 0)
                if game.lives == 0:
                    player.kill()

    def render(self):
        if not self.destroyed:
            screen.blit(self.body, (self.x, self.y))

class Player():
    def __init__(self):
        self.body = PLAYER_FLYING
        self.og_body = PLAYER_FLYING
        self.width = PLAYER_FLYING_WIDTH
        self.height = PLAYER_FLYING_HEIGHT
        self.x = 0
        self.vx = 0.0
        self.y = screen.get_height() / 2
        self.vy = 1.0
        self.angle = 0.0
        self.fired = []
        self.last_fired = 0.0
        self.destroyed = False
        self.time_of_death = 0

    def kill(self):
        self.destroyed = True
        game.lives = 0
        self.time_of_death = game.time

    def update(self, dt):
        if keys[pygame.K_w]:
            self.angle += 0.2
            self.vy -= ACCELERATION * math.cos(radian(self.angle)) * dt
        if keys[pygame.K_s]:
            self.angle -= 0.2
            self.vy += ACCELERATION * math.cos(radian(self.angle)) * dt
        if keys[pygame.K_r]:
            self.vy = 0
        if keys[pygame.K_SPACE]:
            if game.time - self.last_fired > 1:
                self.last_fired = game.time
                self.fired.append(Missle(self.x, self.y, self.vx, self.vy, self.angle))
        
        self.vx = 0 if math.tan(radian(self.angle)) is None or math.tan(radian(self.angle)) == 0 else abs( self.vy / math.tan(radian(self.angle)))
        self.body = pygame.transform.rotate(self.og_body, self.angle)

        for missile in self.fired:
            missile.update(dt)

        if self.destroyed: 
            self.vy = 0
        self.y += self.vy * dt

        for enemy in game.enemies:
            if enemy.destroyed:
                continue
            if collision(self, enemy, plane=True):
                self.kill()
                game.add_object(Explosion(self.x + self.width / 2, self.y))
                enemy.destroyed = True
                game.add_object(Explosion(enemy.x, enemy.y))
        
    def render(self):
        for index, missile in enumerate(self.fired):
            if index % 2 == 1:
                missile.render()
        if not self.destroyed:
            screen.blit(self.body, (self.x, self.y))
        
        for index, missile in enumerate(self.fired):
            if index % 2 == 0:
                missile.render()

class Game():
    def __init__(self, screen="init"):
        self.running = True
        self.background = BACKGROUND_COLOR
        self.objects = []
        self.time = 0
        self.paused = False
        self.lives = 3
        self.score = 0
        self.name = ["A", "A", "A"]
        self.scores = []
        self.lives
        self.enemies = [Enemy(), Enemy()]
        self.last_fired = 0
        self.warning = False
        self.every = WARNING_EVERY
        self.screen = screen
        self.selected = 0
        self.last_pressed = 0
        self.restarting = True
        self.letter_selected = 0
    
    def pressed(self, key):
        if self.time - self.last_pressed  > 0.2 and key:
            self.last_pressed = self.time
            return True
        return False
    
    def level(self):
        return (self.time // 20) + 1

    def save_score(self):
        file = open("high_scores.csv", "w")
        file.write("name,score\n")
        for score in self.scores:
            file.write(score['name'] + "," + str(score['score']) + "\n")
        file.close()
    
    def check_for_high_score(self):
        i = 0

        for s in self.scores:
            if self.score > s["score"]:
                return i
            i+=1

        if len(self.scores) < 5:
            return len(self.scores)
        
        return None

    def load_scores(self):
        try:
            file = open("high_scores.csv", "r")
            index = -1
            for line in file:
                index += 1
                if index == 0:
                    continue
                line_lst = line.split(",")
                self.scores.append({"name": line_lst[0], "score": int(line_lst[1])})
            self.scores.sort(key=lambda x:x["score"], reverse=True)
        except FileNotFoundError:
            self.scores = []

    def end(self):
        self.running = False
        self.restarting = False
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
    
    def start(self):
        self.screen = "game"
        self.selected = 0
        self.time = 0

    def end_game(self):
        if self.check_for_high_score() != None:
            self.screen = "high_score"
        else:
            self.screen = "end"

    def update(self, dt):
        self.time += dt
        if self.screen == "game":

            if player.destroyed and not (game.time - player.time_of_death < 2):
                self.end_game()
                return
            
            if not self.warning and self.time - self.last_fired > random.randint(WARNING_EVERY // 3, WARNING_EVERY):
                self.warning = True
                self.add_object(Warning(y=player.y))
            for obj in self.objects:
                obj.update(dt)
            for enemy in self.enemies:
                enemy.update(dt)

        elif self.screen == "init":
            if self.pressed(keys[pygame.K_RETURN]):
                if self.selected == 0:
                    game.start()
                elif self.selected == 1:
                    game.screen = "scores"
                elif self.selected == 2:
                    game.screen = "about"

            if self.pressed(keys[pygame.K_s]):
                self.selected = (self.selected + 1) % 3

            if self.pressed(keys[pygame.K_w]):
                self.selected = (self.selected - 1) % 3
        elif game.screen == "scores" or game.screen == "about":
            if keys[pygame.K_ESCAPE]:
                self.screen = "init"

        elif game.screen == "high_score":
            if self.pressed(keys[pygame.K_w]):
                self.name[self.letter_selected] = ABC[(ABC.find(self.name[self.letter_selected]) - 1 ) % len(ABC)]
            if self.pressed(keys[pygame.K_s]): 
                self.name[self.letter_selected] = ABC[(ABC.find(self.name[self.letter_selected]) + 1 ) % len(ABC)]
            if self.pressed(keys[pygame.K_a]):
                self.letter_selected = (self.letter_selected - 1) % len(self.name)
            if self.pressed(keys[pygame.K_d]):
                self.letter_selected = (self.letter_selected + 1) % len(self.name)
            
            if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                self.scores.insert(self.check_for_high_score(), {"name": ''.join(self.name), "score": self.score})
                self.scores = self.scores[:5]
                self.save_score()
                self.restarting = True
                self.running = False

        elif game.screen == "end":
            if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                self.restarting = True
                self.running = False

    def render(self):
        screen.fill(self.background)
        for obj in self.objects:
            obj.render()

        if self.screen == "game":
            for enemy in self.enemies:
                enemy.render()
            
            info(self.lives, self.score)

        elif self.screen == "init":
            write("Start Game", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 0 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 - 110))
            write("High Scores", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 1 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 + 0))
            write("About", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 2 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 + 110))


        elif self.screen == "scores":
            write(
                "High Scores",
                font="Times New Roman",
                fontsize=60,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 100)
            )
            
            for index, score in enumerate(self.scores):
                y_position = 200 + index * 50
                write(
                    f"{index + 1}. {score['name']} - {score['score']}",
                    font="Times New Roman",
                    fontsize=40,
                    color=(0, 0, 0),
                    location=(screen.get_width() / 2, y_position)
                )

            write(
                "To return to main menue enter ESCAPE",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 580)
            )

        elif self.screen == "about":
            write(
                "Fly a fighter jet to defend your country ",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 100)
            )
            write(
                "from autonomous drone attack. Use S W keys",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 130)
            )
            write(
                "to control your aircraft's nose and SPACE",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 160)
            )
            write(
                "to fire rockets. If more than 3 drones get",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 190)
            )
            write(
                "passed you, you fail your mission. Watch",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 220)
            )
            write(
                "for warnings behind you that mark incoming",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 250)
            )
            write(
                "missiles. If your get hit by a missile",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 280)
            )
            write(
                "or collide with a drone, your die.",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 310)
            )

            write(
                "You can pause your game at any time using",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 500)
            )
            write(
                " the ESCAPE key.",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 530)
            )

            write(
                "To return to main menue enter ESCAPE",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 580)
            )
            
        elif self.screen == "high_score":
            write(
                "NEW HIGH SCORE!",
                font="Times New Roman",
                fontsize=40,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 100)
            )
            write(
                "FINAL SCORE: " + str(self.score),
                font="Times New Roman",
                fontsize=40,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 150)
            )

            write(
                "enter your initials (use awsd keys)",
                font="Times New Roman",
                fontsize=25,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 200)
            )

            for index, char in enumerate(self.name):
                write(
                    f"{char}",
                    font="Times New Roman",
                    fontsize=60,
                    color= SELECTED_COLOR if self.letter_selected == index else (0, 0, 0),
                    location=(screen.get_width() / 2 + 45 * index , 300)
                )

            write(
                "press ENTER / RETURN to finish",
                font="Times New Roman",
                fontsize=25,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 400)
            )


        elif self.screen == "end":
            write(
                "GAME OVER",
                font="Times New Roman",
                fontsize=40,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 100)
            )
            write(
                "FINAL SCORE: " + str(self.score),
                font="Times New Roman",
                fontsize=40,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 150)
            )
            write(
                "press ENTER / RETURN to restart",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 200)
            )
                
restarting = True
high_scored = False
while restarting:
    game = Game() if not high_scored else Game("scores")
    player = Player()
    for i in range(3):
        game.add_object(Cloud(random.randint(0, screen.get_width() * 0.75)))
    game.add_object(player)
    game.load_scores()

    dt = clock.tick(100) / 1000
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.end()
        keys = pygame.key.get_pressed()
        

        if game.screen == "game" and keys[pygame.K_ESCAPE]:
            game.pause()
        if not game.paused:
            game.update(dt)
            game.render()
        else:
            if keys[pygame.K_RETURN]:
                game.resume()

        pygame.display.flip()
        dt = clock.tick(100) / 1000  # limits FPS to 60

    if game.check_for_high_score() is not None:
        high_scored = True
    else:
        high_scored = False
    restarting = game.restarting

pygame.quit()