# to do:
# animate fishes
# word database
# bosses
# sounds
# death

import pygame
from random import randint, choice
from webbrowser import open as open_link
import pygame.image
import pygame.docs

pygame.init()

# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = 'pyShark Typer'
MIN_SPAWN_HEIGHT = 10
MAX_SPAWN_HEIGHT = int(SCREEN_HEIGHT * 0.8)
SHARK_WORDS = []
FISH = True
SHARK = True
BOSS = True
BUBBLES = True
MUSIC = True
GAME_FONT =  pygame.font.Font(None, int(SCREEN_HEIGHT*0.075))
FPS = 30

# groups
entities = pygame.sprite.Group()
buttons = pygame.sprite.Group()
bubbles = pygame.sprite.Group()
players = pygame.sprite.Group()
bombs = pygame.sprite.Group()
sharks = pygame.sprite.RenderUpdates()
bosses = pygame.sprite.GroupSingle()
fishes = pygame.sprite.RenderUpdates()
deads = pygame.sprite.Group()
breakthrough_enemy = pygame.sprite.GroupSingle()

def return_args(args):
    return args

def wordlist_from_file(file):
    # gives a list of all words separated by line in a txt file   

    result = []
    with open(file) as Reader:
        lines = Reader.readlines(-1)
        for line in lines:
            newline = line[:-1]
            result.append(newline)
    return result

def flip_sprites(sprite_list : list):
    # flips the sprites horizontally

    my_list = []
    for sprite in sprite_list:
        my_list.append(pygame.transform.flip(sprite,True, False))
    return my_list

def load_sounds(sound_name):
    # returns a sound
    file = sound_name + '.wav'
    return pygame.mixer.Sound(file)


def load_sprites(entity_name, number_of_frames, size):
    # gives a list of all sprite images for an entity
    
    surfaces = []
    for i in range (number_of_frames):
        file = entity_name + '_' + str(i+1)+'.png'
        surfaces.append(
            pygame.transform.scale(
                pygame.image.load(
                    file).convert_alpha(), size))
    return surfaces

