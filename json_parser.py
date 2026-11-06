import json
import os

def load_safety_json(json_path: str):
    """
    解析 safety_ports.json 配置文件
    :param json_path: json文件相对/绝对路径
    :return: dict，包含 group_ports、function_blocks
    :raises FileNotFoundError: 文件不存在
    :raises json.JSONDecodeError: json格式错误
    """
    abs_path = os.path.abspath(json_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"JSON文件不存在：{abs_path}")

    with open(abs_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    # 本文件内简易自测（可选）
    data = load_safety_json("safety_ports.json")
    print("简易自测：成功读取，FB列表：", list(data["function_blocks"].keys()))
