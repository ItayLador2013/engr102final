# By submitting this assignment, I agree to the following:
#   "Aggies do not lie, cheat, or steal, or tolerate those who do"
#   "I have not given or received any unauthorized aid on this assignment"
#
# Names: Itay Lador
# David Butsch
# Ryan Hu
# Ese Oduware
# Section: 461
# Assignment: Lab 11
# Date: 3rd December 2024

#assets folder holds all images for the graphics
from util import * #import everything from the util file which holds my constant variables and helper functions (including pygame, random, and math)

#initiate the pygame and set a new screen
pygame.init() 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Fighter Jet")

#this is the game clock 
clock = pygame.time.Clock()


def write(text, font, fontsize, color, location):
    """display text on the screen with desired styles"""
    myFont = pygame.font.SysFont(font, fontsize)
    score_display = myFont.render(str(text), 1, color)
    screen.blit(score_display,location)

def info(lives, score):
    """display the player information of the lives and score on the top right of screen"""
    for i in range(lives):
        screen.blit(FULL_HEART, (i*HEART_WIDTH+HEARTS_PADDING, HEARTS_PADDING))

    for j in range(MAX_LIVES - lives):
        screen.blit(EMPTY_HEART, ((lives+j)*HEART_WIDTH+HEARTS_PADDING, HEARTS_PADDING))

    write(text=score, font="Times New Roman", fontsize=30, color=(0,0,0), location=((3 * (HEART_WIDTH + HEARTS_PADDING) / 2) - (len(str(score)) * 30) / 2, HEART_HEIGHT + HEARTS_PADDING))

class GameObject:
    def __init__(self, y=0, x=0, destroyed=False, vx=0, vy=0, body=None, width=0, height=0):
        self.y : float = y
        self.x : float = x
        self.destroyed : bool = destroyed
        self.vx : float = vx
        self.vy : float = vy
        self.body : pygame.Surface = body
        self.width : float = width
        self.height : float = height

    def update(self, dt):
        if not self.destroyed:
            self.x += self.vx * dt
            self.y += self.vy * dt
    
    def render(self):
        """display the object on the screen if it is not destroyed"""
        if not self.destroyed:
            screen.blit(self.body, (self.x, self.y))

#Warning is a warning object for a player for a incoming missile from behind
class Warning(GameObject):
    def __init__(self, y):
        super().__init__(y=y, x=0, body=WARNING, height=WARNING_HEIGHT, width=WARNING_WIDTH)
        self.time = 0
    
    def update(self, dt):
        """the warning follows the player's in the y with its velocity * 0.68. if warning time is over create a new enemy missile in the warning's y position"""
        self.time += dt #increment the time the warning exists by delta time
        if self.time >= WARNING_TIME / (game.level() / 2):
            game.warning = False
            game.last_fired = game.time
            game.objects.remove(self)
            game.objects.append(EnemyMissile(self.y))
        self.vy = player.vy * 0.68
        self.y += self.vy * dt

#An explosion to display when an object is destroyed
class Explosion(GameObject):
    def __init__(self, x, y):
        """create the explosion where its object used to be"""
        super().__init__(x=x,vx=-1000)
        self.explosion = random.choice(EXPLOSIONS)
        self.y = y - (self.explosion["height"] / 2)

    def render(self):
        """display the explosion on the screen"""
        screen.blit(self.explosion["body"], (self.x, self.y))

#Cloud object for decoration
class Cloud(GameObject):
    def __init__(self, right = 0):
        """create the cloud at a random x and y"""
        super().__init__(x=random.randint(screen.get_width(), screen.get_width() + 50), y=random.randint(0, int(screen.get_height() * 0.75)))
        self.cloud = random.choice(CLOUDS)

    def update(self, dt):
        """give the effect of the cloud staying in place while the player travels forward"""
        self.vx = -1000
        self.x += self.vx * dt
        #if cloud is off screen move it to right of screen and reshape it
        if self.x + self.cloud["width"] < 0:
            self.x = random.randint(screen.get_width(), screen.get_width() + 50)
            self.y = random.randint(0, int(screen.get_height() * 0.75))
            self.cloud = random.choice(CLOUDS)

    def render(self):
        """display the cloud on the screen"""
        screen.blit(self.cloud["body"], (self.x, self.y))

#A missile created by the player
class Missle(GameObject):
    def __init__(self, x=0, y=0, vx=0, vy=0, angle=0):
        """create a new missile at player's position, velocity, and angle """
        super().__init__(vx=vx, x=x, y=y, vy=vy,height=MISSILE_HEIGHT, width=MISSILE_WIDTH,body=MISSILE)
        self.angle = angle
        self.body = pygame.transform.rotate(MISSILE, angle)
        self.acceleration_factor = 4.5
        self.enemy = False

    def update(self, dt):
        """send the misile forward in a acceleration_factor times the player's accelecation in the x and y direction in accordance with its angle"""
        if not self.destroyed:
            self.vy += -self.acceleration_factor * ACCELERATION * math.sin(radian(self.angle)) * dt
            self.vx += self.acceleration_factor  * ACCELERATION * math.cos(radian(self.angle)) * dt
        else:
            self.vy = 0
            self.vx = -1000
        self.y += self.vy * dt
        self.x += self.vx * dt

        #check for collision with an enemy and destroyes the enemy and itself if collides
        if not self.destroyed:
            if self.enemy:
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

