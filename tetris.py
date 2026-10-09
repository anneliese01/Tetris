import pygame
import random

# --- Constantes y Colores ---
# Aquí definimos los valores fijos del juego, como el tamaño de los bloques
# y los colores que vamos a usar para las piezas.
BLOCK_SIZE = 30
GRID_WHIDTH = 10  # Ancho del tablero (10 bloques)
GRID_HEIGHT = 20  # Alto del tablero (20 bloques)

# Calculamos el tamaño de la ventana basándonos en el tablero
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WHIDTH + 8) 
SCREEN_HEIGHY = BLOCK_SIZE * GRID_HEIGHT

# Definición de colores en formato RGB
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 0, 255)
NARANJA = (255, 165, 0)
CYAN = (0, 255, 255)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
MORADO = (128, 0, 128)
GRIS = (128, 128, 128)

# --- Definición de Figuras ---
# Cada lista representa una forma (I, J, L, O, S, T, Z) usando 1s y 0s.
SHAPES = [
    [[1, 1, 1, 1]],          # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]
COLORS = [AZUL, NARANJA, CYAN, AMARILLO, VERDE, ROJO, MORADO]

# --- Clase Tetromino ---
# Esta clase representa una pieza individual del juego.
class Tetromino:
    # Le asignamos su forma, su color y su posición inicial (arriba al centro).
    def __init__(self, shape_idx):
        self.shape_idx = shape_idx
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WHIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    # Método para rotar la pieza.
    def rotate(self):
        self.shape = [[self.shape[y][x] for y in range(len(self.shape) - 1, -1, -1)]
                    for x in range(len(self.shape[0]))]

# --- Clase TetrisGame ---
# Esta clase maneja toda la lógica principal del juego.
class TetrisGame:
    # Prepara el tablero vacío, crea la primera pieza y configura las variables
    # iniciales como el puntaje y la velocidad.
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        # Creamos el tablero lleno de color NEGRO (vacío)
        self.grid = [[NEGRO for _ in range(GRID_WHIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece() # Pieza que cae
        self.next_piece = self.new_piece()    # Pieza que sigue
        
        self.game_over = False
        self.score = 0
        self.fall_time = 0
        self.fall_speed = 500
        # Cargamos las fuentes para escribir texto en pantalla
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 60)

    # Método para crear una pieza nueva al azar.
    def new_piece(self):
        return Tetromino(random.randint(0, len(SHAPES) - 1))

    # Método para validar movimientos.
    # Revisa si la pieza choca con los bordes o con otras piezas fijas.
    # Si el movimiento es válido devuelve True, si choca devuelve False.
    def valid_move(self, piece, x_offset, y_offset, shape=None):
        check_shape = shape if shape is not None else piece.shape
        
        for i in range(len(check_shape)):
            for j in range(len(check_shape[i])):
                if check_shape[i][j]: # Si esa parte de la pieza tiene bloque
                    new_x = piece.x + j + x_offset
                    new_y = piece.y + i + y_offset
                    # Verificamos que esté dentro del tablero y no choque con nada
                    if (new_x < 0 or new_x >= GRID_WHIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x] != NEGRO)):
                        return False
        return True

    # Método para fijar la pieza en el tablero.
    # Cuando una pieza ya no puede bajar más, se "copia" en la rejilla (grid).
    # También revisa si perdiste (si la pieza se queda trabada arriba del todo).
    def lock_piece(self):
        for i in range(len(self.current_piece.shape)):
            for j in range(len(self.current_piece.shape[i])):
                if self.current_piece.shape[i][j]:
                
                    # Si la pieza se bloquea fuera de la pantalla (arriba), es Game Over
                    if self.current_piece.y + i < 1:
                        self.game_over = True
                        return 
                        
                    # Guardamos el color de la pieza en la posición correspondiente del tablero
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.color
        
        # Después de fijar, revisamos si hay líneas completas
        self.clear_lines()
        # Pasamos a la siguiente pieza
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # Si la nueva pieza ya choca al nacer, perdiste
        if not self.valid_move(self.current_piece, 0, 0):
            self.game_over = True

    # Método para borrar líneas completas.
    # Recorre el tablero, elimina las filas llenas, baja las de arriba
    # y aumenta el puntaje y la velocidad.
    def clear_lines(self):
        lines_cleared = 0
        # Crea una nueva lista solo con las filas que NO están llenas
        new_grid = [row for row in self.grid if any(cell == NEGRO for cell in row)]
        
        lines_cleared = GRID_HEIGHT - len(new_grid)
        
        # Rellena lo que falta arriba con filas vacías
        empty_rows = [[NEGRO for _ in range(GRID_WHIDTH)] for _ in range(lines_cleared)]
        self.grid = empty_rows + new_grid
        
        # Suma puntos y aumenta dificultad
        self.score += lines_cleared * 100
        
        if lines_cleared > 0 and self.fall_speed > 100:
            self.fall_speed -= 15 * lines_cleared

    # Método para dibujar la cuadrícula gris de fondo.
    def draw_grid(self):
        for x in range(0, BLOCK_SIZE * GRID_WHIDTH + 1, BLOCK_SIZE):
            pygame.draw.line(self.screen, GRIS, (x, 0), (x, SCREEN_HEIGHY))
        for y in range(0, SCREEN_HEIGHY + 1, BLOCK_SIZE):
            pygame.draw.line(self.screen, GRIS, (0, y), (BLOCK_SIZE * GRID_WHIDTH, y))

    # Método auxiliar para dibujar una pieza en pantalla.
    def draw_piece(self, piece, x_offset=0, y_offset=0):
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j]:
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        ( (piece.x + j + x_offset) * BLOCK_SIZE,
                          (piece.y + i + y_offset) * BLOCK_SIZE,
                        BLOCK_SIZE - 2,
                        BLOCK_SIZE - 2 )
                    )

    # Método para dibujar todas las piezas que ya están fijas en el tablero.
    def draw_board(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WHIDTH):
                if self.grid[y][x] != NEGRO:
                    pygame.draw.rect(
                        self.screen,
                        self.grid[y][x],
                        ( x * BLOCK_SIZE, y * BLOCK_SIZE,
                        BLOCK_SIZE - 2, BLOCK_SIZE - 2 )
                    )
    
    # Método para mostrar el texto (Puntaje y Siguiente Pieza).
    def draw_text(self):
        score_text = self.font.render(f"Puntaje: {self.score}", True, BLANCO)
        self.screen.blit(score_text, (GRID_WHIDTH * BLOCK_SIZE + 20, 50))
        
        next_piece_text = self.font.render("Siguiente:", True, BLANCO)
        self.screen.blit(next_piece_text, (GRID_WHIDTH * BLOCK_SIZE + 20, 150))
        # Dibujamos la pieza siguiente a un lado
        self.draw_piece(self.next_piece, x_offset=GRID_WHIDTH - 3, y_offset=6)
        
    # Método interno para dibujar el mensaje de "Game Over".
    def draw_game_over(self):
        over_text = self.game_over_font.render("GAME OVER", True, ROJO)
        text_rect = over_text.get_rect(center=(
            (GRID_WHIDTH * BLOCK_SIZE) // 2,
            SCREEN_HEIGHY // 2
        ))

        # Creamos un fondo semi-transparente para que el texto se lea mejor
        s = pygame.Surface(((GRID_WHIDTH * BLOCK_SIZE), SCREEN_HEIGHY // 4))
        s.set_alpha(180)
        s.fill(NEGRO)
        self.screen.blit(s, (0, SCREEN_HEIGHY // 2 - 50))
        
        self.screen.blit(over_text, text_rect)

    # Método público para mostrar la pantalla final completa.
    def draw_game_over_screen(self):
        self.draw_game_over()
        self.draw_text() 

    # Método principal del ciclo de juego (Un paso a la vez).
    # Se llama 60 veces por segundo desde el main().
    def run_game_step(self, events):
        
        # 1. Procesar teclas (Izquierda, Derecha, Abajo, Arriba/Rotar)
        for event in events:
            if event.type == pygame.KEYDOWN and not self.game_over:
                if event.key == pygame.K_LEFT:
                    if self.valid_move(self.current_piece, -1, 0):
                        self.current_piece.x -= 1
                if event.key == pygame.K_RIGHT:
                    if self.valid_move(self.current_piece, 1, 0):
                        self.current_piece.x += 1
                if event.key == pygame.K_DOWN:
                    if self.valid_move(self.current_piece, 0, 1):
                        self.current_piece.y += 1
                if event.key == pygame.K_UP:
                    # Intenta rotar creando una copia temporal de la forma
                    rotated_shape = [[self.current_piece.shape[y][x]
                                    for y in range(len(self.current_piece.shape) - 1, -1, -1)]
                                    for x in range(len(self.current_piece.shape[0]))]
                    
                    if self.valid_move(self.current_piece, 0, 0, shape=rotated_shape):
                        self.current_piece.shape = rotated_shape
        
        # 2. Lógica de gravedad (hacer caer la pieza automáticamente)
        if not self.game_over:
            self.fall_time += self.clock.get_time()
            
            # Si ya pasó el tiempo suficiente, bajamos la pieza
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if self.valid_move(self.current_piece, 0, 1):
                    self.current_piece.y += 1
                else:
                    # Si no puede bajar más, se bloquea
                    self.lock_piece()
        
        # 3. Dibujar todo en pantalla
        self.screen.fill(NEGRO)
        self.draw_board()
        self.draw_grid()
        self.draw_piece(self.current_piece)
        self.draw_text()
        
        # 4. Avisar al Main si el juego sigue o terminó
        if self.game_over:
            return "game_over"
        else:
            return "playing"

# --- FUNCIONES INDEPENDIENTES (Menú y Cuenta Atrás) ---

# Función para dibujar el menú principal.
def draw_menu(screen, font_title, font_text):
    screen.fill(NEGRO)
    
    # Dibuja el título y las instrucciones centrados
    title_text = font_title.render("Tetris 2D", True, BLANCO)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHY / 2 - 50))
    
    start_text = font_text.render("Presiona 'ESPACIO' para empezar", True, BLANCO)
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHY / 2 + 30))
    
    screen.blit(title_text, title_rect)
    screen.blit(start_text, start_rect)
    
    pygame.display.flip()

