# -*- coding: utf-8 -*-
"""ESI 文件解析器 - 支持 Beckhoff、Hollysys、INOVANCE 格式"""
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional


def get_module_ident(device) -> str:
    """获取 FSOE-Slot 的 ModuleIdent 作为 SubType 依据"""
    # 优先查找 FSoE 相关的 Module
    for m in device.iter("Module"):
        type_el = m.find("Type")
        if type_el is not None:
            type_text = (type_el.text or "").upper()
            module_ident = type_el.get("ModuleIdent", "")
            if "FSOE" in type_text or "FSoE" in type_text:
                return module_ident
    
    # Beckhoff: 从 Slot 获取
    for slot in device.iter("Slot"):
        name = slot.findtext("Name", "").strip()
        if "FSOE" in name.upper():
            return slot.findtext("ModuleIdent", "").strip()
    
    # Hollysys: 直接从 Slot 获取
    for slot in device.iter("Slot"):
        ident = slot.findtext("ModuleIdent", "").strip()
        if ident:
            return ident
    return ""


def get_subtype_value(ident: str) -> int:
    """将 ModuleIdent 转换为 SubType 数值"""
    if not ident:
        return 0
    try:
        return int(ident.replace("#x", "0x"), 16)
    except:
        return 0


def get_vendor_id(root) -> int:
    """从 ESI 文件获取 VendorId"""
    vendor = root.find(".//Vendor")
    if vendor is not None:
        id_elem = vendor.find("Id")
        if id_elem is not None and id_elem.text:
            try:
                return int(id_elem.text.replace("#x", "0x"), 16)
            except:
                pass
    return 2  # 默认 Beckhoff


def parse_pdo_elements(pdo_elem) -> List[Dict[str, Any]]:
    """解析 PDO 元素"""
    elements = []
    for entry in pdo_elem.findall("Entry"):
        # 支持 <Name> 和 <Name LcId="1033"> 两种格式
        name = ""
        for n in entry.findall("Name"):
            lc = n.get("LcId", "")
            if lc == "1033":
                name = n.text or ""
                break
            elif not lc:
                name = n.text or ""
        
        if not name or name == "Reserved":
            continue
        
        elem = {
            "Name": name,
            "Index": entry.findtext("Index", ""),
            "SubIndex": entry.findtext("SubIndex", ""),
            "BitLen": entry.findtext("BitLen", ""),
            "DataType": entry.findtext("DataType", ""),
        }
        elements.append(elem)
    return elements


def parse_pdo_by_sm(module_or_device) -> tuple:
    """
    根据 SM 属性解析 PDO 通道方向
    SM="2" → 输出通道 (FB输出, 命令到设备)
    SM="3" → 输入通道 (FB输入, 状态从设备)
    
    返回: (input_elements, output_elements)
    """
    input_elements = []   # SM=3, FB输入, 设备状态
    output_elements = []  # SM=2, FB输出, 命令
    
    for pdo in module_or_device.findall("RxPdo"):
        sm = pdo.get("Sm", "")
        elements = parse_pdo_elements(pdo)
        if sm == "2":
            # SM=2 是输出通道 (FB输出)
            output_elements.extend(elements)
        elif sm == "3":
            # SM=3 是输入通道 (FB输入)
            input_elements.extend(elements)
        else:
            # 默认 RxPdo 视为输出通道
            output_elements.extend(elements)
    
    for pdo in module_or_device.findall("TxPdo"):
        sm = pdo.get("Sm", "")
        elements = parse_pdo_elements(pdo)
        if sm == "2":
            # SM=2 是输出通道 (FB输出)
            output_elements.extend(elements)
        elif sm == "3":
            # SM=3 是输入通道 (FB输入)
            input_elements.extend(elements)
        else:
            # 默认 TxPdo 视为输入通道
            input_elements.extend(elements)
    
    return input_elements, output_elements


