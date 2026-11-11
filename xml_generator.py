"""
将 TwinSAFEProject 配置模型转换为符合 template.xml 格式的 TwinCATExport XML。
"""
import xml.etree.ElementTree as ET
from typing import Any, List

from config_model import (
    TwinSAFEProject, GeneralInformation, TargetSystemConfiguration,
    TwinSAFEGroup, FunctionBlock, Port, SafetyAliasDevice,
    StandardAliasDevice, ApplicationConfiguration, Mapping,
    ProcessImage, ProcessImageElement, SafetyParameter
)
from port_library import get_port_library


# XSD 中 FunctionBlock 允许的设置字段（按 XSD 顺序）
_FB_SETTING_FIELDS = [
    "SafeInputsAfterDiscrepancyTimeError",
    "DiscTime", "OutputDelayTime", "ManualRestartActive",
    "ManualFunctionTestActive", "SwitchOffTime", "SwitchOnTime",
    "SequentialInputsActive", "FilterTime", "MaxMutingTime",
    "BackwardsMode", "TofTime", "TonTime", "ConnId", "CompareMode",
    "ToleranceTime", "AllowedDeviation", "DivisionRounding",
    "PresetValue", "CounterLimit", "MinValue", "MaxValue",
    "MultiplicationFirst", "ScalingFactorMul", "ScalingFactorDiv",
    "ScalingOffset", "MoveDetectionTime", "PressStartDelayTime",
    "MinPositionChange", "AllowedPositionJitter", "ExcentricMode",
    "StopDetectionTime", "MaxPosition", "TDC1LowerLimit", "TDC1UpperLimit",
    "TDC2LowerLimit", "TDC2UpperLimit", "BDCLowerLimit", "BDCUpperLimit",
    "OverrunMax", "Overflow", "TimeInterval", "Outside", "IncValue",
    "DecValue", "LimitPos", "LimitNeg", "TargetValue", "Offset", "MaxTime",
    "TimeAfterInTarget", "OSSDCheckOptional", "Watchdog",
    "StartsWithRemainingTime", "OverflowAllowed", "ExceededSupport",
    "MultiturnMode", "SingleturnPosLL", "SingleturnPosUL",
    "MultiturnPosLL", "MultiturnPosUL", "ScalingFactorNominator",
    "ScalingFactorDenominator", "ScalingUnit", "EncoderMask",
    "EncoderSubMask", "BrakeTestInterval", "MinCurrentIq",
    "MaxPositionDeviation", "MinDuration", "MaxDuration", "Feedback",
]


