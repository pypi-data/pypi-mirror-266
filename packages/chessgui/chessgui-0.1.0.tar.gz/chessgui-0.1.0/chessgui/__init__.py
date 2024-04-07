import chess
import pygame
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (150, 75, 0)
BEIGE = (228, 213, 183)
RED = (255, 127, 127)

PIECES = [
    [
        pygame.image.load("assets/b_pawn.svg"),
        pygame.image.load("assets/b_knight.svg"),
        pygame.image.load("assets/b_bishop.svg"),
        pygame.image.load("assets/b_rook.svg"),
        pygame.image.load("assets/b_queen.svg"),
        pygame.image.load("assets/b_king.svg"),
    ],
    [
        pygame.image.load("assets/w_pawn.svg"),
        pygame.image.load("assets/w_knight.svg"),
        pygame.image.load("assets/w_bishop.svg"),
        pygame.image.load("assets/w_rook.svg"),
        pygame.image.load("assets/w_queen.svg"),
        pygame.image.load("assets/w_king.svg"),
    ],
]


def convert_pieces(pieces: list[list[pygame.Surface]], size: int):
    return [
        list(
            map(
                lambda x: pygame.transform.smoothscale(x, (size, size)).convert_alpha(),
                pieces[0],
            )
        ),
        list(
            map(
                lambda x: pygame.transform.smoothscale(x, (size, size)).convert_alpha(),
                pieces[1],
            )
        ),
    ]


class GUI:
    def __init__(self, size: int = 800) -> None:
        self.size = size
        self.sq_size = size // 8

        self.screen = pygame.display.set_mode((size, size))
        self.screen.fill(BLACK)

        self.pieces = convert_pieces(PIECES, self.sq_size)

        self.from_square = None
        self.to_square = None

    def draw(self, board: chess.Board, highlight_squares: list[int] = []):
        sq_size = self.size // 8

        for sq in range(64):
            pygame.draw.rect(
                self.screen,
                RED
                if sq in highlight_squares
                else (BEIGE if (sq + (sq // 8) % 2) % 2 else BROWN),
                (
                    ((sq % 8) * sq_size, (self.size - sq_size) - (sq // 8) * sq_size),
                    (sq_size, sq_size),
                ),
            )

            piece = board.piece_at(sq)

            if piece != None:
                self.screen.blit(
                    self.pieces[piece.color][piece.piece_type - 1],
                    ((sq % 8) * sq_size, (self.size - sq_size) - (sq // 8) * sq_size),
                )

        for i in range(1, 8):
            pygame.draw.line(
                self.screen, WHITE, (0, i * sq_size), (self.size, i * sq_size)
            )
            pygame.draw.line(
                self.screen, WHITE, (i * sq_size, 0), (i * sq_size, self.size)
            )

        pygame.display.flip()

    def reset_selection(self):
        self.from_square = None
        self.to_square = None

    def handle_events(self):
        events = {
            "quit": False,
            "on_square": None,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events["quit"] = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = 8 * (7 - math.floor(pos[1] / 100)) + math.floor(pos[0] / 100)

                events["on_square"] = square

        return events