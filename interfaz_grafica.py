
import tkinter as tk
from tkinter import messagebox


class DotsAndBoxesGUI:
    def __init__(self, controller, size=4, cell_size=90, padding=45):
        self.controller = controller
        self.size = size
        self.cell_size = cell_size
        self.padding = padding
        self.dot_radius = 6

        self.colors = {
            "background": "#050523",
            "panel": "#0B0B3B",
            "pacman_yellow": "#FFD700",
            "blue_wall": "#1E90FF",
            "pink": "#FF69B4",
            "cyan": "#00FFFF",
            "orange": "#FFB000",
            "white": "#FFFFFF",
            "line": "#FFD700",
            "player_1_box": "#1E90FF",
            "player_2_box": "#FF69B4",
        }

        self.canvas_size = padding * 2 + cell_size * (size - 1)

        self.root = tk.Tk()
        self.root.title("Dots and Boxes")
        self.root.configure(bg=self.colors["background"])

        self.menu_frame = tk.Frame(self.root, bg=self.colors["background"])
        self.game_frame = tk.Frame(self.root, bg=self.colors["background"])

        self.create_menu()
        self.create_game_screen()

        self.show_menu()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def create_menu(self):
        title = tk.Label(
            self.menu_frame,
            text="Dots and Boxes",
            font=("Arial", 26, "bold"),
            bg=self.colors["background"],
            fg=self.colors["pacman_yellow"]
        )
        title.pack(pady=20)

        mode_label = tk.Label(
            self.menu_frame,
            text="Selecciona el modo de juego:",
            font=("Arial", 13),
            bg=self.colors["background"],
            fg=self.colors["white"]
        )
        mode_label.pack(pady=10)

        self.create_menu_button(
            "Dos jugadores",
            lambda: self.start_selected_game("2_jugadores")
        ).pack(pady=8)

        difficulty_label = tk.Label(
            self.menu_frame,
            text="Un jugador:",
            font=("Arial", 13, "bold"),
            bg=self.colors["background"],
            fg=self.colors["pacman_yellow"]
        )
        difficulty_label.pack(pady=(20, 5))

        self.create_menu_button(
            "Fácil",
            lambda: self.start_selected_game("ia", "facil")
        ).pack(pady=5)

        self.create_menu_button(
            "Normal",
            lambda: self.start_selected_game("ia", "normal")
        ).pack(pady=5)

        self.create_menu_button(
            "Difícil",
            lambda: self.start_selected_game("ia", "dificil")
        ).pack(pady=5)

    def create_menu_button(self, text, command):
        return tk.Button(
            self.menu_frame,
            text=text,
            width=25,
            command=command,
            font=("Arial", 11, "bold"),
            bg=self.colors["blue_wall"],
            fg=self.colors["white"],
            activebackground=self.colors["pacman_yellow"],
            activeforeground=self.colors["background"],
            relief="raised",
            bd=3
        )

    def create_game_screen(self):
        self.info_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 14, "bold"),
            bg=self.colors["background"],
            fg=self.colors["pacman_yellow"]
        )
        self.info_label.pack(pady=5)

        self.timer_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 16, "bold"),
            bg=self.colors["background"],
            fg=self.colors["cyan"]
        )
        self.timer_label.pack(pady=5)

        self.canvas = tk.Canvas(
            self.game_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.colors["panel"],
            highlightthickness=3,
            highlightbackground=self.colors["blue_wall"]
        )
        self.canvas.pack(padx=10, pady=10)

        buttons_frame = tk.Frame(self.game_frame, bg=self.colors["background"])
        buttons_frame.pack(pady=10)

        self.reset_button = tk.Button(
            buttons_frame,
            text="Reiniciar partida",
            command=self.controller.reset_game,
            bg=self.colors["blue_wall"],
            fg=self.colors["white"],
            activebackground=self.colors["pacman_yellow"],
            activeforeground=self.colors["background"],
            font=("Arial", 10, "bold")
        )
        self.reset_button.grid(row=0, column=0, padx=5)

        self.menu_button = tk.Button(
            buttons_frame,
            text="Volver al menú",
            command=self.back_to_menu,
            bg=self.colors["blue_wall"],
            fg=self.colors["white"],
            activebackground=self.colors["pacman_yellow"],
            activeforeground=self.colors["background"],
            font=("Arial", 10, "bold")
        )
        self.menu_button.grid(row=0, column=1, padx=5)

        self.canvas.bind("<Button-1>", self.handle_click)

    def show_menu(self):
        self.controller.stop_timer()
        self.controller.play_music("musica_inicio.wav")
        self.game_frame.pack_forget()
        self.menu_frame.pack(padx=30, pady=30)

    def show_game(self):
        self.menu_frame.pack_forget()
        self.game_frame.pack()

    def start_selected_game(self, mode, difficulty=None):
        self.show_game()
        self.controller.configure_game(mode=mode, difficulty=difficulty)

        if mode == "2_jugadores":
            self.controller.play_music("musica_1_vs_2.wav")
        else:
            self.controller.play_music("musica_vs_ia.wav")

        self.draw_board()
        self.controller.start_timer()
        self.controller.try_ai_turn()

    def back_to_menu(self):
        self.controller.stop_timer()
        self.show_menu()

    def run(self):
        self.root.mainloop()

    def close_window(self):
        self.controller.stop_timer()
        self.controller.stop_music()
        self.root.destroy()

    def board_to_canvas(self, row, col):
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        return x, y

    def handle_click(self, event):
        if self.controller.is_ai_turn():
            return

        move = self.get_nearest_line(event.x, event.y)

        if move is not None:
            self.controller.play_turn(move)

    def get_nearest_line(self, x, y):
        tolerance = 14

        for row in range(self.size):
            for col in range(self.size - 1):
                x1, y1 = self.board_to_canvas(row, col)
                x2, y2 = self.board_to_canvas(row, col + 1)

                if x1 <= x <= x2 and abs(y - y1) <= tolerance:
                    return ("H", row, col)

        for row in range(self.size - 1):
            for col in range(self.size):
                x1, y1 = self.board_to_canvas(row, col)
                x2, y2 = self.board_to_canvas(row + 1, col)

                if y1 <= y <= y2 and abs(x - x1) <= tolerance:
                    return ("V", row, col)

        return None

    def draw_board(self):
        self.canvas.delete("all")
        self.draw_grid_background()
        self.draw_boxes()
        self.draw_lines()
        self.draw_dots()
        self.update_info()
        self.update_timers()

    def draw_grid_background(self):
        for row in range(self.size):
            for col in range(self.size):
                x, y = self.board_to_canvas(row, col)
                self.canvas.create_oval(
                    x - 2, y - 2,
                    x + 2, y + 2,
                    fill=self.colors["orange"],
                    outline=""
                )

    def draw_boxes(self):
        for row in range(self.size - 1):
            for col in range(self.size - 1):
                owner = self.controller.boxes[row][col]

                if owner:
                    x1, y1 = self.board_to_canvas(row, col)
                    x2, y2 = self.board_to_canvas(row + 1, col + 1)

                    color = self.colors["player_1_box"] if owner == "Jugador 1" else self.colors["player_2_box"]

                    self.canvas.create_rectangle(
                        x1 + 7, y1 + 7,
                        x2 - 7, y2 - 7,
                        fill=color,
                        outline=self.colors["white"],
                        width=2,
                        stipple="gray50"
                    )

                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=owner[-1],
                        font=("Arial", 20, "bold"),
                        fill=self.colors["white"]
                    )

    def draw_lines(self):
        for line in self.controller.horizontal_lines:
            _, row, col = line
            x1, y1 = self.board_to_canvas(row, col)
            x2, y2 = self.board_to_canvas(row, col + 1)

            self.canvas.create_line(x1, y1, x2, y2, width=8, fill=self.colors["background"])
            self.canvas.create_line(x1, y1, x2, y2, width=5, fill=self.colors["line"])

        for line in self.controller.vertical_lines:
            _, row, col = line
            x1, y1 = self.board_to_canvas(row, col)
            x2, y2 = self.board_to_canvas(row + 1, col)

            self.canvas.create_line(x1, y1, x2, y2, width=8, fill=self.colors["background"])
            self.canvas.create_line(x1, y1, x2, y2, width=5, fill=self.colors["line"])

    def draw_dots(self):
        for row in range(self.size):
            for col in range(self.size):
                x, y = self.board_to_canvas(row, col)
                self.canvas.create_oval(
                    x - self.dot_radius,
                    y - self.dot_radius,
                    x + self.dot_radius,
                    y + self.dot_radius,
                    fill=self.colors["pacman_yellow"],
                    outline=self.colors["white"],
                    width=1
                )

    def update_info(self):
        scores = self.controller.scores
        mode_text = "Dos jugadores" if self.controller.mode == "2_jugadores" else f"Un jugador ({self.controller.difficulty})"

        text = (
            f"{mode_text} | Turno: {self.controller.current_player} | "
            f"Jugador 1: {scores['Jugador 1']} | "
            f"Jugador 2/IA: {scores['Jugador 2']}"
        )
        self.info_label.config(text=text)

    def format_time(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def update_timers(self):
        player_1_time = self.format_time(self.controller.player_times["Jugador 1"])
        player_2_time = self.format_time(self.controller.player_times["Jugador 2"])

        text = f"Jugador 1: {player_1_time}  |  Jugador 2/IA: {player_2_time}"
        self.timer_label.config(text=text)

    def show_message(self, title, message):
        messagebox.showinfo(title, message)
