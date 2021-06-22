"""
A basic visualiser (using PySimpleGUI) to showcase the solving process of A*
"""

import PySimpleGUI as sg  # type: ignore


def get_heuristic_fullname(heuristic: str, greedy: bool) -> str:
    """
    Returns the full name of the heuristic, for a cleaner display
    """
    heuristics = {
        "uniform": "Uniform Cost",
        "hamming": "Hamming Distance",
        "manhattan": "Manhattan Distance",
        "linear": "Linear Conflicts",
    }

    heuristic_fullname = heuristics.get(heuristic, "Manhattan Distance")

    if greedy:
        heuristic_fullname += " (Greedy)"

    return heuristic_fullname


def generate_grid_layout(
    size: int, solution_line: tuple[int, ...]
) -> list[list[sg.PySimpleGUI.Text]]:
    """
    Generates the layout for our puzzle grid
    """
    layout: list[list[sg.PySimpleGUI.Text]] = [[] for x in range(size)]
    max_width: int = len(str(size * size)) + 1

    for row in range(size):
        for col in range(size):
            index = col + (row * size)
            layout[row].append(
                sg.Text(
                    solution_line[index],
                    size=(max_width, 1),
                    key=str(index),
                    font=("Arial", 32),
                )
            )

    return layout


def results_visualiser(
    size: int, solution: list[tuple[int, ...]], heuristic: str, shape: str, greedy: bool
) -> None:
    """
    Opens a new window and allows the user to step through the solving process
    """
    step = 0
    number_of_moves = len(solution)

    print(
        """\n\033[4mNavigate with the arrow keys:\033[m
    Left => Previous\tRight => Next
    Up => First\t\tDown => Last
    """
    )

    sg.theme("SystemDefaultForReal")
    layout = [
        [
            sg.Frame(
                f"Step {step + 1} / {number_of_moves}",
                key="-FRAME-",
                layout=generate_grid_layout(size, solution[step]),
            )
        ],
        [sg.Text(f"Goal shape: {shape.capitalize()}")],
        [sg.Text(f"Heuristic: {get_heuristic_fullname(heuristic, greedy)}")],
        [
            sg.Button("First"),
            sg.Button("<", key="-PREVIOUS-"),
            sg.Button(">", key="-NEXT-"),
            sg.Button("Last"),
        ],
    ]

    # Create the Window
    window = sg.Window(
        "N-Puzzle visualiser",
        layout,
        element_justification="center",
        return_keyboard_events=True,
    )

    # Event Loop to process "events"
    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, "q", "q:24"):
            break
        if event in ("First", "Up:38", "Up:111"):
            step = 0
        if event in ("-PREVIOUS-", "Left:37", "Left:113"):
            if step > 0:
                step -= 1
        if event in ("-NEXT-", "Right:39", "Right:114"):
            if step < number_of_moves - 1:
                step += 1
        if event in ("Last", "Down:40", "Down:116"):
            step = number_of_moves - 1

        window["-FRAME-"].update(f"Step {step + 1} / {number_of_moves}")

        for row in range(size):
            for col in range(size):
                index = col + (row * size)
                window[str(index)].update(solution[step][index])

    window.close()
