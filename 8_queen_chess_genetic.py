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

def distance_to_goal_fitness(state, goal_state):
    if len(state) != len(goal_state):
        raise ValueError("State và Goal State phải có cùng kích thước.")
    total_distance = sum(abs(state[i] - goal_state[i]) for i in range(len(state)))
    return total_distance

def selection(population_with_fitness, k=3):
    tournament_contenders = random.sample(population_with_fitness, k)
    winner = min(tournament_contenders, key=lambda item: item[1])
    return winner[0] 

def crossover(parent1, parent2):
    n = len(parent1)
    crossover_point = random.randint(1, n - 1)
    return parent1[:crossover_point] + parent2[crossover_point:]

def mutate(individual, mutation_rate=0.1):
    if random.random() < mutation_rate:
        n = len(individual)
        mutation_row = random.randint(0, n - 1)
        individual[mutation_row] = random.randint(0, n - 1)
    return individual

def genetic_algorithm_steps(goal, n=8, population_size=100, max_generations=1000, mutation_rate=0.1):
    population = [[random.randrange(n) for _ in range(n)] for _ in range(population_size)]
    population_with_fitness = [(ind, distance_to_goal_fitness(ind, goal)) for ind in population]
    best_initial_state, best_initial_fitness = min(population_with_fitness, key=lambda item: item[1])
    path = [(i, best_initial_state[i], best_initial_fitness, 1) for i in range(n)]
    yield best_initial_state[:], False, path[:]

    for generation in range(max_generations):
        population_with_fitness = [(ind, distance_to_goal_fitness(ind, goal)) for ind in population]
        sorted_population = sorted(population_with_fitness, key=lambda item: item[1])
        current_best_state, current_best_fitness = sorted_population[0]
        path = [(i, current_best_state[i], current_best_fitness, generation + 1) for i in range(n)]

        if current_best_fitness == 0:
            yield current_best_state[:], True, path[:]
            return
            
        yield current_best_state[:], False, path[:]

        new_population = [sorted_population[0][0], sorted_population[1][0]]
        while len(new_population) < population_size:
            parent1 = selection(population_with_fitness)
            parent2 = selection(population_with_fitness)
            child = crossover(parent1, parent2)
            mutated_child = mutate(child, mutation_rate)
            new_population.append(mutated_child)
        population = new_population

    final_best_state, final_best_fitness = sorted(population_with_fitness, key=lambda item: item[1])[0]
    path = [(i, final_best_state[i], final_best_fitness, generation + 1) for i in range(n)]
    yield final_best_state[:], False, path[:]
    return

def main():
    root = tk.Tk()
    root.title("N-Queens Genetic Algorithm")

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
        goal_holder["gen"] = genetic_algorithm_steps(sol, 8, 100, 10, 0.1)
        step(8, 10)

    def step(size, generation):
        gen = goal_holder.get("gen")
        if not gen:
            return
        try:
            state, done, path = next(gen)
            gen_num = path[-1][3]
            fit = path[-1][2]
            board_left.show_partial(state, color="red")

            goal_holder["log"].append({
                "generation": gen_num,
                "fitness": fit,
                "state": state
            })

            if done:
                board_left.flash_scene("lightgreen")
                return
            elif len(path) == size and path[7][3] == generation:
                board_left.flash_scene("red")
                return

            root.after(100, lambda: step(size, generation))
        except StopIteration:
            return

    def export_csv():
        if not goal_holder["log"]:
            return
        with open("result.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["generation", "fitness", "state"])
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