import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from enum import Enum

from compiler.lexer import NeoLexer
from compiler.parser import NeoParser
from compiler.evaluator import NeoEvaluator
from compiler.symbol_table import SemanticError


class Direction(Enum):
    NORTH = (-1, 0, "↑")
    EAST = (0, 1, "→")
    SOUTH = (1, 0, "↓")
    WEST = (0, -1, "←")

    @property
    def dr(self):
        return self.value[0]

    @property
    def dc(self):
        return self.value[1]

    @property
    def symbol(self):
        return self.value[2]


@dataclass
class Robot:
    row: int
    col: int
    direction: Direction = Direction.EAST


class NeoRuntimeError(Exception):
    pass


class NeoWorld:
    EMPTY, OBSTACLE, GOAL = 0, 1, 2

    def __init__(self, grid, start=(4, 0), direction=Direction.EAST):
        self.grid = [r[:] for r in grid]
        self.start = start
        self.start_direction = direction
        self.robot = Robot(*start, direction)

    @property
    def rows(self):
        return len(self.grid)

    @property
    def cols(self):
        return len(self.grid[0])

    def reset(self):
        self.robot = Robot(*self.start, self.start_direction)

    def inside(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def front_position(self):
        return (
            self.robot.row + self.robot.direction.dr,
            self.robot.col + self.robot.direction.dc
        )

    def obstacle(self):
        r, c = self.front_position()
        return (
            not self.inside(r, c)
            or self.grid[r][c] == self.OBSTACLE
        )

    def goal(self):
        return (
            self.grid[self.robot.row][self.robot.col]
            == self.GOAL
        )

    def turn(self, side):
        directions = [
            Direction.NORTH,
            Direction.EAST,
            Direction.SOUTH,
            Direction.WEST
        ]
        i = directions.index(self.robot.direction)

        if side == "RIGHT":
            self.robot.direction = directions[(i + 1) % 4]
        elif side == "LEFT":
            self.robot.direction = directions[(i - 1) % 4]
        else:
            raise NeoRuntimeError(
                "turn() expected LEFT or RIGHT"
            )

    def move_one(self):
        if self.obstacle():
            raise NeoRuntimeError(
                "Neo tried to enter an obstacle or leave the world"
            )
        self.robot.row += self.robot.direction.dr
        self.robot.col += self.robot.direction.dc


class NeoApp:
    CELL = 64

    def __init__(self, root):
        self.root = root
        root.title("Neo — Language Processors")

        self.world = NeoWorld([
            [0, 0, 0, 1, 0, 0, 2],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ])

        # NeoEvaluator is the single execution engine.
        # The GUI supplies sensors and visible robot actions.
        self.evaluator = NeoEvaluator(
            obstacle_sensor=self.world.obstacle,
            goal_sensor=self.world.goal,
            move_action=self.runtime_move,
            turn_action=self.runtime_turn
        )

        self.running = False

        outer = ttk.Frame(root, padding=14)
        outer.pack(fill="both", expand=True)

        main = ttk.Frame(outer)
        main.pack(fill="both", expand=True)

        left = ttk.LabelFrame(main, text="Neo Program", padding=10)
        left.pack(
            side="left", fill="both", expand=True, padx=(0, 10)
        )

        self.editor = tk.Text(
            left, width=34, height=18, font=("Menlo", 13)
        )
        self.editor.pack(fill="both", expand=True)

        # Neo P6 example.
        self.editor.insert(
            "1.0",
            "int doubleValue(int x) {\n"
            "    return x * 2;\n"
            "}\n"
            "\n"
            "void advance(int n) {\n"
            "    move(n);\n"
            "}\n"
            "\n"
            "void main() {\n"
            "    int steps;\n"
            "    steps = doubleValue(1);\n"
            "    advance(steps);\n"
            "    turn(LEFT);\n"
            "    advance(1);\n"
            "}\n"
        )

        bar = ttk.Frame(left)
        bar.pack(fill="x", pady=(8, 0))

        self.runbtn = ttk.Button(
            bar, text="▶ Run", command=self.run
        )
        self.runbtn.pack(side="left")

        ttk.Button(
            bar, text="↺ Reset", command=self.reset
        ).pack(side="left", padx=8)

        right = ttk.LabelFrame(main, text="World", padding=10)
        right.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            right,
            width=self.world.cols * self.CELL,
            height=self.world.rows * self.CELL,
            bg="white"
        )
        self.canvas.pack()

        self.status = ttk.Label(right)
        self.status.pack(anchor="w", pady=8)

        cf = ttk.LabelFrame(outer, text="Console", padding=6)
        cf.pack(fill="x", pady=(10, 0))

        self.console = tk.Text(
            cf, height=6, state="disabled", font=("Menlo", 10)
        )
        self.console.pack(fill="x")

        self.draw()
        self.log("Neo ready. Write a program and press Run.")

    def log(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    # ---------------------------------------------------------
    # Runtime actions called by NeoEvaluator
    # ---------------------------------------------------------

    def runtime_turn(self, side):
        self.log(f"turn({side});")
        self.world.turn(side)
        self.draw()
        self.root.update_idletasks()

    def runtime_move(self, steps):
        self.log(f"move({steps});")

        for _ in range(steps):
            self.world.move_one()
            self.draw()
            self.root.update_idletasks()

            if self.world.goal():
                self.log("★ Neo has reached the goal.")

            # A short visual delay while keeping a single,
            # synchronous language execution engine.
            self.root.after(180)
            self.root.update()

    def draw(self):
        self.canvas.delete("all")

        for r, row in enumerate(self.world.grid):
            for c, value in enumerate(row):
                x = c * self.CELL
                y = r * self.CELL

                if value == 1:
                    fill = "#444"
                elif value == 2:
                    fill = "#fff2b2"
                else:
                    fill = "white"

                self.canvas.create_rectangle(
                    x, y, x + self.CELL, y + self.CELL,
                    fill=fill, outline="#bbb"
                )

                if value == 2:
                    self.canvas.create_text(
                        x + self.CELL / 2,
                        y + self.CELL / 2,
                        text="★",
                        font=("Arial", 26)
                    )

        rb = self.world.robot
        cx = rb.col * self.CELL + self.CELL / 2
        cy = rb.row * self.CELL + self.CELL / 2
        s = 0.70

        def p(x, y):
            return cx + x * s, cy + y * s

        def oval(x1, y1, x2, y2, **kwargs):
            self.canvas.create_oval(
                *p(x1, y1), *p(x2, y2), **kwargs
            )

        def line(x1, y1, x2, y2, **kwargs):
            self.canvas.create_line(
                *p(x1, y1), *p(x2, y2), **kwargs
            )

        line(0, -22, 0, -29, fill="#222222", width=2)
        oval(
            -3, -32, 3, -26,
            fill="#4fc3f7", outline="#222222", width=1
        )
        oval(
            -18, -23, 18, 2,
            fill="#e6f1ff", outline="#222222", width=2
        )
        oval(
            -13, -17, 13, -2,
            fill="#243447", outline="#222222", width=1
        )
        oval(-8, -13, -4, -7, fill="#4fc3f7", outline="")
        oval(4, -13, 8, -7, fill="#4fc3f7", outline="")
        oval(
            -12, 1, 12, 23,
            fill="#e6f1ff", outline="#222222", width=2
        )
        oval(
            -3, 7, 3, 13,
            fill="#4fc3f7", outline="#222222", width=1
        )
        line(-12, 7, -19, 13, fill="#222222", width=2)
        line(12, 7, 19, 13, fill="#222222", width=2)
        line(-6, 21, -8, 28, fill="#222222", width=2)
        line(6, 21, 8, 28, fill="#222222", width=2)

        offset = self.CELL * 0.40

        if rb.direction == Direction.NORTH:
            dx, dy = 0, -offset
            if rb.row == 0:
                dy = offset
        elif rb.direction == Direction.SOUTH:
            dx, dy = 0, offset
            if rb.row == self.world.rows - 1:
                dy = -offset
        elif rb.direction == Direction.EAST:
            dx, dy = offset, 0
            if rb.col == self.world.cols - 1:
                dx = -offset
        else:
            dx, dy = -offset, 0
            if rb.col == 0:
                dx = offset

        self.canvas.create_text(
            cx + dx, cy + dy,
            text=rb.direction.symbol,
            font=("Arial", 12, "bold"),
            fill="#1976d2"
        )

        self.status.config(
            text=(
                f"Position: ({rb.row}, {rb.col})   "
                f"Direction: {rb.direction.name}"
            )
        )

    def reset(self):
        self.running = False
        self.world.reset()
        self.evaluator.reset()
        self.runbtn.config(state="normal")
        self.draw()
        self.log("World reset.")

    def run(self):
        if self.running:
            return

        code = self.editor.get("1.0", "end-1c")

        self.world.reset()
        self.evaluator.reset()
        self.draw()

        self.log("────────────────────────────")
        self.log("Compiling program...")

        try:
            lexer = NeoLexer()
            parser = NeoParser()

            ast = parser.parse(
                lexer.tokenize(code)
            )

            if ast is None:
                self.log("✗ Unable to build the AST.")
                return

            self.log("✓ Analysis completed successfully.")
            self.log(f"AST: {ast}")
            self.log(
                "Symbol Table: "
                + str(parser.symbol_table.scopes)
            )

            self.running = True
            self.runbtn.config(state="disabled")
            self.log("Executing program...")

            self.evaluator.execute_program(ast)

            self.log("✓ Program finished.")

        except NotImplementedError as e:
            self.log(
                "✗ Compiler component not implemented: "
                + str(e)
            )
        except SyntaxError as e:
            self.log("✗ Syntax error: " + str(e))
        except SemanticError as e:
            self.log("✗ Semantic error: " + str(e))
        except ValueError as e:
            self.log("✗ Lexical error: " + str(e))
        except (NeoRuntimeError, RuntimeError) as e:
            self.log("✗ Runtime error: " + str(e))
        except Exception as e:
            self.log("✗ Error: " + str(e))
        finally:
            self.running = False
            self.runbtn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    NeoApp(root)
    root.mainloop()
