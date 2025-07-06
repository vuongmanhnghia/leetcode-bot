import csv


def load_leetcode_data(csv_file):
    """
    Load toàn bộ dữ liệu CSV vào dictionary để truy cập nhanh

    Args:
        csv_file (str): Đường dẫn đến file CSV

    Returns:
        dict: Dictionary với key là ID, value là URL
    """
    leetcode_data = {}

    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                leetcode_data[int(row["id"])] = row["url"]

        return leetcode_data

    except Exception as e:
        print(f"Lỗi khi load dữ liệu: {e}")
        return {}


def get_url_from_data(leetcode_data, problem_id) -> str:
    """
    Lấy URL từ dictionary đã load sẵn

    Args:
        leetcode_data (dict): Dictionary chứa dữ liệu ID -> URL
        problem_id (int): ID của problem

    Returns:
        str: URL của problem, hoặc None nếu không tìm thấy
    """
    return leetcode_data.get(int(problem_id))


# Ví dụ sử dụng
if __name__ == "__main__":
    data = load_leetcode_data("leetcode_filter.csv")

    # Test với nhiều ID
    test_ids = [1, 2, 3, 100, 999]
    for pid in test_ids:
        url = get_url_from_data(data, pid)
        if url:
            print(f"Problem {pid}: {url}")
        else:
            print(f"Problem {pid}: Không tìm thấy")
