'''

TESTE 13 - INTEGRAR COM O SIMULADOR - 
satisfatório para entrega!

tENTATIVA DE ADIÇÃO DA INTERFACE
'''

'''
CONTROLES:

ESPAÇO - GERA UMA NOVA PEÇA
R - remove blocos

1 2 - Acionam as portas 1 e 2

del - reseta a contagem e remove todos os blocos

'''
import sys, os
import pygame
import random, time, math, copy, sys
import my_serialduino_protocol as mp
from pygame.locals import *
import threading
from simulation_models import extrair_porta_para_lista

def res_path(relative_path):
    try:
        base_path = sys._METPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)


# Variáveis da simulação e da janela
SIMULATION_TICKS = 10 
SCREEN_SIZE = (650, 600)

# Limites:
LIMIT_DESVIO_X_1 = 0
LIMIT_DESVIO_X_2 = 0
LIMIT_CONTAGEM_Y_1 = 0
LIMIT_CONTAGEM_Y_2 = 0
LIMIT_FINAL_X = 0

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __mul__(self, other):
        return Position(other * self.x, other * self.y)

    def current(self):
        return (self.x, self.y)

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
        self.image_activated = pygame.image.load(res_path("imgs/sensor_active.png")) 
        self.image_deactivated = pygame.image.load(res_path("imgs/sensor_inactive.png")) 
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
        self.image = pygame.image.load(res_path("imgs/door_h.png"))
        
        if orientation_activation == 'up':
            self.image_activated = pygame.image.load(res_path("imgs/door_tilt_up.png")) 
            self.position_activated = Position(x, y-48)
        elif orientation_activation == 'down':
            self.image_activated = pygame.image.load(res_path("imgs/door_tilt_down.png")) 
            self.position_activated = self.position
        else:
            self.image_h = pygame.image.loadres_path(("imgs/door_h.png"))
    
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

