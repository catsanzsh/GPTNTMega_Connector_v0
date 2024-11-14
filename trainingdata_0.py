import sys
import pygame
import random
from collections import deque

pygame.init()

# Window dimensions
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS = WIDTH // BLOCK_SIZE
ROWS = HEIGHT // BLOCK_SIZE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(0, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

class MegaConnector:
    """
    Simulates a data streaming service for Tetromino pieces.
    """
    def __init__(self):
        self.pieces = [
            {"shape": [[1, 1, 1, 1]], "color": (0, 255, 255)},  # I
            {"shape": [[1, 1], [1, 1]], "color": (255, 0, 0)},  # O
            {"shape": [[0, 1, 0], [1, 1, 1]], "color": (0, 255, 0)},  # T
            {"shape": [[1, 0, 0], [1, 1, 1]], "color": (0, 0, 255)},  # L
            {"shape": [[0, 0, 1], [1, 1, 1]], "color": (255, 255, 0)}  # J
        ]

    def stream_piece(self):
        return random.choice(self.pieces)

class Piece:
    def __init__(self, shape, color, x, y):
        self.shape = shape
        self.color = color
        self.x = x
        self.y = y

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class ToonToonTetrimo:
    """
    Main engine with streaming-like behavior for Tetromino pieces.
    """
    def __init__(self, connector):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.connector = connector
        self.piece_queue = deque([self._get_new_piece() for _ in range(3)])
        self.current_piece = self.piece_queue.popleft()
        self.piece_queue.append(self._get_new_piece())
        self.game_over = False

    def _get_new_piece(self):
        piece_data = self.connector.stream_piece()
        return Piece(piece_data["shape"], piece_data["color"], COLS // 2 - len(piece_data["shape"][0]) // 2, 0)

    def draw_grid(self, screen):
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, screen):
        shape = self.current_piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, self.current_piece.color,
                        ((self.current_piece.x + x) * BLOCK_SIZE, (self.current_piece.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )
                    pygame.draw.rect(
                        screen, WHITE,
                        ((self.current_piece.x + x) * BLOCK_SIZE, (self.current_piece.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1
                    )

    def valid_space(self, shape, offset):
        off_x, off_y = offset
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x + off_x
                    new_y = self.current_piece.y + y + off_y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        shape = self.current_piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_rows()
        if self.piece_queue:
            self.current_piece = self.piece_queue.popleft()
            self.piece_queue.append(self._get_new_piece())
        else:
            self.current_piece = self._get_new_piece()
        if not self.valid_space(self.current_piece.shape, (0, 0)):
            self.game_over = True

    def clear_rows(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        rows_cleared = ROWS - len(new_grid)
        self.grid = [[0 for _ in range(COLS)] for _ in range(rows_cleared)] + new_grid
        self.score += rows_cleared

    def update(self):
        self.current_piece.y += 1
        if not self.valid_space(self.current_piece.shape, (0, 0)):
            self.current_piece.y -= 1
            self.lock_piece()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_piece.x -= 1
                if not self.valid_space(self.current_piece.shape, (0, 0)):
                    self.current_piece.x += 1
            elif event.key == pygame.K_RIGHT:
                self.current_piece.x += 1
                if not self.valid_space(self.current_piece.shape, (0, 0)):
                    self.current_piece.x -= 1
            elif event.key == pygame.K_DOWN:
                self.current_piece.y += 1
                if not self.valid_space(self.current_piece.shape, (0, 0)):
                    self.current_piece.y -= 1
            elif event.key == pygame.K_UP:
                self.current_piece.rotate()
                if not self.valid_space(self.current_piece.shape, (0, 0)):
                    self.current_piece.rotate()  # Rotate back if invalid

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Initialize MegaConnector for streaming-like behavior
    connector = MegaConnector()

    # Start ToonToonTetrimo engine
    engine = ToonToonTetrimo(connector)

    drop_speed = 500  # Speed in milliseconds
    last_drop = pygame.time.get_ticks()

    while not engine.game_over:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            engine.handle_event(event)

        # Automatic piece drop (gravity simulation)
        if pygame.time.get_ticks() - last_drop > drop_speed:
            engine.update()
            last_drop = pygame.time.get_ticks()

        engine.draw_grid(screen)
        engine.draw_piece(screen)
        pygame.display.flip()
        clock.tick(30)  # FPS limit for smooth input handling

if __name__ == "__main__":
    main()