def _indent(elem, level=0):
    """美化 XML 缩进"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def _sub(parent, tag, text=None, attrib=None) -> ET.Element:
    el = ET.SubElement(parent, tag)
    if text is not None:
        el.text = str(text)
    if attrib:
        for k, v in attrib.items():
            if v is not None:
                el.set(k, str(v))
    return el


def _add_bool(parent, tag, value: bool):
    return _sub(parent, tag, "true" if value else "false")


class TwinSAFEXmlGenerator:
    """TwinCAT Safety XML 生成器（参照 template.xml 格式）"""

    def __init__(self, project: TwinSAFEProject):
        self.project = project
        self.lib = get_port_library()

    def generate(self) -> ET.Element:
        root = ET.Element("TwinCATExport")
        root.set("Version", self.project.Version)

        self._add_general_information(root, self.project.GeneralInformation)
        self._add_target_system_configuration(root, self.project.TargetSystemConfiguration)
        self._add_application_configuration(root, self.project.ApplicationConfiguration)
        return root

    def generate_string(self) -> str:
        root = self.generate()
        _indent(root)
        return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")

    def generate_file(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.generate_string())

    # ------------------------------------------------------------------
    # GeneralInformation
    # ------------------------------------------------------------------
    def _add_general_information(self, root: ET.Element, gi: GeneralInformation):
        gi_el = _sub(root, "GeneralInformation")
        _sub(gi_el, "ProjectName", gi.ProjectName)
        _sub(gi_el, "Author", gi.Author)
        _sub(gi_el, "InternalProjectName", gi.InternalProjectName)

    # ------------------------------------------------------------------
    # TargetSystemConfiguration
    # ------------------------------------------------------------------
    def _add_target_system_configuration(self, root: ET.Element, tsc: TargetSystemConfiguration):
        tsc_el = _sub(root, "TargetSystemConfiguration", attrib={
            "Id": tsc.Id,
            "Type": tsc.Type,
            "SubType": tsc.SubType,
            "IsExternal": "true" if tsc.IsExternal else "false",
        })
        _sub(tsc_el, "SafeAddress", tsc.SafeAddress)
        if tsc.IoPath:
            _sub(tsc_el, "IoPath", tsc.IoPath)
        if tsc.ProductCode is not None:
            _sub(tsc_el, "ProductCode", tsc.ProductCode)
        if tsc.RevisionNo is not None:
            _sub(tsc_el, "RevisionNo", tsc.RevisionNo)
        _sub(tsc_el, "VersionNumber", 1)  # 固定为 1

        # BackupRestore
        br = tsc.BackupRestore
        br_el = _sub(tsc_el, "BackupRestore", attrib={
            "Activated": "true" if br.Activated else "false",
            "RestoreUserAdministration": "true" if br.RestoreUserAdministration else "false",
            "NumberOfDevicesWithMatchingCRC": str(br.NumberOfDevicesWithMatchingCRC),
        })

        _add_bool(tsc_el, "MapProjectCRC", tsc.MapProjectCRC)
        _add_bool(tsc_el, "MapSerialNumber", tsc.MapSerialNumber)
        _add_bool(tsc_el, "ConnectionInfoDataConfigOld", tsc.ConnectionInfoDataConfigOld)
        _add_bool(tsc_el, "TakeOverSafetyAliasDeviceNamesInProcessImage", tsc.TakeOverSafetyAliasDeviceNamesInProcessImage)
        _add_bool(tsc_el, "TakeOverStandardAliasDeviceNamesInProcessImage", tsc.TakeOverStandardAliasDeviceNamesInProcessImage)

    # ------------------------------------------------------------------
    # ApplicationConfiguration
    # ------------------------------------------------------------------
    def _add_application_configuration(self, root: ET.Element, ac: ApplicationConfiguration):
        ac_el = _sub(root, "ApplicationConfiguration")
        groups_el = _sub(ac_el, "TwinSAFEGroups")
        for group in ac.TwinSAFEGroups:
            self._add_twinsafe_group(groups_el, group)

        # Mappings
        if ac.Mappings:
            self._add_mappings(ac_el, ac.Mappings)

    def _add_mappings(self, parent: ET.Element, mappings: list):
        maps_el = _sub(parent, "Mappings")
        for m in mappings:
            attr = {"SourceId": m.SourceId, "TargetId": m.TargetId}
            if m.LocalVarName:
                attr["LocalVarName"] = m.LocalVarName
            if m.GlobalVarName:
                attr["GlobalVarName"] = m.GlobalVarName
            if m.Local:
                attr["Local"] = "true"
            _sub(maps_el, "Mapping", attrib=attr)

    def _add_twinsafe_group(self, parent: ET.Element, group: TwinSAFEGroup):
        group_el = _sub(parent, "TwinSAFEGroup", attrib={
            "Id": group.Id,
            "OrderId": str(group.OrderId),
        })
        _sub(group_el, "Name", group.Name)

        # TwinSAFEGroupOptions
        opts_el = _sub(group_el, "TwinSAFEGroupOptions")
        _add_bool(opts_el, "MapDiag", group.MapDiag)
        _add_bool(opts_el, "MapState", group.MapState)
        _add_bool(opts_el, "PassificationAllowed", group.PassificationAllowed)
        _add_bool(opts_el, "TemporaryDeactivationAllowed", group.TemporaryDeactivationAllowed)
        _add_bool(opts_el, "PermanentDeactivationAllowed", group.PermanentDeactivationAllowed)
        _sub(opts_el, "TimeOutPassificationAllowed", group.TimeOutPassificationAllowed)
        _add_bool(opts_el, "VerifyAnalogFBInputsByStartup", group.VerifyAnalogFBInputsByStartup)
        _add_bool(opts_el, "AnalogFBOutputCustomReplacementValues", group.AnalogFBOutputCustomReplacementValues)

        # GroupOutputs / GroupInputs
        if group.GroupOutputs:
            self._add_group_ports(group_el, "GroupOutputs", group.GroupOutputs)
        if group.GroupInputs:
            self._add_group_ports(group_el, "GroupInputs", group.GroupInputs)

        # AliasDevices
        alias_el = _sub(group_el, "AliasDevices")
        for dev in group.AliasDevices:
            if isinstance(dev, SafetyAliasDevice):
                self._add_safety_alias_device(alias_el, dev)
            elif isinstance(dev, StandardAliasDevice):
                self._add_standard_alias_device(alias_el, dev)

        # Application -> Network -> FunctionBlocks
        app_el = _sub(group_el, "Application")
        for i, fb in enumerate(group.FunctionBlocks):
            if i == 0:
                net_el = _sub(app_el, "Network", attrib={"Id": f"{group.Id}_n1", "OrderId": "1"})
                _sub(net_el, "Name", "Network1")
            self._add_function_block(net_el, fb)

        if group.Comment:
            _sub(group_el, "Comment", group.Comment)

    def _add_group_ports(self, parent: ET.Element, tag: str, ports: List[Port]):
        gp_el = _sub(parent, tag)
        for port in ports:
            el = _sub(gp_el, "Element", attrib={"Id": port.Id})
            _sub(el, "PortId", port.PortId)
            _sub(el, "Alias", port.Alias)
            _add_bool(el, "Active", port.Active)

    # ------------------------------------------------------------------
    # SafetyAliasDevice
    # ------------------------------------------------------------------
    def _add_safety_alias_device(self, parent: ET.Element, dev: SafetyAliasDevice):
        dev_el = _sub(parent, "SafetyAliasDevice", attrib={
            "Id": dev.Id,
            "IsExternal": "true" if dev.IsExternal else "false",
        })
        _sub(dev_el, "VendorId", dev.VendorId)
        if dev.ProductCode is not None:
            _sub(dev_el, "ProductCode", dev.ProductCode)
        if dev.RevisionNo is not None:
            _sub(dev_el, "RevisionNo", dev.RevisionNo)
        _sub(dev_el, "Type", dev.Type)
        _sub(dev_el, "SubType", dev.SubType)
        _sub(dev_el, "ConnectionType", dev.ConnectionType)
        _sub(dev_el, "LogicType", dev.LogicType)
        _sub(dev_el, "AliasName", dev.AliasName)
        _sub(dev_el, "IoPath", dev.IoPath)
        _sub(dev_el, "ConnectionId", dev.ConnectionId)
        _sub(dev_el, "SafeAddress", dev.SafeAddress)

        # DynamicPortionSafeAddress
        if dev.DynamicPortionSafeAddressId:
            _sub(dev_el, "DynamicPortionSafeAddress", attrib={"Id": dev.DynamicPortionSafeAddressId})

        _sub(dev_el, "Watchdog", dev.Watchdog)

        # SafetyParameters
        if dev.SafetyParameters:
            sp_el = _sub(dev_el, "SafetyParameters")
            for sp in dev.SafetyParameters:
                sp_item = _sub(sp_el, "SafetyParameter", attrib={
                    "OrderId": str(sp.OrderId),
                    "Name": sp.Name,
                })
                sp_item.text = sp.Value

        # RxPdo / TxPdo
        if dev.RxPdo and dev.RxPdo.Elements:
            self._add_process_image(dev_el, "RxPdo", dev.RxPdo)
        if dev.TxPdo and dev.TxPdo.Elements:
            self._add_process_image(dev_el, "TxPdo", dev.TxPdo)

        # ComErrAck
        if dev.ComErrAckId:
            _sub(dev_el, "ComErrAck", attrib={"Id": dev.ComErrAckId})

        _add_bool(dev_el, "ModuleFaultAsComErr", dev.ModuleFaultAsComErr)
        _add_bool(dev_el, "MapState", dev.MapState)
        _add_bool(dev_el, "MapDiag", dev.MapDiag)
        _add_bool(dev_el, "MapInputs", dev.MapInputs)
        _add_bool(dev_el, "MapOutputs", dev.MapOutputs)
        _add_bool(dev_el, "IncrementalDownloadEnabled", dev.IncrementalDownloadEnabled)

    def _add_standard_alias_device(self, parent: ET.Element, dev: StandardAliasDevice):
        attr = {"Id": dev.Id}
        if dev.OrderId is not None:
            attr["OrderId"] = str(dev.OrderId)
        dev_el = _sub(parent, "StandardAliasDevice", attrib=attr)
        _sub(dev_el, "AliasName", dev.AliasName)
        if dev.RxPdo and dev.RxPdo.Elements:
            self._add_process_image(dev_el, "RxPdo", dev.RxPdo)
        if dev.TxPdo and dev.TxPdo.Elements:
            self._add_process_image(dev_el, "TxPdo", dev.TxPdo)

    # ------------------------------------------------------------------
    # ProcessImage (RxPdo/TxPdo)
    # ------------------------------------------------------------------
    def _add_process_image(self, parent: ET.Element, tag: str, pi: ProcessImage):
        pi_el = _sub(parent, tag, attrib={"BitSize": str(pi.BitSize)})
        for elem in pi.Elements:
            el = _sub(pi_el, "Element", attrib={"Id": elem.Id})
            _sub(el, "Name", elem.Name)
            _sub(el, "Type", elem.Type)
            _sub(el, "BitOffset", str(elem.BitOffset))
            _sub(el, "BitSize", str(elem.BitSize))
            _add_bool(el, "IsSafeTimer", elem.IsSafeTimer)
            if elem.Index is not None:
                _sub(el, "Index", elem.Index)
            if elem.SubIndex is not None:
                _sub(el, "SubIndex", elem.SubIndex)
            if elem.Alias:
                _sub(el, "Alias", elem.Alias)

    # ------------------------------------------------------------------
    # FunctionBlock
    # ------------------------------------------------------------------
    def _add_function_block(self, parent: ET.Element, fb: FunctionBlock):
        fb_el = _sub(parent, "FunctionBlock", attrib={"Id": fb.Id, "OrderId": str(fb.OrderId)})
        _sub(fb_el, "Type", fb.Type)
        _sub(fb_el, "Name", fb.Name)
        _add_bool(fb_el, "MapDiag", fb.MapDiag)
        _add_bool(fb_el, "MapState", fb.MapState)

        # 按 XSD 顺序写入 settings
        for key in _FB_SETTING_FIELDS:
            if key in fb.settings and fb.settings[key] is not None:
                _sub(fb_el, key, fb.settings[key])

        # Outports / Inports
        self._add_fb_ports(fb_el, "Outports", fb.Outports)
        self._add_fb_ports(fb_el, "Inports", fb.Inports)

        if fb.Comment:
            _sub(fb_el, "Comment", fb.Comment)

    def _add_fb_ports(self, parent: ET.Element, tag: str, ports: List[Port]):
        if not ports:
            return
        ports_el = _sub(parent, tag)
        for port in ports:
            el = _sub(ports_el, "Element", attrib={"Id": port.Id})
            _sub(el, "PortId", port.PortId)
            if port.PortName:
                _sub(el, "PortName", port.PortName)
            if port.Alias:
                _sub(el, "Alias", port.Alias)
            if port.Type:
                _sub(el, "Type", port.Type)
            _add_bool(el, "Negated", port.Negated)
            _add_bool(el, "Active", port.Active)


def generate_xml(project: TwinSAFEProject, output_path: str):
    gen = TwinSAFEXmlGenerator(project)
    gen.generate_file(output_path)