class Block:
    ''' Classe dos blocos '''
    idcount = 0
    blocks = []
    block_images = [res_path("imgs/peça_metalica.png"),
                    res_path("imgs/peça_n_metalica.png"),
                    res_path("imgs/peça_pequena_metalica.png"),
                    res_path("imgs/peça_pequena_n_metalica.png")]
    type_count = [0,0,0,0]
    materials = ['m','n','m','n']
    tamanhos  = ['g','g','p','p']
    ponto_de_inicio = [(80,245), (80,245), (80,255), (80,255)]
    widths = [50, 50, 30, 30]

    def __init__(self, recipient):
        # A qual objeto ele estará vinculado
        self.recipient = recipient
        recipient.novo_bloco(self)
        
        k = random.randint(0,3) 
        # Randomizar a peça
        Block.type_count[k] += 1
        self.image = pygame.image.load(Block.block_images[k])
        self.material = Block.materials[k]
        self.tamanho = Block.tamanhos[k]
        self.tipo = 1
        # Contagem dos blocos da simulação
        Block.idcount += 1
        self.id = Block.idcount
        
        # De acordo com a peça, pegar o tamanho do bloco
        self.block_width = Block.widths[k]

        self.position = Position(Block.ponto_de_inicio[k][0], Block.ponto_de_inicio[k][1])
        
        self.boundaries = Region(self.position.x, 
                                 self.position.x + self.block_width,
                                 self.position.y,
                                 self.position.y + self.block_width,
                                 self.id,
                                 'b')
        
    

        # define em que região da simulação ela está.
        self.region_id = 0

        self.on_screen = True

        self.inside_limits = []

    
    def update_pos(self, y):
        
        #
        # ###############################################################
        # ###############################################################
        #   

        #O que eu quero? determinar a próxima posição dependendo de onde ele está agora

        velocidade = self.recipient.velocidade

        #print('Posicao do bloco:', self.position.current())
        if not self.on_screen:
            return

        self.inside_limits = self.check_limits()
        #print(self.inside_limits)
        for i in self.inside_limits:
            #print('Regiao que esta em contato: ', i, '(', Region.regions[i].x_start, Region.regions[i].y_start, Region.regions[i].x_end, Region.regions[i].y_end, ')')

            if i == 'porta1' and porta1.status:
                if porta1.status and self.boundaries.doTouchLine(porta1.boundary):
                    velocidade = Position(round(math.sqrt(velocidade.x**2 +velocidade.y**2) * 0.7) , 
                                      round(math.sqrt(velocidade.x**2 +velocidade.y**2) * 0.7))
            
            elif i == 'porta2' and porta2.status:
                if porta2.status and self.boundaries.doTouchLine(porta2.boundary):
                    velocidade = Position(round(math.sqrt(velocidade.x**2 +velocidade.y**2) * 0.7) , 
                                      -round(math.sqrt(velocidade.x**2 +velocidade.y**2) * 0.7))
            
            elif i == 'esteira1':
                self.recipient.blocks.remove(self)
                self.recipient = esteira_vert_1
                self.recipient.novo_bloco(self)

            elif i == 'esteira2':
                self.recipient.blocks.remove(self)
                self.recipient = esteira_vert_2
                self.recipient.novo_bloco(self)  
                        
            elif i == 'esteira0':
                #print('na esteira 0')
                pass

            elif i == 'saida':
                #self.recipient.remove_bloco(self)
                self.on_screen = False
                self.recipient.blocks.remove(self)
                saida.swallow(self)
                #print(saida.blocks)

            elif i == 'contador2':
                self.on_screen = False
                self.recipient.blocks.remove(self)
                contagem_2.swallow(self)


            elif i == 'contador1':
                self.on_screen = False
                self.recipient.blocks.remove(self)
                contagem_1.swallow(self)

        
            elif i == 'c':
                pass     
            # 
            # terminar de escrever!
            #       
            else:
                pass  
        

        if self.position.x < SCREEN_SIZE[0] and self.position.y < SCREEN_SIZE[1]:
            self.position = self.position + velocidade
        else:
            self.on_screen = False

        # Atualizar os limites
        self.boundaries.x_start = self.position.x 
        self.boundaries.x_end =  self.position.x + self.block_width
        self.boundaries.y_start =  self.position.y
        self.boundaries.y_end = self.position.y + self.block_width
        

        #
        # ###############################################################
        # ###############################################################
        #

    def update_screen(self):
        screen.blit(self.image, self.position.current())  

    def remove_from_screen(self):
        self.on_screen = False
        self.recipient.remove_bloco(self)
    
    def check_limits(self):
        '''
        scan todas as regiões em Region.regions

        retorna uma lista das regões que ele toca
        '''
        #print("Check limits")
        ls = []
        for k, reg in Region.regions.items():
            if self.boundaries.doOverlap(reg):
                    ls.append(k)


        return ls
                
    def add_to_recipient(self, recipient):
        recipient.novo_bloco(self,self)
    
    @classmethod
    def new_block(cls, recipient):
        Block.blocks.append(Block(recipient))

    @classmethod
    def update_blocks_screen(cls):
        for blk in cls.blocks:
            if not blk.on_screen:
                cls.blocks.remove(blk)
                blk.recipient.update_peso()
                pass
            
            blk.update_screen()

    @classmethod
    def update_blocks_position(cls):
        for blk in cls.blocks:
            blk.update_pos(blk.recipient.velocidade)

    @classmethod
    def reset_all(self):
        Block.blocks = []
        Block.type_count = [0,0,0,0]
        Block.idcount = 0

