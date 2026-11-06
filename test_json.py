import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from json_parser import load_safety_json

def test_parse_safety_json():
    print("===== 开始测试解析 safety_ports.json =====")
    cfg = load_safety_json("safety_ports.json")

    # 打印 group_ports -> imports
    print("\n【Group Imports】")
    imports = cfg["group_ports"]["imports"]
    for name, item in imports.items():
        print(f"  {name:12s} | hex={item['hex']}, dec={item['dec']}")

    # 打印 group_ports -> outputs
    print("\n【Group Outputs】")
    outputs = cfg["group_ports"]["outputs"]
    for name, item in outputs.items():
        print(f"  {name:12s} | hex={item['hex']}, dec={item['dec']}")

    # 打印 function_blocks
    print("\n【Function Blocks】")
    for fb_name, fb_info in cfg["function_blocks"].items():
        print(f"\n  FB: {fb_name} | type={fb_info['type']}, subtype={fb_info['subtype']}")
        for port_name, port_info in fb_info["ports"].items():
            print(f"      port:{port_name:12s} | dir={port_info['dir']}, hex={port_info['hex']}, dec={port_info['dec']}")

    print("\n===== 解析完成，无异常 =====")

if __name__ == "__main__":
    test_parse_safety_json()
