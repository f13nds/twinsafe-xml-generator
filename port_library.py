"""
端口库：加载 safety_ports.json，为 FB 和 Group 端口提供查询与验证。
"""
import json
import os
from typing import Dict, Any, Optional


class PortLibrary:
    """封装 safety_ports.json 中的端口定义"""

    def __init__(self, json_path: str = None):
        if json_path is None:
            import sys
            if hasattr(sys, '_MEIPASS'):
                json_path = os.path.join(sys._MEIPASS, "safety_ports.json")
            else:
                json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "safety_ports.json")
        abs_path = os.path.abspath(json_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"端口库文件不存在：{abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    @property
    def function_blocks(self) -> Dict[str, Any]:
        return self._data.get("function_blocks", {})

    @property
    def group_ports(self) -> Dict[str, Any]:
        return self._data.get("group_ports", {})

    def get_fb_types(self) -> list:
        """返回所有 FB 类型名称列表"""
        return list(self.function_blocks.keys())

    def get_fb_info(self, fb_type: str) -> Optional[Dict[str, Any]]:
        return self.function_blocks.get(fb_type)

    def get_fb_ports(self, fb_type: str) -> Dict[str, Any]:
        info = self.get_fb_info(fb_type)
        if not info:
            return {}
        return info.get("ports", {})

    def get_fb_type_number(self, fb_type: str) -> Optional[int]:
        info = self.get_fb_info(fb_type)
        return info.get("type") if info else None

    def get_group_imports(self) -> Dict[str, Any]:
        return self.group_ports.get("imports", {})

    def get_group_outputs(self) -> Dict[str, Any]:
        return self.group_ports.get("outputs", {})

    def port_direction(self, fb_type: str, port_name: str) -> Optional[str]:
        ports = self.get_fb_ports(fb_type)
        p = ports.get(port_name)
        return p.get("dir") if p else None

    def port_hex(self, fb_type: str, port_name: str) -> Optional[str]:
        ports = self.get_fb_ports(fb_type)
        p = ports.get(port_name)
        return p.get("hex") if p else None

    def port_dec(self, fb_type: str, port_name: str) -> Optional[int]:
        ports = self.get_fb_ports(fb_type)
        p = ports.get(port_name)
        return p.get("dec") if p else None

    def get_inports(self, fb_type: str) -> Dict[str, Any]:
        return {k: v for k, v in self.get_fb_ports(fb_type).items() if v.get("dir") == "in"}

    def get_outports(self, fb_type: str) -> Dict[str, Any]:
        return {k: v for k, v in self.get_fb_ports(fb_type).items() if v.get("dir") == "out"}


# 单例入口，便于 GUI 与生成器共享
_library: Optional[PortLibrary] = None


def get_port_library(json_path: str = None) -> PortLibrary:
    global _library
    if _library is None:
        _library = PortLibrary(json_path)
    return _library