class Esteira:
    esteiras = []
    def __init__(self, orientation, direction, region_coords, key):
        '''
        orientation = 'v' ou 'h'
        direction = '+' ou '-'
        region = (x1,y1,x2,y2)
        key
        '''
        Esteira.esteiras.append(self)

        self.region = Region(region_coords[0], region_coords[1], region_coords[2], region_coords[3],
                            key,'l')
        self.pos = (140,235)
        self.blocks = []
        self.velocidade = Position(0,0)
        self.orientation = orientation
        self.velocidades = [10, 10, 10, 10, 10, 10, 10, 3, 2, 1, 1, 0] 
        #[10, 10, 9, 9, 8, 6, 5, 3, 2, 1, 1, 0]
        
        if direction == '-':
            self.direction = -1
        else:
            self.direction = 1 

        if orientation == 'h':
            self.velocidade_liga = Position(10,0)
            self.image = pygame.image.load(res_path("imgs/esteira.png"))

        elif orientation == 'v':
            self.velocidade_liga = Position(0,10)
            if direction == '-':
                self.velocidade_liga = Position(0,-10)

            self.image = pygame.image.load(res_path("imgs/esteira_v.png"))

            
    @classmethod
    def update_peso(cls):
        for est in [Esteira.esteiras[0]]:
            if len(est.blocks) < len(est.velocidades):
                if est.orientation == 'h':
                    est.velocidade.x = est.direction * est.velocidades[len(est.blocks)]
                else:
                    est.velocidade.y = est.direction * est.velocidades[len(est.blocks)]
            else:
                if est.orientation == 'h':
                    est.velocidade.x = est.direction * est.velocidades[-1]
                else:
                    est.velocidade.y = est.direction * est.velocidades[-1]

                

    def liga_esteira(self):
        self.velocidade = copy.deepcopy(self.velocidade_liga)
    
    def novo_bloco(self, blk):
        self.blocks.append(blk)
        self.update_peso()
        
    def remove_bloco(self, blk):
        '''
            ajustar
        '''
        #self.blocks.remove(blk) #metodo da lista
        #self.update_peso()

    def update_conveyor_screen(self):
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

    @classmethod 
    def reset_all(cls):
        for est in cls.esteiras:
            est.blocks = []

class Sinkhole:
    sinkholes = []
    def __init__(self, boundaries, position: Position, key):
        '''
        definir a imagem após instanciar

        boundaries: (x1, y1, x2, y2)

        position: posição para colocar a imagem

        key: nome

        '''
        
        # definir de forma rudimentar quando instanciar um objeto
        self.image = 0
        Sinkhole.sinkholes.append(self)
        self.boundaries = Region(boundaries[0],boundaries[2],boundaries[1],boundaries[3], key, 'l')
        self.position = position
        self.blocks = []
        self.velocidade = Position(0,0) # Caso precise.
        self.key = key

    def update_screen(self):
        screen.blit(self.image, self.position.current())

    def swallow(self, blk: Block):
        self.blocks.append(blk)
        print(self.key, ' engoliu o bloco ', blk.id, '. Yummy!')
        #for bk in self.blocks:
            #print(self.boundaries.key, '=>' , 'Bloco: ', bk.id, ' | Tipo: ', bk.tamanho, ' | Material: ', bk.material )
            #pass
    
    def remove_bloco(self, blk: Block):
        self.blocks.append(blk) #metodo da lista
        for bk in self.blocks:
            #print(self.boundaries.key, '=>' , 'Bloco: ', bk.id, ' | Tipo: ', bk.tamanho, ' | Material: ', bk.material )
            pass
    @classmethod 
    def reset_all(cls):
        for snk in cls.sinkholes:
            snk.blocks = []

#definir um evento que será lançado quando uma porta mudar
#tipo_do_evento = pygame.event.custom_type()
evento_porta = pygame.event.Event(USEREVENT)
USEREVENT2 = USEREVENT + 1 
evento_porta_auxiliar = pygame.event.Event(USEREVENT2)

# Variavel que salva a ultima entrada
last_input = 0 
to_auxiliary_output = 0
to_output = 0

PORTA_COM = input('Qual a porta COM na qual a interface está conectada? (digite COM6 por exemplo)')


run_simulation = True 

# Definir a thread da comunicação
def conversa(running_simulation):
    
    global last_input
    global to_auxiliary_output
    global to_output

    comm = mp.My_protocol(PORTA_COM, pygame)
    
    comm.open_port()
    time.sleep(1)
    comm.start_commmunication()
    
    last_input = comm.read_inputs()
    last_auxiliary_input = comm.read_auxiliary_inputs()

    while(True):
        # Solicita leitura:
        x = comm.read_inputs()
        y = comm.read_auxiliary_inputs()

        # Aplica leitura à saída:
        
        comm.set_outputs(to_output)
        comm.set_auxiliary_outputs(to_auxiliary_output)

        if (x != last_input):
            last_input = x

            # Lança o evento
            #print('Evento lançado!', ' | last_input= ', last_input)
            pygame.event.post(evento_porta)

        if(y != last_auxiliary_input):
            last_auxiliary_input = y
            # Lança o evento
            #print('Evento lançado!', ' | last_input= ', last_input)
            pygame.event.post(evento_porta_auxiliar)
        
        if not running_simulation():
            comm.termina()
            comm.close_port()
            break

        # 1 ms
        #time.sleep(0.001)

