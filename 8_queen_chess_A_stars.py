import tkinter as tk
import random
import csv
from tkinter import filedialog

def is_safe(state, row, col):
    for r, c in enumerate(state):
        if c == col or abs(c - col) == abs(r - row):
            return False
    return True

def solve_n_queens_all(n=8):
    sols = []
    def backtrack(state):
        row = len(state)
        if row == n:
            sols.append(tuple(state))
            return
        for col in range(n):
            if is_safe(state, row, col):
                state.append(col)
                backtrack(state)
                state.pop()
    backtrack([])
    return sols

class BoardCanvas:
    def __init__(self, parent, n=8, cell_size=40):
        self.n = n
        self.cell = cell_size
        self.canvas = tk.Canvas(parent, width=n*cell_size, height=n*cell_size)
        self.canvas.pack()
        self.queen_items = []
        self._draw_grid()

    def _draw_grid(self):
        self.canvas.delete("cell")
        for r in range(self.n):
            for c in range(self.n):
                x1, y1 = c*self.cell, r*self.cell
                x2, y2 = x1+self.cell, y1+self.cell
                color = "white" if (r+c)%2==0 else "gray"
                self.canvas.create_rectangle(x1,y1,x2,y2, fill=color, tags="cell")

    def clear_queens(self):
        for item in self.queen_items:
            self.canvas.delete(item)
        self.queen_items = []

    def show_partial(self, state, color="red"):
        self.clear_queens()
        for r, c in enumerate(state):
            cx = c*self.cell + self.cell/2
            cy = r*self.cell + self.cell/2
            tid = self.canvas.create_text(cx, cy, text="Q", font=("Arial", 16, "bold"), fill=color)
            self.queen_items.append(tid)

    def flash_scene(self, color):
        overlay = self.canvas.create_rectangle(
            0, 0, self.n*self.cell, self.n*self.cell,
            fill=color, outline="")
        self.canvas.after(500, lambda: self.canvas.delete(overlay))

def calc_attack_cost(row, col, path):
    if not path:
        r_last, c_last = 0, 0
    else:
        r_last, c_last = path[-1][0], path[-1][1]
    return abs(row - r_last) + abs(col - c_last)

def func_f(cells, c):
    def safe_key(item):
        try:
            return item[3]
        except Exception:
            return float('inf')
    c.sort(reverse=True, key=safe_key)
    return cells + c

def astar_steps(goal, n=8):
    cells = [(0, [], [], 0, 0)]
    while cells:
        row, state, path, f_cost, g_cost = cells.pop()

        if row == n:
            if tuple(state) == goal:
                yield state, True, path
                return
            continue

        c = []
        for col in range(n):
            if is_safe(state, row, col):
                new_state = state + [col]
                step_cost = calc_attack_cost(row, col, path)
                new_g = g_cost + step_cost
                h = abs(goal[row] - col)
                new_f = new_g + h
                new_path = path + [(row, col, new_g, h, new_f)]
                yield new_state, False, new_path
                c.append((row + 1, new_state, new_path, new_f, new_g))

        cells = func_f(cells, c)

def main():
    root = tk.Tk()
    root.title("N-Queens A* Search")

    frame = tk.Frame(root)
    frame.pack()
    board_left = BoardCanvas(frame, n=8, cell_size=40)
    board_right = BoardCanvas(frame, n=8, cell_size=40)

    all_sols = solve_n_queens_all(8)
    goal_holder = {"sol": None, "gen": None}
    last_path_holder = {"path": []}

    def random_goal():
        sol = random.choice(all_sols)
        goal_holder["sol"] = sol
        board_right.show_partial(sol, color="blue")
        board_left.clear_queens()
        last_path_holder["path"] = []

    def run():
        sol = goal_holder.get("sol")
        if not sol: 
            return
        goal_holder["gen"] = astar_steps(sol, 8)
        step()

    def step():
        gen = goal_holder.get("gen")
        if not gen:
            return
        try:
            state, done, path = next(gen)
            board_left.show_partial(state, color="red")
            if done:
                last_path_holder["path"] = path
                board_left.flash_scene("lightgreen")
                return
            root.after(10, step)
        except StopIteration:
            board_left.flash_scene("red")
            return

    def export_csv():
        if not last_path_holder["path"]:
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Lưu file CSV"
        )
        if not filename:
            return
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Hàng", "Cột", "g(n)", "h(n)", "f(n)"])
            for r, c, g, h, f_cost in last_path_holder["path"]:
                writer.writerow([r + 1, c + 1, g, h, f_cost])
        board_left.flash_scene("lightblue")

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Random Goal", command=random_goal).pack(side="left", padx=10, pady=10)
    tk.Button(btn_frame, text="Run", command=run).pack(side="left", padx=10, pady=10)
    tk.Button(btn_frame, text="Export CSV", command=export_csv).pack(side="left", padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()