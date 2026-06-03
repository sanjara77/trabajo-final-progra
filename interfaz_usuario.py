"""
interfaz_usuario.py
Controlador/lógica del juego Dots and Boxes.
Compatible con Python 3.14 en Windows usando winsound para música.
"""

import os
import random

try:
    import winsound
except ImportError:
    winsound = None

from interfaz_grafica import DotsAndBoxesGUI


class DotsAndBoxesController:
    def __init__(self, size=4, player_time=60):
        if size < 2:
            raise ValueError("El tamaño del tablero debe ser mínimo 2.")

        self.size = size
        self.player_time = player_time
        self.gui = None
        self.timer_id = None
        self.game_finished = False
        self.mode = "2_jugadores"
        self.difficulty = None
        self.ai_player = "Jugador 2"
        self.current_music = None
        self.reset_state()

    def play_music(self, filename):
        if winsound is None:
            print("Aviso: winsound no está disponible. El juego funcionará sin música.")
            return

        if self.current_music == filename:
            return

        music_path = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(music_path):
            print(f"Aviso: no se encontró el archivo de música: {filename}")
            return

        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
            winsound.PlaySound(
                music_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP
            )
            self.current_music = filename
        except RuntimeError as error:
            print(f"Aviso: no se pudo reproducir {filename}. Error: {error}")

    def stop_music(self):
        if winsound is not None:
            winsound.PlaySound(None, winsound.SND_PURGE)
        self.current_music = None

    def reset_state(self):
        self.current_player = "Jugador 1"
        self.scores = {
            "Jugador 1": 0,
            "Jugador 2": 0
        }

        self.player_times = {
            "Jugador 1": self.player_time,
            "Jugador 2": self.player_time
        }

        self.horizontal_lines = set()
        self.vertical_lines = set()
        self.boxes = [
            [None for _ in range(self.size - 1)]
            for _ in range(self.size - 1)
        ]

        self.game_finished = False

    def start(self):
        self.gui = DotsAndBoxesGUI(self, size=self.size)
        self.gui.run()

    def configure_game(self, mode, difficulty=None):
        self.stop_timer()
        self.mode = mode
        self.difficulty = difficulty
        self.reset_state()

    def reset_game(self):
        self.stop_timer()
        self.reset_state()
        self.gui.draw_board()
        self.start_timer()
        self.try_ai_turn()

    def start_timer(self):
        if self.game_finished:
            return

        self.stop_timer()
        self.gui.update_timers()
        self.timer_id = self.gui.root.after(1000, self.countdown)

    def stop_timer(self):
        if self.gui and self.timer_id is not None:
            self.gui.root.after_cancel(self.timer_id)
            self.timer_id = None

    def countdown(self):
        if self.game_finished:
            return

        self.player_times[self.current_player] -= 1
        self.gui.update_timers()

        if self.player_times[self.current_player] <= 0:
            self.player_times[self.current_player] = 0
            self.gui.update_timers()
            self.handle_time_out()
            return

        self.timer_id = self.gui.root.after(1000, self.countdown)

    def handle_time_out(self):
        self.stop_timer()
        self.game_finished = True

        loser = self.current_player
        winner = "Jugador 2" if loser == "Jugador 1" else "Jugador 1"

        self.gui.show_message(
            "Tiempo agotado",
            f"Se acabó el tiempo de {loser}. Gana {winner}."
        )

    def is_ai_turn(self):
        return self.mode == "ia" and self.current_player == self.ai_player and not self.game_finished

    def try_ai_turn(self):
        if self.is_ai_turn():
            self.gui.root.after(600, self.play_ai_turn)

    def play_ai_turn(self):
        if not self.is_ai_turn():
            return

        move = self.choose_ai_move()

        if move is not None:
            self.play_turn(move)

    def play_turn(self, move):
        if self.game_finished or not self.is_valid_move(move):
            return

        self.stop_timer()
        self.add_line(move)
        completed_boxes = self.check_completed_boxes(move)

        if completed_boxes == 0:
            self.change_player()
        else:
            self.scores[self.current_player] += completed_boxes

        self.gui.draw_board()

        if self.is_game_over():
            self.game_finished = True
            self.show_winner()
            return

        self.start_timer()
        self.try_ai_turn()

    def choose_ai_move(self):
        moves = self.get_available_moves()

        if not moves:
            return None

        scoring_moves = [move for move in moves if self.count_completed_boxes_if_move(move) > 0]
        safe_moves = [move for move in moves if not self.gives_box_to_opponent(move)]

        if self.difficulty == "facil":
            if scoring_moves and random.random() < 0.45:
                return random.choice(scoring_moves)
            return random.choice(moves)

        if self.difficulty == "normal":
            if scoring_moves:
                return max(scoring_moves, key=self.count_completed_boxes_if_move)
            if safe_moves:
                return random.choice(safe_moves)
            return random.choice(moves)

        if self.difficulty == "dificil":
            if scoring_moves:
                return max(scoring_moves, key=self.count_completed_boxes_if_move)
            if safe_moves:
                return self.choose_best_safe_move(safe_moves)
            return min(moves, key=self.count_danger_created_by_move)

        return random.choice(moves)

    def choose_best_safe_move(self, safe_moves):
        return min(safe_moves, key=self.count_danger_created_by_move)

    def get_available_moves(self):
        moves = []

        for row in range(self.size):
            for col in range(self.size - 1):
                move = ("H", row, col)
                if move not in self.horizontal_lines:
                    moves.append(move)

        for row in range(self.size - 1):
            for col in range(self.size):
                move = ("V", row, col)
                if move not in self.vertical_lines:
                    moves.append(move)

        return moves

    def count_completed_boxes_if_move(self, move):
        line_type, row, col = move
        completed = 0

        for box_row, box_col in self.get_adjacent_boxes(line_type, row, col):
            if self.boxes[box_row][box_col] is None and self.is_box_complete_after_move(box_row, box_col, move):
                completed += 1

        return completed

    def gives_box_to_opponent(self, move):
        if self.count_completed_boxes_if_move(move) > 0:
            return False

        return self.count_danger_created_by_move(move) > 0

    def count_danger_created_by_move(self, move):
        line_type, row, col = move
        danger = 0

        for box_row, box_col in self.get_adjacent_boxes(line_type, row, col):
            if self.boxes[box_row][box_col] is None:
                sides_after_move = self.count_box_sides_after_move(box_row, box_col, move)
                if sides_after_move == 3:
                    danger += 1

        return danger

    def count_box_sides_after_move(self, row, col, move):
        sides = 0

        box_lines = [
            ("H", row, col),
            ("H", row + 1, col),
            ("V", row, col),
            ("V", row, col + 1)
        ]

        for line in box_lines:
            if line == move or self.line_exists(line):
                sides += 1

        return sides

    def is_box_complete_after_move(self, row, col, move):
        return self.count_box_sides_after_move(row, col, move) == 4

    def is_valid_move(self, move):
        line_type, row, col = move

        if line_type == "H":
            return 0 <= row < self.size and 0 <= col < self.size - 1 and move not in self.horizontal_lines

        if line_type == "V":
            return 0 <= row < self.size - 1 and 0 <= col < self.size and move not in self.vertical_lines

        return False

    def line_exists(self, move):
        if move[0] == "H":
            return move in self.horizontal_lines
        return move in self.vertical_lines

    def add_line(self, move):
        if move[0] == "H":
            self.horizontal_lines.add(move)
        else:
            self.vertical_lines.add(move)

    def check_completed_boxes(self, move):
        line_type, row, col = move
        completed = 0

        for box_row, box_col in self.get_adjacent_boxes(line_type, row, col):
            if self.boxes[box_row][box_col] is None and self.is_box_complete(box_row, box_col):
                self.boxes[box_row][box_col] = self.current_player
                completed += 1

        return completed

    def get_adjacent_boxes(self, line_type, row, col):
        boxes = []

        if line_type == "H":
            if row > 0:
                boxes.append((row - 1, col))
            if row < self.size - 1:
                boxes.append((row, col))

        elif line_type == "V":
            if col > 0:
                boxes.append((row, col - 1))
            if col < self.size - 1:
                boxes.append((row, col))

        return boxes

    def is_box_complete(self, row, col):
        top = ("H", row, col) in self.horizontal_lines
        bottom = ("H", row + 1, col) in self.horizontal_lines
        left = ("V", row, col) in self.vertical_lines
        right = ("V", row, col + 1) in self.vertical_lines

        return top and bottom and left and right

    def change_player(self):
        self.current_player = "Jugador 2" if self.current_player == "Jugador 1" else "Jugador 1"

    def is_game_over(self):
        total_boxes = (self.size - 1) ** 2
        return sum(self.scores.values()) == total_boxes

    def show_winner(self):
        self.stop_timer()

        player_1_score = self.scores["Jugador 1"]
        player_2_score = self.scores["Jugador 2"]

        if player_1_score > player_2_score:
            message = "Ganó Jugador 1."
        elif player_2_score > player_1_score:
            message = "Ganó Jugador 2."
        else:
            message = "Empate."

        self.gui.show_message("Fin del juego", message)
