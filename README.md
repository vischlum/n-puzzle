# n-puzzle
This a [School 42](https://www.42.fr/) project to use the [A\* algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) to solve [n-puzzles](https://en.wikipedia.org/wiki/15_puzzle). The PDF of the subject is [here](https://cdn.intra.42.fr/pdf/pdf/17244/en.subject.pdf).   
Due to the use of [PEP 585](https://www.python.org/dev/peps/pep-0585) (type hinting generics in standard collections) and [`@cache`](https://docs.python.org/3/library/functools.html#functools.cache), [Python 3.9](https://docs.python.org/3/whatsnew/3.9.html) is required.  
The code has been formatted with [black](https://github.com/psf/black). I used [pylint](https://pylint.org/) for linting and [mypy](https://github.com/python/mypy) for type checking, and made sure that both `pylint *.py` and `mypy --strict --pretty *.py` don't return any issues.

## How to run
1. Create a virtual environment: `python3.9 -m venv env`
2. Activate the virtual environment: `source env/bin/activate`
3. Install the dependencies: `python3.9 -m pip install -r requirements.txt`
4. Run with `./main.py --file puzzles/ok/3-random_1.txt`

The script has various flags:
- `--file` (or `-f`) to choose the file with the puzzle to be solved
- `--size` (or `-s`) to randomly generate a puzzle (instead of using a file). The size can be up to 7, but puzzles with a size above 4 can only be reliably solved with Linear Conflicts + greedy search
- `--heuristic` to choose the heuristic to be used by A\*. Options are `uniform`, `hamming`, `manhattan` (default) and `linear`
- `--greedy` (or `-g`) to enable greedy search
- `--shape` to choose the shape of the solution. Options are `ascending`, `descending`, `spiral` (default) and `random`
- `--visualiser` (or `-v`) to enable the GUI visualiser for the solution

## A\* and heuristics
A\* is a graph-traversal algorithm that uses a heuristic function to get the best result. At each iteration of its main loop, A\* selects the path that minimizes *f(n) = g(n) + h(n)*:
- *n* is the next node on the path
- *g(n)* is the cost of the path from the start node to *n*
- *h(n)* is a heuristic function that estimates the cost of the cheapest path from *n* to the goal

A heuristic function is said to be *admissible* if it never overestimates the actual cost to get to the goal. With an admissible heuristic, A\* is sure to return a least-cost path from start to goal.

When using greedy search, A\* ignores the path cost to the current node and will always expand the nearest node to the goal. In effect, *f(n) = h(n)* (there's no *g(n)*). This makes the search much faster but the solution is suboptimal, requiring many more moves than with a non-greedy search.

### Heuristics used
- *Uniform Cost*: not an actual heuristic, because uniform cost search is uninformed. This means that *f(n) = g(n)* (there's no *h(n)*). A\* will eventually find the same solution as with a proper heuristic, but will have to go through many more nodes. Basically, this turns A\* into [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm).
- *Hamming Distance*: the number of tiles not in their final position.
- *Manhattan Distance*: the sum of the minimal number of moves necessary for each tile to get to its final position.
- *Linear Conflicts*: this one is often badly explained, so here's the definition from the [original paper (PDF)](https://cse.sc.edu/~mgv/csce580sp15/gradPres/HanssonMayerYung1992.pdf): 
> Two tiles *tj* and *tk* are in a *linear conflict* if *tj* and *tk* are in the same line, the goal position of *tj* and *tk* are both in that line, *tj* is to the right of *tk*, and the goal position of *tj* is to the left of the goal position of *tk*.

#### A note on Linear Conflicts
Most explanations of Linear Conflicts seem satisfied with simply returning the total number of conflicts on the line. But to guarantee that Linear Conflicts is admissible, it must return the lowest number of moves to solve all the linear conflicts in a given line. That's why after finding all the conflicts in a line, it must first remove the tile with the most conflicts and start another search for conflicts until none of them remains in the line.  

This can be easily verified:
1. Edit [`get_conflicts_in_line()`](heuristics.py)
```python
    # if max(conflicts) != 0:
    #     index = conflicts.index(max(conflicts))
    #     tmp = list(grid_line)
    #     tmp[index] = -1
    #     grid_line = tuple(tmp)
    #     conflicts_in_line += 1
    #     return get_conflicts_in_line(size, grid_line, goal_line, conflicts_in_line)
    conflicts_in_line = sum(conflicts)
```
2. Test with `./main.py -f puzzles/ok/4-random_1.txt --heuristic linear`
3. A\* finds a solution in 46 moves (instead of 44): since it didn't return a least-cost path from start to goal, this simplified Linear Conflicts is not an admissible heuristic.

### Results with various heuristics
- Time complexity is the total number of states ever selected in the opened set
- Size complexity is the maximum number of states ever represented in memory at the same time during the search
- CPU time (measured with the `time` shell command) is only given as an estimate, to better see the benefit of a good heuristic

The puzzles used were randomly generated with the [script given by the school](puzzles/npuzzle-gen.py).

#### Results for 8-Puzzles
| Puzzle | Heuristic | Moves | Time complexity | Size complexity | CPU time |
|--------|-----------|-------|-----------------|-----------------|----------|
| [3-random_1.txt](puzzles/ok/3-random_1.txt)                               |
|        | Uniform   | 24    | 146 310         | 152 860         | 1.7s     |
|        | Hamming   | 24    | 18 751          | 27 384          | 0.3s     |
|        | Manhattan | 24    | 703             | 1 160           | 0.2s     |
|        | Linear    | 24    | 367             | 613             | 0.2s     |
| [3-random_2.txt](puzzles/ok/3-random_2.txt)                               |
|        | Uniform   | 24    | 144 430         | 151 363         | 1.6s     |
|        | Hamming   | 24    | 13 711          | 20 677          | 0.4s     |
|        | Manhattan | 24    | 543             | 859             | 0.2s     |
|        | Linear    | 24    | 374             | 583             | 0.2s     |
| [3-random_3.txt](puzzles/ok/3-random_3.txt)                               |
|        | Uniform   | 12    | 2 483           | 3 778           | 0.1s     |
|        | Hamming   | 12    | 112             | 186             | 0.1s     |
|        | Manhattan | 12    | 19              | 35              | 0.1s     |
|        | Linear    | 12    | 19              | 35              | 0.1s     |
| [3-random_4.txt](puzzles/ok/3-random_4.txt)                               |
|        | Uniform   | 20    | 45 033          | 60 683          | 0.5s     |
|        | Hamming   | 20    | 2 524           | 4 028           | 0.2s     |
|        | Manhattan | 20    | 181             | 306             | 0.1s     |
|        | Linear    | 20    | 151             | 247             | 0.1s     |
| [3-random_5.txt](puzzles/ok/3-random_5.txt)                               |
|        | Uniform   | 12    | 1 497           | 2 389           | 0.1s     |
|        | Hamming   | 12    | 78              | 136             | 0.1s     |
|        | Manhattan | 12    | 15              | 27              | 0.1s     |
|        | Linear    | 12    | 15              | 27              | 0.1s     |

8-Puzzles are simple enough that even a basic heuristic like the Hamming Distance can do the job. There's a large difference in term of evaluated nodes (time complexity) compared to Linear Conflicts, but the difference in CPU time in minimal.

#### Results for 15-Puzzles
Uniform and Hamming Distance are not used here, because they're completely inadequate to solve 15-Puzzles within a reasonable timeframe/RAM usage.  
For Linear Conflicts, the second CPU time is with [`@cache`](https://docs.python.org/3/library/functools.html#functools.cache) disabled.

| Puzzle | Heuristic | Moves | Time complexity | Size complexity | CPU time |
|--------|-----------|-------|-----------------|-----------------|----------|
| [4-random_1.txt](puzzles/ok/4-random_1.txt)                               |
|        | Manhattan | 44    | 1 724 006       | 3 212 048       | 55s      |
|        | Linear    | 44    | 171 056         | 323 198         | 10s / 19s|
| [4-random_2.txt](puzzles/ok/4-random_2.txt)                               |
|        | Manhattan | 58    | 2 163 847       | 4 136 348       | 72s      |
|        | Linear    | 58    | 538 016         | 1 019 968       | 35s / 55s|
| [4-random_3.txt](puzzles/ok/4-random_3.txt)                               |
|        | Manhattan | 52    | 1 100 615       | 2 076 365       | 37s      |
|        | Linear    | 52    | 178 430         | 339 766         | 10s / 19s|
| [4-random_4.txt](puzzles/ok/4-random_4.txt)                               |
|        | Manhattan |  No results after 15 minutes and 10 GB of RAM        |
|        | Linear    | 60    | 3 081 169       | 5 723 198       | 200s / 290s|
| [4-random_5.txt](puzzles/ok/4-random_5.txt)                               |
|        | Manhattan | No results after 15 minutes and 10 GB of RAM         |
|        | Linear    | 58    | 2 443 951       | 4 425 050       | 155s / 255s|

#### Comparison between standard and greedy search
| Puzzle | Heuristic | Moves | Time complexity | Size complexity | CPU time |
|--------|-----------|-------|-----------------|-----------------|----------|
| [3-random_1.txt](puzzles/ok/3-random_1.txt)                               |
|        | Uniform   | 24    | 146 310         | 152 860         | 1.7s     |
|| Uniform + Greedy  | 2010  | 26 558          | 45 749          | 0.4s     |
|        | Hamming   | 24    | 18 751          | 27 384          | 0.3s     |
|| Hamming + Greedy  | 44    | 336             | 533             | 0.1s     |
|        | Manhattan | 24    | 703             | 1 160           | 0.2s     |
|| Manhattan + Greedy| 64    | 230             | 373             | 0.1s     |
|        | Linear    | 24    | 367             | 613             | 0.2s     |
|| Linear + Greedy   | 28    | 38              | 67              | 0.1s     |
| [4-random_1.txt](puzzles/ok/4-random_1.txt)                               |
|| Hamming + Greedy  | 586   | 5 880           | 12 142          | 0.3s     |
|        | Manhattan | 44    | 1 724 006       | 3 212 048       | 55s      |
|| Manhattan + Greedy| 270   | 3682            | 7 021           | 0.3s     |
|        | Linear    | 44    | 171 056         | 323 198         | 10s / 19s|
|| Linear + Greedy   | 64    | 121             | 259             | 0.1s     |

## Ressources
- [*Introduction to A\**](https://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html)
- Slocum, Jerry and Weisstein, Eric W. "15 Puzzle." From MathWorld--A Wolfram Web Resource. https://mathworld.wolfram.com/15Puzzle.html 
- Some general overviews of using A\* to solve N-Puzzles:
    - [*Implementing A-star(A\*) to solve N-Puzzle*](https://algorithmsinsight.wordpress.com/graph-theory-2/a-star-in-general/implementing-a-star-to-solve-n-puzzle/)
    - [*Solving the 15 Puzzle*](https://michael.kim/blog/puzzle)
    - [*15 Puzzle Solver in C Using Literate Programming* (PDF)](https://kenogo.org/literate_programming/15_puzzle_solver.pdf)
- Linear Conflicts is often poorly (and wrongly) explained. This [article](https://medium.com/swlh/looking-into-k-puzzle-heuristics-6189318eaca2) and the [original paper](https://cse.sc.edu/~mgv/csce580sp15/gradPres/HanssonMayerYung1992.pdf) made it click for me.