def parse_device(device, root=None, vendor_id: int = 2) -> List[Dict[str, Any]]:
    """解析单个设备（支持 Beckhoff、Hollysys、INOVANCE 格式）
    
    Returns:
        List[Dict] - 可能返回多个设备变体（如 INOVANCE 的 FSoE-SRA 和 FSoE-noSRA）
    """
    results = []
    if root is None:
        root = device
    
    type_el = device.find("Type")
    if type_el is None:
        return []
    
    base_name = type_el.text or ""
    product_code_hex = type_el.get("ProductCode", "")
    revision_no_hex = type_el.get("RevisionNo", "")
    
    # 转换为十进制
    try:
        product_code = int(product_code_hex.replace("#x", "0x"), 16)
    except:
        product_code = 0
    try:
        revision_no = int(revision_no_hex.replace("#x", "0x"), 16)
    except:
        revision_no = 0
    
    # 描述 - 支持多种格式
    desc = ""
    for n in device.findall("Name"):
        lc = n.get("LcId", "")
        if lc == "1033":
            desc = n.text or ""
            break
        elif not lc and not desc:
            desc = n.text or ""
    
    # Slot 分析
    slots = []
    for slot in device.iter("Slot"):
        s = slot.findtext("Name", "").strip()
        if s:
            slots.append(s)
    
    has_fslogic = "FSLOGIC" in slots
    has_fsoe = any("FSOE" in s.upper() for s in slots)
    
    # 查找所有 FSoE Module（从根元素搜索）
    fsoe_modules = []
    for m in root.iter("Module"):
        m_type_el = m.find("Type")
        if m_type_el is not None:
            type_text = (m_type_el.text or "").upper()
            if "FSOE" in type_text:
                fsoe_modules.append(m)
                has_fsoe = True
    
    # 检查 Device 直接下的 RxPdo/TxPdo 是否有 FSOE
    if not has_fsoe:
        for pdo_name in ["RxPdo", "TxPdo"]:
            for pdo in device.findall(pdo_name):
                name = pdo.findtext("Name", "")
                if "FSOE" in name.upper():
                    has_fsoe = True
                    break
    
    if fsoe_modules:
        # 为每个 FSoE Module 创建独立设备变体
        for m in fsoe_modules:
            m_type_el = m.find("Type")
            module_type_name = m_type_el.text if m_type_el is not None else ""
            module_ident = m_type_el.get("ModuleIdent", "") if m_type_el is not None else ""
            subtype = get_subtype_value(module_ident)
            
            info = {
                "name": f"{base_name}-{module_type_name}",  # 如 InoSV680S-FSoE-SRA
                "base_name": base_name,
                "module_type": module_type_name,
                "description": desc,
                "product_code_hex": product_code_hex,
                "revision_no_hex": revision_no_hex,
                "ProductCode": product_code,
                "RevisionNo": revision_no,
                "VendorId": vendor_id,
                "SubType": subtype,
                "ModuleIdent": module_ident,
                "slots": slots,
                "HasFSLOGIC": has_fslogic,
                "HasFSoE": has_fsoe,
            }
            
            # 使用 SM 属性解析 PDO 通道方向
            # SM="2" → 输出通道 (FB输出), SM="3" → 输入通道 (FB输入)
            input_elements, output_elements = parse_pdo_by_sm(m)
            
            # 如果 Module 没有 PDO，从 Device 级别获取 (如 Hollysys)
            if not input_elements and not output_elements:
                input_elements, output_elements = parse_pdo_by_sm(device)
            
            info["rx_elements"] = input_elements
            info["tx_elements"] = output_elements
            info["rx_count"] = len(input_elements)
            info["tx_count"] = len(output_elements)
            
            # 分类
            PLC_ONLY = {"EL6900", "EL6910", "EL6930", "EJ6910"}
            has_pdo = info["rx_count"] > 0 or info["tx_count"] > 0
            
            if base_name in PLC_ONLY:
                info["category"] = "安全PLC"
                info["IsSafetyPLC"] = True
                info["IsAliasDevice"] = False
            elif has_fslogic and has_fsoe:
                info["category"] = "双模式"
                info["IsSafetyPLC"] = True
                info["IsAliasDevice"] = True
            elif has_fslogic:
                info["category"] = "安全PLC"
                info["IsSafetyPLC"] = True
                info["IsAliasDevice"] = False
            elif has_pdo:
                info["category"] = "安全别名设备"
                info["IsSafetyPLC"] = False
                info["IsAliasDevice"] = True
            else:
                info["category"] = "未分类"
                info["IsSafetyPLC"] = False
                info["IsAliasDevice"] = False
            
            results.append(info)
    
    else:
        # 没有 FSoE Module，按传统方式解析单个设备
        info = {
            "name": base_name,
            "base_name": base_name,
            "description": desc,
            "product_code_hex": product_code_hex,
            "revision_no_hex": revision_no_hex,
            "ProductCode": product_code,
            "RevisionNo": revision_no,
            "VendorId": vendor_id,
            "slots": slots,
            "HasFSLOGIC": has_fslogic,
            "HasFSoE": has_fsoe,
        }
        
        # SubType
        module_ident = get_module_ident(device)
        info["SubType"] = get_subtype_value(module_ident)
        info["ModuleIdent"] = module_ident
        
        # PDO 解析 - 使用 SM 属性判断通道方向
        input_elements, output_elements = parse_pdo_by_sm(device)
        
        # 也从 Module 中提取 (Beckhoff/INOVANCE)
        if not input_elements and not output_elements:
            for m in device.iter("Module"):
                m_input, m_output = parse_pdo_by_sm(m)
                input_elements.extend(m_input)
                output_elements.extend(m_output)
        
        rx_elements = input_elements   # FB输入
        tx_elements = output_elements  # FB输出
        
        # 方式4: VendorSpecific SafeInput/SafeOutput (Hollysys)
        for vs in device.findall("VendorSpecific"):
            for si in vs.findall("SafeInput"):
                for entry in si.findall("Entry"):
                    name = entry.findtext("Name", "")
                    if name and not any(e["Name"] == name for e in rx_elements):
                        rx_elements.append({
                            "Name": name,
                            "Index": "",
                            "SubIndex": "",
                            "BitLen": entry.findtext("BitLen", ""),
                            "DataType": entry.findtext("DataType", ""),
                        })
            
            for so in vs.findall("SafeOutput"):
                for entry in so.findall("Entry"):
                    name = entry.findtext("Name", "")
                    if name and not any(e["Name"] == name for e in tx_elements):
                        tx_elements.append({
                            "Name": name,
                            "Index": "",
                            "SubIndex": "",
                            "BitLen": entry.findtext("BitLen", ""),
                            "DataType": entry.findtext("DataType", ""),
                        })
        
        info["rx_elements"] = rx_elements
        info["tx_elements"] = tx_elements
        info["rx_count"] = len(rx_elements)
        info["tx_count"] = len(tx_elements)
        
        # 分类
        PLC_ONLY = {"EL6900", "EL6910", "EL6930", "EJ6910"}
        has_pdo = info["rx_count"] > 0 or info["tx_count"] > 0
        
        if base_name in PLC_ONLY:
            info["category"] = "安全PLC"
            info["IsSafetyPLC"] = True
            info["IsAliasDevice"] = False
        elif has_fslogic and has_fsoe:
            info["category"] = "双模式"
            info["IsSafetyPLC"] = True
            info["IsAliasDevice"] = True
        elif has_fslogic:
            info["category"] = "安全PLC"
            info["IsSafetyPLC"] = True
            info["IsAliasDevice"] = False
        elif has_pdo:
            info["category"] = "安全别名设备"
            info["IsSafetyPLC"] = False
            info["IsAliasDevice"] = True
        else:
            info["category"] = "未分类"
            info["IsSafetyPLC"] = False
            info["IsAliasDevice"] = False
        
        results.append(info)
    
    return results


