from heapq import heappop, heappush
import os
from random import Random

from manim import *


ROAD_MAP = [
    "..........",
    ".##...##..",
    "...#...#..",
    ".#.....#..",
    ".#..##....",
    "...##..#..",
    "..#...#...",
    "..#...#...",
    "..#.......",
    "..........",
]
DELTAS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def make_road(road_map):
    return {
        (row, col)
        for row, line in enumerate(road_map)
        for col, value in enumerate(line)
        if value == "."
    }


def neighbours(position, road, blocked):
    row, col = position
    for delta_row, delta_col in DELTAS:
        neighbour = (row + delta_row, col + delta_col)
        if neighbour in road and neighbour not in blocked:
            yield neighbour


def reachable(start, end, road, blocked):
    seen = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for neighbour in neighbours(current, road, blocked):
            if neighbour not in seen:
                seen.add(neighbour)
                frontier.append(neighbour)
    return end in seen


def make_scenario(road, seed=1):
    rng = Random(seed)
    available = sorted(road)
    start = rng.choice(available)
    end = rng.choice([position for position in available if position != start])
    candidates = [position for position in available if position not in {start, end}]
    blocked = set(rng.sample(candidates, 7))
    while not reachable(start, end, road, blocked):
        blocked.remove(next(iter(blocked)))
    return start, end, blocked


def rebuild_path(parent, end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))


def online_dijkstra(start, end, road, blocked):
    frontier = [(0, start)]
    distances = {start: 0}
    parent = {start: None}
    visits = {start: 1}
    while frontier:
        distance, current = heappop(frontier)
        if distance != distances[current]:
            continue
        if current == end:
            yield current, []
            return rebuild_path(parent, end)
        changed = []
        for neighbour in neighbours(current, road, blocked):
            visits[neighbour] = visits.get(neighbour, 0) + 1
            changed.append((neighbour, visits[neighbour]))
            new_distance = distance + 1
            if new_distance < distances.get(neighbour, float("inf")):
                distances[neighbour] = new_distance
                parent[neighbour] = current
                heappush(frontier, (new_distance, neighbour))
        yield current, changed


def online_a_star(start, end, road, blocked):
    def heuristic(position):
        return abs(position[0] - end[0]) + abs(position[1] - end[1])

    frontier = [(heuristic(start), 0, start)]
    distances = {start: 0}
    parent = {start: None}
    visits = {start: 1}
    while frontier:
        _, distance, current = heappop(frontier)
        if distance != distances[current]:
            continue
        if current == end:
            yield current, []
            return rebuild_path(parent, end)
        changed = []
        for neighbour in neighbours(current, road, blocked):
            visits[neighbour] = visits.get(neighbour, 0) + 1
            changed.append((neighbour, visits[neighbour]))
            new_distance = distance + 1
            if new_distance < distances.get(neighbour, float("inf")):
                distances[neighbour] = new_distance
                parent[neighbour] = current
                heappush(frontier, (new_distance + heuristic(neighbour), new_distance, neighbour))
        yield current, changed


def online_tremaux(start, end, road, blocked):
    stack = [start]
    parent = {start: None}
    visited = {start}
    edge_marks = {}
    visits = {start: 1}
    while stack:
        current = stack[-1]
        if current == end:
            yield current, []
            return rebuild_path(parent, end)
        changed = []
        next_position = None
        for neighbour in neighbours(current, road, blocked):
            edge = frozenset((current, neighbour))
            if edge_marks.get(edge, 0) < 2:
                edge_marks[edge] = edge_marks.get(edge, 0) + 1
                visits[neighbour] = visits.get(neighbour, 0) + 1
                changed.append((neighbour, visits[neighbour]))
                next_position = neighbour
                break
        if next_position is None:
            stack.pop()
            next_position = stack[-1] if stack else current
        elif next_position not in visited:
            visited.add(next_position)
            parent[next_position] = current
            stack.append(next_position)
        yield next_position, changed


def build_board(road, side, center):
    cells = {}
    board = VGroup()
    for row in range(10):
        for col in range(10):
            cell = Square(side_length=side, stroke_color=GREY_B, stroke_width=1)
            cell.move_to(center + np.array(((col - 4.5) * side, (4.5 - row) * side, 0)))
            cell.set_fill("#303640" if (row, col) in road else WHITE, opacity=1)
            cells[(row, col)] = cell
            board.add(cell)
    return board, cells


