import pygame
import random
import threading
import queue

pygame.init()
pygame.display.set_caption("Jogo Snake Python")

largura, altura = 1200, 800
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

# cores RGB
preta = (0, 0, 0)
branca = (255, 255, 255)
vermelha = (255, 0, 0)
verde = (0, 255, 0)

# parametros da cobrinha
tamanho_quadrado = 20
velocidade_jogo = 15

# Filas para comunicação entre threads
event_queue = queue.Queue()
state_queue = queue.Queue()

# Eventos de sincronização
update_event = threading.Event()
render_event = threading.Event()

def gerar_comida():
    comida_x = round(random.randrange(0, largura - tamanho_quadrado) / float(tamanho_quadrado)) * float(tamanho_quadrado)
    comida_y = round(random.randrange(0, altura - tamanho_quadrado) / float(tamanho_quadrado)) * float(tamanho_quadrado)
    return comida_x, comida_y

def desenhar_comida(tamanho, comida_x, comida_y):
    pygame.draw.rect(tela, verde, [comida_x, comida_y, tamanho, tamanho])

def desenhar_cobra(tamanho, pixels):
    for pixel in pixels:
        pygame.draw.rect(tela, branca, [pixel[0], pixel[1], tamanho, tamanho])

def desenhar_pontuacao(pontuacao):
    fonte = pygame.font.SysFont("Helvetica", 35)
    texto = fonte.render(f"Pontos: {pontuacao}", True, vermelha)
    tela.blit(texto, [1, 1])

def selecionar_velocidade(tecla):
    if tecla == pygame.K_DOWN:
        return 0, tamanho_quadrado
    elif tecla == pygame.K_UP:
        return 0, -tamanho_quadrado
    elif tecla == pygame.K_RIGHT:
        return tamanho_quadrado, 0
    elif tecla == pygame.K_LEFT:
        return -tamanho_quadrado, 0
    return None

def atualizar_jogo():
    global fim_jogo, x, y, velocidade_x, velocidade_y, tamanho_cobra, pixels, comida_x, comida_y

    while not fim_jogo:
        try:
            evento = event_queue.get_nowait()
            if evento.type == pygame.QUIT:
                fim_jogo = True
            elif evento.type == pygame.KEYDOWN:
                nova_velocidade = selecionar_velocidade(evento.key)
                if nova_velocidade:
                    velocidade_x, velocidade_y = nova_velocidade
        except queue.Empty:
            pass

        if x < 0 or x >= largura or y < 0 or y >= altura:
            fim_jogo = True

        x += velocidade_x
        y += velocidade_y

        pixels.append([x, y])

        if len(pixels) > tamanho_cobra:
            del pixels[0]

        for pixel in pixels[:-1]:
            if pixel == [x, y]:
                fim_jogo = True

        if x == comida_x and y == comida_y:
            tamanho_cobra += 1
            comida_x, comida_y = gerar_comida()

        state = {
            'pixels': pixels.copy(),
            'comida_x': comida_x,
            'comida_y': comida_y,
            'tamanho_cobra': tamanho_cobra - 1
        }

        state_queue.put(state)
        update_event.set()
        render_event.wait()
        render_event.clear()

        relogio.tick(velocidade_jogo)

def renderizar():
    while not fim_jogo:
        update_event.wait()
        update_event.clear()
        tela.fill(preta)
        try:
            state = state_queue.get_nowait()
            desenhar_comida(tamanho_quadrado, state['comida_x'], state['comida_y'])
            desenhar_cobra(tamanho_quadrado, state['pixels'])
            desenhar_pontuacao(state['tamanho_cobra'])
        except queue.Empty:
            pass
        pygame.display.update()
        render_event.set()

def rodar_jogo():
    global fim_jogo, x, y, velocidade_x, velocidade_y, tamanho_cobra, pixels, comida_x, comida_y

    x = largura / 2
    y = altura / 2
    velocidade_x = 0
    velocidade_y = 0
    tamanho_cobra = 1
    pixels = []
    comida_x, comida_y = gerar_comida()
    fim_jogo = False

    thread_jogo = threading.Thread(target=atualizar_jogo)
    thread_render = threading.Thread(target=renderizar)

    thread_jogo.start()
    thread_render.start()

    while not fim_jogo:
        for evento in pygame.event.get():
            event_queue.put(evento)

    thread_jogo.join()
    thread_render.join()

rodar_jogo()
pygame.quit()