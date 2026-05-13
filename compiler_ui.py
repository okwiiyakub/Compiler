import tkinter as tk
from tkinter import scrolledtext, messagebox
from main import compile_source

DEFAULT_CODE = """int x = 5;
int y = 10;
int z;
z = x + y * 2;
print z;
"""

def run_compiler():
    src = source_editor.get("1.0", tk.END).strip()
    if not src:
        messagebox.showwarning("No Input", "Please enter source code.")
        return
    result = compile_source(src, generate_ast_image=True)
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, result)
    output_box.config(state=tk.DISABLED)

def clear_all():
    source_editor.delete("1.0", tk.END)
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    output_box.config(state=tk.DISABLED)


root = tk.Tk()
root.title("Expanded Mini C-like Compiler Frontend")
root.geometry("1150x700")

tk.Label(
    root,
    text="Expanded Mini C-like Compiler Frontend",
    font=("Arial", 16, "bold"),
).pack(pady=10)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

left = tk.Frame(main_frame)
left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

right = tk.Frame(main_frame)
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

tk.Label(left, text="Source Code Input", font=("Arial", 12, "bold")).pack(
    anchor="w"
)
source_editor = scrolledtext.ScrolledText(left, wrap=tk.WORD, font=("Consolas", 11))
source_editor.pack(fill=tk.BOTH, expand=True)
source_editor.insert(tk.END, DEFAULT_CODE)

tk.Label(right, text="Compiler Output", font=("Arial", 12, "bold")).pack(
    anchor="w"
)
output_box = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=("Consolas", 10))
output_box.pack(fill=tk.BOTH, expand=True)
output_box.config(state=tk.DISABLED)

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="Compile",
    width=15,
    command=run_compiler,
    bg="#2d6cdf",
    fg="white",
    font=("Arial", 11, "bold"),
).pack(side=tk.LEFT, padx=5)

tk.Button(
    buttons,
    text="Clear",
    width=15,
    command=clear_all,
    font=("Arial", 11),
).pack(side=tk.LEFT, padx=5)

root.mainloop()