class Labyrinth(Scene):
    def animate_online_search(self, boards, road, blocked, start, end, searches, counters):
        generators = [search(start, end, road, blocked) for search in searches]
        agents = [Dot(radius=0.06, color=GREEN_C) for _ in boards]
        overlays = [{} for _ in boards]
        visit_counts = [{} for _ in boards]

        for agent, (_, cells) in zip(agents, boards):
            agent.move_to(cells[start].get_center())
        self.add(*agents)

        finished_paths = [None] * len(generators)
        step_counts = [0] * len(generators)
        active = set(range(len(generators)))
        while active:
            animations = []
            for index in tuple(active):
                try:
                    position, changed = next(generators[index])
                except StopIteration as result:
                    finished_paths[index] = result.value
                    active.remove(index)
                    continue
                _, cells = boards[index]
                step_counts[index] += 1
                animations.append(agents[index].animate.move_to(cells[position].get_center()))
                animations.append(counters[index].animate.set_value(step_counts[index]))
                for changed_position, count in changed:
                    visit_counts[index][changed_position] = count
                    if changed_position in {start, end}:
                        continue
                    color = PINK if count == 1 else PURPLE
                    if changed_position not in overlays[index]:
                        mark = cells[changed_position].copy().set_fill(color, opacity=0.9)
                        overlays[index][changed_position] = mark
                        self.add(mark)
                        mark.set_fill(color, opacity=0)
                        animations.append(mark.animate.set_fill(color, opacity=0.9))
                    else:
                        animations.append(overlays[index][changed_position].animate.set_fill(color, opacity=0.9))
            if animations:
                self.play(*animations, run_time=0.2)

        routes = []
        for index, path in enumerate(finished_paths):
            _, cells = boards[index]
            route = VGroup(
                *[
                    Line(cells[first].get_center(), cells[second].get_center(), stroke_color=GREEN_C, stroke_width=3)
                    for first, second in zip(path, path[1:])
                ]
            )
            routes.append(route)
        self.play(*[Create(route) for route in routes], run_time=0.5)

    def construct(self):
        road = make_road(ROAD_MAP)
        seed = int(os.environ.get("MANIM_SCENARIO_SEED", "1"))
        start, end, blocked = make_scenario(road, seed=seed)
        side = 0.29
        centers = [
            LEFT * 3.4 + DOWN * 0.25,
            DOWN * 0.25,
            RIGHT * 3.4 + DOWN * 0.25,
        ]
        boards = [build_board(road, side, center) for center in centers]
        names = ("TRÉMAUX", "DIJKSTRA", "A STAR")
        searches = (online_tremaux, online_dijkstra, online_a_star)

        title = Text("ONLINE SEARCH RACE", font_size=30, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        subtitle = Text("pink = visited once    purple = revisited", font_size=17)
        subtitle.to_edge(DOWN, buff=0.25)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.play(LaggedStart(*[FadeIn(board) for board, _ in boards], lag_ratio=0.15), run_time=1)

        labels = VGroup()
        counters = []
        
        for (board, cells), name in zip(boards, names):
            label = Text(name, font_size=16, weight=BOLD)
            label.next_to(cells[(0, 0)], UP, buff=0.12)
            labels.add(label)
            counter = Integer(0, font_size=18)
            counter.next_to(cells[(9, 0)], DOWN, buff=0.12)
            counters.append(counter)
        self.play(FadeIn(labels))

        obstacle_marks = VGroup(
            *[
                cells[position].copy().set_fill(RED_C, opacity=1)
                for _, cells in boards
                for position in blocked
            ]
        )
        endpoint_marks = VGroup(
            *[
                cells[start].copy().set_fill(GREEN_C, opacity=1)
                for _, cells in boards
            ],
            *[
                cells[end].copy().set_fill(YELLOW_C, opacity=1)
                for _, cells in boards
            ],
        )
        self.play(FadeIn(obstacle_marks), FadeIn(endpoint_marks))
        self.play(*[FadeIn(counter) for counter in counters])
        self.animate_online_search(boards, road, blocked, start, end, searches, counters)
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.5)
    