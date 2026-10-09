"""
algorithms_registry.py
-----------------------
Nơi "đóng gói" các thuật toán cụ thể thành class kế thừa PathAlgorithm.
BFSAlgorithm chỉ gọi lại hàm bfs() gốc của bạn B trong grid_bfs.py - không viết lại logic,
chỉ thêm lớp vỏ để đúng chuẩn OOP (đa hình) mà đề bài yêu cầu.

Khi có Dijkstra/A*, chỉ cần thêm class tương tự bên dưới và đăng ký vào ALGORITHMS.
"""

from algorithms.base_algorithm import PathAlgorithm
from algorithms.grid_bfs import bfs as bfs_function


class BFSAlgorithm(PathAlgorithm):
    name = "BFS"

    def find_path(self, grid) -> tuple:
        return bfs_function(grid)


# Đăng ký các thuật toán có sẵn để MainWindow tra theo tên hiển thị trên ControlPanel.
# Khi bạn B thêm Dijkstra/A*, chỉ cần thêm dòng tương ứng ở đây, không cần sửa main_window.py.
ALGORITHMS = {
    "BFS": BFSAlgorithm(),
    # "Dijkstra": DijkstraAlgorithm(),
    # "A*": AStarAlgorithm(),
}
