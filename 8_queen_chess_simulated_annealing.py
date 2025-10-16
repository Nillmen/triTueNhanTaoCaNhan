import tkinter as tk
import random
import math
import csv

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

def cost(state, goal_state=None):
    n = len(state)
    attacks = 0
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            c1 = state[r1]
            c2 = state[r2]
            if abs(r1 - r2) == abs(c1 - c2):
                attacks += 1

    if goal_state is None:
        return attacks
    else:
        distance = 0
        for i in range(n):
            if state[i] != goal_state[i]:
                distance += 1
        return attacks * n + distance

def simulated_annealing_steps(goal_state=None, n=8, T_max=50000.0, alpha=0.99995, max_steps=50000):
    current_state = list(range(n))
    random.shuffle(current_state)
    
    current_cost = cost(current_state, goal_state)
    T = T_max
    path = [] 

    for step in range(max_steps):
        if current_cost == 0:
            yield current_state, True, path
            return

        T *= alpha
        if T <= 1e-3: 
             break

        new_state = list(current_state)
        r1, r2 = random.sample(range(n), 2)
        new_state[r1], new_state[r2] = new_state[r2], new_state[r1]
        
        new_cost = cost(new_state, goal_state)
        delta_E = new_cost - current_cost

        if delta_E < 0 or random.random() < math.exp(-delta_E / T):
            current_state = new_state
            current_cost = new_cost
            path.append((r1, current_state[r1], current_cost))
            if len(path) > n:
                path.pop(0)

        yield current_state, False, path

    yield current_state, False, path

def main():
    root = tk.Tk()
    root.title("N-Queens Simulated Annealing")
    
    frame = tk.Frame(root)
    frame.pack()
    board_left = BoardCanvas(frame, n=8, cell_size=40)
    board_right = BoardCanvas(frame, n=8, cell_size=40)

    all_sols = solve_n_queens_all(8)
    goal_holder = {"sol": None, "gen": None, "path": []}

    def random_goal():
        sol = random.choice(all_sols)
        goal_holder["sol"] = sol
        goal_holder["path"] = []
        board_right.show_partial(sol, color="blue")
        board_left.clear_queens()

    def run():
        sol = goal_holder.get("sol")
        if not sol: return
        goal_holder["path"] = []
        goal_holder["gen"] = simulated_annealing_steps(sol, 8, 50000.0, 0.99995, 20000)
        step(20000, 1)

    def step(max_step, current_step):
        gen = goal_holder.get("gen")
        if not gen: 
            return
        try:
            state, done, path = next(gen)
            goal_holder["path"] = path
            board_left.show_partial(state, color="red")

            if done:
                board_left.flash_scene("lightgreen")
                return
            elif current_step == max_step:
                board_left.flash_scene("red")
                return

            root.after(1, step, max_step, current_step + 1)
        except StopIteration:
            return

    def export_csv():
        path = goal_holder.get("path", [])
        if not path:
            return
        with open("result.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Bước", "Hàng", "Cột", "Chi phí"])
            for i, (r, c, cost_val) in enumerate(path, 1):
                writer.writerow([i, r + 1, c + 1, cost_val])
        board_left.flash_scene("yellow")

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Random Goal", command=random_goal).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Run", command=run).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Xuất CSV", command=export_csv).pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()