# Lançar a thread
t2 = threading.Thread(target=conversa, args=(lambda : run_simulation, ))
t2.start()


time.sleep(4)


#minha_linha = Line_Boundary(295,226,350,287)
#minha_linha_2 = Line_Boundary()

sensor_indutivo = Sensor(190,232,190,232,190,20, 'm', 'x')
sensor_optico = Sensor(205,232,205,232,205,20, 'x', 'g')
sensor_capacitivo = Sensor(175,232,175,232,175,20,'n','x')

#induction_sensor_line = Line_Boundary(190,232,190,20) 
#optical_sensor_line = Line_Boundary(190,0,190,0)


# regions = {
#     'esteira0' : Region(140, 585, 235, 310,'esteira0', 'l' ), # Esteira
#     'gerador'  : Region( 50, 215, 235, 310,'gerador', 'l'),# Saída do gerador
#     'saida'    : Region(630, 650, 235, 310,'saida','l') , # Remover peça do jogo
#     'porta1'   : Region(320, 352, 235, 285,'porta1','p'), # Região da primeira porta
#     'porta2'   : Region(470, 535, 255, 310,'porta2','p'), # Região da segunda porta
#     'contagem1': Region(450, 515,  90, 130,'contagem1','l'), # Contagem 1
#     'contagem2': Region(300, 375, 445, 475,'contagem2','l'), # Contagem 2
#     'esteira1' : Region(300, 370, 310, 410,'esteira1', 'l'), # EsteiraVertical de baixo
#     'esteira2' : Region(450, 520, 135, 235,'esteira2','l')  # EsteiraVertical de baixo
#     }

### VARIAVEIS:
UP      = 0
RIGHT   = 1 
DOWN    = 2
LEFT    = 3

# Iniciar pygame
pygame.init()




# ajustar o tamanho da tela
screen = pygame.display.set_mode(SCREEN_SIZE)

# colocar titulo
pygame.display.set_caption('Interface HIL - Planta para classificação de Peças')
icon = pygame.image.load(res_path("imgs/icon.png"))
pygame.display.set_icon(icon)

# instanciar pygame.time.Clock()
clock = pygame.time.Clock()

#definir um evento que será lançado quando uma porta mudar
#tipo_do_evento = pygame.event.custom_type()
evento_porta = pygame.event.Event(pygame.USEREVENT)
USEREVENT2 = pygame.USEREVENT + 1 
evento_porta_auxiliar = pygame.event.Event(USEREVENT2)

# carregar as imagens:

# Imagem do gerador de peças
gerador = pygame.image.load(res_path("imgs/gerador.png"))
gerador_pos = (50, 190)

# Imagem da saída de peças
saida = pygame.image.load(res_path("imgs/saida.png"))
saida_pos = (585,200)

porta1 = pygame.image.load(res_path("imgs/door_h.png"))
porta1_pos = (0,0)

my_direction = 5
position = (0, 0)
step = 5

img = pygame.image.load(res_path("imgs/door_h.png"))
img2 = pygame.image.load(res_path("imgs/peça_pequena_metalica.png"))

# Instanciar as esteiras:

# Esteira horizontal:
esteira = Esteira('h', '+',(140, 585, 235, 310), 'esteira0')
esteira.liga_esteira()

# Esteira vertical: fazer os ajustes necessários
esteira_vert_2 = Esteira('v', '-',(300, 370, 310, 410),'esteira1')
esteira_vert_2.pos = (450,125)
esteira_vert_2.liga_esteira()

esteira_vert_1 = Esteira('v', '+',(450, 520, 135, 235),'esteira2')
esteira_vert_1.pos = (300,305) 
esteira_vert_1.liga_esteira()

saida = Sinkhole((603, 201, 647, 340), Position(585,200) ,'saida')
saida.image = pygame.image.load(res_path("imgs/saida.png"))

