# Modelos para as simulações

# imports:
import pygame
from pygame.locals import *
import random, time, copy

# Classes:

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def current(self):
        return (self.x, self.y)

# class Block:
#     ''' Bloco '''

#     def __init__(self):
#         self.image = pygame.image.load("imgs/peça_pequena_metalica.png")
#         self.position = Position(80,245)
#         self.tipo = 0
#         self.on_screen = True


#     def update_pos(self, velocidade):
#         if self.position.x < SCREEN_SIZE[0] and self.position.y < SCREEN_SIZE[1]:
#             self.position = self.position + velocidade
#         else:
#             self.on_screen = False

#     def update_screen(self, scrn):
#         scrn.blit(self.image, self.position.current())  

#     def remove_from_screen(self):
#         self.on_screen = False



class Piston:
    '''
    modos: spring_return_+; spring_return_-; 
    '''
    def __init__(self, p: Position):
        self.image_body = pygame.image.load("imgs/piston_body.png")
        self.image_embolo = pygame.image.load("imgs/piston_embolo.png")
        self.image_background = pygame.image.load("imgs/piston_bg.png")
        self.position = p #Posição do backgound (Referência)
        self.position_embolo = self.position + Position(95, 50) #Posição do embolo
        self.position_body = self.position + Position(45, 25)
        self.min = True #Indica fim de curso
        self.max = False #Indica fim de curso
        self.dx_max_embolo = 10 
        self.velocidade = Position(-5,0)

    def update_pos(self):
        self.position_embolo = self.position_embolo + self.velocidade

        if self.position_embolo.x <= (self.position.x + 95): 
            self.position_embolo.x = self.position.x + 95
            self.min = True    
        elif self.position_embolo.x >= (self.position.x + 245):
            self.position_embolo.x = self.position.x + 245
            self.max = True
        else:
            self.min = False
            self.max = False

    def activate_fwd(self):
        self.velocidade = Position(15,0)

    def activate_bwd(self):
        self.velocidade = Position(-15,0)

    def activate_spring_return_back(self):
        self.velocidade = Position(-7, 0)
            
    def activate_spring_return_forward(self):
        self.velocidade = Position(7,0)

    def update_screen(self,scrn):
        scrn.blit(self.image_background, self.position.current())
        scrn.blit(self.image_embolo, self.position_embolo.current())
        scrn.blit(self.image_body, self.position_body.current())
      
class Esteira:
    def __init__(self, orientation, direction, region_coords, key):
        '''
        orientation = 'v' ou 'h'
        direction = '+' ou '-'
        region = (x1,y1,x2,y2)
        key
        '''

        self.region = Region(region_coords[0], region_coords[1], region_coords[2], region_coords[3],
                            key,'l')
        self.pos = (140,235)
        self.blocks = []
        self.velocidade = Position(0,0)
        self.orientation = orientation
        self.velocidades = [10, 10, 9, 9, 8, 6, 5, 3, 2, 1, 1, 0]
        
        if direction == '-':
            self.direction = -1
        else:
            self.direction = 1 

        if orientation == 'h':
            self.velocidade_liga = Position(10,0)
            self.image = pygame.image.load("imgs/esteira.png")

        elif orientation == 'v':
            self.velocidade_liga = Position(0,10)
            if direction == '-':
                self.velocidade_liga = Position(0,-10)

            self.image = pygame.image.load("imgs/esteira_v.png")

            
    def update_peso(self):
        if self.orientation == 'h':
            self.velocidade.x = self.direction * self.velocidades[len(self.blocks)]
        else:
            self.velocidade.y = self.direction * self.velocidades[len(self.blocks)]
 
    def liga_esteira(self):
        self.velocidade = copy.deepcopy(self.velocidade_liga)
    
    def novo_bloco(self, blk):
        self.blocks.append(blk)
        self.update_peso()
        
    def remove_bloco(self, blk):
        self.blocks.remove(blk) #metodo da lista
        self.update_peso()

    def update_conveyor_screen(self, screen):
        screen.blit(self.image, self.pos)

    # Defasada. transferida pra classe Block 
    def update_blocks_screen(self):
        for blk in self.blocks:
            if not blk.on_screen:
                self.blocks.remove(blk)
                self.update_peso()
                pass
            
            blk.update_screen()

    # Defasada. transferida pra classe Block        
    def update_blocks_position(self):
        for blk in self.blocks:
            blk.update_pos(self.velocidade)

class Sinkhole:
    def __init__(self, boundaries, position: Position, key):
        '''
        definir a imagem após instanciar

        boundaries: (x1, y1, x2, y2)

        position: posição para colocar a imagem

        key: nome

        '''
        
        # definir de forma rudimentar quando instanciar um objeto
        self.image = 0

        self.boundaries = Region(boundaries[0],boundaries[2],boundaries[1],boundaries[3], key, 'l')
        self.position = position
        self.blocks = []
        self.velocidade = Position(0,0) # Caso precise.
        self.key = key

    def update_screen(self, screen):
        screen.blit(self.image, self.position.current())

    def swallow(self, blk):
        self.blocks.append(blk)
        print(self.key, ' engoliu o bloco ', blk.id, '. Yummy!')
        #for bk in self.blocks:
            #print(self.boundaries.key, '=>' , 'Bloco: ', bk.id, ' | Tipo: ', bk.tamanho, ' | Material: ', bk.material )
            #pass
    
    def remove_bloco(self, blk):
        self.blocks.append(blk) #metodo da lista
        for bk in self.blocks:
            print(self.boundaries.key, '=>' , 'Bloco: ', bk.id, ' | Tipo: ', bk.tamanho, ' | Material: ', bk.material ) 