def update(entity, dt, animation_frame, y_velocity = 0, do_not_orient = False):
    # updates all sprites to their new position and sprite image
    
    # make sure the sprite faces the right direction
    if not do_not_orient:
        if entity.x_velocity > 0:
            entity.sprites = entity.sprites_right
        else:
            entity.sprites = entity.sprites_left
        
    # animate only alive sprites
    if entity.active:
        entity.image = entity.sprites[animation_frame//3].copy()
    entity.rect.move_ip(entity.x_velocity*dt, y_velocity*dt)

    # kill all sprites that go beyond the screen
    if entity.rect.right < -10:
        if not entity.hostile:
            entity.kill()

    if entity.rect.left > SCREEN_WIDTH + 10 or entity.rect.bottom < -10 or entity.rect.top > SCREEN_HEIGHT + 10:
        entity.kill()

# game entities

class Button(pygame.sprite.Sprite):

    def __init__(self, word, sprites, button_center,  onclick, args = None):
        super(Button, self).__init__()

        self.x_velocity = 0
        self.y_velocity = 0
        self.active = True
        self.hostile = False
        self.width = sprites[0].get_width()
        self.height = sprites[0].get_height()
        self.sprites = sprites
        self.sprites_left = sprites
        self.sprites_right = flip_sprites(sprites)
        self.image = sprites[0].copy()
        self.rect = self.image.get_rect(center = button_center)
        self.word = word
        self.on_click = onclick
        self.args = args

        self.add(buttons)

    def onclick(button):
        if button.args == None:
            return button.on_click()
        else:
            return button.on_click(button.args)
    
class Player(pygame.sprite.Sprite):
    def __init__(self, sprites):
        super(Player, self).__init__()

        self.x_velocity = 0
        self.y_velocity = 0
        self.active = True
        self.hostile = True
        self.width = sprites[0].get_width()
        self.height = sprites[0].get_height()

        self.image = None
        self.rect = sprites[0].get_rect(center = (-SCREEN_WIDTH *0.85, SCREEN_HEIGHT//2))

        self.sprites = None
        self.sprites_left = flip_sprites(sprites)
        self.sprites_right = sprites

        self.add(entities)
        self.add(players)
       
class Fish(pygame.sprite.Sprite):
    def __init__(self, sprites):
        super(Fish, self).__init__()

        self.x_velocity = randint(25,50)*choice([1,-1])
        self.y_velocity = 0
        self.active = True
        self.hostile = False
        self.width = sprites[0].get_width()
        self.height = sprites[0].get_height()
        self.random_y = randint(MIN_SPAWN_HEIGHT, MAX_SPAWN_HEIGHT)
        if self.x_velocity > 0: 
            self.random_x = -self.width
        else: 
            self.random_x = SCREEN_WIDTH

        self.image = None
        self.rect = sprites[0].get_rect(x = self.random_x, y = self.random_y)

        self.sprites = None
        self.sprites_left = sprites
        self.sprites_right = flip_sprites(sprites)
        
        self.add(fishes)
        self.add(entities)



class Shark(pygame.sprite.Sprite):
    start_x_velocity = -100
    sharks_dead = 0
    max_sharks = 3 + sharks_dead//10
    spawn_rate = {'num': 40 + sharks_dead//5,
                  'den': 100}

    def __init__(self, sprites):
        super(Shark, self).__init__()
        max_word_len = Shark.sharks_dead//10 + 3
        self.x_velocity = Shark.start_x_velocity - Shark.sharks_dead
        self.y_velocity = 0
        self.active = True
        self.hostile = True
        self.width = sprites[0].get_width()
        self.height = sprites[0].get_height()
        shark_y = []
        for i in range(20,SCREEN_HEIGHT - 1*self.height, self.height):
            shark_y.append(i)
        self.random_y = choice(shark_y)
        
        self.image = None
        self.rect = sprites[0].get_rect(x = SCREEN_WIDTH, y = self.random_y)
        self.word = choice(SHARK_WORDS)
        while len(self.word) > max_word_len or not self.word.isalpha():
            self.word = choice(SHARK_WORDS)
       
        self.sprites = None
        self.sprites_left = sprites
        self.sprites_right = flip_sprites(sprites)
        self.dead = sprites[len(sprites)-1]

        self.add(sharks)
        self.add(entities)

    def draw_word(shark):
        if shark.active:
            x_start = 300
            word = shark.word     
            
            temp_surface = GAME_FONT.render(shark.word, True, 'white')
            cumulative_width = x_start
            for char in word:
                surface = GAME_FONT.render(char, True, 'white')
                surface.blit(surface, surface.get_rect(x = cumulative_width))
                cumulative_width += surface.get_width()
        
            shark.image.blit(temp_surface, temp_surface.get_rect(center = (shark.width*2//5, shark.height//2)))
                            
class Boss(pygame.sprite.Sprite):
   
    words = {'megalodon':['2', '6', '10', '15', '19', '23', 'hexamethyl', '2', '6', '10','14', '18', '22', 'tetracosahexaene'] 
}
    start_x_velocity = -100
    boss = load_sounds('boss')

    def __init__(self, sprites):
        super(Boss, self).__init__()

        self.default_x_velocity = Boss.start_x_velocity
        self.x_velocity = self.default_x_velocity
        self.y_velocity = 0
        self.active = True
        self.hostile = True
        self.width = sprites[0].get_width()
        self.height = sprites[0].get_height()
        self.image = None
        self.rect = sprites[0].get_rect(x = SCREEN_WIDTH, y = 20)
        self.words= Boss.words['megalodon']
        self.index = 0
        self.word = self.words[self.index]
        self.sprites = None
        self.sprites_left = sprites
        self.sprites_right = flip_sprites(sprites)
        self.knockbacked = False
        self.stunned = False
        self.status_frames = 10
        self.status_frame = self.status_frames
        self.dead = sprites[len(sprites)-1]
        self.life = len(self.words)

        self.add(bosses)
        Boss.boss.play()

    def draw_word(boss):
         if boss.active:
           
            x_start = 300
            word = boss.word
            boss_font = pygame.font.Font(None, boss.height//6)     
            
            temp_surface = boss_font.render(word, True, 'white')
            cumulative_width = x_start
            for char in word:
                surface = boss_font.render(char, True, 'white')
                surface.blit(surface, surface.get_rect(x = cumulative_width))
                cumulative_width += surface.get_width()
        
            boss.image.blit(temp_surface, temp_surface.get_rect(center = (boss.width*4//9, boss.height//2)))

    def update_word(boss):
        boss.word = boss.words[boss.index]

def main(screen):
    global SHARK
    global FISH
    global BUBBLES
    global BOSS
   
    # create word list 
    SHARK_WORDS.extend(wordlist_from_file('english-common-words.txt'))

    # define sprites
    game_sprites = {'background': load_sprites('bg', 1, (1600, 600)),
                    'shark': load_sprites('shark', 9, (804//2, 350//2)),
                    'megalodon': load_sprites('megalodon', 9, (804, 500)),
                    'fish1': load_sprites('red', 4, (129//2, 109//2)),
                    'fish2': load_sprites('blue', 4, (129//2, 109//2)),
                    'fish3': load_sprites('green', 4, (129//2, 109//2)),
                    'fish4': load_sprites('pink', 4, (129//2, 109//2)),
                    'bubble': load_sprites('bubble', 1, (27, 27)),
                    'player': load_sprites('player', 8, (500//3, 500//3)),
                    'bomb': load_sprites('bomb', 1, (322, 600))}
        
    # sounds
    game_sounds = {'select': load_sounds('select'),
                   'hit': load_sounds('hit'),
                   'points': load_sounds('points'),
                   'boss': load_sounds('boss'),
                   'explosion': load_sounds('explosion')}

    # initialize event timer
    SPAWN_SHARK = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_SHARK, 1800)
    SPAWN_FISH = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWN_FISH, 3500)
    SPAWN_BUBBLES = pygame.USEREVENT + 3
    pygame.time.set_timer(SPAWN_BUBBLES, 900)
    SPAWN_BOSS = pygame.USEREVENT + 4
    SCROLL = pygame.USEREVENT + 5
    GAME_END = pygame.USEREVENT + 6
    
    # instantiate clock and delta time
    dt = 0
    clock = pygame.time.Clock()
   
    # text input
    user_text = ''
    running = True
              
    # initialize background
    bg_image = game_sprites['background'][0]
    bg_image_rect = bg_image.get_rect(x = -SCREEN_WIDTH)
    
    # Enable spawns
    SHARK = True
    FISH = True
    BOSS = True
    BUBBLES = True

    # start counters
    animation_frame = 0
    animation_frame2 = 0
    score = 0
    bg_scroll = False
    scroll_frame = 0
    scroll_speed = 500
    game_over = False

    # game loop
    while running:

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [False, False]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  
                    user_text = user_text[:-1]
                elif event.key == pygame.K_DELETE:
                    user_text = ''
                else:
                    try:
                        code = (ord(event.unicode)) 
                    except:
                        continue
                       
                    if code > 64 and code < 123:
                        user_text += event.unicode
                    
                    if code > 46 and code < 58 and len(bosses) > 0:
                        user_text += event.unicode

            if event.type == SPAWN_SHARK and SHARK and len(bosses) < 1:  
                if len(sharks) < Shark.max_sharks and randint(1,Shark.spawn_rate['den']) <= Shark.spawn_rate['num']:
                    new_shark = Shark(game_sprites['shark'])

            if event.type == SPAWN_BOSS and BOSS:
                megalodon = Boss(game_sprites['megalodon'])
                update(megalodon, dt, animation_frame)
                SHARK = False
                FISH = False

                for fish in fishes:
                    fish.x_velocity = fish.x_velocity * 3

            if event.type == SPAWN_FISH and FISH:
                new_fish = Fish(game_sprites['fish'+str(randint(1,4))])
                
            if event.type == SPAWN_BUBBLES:
                bubble = pygame.sprite.Sprite(bubbles)
                bubble.x_velocity = randint(-100,100)
                bubble.active = True
                bubble.hostile = False
                bubble.image = game_sprites['bubble'][0]
                bubble.rect = bubble.image.get_rect(center = (randint(20, SCREEN_WIDTH-20), SCREEN_HEIGHT))
                bubble.sprites_right = game_sprites['bubble']
                bubble.sprites_left = game_sprites['bubble']
                bubble.add(entities)

            if event.type == SCROLL:
                my_player = Player(game_sprites['player'])
                bomb = pygame.sprite.Sprite()
                bomb.x_velocity = 0
                bomb.y_velocity = 0
                bomb.image = game_sprites['bomb'][0]
                bomb.rect = bomb.image.get_rect(center = (-SCREEN_WIDTH*0.6, SCREEN_HEIGHT*0.7))
                bomb.active = True
                bomb.hostile = True
                bomb.sprites = game_sprites['bomb']
                bomb.sprites_left = flip_sprites(bomb.sprites)
                bomb.sprites_right = bomb.sprites
                bomb.add(entities)
                bomb.add(bombs)

                
                for entity in entities:
                    entity.x_velocity = scroll_speed
                for boss in bosses:
                    boss.knockbacked = True
                bg_scroll = True
                SHARK = False
                FISH = False
                BOSS = False
            
            if event.type == GAME_END:

                # game over animation
                enemy = breakthrough_enemy.sprite
            
                # define variables

                animation_frame3 = 0
                end_running = True
                dt2 = 0
                centery1 = False
                centery2 = False
                back_up1 = False
                back_up2 = False
                charge = 0
        
                # death animation 

                while end_running:
                   
                    x = enemy.rect.left
                    y = enemy.rect.top
                    
                    if centery1 and centery2:
                        enemy.y_velocity = 0
                
                    elif y > (SCREEN_HEIGHT - enemy.height)//2 :
                        enemy.y_velocity = -200
                        centery1 = True
                    else: 
                        enemy.y_velocity = 200
                        centery2 = True

                    if back_up1 and back_up2:
                        # enemy is in position
                        if x > SCREEN_WIDTH//2:
                            charge += charge + 1
                            enemy.x_velocity = charge * -2
                        else:
                            enemy.x_velocity = 0
                            game_over = True

                    elif x < SCREEN_WIDTH*3//4:
                        enemy.x_velocity = 200
                        back_up1 = True
                    else: 
                        enemy.x_velocity = -200
                        back_up2 = True

                    # player runs
                    my_player.x_velocity = -100
                    my_player.y_velocity = -200

                    # bomb
                    bomb.x_velocity = 0
                    
                    if game_over:
                        end_running = False
                        breakthrough_enemy.empty()

                    update(enemy, dt2, animation_frame3, enemy.y_velocity, True)
                    update(my_player, dt2, animation_frame3, player.y_velocity)
                    update(bomb, dt2, 0, 0, True)
                    screen.blit(bg_image, bg_image_rect)
                    screen.blit(bomb.image, bomb.rect)
                    screen.blit(enemy.image, enemy.rect)
                    screen.blit(my_player.image, player.rect)
                    pygame.display.flip()

                    dt2 = clock.tick(FPS)/1000

                    animation_frame3 += 1
                    if animation_frame3 > 23:
                        animation_frame3 = 0
                
        if game_over:
            game_sounds['explosion'].play()
            return game_over_screen(screen, score)

        else:
            screen.blit(bg_image, bg_image_rect)
            
            # elements
            typed_text_surface = GAME_FONT.render(user_text, True, "white")
            score_text = str(score)
            if len(score_text) > 5:
                score_text = '{:.2e}'.format(score)
            score_surface = GAME_FONT.render(score_text, True, 'white')
            
            # scroll left
            if bg_scroll:
                scroll_frame += scroll_speed
            
            # updates
            
            for dead in deads:
                # updates all dead sharks
                if animation_frame% 4 == 0:
                    game_sounds['points'].play()    
                score += 2
                update(dead, dt, animation_frame, dead.y_velocity)

            for fish in fishes:
                # updates all fishes

                update(fish, dt, animation_frame2, do_not_orient = bg_scroll)
                
            for shark in sharks:
                # updates all sharks

                update(shark, dt, animation_frame, shark.y_velocity, do_not_orient = bg_scroll)
                shark.draw_word()

                if user_text.lower() == shark.word.lower():
                    # handles an event where a shark is killed
                    shark.image = shark.dead
                    shark.active = False
                    shark.hostile = False
                    shark.x_velocity = -150
                    shark.y_velocity = 400
                    Shark.sharks_dead += 1
                    user_text = ""

                    if score > 1000 and len(bosses) < 1 and randint(1,75) == 1:
                        pygame.event.post(pygame.event.Event(SPAWN_BOSS))

                    deads.add(shark)
                    sharks.remove(shark)
                
                if shark.rect.right < - 10:
                    breakthrough_enemy.add(shark)
                    pygame.event.post(pygame.event.Event(SCROLL))
                    
                
            for bubble in bubbles:
                # updates all bubbles

                update(bubble, dt, 0, randint(-100, -80))
            
            for boss in bosses:
                if len(entities) < 1:

                    update(megalodon, dt, animation_frame, y_velocity = boss.y_velocity, do_not_orient = boss.knockbacked)
                    boss.draw_word()

                if user_text.lower() == boss.word.lower():
                    user_text = ''
                    
                    # death handler
                    if boss.index == boss.life-1:
                        boss.x_velocity = -80
                        boss.y_velocity = 100
                        boss.image = boss.dead
                        boss.active = False
                        FISH = True
                        SHARK = True
                        deads.add(boss)
                    
                    else:
                        score += len(boss.word)*23
                        game_sounds['hit'].play()

                        # status triggers
                        if len(boss.word) > 5:
                            boss.knockbacked = True
                            boss.status_frame = boss.status_frames
                        
                        elif randint(1,10) != 1:
                            boss.stunned = True
                            boss.status_frame = boss.status_frames
                            
                        boss.index += 1
                        boss.update_word()
                    
                # status handlers
                if boss.knockbacked:
                    if boss.status_frame > 0:
                            boss.status_frame -= 1
                            boss.x_velocity = boss.status_frame*100
                    else:
                            boss.status_frame = boss.status_frames
                            boss.knockbacked = False
                            boss.x_velocity = boss.default_x_velocity

                if boss.stunned:
                    if boss.status_frame > 0:
                        if randint (1,4) == 3:
                            boss.status_frame -= 1
                        boss.x_velocity = 0
                    else:
                        boss.status_frame = boss.status_frames
                        boss.stunned = False
                        boss.x_velocity = boss.default_x_velocity

                # score on kill
                if not boss.active:
                    if animation_frame% 4 == 0:
                        game_sounds['points'].play()    
                    score += boss.life * 2

                if boss.rect.right < - 10:
                    breakthrough_enemy.add(boss)
                    pygame.event.post(pygame.event.Event(SCROLL))
            
            for player in players:
                update(player, dt, animation_frame, player.y_velocity)

            for bomb in bombs:
                update(bomb, dt, 0, 0)

            # screen blits

            bubbles.draw(screen)
            deads.draw(screen)
            bosses.draw(screen)
            fishes.draw(screen)    
            sharks.draw(screen)
            players.draw(screen)
            bombs.draw(screen)
            screen.blit(score_surface, score_surface.get_rect(center = (SCREEN_WIDTH*0.9, SCREEN_HEIGHT*0.9)))
            screen.blit(typed_text_surface,typed_text_surface.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT*0.9)))
            
            pygame.display.update()

            # counters
            animation_frame += 1
            animation_frame2 += 1

            if bg_scroll:
                bg_image_rect.move_ip(scroll_speed*dt, 0)
                # for player in players:
                #     player.rect.move_ip(scroll_speed*dt, 0)

            if animation_frame > 23:
                animation_frame = 0
            
            if animation_frame2 > 11:
                animation_frame2 = 0

            if bg_image_rect.left >= -10 and bg_scroll:
                bg_scroll = False
                pygame.event.post(pygame.event.Event(GAME_END))
                
            dt = clock.tick(FPS)/1000

def main_menu(screen = pygame.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT])):

    # create screen
    pygame.display.set_caption(TITLE)
    pygame.display.set_icon(pygame.image.load('logo.png'))

    # main_menu sprites
    button_sprite = load_sprites('shark', 8, (804//2, 350//2))
    bubble_img = pygame.image.load('bubble_1.png')
    main_menu_bg = pygame.image.load('main_menu_1.png')

    # music
    if MUSIC:
        main_menu_music = pygame.mixer.music
        main_menu_music.load('OurMusicBox - Chase That Comic.mp3')
        main_menu_music.play(-1)
    
    # controls
    controls_font = pygame.font.Font(None, SCREEN_HEIGHT//25)
    controls_heading = GAME_FONT.render('Controls', True, 'white')
    backspace_key = controls_font.render('Backspace — delete a character', True, 'white')
    del_key = controls_font.render('Del — delete all characters', True, 'white')

    # buttons
    play_button = Button('Play', button_sprite, (SCREEN_WIDTH*3//4, SCREEN_HEIGHT*3//5), main, screen)
    credits_button = Button('Credits', button_sprite, (SCREEN_WIDTH*3//4, SCREEN_HEIGHT*2//3 + 120), credits, screen)
   
    # initialize buttons
    Shark.draw_word(play_button)
    Shark.draw_word(credits_button)

    # create bubbles
    SPAWN_BUBBLES = pygame.USEREVENT + 3
    pygame.time.set_timer(SPAWN_BUBBLES, 500)

    # initialize variables
    user_text = ""
    update_buttons = False
    running = True
    animation_frame = 0
   

    while running:
        
        typed_text_surface = GAME_FONT.render(user_text, True, "white")

        for bubble in bubbles:
            update(bubble, dt, 0, randint(-100, -80))

        screen.blit(main_menu_bg, main_menu_bg.get_rect())
        bubbles.draw(screen)
        buttons.draw(screen)
        screen.blit(typed_text_surface, typed_text_surface.get_rect(x = SCREEN_WIDTH*0.05, y = SCREEN_HEIGHT * 0.9))
        screen.blit(controls_heading, controls_heading.get_rect(x = SCREEN_WIDTH*0.05, y = SCREEN_HEIGHT * 0.05))
        screen.blit(backspace_key, backspace_key.get_rect(x = SCREEN_WIDTH*0.05, y = SCREEN_HEIGHT * 0.12))
        screen.blit(del_key, del_key.get_rect(x = SCREEN_WIDTH*0.05, y = SCREEN_HEIGHT * 0.17))
        pygame.display.flip()

        dt = pygame.time.Clock().tick(30)/1000
        animation_frame += 1
        if animation_frame > 23:
            animation_frame = 0

        # poll for events in main menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  
                    user_text = user_text[:-1]
                elif event.key == pygame.K_DELETE:
                    user_text = ''
                else:
                    try:
                        code = (ord(event.unicode)) 
                    except:
                        continue
                    if code > 64 and code < 123:
                        user_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos() 
                rect = pygame.Surface((10,10)).get_rect(center=pos)
                for button in buttons:
                    if rect.colliderect(button.rect):
                        load_sounds('select').play()
                        button.x_velocity = -250
                        update_buttons = True

            if event.type == SPAWN_BUBBLES:
                bubble = pygame.sprite.Sprite(bubbles)
                bubble.x_velocity = randint(-100,100)
                bubble.active = True
                bubble.hostile = False
                bubble.image = bubble_img
                bubble.rect = bubble.image.get_rect(center = (randint(20, SCREEN_WIDTH-20), SCREEN_HEIGHT))
                bubble.sprites_right = [bubble_img]
                bubble.sprites_left = [bubble_img]
                bubble.add(entities)

        # user text things
        
        match user_text.lower():
            case 'hard':
                user_text = ''
                Shark.start_x_velocity = -250
                Boss.start_x_velocity = -150
            case 'music':
                user_text = ''
                if main_menu_music.get_busy():
                    main_menu_music.stop()
                else: 
                    main_menu_music.play()
        
        # update buttons
        for button in buttons:
            if user_text.lower() == button.word.lower():
                load_sounds('select').play()
                button.x_velocity = -250
                user_text = ""
                update_buttons = True

            if button.rect.right < 0:
                bubbles.empty()
                sharks.empty()
                buttons.empty()
                replay = True
                while replay:
                    nav_list = button.onclick()
                    # nav_list (main_menu, exit_game)
                    replay = nav_list[0]

                # reset values
                play_button = Button('Play', button_sprite, (SCREEN_WIDTH*3//4, SCREEN_HEIGHT*3//5), main, screen)
                credits_button = Button('Credits', button_sprite, (SCREEN_WIDTH*3//4, SCREEN_HEIGHT*2//3 + 120), credits, screen)
                Shark.draw_word(play_button)
                Shark.draw_word(credits_button)
                user_text = ""
                update_buttons = False
                running = True
                animation_frame = 0

                # exit the game?
                running = nav_list[1]
                
            if update_buttons:
                if button.x_velocity != 0:
                    update(button, dt, animation_frame)
                    Shark.draw_word(button)
        
    pygame.quit()
      
def credits(screen):
    # create bg
    background_img = pygame.image.load('bg_1.png').convert()
    credits_title_font = pygame.font.Font(None, SCREEN_HEIGHT//12)
    credits_subtitle_font = pygame.font.Font(None, SCREEN_HEIGHT//20)
    credits_text_font = pygame.font.Font(None, SCREEN_HEIGHT//25)
    header = credits_title_font.render('Credits', True, 'white')
    creator_title = credits_subtitle_font.render('Made by:', True, 'white')
    creator = credits_text_font.render('Eubert Lloyd Pineda', True, 'gray')
    words_title = credits_subtitle_font.render('Words', True, 'white')
    words = credits_text_font.render('https://python.sdv.univ-paris-diderot.fr/data-files/english-common-words.txt', True, 'gray')
    sprite_title = credits_subtitle_font.render('Sprites', True, 'white')
    sprites = credits_text_font.render('made with Ibis Paint X', True, 'gray')
    sound_title = credits_subtitle_font.render('Sound', True, 'white')
    sound =  credits_text_font.render('jsfxr', True, 'gray')
    music_title = credits_subtitle_font.render('Music', True, 'white')
    music1 =  credits_text_font.render('Music by Jay Man | OurMusicBox', True, 'gray')
    music2 =  credits_text_font.render('Website: www.our-music-box.com', True, 'gray')
    music3 =  credits_text_font.render('YouTube: www.youtube.com/c/ourmusicbox', True, 'gray')
    platform = credits_text_font.render('Code in Place 2024', True, 'white')

    button_sprite = load_sprites('shark', 8, (804//2, 350//2))
    back_button = Button('Back', button_sprite, (SCREEN_WIDTH*0.3, SCREEN_HEIGHT*2//3 + 120), main_menu, screen)
    
    Shark.draw_word(back_button)

    pygame.display.flip()

    user_text = ""
    update_buttons = False
    running = True
    animation_frame = 0

    while running:
        
        typed_text_surface = GAME_FONT.render(user_text, True, "white")

        screen.blit(background_img, background_img.get_rect())
        screen.blit(header, header.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.05 * SCREEN_HEIGHT))
        screen.blit(creator_title, creator_title.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.15 * SCREEN_HEIGHT))
        screen.blit(creator, creator.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.20 * SCREEN_HEIGHT))
        screen.blit(words_title, words_title.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.25 * SCREEN_HEIGHT))
        screen.blit(words, words.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.30 * SCREEN_HEIGHT))
        screen.blit(sprite_title, sprite_title.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.35 * SCREEN_HEIGHT))
        screen.blit(sprites, sprites.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.40 * SCREEN_HEIGHT))
        screen.blit(sound_title, sound_title.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.45 * SCREEN_HEIGHT))
        screen.blit(sound, sound.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.50 * SCREEN_HEIGHT))
        screen.blit(music_title, music_title.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.55 * SCREEN_HEIGHT))
        screen.blit(music1, music1.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.60 * SCREEN_HEIGHT))
        screen.blit(music2, music2.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.64 * SCREEN_HEIGHT))
        screen.blit(music3, music3.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.68 * SCREEN_HEIGHT))
        screen.blit(platform, platform.get_rect(x = 0.75 * SCREEN_WIDTH, y = 0.90 * SCREEN_HEIGHT))
        screen.blit(typed_text_surface, typed_text_surface.get_rect(right = 0.95 * SCREEN_WIDTH, y = 0.05 * SCREEN_HEIGHT))
        buttons.draw(screen)
        pygame.display.flip()

        dt = pygame.time.Clock().tick(30)/1000

        animation_frame += 1
        if animation_frame > 23:
            animation_frame = 0

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return [False, False]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  
                    user_text = user_text[:-1]
                elif event.key == pygame.K_DELETE:
                    user_text = ''
                else:
                    try:
                        code = (ord(event.unicode)) 
                    except:
                        continue
                    if code > 64 and code < 123:
                        user_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos() 
                rect = pygame.Surface((10,10)).get_rect(center=pos)
                if rect.colliderect(words.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.30 * SCREEN_HEIGHT)):
                    open_link('https://python.sdv.univ-paris-diderot.fr/data-files/english-common-words.txt', 2)
                if rect.colliderect(music2.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.64 * SCREEN_HEIGHT)):
                    open_link('https://www.our-music-box.com', 2)
                if rect.colliderect(music3.get_rect(x = 0.05 * SCREEN_WIDTH, y = 0.68 * SCREEN_HEIGHT)):
                    open_link('https://www.youtube.com/c/ourmusicbox', 2)
                
                else:
                    for button in buttons:
                        if rect.colliderect(button.rect):
                            load_sounds('select').play()
                            button.x_velocity = -250
                            update_buttons = True

        for button in buttons:
            if user_text.lower() == button.word.lower():
                load_sounds('select').play()
                button.x_velocity = -250
                user_text = ""
                update_buttons = True

            if button.rect.right < 0:

                buttons.empty()
                bubbles.empty()
                return [False, True]
                
               
            if update_buttons:
                if button.x_velocity != 0:
                    update(button, dt, animation_frame)
                    Shark.draw_word(button)

def game_over_screen(screen, score):
    
    # game over screen
    background_img = pygame.image.load('game_over_1.png').convert()
    button_sprite = load_sprites('shark', 8, (804//2, 350//2))      
    replay_button = Button('Play again', button_sprite, (SCREEN_WIDTH*0.55, SCREEN_HEIGHT*0.6), return_args, [True, True])
    back_button = Button('Main Menu', button_sprite, (SCREEN_WIDTH*0.55, SCREEN_HEIGHT*0.85), return_args, [False, True])
    Shark.draw_word(replay_button)
    Shark.draw_word(back_button)

    user_text = ""
    update_buttons = False
    running = True
    animation_frame = 0

    while True:
        game_over_title = GAME_FONT.render('GAME OVER', True, 'white')
        score_text = GAME_FONT.render('SCORE: ' + str(score), True, 'white')

        screen.blit(background_img, background_img.get_rect())
        screen.blit(game_over_title, game_over_title.get_rect(center = (SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.3)))
        screen.blit(score_text, score_text.get_rect(center = (SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.4)))
        buttons.draw(screen)
        
        pygame.display.flip()

        dt = pygame.time.Clock().tick(30)/1000

        animation_frame += 1
        if animation_frame > 23:
            animation_frame = 0

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return [False, False]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:  
                    user_text = user_text[:-1]
                elif event.key == pygame.K_DELETE:
                    user_text = ''
                else:
                    try:
                        code = (ord(event.unicode)) 
                    except:
                        continue
                    if code > 64 and code < 123:
                        user_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos() 
                rect = pygame.Surface((10,10)).get_rect(center=pos)
               
                for button in buttons:
                    if rect.colliderect(button.rect):
                        load_sounds('select').play()
                        button.x_velocity = -250
                        update_buttons = True

        for button in buttons:
            if user_text.lower() == button.word.lower():
                load_sounds('select').play()
                button.x_velocity = -250
                user_text = ""
                update_buttons = True

            if button.rect.right < 0:

                buttons.empty()
                bubbles.empty()
                return [False, True]
                
            
            if update_buttons:
                if button.x_velocity != 0:
                    update(button, dt, animation_frame)
                    Shark.draw_word(button)



if __name__=='__main__':
    main_menu()
   
   
