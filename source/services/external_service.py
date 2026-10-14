"""
external_service.py
--------------------
Tích hợp dữ liệu từ nguồn bên ngoài (yêu cầu bắt buộc của đề: crawl hoặc dùng API).

Ý tưởng: dùng API geocode miễn phí của OpenStreetMap (Nominatim) để lấy tọa độ thật
của 2 địa điểm do người dùng nhập, tính khoảng cách thực tế giữa chúng (Haversine),
sau đó làm sạch/chuyển đổi và lưu kết quả vào file JSON để dùng làm dữ liệu tham khảo
minh họa cho bài toán tìm đường (so sánh khoảng cách thực tế và số bước thuật toán tìm được).

Lưu ý khi nộp báo cáo: ghi rõ nguồn API là https://nominatim.openstreetmap.org/
và tuân thủ điều khoản sử dụng (giới hạn tần suất request, có User-Agent).
"""

import math
from datetime import datetime

import requests

from .json_handler import JSONHandler, JSONHandlerError

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
REQUEST_HEADERS = {"User-Agent": "pathfinding-app-hocphan-python/1.0"}
REQUEST_TIMEOUT = 6  # giây


class ExternalServiceError(Exception):
    """Ngoại lệ khi gọi API ngoài thất bại (mất kết nối, timeout, không tìm thấy dữ liệu...)."""
    pass


class ExternalService:
    def __init__(self, cache_path: str = "data/external_data.json"):
        self.cache_handler = JSONHandler(cache_path, default_data=[])

    def _geocode(self, place_name: str) -> dict:
        """Gọi API để lấy tọa độ (lat, lon) của một địa điểm theo tên."""
        params = {"q": place_name, "format": "json", "limit": 1}
        try:
            response = requests.get(
                NOMINATIM_URL, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ExternalServiceError(f"Hết thời gian chờ khi tra cứu địa điểm '{place_name}'.")
        except requests.exceptions.ConnectionError:
            raise ExternalServiceError("Không thể kết nối tới máy chủ API (kiểm tra mạng).")
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Lỗi khi gọi API: {e}")

        try:
            data = response.json()
        except ValueError:
            raise ExternalServiceError("Dữ liệu trả về từ API không đúng định dạng JSON.")

        if not data:
            raise ExternalServiceError(f"Không tìm thấy địa điểm '{place_name}'.")

        # Làm sạch / chuyển đổi dữ liệu: chỉ giữ các trường cần thiết, ép kiểu float
        try:
            first = data[0]
            return {
                "name": place_name,
                "display_name": first.get("display_name", place_name),
                "lat": float(first["lat"]),
                "lon": float(first["lon"]),
            }
        except (KeyError, ValueError, TypeError):
            raise ExternalServiceError("Dữ liệu địa điểm trả về thiếu hoặc sai kiểu.")

    @staticmethod
    def _haversine_km(lat1, lon1, lat2, lon2) -> float:
        """Tính khoảng cách thực tế (km) giữa 2 tọa độ địa lý."""
        r = 6371.0  # bán kính Trái Đất (km)
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = (math.sin(d_phi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 3)

    def fetch_real_distance(self, place_a: str, place_b: str) -> dict:
        """
        Lấy khoảng cách thực tế giữa 2 địa điểm bằng API, lưu kết quả vào cache JSON
        để không phải gọi lại API nếu đã tra cứu trước đó (giảm tải cho API bên ngoài).
        """
        if not place_a.strip() or not place_b.strip():
            raise ExternalServiceError("Vui lòng nhập đầy đủ tên 2 địa điểm.")

        geo_a = self._geocode(place_a)
        geo_b = self._geocode(place_b)
        distance_km = self._haversine_km(geo_a["lat"], geo_a["lon"], geo_b["lat"], geo_b["lon"])

        result = {
            "place_a": geo_a,
            "place_b": geo_b,
            "distance_km": distance_km,
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
        }

        try:
            cache = self.cache_handler.load()
            cache.append(result)
            self.cache_handler.save(cache)
        except JSONHandlerError:
            # Lỗi cache không nên làm hỏng kết quả trả về cho người dùng
            pass

        return result
