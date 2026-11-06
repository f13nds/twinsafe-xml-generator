"""
TwinSAFE 项目配置数据模型
参照 template.xml 导出的安全程序 XML 格式模板
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json


@dataclass
class GeneralInformation:
    """项目基本信息"""
    ProjectName: str = "TwinSAFE Project"
    Author: str = ""
    InternalProjectName: str = ""


@dataclass
class BackupRestore:
    """备份恢复设置"""
    Activated: bool = False
    RestoreUserAdministration: bool = False
    NumberOfDevicesWithMatchingCRC: int = 0


@dataclass
class TargetSystemConfiguration:
    """目标系统（安全 PLC）配置"""
    Id: str = "t1"
    Type: str = "Hardware"
    SubType: str = "EL6910"
    IsExternal: bool = False
    SafeAddress: int = 1
    IoPath: str = ""
    ProductCode: Optional[int] = None
    RevisionNo: Optional[int] = None
    VersionNumber: int = 1
    BackupRestore: BackupRestore = field(default_factory=BackupRestore)
    MapProjectCRC: bool = False
    MapSerialNumber: bool = False
    ConnectionInfoDataConfigOld: bool = False
    TakeOverSafetyAliasDeviceNamesInProcessImage: bool = False
    TakeOverStandardAliasDeviceNamesInProcessImage: bool = False


@dataclass
class ProcessImageElement:
    """安全IO过程映像元素 (RxPdo/TxPdo 中的 Element)"""
    Id: str
    Name: str = ""
    Type: str = "BIT"
    BitOffset: int = 0
    BitSize: int = 1
    IsSafeTimer: bool = False
    Index: Optional[str] = None
    SubIndex: Optional[str] = None
    Alias: str = ""


@dataclass
class ProcessImage:
    """安全IO过程映像 (RxPdo/TxPdo)"""
    BitSize: int = 0
    Elements: List[ProcessImageElement] = field(default_factory=list)


@dataclass
class SafetyParameter:
    """安全参数"""
    OrderId: int
    Name: str
    Value: str = ""


@dataclass
class Port:
    """FB 端口或 Group 端口实例"""
    Id: str
    PortId: str
    Alias: str = ""
    Active: bool = True
    PortName: str = ""
    Negated: bool = False
    Type: Optional[str] = None
    Comment: str = ""


@dataclass
class SafetyAliasDevice:
    """安全别名设备（SIL>0）"""
    Id: str
    IsExternal: bool = False
    VendorId: int = 2
    ProductCode: Optional[int] = None
    RevisionNo: Optional[int] = None
    Type: int = 60
    SubType: int = 290
    ConnectionType: str = "FSoEMaster"
    LogicType: str = "None"
    AliasName: str = ""
    IoPath: str = ""
    ConnectionId: int = 1
    SafeAddress: int = 1
    DynamicPortionSafeAddressId: Optional[str] = None
    Watchdog: int = 100
    SafetyParameters: List[SafetyParameter] = field(default_factory=list)
    RxPdo: Optional[ProcessImage] = None
    TxPdo: Optional[ProcessImage] = None
    ComErrAckId: Optional[str] = None
    ModuleFaultAsComErr: bool = False
    MapState: bool = False
    MapDiag: bool = False
    MapInputs: bool = False
    MapOutputs: bool = False
    IncrementalDownloadEnabled: bool = False


@dataclass
class StandardAliasDevice:
    """标准别名设备"""
    Id: str
    OrderId: Optional[int] = None
    AliasName: str = ""
    RxPdo: Optional[ProcessImage] = None
    TxPdo: Optional[ProcessImage] = None


@dataclass
class FunctionBlock:
    """功能块实例"""
    Id: str
    OrderId: int
    Name: str
    Type: int
    MapState: bool = False
    MapDiag: bool = False
    Comment: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)
    Inports: List[Port] = field(default_factory=list)
    Outports: List[Port] = field(default_factory=list)


@dataclass
class TwinSAFEGroup:
    """TwinSAFE 组"""
    Id: str
    OrderId: int
    Name: str = ""
    MapDiag: bool = False
    MapState: bool = False
    PassificationAllowed: bool = False
    TemporaryDeactivationAllowed: bool = False
    PermanentDeactivationAllowed: bool = False
    TimeOutPassificationAllowed: int = 10000
    VerifyAnalogFBInputsByStartup: bool = False
    AnalogFBOutputCustomReplacementValues: bool = False
    GroupOutputs: List[Port] = field(default_factory=list)
    GroupInputs: List[Port] = field(default_factory=list)
    AliasDevices: List[Any] = field(default_factory=list)
    FunctionBlocks: List[FunctionBlock] = field(default_factory=list)
    Comment: str = ""


@dataclass
class Mapping:
    """变量/端口映射"""
    SourceId: str = ""
    TargetId: str = ""
    LocalVarName: str = ""
    GlobalVarName: str = ""
    Local: bool = False


@dataclass
class ApplicationConfiguration:
    """应用层配置"""
    TwinSAFEGroups: List[TwinSAFEGroup] = field(default_factory=list)
    Mappings: List[Mapping] = field(default_factory=list)


@dataclass
class TwinSAFEProject:
    """完整项目"""
    Version: str = "0.32"
    GeneralInformation: GeneralInformation = field(default_factory=GeneralInformation)
    TargetSystemConfiguration: TargetSystemConfiguration = field(default_factory=TargetSystemConfiguration)
    ApplicationConfiguration: ApplicationConfiguration = field(default_factory=ApplicationConfiguration)

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "TwinSAFEProject":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "TwinSAFEProject":
        return cls(
            Version=data.get("Version", "0.32"),
            GeneralInformation=GeneralInformation(**data.get("GeneralInformation", {})),
            TargetSystemConfiguration=cls._parse_target(data.get("TargetSystemConfiguration", {})),
            ApplicationConfiguration=cls._parse_app(data.get("ApplicationConfiguration", {})),
        )

    @classmethod
    def _parse_target(cls, data: dict) -> TargetSystemConfiguration:
        br = data.get("BackupRestore", {})
        return TargetSystemConfiguration(
            Id=data.get("Id", "t1"),
            Type=data.get("Type", "Hardware"),
            SubType=data.get("SubType", "EL6910"),
            IsExternal=data.get("IsExternal", False),
            SafeAddress=data.get("SafeAddress", 1),
            IoPath=data.get("IoPath", ""),
            ProductCode=data.get("ProductCode"),
            RevisionNo=data.get("RevisionNo"),
            VersionNumber=data.get("VersionNumber", 1),
            BackupRestore=BackupRestore(**br) if br else BackupRestore(),
            MapProjectCRC=data.get("MapProjectCRC", False),
            MapSerialNumber=data.get("MapSerialNumber", False),
            ConnectionInfoDataConfigOld=data.get("ConnectionInfoDataConfigOld", False),
            TakeOverSafetyAliasDeviceNamesInProcessImage=data.get("TakeOverSafetyAliasDeviceNamesInProcessImage", False),
            TakeOverStandardAliasDeviceNamesInProcessImage=data.get("TakeOverStandardAliasDeviceNamesInProcessImage", False),
        )

    @classmethod
    def _parse_app(cls, data: dict) -> ApplicationConfiguration:
        groups = [cls._parse_group(g) for g in data.get("TwinSAFEGroups", [])]
        mappings = [Mapping(**m) for m in data.get("Mappings", [])]
        return ApplicationConfiguration(TwinSAFEGroups=groups, Mappings=mappings)

    @classmethod
    def _parse_group(cls, data: dict) -> TwinSAFEGroup:
        alias_devices = []
        for d in data.get("AliasDevices", []):
            if "SafeAddress" in d:
                alias_devices.append(cls._parse_safety_alias(d))
            else:
                alias_devices.append(cls._parse_standard_alias(d))
        fbs = [cls._parse_fb(fb) for fb in data.get("FunctionBlocks", [])]
        outputs = [Port(**p) for p in data.get("GroupOutputs", [])]
        inputs = [Port(**p) for p in data.get("GroupInputs", [])]
        return TwinSAFEGroup(
            Id=data.get("Id", ""),
            OrderId=data.get("OrderId", 0),
            Name=data.get("Name", ""),
            MapDiag=data.get("MapDiag", False),
            MapState=data.get("MapState", False),
            PassificationAllowed=data.get("PassificationAllowed", False),
            TemporaryDeactivationAllowed=data.get("TemporaryDeactivationAllowed", False),
            PermanentDeactivationAllowed=data.get("PermanentDeactivationAllowed", False),
            TimeOutPassificationAllowed=data.get("TimeOutPassificationAllowed", 10000),
            VerifyAnalogFBInputsByStartup=data.get("VerifyAnalogFBInputsByStartup", False),
            AnalogFBOutputCustomReplacementValues=data.get("AnalogFBOutputCustomReplacementValues", False),
            GroupOutputs=outputs,
            GroupInputs=inputs,
            AliasDevices=alias_devices,
            FunctionBlocks=fbs,
            Comment=data.get("Comment", ""),
        )

    @classmethod
    def _parse_safety_alias(cls, data: dict) -> SafetyAliasDevice:
        params = [SafetyParameter(**p) for p in data.get("SafetyParameters", [])]
        return SafetyAliasDevice(
            Id=data.get("Id", ""),
            IsExternal=data.get("IsExternal", False),
            VendorId=data.get("VendorId", 2),
            ProductCode=data.get("ProductCode"),
            RevisionNo=data.get("RevisionNo"),
            Type=data.get("Type", 60),
            SubType=data.get("SubType", 290),
            ConnectionType=data.get("ConnectionType", "FSoEMaster"),
            LogicType=data.get("LogicType", "None"),
            AliasName=data.get("AliasName", ""),
            IoPath=data.get("IoPath", ""),
            ConnectionId=data.get("ConnectionId", 1),
            SafeAddress=data.get("SafeAddress", 1),
            DynamicPortionSafeAddressId=data.get("DynamicPortionSafeAddressId"),
            Watchdog=data.get("Watchdog", 100),
            SafetyParameters=params,
            RxPdo=cls._parse_pi(data.get("RxPdo")),
            TxPdo=cls._parse_pi(data.get("TxPdo")),
            ComErrAckId=data.get("ComErrAckId"),
            ModuleFaultAsComErr=data.get("ModuleFaultAsComErr", False),
            MapState=data.get("MapState", False),
            MapDiag=data.get("MapDiag", False),
            MapInputs=data.get("MapInputs", False),
            MapOutputs=data.get("MapOutputs", False),
            IncrementalDownloadEnabled=data.get("IncrementalDownloadEnabled", False),
        )

    @classmethod
    def _parse_standard_alias(cls, data: dict) -> StandardAliasDevice:
        return StandardAliasDevice(
            Id=data.get("Id", ""),
            OrderId=data.get("OrderId"),
            AliasName=data.get("AliasName", ""),
            RxPdo=cls._parse_pi(data.get("RxPdo")),
            TxPdo=cls._parse_pi(data.get("TxPdo")),
        )

    @classmethod
    def _parse_pi(cls, data: Optional[dict]) -> Optional[ProcessImage]:
        if data is None:
            return None
        elements = [ProcessImageElement(**e) for e in data.get("Elements", [])]
        return ProcessImage(BitSize=data.get("BitSize", 0), Elements=elements)

    @classmethod
    def _parse_fb(cls, data: dict) -> FunctionBlock:
        inports = [Port(**p) for p in data.get("Inports", [])]
        outports = [Port(**p) for p in data.get("Outports", [])]
        return FunctionBlock(
            Id=data.get("Id", ""),
            OrderId=data.get("OrderId", 0),
            Name=data.get("Name", ""),
            Type=data.get("Type", 0),
            MapState=data.get("MapState", False),
            MapDiag=data.get("MapDiag", False),
            Comment=data.get("Comment", ""),
            settings=data.get("settings", {}),
            Inports=inports,
            Outports=outports,
        )