#EnemyMissile is a missile that fires at the player from behind
class EnemyMissile(Missle):
    def __init__(self, y):
        super().__init__(y=y, vx=500)
        self.x = random.randint(-100-self.width, -self.width)
        self.enemy = True
        self.acceleration_factor = 4

#An enemy drone
class Enemy(GameObject):
    def __init__(self):
        super().__init__(height=DRONE_HEIGHT, width=DRONE_WIDTH, body=DRONE, x=screen.get_width() + random.randint(0, int(screen.get_width() / 2)), vx= -1000 + random.randint(700, 900))
        self.y = random.randint(0, screen.get_height() - self.height)
        self.score = DRONE_SCORE

    def update(self, dt):
        """travels backwards at a random speed to give the effect of moving forward but slower than the player"""
        if self.destroyed:
            self.vx = -1000
        self.x += self.vx * dt

        #if an enemy is off screen player looses a life and another enemy is created
        if self.x < -self.width:
            game.enemies.append(Enemy())
            game.enemies.remove(self)
            if not self.destroyed:
                game.lives = max(game.lives-1, 0)
                if game.lives == 0:
                    player.kill()

class Player(GameObject):
    def __init__(self):
        """create a new player object"""
        super().__init__(body=PLAYER_FLYING, width=PLAYER_FLYING_WIDTH, height=PLAYER_FLYING_HEIGHT, y=screen.get_height() / 2, vy=1.0)
        self.og_body : pygame.Surface = PLAYER_FLYING
        self.angle : float = 0.0
        self.fired : list[Missle] = []
        self.last_fired : float = 0.0
        self.time_of_death : float = 0

    def kill(self):
        """called when the player dies"""
        self.destroyed = True
        game.lives = 0
        self.time_of_death = game.time

    def update(self, dt):
        """move the player's nose in accordance with user input"""
        #move player nose up - giving an upward aceleration on the y axis
        if keys[pygame.K_w]:
            self.angle += 0.2
            self.vy -= ACCELERATION * math.cos(radian(self.angle)) * dt

        #move player nose down - giving an downward aceleration on the y axis
        if keys[pygame.K_s]:
            self.angle -= 0.2
            self.vy += ACCELERATION * math.cos(radian(self.angle)) * dt
        
        #shoot rockets
        if keys[pygame.K_SPACE]:
            if game.time - self.last_fired > 1:
                self.last_fired = game.time
                self.fired.append(Missle(self.x + PLAYER_FLYING_WIDTH / 2, self.y + PLAYER_FLYING_HEIGHT / 2, 0, self.vy, self.angle))
        
        self.vx = 0 if math.tan(radian(self.angle)) is None or math.tan(radian(self.angle)) == 0 else abs( self.vy / math.tan(radian(self.angle)))
        self.body = pygame.transform.rotate(self.og_body, self.angle) #rotate the body with the current angle

        #update every missile the player fired 
        for missile in self.fired:
            missile.update(dt)

        if self.destroyed: 
            self.vy = 0
        self.y += self.vy * dt

        #check if the player collides with a living enemy and kill the player if True
        for enemy in game.enemies:
            if enemy.destroyed:
                continue
            if collision(self, enemy, plane=True):
                self.kill()
                game.add_object(Explosion(self.x + self.width / 2, self.y))
                enemy.destroyed = True
                game.add_object(Explosion(enemy.x, enemy.y))
        
    def render(self):
        """display the player and the player's missiles on the screen"""
        #display missiles that were fired from the left wing of the player
        for index, missile in enumerate(self.fired):
            if index % 2 == 1:
                missile.render()

        super().render()
        
        #display misiles that were fired from the right wing of the player
        for index, missile in enumerate(self.fired):
            if index % 2 == 0:
                missile.render()

