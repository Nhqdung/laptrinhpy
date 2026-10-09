from collections import deque


# =========================
# LỚP LUOI
# =========================
class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

        # Các ô vật cản
        self.obstacles = set()

        # Điểm bắt đầu
        self.start = None

        # Điểm đích
        self.end = None

    # Kiểm tra ô có nằm trong lưới không
    def in_grid(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    # Kiểm tra ô có phải vật cản không
    def is_obstacle(self, row, col):
        return (row, col) in self.obstacles

    # Lấy các ô hàng xóm
    def get_neighbors(self, row, col):
        directions = [
            (-1, 0),  # lên
            (1, 0),   # xuống
            (0, -1),  # trái
            (0, 1)    # phải
        ]

        neighbors = []

        for dr, dc in directions:
            nr = row + dr
            nc = col + dc

            if self.in_grid(nr, nc) and not self.is_obstacle(nr, nc):
                neighbors.append((nr, nc))

        return neighbors


# =========================
# THUẬT TOÁN BFS
# =========================
def bfs(grid):

    start = grid.start
    end = grid.end

    # Nếu chưa có điểm đầu hoặc điểm đích
    if start is None or end is None:
        return [], []

    # Hàng đợi BFS
    queue = deque()

    # Đưa điểm bắt đầu vào hàng đợi
    queue.append(start)

    # Lưu các ô đã duyệt
    visited = set()
    visited.add(start)

    # Lưu ô cha
    parent = {}

    # Lưu thứ tự các ô đã duyệt
    visited_order = []

    # Bắt đầu BFS
    while queue:

        # Lấy ô đầu hàng đợi
        current = queue.popleft()

        # Lưu lại thứ tự duyệt
        visited_order.append(current)

        # Nếu đã đến đích
        if current == end:
            break

        row, col = current

        # Lấy các ô hàng xóm
        for neighbor in grid.get_neighbors(row, col):

            # Nếu ô này chưa được duyệt
            if neighbor not in visited:

                visited.add(neighbor)

                # Lưu ô cha
                parent[neighbor] = current

                # Đưa vào hàng đợi
                queue.append(neighbor)

    # Nếu không tìm thấy đường đi
    if end not in visited:
        return visited_order, []


    path = []

    current = end

    while current != start:

        path.append(current)

        current = parent[current]

   
    path.append(start)

    
    path.reverse()

    return visited_order, path


def main():

    
    grid = Grid(4, 5)

   
    grid.start = (0, 0)

    
    grid.end = (3, 4)

   
    grid.obstacles = {
        (0, 1),
        (1, 1),
        (2, 3)
    }

    
    visited_order, path = bfs(grid)


    print("===== TIM DUONG BANG BFS =====")

    print("Diem bat dau:", grid.start)

    print("Diem dich:", grid.end)

    print("\nCac o vat can:")
    print(grid.obstacles)

    print("\nThu tu cac o da duyet:")
    print(visited_order)

    print("\nDuong di tim duoc:")

    if path:
        print(path)
    else:
        print("Khong tim thay duong di")



if __name__ == "__main__":
    main()