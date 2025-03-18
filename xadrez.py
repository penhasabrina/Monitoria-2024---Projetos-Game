import tkinter as tk
from tkinter import messagebox

class JogoXadrez:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Jogo de Xadrez")

        # Tamanho do tabuleiro e célula
        self.board_size = 8
        self.cell_size = 80

        self.canvas = tk.Canvas(self.window, width=self.board_size * self.cell_size,
                                height=self.board_size * self.cell_size)
        self.canvas.pack()

        # Criação do tabuleiro
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = 'yellow'  # Amarelo começa (representando o branco)
        self.selected_piece = None
        self.valid_moves = []
        self.king_positions = {'yellow': (7, 4), 'black': (0, 4)}  # Posições dos reis
        self.castling_rights = {'yellow': {'short': True, 'long': True}, 'black': {'short': True, 'long': True}}
        self.en_passant = None  # Guardar a posição da jogada "en passant"

        self.create_board()
        self.setup_pieces()

        self.canvas.bind("<Button-1>", self.click)  # Bind para cliques no tabuleiro

    def create_board(self):
        # Criação do tabuleiro de xadrez (8x8)
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                             (col + 1) * self.cell_size, (row + 1) * self.cell_size, fill=color)

    def setup_pieces(self):
        # Configuração inicial das peças
        for col in range(self.board_size):
            self.board[1][col] = ('black', 'pawn')
            self.board[6][col] = ('yellow', 'pawn')

        self.setup_major_pieces(0, 'black')
        self.setup_major_pieces(7, 'yellow')

        self.draw_pieces()

    def setup_major_pieces(self, row, color):
        # Peças maiores: Torres, Cavalos, Bispos, Rainha e Rei
        self.board[row][0] = self.board[row][7] = (color, 'rook')
        self.board[row][1] = self.board[row][6] = (color, 'knight')
        self.board[row][2] = self.board[row][5] = (color, 'bishop')
        self.board[row][3] = (color, 'queen')
        self.board[row][4] = (color, 'king')

    def draw_pieces(self):
        self.canvas.delete("pieces")  # Apagar todas as peças desenhadas
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    self.draw_piece(row, col, piece)

    def draw_piece(self, row, col, piece):
        x1, y1 = col * self.cell_size, row * self.cell_size
        x2, y2 = (col + 1) * self.cell_size, (row + 1) * self.cell_size
        color, piece_type = piece
        piece_symbol = self.get_piece_symbol(piece_type)
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=piece_symbol,
                                font=("Arial", 36), fill=color, tags="pieces")

    def get_piece_symbol(self, piece_type):
        # Símbolos Unicode para peças de xadrez
        symbols = {
            'king': '♔' if self.turn == 'yellow' else '♚',
            'queen': '♕' if self.turn == 'yellow' else '♛',
            'rook': '♖' if self.turn == 'yellow' else '♜',
            'bishop': '♗' if self.turn == 'yellow' else '♝',
            'knight': '♘' if self.turn == 'yellow' else '♞',
            'pawn': '♙' if self.turn == 'yellow' else '♟'
        }
        return symbols[piece_type]

    def click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return

        if self.selected_piece:
            if (row, col) in self.valid_moves:
                self.move_piece(self.selected_piece[0], self.selected_piece[1], row, col)
                self.switch_turn()
            self.selected_piece = None
            self.valid_moves = []
            self.clear_highlight()
        else:
            piece = self.board[row][col]
            if piece and piece[0] == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
                self.highlight_moves(self.valid_moves)

    def get_valid_moves(self, row, col):
        # Implementação básica para obtenção de movimentos válidos
        piece = self.board[row][col]
        piece_type = piece[1]
        color = piece[0]

        moves = []
        if piece_type == 'pawn':
            moves = self.get_pawn_moves(row, col, color)
        elif piece_type == 'rook':
            moves = self.get_rook_moves(row, col, color)
        elif piece_type == 'knight':
            moves = self.get_knight_moves(row, col, color)
        elif piece_type == 'bishop':
            moves = self.get_bishop_moves(row, col, color)
        elif piece_type == 'queen':
            moves = self.get_queen_moves(row, col, color)
        elif piece_type == 'king':
            moves = self.get_king_moves(row, col, color)

        return moves

    def get_pawn_moves(self, row, col, color):
        # Movimentos do peão
        moves = []
        direction = -1 if color == 'yellow' else 1

        # Movimento normal
        if self.board[row + direction][col] is None:
            moves.append((row + direction, col))
            if (row == 6 and color == 'yellow') or (row == 1 and color == 'black'):
                if self.board[row + 2 * direction][col] is None:
                    moves.append((row + 2 * direction, col))

        # Captura diagonal
        for dcol in [-1, 1]:
            new_col = col + dcol
            if 0 <= new_col < self.board_size:
                if self.board[row + direction][new_col] and self.board[row + direction][new_col][0] != color:
                    moves.append((row + direction, new_col))

        # En passant
        if self.en_passant:
            if row == (3 if color == 'yellow' else 4) and abs(col - self.en_passant[1]) == 1:
                moves.append((row + direction, self.en_passant[1]))

        return moves

    def get_rook_moves(self, row, col, color):
        # Movimentos da torre (horizontal e vertical)
        return self.get_straight_line_moves(row, col, color)

    def get_straight_line_moves(self, row, col, color):
        # Movimentos em linha reta (horizontal e vertical)
        moves = []

        # Movimentos verticais (para cima e para baixo)
        for i in [-1, 1]:
            r = row + i
            while 0 <= r < self.board_size:
                if self.board[r][col] is None:  # Se a casa está vazia, pode se mover
                    moves.append((r, col))
                elif self.board[r][col][0] != color:  # Se for uma peça adversária, pode capturar
                    moves.append((r, col))
                    break
                else:  # Se for uma peça aliada, bloqueia o movimento
                    break
                r += i

        # Movimentos horizontais (para a esquerda e direita)
        for i in [-1, 1]:
            c = col + i
            while 0 <= c < self.board_size:
                if self.board[row][c] is None:  # Se a casa está vazia, pode se mover
                    moves.append((row, c))
                elif self.board[row][c][0] != color:  # Se for uma peça adversária, pode capturar
                    moves.append((row, c))
                    break
                else:  # Se for uma peça aliada, bloqueia o movimento
                    break
                c += i

        return moves

    def get_knight_moves(self, row, col, color):
        # Movimentos do cavalo (em "L")
        moves = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for drow, dcol in knight_moves:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                moves.append((new_row, new_col))
        return moves

    def get_bishop_moves(self, row, col, color):
        # Movimentos do bispo (diagonal)
        return self.get_diagonal_moves(row, col, color)

    def get_diagonal_moves(self, row, col, color):
        # Movimentos em diagonal (para as quatro direções diagonais)
        moves = []

        # Verificar as quatro diagonais: (-1,-1), (-1,+1), (+1,-1), (+1,+1)
        for d_row, d_col in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row + d_row, col + d_col
            while 0 <= r < self.board_size and 0 <= c < self.board_size:
                if self.board[r][c] is None:  # Se a casa está vazia, pode se mover
                    moves.append((r, c))
                elif self.board[r][c][0] != color:  # Se for uma peça adversária, pode capturar
                    moves.append((r, c))
                    break
                else:  # Se for uma peça aliada, bloqueia o movimento
                    break
                r += d_row
                c += d_col

        return moves

    def get_queen_moves(self, row, col, color):
        # Movimentos da rainha (combina torre e bispo)
        return self.get_straight_line_moves(row, col, color) + self.get_diagonal_moves(row, col, color)

    def get_king_moves(self, row, col, color):
        # Movimentos do rei (um quadrado em qualquer direção) e roque
        moves = []
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow != 0 or dcol != 0:
                    new_row, new_col = row + drow, col + dcol
                    if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                        moves.append((new_row, new_col))

        # Roque curto e longo
        if self.castling_rights[color]['short']:
            moves.append((row, col + 2))
        if self.castling_rights[color]['long']:
            moves.append((row, col - 2))

        return moves

    def highlight_moves(self, moves):
        for row, col in moves:
            self.canvas.create_rectangle(col * self.cell_size, row * self.cell_size,
                                         (col + 1) * self.cell_size, (row + 1) * self.cell_size,
                                         outline='yellow', width=3, tags="highlight")

    def clear_highlight(self):
        self.canvas.delete("highlight")

    def move_piece(self, start_row, start_col, end_row, end_col):
        # Movimentação da peça e promoções
        piece = self.board[start_row][start_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Promoção de peão
        if piece[1] == 'pawn' and (end_row == 0 or end_row == 7):
            self.board[end_row][end_col] = (piece[0], 'queen')

        # Roque
        if piece[1] == 'king' and abs(end_col - start_col) == 2:
            if end_col == 6:  # Roque curto
                self.board[end_row][5] = self.board[end_row][7]
                self.board[end_row][7] = None
            elif end_col == 2:  # Roque longo
                self.board[end_row][3] = self.board[end_row][0]
                self.board[end_row][0] = None

        # En passant
        if piece[1] == 'pawn' and (end_row, end_col) == self.en_passant:
            self.board[start_row][end_col] = None

        # Atualização de roque e en passant
        self.update_castling_rights(piece, start_row, start_col)
        self.update_en_passant(piece, start_row, end_row, start_col, end_col)

        self.draw_pieces()

    def update_castling_rights(self, piece, start_row, start_col):
        # Se o rei ou a torre moverem, perdemos os direitos de roque
        if piece[1] == 'king':
            self.castling_rights[piece[0]]['short'] = False
            self.castling_rights[piece[0]]['long'] = False
        elif piece[1] == 'rook':
            if start_col == 0:
                self.castling_rights[piece[0]]['long'] = False
            elif start_col == 7:
                self.castling_rights[piece[0]]['short'] = False

    def update_en_passant(self, piece, start_row, end_row, start_col, end_col):
        # Atualiza a jogada en passant após movimento do peão
        if piece[1] == 'pawn' and abs(end_row - start_row) == 2:
            self.en_passant = (start_row + (end_row - start_row) // 2, start_col)
        else:
            self.en_passant = None

    def switch_turn(self):
        self.turn = 'yellow' if self.turn == 'black' else 'black'
        #messagebox.showinfo("Vez do jogador", f"Agora é a vez das peças {self.turn}.")
        self.check_checkmate()

    def check_checkmate(self):
        king_position = self.find_king(self.turn)
        if self.is_in_check(king_position, self.turn):
            if self.has_legal_moves(self.turn):
                messagebox.showinfo("Xeque", f"{self.turn.capitalize()} está em xeque!")
            else:
                messagebox.showinfo("Xeque-Mate", f"{self.turn.capitalize()} está em xeque-mate!")
                self.window.quit()
        else:
            if not self.has_legal_moves(self.turn):
                messagebox.showinfo("Empate", "Jogo empatado por afogamento!")
                self.window.quit()

    def find_king(self, color):
        # Encontra a posição do rei de uma determinada cor
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece[0] == color and piece[1] == 'king':
                    return (row, col)
        return None

    def is_in_check(self, king_position, color):
        # Verifica se o rei está em xeque (se alguma peça adversária pode capturar o rei)
        opponent_color = 'black' if color == 'yellow' else 'yellow'
        king_row, king_col = king_position

        # Verifica todos os movimentos possíveis do oponente para ver se alguma pode capturar o rei
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece[0] == opponent_color:
                    valid_moves = self.get_valid_moves(row, col, piece)
                    if (king_row, king_col) in valid_moves:
                        return True
        return False

    def has_legal_moves(self, color):
        # Verifica se o jogador ainda tem algum movimento legal (se não tiver, é xeque-mate ou empate)
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece[0] == color:
                    valid_moves = self.get_valid_moves(row, col, piece)
                    for move in valid_moves:
                        # Tentar o movimento e ver se ainda está em xeque
                        temp_board = [row.copy() for row in self.board]
                        self.board[move[0]][move[1]] = piece
                        self.board[row][col] = None
                        king_position = self.find_king(color)
                        if not self.is_in_check(king_position, color):
                            self.board = temp_board  # Reverte o tabuleiro para o estado original
                            return True
                        self.board = temp_board  # Reverte o tabuleiro para o estado original
        return False

if __name__ == "__main__":
    jogo = JogoXadrez()
    jogo.window.mainloop()
