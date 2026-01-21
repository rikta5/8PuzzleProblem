import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from typing import Optional, List
from src.domain import SlidingPuzzleProblem
from src.algorithms import (
    misplaced_tiles_heuristic,
    manhattan_distance_heuristic,
    linear_conflict_heuristic,
    AStarSearch,
    GreedyBestFirstSearch,
    HillClimbingSearch,
    SimulatedAnnealingSearch,
    IDAStarSearch,
    GeneticAlgorithmSearch,
)
from src.core import SearchAgent, Node

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sliding Tile Puzzle AI")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")
        
        self.colors = {
            "bg": "#f0f2f5",
            "panel": "#ffffff",
            "tile": "#3b82f6",
            "tile_correct": "#10b981",
            "text": "#ffffff",
            "canvas_bg": "#1e293b",
        }
        
        self.size = 3
        self.tile_size = 100
        self.padding = 5
        self.animation_speed = 0.2
        
        self.problem: Optional[SlidingPuzzleProblem] = None
        self.current_state = None
        self.solution_path: List[Node] = []
        self.current_step = 0
        self.is_animating = False
        
        self._configure_styles()
        self._setup_ui()
        self._init_puzzle()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], font=("Segoe UI", 10))
        style.configure("Panel.TFrame", background=self.colors["panel"], relief="flat")
        style.configure("Panel.TLabel", background=self.colors["panel"], font=("Segoe UI", 10))
        
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "#2563eb")])

    def _setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        canvas_frame = ttk.LabelFrame(main_container, text="Puzzle Board", padding=10)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.canvas_container = tk.Frame(canvas_frame, bg=self.colors["bg"])
        self.canvas_container.pack(expand=True, fill=tk.BOTH)

        control_panel = ttk.Frame(main_container, style="Panel.TFrame", padding=20)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        header_frame = ttk.Frame(control_panel, style="Panel.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Controls", font=("Segoe UI", 16, "bold"), style="Panel.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="?", width=3, command=self._show_help).pack(side=tk.RIGHT)

        ttk.Label(control_panel, text="Algorithm:", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.algo_var = tk.StringVar(value="astar_manhattan")
        algo_options = [
            "astar_linear",
            "astar_weighted",
            "astar_manhattan",
            "astar_misplaced",
            "idastar_linear",
            "idastar_manhattan",
            "greedy_manhattan",
            "hill_climbing_manhattan",
            "sa_manhattan",
            "genetic_manhattan"
        ]
        
        opt_menu = ttk.OptionMenu(control_panel, self.algo_var, algo_options[0], *algo_options)
        opt_menu.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(control_panel, text="Size:", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.size_var = tk.IntVar(value=3)
        size_frame = ttk.Frame(control_panel, style="Panel.TFrame")
        size_frame.pack(fill=tk.X, pady=(5, 15))
        ttk.Radiobutton(size_frame, text="3x3", variable=self.size_var, value=3, command=self._change_size).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(size_frame, text="4x4", variable=self.size_var, value=4, command=self._change_size).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_panel, text="Difficulty (Depth):", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.depth_var = tk.IntVar(value=20)
        ttk.Entry(control_panel, textvariable=self.depth_var).pack(fill=tk.X, pady=(5, 15))
        
        ttk.Button(control_panel, text="New Game (Scramble)", command=self._scramble).pack(fill=tk.X, pady=5)
        ttk.Button(control_panel, text="AI Solve", command=self._solve).pack(fill=tk.X, pady=5)
        
        ttk.Separator(control_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        ttk.Label(control_panel, text="Playback:", style="Panel.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.btn_play = ttk.Button(control_panel, text="▶ Play Animation", command=self._toggle_animation, state=tk.DISABLED)
        self.btn_play.pack(fill=tk.X, pady=5)
        
        self.btn_step = ttk.Button(control_panel, text="⏯ Step Forward", command=self._step_forward, state=tk.DISABLED)
        self.btn_step.pack(fill=tk.X, pady=5)
        
        self.btn_reset = ttk.Button(control_panel, text="⏮ Reset Path", command=self._reset_to_start, state=tk.DISABLED)
        self.btn_reset.pack(fill=tk.X, pady=5)

        self.lbl_status = ttk.Label(control_panel, text="Ready to Play!", font=("Segoe UI", 12), foreground="#64748b", background=self.colors["panel"], wraplength=200, justify="center")
        self.lbl_status.pack(pady=20, side=tk.BOTTOM)

        self._update_canvas_size()

    def _show_help(self):
        msg = """How to Play:
1. Click 'New Game' to scramble the board.
2. Click tiles adjacent to the empty space to move them.
3. Goal: Arrange numbers in order (1, 2, 3...) with empty space at end.

AI Solve:
- Select an algorithm from the dropdown.
- Click 'AI Solve' to let the computer find a solution.
- Use Play/Step controls to watch the solution.

Tips:
- A* Manhattan is usually the fastest and finds optimal solutions.
- IDA* uses less memory but can be slower on hard puzzles.
- Greedy is usually fast but doesn't guarantee the shortest path.
        """
        messagebox.showinfo("Instructions", msg)

    def _update_canvas_size(self):
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
            
        canvas_px = self.size * self.tile_size + 2 * self.padding
        self.canvas = tk.Canvas(self.canvas_container, width=canvas_px, height=canvas_px, bg=self.colors["canvas_bg"], highlightthickness=0)
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _init_puzzle(self):
        self.problem = SlidingPuzzleProblem(size=self.size) 
        self.current_state = self.problem.goal_state
        self._draw_state(self.current_state)
        self.lbl_status.config(text="Welcome! Click 'New Game' or move tiles manually.")

    def _on_canvas_click(self, event):
        if self.is_animating:
            return

        if not self.problem:
             self.problem = SlidingPuzzleProblem(size=self.size)

        col = (event.x - self.padding) // self.tile_size
        row = (event.y - self.padding) // self.tile_size
        
        if 0 <= col < self.size and 0 <= row < self.size:
            clicked_idx = row * self.size + col
            
            if self.current_state is None: return
            state_list = list(self.current_state)
            if 0 not in state_list: return
            
            blank_idx = state_list.index(0)
            
            b_row, b_col = divmod(blank_idx, self.size)
            
            dist = abs(row - b_row) + abs(col - b_col)
            
            if dist == 1:
                state_list[blank_idx], state_list[clicked_idx] = state_list[clicked_idx], state_list[blank_idx]
                new_state = tuple(state_list)
                self.current_state = new_state
                self._draw_state(new_state)
                
                self.solution_path = []
                self._update_controls(has_solution=False)

                if new_state == self.problem.goal_state:
                    self.lbl_status.config(text="YOU WON!", foreground="#16a34a", font=("Segoe UI", 14, "bold"))
                    self.canvas.config(bg="#dcfce7")
                else:
                    self.lbl_status.config(text="Move made...", foreground="#334155")
            else:
                 self.lbl_status.config(text="Cannot move that tile!", foreground="#ef4444")

    def _change_size(self):
        new_size = self.size_var.get()
        if new_size != self.size:
            self.size = new_size
            if self.size > 3:
                self.tile_size = 80
            else:
                self.tile_size = 100
            
            self._update_canvas_size()
            self._scramble()

    def _scramble(self):
        try:
            depth = self.depth_var.get()
        except:
            depth = 20
        
        self.problem = SlidingPuzzleProblem.scrambled(size=self.size, scramble_depth=depth)
        self.current_state = self.problem.initial_state()
        self._draw_state(self.current_state)
        
        self.solution_path = []
        self.current_step = 0
        self._update_controls(has_solution=False)
        self.lbl_status.config(text=f"Scrambled (Depth {depth})", foreground="#334155")
        self.canvas.config(bg=self.colors["canvas_bg"])

    def _draw_state(self, state):
        self.canvas.delete("all")
        for i, tile_val in enumerate(state):
            if tile_val == 0:
                continue
            
            row, col = divmod(i, self.size)
            
            gap = 4
            x = col * self.tile_size + self.padding + gap // 2
            y = row * self.tile_size + self.padding + gap // 2
            size = self.tile_size - gap
            
            goal_row, goal_col = divmod(tile_val - 1, self.size)
            
            is_correct = (row == goal_row and col == goal_col)
            fill_color = self.colors["tile_correct"] if is_correct else self.colors["tile"]
            
            self.canvas.create_rectangle(
                x, y, x + size, y + size,
                fill=fill_color, outline="", width=0
            )
            
            font_size = 28 if self.size <= 3 else 20
            self.canvas.create_text(
                x + size/2, y + size/2,
                text=str(tile_val), 
                font=("Segoe UI", font_size, "bold"), 
                fill=self.colors["text"]
            )

    def _solve(self):
        if not self.problem or self.current_state is None:
             self.problem = SlidingPuzzleProblem(size=self.size)
             self.current_state = self.problem.goal_state
        
        solve_problem = SlidingPuzzleProblem(size=self.size, initial_state=self.current_state)
            
        algo_name = self.algo_var.get()
        self.lbl_status.config(text="Thinking...", foreground="#eab308")
        self.root.update()
        
        threading.Thread(target=self._run_search, args=(solve_problem, algo_name), daemon=True).start()

    def _run_search(self, problem, algo_name):
        h_manhattan = manhattan_distance_heuristic(problem.goal_state, problem.size)
        h_misplaced = misplaced_tiles_heuristic(problem.goal_state)
        h_linear = linear_conflict_heuristic(problem.goal_state, problem.size)
        
        if algo_name == "astar_manhattan":
            algo = AStarSearch(h_manhattan)
        elif algo_name == "astar_weighted":
            algo = AStarSearch(h_manhattan, weight=1.5)
        elif algo_name == "astar_linear":
            algo = AStarSearch(h_linear)
        elif algo_name == "astar_misplaced":
            algo = AStarSearch(h_misplaced)
        elif algo_name == "greedy_manhattan":
            algo = GreedyBestFirstSearch(h_manhattan)
        elif algo_name == "hill_climbing_manhattan":
            algo = HillClimbingSearch(h_manhattan, max_steps=2000)
        elif algo_name == "sa_manhattan":
            algo = SimulatedAnnealingSearch(h_manhattan)
        elif algo_name == "idastar_manhattan":
            algo = IDAStarSearch(h_manhattan)
        elif algo_name == "idastar_linear":
            algo = IDAStarSearch(h_linear)
        elif algo_name == "genetic_manhattan":
            algo = GeneticAlgorithmSearch(h_manhattan)
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "Unknown algorithm"))
            return

        agent = SearchAgent(problem, algo)
        result = agent.solve()
        
        self.root.after(0, lambda: self._on_solve_complete(result))

    def _on_solve_complete(self, result):
        if result.success:
            self.solution_path = result.solution_path
            self.current_step = 0
            self.lbl_status.config(
                text=f"Solved!\nCost: {result.solution_cost}\nNodes: {result.nodes_expanded}\nTime: {result.runtime:.4f}s"
            )
            self._update_controls(has_solution=True)
        else:
            self.lbl_status.config(text=f"Failed.\nNodes: {result.nodes_expanded}")
            messagebox.showinfo("Result", "No solution found.")

    def _update_controls(self, has_solution):
        state = tk.NORMAL if has_solution else tk.DISABLED
        self.btn_play.config(state=state)
        self.btn_step.config(state=state)
        self.btn_reset.config(state=state)

    def _toggle_animation(self):
        if self.is_animating:
            self.is_animating = False
            self.btn_play.config(text="Play Animation")
        else:
            self.is_animating = True
            self.btn_play.config(text="Stop Animation")
            self._animate_step()

    def _animate_step(self):
        if not self.is_animating:
            return
            
        if self.current_step < len(self.solution_path) - 1:
            self._step_forward()
            self.root.after(int(self.animation_speed * 1000), self._animate_step)
        else:
            self.is_animating = False
            self.btn_play.config(text="Play Animation")

    def _step_forward(self):
        if self.current_step < len(self.solution_path) - 1:
            self.current_step += 1
            node = self.solution_path[self.current_step]
            self._draw_state(node.state)

    def _reset_to_start(self):
        self.is_animating = False
        self.btn_play.config(text="Play Animation")
        self.current_step = 0
        if self.solution_path:
            self._draw_state(self.solution_path[0].state)

if __name__ == "__main__":
    print("Starting GUI...")
    root = tk.Tk()
    app = PuzzleGUI(root)
    
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    print("GUI Window opened. Please check your taskbar if you don't see it.")
    root.mainloop()
