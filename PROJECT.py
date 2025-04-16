import tkinter as tk
from tkinter import ttk, messagebox
import random
from collections import deque, OrderedDict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Strategy Analyzer")
        self.root.geometry("1000x700")
        
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # Input Frame
        self.input_frame = ttk.LabelFrame(self.root, text="Simulation Parameters")
        
        self.ref_string_label = ttk.Label(self.input_frame, text="Reference String:")
        self.ref_string_entry = ttk.Entry(self.input_frame, width=30)
        self.ref_string_entry.insert(0, "1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5")
        
        self.generate_random_btn = ttk.Button(
            self.input_frame, 
            text="Generate Random", 
            command=self.generate_random_ref_string
        )
        
        self.frames_label = ttk.Label(self.input_frame, text="Number of Frames:")
        self.frames_spinbox = ttk.Spinbox(
            self.input_frame, 
            from_=1, 
            to=10, 
            width=5
        )
        self.frames_spinbox.set(3)
        
        self.strategy_label = ttk.Label(self.input_frame, text="Replacement Strategy:")
        self.strategy_combobox = ttk.Combobox(
            self.input_frame,
            values=["FIFO", "LRU", "Optimal", "Compare All"],
            state="readonly"
        )
        self.strategy_combobox.set("FIFO")
        
        self.simulate_btn = ttk.Button(
            self.input_frame, 
            text="Simulate", 
            command=self.run_simulation
        )
        
        # Results Frame
        self.results_frame = ttk.LabelFrame(self.root, text="Simulation Results")
        
        self.results_text = tk.Text(
            self.results_frame, 
            height=15, 
            width=80,
            state="disabled"
        )
        self.scrollbar = ttk.Scrollbar(
            self.results_frame, 
            orient="vertical", 
            command=self.results_text.yview
        )
        self.results_text.configure(yscrollcommand=self.scrollbar.set)
        
        # Visualization Frame
        self.visualization_frame = ttk.LabelFrame(self.root, text="Visualization")
        
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.visualization_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_layout(self):
        # Input Frame Layout
        self.input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.ref_string_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ref_string_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.generate_random_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.frames_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.frames_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.strategy_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.strategy_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.simulate_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Results Frame Layout
        self.results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Visualization Frame Layout
        self.visualization_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
    def generate_random_ref_string(self):
        length = random.randint(10, 20)
        ref_string = [random.randint(1, 9) for _ in range(length)]
        self.ref_string_entry.delete(0, tk.END)
        self.ref_string_entry.insert(0, ", ".join(map(str, ref_string)))
        
    def validate_inputs(self):
        try:
            ref_string = [int(x.strip()) for x in self.ref_string_entry.get().split(",")]
            frames = int(self.frames_spinbox.get())
            if frames <= 0:
                raise ValueError("Number of frames must be positive")
            if any(x <= 0 for x in ref_string):
                raise ValueError("Page numbers must be positive integers")
            return ref_string, frames
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None, None
        
    def run_simulation(self):
        ref_string, frames = self.validate_inputs()
        if ref_string is None:
            return
            
        strategy = self.strategy_combobox.get()
        
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        
        if strategy == "Compare All":
            results = {}
            
            # FIFO
            fifo_faults, fifo_frames_history = self.fifo(ref_string, frames)
            results["FIFO"] = {
                "faults": fifo_faults,
                "history": fifo_frames_history
            }
            
            # LRU
            lru_faults, lru_frames_history = self.lru(ref_string, frames)
            results["LRU"] = {
                "faults": lru_faults,
                "history": lru_frames_history
            }
            
            # Optimal
            optimal_faults, optimal_frames_history = self.optimal(ref_string, frames)
            results["Optimal"] = {
                "faults": optimal_faults,
                "history": optimal_frames_history
            }
            
            # Display comparison results
            self.display_comparison_results(ref_string, frames, results)
            self.plot_comparison(ref_string, results)
            
        else:
            if strategy == "FIFO":
                faults, frames_history = self.fifo(ref_string, frames)
            elif strategy == "LRU":
                faults, frames_history = self.lru(ref_string, frames)
            elif strategy == "Optimal":
                faults, frames_history = self.optimal(ref_string, frames)
                
            self.display_single_result(ref_string, frames, strategy, faults, frames_history)
            self.plot_single(ref_string, frames_history, strategy, faults)
            
        self.results_text.config(state="disabled")
        
    def fifo(self, ref_string, frames):
        memory = deque(maxlen=frames)
        faults = 0
        frames_history = []
        
        for page in ref_string:
            if page not in memory:
                faults += 1
                if len(memory) == frames:
                    memory.popleft()
                memory.append(page)
            frames_history.append(list(memory))
            
        return faults, frames_history
        
    def lru(self, ref_string, frames):
        memory = OrderedDict()
        faults = 0
        frames_history = []
        
        for i, page in enumerate(ref_string):
            if page in memory:
                # Move to end to show it was recently used
                memory.move_to_end(page)
            else:
                faults += 1
                if len(memory) == frames:
                    # Remove first item (least recently used)
                    memory.popitem(last=False)
                memory[page] = True
            frames_history.append(list(memory.keys()))
            
        return faults, frames_history
        
    def optimal(self, ref_string, frames):
        memory = set()
        faults = 0
        frames_history = []
        
        for i, page in enumerate(ref_string):
            if page not in memory:
                faults += 1
                if len(memory) == frames:
                    # Find page not used for longest time in future
                    farthest = -1
                    victim = None
                    for p in memory:
                        try:
                            next_use = ref_string.index(p, i+1)
                            if next_use > farthest:
                                farthest = next_use
                                victim = p
                        except ValueError:
                            victim = p
                            break
                    memory.discard(victim)
                memory.add(page)
            frames_history.append(list(memory))
            
        return faults, frames_history
        
    def display_single_result(self, ref_string, frames, strategy, faults, frames_history):
        self.results_text.insert(tk.END, f"Reference String: {ref_string}\n")
        self.results_text.insert(tk.END, f"Number of Frames: {frames}\n")
        self.results_text.insert(tk.END, f"Replacement Strategy: {strategy}\n")
        self.results_text.insert(tk.END, f"Total Page Faults: {faults}\n")
        self.results_text.insert(tk.END, f"Fault Rate: {faults/len(ref_string)*100:.2f}%\n\n")
        
        self.results_text.insert(tk.END, "Step-by-Step Page Allocation:\n")
        self.results_text.insert(tk.END, "Ref\tFrames\t\tFault\n")
        self.results_text.insert(tk.END, "-"*30 + "\n")
        
        for i, page in enumerate(ref_string):
            frames_str = ", ".join(map(str, frames_history[i])) if frames_history[i] else "-"
            fault = "Yes" if (i == 0 or page not in frames_history[i-1]) and page not in (frames_history[i] if i < len(frames_history) else []) else "No"
            self.results_text.insert(tk.END, f"{page}\t{frames_str.ljust(15)}\t{fault}\n")
            
    def display_comparison_results(self, ref_string, frames, results):
        self.results_text.insert(tk.END, f"Reference String: {ref_string}\n")
        self.results_text.insert(tk.END, f"Number of Frames: {frames}\n\n")
        
        self.results_text.insert(tk.END, "Comparison of Page Replacement Algorithms:\n")
        self.results_text.insert(tk.END, "-"*50 + "\n")
        self.results_text.insert(tk.END, "Algorithm\tPage Faults\tFault Rate\n")
        self.results_text.insert(tk.END, "-"*50 + "\n")
        
        for algo, data in results.items():
            fault_rate = data["faults"] / len(ref_string) * 100
            self.results_text.insert(tk.END, f"{algo}\t{data['faults']}\t\t{fault_rate:.2f}%\n")
            
        # Find the best algorithm
        best_algo = min(results.items(), key=lambda x: x[1]["faults"])[0]
        self.results_text.insert(tk.END, f"\nBest algorithm for this reference string: {best_algo}\n")
        
    def plot_single(self, ref_string, frames_history, strategy, faults):
        self.ax.clear()
        
        # Prepare data for visualization
        pages = list(set(ref_string))
        steps = list(range(1, len(ref_string)+1))
        
        # Create a grid for visualization
        grid = []
        for i in range(len(ref_string)):
            row = []
            for page in pages:
                if page in frames_history[i]:
                    row.append(1)
                else:
                    row.append(0)
            grid.append(row)
            
        # Plot the grid
        self.ax.imshow(grid, cmap="Blues", aspect="auto", interpolation="none")
        
        # Set ticks and labels
        self.ax.set_xticks(range(len(pages)))
        self.ax.set_xticklabels(pages)
        self.ax.set_yticks(range(len(ref_string)))
        self.ax.set_yticklabels(ref_string)
        
        self.ax.set_xlabel("Page Number")
        self.ax.set_ylabel("Reference String Step")
        self.ax.set_title(f"{strategy} Page Replacement (Faults: {faults})")
        
        self.canvas.draw()
        
    def plot_comparison(self, ref_string, results):
        self.ax.clear()
        
        algorithms = list(results.keys())
        faults = [data["faults"] for data in results.values()]
        fault_rates = [data["faults"]/len(ref_string)*100 for data in results.values()]
        
        x = range(len(algorithms))
        
        bars = self.ax.bar(x, faults, color=['blue', 'green', 'orange'])
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(algorithms)
        self.ax.set_ylabel("Number of Page Faults")
        self.ax.set_title("Comparison of Page Replacement Algorithms")
        
        # Add fault rate labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{faults[i]} ({fault_rates[i]:.1f}%)',
                        ha='center', va='bottom')
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()