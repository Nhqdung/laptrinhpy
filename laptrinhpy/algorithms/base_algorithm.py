"""
base_algorithm.py
------------------
Lớp thuật toán trừu tượng cho bài toán tìm đường trên lưới.
Mỗi thuật toán cụ thể (BFS, Dijkstra, A*...) kế thừa PathAlgorithm và cài đặt find_path().
Đây là điểm thể hiện tính đa hình: MainWindow chỉ gọi algorithm.find_path(grid)
mà không cần biết bên trong là thuật toán nào.
"""

from abc import ABC, abstractmethod


class PathAlgorithm(ABC):
    name = "Abstract"

    @abstractmethod
    def find_path(self, grid) -> tuple:
        """
        grid: đối tượng Grid (rows, cols, start, end, obstacles).
        Trả về (visited_order, path):
            visited_order: list các ô (row, col) theo đúng thứ tự đã duyệt.
            path: list các ô (row, col) từ start đến end, rỗng nếu không tìm thấy.
        """
        raise NotImplementedError