class Game():
    def __init__(self, screen="init"):
        """initiate a new game"""
        self.running : bool = True
        self.background : tuple[int] = BACKGROUND_COLOR
        self.objects : list[GameObject] = []
        self.time : float = 0
        self.paused : bool = False
        self.lives : int = 3
        self.score : int = 0
        self.name : list[str] = ["A", "A", "A"]
        self.scores : list[dict] = []
        self.enemies : list[Enemy] = [Enemy(), Enemy()]
        self.last_fired : float = 0
        self.warning : bool = False
        self.every : float = WARNING_EVERY
        self.screen : pygame.Surface = screen
        self.selected : int = 0
        self.last_pressed : float = 0
        self.restarting : bool = True
        self.letter_selected : int = 0
    
    def pressed(self, key) -> bool:
        """checks if a key was pressed within a certain range of the last time a key was pressed - returns True or False"""
        if self.time - self.last_pressed  > 0.2 and key:
            self.last_pressed = self.time
            return True
        return False
    
    def level(self) -> int:
        """returns the current level the player is at based on the time in game"""
        return (self.time // 20) + 1

    def save_score(self):
        """saves the updated high scores list to the csv file"""
        file = open("high_scores.csv", "w")
        file.write("name,score\n")
        for score in self.scores:
            file.write(score['name'] + "," + str(score['score']) + "\n")
        file.close()
    
    def check_for_high_score(self) -> int:
        """returns the player's ranking if player's score is in top 5. returns None otherwise."""
        i = 0
        for s in self.scores:
            if self.score > s["score"]:
                return i
            i+=1

        if len(self.scores) < 5:
            return len(self.scores)
        
        return None

    def load_scores(self):
        """trying to load the high scores from the csv file. if no high_scores.csv file exists - it creates a new one."""
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
        """ends the game"""
        self.running = False
        self.restarting = False
    
    def add_object(self, obj):
        """adds an object to the game (cloud, missile, warning, explosion)"""
        self.objects.append(obj)
    
    def pause(self):
        """pause the game"""
        self.paused = True
    
    def resume(self):
        """resume the game"""
        self.paused = False
    
    def start(self):
        """start the game"""
        self.screen = "game"
        self.selected = 0
        self.time = 0

    def end_game(self):
        """end the game and move to the next screen - if high score move to new high score screen otherwise end"""
        if self.check_for_high_score() != None:
            self.screen = "high_score"
        else:
            self.screen = "end"

    def update(self, dt):
        """update the game and all its objects"""
        self.time += dt #increment the time by dt
        
        #update all the game's contents if the game is going
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

        #updates the main menue with user input
        elif self.screen == "init":
            if self.pressed(keys[pygame.K_RETURN]):
                if self.selected == 0:
                    game.start()
                elif self.selected == 1:
                    game.screen = "scores"
                elif self.selected == 2:
                    game.screen = "instructions"

            if self.pressed(keys[pygame.K_s]):
                self.selected = (self.selected + 1) % 3

            if self.pressed(keys[pygame.K_w]):
                self.selected = (self.selected - 1) % 3
        
        #updates the high scores screen with user input
        elif game.screen == "scores" or game.screen == "instructions":
            if keys[pygame.K_ESCAPE]:
                self.screen = "init"

        #updates the new high score screen with user input
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
        
        #updates the game over screen with user input
        elif game.screen == "end":
            if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                self.restarting = True
                self.running = False

    def render(self):
        """displays the game and all of its objects on the screen in accordance to current screen"""
        screen.fill(self.background) #fill the background
        for obj in self.objects:
            obj.render()

        if self.screen == "game":
            for enemy in self.enemies:
                enemy.render()
            
            info(self.lives, self.score)

        elif self.screen == "init":
            write("Start Game", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 0 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 - 110))
            write("High Scores", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 1 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 + 0))
            write("Instructions", font="Times New Roman", fontsize=80, color=SELECTED_COLOR if self.selected == 2 else (0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 + 110))
            write("use W S keys to navigate menue and ENTER/RETURN to select", font="Times New Roman", fontsize=20, color=(0,0,0), location=(screen.get_width() / 2 , screen.get_height() / 2 + 220))

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

        elif self.screen == "instructions":
            write(
                "Fly a fighter jet to defend your country ",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 100)
            )
            write(
                "from an autonomous drone attack. Use S W keys",
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
                "past you, you fail your mission. Watch",
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
                "missiles. If you get hit by a missile",
                font="Times New Roman",
                fontsize=30,
                color=(0, 0, 0),
                location=(screen.get_width() / 2, 280)
            )
            write(
                "or collide with a drone, you die.",
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
                "the ESCAPE key.",
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
                
                

restarting = True #variable to manage looping of game when game is over
high_scored = False #stores if the player reached a top 5 high score in the current game iteration
while restarting:
    game = Game() if not high_scored else Game("scores") #start a new game
    #create cloud objects
    for i in range(3):
        game.add_object(Cloud(random.randint(0, int(screen.get_width() * 0.75))))
    
    player = Player() #create a new player
    game.add_object(player)

    game.load_scores() #load the high scores

    dt = clock.tick(100) / 1000 #set the delta time with 100 frames per second

    #loops with delta time between each iteration, updates, and displays the updates on the screen
    while game.running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.end()
        keys = pygame.key.get_pressed() #gets all keys pressed at the moment
        

        if game.screen == "game" and keys[pygame.K_ESCAPE]:
            game.pause()
        if not game.paused:
            game.update(dt) #updates the game with delta time
            game.render() #rerenders the game
        else:
            if keys[pygame.K_RETURN]:
                game.resume()

        pygame.display.flip() #shows everying on the screen
        dt = clock.tick(100) / 1000  #set the delta time with 100 frames per second

    #when the game is over checks whether the user wishes to restart and whether a high score was reached
    if game.check_for_high_score() is not None:
        high_scored = True
    else:
        high_scored = False
    restarting = game.restarting

#end the game and close the screen
pygame.quit()
