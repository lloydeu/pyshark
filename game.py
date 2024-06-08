
import pygame
from random import randint


# shark start pos ((SCREEN_WIDTH, random_y, SCREEN_WIDTH + self.width, random_y + self.height)) 
# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = 'pyShark'
MIN_SPAWN_HEIGHT = 10
MAX_SPAWN_HEIGHT = SCREEN_HEIGHT

def update(entity, dt):
    entity.rect.move_ip(entity.speed*dt, 0)
    

def main():
    # pygame setup
    pygame.init()

    # create player class
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.speed = 0
            self.width = 40
            self.height = 100
            self.surface = pygame.Surface((self.width, self.height))
            self.surface.fill("white")
            self.rect = self.surface.get_rect()
            # player start pos ((SCREEN_WIDTH/10), (SCREEN_HEIGHT-self.height)/2, (SCREEN_WIDTH/10)+ self.width, (SCREEN_HEIGHT-self.height)/2 + self.height )

    # create game entities
    class Fish(pygame.sprite.Sprite):
        def __init__(self):
            super(Fish, self).__init__()
            self.speed = randint(-20,20)
            self.surface = pygame.Surface((10,20))
            self.rect = self.surface.get_rect()  
          

    class Shark(Fish):
        def __init__(self):
            super(Shark, self).__init__()
            self.speed = 50
            self.height = 100
            self.word = "assign random string"
            #random_y = randint(MIN_SPAWN_HEIGHT, MAX_SPAWN_HEIGHT + 1)
            random_y = 10
            self.width = 40
            self.surface = pygame.Surface((self.width, self.height))
            self.surface.fill("black")
            self.rect = self.surface.get_rect()

    
    
    class Boss(Fish):
        def __init__(self):
            super(Boss, self).__init__()
            self.surface = pygame.Surface(10,20)
            self.rect = self.surface.get_rect()   

    # create screen
    screen = pygame.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT])
    pygame.display.set_caption(TITLE)

    # instantiate player
    player = Player()
    

    # instantiate clock and delta time
    dt = 0
    clock = pygame.time.Clock()
   

    running = True
        
    shark = Shark()

    # game loop
    while running:
        

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
       # background
        screen.fill("blue")
        land = pygame.Surface((SCREEN_WIDTH,int(1/8*SCREEN_HEIGHT)))
        land.fill("brown")
        screen.blit(land, (0,int(7/8*SCREEN_HEIGHT)))

        #player
        update(shark, dt)
        

        screen.blit(player.surface, player.rect)
    
        #shark
        screen.blit(shark.surface, shark.rect)

        pygame.display.flip()
        dt = clock.tick(30)/1000

       
   
    



    # game exit
    pygame.quit()
            
   

if __name__=='__main__':
    main()

    