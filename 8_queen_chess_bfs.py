import csv
import tkinter as tk
import random
from collections import deque

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

def bfs_steps(goal, n=8, log_list=None):
    queue = deque([[]])
    step = 0
    while queue:
        state = queue.popleft()
        row = len(state)
        step += 1

        if log_list is not None:
            log_list.append({
                "Step": step,
                "Row": row,
                "State": state.copy(),
                "Status": "Đang xét"
            })

        if row == n:
            if tuple(state) == goal:
                if log_list is not None:
                    log_list.append({
                        "Step": step,
                        "Row": row,
                        "State": state.copy(),
                        "Status": "Hoàn thành (Goal)"
                    })
                yield state, True
                return
            continue

        for col in range(n):
            if is_safe(state, row, col):
                new_state = state + [col]
                if log_list is not None:
                    log_list.append({
                        "Step": step,
                        "Row": row,
                        "State": new_state.copy(),
                        "Status": f"Thử cột {col}"
                    })
                yield new_state, False
                queue.append(new_state)

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

def main():
    root = tk.Tk()
    root.title("N-Queens BFS")

    all_sols = solve_n_queens_all(8)
    goal_holder = {"sol": None, "gen": None, "log": []}

    def random_goal():
        sol = random.choice(all_sols)
        goal_holder["sol"] = sol
        board_right.show_partial(sol, color="blue")
        board_left.clear_queens()

    def run():
        sol = goal_holder.get("sol")
        if not sol: return
        goal_holder["log"].clear()
        goal_holder["gen"] = bfs_steps(sol, 8, log_list=goal_holder["log"])
        step()

    def step():
        gen = goal_holder.get("gen")
        if not gen: return
        try:
            state, done = next(gen)
            board_left.show_partial(state, color="red")
            if done:
                board_left.flash_scene("lightgreen")
                return
            root.after(10, step)
        except StopIteration:
            return

    def export_bfs_log():
        log = goal_holder["log"]
        if not log:
            return
        filename = "bfs_process.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Step", "Row", "State", "Status"])
            writer.writeheader()
            for row in log:
                writer.writerow(row)
        popup = tk.Toplevel(root)
        tk.Label(popup, text=f"Đã lưu quá trình BFS vào {filename}", padx=20, pady=10).pack()
        tk.Button(popup, text="Đóng", command=popup.destroy).pack(pady=10)

    # Giao diện
    frame = tk.Frame(root)
    frame.pack()
    board_left = BoardCanvas(frame, n=8, cell_size=40)
    board_right = BoardCanvas(frame, n=8, cell_size=40)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Random Goal", command=random_goal).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Run", command=run).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Xuất quá trình", command=export_bfs_log).pack(side="left", padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
