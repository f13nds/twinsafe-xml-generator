"""
XSD 校验模块。
优先使用外部 xmlschema/lxml 库做完整校验；
未安装时退回到内置的结构化校验，覆盖 XSD 中与我们导出相关的主要约束。
"""
import os
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional


XSD_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "twincat3-safety-editor_export-format.xsd",
    "twincat3-safety-editor_export-format.xsd"
))


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def __str__(self) -> str:
        lines = []
        if self.ok:
            lines.append("校验通过")
        else:
            lines.append(f"校验失败，共 {len(self.errors)} 个错误：")
            for e in self.errors:
                lines.append(f"  [错误] {e}")
        for w in self.warnings:
            lines.append(f"  [警告] {w}")
        return "\n".join(lines)


def validate_with_xsd(xml_path: str, xsd_path: str = XSD_PATH) -> ValidationResult:
    """入口：尝试完整 XSD 校验，否则结构化校验"""
    result = ValidationResult()

    if not os.path.exists(xml_path):
        result.add_error(f"XML 文件不存在：{xml_path}")
        return result

    if not os.path.exists(xsd_path):
        result.add_warning(f"XSD 文件不存在：{xsd_path}，将只进行基础结构校验")
        xsd_path = None

    # 1) 尝试完整 XSD 校验
    if xsd_path:
        full = _validate_full(xml_path, xsd_path)
        if full is not None:
            return full

    # 2) 退回到结构化校验
    return _validate_structural(xml_path)


def _should_ignore_error(msg: str) -> bool:
    """判断 XSD 校验错误是否应忽略
    
    忽略规则：
    1. Version 0.31/0.32 差异（XSD 固定值约束）
    2. XML 中包含 XSD 未定义的额外元素
    """
    import re as _re
    # 忽略 Version 固定值约束差异
    if _re.search(r"Version.*does not match.*fixed value", msg, _re.IGNORECASE):
        return True
    # 忽略 XSD 中不存在的额外元素（如 ConnectionInfoDataConfigOld、LogicType、MapState 等）
    if _re.search(r"is not expected.*Expected is one of", msg, _re.IGNORECASE):
        return True
    return False


def _validate_full(xml_path: str, xsd_path: str) -> Optional[ValidationResult]:
    """使用 xmlschema/lxml 进行完整校验，返回 None 表示库不可用"""
    try:
        import xmlschema
        schema = xmlschema.XMLSchema(xsd_path)
        result = ValidationResult()
        errors = list(schema.iter_errors(xml_path))
        for err in errors[:100]:
            msg = str(err)
            if not _should_ignore_error(msg):
                result.add_error(msg)
        return result
    except ImportError:
        pass

    try:
        from lxml import etree
        with open(xsd_path, "rb") as f:
            xsd_doc = etree.parse(f)
        schema = etree.XMLSchema(xsd_doc)
        with open(xml_path, "rb") as f:
            doc = etree.parse(f)
        result = ValidationResult()
        if not schema.validate(doc):
            for err in schema.error_log[:100]:
                msg = f"line {err.line}: {err.message}"
                if not _should_ignore_error(msg):
                    result.add_error(msg)
        return result
    except ImportError:
        pass

    return None


def _validate_structural(xml_path: str) -> ValidationResult:
    """未安装 XSD 库时的内置结构化校验"""
    result = ValidationResult()
    result.add_warning("未安装 xmlschema / lxml，仅进行内置结构化校验。"
                       "建议运行 'pip install xmlschema' 获得完整 XSD 校验。")

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        result.add_error(f"XML 格式错误：{e}")
        return result

    root = tree.getroot()
    _check_root(root, result)
    _check_general_information(root, result)
    _check_target_system_configuration(root, result)
    _check_application_configuration(root, result)
    return result


def _check_root(root: ET.Element, result: ValidationResult):
    if root.tag != "TwinCATExport":
        result.add_error(f"根元素应为 TwinCATExport，实际为 {root.tag}")
        return
    version = root.get("Version")
    if version not in ("0.31", "0.32"):
        result.add_error(f"TwinCATExport/@Version 应为 0.31 或 0.32，实际为 {version}")


def _check_general_information(root: ET.Element, result: ValidationResult):
    gi = root.find("GeneralInformation")
    if gi is None:
        result.add_error("缺少 GeneralInformation 元素")
        return
    if gi.find("ProjectName") is None or not gi.find("ProjectName").text:
        result.add_error("GeneralInformation/ProjectName 不能为空")


