import tkinter as tk
from tkinter import messagebox as mb


class Node:
    def __init__(self, board, player, parent=None):
        self.board = board
        self.player = player
        self.parent = parent

    def is_terminal(self):
        altNode = Node(self.board, 'black' if self.player == 'white' else 'white', parent=self.parent)
        return altNode.get_valid_moves() == [] and self.get_valid_moves() == []
    
    def get_children(self):
        self.children = []
        valid_moves = self.get_valid_moves()
        for valid_move in valid_moves:
            new_board = move(self.board, valid_move[0], valid_move[1], self.player)
            new_player = 'black' if self.player == 'white' else 'white'
            new_node = Node(new_board, new_player, parent=self)
            self.children.append(new_node)
        return self.children
    
    def get_heuristic(self):
        opponent = 'black' if self.player == 'white' else 'white'
        heuristicValue = 0
        for row in self.board:
            for piece in row:
                if piece == self.player:
                    heuristicValue += 1
                elif piece == opponent:
                    heuristicValue -= 1
        return heuristicValue
    
    def is_valid_move(self, row, col):
        if self.board[row][col] != '*':
          return False
        opponent = 'black' if self.player == 'white' else 'white'
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for rowDirection, columnDirection in directions:
            r, c = row + rowDirection, col + columnDirection
            if not (0 <= r < 8 and 0 <= c < 8) or self.board[r][c] != opponent:
                continue
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                r += rowDirection
                c += columnDirection
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.player:
                return True
        return False
    
    def get_valid_moves(self):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves

board = [ #initialising the starter game board
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', 'black', 'white', '*', '*', '*'],
    ['*', '*', '*', 'white', 'black', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
]


def move(board, row, col, player):
    new_board = [row.copy() for row in board] # initialise a new local board that copies the original board
    opponent = 'black' if player == 'white' else 'white' # Determine the opponent's color based on the current player's color
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] #valid move direction 
    for rowDirection, columnDirection in directions:
        r, c = row + rowDirection, col + columnDirection
        while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == opponent: # Keep moving in the direction until either reaching an edge or a player's own piece
            r += rowDirection
            c += columnDirection
        if 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == player: # If a player's piece is found in the direction, flip opponent's pieces in between
            while (r, c) != (row, col):
                new_board[r][c] = player
                r -= rowDirection
                c -= columnDirection
    new_board[row][col] = player
    return new_board

