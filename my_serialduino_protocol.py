import serial
import time
import pygame
import threading

class My_protocol(object):

    def __init__(self, COM_PORT, pygame: pygame):
        '''
        COM_PORT: STRING COM A PORTA COM DA INTERFACE
        pygame: Instância do módulo pygame:

        ex: cll mp = My_protocol('COM7', pygame)
        '''
    
        self.COM_PORT = COM_PORT
        self.b = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.pygame_instance = pygame
        # Variaveis para ajundar na comunicação
        self.last_input = 0
        self.to_auxiliary_output = 0
        self.to_output = 0

        self.evento_porta = self.pygame_instance.event.Event(self.pygame_instance.USEREVENT)
        USEREVENT2 = self.pygame_instance.USEREVENT + 1 
        self.evento_porta_auxiliar = self.pygame_instance.event.Event(USEREVENT2)

        self.communication_thread = threading.Thread(target=self.communication)

    def open_port(self):
        self.ser = serial.Serial(self.COM_PORT, baudrate=9600, timeout=2)
        time.sleep(2)

    def close_port(self):
        self.ser.close()
    
    def send_msg(self, comando, valor):
        # self.ser.write(b'\x02')
        # self.ser.write(bytes([comando])) #SOK
        # self.ser.write(bytes([valor])) #ENQ
        # self.ser.write(b'\x03')
        self.ser.write(bytes([0x02, comando, valor, 0x03]))

    def get_answer(self, expected):
        #t1 = time.perf_counter()
        ''' 
        dado que o frame esperado na resposta é:
        | 0x02 | comando | valor | 0x03 | 
        
        expected: comando esperado na resposta (em inteiro)
        exemplo: ord('A') ou 65 ou 0x41

        '''

        # cria um buffer (tamanho da mensagem)
        #b = [0,0,0,0]
        counter = 3

        # continua insistindo até que encontre uma mensagem.
        while(self.ser.in_waiting != 0 or (not (self.b[counter]== 3 and self.b[counter-3]== 2 and self.b[counter-2] == expected))):
            # Append até que a mensagem seja encontrada
            counter = counter + 1
            self.b[counter] = int.from_bytes(self.ser.read(), byteorder='big')
            
            if counter > 15:
                print(counter, self.b)
                raise NameError('Procurando resposta, mas sem mensagem!')
        
        #t2 = time.perf_counter()
        #print("tempo do get_answer =",t2-t1, "counter = ", counter)
        #retorna o valor recebido    
        return self.b[counter-1]

    def get_start_ackowledge(self):
        ## FUNÇÃO INUTILIZADA! ##
        
        # Função para bloquear enquando ACK não é recebido dando
        #   início à comunicação.
        
        # cria um buffer (tamanho da mensagem)
        b = 6 #NAK

        counter = 0
        # continua insistindo até que encontre uma mensagem.
        while((b != 6)):
            # Append até que a mensagem seja encontrada
            b= int.from_bytes(self.ser.read(), byteorder='big')
            print(b)
            counter = counter + 1
            if counter > 1024:
                raise NameError('ACK nao recebido!')
        

    def start_commmunication(self):
        '''
            Função para iniciar a comunicação
        '''
        # Limpa buffer da entrada
        self.ser.flushInput()
        
        # Envia inicio da comunicação
        self.send_msg(1, 5) # SOK, ENQ
        
        time.sleep(1)
        print('INICIA COMUNICAÇÃO!')
    
        print('COMUNICAÇÃO INICIADA COM SUCESSO!')


    def termina(self):
        # Encerra comunicação
        self.send_msg(4, 5) # EOT, ENQ
        

    def set_outputs(self, VALOR):
        '''
        Recebe um inteiro e aciona o valor nas portas de saída.
        '''
        #Envia comando para acionar:
        self.send_msg(ord('A'), VALOR)

        #Aguarda confirmação de tarefa efetuada!
        if(self.get_answer(ord('A')) != 6):
            raise NameError('Porta não acionada como deveria!')

    def set_auxiliary_outputs(self, VALOR):
        '''
        Recebe um inteiro e aciona o valor nas portas de saída.
        '''
        #Envia comando para acionar:
        self.send_msg(ord('X'), VALOR)

        #Aguarda confirmação de tarefa efetuada!
        if(self.get_answer(ord('X')) != 6):
            raise NameError('Porta não acionada como deveria!')
       
    
    def read_inputs(self):
        '''
        Retorna um inteiro com as portas que estão ativas
        '''
        #print('SOLICITA LEITURA ----')
        #limpa o buffer de entrada
        self.ser.flushInput()

        # Envia mensagem solicitando leitura:
        self.send_msg(ord('R'),ord('Q'))

        #aguarda resposta e retorna o valor
        return self.get_answer(ord('R'))

    def read_auxiliary_inputs(self):
        '''
        Retorna um inteiro com as portas auxiliares que estão ativas
        '''
        #print('SOLICITA LEITURA ----')
        #limpa o buffer de entrada
        self.ser.flushInput()

        # Envia mensagem solicitando leitura:
        self.send_msg(ord('R'), ord('A'))

        #aguarda resposta e retorna o valor
        return self.get_answer(ord('R'))



    def return_active_ports(self):
        '''Retorna uma lista contendo as portas que estão ativas
            numeradas de 0 a 5
        '''

        dt = self.read_inputs()
        out = []
        for i in range(6):
            if (dt & 2**i)>0 :
                out.append(i)
        return out

    
    def communication(self):
        
        '''
        on pygame instance:
        import pygame
        
        call:

        t2 = threading.Thread(target=communication)
        t2.start()

        '''

        #My_protocol.last_input
        #global to_auxiliary_output
        #global to_output

        self.open_port()
        time.sleep(1)
        self.start_comm()
        
        self.last_input = self.read_inputs()
        self.last_auxiliary_input = self.read_auxiliary_inputs()

        while(True):
            # Solicita leitura:
            x = self.read_inputs()
            y = self.read_auxiliary_inputs()

            # Aplica leitura à saída:
            
            self.set_outputs(self.to_output)
            self.set_auxiliary_outputs(self.to_auxiliary_output)

            if (x != last_input):
                last_input = x

                # Lança o evento
                #print('Evento lançado!', ' | last_input= ', last_input)
                self.pygame_instance.event.post(self.evento_porta)

            if(y != last_auxiliary_input):
                last_auxiliary_input = y
                # Lança o evento
                #print('Evento lançado!', ' | last_input= ', last_input)
                self.pygame_instance.event.post(self.evento_porta_auxiliar)


    def read_inputs_ls_str(self):
        '''
        Retorna uma lista com as strings das portas que estão ativas
        Ex: ['I0', 'I3', 'I4']
        TESTAR!
        '''
        #print('SOLICITA LEITURA ----')
        #limpa o buffer de entrada
        self.ser.flushInput()

        # Envia mensagem solicitando leitura:
        self.send_msg(ord('R'),ord('Q'))
        #aguarda resposta e retorna o valor
        QS = self.get_answer(ord('R'))
        Q_LS = []
        for idx, Q in enumerate([1, 2, 4, 8, 16, 32, 64, 128]):
            if (Q & QS):
                Q_LS.append('Q{}'.format(idx))
                
        
        return Q_LS
            


