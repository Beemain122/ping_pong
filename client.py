from http import client

from pygame import *
import socket
import json
from threading import Thread

WIDTH, HEIGHT = 800, 600

init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))  # --- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            print("Received data:", data)  # Додаємо вивід отриманих даних
            buffer += data
            while '\n' in buffer:
                packet, buffer = buffer.split('\n', 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except Exception as e:
            print("Receive error:", e)
            game_state["winner"] = -1
            break


# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ЗОБРАЖЕННЯ ---

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()

Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    screen.fill((50, 50, 50))  # Просто сірий фон
    draw.rect(screen, (255, 0, 0), (100, 100, 20, 100))  # Намалюємо ракетку
    display.update()
    clock.tick(60)


    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render("Натисни R — рестарт", True, (255, 255, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        screen.fill((30, 30, 30))

        if "paddles" in game_state and '0' in game_state["paddles"]:
            x, y = game_state["paddles"]['0']
            draw.rect(screen, (255, 0, 0), (x, y, 20, 100))

        if "paddles" in game_state and '1' in game_state["paddles"]:
            x, y = game_state["paddles"]['1']
            draw.rect(screen, (0, 0, 255), (x, y, 20, 100))

        clock.tick(60)
        display.update()
