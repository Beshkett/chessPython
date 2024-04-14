import os
import chess
import chess.engine
import pygame

class ChessGame:
    def __init__(self):
        """
        Initializes a new instance of the ChessGame class.
        """
        self.board = chess.Board()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        engine_path = os.path.join(dir_path, 'stockfish-windows-x86-64-avx2.exe')
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.engine.configure({"Skill Level": 1})
        self.human_player = chess.WHITE
        self.computer_player = chess.BLACK

        self.board_size = 640
        self.square_size = self.board_size // 8
        self.piece_images = self.load_piece_images()
        self.selected_piece = None
        self.selected_square = None

        pygame.init()
        self.screen = pygame.display.set_mode((self.board_size, self.board_size))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()

    def load_piece_images(self):
        """
        Loads the images for each chess piece.

        Returns:
        - piece_images: A dictionary mapping piece types and colors to their corresponding images.
        """
        piece_images = {}
        piece_symbols = ['p', 'n', 'b', 'r', 'q', 'k']
        dir_path = os.path.dirname(os.path.realpath(__file__))
        for piece_type, piece_symbol in zip(chess.PIECE_TYPES, piece_symbols):
            for player in [chess.WHITE, chess.BLACK]:
                image_path = os.path.join(dir_path, f"images/{piece_symbol}{('w' if player == chess.WHITE else 'b')}.png")
                image = pygame.image.load(image_path)
                piece_images[piece_type, player] = image
        return piece_images

    def draw_board(self):
        """
        Draws the chess board on the screen.
        """
        colors = [(233, 236, 239), (125, 135, 150)]
        for square in range(64):
            row, col = 7 - square // 8, square % 8
            color = colors[((row + col) % 2)]
            pygame.draw.rect(self.screen, color, pygame.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))

    def draw_pieces(self):
        """
        Draws the chess pieces on the board.
        """
        for square in range(64):
            piece = self.board.piece_at(square)
            if piece is not None:
                row, col = 7 - square // 8, square % 8
                image = self.piece_images[piece.piece_type, piece.color]
                image_width, image_height = image.get_size()
                x = col * self.square_size + self.square_size // 2 - image_width // 2
                y = row * self.square_size + self.square_size // 2 - image_height // 2
                self.screen.blit(image, (x, y))

    def draw_possible_moves(self):
        """
        Draws circles on the board to indicate the possible moves for the selected piece.
        """
        if self.selected_piece is not None:
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    row, col = 7 - move.to_square // 8, move.to_square % 8
                    pygame.draw.circle(self.screen, (135, 24, 16), (col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2), 10)

    def play(self):
        """
        Starts the chess game and handles the game loop.
        """
        running = True
        while running:
            self.draw_board()
            self.draw_pieces()
            self.draw_possible_moves()
            pygame.display.flip()

            if self.board.is_game_over():
                result = self.get_result()
                print(result)
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.board.turn == self.human_player:
                    self.handle_human_move(event)

            if running and self.board.turn == self.computer_player:
                self.handle_computer_move()

    def get_result(self):
        """
        Determines the result of the game.

        Returns:
        - result: The result of the game.
        """
        if self.board.is_checkmate():
            if self.board.turn == self.human_player:
                return "You lost"
            else:
                return "You won"
        elif self.board.is_stalemate():
            return "It's a stalemate"
        elif self.board.is_insufficient_material():
            return "It's a draw due to insufficient material"
        elif self.board.is_seventyfive_moves():
            return "It's a draw due to the 75-move rule"
        elif self.board.is_fivefold_repetition():
            return "It's a draw due to the fivefold repetition rule"
        elif self.board.can_claim_draw():
            return "It's a draw by claim"
        else:
            return "Unknown result"

    def handle_human_move(self, event):
        """
        Handles the human player's move.

        This method is responsible for processing the mouse events and updating the game state based on the human player's actions.

        Args:
        - event: The Pygame event object.

        Returns:
        - None

        Raises:
        - None

        Algorithm:
        1. Check if the event type is MOUSEBUTTONDOWN.
        2. If it is, get the position of the mouse click and calculate the corresponding column and row on the chessboard.
        3. Convert the column and row to a square on the chessboard.
        4. Check if there is a piece at the selected square and if it belongs to the human player.
        5. If there is a valid piece, set it as the selected piece and store the selected square.
        6. Check if the event type is MOUSEBUTTONUP.
        7. If it is, check if there is a selected piece.
        8. If there is, get the position of the mouse release and calculate the corresponding column and row on the chessboard.
        9. Convert the column and row to a target square on the chessboard.
        10. Create a move object using the selected square and target square.
        11. Check if the move is a legal move.
        12. If it is, update the game board by pushing the move and reset the selected piece and square.

        Example Usage:
        ```
        handle_human_move(event)
        ```

        Note:
        - This method assumes that the `self.board` attribute is a valid chess board object.
        - The `self.human_player` attribute should be set to the color of the human player (e.g., chess.WHITE or chess.BLACK) before calling this method.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col = pos[0] // self.square_size
            row = pos[1] // self.square_size
            square = chess.square(col, 7 - row)
            piece = self.board.piece_at(square)
            if piece is not None and piece.color == self.human_player:
                self.selected_piece = piece
                self.selected_square = square
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.selected_piece is not None:
                pos = pygame.mouse.get_pos()
                col = pos[0] // self.square_size
                row = pos[1] // self.square_size
                target_square = chess.square(col, 7 - row)
                move = chess.Move(self.selected_square, target_square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.selected_piece = None
                    self.selected_square = None

    def handle_computer_move(self):
        """
        Handles the computer player's move.
        """
        result = self.engine.play(self.board, chess.engine.Limit(time=0.2))
        self.board.push(result.move)

if __name__ == "__main__":
    game = ChessGame()
    game.play()

input("Press Enter to close...")