import tkinter as tk
import random
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

def conflict(state):
    conflicts = 0
    n = len(state)
    for i in range(n):
        for j in range(i+1, n):
            if state[i] == state[j] or abs(state[i]-state[j]) == abs(i-j):
                conflicts += 1
    return conflicts

def hill_climb_steps(goal, n=8):
    state = [random.randrange(n) for _ in range(n)]
    path = [(i, state[i], conflict(state)) for i in range(n)]
    yield state[:], False, path[:]

    while True:
        current_conf = conflict(state)
        if current_conf == 0:
            ok = (tuple(state) == goal)
            yield state[:], ok, path[:]
            return

        neighbors = []
        for row in range(n):
            for col in range(n):
                if col != state[row]:
                    new_state = state[:]
                    new_state[row] = col
                    neighbors.append((new_state, conflict(new_state), row, col))

        if not neighbors:
            yield state[:], False, path[:]
            return

        new_state, new_conf, r, c = min(neighbors, key=lambda x: x[1])

        if new_conf < current_conf:
            state = new_state
            path.append((r, c, new_conf))
            yield state[:], False, path[:]
        else:
            yield state[:], False, path[:]
            return

def main():
    root = tk.Tk()
    root.title("N-Queens - Hill Climbing")

    frame = tk.Frame(root)
    frame.pack()
    board_left = BoardCanvas(frame, n=8, cell_size=40)
    board_right = BoardCanvas(frame, n=8, cell_size=40)

    all_sols = solve_n_queens_all(8)
    goal_holder = {"sol": None, "gen": None, "log": []}

    def random_goal():
        sol = random.choice(all_sols)
        goal_holder["sol"] = sol
        board_right.show_partial(sol, color="blue")
        board_left.clear_queens()
        goal_holder["log"].clear()

    def run():
        sol = goal_holder.get("sol")
        if not sol:
            return
        goal_holder["gen"] = hill_climb_steps(sol, 8)
        step(8)

    def step(size):
        gen = goal_holder.get("gen")
        if not gen:
            return
        try:
            state, done, path = next(gen)
            step_num = len(path)
            conf = path[-1][2]

            goal_holder["log"].append({
                "step": step_num,
                "conflicts": conf,
                "state": state
            })

            board_left.show_partial(state, color="red")

            if done:
                board_left.flash_scene("lightgreen")
                return
            elif len(path) == size:
                board_left.flash_scene("red")
                return

            root.after(200, lambda: step(size))
        except StopIteration:
            return

    def export_csv():
        if not goal_holder["log"]:
            return
        with open("result.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["step", "conflicts", "state"])
            writer.writeheader()
            writer.writerows(goal_holder["log"])

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Random Goal", command=random_goal).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Run", command=run).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Xuất CSV", command=export_csv).pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