class GameController:
    def __init__(self,color,op_color,difficulty): #initiate the game controller class
        self.state = Node(board, "black")
        self.color = color
        self.op_color = op_color
        self.difficulty = difficulty
        
    def get_winner(self):
        if self.state.is_terminal():
            if self.state.get_heuristic() > 0:
                return self.state.player
            elif self.state.get_heuristic() < 0:
                return 'white' if self.state.player == 'black' else 'black'
            else:
                return 'draw'
        else:
            return None

    def make_move(self, row, col):
        if self.state.is_valid_move(row, col):
            new_board = move(self.state.board, row, col, self.state.player)
            new_player = 'black' if self.state.player == 'white' else 'white'
            self.state = Node(new_board, new_player, parent=self.state)
            return True
        else:
            return False
        
    def alpha_beta_search(self, depth):
        best_value = -float('inf')
        best_move = None
        moves = self.state.get_valid_moves()
        for potential_move in moves:
            new_board = move(self.state.board, potential_move[0], potential_move[1], self.state.player)
            new_player = 'black' if self.state.player == 'white' else 'white'
            new_node = Node(new_board, new_player, parent=self.state)
            value = self.alpha_beta(new_node,-float('inf'), float('inf'), True, depth)
            if value > best_value:
                best_value = value
                best_move = potential_move
        return best_move
    
    def alpha_beta(self,node, alpha, beta, maximizing_player, depth):
        if node.is_terminal() or depth == 0:
            return node.get_heuristic()
        if maximizing_player:
            value = -float('inf')
            for child in node.get_children():
                child_value = self.alpha_beta(child, alpha, beta, False , depth - 1)*-1
                value = max(value, child_value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for child in node.get_children():
                child_value = self.alpha_beta(child, alpha, beta, True, depth - 1)
                value = min(value, child_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
        
    def computer_turn(self):
        next_move = self.alpha_beta_search(self.difficulty)
        next_board = move(self.state.board, next_move[0], next_move[1], self.state.player)
        next_player = 'black' if self.state.player == 'white' else 'white'
        self.state = Node(next_board, next_player, parent=self.state)

class OthelloGUI:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.root = tk.Tk()
        self.root.title("Othello")

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="green")
        self.canvas.pack()

        self.status_label = tk.Label(self.root, text=f"Current Turn: {self.game_controller.state.player}")
        self.status_label.pack()

        self.black_score_label = tk.Label(self.root, text=f"Black: {self.game_controller.state.get_heuristic()}")
        self.black_score_label.pack()

        self.white_score_label = tk.Label(self.root, text=f"White: {64 - self.game_controller.state.get_heuristic()}")
        self.white_score_label.pack()
        self.refresh()
        self.root.after(0, self.gameplay_loop)
        self.root.mainloop()

    def draw_board(self):
        self.canvas.delete("highlight")  # Clear previous highlights
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 50, row * 50
                x2, y2 = x1 + 50, y1 + 50
                color = "green" if (row + col) % 2 == 0 else "dark green"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                if (row, col) in self.game_controller.state.get_valid_moves():
                    self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="light green", tags="highlight")

    def draw_pieces(self):
        self.canvas.delete("piece")  # Clear previous pieces
        for row in range(8):
            for col in range(8):
                x, y = col * 50 + 25, row * 50 + 25
                if self.game_controller.state.board[row][col] == 'black':
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="black", tags="piece")
                elif self.game_controller.state.board[row][col] == 'white':
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="white", tags="piece")

    def refresh(self):
        self.draw_board()
        self.draw_pieces()
        
        
    def handle_click(self, event):
        row, col = event.y // 50, event.x // 50
        if (row,col) in self.game_controller.state.get_valid_moves():
            self.game_controller.make_move(row, col)
            self.update_status_label()
            computer = self.game_controller.state.player
            self.refresh()  # Redraw the board to update highlights
            self.update_score_labels()  # Update score labels

    def update_status_label(self):
        self.status_label.config(text=f"Current Turn: {self.game_controller.state.player}")
        self.refresh()

    def update_score_labels(self):
        black_score = sum(row.count('black') for row in self.game_controller.state.board)
        white_score = sum(row.count('white') for row in self.game_controller.state.board)
        self.black_score_label.config(text=f"Black: {black_score}")
        self.white_score_label.config(text=f"White: {white_score}")


    def gameplay_loop(self):
        print("Self :",self.game_controller.state.get_valid_moves())
        other_state = Node(self.game_controller.state.board,'black' if self.game_controller.state.player == 'white' else 'white')
        print("Other :",other_state.get_valid_moves())

        print(other_state.get_valid_moves())
        if self.game_controller.state.is_terminal():
            winner = self.game_controller.get_winner()
            mb.showinfo("Winner", f"{winner} wins!")
            self.root.quit()
        elif len(self.game_controller.state.get_valid_moves()) == 0:
            self.game_controller.state.player = 'black' if self.game_controller.state.player == 'white' else 'white'
            self.refresh()
        print(self.game_controller.state.player,self.game_controller.op_color,666)
        if self.game_controller.state.player == self.game_controller.op_color:
            self.game_controller.computer_turn()
            self.refresh()
            self.update_status_label()
            self.update_score_labels()
        else:
            self.canvas.bind("<Button-1>", self.handle_click)

        self.root.after(100, self.gameplay_loop)


        
class SettingsGUI:
    def __init__(self, game_controller):
        self.game_controller = game_controller
        self.root = tk.Tk()
        self.root.title("Othello")

        self.difficulty_label = tk.Label(self.root, text="Select Difficulty:")
        self.difficulty_label.pack()

        self.difficulty_var = tk.StringVar(self.root)
        self.difficulty_var.set("3")  
        self.difficulty_menu = tk.OptionMenu(self.root, self.difficulty_var, "1", "3", "5")
        self.difficulty_menu.pack()

        self.color_label = tk.Label(self.root, text="Select Your Color:")
        self.color_label.pack()

        self.color_var = tk.StringVar(self.root)
        self.color_var.set("black")  
        self.color_menu = tk.OptionMenu(self.root, self.color_var, "black", "white")
        self.color_menu.pack()

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack()

        self.root.mainloop()

    def start_game(self):
        self.difficulty = int(self.difficulty_var.get())
        self.color = self.color_var.get()
        self.op_color = 'black' if self.color == 'white' else 'white'
        mb.showinfo("Game Settings", f"Difficulty: {self.difficulty}, Your Color: {self.color}, Computer Color: {self.op_color}")
        self.root.destroy()

settings_gui = SettingsGUI(None)  # Instantiate SettingsGUI first
game_controller = GameController(settings_gui.color, settings_gui.op_color, settings_gui.difficulty)
gui = OthelloGUI(game_controller)