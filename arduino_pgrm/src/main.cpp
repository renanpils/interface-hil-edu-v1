/* ==================================================
Programa de testes para comunicação entre Python e Arduino via UART.
Parte do TCC2

aguarda a mensagem: 1 2 3 4

Autor: Renan Sandes
Outubro 2019

last upload: 10/01/2020
==================================================*/

#define __AVR_ATmega328P__
#include <Arduino.h>
#define FOSC 16000000
#define USART_BAUDRATE 9600 
#define LED_PIN 13
#define BUTTON_PIN 12

#define INICIO 0
#define RUN 1

// Define para comm

#define STX 0x02
#define ETX 0x03
#define ACK 0x06
#define EOT 0x04
#define NAK 0x15

#define START_MSG_CHAR STX
#define END_MSG_CHAR ETX


// Variáveis Globais:
volatile int LED_STATE = 0;
volatile int ESTADO_ATUAL = 0;

#define ESTADO_INICIAL 0
#define ESTADO_RODANDO 1


volatile int MSG_COUNT = 0;
volatile char MSG_RECEBIDA_VEC[21];
volatile char MSG_RECEBIDA_FLAG = 0;

volatile char COMANDO;
volatile char VALOR;
volatile char entradas_lidas;
volatile char auxiliares_lidas;


#define BUFFER_SIZE 8
typedef struct buffer_t
{
  volatile char data[BUFFER_SIZE];
  volatile unsigned char pos;
  volatile char b_size;
} buffer_t;

buffer_t rx_buffer;
void buffer_init(buffer_t b){
  b.b_size = BUFFER_SIZE;
}

// Protótipos:
void readInputs(char *i);
void writeOutput(char c);
void writeAuxiliaryOutput(char c);
void readAuxiliaryInputs(volatile char *i);
void TIMER1_INIT();

// Protótipos do protocolo:
void mp_UART_INIT();
void mp_ENVIA_CARACTERE(unsigned char c);
void executa_comando(volatile char COMANDO, volatile char VALOR);
void responde_comando(volatile char COMANDO, volatile char VALOR);
void envia_mensagem_protocolo(volatile char COMANDO, volatile char VALOR);


// Definições das interrupções:

// Interrupção da recepção via UART
ISR(USART_RX_vect){

  UCSR0A  &= 0b01111111;  // Abaixar o flag de caractere recebido
  
  rx_buffer.data[rx_buffer.pos] = UDR0;

  // Caso seja identificado inicio e final da mensagem
  if (rx_buffer.data[rx_buffer.pos] == END_MSG_CHAR &&
      rx_buffer.data[((char)(rx_buffer.pos-3))%rx_buffer.b_size] == START_MSG_CHAR)
  {
    COMANDO = rx_buffer.data[((char)(rx_buffer.pos-2))%rx_buffer.b_size];
    VALOR =   rx_buffer.data[((char)(rx_buffer.pos-1))%rx_buffer.b_size]; 
    MSG_RECEBIDA_FLAG = 1;
    
    /* Descomentar em caso de debug
    // Eco na mensagem que ele acha que recebeu.
    mp_ENVIA_CARACTERE(rx_buffer.data[((char)(rx_buffer.pos-3))%rx_buffer.b_size]);
    mp_ENVIA_CARACTERE(rx_buffer.data[((char)(rx_buffer.pos-2))%rx_buffer.b_size]);
    mp_ENVIA_CARACTERE(rx_buffer.data[((char)(rx_buffer.pos-1))%rx_buffer.b_size]);
    mp_ENVIA_CARACTERE(rx_buffer.data[((char)(rx_buffer.pos))%rx_buffer.b_size]);
    */

    rx_buffer.pos = 0;
  }
  // Senão, incrementa e cai fora da interrupção
  else
  { 
    rx_buffer.pos = (rx_buffer.pos + 1) % rx_buffer.b_size;  
    MSG_RECEBIDA_FLAG = 0;
  }
  
}
ISR(TIMER1_COMPA_vect){
  if (LED_STATE); 
    //writeOutput(VAL);
  else;
    //writeOutput(0);

  LED_STATE = !LED_STATE;
  
  
}
void TRIP_TIMER_1(){ 
  // Começa a contar o timer!
  TCCR1B |= (1<<CS10)|(0<<CS11)|(1<<CS12);
 }
 void STOP_TIMER_1(){
   // stop timer.
  TCCR1B &= (0<<CS10)|(0<<CS11)|(0<<CS12);
  TCNT1  = 0;
   
  writeOutput(0);
 }