contagem_1 = Sinkhole((290,440,380,470), Position(275,410), 'contador1')
contagem_1.image = pygame.image.load(res_path("imgs/contador_up.png"))

contagem_2 = Sinkhole((420,60,544,90), Position(425, 60), 'contador2')
contagem_2.image = pygame.image.load(res_path("imgs/contador_down.png"))

#regiao_teste = Region(456,514,156,184,'teste','l')

#Barrier()

# Instanciar as Portas
porta1 = Barrier(275, 210, 295, 226, 350, 287, 'porta1',  "down")
porta2 = Barrier(430, 300, 450, 226, 510, 287, 'porta2',  "up")

velocidade = Position(10, 0)

##
#Objetos para mostrar na contagem:
bgm_cor = 0
bgm_ger = 0

bpm_cor = 0
bpm_ger = 0

bgn_cor = 0
bgn_ger = 0

bpn_cor = 0
bpn_ger = 0

#fonte dos textos
BLUE = pygame.Color('dodgerblue1')
MY_NAME_COLOR = pygame.Color('darkgrey')
MY_NAME_FONT = pygame.font.Font(None, 18)
MY_NAME_TEXT = 'Programa elaborado por RENAN P I L SANDES para o Trabalho de Conclusão de Curso de Eng. Eletrônica 2020.1' 
FONT = pygame.font.Font(None, 20)
background_img = pygame.image.load(res_path("imgs/background-block-counting.png"))
title_img = pygame.image.load(res_path("imgs/titulo-label.png"))
interface_hil_label = pygame.image.load(res_path("imgs/interface-hil-label.png"))
ufs_del_label = pygame.image.load(res_path("imgs/ufs-del-label.png"))

ELEMENTS_LABELS_COLOR = pygame.Color('red')
ELEMENTS_LABELS_FONT = pygame.font.Font(None, 18)

my_name_render = MY_NAME_FONT.render(MY_NAME_TEXT,True, MY_NAME_COLOR)
screen.blit(my_name_render, (0, 580))

def render_texts():
    
    x0 = 5
    y0 = 495

    screen.blit(interface_hil_label, (0,0))
    screen.blit(title_img, (200, 0))
    screen.blit(ufs_del_label, (480 ,485))
    screen.blit(background_img, (x0-5, y0-10))
    text_img1 = FONT.render('  Contagem dos blocos nas esteiras: {}'.format(len(Block.blocks)),True, BLUE)
    screen.blit(text_img1, (5 + x0 ,0 + y0))
    screen.blit(my_name_render, (0, 583))
    bgm_ger = Block.type_count[0]
    bpm_ger = Block.type_count[2]
    bgn_ger = Block.type_count[1]
    bpn_ger = Block.type_count[3]

    #
    k = 0
    for blk in contagem_2.blocks:
        if blk.material == 'm' and blk.tamanho == 'g':
            k = k+1 

    bgm_cor = k
    
    #
    k = 0
    for blk in contagem_1.blocks:
        if blk.material == 'm' and blk.tamanho == 'p':
            k = k+1 
    
    bpm_cor = k

    #
    k = 0
    for blk in contagem_1.blocks:
        if blk.material == 'n' and blk.tamanho == 'g':
            k = k+1 
    
    bgn_cor = k
    
    # Contar os blocos pequenos não metálicos contados na saída
    k = 0
    for blk in saida.blocks:
        if blk.material == 'n' and blk.tamanho == 'p':
            k = k+1 
    
    bpn_cor = k
    #print(bpn_cor, saida.blocks)
    
    text_img2 = FONT.render('     B. met. grn => gerados: {} | redirec. p/ contagem: {} '.format(bgm_ger,bgm_cor),True, BLUE)
    screen.blit(text_img2, (5+x0, 15+y0))

    text_img3 = FONT.render('     B. met. peq => gerados: {} | redirec. p/ contagem: {} '.format(bpm_ger, bpm_cor),True, BLUE)
    screen.blit(text_img3, (5+x0,30+y0))

    text_img4 = FONT.render('     B. não met. grn => gerados: {} | redirec. p/ contagem: {} '.format(bgn_ger, bgn_cor),True, BLUE)
    screen.blit(text_img4, (5+x0,45+y0))

    text_img5 = FONT.render('     B. não met. peq => gerados: {} | redirec. p/ contagem: {} '.format(bpn_ger, bpn_cor),True, BLUE)
    screen.blit(text_img5, (5+x0,60+y0))

    # sensores e elementos da tela
    cap_label = ELEMENTS_LABELS_FONT.render('c', True, ELEMENTS_LABELS_COLOR)
    screen.blit(cap_label, (177,329))
    ind_label = ELEMENTS_LABELS_FONT.render('i', True, ELEMENTS_LABELS_COLOR)
    screen.blit(ind_label, (192,329))
    opt_label = ELEMENTS_LABELS_FONT.render('o', True, ELEMENTS_LABELS_COLOR)
    screen.blit(opt_label, (207,329))