def parse_esi_file(filepath: str) -> List[Dict[str, Any]]:
    """解析单个 ESI 文件"""
    devices = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # 获取 VendorId
        vendor_id = get_vendor_id(root)
        
        for device in root.iter("Device"):
            device_list = parse_device(device, root, vendor_id)
            for info in device_list:
                info["source_file"] = os.path.basename(filepath)
                devices.append(info)
    except Exception as e:
        print(f"[解析错误] {filepath}: {e}")
    return devices


def parse_esi_directory(esi_dir: str) -> List[Dict[str, Any]]:
    """解析 ESI 目录下所有 XML 文件"""
    all_devices = []
    
    if not os.path.exists(esi_dir):
        return all_devices
    
    for fname in sorted(os.listdir(esi_dir)):
        if not fname.lower().endswith(".xml"):
            continue
        filepath = os.path.join(esi_dir, fname)
        devices = parse_esi_file(filepath)
        all_devices.extend(devices)
    
    # 去重（同型号同 RevisionNo 只保留一个）
    seen = set()
    unique = []
    for d in all_devices:
        key = (d["name"], d["revision_no_hex"])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    
    return unique


def get_alias_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """筛选出可作为安全别名设备的设备"""
    return [d for d in devices if d.get("IsAliasDevice", False)]


def get_safety_plc_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """筛选出可作为安全PLC的设备"""
    return [d for d in devices if d.get("IsSafetyPLC", False)]


def get_dual_mode_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """筛选出双模式设备"""
    return [d for d in devices if d.get("IsSafetyPLC") and d.get("IsAliasDevice")]