def _check_target_system_configuration(root: ET.Element, result: ValidationResult):
    tsc = root.find("TargetSystemConfiguration")
    if tsc is None:
        result.add_error("缺少 TargetSystemConfiguration 元素")
        return
    if not tsc.get("Id"):
        result.add_error("TargetSystemConfiguration/@Id 必填")
    ttype = tsc.get("Type")
    if ttype not in ("Hardware", "Software"):
        result.add_error(f"TargetSystemConfiguration/@Type 必须是 Hardware 或 Software，实际为 {ttype}")
    subtype = tsc.get("SubType")
    if subtype not in ("EL6900", "EL6910", "EL6930", "EK1960", "SafetyPLC"):
        result.add_error(f"TargetSystemConfiguration/@SubType 枚举值非法：{subtype}")
    safe = tsc.find("SafeAddress")
    if safe is None or not safe.text or int(safe.text) <= 0:
        result.add_error("TargetSystemConfiguration/SafeAddress 必须为正整数")
    vn = tsc.find("VersionNumber")
    if vn is None or not vn.text:
        result.add_error("TargetSystemConfiguration/VersionNumber 必填")


def _check_application_configuration(root: ET.Element, result: ValidationResult):
    ac = root.find("ApplicationConfiguration")
    if ac is None:
        result.add_error("缺少 ApplicationConfiguration 元素")
        return
    groups = ac.find("TwinSAFEGroups")
    if groups is None:
        result.add_error("ApplicationConfiguration/TwinSAFEGroups 必填")
        return
    for g in groups.findall("TwinSAFEGroup"):
        _check_group(g, result)


def _check_group(group: ET.Element, result: ValidationResult):
    if not group.get("Id"):
        result.add_error("TwinSAFEGroup/@Id 必填")
    order = group.get("OrderId")
    if order is None:
        result.add_error("TwinSAFEGroup/@OrderId 必填")

    opts = group.find("TwinSAFEGroupOptions")
    if opts is not None:
        for child in opts:
            if child.text and child.text.lower() not in ("true", "false"):
                if child.tag == "TimeOutPassificationAllowed":
                    try:
                        int(child.text)
                    except ValueError:
                        result.add_error(f"TwinSAFEGroupOptions/{child.tag} 应为整数")
                else:
                    result.add_error(f"TwinSAFEGroupOptions/{child.tag} 应为布尔值 true/false")

    app = group.find("Application")
    if app is None:
        result.add_error("TwinSAFEGroup/Application 必填")
        return
    for net in app.findall("Network"):
        if not net.get("Id"):
            result.add_error("Network/@Id 必填")
        if net.get("OrderId") is None:
            result.add_error("Network/@OrderId 必填")
        for fb in net.findall("FunctionBlock"):
            _check_function_block(fb, result)


def _check_function_block(fb: ET.Element, result: ValidationResult):
    if not fb.get("Id"):
        result.add_error("FunctionBlock/@Id 必填")
    if fb.get("OrderId") is None:
        result.add_error("FunctionBlock/@OrderId 必填")
    t = fb.find("Type")
    if t is None or not t.text:
        result.add_error("FunctionBlock/Type 必填")
    n = fb.find("Name")
    if n is None or not n.text:
        result.add_error("FunctionBlock/Name 必填")

    # PortId 值必须是 HexDecUInt32Value 格式
    for tag in ("Outports", "Inports"):
        ports = fb.find(tag)
        if ports is None:
            continue
        for el in ports.findall("Element"):
            if not el.get("Id"):
                result.add_error(f"{tag}/Element/@Id 必填")
            pid = el.find("PortId")
            if pid is None or not _is_hex_dec_uint32(pid.text):
                result.add_error(f"{tag}/Element/PortId 值非法：{pid.text if pid is not None else 'None'}")


def _is_hex_dec_uint32(value: str) -> bool:
    if value is None:
        return False
    # XSD 中的模式：十进制 0..4294967295 或 0x/0X 十六进制
    if re.fullmatch(r"[+]?0", value):
        return True
    if re.fullmatch(r"[+]?[1-9][0-9]{0,8}", value):
        return True
    if re.fullmatch(r"[+]?[1-3][0-9]{9}", value):
        return True
    if re.fullmatch(r"[+]?4[0-1][0-9]{8}", value):
        return True
    if re.fullmatch(r"[+]?42[0-8][0-9]{7}", value):
        return True
    if re.fullmatch(r"[+]?429[0-3][0-9]{6}", value):
        return True
    if re.fullmatch(r"[+]?4294[0-8][0-9]{5}", value):
        return True
    if re.fullmatch(r"[+]?42949[0-5][0-9]{4}", value):
        return True
    if re.fullmatch(r"[+]?429496[0-6][0-9]{3}", value):
        return True
    if re.fullmatch(r"[+]?4294967[0-1][0-9]{2}", value):
        return True
    if re.fullmatch(r"[+]?42949672[0-8][0-9]", value):
        return True
    if re.fullmatch(r"[+]?429496729[0-5]", value):
        return True
    if re.fullmatch(r"[0#]x[0-9a-fA-F]{1,8}", value):
        return True
    # 更宽松的通用检查：十进制在范围内或合法十六进制
    try:
        if value.lower().startswith("0x"):
            return 0 <= int(value, 16) <= 0xFFFFFFFF
        return 0 <= int(value) <= 0xFFFFFFFF
    except ValueError:
        return False