#
#
#
#
#
#
#
#
#
#
#

var_aux_pode_ger_blk = True 
# Início do laço do jogo!


while(run_simulation):
    #determina o fps?
    clock.tick(SIMULATION_TICKS)
    
    # Scan dos eventos que estão para serem handled
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_simulation = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Mouse click:", pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                my_direction = UP
            elif event.key == pygame.K_LEFT:
                my_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                my_direction = RIGHT
            elif event.key == pygame.K_DOWN:
                my_direction = DOWN
            elif event.key == pygame.K_SPACE:
                Block.new_block(esteira)
                #print(Block.blocks)
            elif event.key == pygame.K_r:
                Block.blocks[-1].remove_from_screen()
            elif event.key == pygame.K_1:
                porta1.toggle()
            elif event.key == pygame.K_2:
                porta2.toggle()
            elif event.key == pygame.K_DELETE:
                Block.reset_all()
                Esteira.reset_all()
                Sinkhole.reset_all()

            else:
                my_direction = 5

        
        if event.type == pygame.WINDOWEVENT_CLOSE:
            pygame.quit()
            break

        if event.type == USEREVENT:
            # Atualiza o valor das portas para serem acionadas
            portas_acesas = extrair_porta_para_lista(last_input)

            for indx, p in enumerate(portas_acesas):
                if indx == 0:
                    if p==1:
                        porta1.activate()
                    else:
                        porta1.deactivate()
                
                if indx == 1:
                    if p==1:
                        porta2.activate()
                    else:
                        porta2.deactivate()
                if indx == 5:
                    if p==1 and var_aux_pode_ger_blk:
                        Block.new_block(esteira)
                        var_aux_pode_ger_blk = False
                    else:
                        var_aux_pode_ger_blk = True


        if my_direction == UP:
            position = (position[0], position[1] - step)
            #print('posicao da figura:', position)

        elif my_direction == LEFT:
            position = (position[0] - step, position[1])
            #print('posicao da figura:', position)

        elif my_direction == DOWN:
            position = (position[0], position[1] + step)
            #print('posicao da figura:', position)

        elif my_direction == RIGHT:
            position = (position[0] + step, position[1])
            #print('posicao da figura:', position)

        else:
            my_direction = 5


    # Atualizar a posição dos blocos:
    Block.update_blocks_position()

    #Limpar a tela
    screen.fill((200,200,200))

    # Colocar as imagens na tela:
    esteira_vert_1.update_conveyor_screen()
    esteira_vert_2.update_conveyor_screen()
    esteira.update_conveyor_screen()
    
    #-----AQUI VÃO OS BLOCOS vvvv-------
    Block.update_blocks_screen()
    Esteira.update_peso()
    #-----AQUI VÃO OS BLOCOS ^^^^-------


    screen.blit(gerador,gerador_pos)

    contagem_1.update_screen()
    contagem_2.update_screen()
    
    
    saida.update_screen()

    #portas:
    porta1.update_screen()
    porta2.update_screen()
    
    sensor_indutivo.update_screen()
    sensor_optico.update_screen()
    sensor_capacitivo.update_screen()

    k = 0
    if sensor_optico.status:
        k = k + 4
    if sensor_indutivo.status:
        k = k + 2
    if sensor_capacitivo.status:
        k = k + 1

    to_output = k
    # Para testes
    #screen.blit(img2,(0,0))
    render_texts()

   

    # Atualiza o display    
    pygame.display.update()

    # ----- fim do while

pygame.quit()