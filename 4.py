import pygame
import sys

cell_size = 68
board_size = 8
window_size_w = 1100
window_size_h = 700
board_offset = window_size_w - (cell_size * board_size) - 50
board_offset_y = 50
white = (227, 214, 200)
black = (0, 0, 0)
gray = (130, 163, 194)
fps = 60


class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_header = pygame.font.SysFont('Arial', 30)
        self.font_entry = pygame.font.SysFont('Arial', 24)
        self.font_label = pygame.font.SysFont('Arial', 22)

        self.username = ""
        self.password = ""
        self.active_input = None
        self.show_register_popup = False
        self.is_registration = False
        self.game_started = False
        self.error_message = ""
        self.error_timer = 0

        self.username_rect = pygame.Rect(window_size_w // 2 - 100, 230, 200, 30)
        self.password_rect = pygame.Rect(window_size_w // 2 - 100, 330, 200, 30)
        self.login_btn = pygame.Rect(window_size_w // 2 - 50, 410, 100, 40)

        self.popup_rect = pygame.Rect(window_size_w // 2 - 200, window_size_h // 2 - 100, 400, 200)
        self.yes_btn = pygame.Rect(window_size_w // 2 - 100, window_size_h // 2 + 20, 80, 40)
        self.no_btn = pygame.Rect(window_size_w // 2 + 20, window_size_h // 2 + 20, 80, 40)

    def caesar_cipher(self, text, shift=6):
        result = ""
        for char in text:
            if 'А' <= char <= 'Я' or 'а' <= char <= 'я':
                ascii_offset = ord('а') if char.islower() else ord('А')
                shifted = (ord(char) - ascii_offset + shift) % 32 + ascii_offset
                result += chr(shifted)
            elif 'A' <= char <= 'Z' or 'a' <= char <= 'z':
                ascii_offset = ord('a') if char.islower() else ord('A')
                shifted = (ord(char) - ascii_offset + shift) % 26 + ascii_offset
                result += chr(shifted)
            else:
                result += char
        return result

    def caesar_decipher(self, text, shift=6):
        return self.caesar_cipher(text, -shift)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_register_popup:
                if self.username_rect.collidepoint(event.pos):
                    self.active_input = "username"
                elif self.password_rect.collidepoint(event.pos):
                    self.active_input = "password"
                elif self.login_btn.collidepoint(event.pos):
                    if self.is_registration:
                        self.register_user()
                    else:
                        self.login()
                else:
                    self.active_input = None
            elif self.show_register_popup:
                if self.yes_btn.collidepoint(event.pos):
                    self.is_registration = True
                elif self.no_btn.collidepoint(event.pos):
                    self.show_register_popup = False
                    self.username = ""
                    self.password = ""

        elif event.type == pygame.KEYDOWN and self.active_input and not self.show_register_popup:
            if event.key == pygame.K_BACKSPACE:
                if self.active_input == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            elif event.key == pygame.K_RETURN:
                if self.is_registration:
                    self.register_user()
                else:
                    self.login()
            else:
                if self.active_input == "username":
                    self.username += event.unicode
                else:
                    self.password += event.unicode

    def login(self):
        if len(self.password) < 3:
            self.error_message = "Пароль должен содержать минимум 3 символа"
            self.error_timer = 1500
            return False

        try:
            with open('users.txt', 'r', encoding='utf-8') as file:
                for line in file:
                    encrypted_line = line.strip()
                    decrypted_line = self.caesar_decipher(encrypted_line)
                    stored_username, stored_password = decrypted_line.split(':')
                    if stored_username.strip() == self.username and stored_password.strip() == self.password:
                        self.game_started = True
                        return True
            self.show_register_popup = True
            return False
        except FileNotFoundError:
            with open('users.txt', 'w', encoding='utf-8') as file:
                pass
            self.show_register_popup = True
            return False

    def register_user(self):
        if len(self.password) < 3:
            self.error_message = "Пароль должен содержать минимум 3 символа"
            self.error_timer = 1500
            return False

        if self.username and self.password:
            user_data = f"{self.username}:{self.password}"
            encrypted_data = self.caesar_cipher(user_data)
            with open('users.txt', 'a', encoding='utf-8') as file:
                file.write(encrypted_data + '\n')
            return True
        return False

    def draw(self):
        if self.game_started:
            return

        header_text = "Регистрация" if self.is_registration else "Авторизация"
        header = self.font_header.render(header_text, True, black)
        header_rect = header.get_rect(center=(window_size_w // 2, 160))
        self.screen.blit(header, header_rect)

        username_label = self.font_label.render("Имя пользователя", True, black)
        self.screen.blit(username_label, (window_size_w // 2 - 100, 200))

        pygame.draw.rect(self.screen, gray if self.active_input == "username" else black,
                         self.username_rect, 2)
        username_text = self.font_entry.render(self.username, True, black)
        self.screen.blit(username_text, (self.username_rect.x + 5, self.username_rect.y + 5))

        password_label = self.font_label.render("Пароль", True, black)
        self.screen.blit(password_label, (window_size_w // 2 - 100, 300))

        pygame.draw.rect(self.screen, gray if self.active_input == "password" else black,
                         self.password_rect, 2)
        hidden_password = "*" * len(self.password)
        password_text = self.font_entry.render(hidden_password, True, black)
        self.screen.blit(password_text, (self.password_rect.x + 5, self.password_rect.y + 5))

        pygame.draw.rect(self.screen, gray, self.login_btn)
        button_text = "Сохранить" if self.is_registration else "Войти"
        login_text = self.font_label.render(button_text, True, black)
        login_text_rect = login_text.get_rect(center=self.login_btn.center)
        self.screen.blit(login_text, login_text_rect)

        if self.error_message and self.error_timer > 0:
            error_surface = self.font_label.render(self.error_message, True, (77, 19, 19))
            error_rect = error_surface.get_rect(center=(window_size_w // 2, 390))
            self.screen.blit(error_surface, error_rect)
            self.error_timer -= 1

        if self.show_register_popup:
            overlay = pygame.Surface((window_size_w, window_size_h))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))

            pygame.draw.rect(self.screen, white, self.popup_rect)
            pygame.draw.rect(self.screen, black, self.popup_rect, 2)

            popup_header = self.font_header.render("Зарегистрироваться", True, black)
            popup_header_rect = popup_header.get_rect(center=(window_size_w // 2, window_size_h // 2 - 70))
            self.screen.blit(popup_header, popup_header_rect)

            popup_text = self.font_label.render("Имя пользователя и пароль не найдены", True, black)
            popup_text2 = self.font_label.render("зарегистрироваться?", True, black)
            popup_text_rect = popup_text.get_rect(center=(window_size_w // 2, window_size_h // 2 - 20))
            popup_text_rect2 = popup_text2.get_rect(center=(window_size_w // 2, window_size_h // 2))
            self.screen.blit(popup_text, popup_text_rect)
            self.screen.blit(popup_text2, popup_text_rect2)

            pygame.draw.rect(self.screen, gray, self.yes_btn)
            pygame.draw.rect(self.screen, gray, self.no_btn)

            yes_text = self.font_label.render("Да", True, black)
            no_text = self.font_label.render("Нет", True, black)

            yes_text_rect = yes_text.get_rect(center=self.yes_btn.center)
            no_text_rect = no_text.get_rect(center=self.no_btn.center)

            self.screen.blit(yes_text, yes_text_rect)
            self.screen.blit(no_text, no_text_rect)


class Checker:
    def __init__(self, row, col, player, game):
        self.row = row
        self.col = col
        self.x = col * cell_size + board_offset + cell_size // 2 - game.white_checker_img.get_width() // 2
        self.y = row * cell_size + board_offset_y + cell_size // 2 - game.white_checker_img.get_height() // 2
        self.selected = False
        self.player = player
        self.game = game

        self.animating = False
        self.animation_path = []
        self.current_path_index = 0
        self.animation_progress = 0
        self.start_x = self.x
        self.start_y = self.y
        self.target_x = self.x
        self.target_y = self.y

    def get_path(self, start_row, start_col, end_row, end_col):
        path = [(start_row, start_col)]
        visited = set()
        found_path = []

        def find_jump_path(x, y, target_x, target_y, current_path):
            nonlocal found_path

            if found_path:
                return

            if (x, y) == (target_x, target_y):
                found_path = current_path.copy()
                return

            visited.add((x, y))

            for dx, dy in [(0, -2), (-2, 0), (0, 2), (2, 0)]:
                new_x = x + dx
                new_y = y + dy

                if (0 <= new_x < board_size and 0 <= new_y < board_size and
                        (new_x, new_y) not in visited):

                    middle_x = x + dx // 2
                    middle_y = y + dy // 2

                    if (self.game.board.board[middle_x][middle_y] is not None and
                            self.game.board.board[new_x][new_y] is None):

                        current_path.append((new_x, new_y))
                        find_jump_path(new_x, new_y, target_x, target_y, current_path)
                        if not found_path:
                            current_path.pop()

            visited.remove((x, y))

        if abs(start_row - end_row) + abs(start_col - end_col) == 1:
            path.append((end_row, end_col))
            return path

        find_jump_path(start_row, start_col, end_row, end_col, path)
        return found_path if found_path else path

    def can_jump(self, start_row, start_col, end_row, end_col):
        if self.game.board.board[end_row][end_col] is not None:
            return False

        if not (start_row == end_row or start_col == end_col):
            return False

        if start_row == end_row:
            mid_col = (start_col + end_col) // 2
            return (abs(start_col - end_col) == 2 and
                    self.game.board.board[start_row][mid_col] is not None)
        else:
            mid_row = (start_row + end_row) // 2
            return (abs(start_row - end_row) == 2 and
                    self.game.board.board[mid_row][start_col] is not None)

    def get_possible_jumps(self, row, col, visited=None):
        if visited is None:
            visited = set()

        possible_moves = set()

        def test_jump(x, y, target_x, target_y, visited_positions):
            if (x, y) not in visited_positions:
                visited_positions.add((x, y))

            if (x, y) != (row, col):
                possible_moves.add((x, y))

            for dx, dy in [(0, -2), (-2, 0), (0, 2), (2, 0)]:
                new_x = x + dx
                new_y = y + dy

                if 0 <= new_x < board_size and 0 <= new_y < board_size:
                    middle_x = x + dx // 2
                    middle_y = y + dy // 2

                    if (self.game.board.board[middle_x][middle_y] is not None and
                            self.game.board.board[new_x][new_y] is None and
                            (new_x, new_y) not in visited_positions):
                        test_jump(new_x, new_y, target_x, target_y, visited_positions)

        test_jump(row, col, None, None, visited)

        return possible_moves

    def get_possible_moves(self, row, col):
        moves = set()

        for d_row, d_col in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_row = row + d_row
            new_col = col + d_col

            if (0 <= new_row < board_size and
                    0 <= new_col < board_size and
                    self.game.board.board[new_row][new_col] is None):
                moves.add((new_row, new_col))

        jumps = self.get_possible_jumps(row, col)
        moves.update(jumps)

        return moves

    def start_animation(self, path):
        self.animating = True
        self.animation_path = path
        self.current_path_index = 0
        self.animation_progress = 0
        self.start_x = self.x
        self.start_y = self.y
        if path:
            next_row, next_col = path[0]
            self.target_x = next_col * cell_size + board_offset + cell_size // 2 - self.game.white_checker_img.get_width() // 2
            self.target_y = next_row * cell_size + board_offset_y + cell_size // 2 - self.game.white_checker_img.get_height() // 2

    def update_animation(self):
        if self.animating:
            self.animation_progress += 0.1
            if self.animation_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.current_path_index += 1

                if self.current_path_index < len(self.animation_path):
                    self.animation_progress = 0
                    self.start_x = self.x
                    self.start_y = self.y
                    next_row, next_col = self.animation_path[self.current_path_index]
                    self.target_x = next_col * cell_size + board_offset + cell_size // 2 - self.game.white_checker_img.get_width() // 2
                    self.target_y = next_row * cell_size + board_offset_y + cell_size // 2 - self.game.white_checker_img.get_height() // 2
                else:
                    self.animating = False
                    self.game.animating = False
                    if self.animation_path:
                        final_row, final_col = self.animation_path[-1]
                        self.row = final_row
                        self.col = final_col
            else:
                t = self.animation_progress
                t = t * t * (3 - 2 * t)
                self.x = self.start_x + (self.target_x - self.start_x) * t
                self.y = self.start_y + (self.target_y - self.start_y) * t

    def draw(self):
        self.update_animation()
        if self.player == 1:
            self.game.screen.blit(self.game.white_checker_img, (self.x, self.y))
        else:
            self.game.screen.blit(self.game.black_checker_img, (self.x, self.y))
        if self.selected:
            pygame.draw.rect(self.game.screen, (74, 75, 77),
                             (self.col * cell_size + board_offset,
                              self.row * cell_size + board_offset_y,
                              cell_size, cell_size), 2)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.x = col * cell_size + board_offset + cell_size // 2 - self.game.white_checker_img.get_width() // 2
        self.y = row * cell_size + board_offset_y + cell_size // 2 - self.game.white_checker_img.get_height() // 2


class Board:
    def __init__(self, game):
        self.game = game
        self.reset_board()
        self.weight_pole = [
            [7, 6, 5, 4, 3, 2, 1, 0],
            [8, 7, 6, 5, 4, 3, 2, 1],
            [9, 8, 7, 6, 5, 4, 3, 2],
            [10, 9, 8, 7, 6, 5, 4, 3],
            [11, 10, 9, 8, 7, 6, 5, 4],
            [14, 14, 14, 9, 8, 7, 6, 5],
            [14, 14, 14, 10, 9, 8, 7, 6],
            [14, 14, 14, 11, 10, 9, 8, 7]
        ]

    def reset_board(self):
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.init_board()
        self.last_move = None

    def init_board(self):
        initial_position = [
            [0, 0, 0, 0, 0, -1, -1, -1],
            [0, 0, 0, 0, 0, -1, -1, -1],
            [0, 0, 0, 0, 0, -1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0]
        ]

        for row in range(board_size):
            for col in range(board_size):
                if initial_position[row][col] != 0:
                    self.board[row][col] = Checker(row, col, initial_position[row][col], self.game)

    def check_winner(self):
        white_win = True
        for row in range(3):
            for col in range(5, 8):
                if not self.board[row][col] or self.board[row][col].player != 1:
                    white_win = False
                    break
            if not white_win:
                break

        black_win = True
        for row in range(5, 8):
            for col in range(3):
                if not self.board[row][col] or self.board[row][col].player != -1:
                    black_win = False
                    break
            if not black_win:
                break

        if white_win:
            return 1
        elif black_win:
            return -1
        return 0

    def draw(self, possible_moves):
        self.game.screen.fill(white)
        desk_rect = self.game.desk_img.get_rect()
        desk_rect.left = board_offset - 27
        desk_rect.top = board_offset_y - 27
        self.game.screen.blit(self.game.desk_img, desk_rect)

        for row in range(board_size):
            for col in range(board_size):
                pygame.draw.rect(self.game.screen, (197, 201, 209),
                                 (col * cell_size + board_offset,
                                  row * cell_size + board_offset_y,
                                  cell_size, cell_size), 2)
                if (row, col) in possible_moves:
                    pygame.draw.rect(self.game.screen, (6, 21, 51),
                                     (col * cell_size + board_offset,
                                      row * cell_size + board_offset_y,
                                      cell_size, cell_size), 2)

        for row in range(board_size):
            for col in range(board_size):
                if self.board[row][col]:
                    self.board[row][col].draw()

    def make_computer_move(self):
        if self.game.animating:
            return False

        def minimax(board, depth, alpha, beta, maximizing_player):
            winner = self.check_winner()
            if winner == -1:
                return float('inf'), None, None, None, None
            elif winner == 1:
                return float('-inf'), None, None, None, None

            if maximizing_player:
                for row in range(board_size):
                    for col in range(board_size):
                        if board[row][col] and board[row][col].player == -1:
                            possible_moves = board[row][col].get_possible_moves(row, col)

                            for new_row, new_col in possible_moves:
                                temp = board[new_row][new_col]
                                board[new_row][new_col] = board[row][col]
                                board[row][col] = None

                                if self.check_winner() == -1:
                                    board[row][col] = board[new_row][new_col]
                                    board[new_row][new_col] = temp
                                    return float('inf'), row, col, new_row, new_col

                                board[row][col] = board[new_row][new_col]
                                board[new_row][new_col] = temp

            if depth == 0:
                score = 0
                for row in range(board_size):
                    for col in range(board_size):
                        if board[row][col]:
                            if board[row][col].player == -1:
                                score += self.weight_pole[row][col]
                            else:
                                score -= self.weight_pole[7 - row][7 - col]
                return score, None, None, None, None

            if maximizing_player:
                max_eval = float('-inf')
                best_move = None
                best_start = None
                moves_found = False

                for row in range(board_size):
                    for col in range(board_size):
                        if board[row][col] and board[row][col].player == -1:
                            possible_moves = board[row][col].get_possible_moves(row, col)

                            if row >= 5 and col <= 2:
                                filtered_moves = set()
                                for new_row, new_col in possible_moves:
                                    if new_row >= 5 and new_col <= 2:
                                        filtered_moves.add((new_row, new_col))
                                possible_moves = filtered_moves

                            for new_row, new_col in possible_moves:
                                moves_found = True
                                temp = board[new_row][new_col]
                                board[new_row][new_col] = board[row][col]
                                board[row][col] = None

                                eval, _, _, _, _ = minimax(board, depth - 1, alpha, beta, False)

                                board[row][col] = board[new_row][new_col]
                                board[new_row][new_col] = temp

                                if eval > max_eval or best_move is None:
                                    max_eval = eval
                                    best_move = (new_row, new_col)
                                    best_start = (row, col)

                                alpha = max(alpha, eval)
                                if beta <= alpha:
                                    break

                if not moves_found or best_start is None or best_move is None:
                    score = 0
                    for row in range(board_size):
                        for col in range(board_size):
                            if board[row][col]:
                                if board[row][col].player == -1:
                                    score += self.weight_pole[row][col]
                                else:
                                    score -= self.weight_pole[7 - row][7 - col]
                    return score, None, None, None, None

                return max_eval, best_start[0], best_start[1], best_move[0], best_move[1]

            else:
                min_eval = float('inf')
                best_move = None
                best_start = None
                moves_found = False

                for row in range(board_size):
                    for col in range(board_size):
                        if board[row][col] and board[row][col].player == 1:
                            possible_moves = board[row][col].get_possible_moves(row, col)

                            for new_row, new_col in possible_moves:
                                moves_found = True
                                temp = board[new_row][new_col]
                                board[new_row][new_col] = board[row][col]
                                board[row][col] = None

                                eval, _, _, _, _ = minimax(board, depth - 1, alpha, beta, True)

                                board[row][col] = board[new_row][new_col]
                                board[new_row][new_col] = temp

                                if eval < min_eval or best_move is None:
                                    min_eval = eval
                                    best_move = (new_row, new_col)
                                    best_start = (row, col)

                                beta = min(beta, eval)
                                if beta <= alpha:
                                    break

                if not moves_found or best_start is None or best_move is None:
                    score = 0
                    for row in range(board_size):
                        for col in range(board_size):
                            if board[row][col]:
                                if board[row][col].player == -1:
                                    score += self.weight_pole[row][col]
                                else:
                                    score -= self.weight_pole[7 - row][7 - col]
                    return score, None, None, None, None

                return min_eval, best_start[0], best_start[1], best_move[0], best_move[1]

        eval_score, start_row, start_col, end_row, end_col = minimax(self.board, 3, float('-inf'), float('inf'), True)

        if None in (start_row, start_col, end_row, end_col):
            return False

        checker = self.board[start_row][start_col]
        if checker is None:
            return False

        path = checker.get_path(start_row, start_col, end_row, end_col)
        if not path:
            return False

        checker.start_animation(path)
        self.game.animating = True
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = checker
        checker.move(end_row, end_col)
        self.last_move = ((start_row, start_col), (end_row, end_col))
        return True


class Game:

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((window_size_w, window_size_h))
        pygame.display.set_caption("Халма")

        icon = pygame.image.load("new_icon.png")
        pygame.display.set_icon(icon)

        pygame.mixer.music.load('music_fon.mp3')
        pygame.mixer.music.set_volume(0.01)
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()

        self.desk_img = pygame.image.load("desk.jpg")
        self.white_checker_img = pygame.image.load("white.png")
        self.black_checker_img = pygame.image.load("black.png")

        self.font = pygame.font.Font(None, 36)

        self.board = Board(self)
        self.selected_checker = None
        self.possible_moves = set()
        self.current_player = 1
        self.error_message = ""
        self.error_timer = 0
        self.is_computer_player = True
        self.animating = False
        self.animation_progress = 0
        self.show_exit_confirmation = False
        self.show_winner_popup = False
        self.winner = 0
        self.login_screen = LoginScreen(self.screen)
        self.logged_in = False

        self.RULES_TEXT = """
                                                  Правила игры Халма:


   У каждого игрока по 9 шашек: белые внизу слева, черные вверху справа.

   Игроки ходят по очереди. Возможные ходы:
   - На одну клетку вправо, влево, вниз, вверх.
   - Прыгать через шашки на пустую клетку.

   За ход можно сделать несколько прыжков, как через свои, так и через
   шашки противника.

   Побеждает тот, кто первый переместит свои шашки в угол противника.

   Совет: используйте шашки как мостики для прыжков!

"""

        self.moves_history = []
        self.moves_font = pygame.font.SysFont('Arial', 22)
        self.col_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}
        self.row_to_number = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}

        self.moves_scroll_y = 0
        self.max_visible_moves = 15
        self.scroll_speed = 25
        self.moves_area_height = 550

    def add_move_to_history(self, start_pos, end_pos, player):
        start_notation = f"{self.col_to_letter[start_pos[1]]}{self.row_to_number[start_pos[0]]}"
        end_notation = f"{self.col_to_letter[end_pos[1]]}{self.row_to_number[end_pos[0]]}"
        move_text = f"{start_notation} → {end_notation}"
        self.moves_history.append((move_text, player))

    def handle_scroll(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            content_height = len(self.moves_history) * 35

            if content_height > self.moves_area_height:
                scroll_bar_rect = pygame.Rect(380, 60, 10, self.moves_area_height)

                if scroll_bar_rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - 60
                    scroll_ratio = relative_y / self.moves_area_height
                    self.moves_scroll_y = min(content_height - self.moves_area_height,
                                              max(0, int(content_height * scroll_ratio)))
                else:
                    if event.button == 4:
                        self.moves_scroll_y = max(0, self.moves_scroll_y - self.scroll_speed)
                    elif event.button == 5:
                        max_scroll = content_height - self.moves_area_height
                        self.moves_scroll_y = min(max_scroll, self.moves_scroll_y + self.scroll_speed)

    def draw_moves_history(self):
        white_header = self.font.render("Ходы белых", True, black)
        black_header = self.font.render("Ходы черных", True, black)
        self.screen.blit(white_header, (20, 20))
        self.screen.blit(black_header, (200, 20))

        total_height = max(self.moves_area_height, len(self.moves_history) * 35)
        moves_surface = pygame.Surface((350, total_height))
        moves_surface.fill(white)

        white_y = 0
        black_y = 0

        for move_text, player in self.moves_history:
            text = self.moves_font.render(move_text, True, black)
            if player == 1:
                moves_surface.blit(text, (0, white_y))
                white_y += 35
            else:
                moves_surface.blit(text, (180, black_y))
                black_y += 35

        content_height = max(white_y, black_y)

        if content_height > self.moves_area_height:
            self.moves_scroll_y = min(content_height - self.moves_area_height,
                                      max(0, self.moves_scroll_y))

        visible_rect = pygame.Rect(0, self.moves_scroll_y, 350, self.moves_area_height)
        self.screen.blit(moves_surface, (20, 60), visible_rect)

        if content_height > self.moves_area_height:
            scroll_height = max(30, self.moves_area_height * self.moves_area_height / content_height)
            scroll_pos = (self.moves_scroll_y * (self.moves_area_height - scroll_height) /
                          (content_height - self.moves_area_height))

            pygame.draw.rect(self.screen, (200, 200, 200),
                             (380, 60, 10, self.moves_area_height))

            pygame.draw.rect(self.screen, (150, 150, 150),
                             (380, 60 + scroll_pos, 10, scroll_height))

    def show_winner_dialog(self):
        overlay = pygame.Surface((window_size_w, window_size_h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        dialog_width = 400
        dialog_height = 200
        dialog_x = (window_size_w - dialog_width) // 2
        dialog_y = (window_size_h - dialog_height) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, white, dialog_rect)
        pygame.draw.rect(self.screen, black, dialog_rect, 2)

        winner_text = "Победили белые!" if self.winner == 1 else "Победили черные!"
        text = self.font.render(winner_text, True, black)
        text_rect = text.get_rect(center=(window_size_w // 2, dialog_y + 60))
        self.screen.blit(text, text_rect)

        ok_button = pygame.Rect(dialog_x + (dialog_width - 100) // 2, dialog_y + dialog_height - 60, 100, 40)
        pygame.draw.rect(self.screen, gray, ok_button)
        ok_text = self.font.render("OK", True, black)
        ok_rect = ok_text.get_rect(center=ok_button.center)
        self.screen.blit(ok_text, ok_rect)

        return ok_button

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, black)
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def show_rules(self):
        rules_running = True
        padding = 50
        line_spacing = 40
        max_width = window_size_w - (padding * 2)

        while rules_running:
            self.screen.fill(white)

            y = padding
            for line in self.RULES_TEXT.split('\n'):
                if line.strip():
                    if line.strip()[0].isdigit():
                        text_surface = self.font.render(line, True, black)
                        self.screen.blit(text_surface, (padding, y))
                        y += line_spacing
                    else:
                        wrapped_lines = self.wrap_text(line, self.font, max_width)
                        for wrapped_line in wrapped_lines:
                            text_surface = self.font.render(wrapped_line, True, black)
                            self.screen.blit(text_surface, (padding, y))
                            y += line_spacing

            back_button = pygame.Rect(window_size_w // 2 - 50, window_size_h - 100, 100, 40)
            pygame.draw.rect(self.screen, gray, back_button)
            back_text = self.font.render("Назад", True, black)
            back_text_rect = back_text.get_rect(center=back_button.center)
            self.screen.blit(back_text, back_text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        rules_running = False

    def show_menu(self):
        menu_running = True
        while menu_running:
            self.screen.fill(white)

            start_button = pygame.Rect(window_size_w // 2 - 100, window_size_h // 2 - 50, 200, 40)
            rules_button = pygame.Rect(window_size_w // 2 - 100, window_size_h // 2 + 10, 200, 40)

            pygame.draw.rect(self.screen, gray, start_button)
            pygame.draw.rect(self.screen, gray, rules_button)

            start_text = self.font.render("Начать игру", True, black)
            rules_text = self.font.render("Правила игры", True, black)

            start_text_rect = start_text.get_rect(center=start_button.center)
            rules_text_rect = rules_text.get_rect(center=rules_button.center)

            self.screen.blit(start_text, start_text_rect)
            self.screen.blit(rules_text, rules_text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        menu_running = False
                        while not self.logged_in:
                            self.screen.fill(white)
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.mixer.music.stop()
                                    pygame.quit()
                                    sys.exit()
                                self.login_screen.handle_event(event)
                                if event.type == pygame.MOUSEBUTTONDOWN and self.login_screen.login_btn.collidepoint(
                                        event.pos):
                                    if self.login_screen.login():
                                        self.logged_in = True

                            self.login_screen.draw()
                            pygame.display.flip()

                        return self.show_opponent_selection()
                    if rules_button.collidepoint(event.pos):
                        self.show_rules()

    def reset_game_state(self):
        self.board.reset_board()
        self.selected_checker = None
        self.possible_moves = set()
        self.current_player = 1
        self.error_message = ""
        self.error_timer = 0
        self.animating = False
        self.animation_progress = 0
        self.show_winner_popup = False
        self.winner = 0
        self.moves_history = []
        self.moves_scroll_y = 0

    def show_opponent_selection(self):
        self.is_computer_player = True
        self.reset_game_state()
        return True

    def show_exit_dialog(self):
        overlay = pygame.Surface((window_size_w, window_size_h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        dialog_width = 300
        dialog_height = 150
        dialog_x = (window_size_w - dialog_width) // 2
        dialog_y = (window_size_h - dialog_height) // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, white, dialog_rect)
        pygame.draw.rect(self.screen, black, dialog_rect, 2)

        text = self.font.render("Хотите закрыть игру?", True, black)
        text_rect = text.get_rect(center=(window_size_w // 2, dialog_y + 60))
        self.screen.blit(text, text_rect)

        yes_button = pygame.Rect(dialog_x + 50, dialog_y + 100, 80, 30)
        no_button = pygame.Rect(dialog_x + 170, dialog_y + 100, 80, 30)

        pygame.draw.rect(self.screen, gray, yes_button)
        pygame.draw.rect(self.screen, gray, no_button)

        yes_text = self.font.render("Да", True, black)
        no_text = self.font.render("Нет", True, black)

        yes_rect = yes_text.get_rect(center=yes_button.center)
        no_rect = no_text.get_rect(center=no_button.center)

        self.screen.blit(yes_text, yes_rect)
        self.screen.blit(no_text, no_rect)

        return yes_button, no_button

    def main_game(self):
        exit_button = pygame.Rect(20, window_size_h - 40, 40, 30)

        while True:
            self.clock.tick(fps)

            winner = self.board.check_winner()
            if winner != 0:
                self.winner = winner
                self.show_winner_popup = True

            if self.show_winner_popup:
                ok_button = self.show_winner_dialog()
                pygame.display.flip()

                waiting_for_ok = True
                while waiting_for_ok:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if ok_button.collidepoint(event.pos):
                                self.reset_game_state()
                                self.show_exit_confirmation = False
                                return
                        elif event.type == pygame.QUIT:
                            pygame.mixer.music.stop()
                            pygame.quit()
                            sys.exit()

            if self.current_player == -1 and self.is_computer_player and not self.animating:
                if self.board.make_computer_move():
                    last_move = self.board.last_move
                    if last_move:
                        self.add_move_to_history(last_move[0], last_move[1], -1)
                    self.current_player = 1
                    self.error_message = ""

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()

                self.handle_scroll(event)

                if event.type == pygame.MOUSEBUTTONDOWN and not self.animating:
                    mouse_pos = event.pos

                    if exit_button.collidepoint(mouse_pos):
                        self.show_exit_confirmation = True
                    elif self.show_exit_confirmation:
                        yes_button, no_button = self.show_exit_dialog()
                        if yes_button.collidepoint(mouse_pos):
                            self.reset_game_state()
                            self.show_exit_confirmation = False
                            return
                        elif no_button.collidepoint(mouse_pos):
                            self.show_exit_confirmation = False
                    else:
                        if self.current_player == 1 or not self.is_computer_player:
                            col = (mouse_pos[0] - board_offset) // cell_size
                            row = (mouse_pos[1] - board_offset_y) // cell_size

                            if 0 <= row < board_size and 0 <= col < board_size:
                                self.handle_click(row, col)

            self.screen.fill(white)
            self.board.draw(self.possible_moves)
            self.draw_moves_history()
            self.draw_interface(exit_button)
            if self.show_exit_confirmation:
                self.show_exit_dialog()
            pygame.display.flip()

    def handle_click(self, row, col):
        if self.selected_checker:
            can_move = False

            if (self.board.board[row][col] is None and
                    ((abs(self.selected_checker.row - row) == 1 and self.selected_checker.col == col) or
                     (abs(self.selected_checker.col - col) == 1 and self.selected_checker.row == row))):
                can_move = True
            elif (row, col) in self.possible_moves:
                can_move = True

            if can_move:
                start_pos = (self.selected_checker.row, self.selected_checker.col)

                path = self.selected_checker.get_path(self.selected_checker.row, self.selected_checker.col, row, col)
                self.selected_checker.start_animation(path)
                self.animating = True

                self.board.board[self.selected_checker.row][self.selected_checker.col] = None
                self.board.board[row][col] = self.selected_checker

                self.add_move_to_history(start_pos, (row, col), self.current_player)

                self.current_player = -self.current_player
                self.error_message = ""
            else:
                self.error_message = "Такой ход сейчас не доступен!"
                self.error_timer = 300

            self.selected_checker.selected = False
            self.selected_checker = None
            self.possible_moves = set()
        elif self.board.board[row][col] and self.board.board[row][col].player == self.current_player:
            self.selected_checker = self.board.board[row][col]
            self.selected_checker.selected = True
            self.possible_moves = self.selected_checker.get_possible_moves(row, col)

    def draw_interface(self, exit_button):
        pygame.draw.rect(self.screen, gray, exit_button)
        exit_text = self.font.render("<=", True, black)
        exit_text_rect = exit_text.get_rect(center=exit_button.center)
        self.screen.blit(exit_text, exit_text_rect)

        player_text = f"Ходят: {'белые' if self.current_player == 1 else 'черные'}"
        text_surface = self.font.render(player_text, True, black)
        text_rect = text_surface.get_rect(center=(window_size_w - 320, window_size_h - 30))
        self.screen.blit(text_surface, text_rect)

        if self.error_message and self.error_timer > 0:
            error_surface = self.font.render(self.error_message, True, (77, 19, 19))
            error_rect = error_surface.get_rect(center=(window_size_w - 320, window_size_h - 60))
            self.screen.blit(error_surface, error_rect)
            self.error_timer -= 1


def main():
    game = Game()
    while True:
        if game.show_menu():
            game.main_game()


if __name__ == "__main__":
    main()