// Variáveis para protocolo:


// Variáveis globais:
volatile unsigned char count = 5;
char X = 0;


// Setup para iniciailizar:
void setup() {
  
  // Saídas
  pinMode(2,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(4,OUTPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);

  //Entradas
  pinMode(8,INPUT);
  pinMode(9,INPUT);
  pinMode(10,INPUT);
  pinMode(11,INPUT);
  pinMode(12,INPUT);
  pinMode(13,INPUT);

  // Auxiliares
  pinMode(A0,INPUT_PULLUP);
  pinMode(A1,INPUT_PULLUP);
  pinMode(A2,INPUT_PULLUP);
  pinMode(A3,OUTPUT);
  pinMode(A4,OUTPUT);
  pinMode(A5,OUTPUT);


  writeOutput(0);

  mp_UART_INIT();
  TIMER1_INIT();

  buffer_init(rx_buffer);
  
  //TRIP_TIMER_1();
  
}

////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

volatile char K;

void loop() {

    if(MSG_RECEBIDA_FLAG == 1){
      MSG_RECEBIDA_FLAG = 0;
      executa_comando(COMANDO, VALOR);
    }
    

    if (ESTADO_ATUAL == ESTADO_INICIAL){
      K = (K==0)?(0xFF):(0);
      writeAuxiliaryOutput(K);
      delay(500);
      

    }
    
}



////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////


// Definição das funções do sketch principal:
void writeOutput(char c){
    digitalWrite(2, ((c & 0b00000001)) == 0);
    digitalWrite(3, ((c & 0b00000010)) == 0);
    digitalWrite(4, ((c & 0b00000100)) == 0);
    digitalWrite(5, ((c & 0b00001000)) == 0);
    digitalWrite(6, ((c & 0b00010000)) == 0);
    digitalWrite(7, ((c & 0b00100000)) == 0);
}
void writeAuxiliaryOutput(char c){
    digitalWrite(A3, ((c & 0b00000001)) != 0);
    digitalWrite(A4, ((c & 0b00000010)) != 0);
    digitalWrite(A5, ((c & 0b00000100)) != 0);
}

void readInputs(volatile char *i){
    *i= 0;
    *i = (*i) | (digitalRead(8) <<0);
    *i = (*i) | (digitalRead(9) <<1);
    *i = (*i) | (digitalRead(10)<<2);
    *i = (*i) | (digitalRead(11)<<3);
    *i = (*i) | (digitalRead(12)<<4);
    *i = (*i) | (digitalRead(13)<<5);
}

void readAuxiliaryInputs(volatile char *i){
    *i = 0;
    *i = (*i) | (digitalRead(A0) <<0);
    *i = (*i) | (digitalRead(A1) <<1);
    *i = (*i) | (digitalRead(A2) <<2);

    *i = *i ^ 0b00000111;
}

// Definição das funções do protocolo:
void mp_UART_INIT() {
  // Função para inicializar a UART
  volatile unsigned char MYUBRR = (unsigned char)(FOSC / 16 / USART_BAUDRATE - 1);
  UBRR0L = ( MYUBRR & 0xff); // Registradores de BAUDRATE
  UBRR0H = ( MYUBRR >> 8  );   // Registradores de BAUDRATE
  UCSR0C = 0b00000110;  // Use 8-bit character sizes
  UCSR0B = 0b10011000;  // Turn on the transmission, reception, and Receive interrupt
  UCSR0A  &= 0b01111111;  // Abaixar o flag de caractere recebido
}

void mp_ENVIA_CARACTERE(unsigned char c) {
  // Esperar esvaziar o buffer de transmissão
  while ( !(UCSR0A & (1 << UDRE0)) );

  // Colocar dados no buffer
  UDR0 = c;
}

void TIMER1_INIT() {

  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;

  OCR1AH = 0xFF;
  OCR1AL = 0xFF;

  TCCR1B |= (1 << WGM12) | (1 << CS10) | (1 << CS12);
  TIMSK1 |= (0 << OCIE1A);
  
  /*para ajustar o valor do pisca: freq Toggle (ciclo on + ciclo off)
  OCRnA = (FCLK / FOCnA) * (1 / (2* PRESCALER)) - 1
  */
}

void envia_mensagem_protocolo(char COMANDO,char VALOR){
  mp_ENVIA_CARACTERE(START_MSG_CHAR);
  mp_ENVIA_CARACTERE(COMANDO);
  mp_ENVIA_CARACTERE(VALOR);
  mp_ENVIA_CARACTERE(END_MSG_CHAR);
}

void responde_comando(char COMANDO, char VALOR){
/*

  'A' - MENSAGEM RECEBIDA E EFETUADA
          -> ACK
          -> NAK

  'R' - RESPOSTA À SOLICITAÇÃO DE LEITURA
          -> 'R' + VALOR

  'S' - RESPONDE STATUS - A SER DEFINIDO
          -> ACK

  EOT - VOLTAR AO MODO DE ESPERA:
          -> EOT + ACK

*/
  switch (COMANDO)
  {
  case 'A':
    /* code */
    break;
  
  case 'R':
    /* code */
    break;
    
  case 'S':
    /* code */
    break;
  
  case EOT:
    /* code */
    break;

  default:
    break;
  }

}

void executa_comando(volatile char COMANDO,volatile char VALOR){
/*
  SOT (ASCII 1) - INICIA TRANSMISSÃO.

  'A' (ASCII 65)- ACIONA O VALOR RECEBIDO NAS SAÍDAS. RECEBE UM CHAR, NO ENTANTO, SÓ TEM 6 SAÍDAS.

  'X' (ASCII 58)

  'R' (ASCII 82)- REQUEST A LEITURA DAS ENTRADAS. RECEBE 8 BITS 

  'S' (ASCII 83) - REQUEST STATUS
  
  EOT (ASCII 4)- END OF TRANSMISSION - RETORNARÁ PARA O ESTADO INICIAL.

*/
  switch (COMANDO)
  {
  case 1: // SOH 
    /* INICIA A COMUNICAÇÃO */
    ESTADO_ATUAL = ESTADO_RODANDO;
    break;


  case 65: // 'A'
    /* ACIONA VALORES RECEBIDOS NA SAÍDA  */
    writeOutput(VALOR);
    envia_mensagem_protocolo(COMANDO, ACK);
    break;

  case 88: // 'X' <- ACIONA SAÍDAS AUXILIARES
    writeAuxiliaryOutput(VALOR);
    envia_mensagem_protocolo(COMANDO, ACK);
    break;

  case 82: // 'R'
    /* REQUEST LEITURA DAS ENTRADAS */
    
    switch (VALOR)
    {
    case 81: // 'Q'
      readInputs(&entradas_lidas);
      envia_mensagem_protocolo(COMANDO, entradas_lidas);
      break;

    case 65: // 'A' <- LER ENTRADAS AUXILIARES
      readAuxiliaryInputs(&auxiliares_lidas);
      envia_mensagem_protocolo(COMANDO, auxiliares_lidas);
      break;

    default:
      break;
    }
    break;

  case 83: // 'S'
    /* REQUEST STATUS */
    envia_mensagem_protocolo(COMANDO, ACK);
    break;

  case 4:
    /* END OF TRANSMISSION */
    ESTADO_ATUAL = ESTADO_INICIAL;
    break;
  
  default:
    break;
  }


}

void executa_estado(){




}