"""
倍福(Beckhoff)安全IO设备库
仅包含 EL1904 和 EL2904，参数参照 template.xml 模板
"""
from typing import Dict, List, Optional, Any
from config_model import ProcessImage, ProcessImageElement, SafetyParameter


# 倍福安全IO设备定义（参数来自 template.xml）
BECKHOFF_SAFETY_DEVICES: Dict[str, Dict[str, Any]] = {
    # ============================================================
    # EL1904 - 4通道数字量安全输入端子
    # ============================================================
    "EL1904": {
        "name": "EL1904 - 4通道数字量安全输入",
        "description": "4通道数字量安全输入端子 (SIL3/PLe)",
        "VendorId": 2,
        "ProductCode": 125710418,
        "RevisionNo": 1114112,
        "Type": 60,
        "SubType": 190,  # PDF 7.2: EL1904 SubType=190
        "ConnectionType": "FSoEMaster",
        "LogicType": "None",
        "Watchdog": 100,
        "SafetyParameters": [
            {"OrderId": 1, "Name": "8000:01 FS Operating Mode:Operating Mode", "Value": "0"},
            {"OrderId": 2, "Name": "8001:01 FS Sensor Test:Sensor test Channel 1 active", "Value": "1"},
            {"OrderId": 3, "Name": "8001:02 FS Sensor Test:Sensor test Channel 2 active", "Value": "1"},
            {"OrderId": 4, "Name": "8001:03 FS Sensor Test:Sensor test Channel 3 active", "Value": "1"},
            {"OrderId": 5, "Name": "8001:04 FS Sensor Test:Sensor test Channel 4 active", "Value": "1"},
            {"OrderId": 6, "Name": "8002:01 FS Logic of Input pairs:Logic of Channel 1 and 2", "Value": "0"},
            {"OrderId": 7, "Name": "8002:03 FS Logic of Input pairs:Logic of Channel 3 and 4", "Value": "0"},
            {"OrderId": 8, "Name": "10E0:01 Store Code", "Value": "0"},
            {"OrderId": 9, "Name": "10E0:02 Project CRC", "Value": "0"},
        ],
        "RxPdo": {
            "BitSize": 48,
            "Elements": [
                {"Name": "InputChannel1", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "24577", "SubIndex": "1"},
                {"Name": "InputChannel2", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "24578", "SubIndex": "1"},
                {"Name": "InputChannel3", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "24579", "SubIndex": "1"},
                {"Name": "InputChannel4", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "24580", "SubIndex": "1"},
            ]
        },
        "TxPdo": None,
    },

    # ============================================================
    # EL1918 - 8通道数字量安全输入端子 (带诊断)
    # ============================================================
    "EL1918": {
        "name": "EL1918, 8 digital inputs (FW 2)",
        "description": "8通道数字量安全输入端子，带通道诊断 (SIL3/PLe)",
        "VendorId": 2,
        "ProductCode": 125710418,
        "RevisionNo": 1114112,
        "Type": 60,
        "SubType": 17827710,
        "ConnectionType": "Local",
        "LogicType": "None",
        "Watchdog": 100,
        "SafetyParameters": [
            {"OrderId": 1, "Name": "1018:01 Identity:Vendor ID", "Value": "2"},
            {"OrderId": 2, "Name": "F050:01 Detected modules:SubIndex 001", "Value": "17827710"},
            {"OrderId": 3, "Name": "8000:01 FSIN Module   1 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 4, "Name": "8000:02 FSIN Module   1 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 5, "Name": "8000:04 FSIN Module   1 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 6, "Name": "8000:05 FSIN Module   1 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 7, "Name": "8001:01 FSIN Module   1 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 8, "Name": "8001:02 FSIN Module   1 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 9, "Name": "8010:01 FSIN Module   2 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 10, "Name": "8010:02 FSIN Module   2 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 11, "Name": "8010:04 FSIN Module   2 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 12, "Name": "8010:05 FSIN Module   2 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 13, "Name": "8011:01 FSIN Module   2 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 14, "Name": "8011:02 FSIN Module   2 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 15, "Name": "8020:01 FSIN Module   3 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 16, "Name": "8020:02 FSIN Module   3 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 17, "Name": "8020:04 FSIN Module   3 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 18, "Name": "8020:05 FSIN Module   3 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 19, "Name": "8021:01 FSIN Module   3 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 20, "Name": "8021:02 FSIN Module   3 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 21, "Name": "8030:01 FSIN Module   4 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 22, "Name": "8030:02 FSIN Module   4 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 23, "Name": "8030:04 FSIN Module   4 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 24, "Name": "8030:05 FSIN Module   4 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 25, "Name": "8031:01 FSIN Module   4 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 26, "Name": "8031:02 FSIN Module   4 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 27, "Name": "8040:01 FSIN Module   5 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 28, "Name": "8040:02 FSIN Module   5 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 29, "Name": "8040:04 FSIN Module   5 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 30, "Name": "8040:05 FSIN Module   5 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 31, "Name": "8041:01 FSIN Module   5 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 32, "Name": "8041:02 FSIN Module   5 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 33, "Name": "8050:01 FSIN Module   6 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 34, "Name": "8050:02 FSIN Module   6 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 35, "Name": "8050:04 FSIN Module   6 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 36, "Name": "8050:05 FSIN Module   6 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 37, "Name": "8051:01 FSIN Module   6 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 38, "Name": "8051:02 FSIN Module   6 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 39, "Name": "8060:01 FSIN Module   7 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 40, "Name": "8060:02 FSIN Module   7 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 41, "Name": "8060:04 FSIN Module   7 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 42, "Name": "8060:05 FSIN Module   7 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 43, "Name": "8061:01 FSIN Module   7 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 44, "Name": "8061:02 FSIN Module   7 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 45, "Name": "8070:01 FSIN Module   8 Settings Common:ModuloDiagTestPulse", "Value": "0"},
            {"OrderId": 46, "Name": "8070:02 FSIN Module   8 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
            {"OrderId": 47, "Name": "8070:04 FSIN Module   8 Settings Common:Diag TestPulse active", "Value": "1"},
            {"OrderId": 48, "Name": "8070:05 FSIN Module   8 Settings Common:Module Fault Link active", "Value": "1"},
            {"OrderId": 49, "Name": "8071:01 FSIN Module   8 Settings Channel:InputFilterTime", "Value": "10"},
            {"OrderId": 50, "Name": "8071:02 FSIN Module   8 Settings Channel:DiagTestPulseFilterTime", "Value": "2"},
            {"OrderId": 51, "Name": "10E0:01 FS Restore Mode:Store Code", "Value": "0"},
            {"OrderId": 52, "Name": "10E0:02 FS Restore Mode:Project CRC", "Value": "0"},
        ],
        "RxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSIN Module 1.Input", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "24577", "SubIndex": "1"},
                {"Name": "FSIN Module 1.Module Fault", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "24578", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Input", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "24593", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Module Fault", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "24594", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Input", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "24609", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Module Fault", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "24610", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Input", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "24625", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Module Fault", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "24626", "SubIndex": "1"},
                {"Name": "FSIN Module 5.Input", "Type": "BIT", "BitOffset": 16, "BitSize": 1, "IsSafeTimer": False, "Index": "24641", "SubIndex": "1"},
                {"Name": "FSIN Module 5.Module Fault", "Type": "BIT", "BitOffset": 17, "BitSize": 1, "IsSafeTimer": False, "Index": "24642", "SubIndex": "1"},
                {"Name": "FSIN Module 6.Input", "Type": "BIT", "BitOffset": 18, "BitSize": 1, "IsSafeTimer": False, "Index": "24657", "SubIndex": "1"},
                {"Name": "FSIN Module 6.Module Fault", "Type": "BIT", "BitOffset": 19, "BitSize": 1, "IsSafeTimer": False, "Index": "24658", "SubIndex": "1"},
                {"Name": "FSIN Module 7.Input", "Type": "BIT", "BitOffset": 20, "BitSize": 1, "IsSafeTimer": False, "Index": "24673", "SubIndex": "1"},
                {"Name": "FSIN Module 7.Module Fault", "Type": "BIT", "BitOffset": 21, "BitSize": 1, "IsSafeTimer": False, "Index": "24674", "SubIndex": "1"},
                {"Name": "FSIN Module 8.Input", "Type": "BIT", "BitOffset": 22, "BitSize": 1, "IsSafeTimer": False, "Index": "24689", "SubIndex": "1"},
                {"Name": "FSIN Module 8.Module Fault", "Type": "BIT", "BitOffset": 23, "BitSize": 1, "IsSafeTimer": False, "Index": "24690", "SubIndex": "1"},
            ]
        },
        "TxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSIN Module 1.ErrAck", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "28674", "SubIndex": "1"},
                {"Name": "FSIN Module 2.ErrAck", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "28690", "SubIndex": "1"},
                {"Name": "FSIN Module 3.ErrAck", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "28706", "SubIndex": "1"},
                {"Name": "FSIN Module 4.ErrAck", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "28722", "SubIndex": "1"},
                {"Name": "FSIN Module 5.ErrAck", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "28738", "SubIndex": "1"},
                {"Name": "FSIN Module 6.ErrAck", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "28754", "SubIndex": "1"},
                {"Name": "FSIN Module 7.ErrAck", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "28770", "SubIndex": "1"},
                {"Name": "FSIN Module 8.ErrAck", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "28786", "SubIndex": "1"},
            ]
        },
    },

    # ============================================================
    # EL2904 - 4通道数字量安全输出端子
    # ============================================================
    "EL2904": {
        "name": "EL2904 - 4通道数字量安全输出",
        "description": "4通道数字量安全输出端子 (SIL3/PLe)",
        "VendorId": 2,
        "ProductCode": 190328914,
        "RevisionNo": 1179648,
        "Type": 60,
        "SubType": 290,
        "ConnectionType": "FSoEMaster",
        "LogicType": "None",
        "Watchdog": 100,
        "SafetyParameters": [
            {"OrderId": 1, "Name": "8000:01 FSOE Settings:Standard outputs active", "Value": "0"},
            {"OrderId": 2, "Name": "8000:02 FSOE Settings:Current measurement active", "Value": "1"},
            {"OrderId": 3, "Name": "8000:03 FSOE Settings:Testing of outputs active", "Value": "1"},
            {"OrderId": 4, "Name": "8000:04 FSOE Settings:Error acknowledge active", "Value": "0"},
            {"OrderId": 5, "Name": "10E0:01 Store Code", "Value": "0"},
            {"OrderId": 6, "Name": "10E0:02 Project CRC", "Value": "0"},
        ],
        "TxPdo": {
            "BitSize": 48,
            "Elements": [
                {"Name": "OutputChannel1", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "1"},
                {"Name": "OutputChannel2", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "2"},
                {"Name": "OutputChannel3", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "3"},
                {"Name": "OutputChannel4", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "4"},
            ]
        },
    },
    # EP1918 - EP1918, 8 Ch. Safety Input
    "EP1918": {
        "name": "EP1918, 8 Ch. Safety Input",
        "description": "8通道数字量安全输入端子，带通道诊断 (SIL3/PLe)",
        "VendorId": 2,
        "Type": 60,
        "SubType": 526206,
        "ConnectionType": "FSoEMaster",
        "LogicType": "None",
        "SafetyParameters": [
                {"OrderId": 1, "Name": "1018:01 Identity:Vendor ID", "Value": "2"},
                {"OrderId": 2, "Name": "F050:01 Detected modules:SubIndex 001", "Value": "526206"},
                {"OrderId": 3, "Name": "8000:01 FSIN Module   1 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 4, "Name": "8000:02 FSIN Module   1 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 5, "Name": "8000:04 FSIN Module   1 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 6, "Name": "8000:05 FSIN Module   1 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 7, "Name": "8000:0C FSIN Module   1 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 8, "Name": "8001:01 FSIN Module   1 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 9, "Name": "8001:02 FSIN Module   1 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 10, "Name": "8001:04 FSIN Module   1 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 11, "Name": "8001:05 FSIN Module   1 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 12, "Name": "8010:01 FSIN Module   2 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 13, "Name": "8010:02 FSIN Module   2 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 14, "Name": "8010:04 FSIN Module   2 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 15, "Name": "8010:05 FSIN Module   2 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 16, "Name": "8010:0C FSIN Module   2 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 17, "Name": "8011:01 FSIN Module   2 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 18, "Name": "8011:02 FSIN Module   2 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 19, "Name": "8011:04 FSIN Module   2 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 20, "Name": "8011:05 FSIN Module   2 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 21, "Name": "8020:01 FSIN Module   3 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 22, "Name": "8020:02 FSIN Module   3 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 23, "Name": "8020:04 FSIN Module   3 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 24, "Name": "8020:05 FSIN Module   3 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 25, "Name": "8020:0C FSIN Module   3 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 26, "Name": "8021:01 FSIN Module   3 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 27, "Name": "8021:02 FSIN Module   3 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 28, "Name": "8021:04 FSIN Module   3 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 29, "Name": "8021:05 FSIN Module   3 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 30, "Name": "8030:01 FSIN Module   4 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 31, "Name": "8030:02 FSIN Module   4 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 32, "Name": "8030:04 FSIN Module   4 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 33, "Name": "8030:05 FSIN Module   4 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 34, "Name": "8030:0C FSIN Module   4 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 35, "Name": "8031:01 FSIN Module   4 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 36, "Name": "8031:02 FSIN Module   4 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 37, "Name": "8031:04 FSIN Module   4 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 38, "Name": "8031:05 FSIN Module   4 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 39, "Name": "10E0:01 Store Code", "Value": "0"},
                {"OrderId": 40, "Name": "10E0:02 Project CRC", "Value": "0"},
        ],
        "RxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSIN Module 1.Channel 1.Input", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "24577", "SubIndex": "1"},
                {"Name": "FSIN Module 1.Channel 2.Input", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "24577", "SubIndex": "2"},
                {"Name": "FSIN Module 1.Module Fault", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "24578", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Channel 1.Input", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "24593", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Channel 2.Input", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "24593", "SubIndex": "2"},
                {"Name": "FSIN Module 2.Module Fault", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "24594", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Channel 1.Input", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "24609", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Channel 2.Input", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "24609", "SubIndex": "2"},
                {"Name": "FSIN Module 3.Module Fault", "Type": "BIT", "BitOffset": 16, "BitSize": 1, "IsSafeTimer": False, "Index": "24610", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Channel 1.Input", "Type": "BIT", "BitOffset": 17, "BitSize": 1, "IsSafeTimer": False, "Index": "24625", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Channel 2.Input", "Type": "BIT", "BitOffset": 18, "BitSize": 1, "IsSafeTimer": False, "Index": "24625", "SubIndex": "2"},
                {"Name": "FSIN Module 4.Module Fault", "Type": "BIT", "BitOffset": 19, "BitSize": 1, "IsSafeTimer": False, "Index": "24626", "SubIndex": "1"},
            ]
        },
        "TxPdo": {
            "BitSize": 48,
            "Elements": [
                {"Name": "FSIN Module 1.ErrAck", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "28674", "SubIndex": "1"},
                {"Name": "FSIN Module 2.ErrAck", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "28690", "SubIndex": "1"},
                {"Name": "FSIN Module 3.ErrAck", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "28706", "SubIndex": "1"},
                {"Name": "FSIN Module 4.ErrAck", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "28722", "SubIndex": "1"},
            ]
        },
    },
    # EP1957 - EP1957, 8 Ch. Safety Input, 4 Ch. Safety Output
    "EP1957": {
        "name": "EP1957, 8 Ch. Safety Input, 4 Ch. Safety Output",
        "description": "8通道数字量安全输入 + 4通道数字量安全输出端子 (SIL3/PLe)",
        "VendorId": 2,
        "Type": 60,
        "SubType": 526245,
        "ConnectionType": "FSoEMaster",
        "LogicType": "None",
        "SafetyParameters": [
                {"OrderId": 1, "Name": "1018:01 Identity:Vendor ID", "Value": "2"},
                {"OrderId": 2, "Name": "F050:01 Detected modules:SubIndex 001", "Value": "526245"},
                {"OrderId": 3, "Name": "8000:01 FSOUT Module   1 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 4, "Name": "8000:02 FSOUT Module   1 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 5, "Name": "8000:03 FSOUT Module   1 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 6, "Name": "8000:04 FSOUT Module   1 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 7, "Name": "8000:07 FSOUT Module   1 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 8, "Name": "8010:01 FSOUT Module   2 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 9, "Name": "8010:02 FSOUT Module   2 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 10, "Name": "8010:03 FSOUT Module   2 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 11, "Name": "8010:04 FSOUT Module   2 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 12, "Name": "8010:07 FSOUT Module   2 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 13, "Name": "8020:01 FSOUT Module   3 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 14, "Name": "8020:02 FSOUT Module   3 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 15, "Name": "8020:03 FSOUT Module   3 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 16, "Name": "8020:04 FSOUT Module   3 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 17, "Name": "8020:07 FSOUT Module   3 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 18, "Name": "8030:01 FSOUT Module   4 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 19, "Name": "8030:02 FSOUT Module   4 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 20, "Name": "8030:03 FSOUT Module   4 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 21, "Name": "8030:04 FSOUT Module   4 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 22, "Name": "8030:07 FSOUT Module   4 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 23, "Name": "8040:01 FSIN Module   1 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 24, "Name": "8040:02 FSIN Module   1 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 25, "Name": "8040:04 FSIN Module   1 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 26, "Name": "8040:05 FSIN Module   1 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 27, "Name": "8040:0C FSIN Module   1 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 28, "Name": "8041:01 FSIN Module   1 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 29, "Name": "8041:02 FSIN Module   1 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 30, "Name": "8041:04 FSIN Module   1 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 31, "Name": "8041:05 FSIN Module   1 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 32, "Name": "8050:01 FSIN Module   2 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 33, "Name": "8050:02 FSIN Module   2 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 34, "Name": "8050:04 FSIN Module   2 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 35, "Name": "8050:05 FSIN Module   2 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 36, "Name": "8050:0C FSIN Module   2 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 37, "Name": "8051:01 FSIN Module   2 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 38, "Name": "8051:02 FSIN Module   2 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 39, "Name": "8051:04 FSIN Module   2 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 40, "Name": "8051:05 FSIN Module   2 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 41, "Name": "8060:01 FSIN Module   3 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 42, "Name": "8060:02 FSIN Module   3 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 43, "Name": "8060:04 FSIN Module   3 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 44, "Name": "8060:05 FSIN Module   3 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 45, "Name": "8060:0C FSIN Module   3 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 46, "Name": "8061:01 FSIN Module   3 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 47, "Name": "8061:02 FSIN Module   3 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 48, "Name": "8061:04 FSIN Module   3 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 49, "Name": "8061:05 FSIN Module   3 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 50, "Name": "8070:01 FSIN Module   4 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 51, "Name": "8070:02 FSIN Module   4 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 52, "Name": "8070:04 FSIN Module   4 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 53, "Name": "8070:05 FSIN Module   4 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 54, "Name": "8070:0C FSIN Module   4 Settings Common:Input Power Mode", "Value": "1"},
                {"OrderId": 55, "Name": "8071:01 FSIN Module   4 Settings Channel:Channel 1.InputFilterTime", "Value": "10"},
                {"OrderId": 56, "Name": "8071:02 FSIN Module   4 Settings Channel:Channel 1.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 57, "Name": "8071:04 FSIN Module   4 Settings Channel:Channel 2.InputFilterTime", "Value": "10"},
                {"OrderId": 58, "Name": "8071:05 FSIN Module   4 Settings Channel:Channel 2.DiagTestPulseFilterTime", "Value": "2"},
                {"OrderId": 59, "Name": "10E0:01 FS Restore Mode:Store Code", "Value": "0"},
                {"OrderId": 60, "Name": "10E0:02 FS Restore Mode:Project CRC", "Value": "0"},
        ],
        "RxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSOUT Module 1.Module Fault", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "24578", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.Module Fault", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "24594", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.Module Fault", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "24610", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.Module Fault", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "24626", "SubIndex": "1"},
                {"Name": "FSIN Module 1.Channel 1.Input", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "24641", "SubIndex": "1"},
                {"Name": "FSIN Module 1.Channel 2.Input", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "24641", "SubIndex": "2"},
                {"Name": "FSIN Module 1.Module Fault", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "24642", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Channel 1.Input", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "24657", "SubIndex": "1"},
                {"Name": "FSIN Module 2.Channel 2.Input", "Type": "BIT", "BitOffset": 16, "BitSize": 1, "IsSafeTimer": False, "Index": "24657", "SubIndex": "2"},
                {"Name": "FSIN Module 2.Module Fault", "Type": "BIT", "BitOffset": 17, "BitSize": 1, "IsSafeTimer": False, "Index": "24658", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Channel 1.Input", "Type": "BIT", "BitOffset": 18, "BitSize": 1, "IsSafeTimer": False, "Index": "24673", "SubIndex": "1"},
                {"Name": "FSIN Module 3.Channel 2.Input", "Type": "BIT", "BitOffset": 19, "BitSize": 1, "IsSafeTimer": False, "Index": "24673", "SubIndex": "2"},
                {"Name": "FSIN Module 3.Module Fault", "Type": "BIT", "BitOffset": 20, "BitSize": 1, "IsSafeTimer": False, "Index": "24674", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Channel 1.Input", "Type": "BIT", "BitOffset": 21, "BitSize": 1, "IsSafeTimer": False, "Index": "24689", "SubIndex": "1"},
                {"Name": "FSIN Module 4.Channel 2.Input", "Type": "BIT", "BitOffset": 22, "BitSize": 1, "IsSafeTimer": False, "Index": "24689", "SubIndex": "2"},
                {"Name": "FSIN Module 4.Module Fault", "Type": "BIT", "BitOffset": 23, "BitSize": 1, "IsSafeTimer": False, "Index": "24690", "SubIndex": "1"},
            ]
        },
        "TxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSOUT Module 1.Output", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "1"},
                {"Name": "FSOUT Module 1.ErrAck", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "28674", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.Output", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "28689", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.ErrAck", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "28690", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.Output", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "28705", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.ErrAck", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "28706", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.Output", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "28721", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.ErrAck", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "28722", "SubIndex": "1"},
                {"Name": "FSIN Module 1.ErrAck", "Type": "BIT", "BitOffset": 16, "BitSize": 1, "IsSafeTimer": False, "Index": "28738", "SubIndex": "1"},
                {"Name": "FSIN Module 2.ErrAck", "Type": "BIT", "BitOffset": 17, "BitSize": 1, "IsSafeTimer": False, "Index": "28754", "SubIndex": "1"},
                {"Name": "FSIN Module 3.ErrAck", "Type": "BIT", "BitOffset": 18, "BitSize": 1, "IsSafeTimer": False, "Index": "28770", "SubIndex": "1"},
                {"Name": "FSIN Module 4.ErrAck", "Type": "BIT", "BitOffset": 19, "BitSize": 1, "IsSafeTimer": False, "Index": "28786", "SubIndex": "1"},
            ]
        },
    },
    # EP2918 - EP2918, 8 Ch. Safety Output
    "EP2918": {
        "name": "EP2918, 8 Ch. Safety Output",
        "description": "8通道数字量安全输出端子，带通道诊断 (SIL3/PLe)",
        "VendorId": 2,
        "Type": 60,
        "SubType": 527206,
        "ConnectionType": "FSoEMaster",
        "LogicType": "None",
        "SafetyParameters": [
                {"OrderId": 1, "Name": "1018:01 Identity:Vendor ID", "Value": "2"},
                {"OrderId": 2, "Name": "F050:01 Detected modules:SubIndex 001", "Value": "527206"},
                {"OrderId": 3, "Name": "8000:01 FSOUT Module   1 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 4, "Name": "8000:02 FSOUT Module   1 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 5, "Name": "8000:03 FSOUT Module   1 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 6, "Name": "8000:04 FSOUT Module   1 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 7, "Name": "8000:07 FSOUT Module   1 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 8, "Name": "8010:01 FSOUT Module   2 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 9, "Name": "8010:02 FSOUT Module   2 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 10, "Name": "8010:03 FSOUT Module   2 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 11, "Name": "8010:04 FSOUT Module   2 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 12, "Name": "8010:07 FSOUT Module   2 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 13, "Name": "8020:01 FSOUT Module   3 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 14, "Name": "8020:02 FSOUT Module   3 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 15, "Name": "8020:03 FSOUT Module   3 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 16, "Name": "8020:04 FSOUT Module   3 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 17, "Name": "8020:07 FSOUT Module   3 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 18, "Name": "8030:01 FSOUT Module   4 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 19, "Name": "8030:02 FSOUT Module   4 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 20, "Name": "8030:03 FSOUT Module   4 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 21, "Name": "8030:04 FSOUT Module   4 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 22, "Name": "8030:07 FSOUT Module   4 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 23, "Name": "8040:01 FSOUT Module   5 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 24, "Name": "8040:02 FSOUT Module   5 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 25, "Name": "8040:03 FSOUT Module   5 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 26, "Name": "8040:04 FSOUT Module   5 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 27, "Name": "8040:07 FSOUT Module   5 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 28, "Name": "8050:01 FSOUT Module   6 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 29, "Name": "8050:02 FSOUT Module   6 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 30, "Name": "8050:03 FSOUT Module   6 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 31, "Name": "8050:04 FSOUT Module   6 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 32, "Name": "8050:07 FSOUT Module   6 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 33, "Name": "8060:01 FSOUT Module   7 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 34, "Name": "8060:02 FSOUT Module   7 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 35, "Name": "8060:03 FSOUT Module   7 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 36, "Name": "8060:04 FSOUT Module   7 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 37, "Name": "8060:07 FSOUT Module   7 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 38, "Name": "8070:01 FSOUT Module   8 Settings Common:ModuloDiagTestPulse", "Value": "0"},
                {"OrderId": 39, "Name": "8070:02 FSOUT Module   8 Settings Common:MultiplierDiagTestPulse", "Value": "1"},
                {"OrderId": 40, "Name": "8070:03 FSOUT Module   8 Settings Common:Standard Outputs active", "Value": "0"},
                {"OrderId": 41, "Name": "8070:04 FSOUT Module   8 Settings Common:Diag TestPulse active", "Value": "1"},
                {"OrderId": 42, "Name": "8070:07 FSOUT Module   8 Settings Common:Module Fault Link active", "Value": "1"},
                {"OrderId": 43, "Name": "10E0:01 Store Code", "Value": "0"},
                {"OrderId": 44, "Name": "10E0:02 Project CRC", "Value": "0"},
        ],
        "RxPdo": {
            "BitSize": 48,
            "Elements": [
                {"Name": "FSOUT Module 1.Module Fault", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "24578", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.Module Fault", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "24594", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.Module Fault", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "24610", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.Module Fault", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "24626", "SubIndex": "1"},
                {"Name": "FSOUT Module 5.Module Fault", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "24642", "SubIndex": "1"},
                {"Name": "FSOUT Module 6.Module Fault", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "24658", "SubIndex": "1"},
                {"Name": "FSOUT Module 7.Module Fault", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "24674", "SubIndex": "1"},
                {"Name": "FSOUT Module 8.Module Fault", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "24690", "SubIndex": "1"},
            ]
        },
        "TxPdo": {
            "BitSize": 56,
            "Elements": [
                {"Name": "FSOUT Module 1.Output", "Type": "BIT", "BitOffset": 8, "BitSize": 1, "IsSafeTimer": False, "Index": "28673", "SubIndex": "1"},
                {"Name": "FSOUT Module 1.ErrAck", "Type": "BIT", "BitOffset": 9, "BitSize": 1, "IsSafeTimer": False, "Index": "28674", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.Output", "Type": "BIT", "BitOffset": 10, "BitSize": 1, "IsSafeTimer": False, "Index": "28689", "SubIndex": "1"},
                {"Name": "FSOUT Module 2.ErrAck", "Type": "BIT", "BitOffset": 11, "BitSize": 1, "IsSafeTimer": False, "Index": "28690", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.Output", "Type": "BIT", "BitOffset": 12, "BitSize": 1, "IsSafeTimer": False, "Index": "28705", "SubIndex": "1"},
                {"Name": "FSOUT Module 3.ErrAck", "Type": "BIT", "BitOffset": 13, "BitSize": 1, "IsSafeTimer": False, "Index": "28706", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.Output", "Type": "BIT", "BitOffset": 14, "BitSize": 1, "IsSafeTimer": False, "Index": "28721", "SubIndex": "1"},
                {"Name": "FSOUT Module 4.ErrAck", "Type": "BIT", "BitOffset": 15, "BitSize": 1, "IsSafeTimer": False, "Index": "28722", "SubIndex": "1"},
                {"Name": "FSOUT Module 5.Output", "Type": "BIT", "BitOffset": 16, "BitSize": 1, "IsSafeTimer": False, "Index": "28737", "SubIndex": "1"},
                {"Name": "FSOUT Module 5.ErrAck", "Type": "BIT", "BitOffset": 17, "BitSize": 1, "IsSafeTimer": False, "Index": "28738", "SubIndex": "1"},
                {"Name": "FSOUT Module 6.Output", "Type": "BIT", "BitOffset": 18, "BitSize": 1, "IsSafeTimer": False, "Index": "28753", "SubIndex": "1"},
                {"Name": "FSOUT Module 6.ErrAck", "Type": "BIT", "BitOffset": 19, "BitSize": 1, "IsSafeTimer": False, "Index": "28754", "SubIndex": "1"},
                {"Name": "FSOUT Module 7.Output", "Type": "BIT", "BitOffset": 20, "BitSize": 1, "IsSafeTimer": False, "Index": "28769", "SubIndex": "1"},
                {"Name": "FSOUT Module 7.ErrAck", "Type": "BIT", "BitOffset": 21, "BitSize": 1, "IsSafeTimer": False, "Index": "28770", "SubIndex": "1"},
                {"Name": "FSOUT Module 8.Output", "Type": "BIT", "BitOffset": 22, "BitSize": 1, "IsSafeTimer": False, "Index": "28785", "SubIndex": "1"},
                {"Name": "FSOUT Module 8.ErrAck", "Type": "BIT", "BitOffset": 23, "BitSize": 1, "IsSafeTimer": False, "Index": "28786", "SubIndex": "1"},
            ]
        },
    },
}


def get_device_names() -> List[str]:
    return list(BECKHOFF_SAFETY_DEVICES.keys())


def get_device_info(device_key: str) -> Optional[Dict[str, Any]]:
    return BECKHOFF_SAFETY_DEVICES.get(device_key)


def get_device_display_list() -> List[str]:
    """返回设备型号列表（仅显示型号）"""
    return list(BECKHOFF_SAFETY_DEVICES.keys())


def parse_device_key(display_name: str) -> str:
    return display_name.split(" - ")[0]


def build_process_image(pi_data: Optional[Dict[str, Any]], device_id: str, direction: str) -> Optional[ProcessImage]:
    """构建过程映像，遵循 PDF 7.2 ID 命名规则
    
    Args:
        pi_data: 过程映像数据
        device_id: 设备 ID (如 g1_a3)
        direction: 方向 "i" (输入/RxPdo) 或 "o" (输出/TxPdo)
    """
    if not pi_data:
        return None
    elements = []
    for i, e in enumerate(pi_data.get("Elements", [])):
        elements.append(ProcessImageElement(
            Id=f"{device_id}_{direction}{i+1}",  # 如 g1_a4_i1, g1_a3_o1
            Name=e.get("Name", ""),
            Type=e.get("Type", "BIT"),
            BitOffset=e.get("BitOffset", 0),
            BitSize=e.get("BitSize", 1),
            IsSafeTimer=e.get("IsSafeTimer", False),
            Index=e.get("Index"),
            SubIndex=e.get("SubIndex"),
        ))
    return ProcessImage(BitSize=pi_data.get("BitSize", 0), Elements=elements)


def create_alias_device_from_library(device_key: str, alias_name: str,
                                     safe_address: int = 1,
                                     connection_id: int = 3,
                                     watchdog: int = 100,
                                     device_id: str = ""):
    """从设备库创建安全别名设备"""
    from config_model import SafetyAliasDevice

    info = get_device_info(device_key)
    if not info:
        raise ValueError(f"未知设备: {device_key}")

    dev_id = device_id or f"g1_a_{device_key}"
    params = [SafetyParameter(**p) for p in info.get("SafetyParameters", [])]

    return SafetyAliasDevice(
        Id=dev_id,
        IsExternal=False,
        VendorId=info.get("VendorId", 2),
        ProductCode=info.get("ProductCode"),
        RevisionNo=info.get("RevisionNo"),
        Type=info.get("Type", 60),
        SubType=info.get("SubType", 290),
        ConnectionType=info.get("ConnectionType", "FSoEMaster"),
        LogicType=info.get("LogicType", "None"),
        AliasName=alias_name or device_key,
        IoPath="",
        ConnectionId=connection_id,
        SafeAddress=safe_address,
        DynamicPortionSafeAddressId=f"{dev_id}_d",  # PDF 7.2: {device_id}_d
        Watchdog=watchdog,
        SafetyParameters=params,
        RxPdo=build_process_image(info.get("RxPdo"), dev_id, "i"),  # PDF 7.2: {device_id}_i{N}
        TxPdo=build_process_image(info.get("TxPdo"), dev_id, "o"),  # PDF 7.2: {device_id}_o{N}
        ComErrAckId=f"{dev_id}_c",  # PDF 7.2: {device_id}_c
        ModuleFaultAsComErr=False,
        MapState=False,
        MapDiag=False,
        MapInputs=False,
        MapOutputs=False,
        IncrementalDownloadEnabled=False,
    )