# Función para mostrar la cuenta regresiva (3, 2, 1...).
def draw_countdown(screen, font_title, count):
    screen.fill(NEGRO)
    # Dibujamos la rejilla de fondo para que se vea mejor
    for x in range(0, BLOCK_SIZE * GRID_WHIDTH + 1, BLOCK_SIZE):
        pygame.draw.line(screen, GRIS, (x, 0), (x, SCREEN_HEIGHY))
    for y in range(0, SCREEN_HEIGHY + 1, BLOCK_SIZE):
        pygame.draw.line(screen, GRIS, (0, y), (BLOCK_SIZE * GRID_WHIDTH, y))
    
    # Dibuja el número grande en el centro
    count_text = font_title.render(str(count), True, BLANCO)
    count_rect = count_text.get_rect(center=( (GRID_WHIDTH * BLOCK_SIZE) // 2, SCREEN_HEIGHY / 2))
    screen.blit(count_text, count_rect)
    
    pygame.display.flip()
    pygame.time.wait(500) # Espera 1 segundo antes de seguir


# --- BUCLE PRINCIPAL (Main) ---
# Aquí empieza la ejecución del programa.
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHY))
    pygame.display.set_caption('Tetris 2D')
    clock = pygame.time.Clock()
    
    font_title = pygame.font.Font(None, 72)
    font_text = pygame.font.Font(None, 36)

    # Estado inicial: estamos en el menú
    game_state = "menu"
    game = None 

    running = True
    while running:
        
        # Revisamos si cierran la ventana
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # --- Máquina de Estados ---
        # Decide qué mostrar según en qué parte del juego estamos
        
        if game_state == "menu":
            draw_menu(screen, font_title, font_text)
            # Si aprietan Espacio, pasamos a la cuenta atrás
            for event in events: 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state = "countdown"
                    
        elif game_state == "countdown":
            # Muestra 3, 2, 1 y luego arranca el juego
            draw_countdown(screen, font_title, 3)
            draw_countdown(screen, font_title, 2)
            draw_countdown(screen, font_title, 1)
            
            game = TetrisGame(screen, clock)
            game_state = "playing"

        elif game_state == "playing":
            if game:
                # Ejecuta la lógica del juego frame por frame
                game_state = game.run_game_step(events)
                pygame.display.flip() 

        elif game_state == "game_over":
            if game:
                game.draw_game_over_screen()
                pygame.display.flip()
                pygame.time.wait(3000) 
            
            game_state = "menu" # Vuelve al menú principal
        
        # Limita el juego a 60 cuadros por segundo
        clock.tick(60)
        
    pygame.quit()
if __name__ == "__main__":
    main()