class Boundary:
    def __init__(self, pos: Position, width, heigth):
        self.x_start = pos.x
        self.x_end = pos.x + width
        self.y_start = pos.y
        self.y_end = pos.y + heigth

class Line_Boundary:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
        # y = ax + b
        if abs(x1 - x2) < 0.001:
            self.a = 0
        else:
            self.a = (y1 - y2) / (x1 - x2)
        
        self.b = y1 - self.a * self. x1
    
    def getY(self, x):
        return self.a * x + self.b

    def getX(self, y):
        if (self.a == 0) :
            return self.x1
        else:
            return (y - self.b) / self.a

class Sensor:
    def __init__(self, x_pos, y_pos, x1, y1, x2, y2 , tipo, tamanho):
        ''''
        tipo:    ''m'' ou ''n'' ou ''x'' '
        tamanho: ''p'' ou ''g'' ou ''x''
        '''
        self.image_activated = pygame.image.load("imgs/sensor_active.png") 
        self.image_deactivated = pygame.image.load("imgs/sensor_inactive.png") 
        self.line = Line_Boundary(x1, y1, x2, y2)
        self.position = Position(x_pos, y_pos)
        self.status = False
        self.material = tipo
        self.tamanho = tamanho

    def check(self):
        for blk in Block.blocks:
            # Check material
            if (blk.boundaries.doTouchLine(self.line) and blk.material == self.material):
                self.status = True
            # Check size
            elif (blk.boundaries.doTouchLine(self.line) and blk.tamanho == self.tamanho):
                self.status = True
            else:
                self.status = False

    def update_screen(self):
        
        self.check()

        if self.status:
            screen.blit(self.image_activated, self.position.current())
        else: 
            screen.blit(self.image_deactivated, self.position.current()) 

class Region:
    regions = {}

    def __init__(self, x_start, x_end, y_start, y_end, key, tipo):
        '''
         __init__(self, x_start, x_end, y_start, y_end)
        key: name of region
        tipo: 'b' - block; 'w' - parede; 'l' - local, como contador ou saída ou gerador
        '''
        self.key = key
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        Region.regions.update({key : self})
        self.tipo = tipo

    def doOverlap(self, other):  
    # If one rectangle is on left side of other 
        if(self.x_start > other.x_end or other.x_start > self.x_end): 
            return False
    # If one rectangle is above other 
        if(self.y_start > other.y_end or other.y_start > self.y_end): 
            return False
  
        return True

    def doTouchLine(self, line: Line_Boundary):
        
        # Faces horizontais
        x_test = line.getX(self.y_start)
        if (x_test > self.x_start and x_test < self.x_end):
            return True
        
        x_test = line.getX(self.y_end)
        if (x_test > self.x_start and x_test < self.x_end):
            return True

        return False

class Barrier:
    id_count = 100

    def __init__(self, x , y, x1, y1, x2, y2, key, orientation_activation):
        '''
        x, y = pivot point;
        orientation_activation: 'up', 'down' a partir do pivot;
        x1 y1 x2 y2 pontos da barreira
        key: nome para a regiao
        '''
        self.id = Barrier.id_count
        Barrier.id_count +=1
        self.key = key
        # Posição
        self.position = Position(x, y)
        
        # Imagens
        self.image = pygame.image.load("imgs/door_h.png")
        
        if orientation_activation == 'up':
            self.image_activated = pygame.image.load("imgs/door_tilt_up.png") 
            self.position_activated = Position(x, y-48)
        elif orientation_activation == 'down':
            self.image_activated = pygame.image.load("imgs/door_tilt_down.png") 
            self.position_activated = self.position
        else:
            self.image_h = pygame.image.load("imgs/door_h.png")
    
        # true = activated; false = deactivated
        self.status = False

        # Barreira:
        self.boundary = Line_Boundary(x1-10, y1, x2-10,  y2)

        self.region = Region(x1, x2, y1, y2, self.key, 'p')

    def update_screen(self):
        if self.status:
            screen.blit(self.image_activated, self.position_activated.current())
        else:
            screen.blit(self.image, self.position.current())

    def activate(self):
        self.status = True
    
    def deactivate(self):
        self.status = False

    def toggle(self):
        self.status = not self.status


# Funções avulso
# O nome diz tudo: Essas cores serão usadas nos indicadores.
def extrair_porta_para_cor(dt):
    out = []
    for i in [1, 2, 4, 8, 16, 32]:
        if (dt & i)>0 :
            out.append((0,255,0))
        else: 
            out.append((20,20,20))

    return out

def extrair_porta_para_lista(dt):
    out = []
    ports_char = [1, 2, 4, 8, 16, 32]
    for i in ports_char:
        if (dt & i)>0 :
            out.append(1)
        else: 
            out.append(0)

    return out

    