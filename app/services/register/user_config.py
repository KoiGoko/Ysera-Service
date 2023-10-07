import heapq


class Node:
    def __init__(self, row, col, evacuation_cost, pollution_influence):
        self.row = row
        self.col = col
        self.evacuation_cost = evacuation_cost
        self.pollution_influence = pollution_influence
        self.total_cost = float('inf')  # 初始化为无穷大，表示未知的路径代价
        self.parent = None


def astar(graph, start, goal):
    open_set = []
    closed_set = set()

    heapq.heappush(open_set, (start.total_cost, start))

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)

        if current_node == goal:
            path = []
            while current_node:
                path.append((current_node.row, current_node.col))
                current_node = current_node.parent
            return path[::-1]

        closed_set.add(current_node)

        for neighbor in get_neighbors(current_node, graph):
            if neighbor in closed_set:
                continue

            tentative_cost = current_node.total_cost + neighbor.evacuation_cost + neighbor.pollution_influence

            if tentative_cost < neighbor.total_cost:
                neighbor.total_cost = tentative_cost
                neighbor.parent = current_node

                if neighbor not in open_set:
                    heapq.heappush(open_set, (neighbor.total_cost, neighbor))

    return None


def get_neighbors(node, graph):
    neighbors = []
    rows, cols = len(graph), len(graph[0])

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for dr, dc in directions:
        nr, nc = node.row + dr, node.col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append(Node(nr, nc, graph[nr][nc][0], graph[nr][nc][1]))

    return neighbors


# 示例用法
start_node = Node(0, 0, 1, 0)
goal_node = Node(4, 4, 1, 0)

# 示例地图，每个格子表示为 (evacuation_cost, pollution_influence)
map_graph = [
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
    [(1, 0), (1, 0), (1, 0), (1, 0), (1, 0)]
]

path = astar(map_graph, start_node, goal_node)
print(path)
