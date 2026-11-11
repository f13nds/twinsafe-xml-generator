# TwinSAFE XML 配置生成器（桌面图形界面）

本项目基于工作目录中的 `safety_ports.json` 与上级目录的 XSD 模式文件，提供一个可视化的 TwinSAFE 安全项目配置工具，最终导出符合 `twincat3-safety-editor_export-format.xsd` 的 `TwinCATExport` XML。

> **注意事项**
> 1. 生成的 XML 文件格式遵循 Beckhoff `twincat3-safety-editor_xml-import_export` 文档规范，但**未对功能块的使用规则、逻辑合理性等进行校验**。生成的文件导入 TwinCAT 后进行安全编译时，仍可能因功能块配置不当等原因报错，需根据编译提示自行排查。
> 2. 安全工程中配置的安全设备仅为逻辑层面的定义，**尚未关联到实际硬件设备**。导入 TwinCAT 工程后，需要手动完成安全设备与物理设备的关联映射。

**作者：Will**

## 安全编译环境

本工具生成的 XML 文件面向以下安全编译环境：

| 项目 | 版本 |
|------|------|
| **安全软件** | Beckhoff TE9000 |
| **版本** | 1.4.16 |

> **注意**：生成的 XML 文件需要在 TE9000 1.4.16 环境下进行安全编译。不同版本的 TE9000 可能存在导出格式差异，请确保使用匹配的版本。

## 运行环境

| 依赖 | 要求 | 说明 |
|------|------|------|
| **Python** | 3.12+ | 基础运行环境 |
| **tkinter** | 内置 | 图形界面（随 Python 安装） |
| **pywin32** | 312+ | TwinCAT Automation Interface（导入功能） |
| **操作系统** | Windows | TwinCAT Automation 仅支持 Windows |
| **TwinCAT 3 XAE** | 3.1+ | 安全项目导入目标环境 |
| **可选** | `xmlschema` | 完整 XSD 校验 |

### 安装

```bash
# 基础运行（无需额外依赖）
python gui.py

# 安装 pywin32（TwinCAT Automation Interface 导入功能需要）
pip install pywin32

# 可选：完整 XSD 校验
pip install xmlschema
```

## 使用说明

### 界面概览

界面包含以下标签页：
- **项目信息**：填写项目名称、作者、目标系统类型/子类型、SafeAddress 等。
- **TwinSAFE 组**：添加/删除 TwinSAFE Group，设置组级选项。
- **功能块**：在选定组内添加 FB（自动从 `safety_ports.json` 填充端口），修改属性。
- **别名设备**：管理安全别名设备，支持配置安全 IO（RxPdo/TxPdo）。

顶部工具栏提供：
- **导入 ESI 文件**：从 ESI XML 文件导入安全设备
- **管理导入设备**：查看/删除已导入的 ESI 设备

底部工具栏提供：
- **生成 XML**：导出 TwinCATExport XML 文件
- **校验 XML**：校验生成的 XML 是否符合 XSD 规范
- **解析 TwinCAT 项目**：从 .tsproj 文件提取安全设备 IoPath 信息
- **嵌入 XML 到解决方案**：通过 Automation Interface API 将安全项目导入 TwinCAT 解决方案
- **打开项目目录**：打开程序所在目录

### 操作流程

1. **配置项目信息**：在"项目信息"页填写项目名称、作者、目标系统类型等。
2. **创建 TwinSAFE 组**：在"TwinSAFE 组"页添加组，设置组属性。
3. **导入 ESI 设备**（可选）：点击"导入 ESI 文件"导入第三方安全设备。
4. **添加安全别名设备**：在"别名设备"页添加设备（从下拉列表选择型号），配置别名、SafeAddress、Watchdog。
5. **添加功能块**：在"功能块"页选择 FB 类型添加，配置引脚关联通道。
6. **生成 XML**：点击底部"生成 XML"按钮导出。

### 生成 XML

点击界面底部 **生成 XML**，选择保存路径，即可导出 `TwinCATExport` XML。

### 导入 TwinCAT Safety Editor

生成的 XML 文件可通过 TwinCAT3 Safety Editor 的导入功能加载到安全工程中。详细步骤参见 Beckhoff 文档 `twincat3-safety-editor_xml-import_export` 第 6.1.2 节。

**导入注意事项：**
- 导入前请确保 Safety Editor 版本为 **TE9000 1.4.16**，以保证格式兼容性
- 导入后需要在 Safety Editor 中**手动完成安全设备与物理硬件的关联映射**
- 导入后请执行**安全编译**（Safety Build），根据编译提示排查可能的逻辑配置问题
- 若导入失败，请检查 XML 文件是否完整、格式是否符合 XSD 规范

## 目录结构

```
demo/
├── main.py                    # 程序入口
├── gui.py                     # tkinter 桌面界面
├── config_model.py            # 项目配置数据模型
├── beckhoff_io_library.py     # 安全 IO 设备库（内置设备）
├── esi_parser.py              # ESI 文件解析器
├── esi_devices.json           # ESI 导入设备持久化存储
├── port_library.py            # safety_ports.json 端口库封装
├── xml_generator.py           # 按 XSD 结构生成 XML
├── xsd_validator.py           # XSD 校验
├── twincat_import_safety.py   # TwinCAT Automation Interface 导入子进程
├── safety_ports.json          # FB / Group 端口定义库
├── example_export.xml         # 示例生成的 XML
└── README.md                  # 本说明
```

## 主要功能

### ESI 文件导入

支持从 ESI（EtherCAT Slave Information）文件导入安全设备，自动解析设备信息和 PDO 通道配置。

**支持的 ESI 格式：**
- Beckhoff ESI 文件（`Esi\` 目录）
- Hollysys ESI 文件
- INOVANCE ESI 文件（支持多 FSoE Module 变体）

**导入方式：**
1. 点击 **导入 ESI 文件** 按钮
2. 选择一个或多个 ESI XML 文件
3. 系统自动解析设备信息、VendorId、PDO 通道
4. 重复导入时可选择覆盖或跳过

**SM 属性方向解析：**
- `SM="2"` → 输出通道（FB 输出，设备命令）
- `SM="3"` → 输入通道（FB 输入，设备状态）

**持久化存储：**
导入的设备保存到 `esi_devices.json`，程序启动时自动加载。

### 设备管理

通过 **管理导入设备** 页面管理 ESI 导入的设备：
- 查看所有导入设备及其来源文件
- 删除选中设备或全部导入设备
- 仅显示 ESI 导入的设备（内置设备不显示）

### 安全 IO 设备选择

在 **别名设备** 配置对话框中，可从预定义的安全 IO 设备库中选择设备型号，自动填充设备参数和安全 IO 配置。同时支持从 ESI 文件导入的第三方设备。

**支持的设备型号：**

| 型号 | 描述 | 通道数 |
|------|------|--------|
| **EL1904** | 4通道数字量安全输入 | 4 DI + 状态/通信 |
| **EL2904** | 4通道数字量安全输出 | 4 DO + 状态/通信 |
| **EL1918** | 8通道数字量安全输入（带通道诊断） | 8 DI + 状态/通信 |
| **EL2911** | 4通道安全输入 + 1通道安全输出 | 4 DI + 1 DO |
| **EL2912** | 2通道安全输出 2A | 2 DO + 状态/通信 |
| **EP1918** | 8通道数字量安全输入（带通道诊断） | 8 DI + 状态/通信 |
| **EP1957** | 8通道数字量安全输入 + 4通道数字量安全输出 | 8 DI + 4 DO |
| **EP2918** | 8通道数字量安全输出（带通道诊断） | 8 DO + 状态/通信 |
| **EJ1914** | 4通道安全输入（EJ 系列） | 4 DI + 状态/通信 |
| **EJ1918** | 8通道安全输入（EJ 系列） | 8 DI + 状态/通信 |
| **EJ1957** | 8通道安全输入 + 4通道安全输出（EJ 系列） | 8 DI + 4 DO |
| **EJ2914** | 4通道安全输出（EJ 系列） | 4 DO + 状态/通信 |
| **EJ2918** | 8通道安全输出（EJ 系列） | 8 DO + 状态/通信 |
| **EK1914** | 2通道安全输入 + 2通道安全输出 | 2 DI + 2 DO |

> 注：EJ 系列设备支持 FW1/FW2 两种固件变体，PDO 配置相同。

**使用方法：**
1. 在 **别名设备** 标签页点击 **添加安全别名设备**
2. 在对话框顶部 **设备型号** 下拉框中选择设备型号（仅显示型号）
3. 系统自动填充设备参数和安全 IO 配置
4. 根据需要修改别名、SafeAddress、Watchdog 后点击确定

### 安全 PLC 双模式

支持双模式的设备（含 EL1918、EP1918、EP1957、EP2918、EJ 系列）：

1. **作为安全 PLC**：选择为目标系统类型时，自动创建 Local 连接类型的安全别名设备（SafeAddress=0）
2. **作为别名设备**：作为安全 IO 设备添加到组中

### TwinCAT 项目解析

从 `.tsproj` 文件提取安全设备的 IoPath 信息，自动创建安全别名设备：

1. 点击底部 **解析 TwinCAT 项目** 按钮
2. 选择 `.tsproj` 项目文件
3. 弹窗显示检测到的安全设备（含 IoPath 预览）
4. 勾选需要导入的设备，选择安全 PLC（单选）
5. 点击确定自动创建安全别名设备

**IoPath 规则：**
- 安全 PLC IoPath（无 Module 后缀）→ `TargetSystemConfiguration`
- 别名设备 IoPath（含 Module 后缀）→ `SafetyAliasDevice`
- PLC 的 Local 别名设备不设置 IoPath

**设备识别：**
- 优先从 EtherCAT `Type` 属性提取型号（如 `"EL1918, 8Ch. Safety Input..."` → `EL1918`）
- 回退到 Box 名称提取（如 `"Term 5 (EL6910)"` → `EL6910`）
- 纯 PLC 设备（如 EL6910）显示为"仅可作为安全 PLC"
- 未知设备显示"⚠ 未知安全设备"

### 嵌入 XML 到解决方案

通过 TwinCAT Automation Interface API 将安全项目直接导入 TwinCAT 解决方案：

1. 点击底部 **嵌入 XML 到解决方案** 按钮
2. 选择 TwinCAT 解决方案文件（`.sln`）
3. 选择安全项目文件（`.xml` 或 `.tfzip`）
4. 项目名称自动从 XML 文件读取
5. 自动导入到解决方案的安全项目树中

**技术实现：**
- 使用 `TcXaeShell.DTE.17.0` COM 接口
- 通过 `project.Object` 获取 `ITcSysManager`
- 使用 `CreateChild` 方法导入安全项目
- 子进程方式执行 COM 操作，避免 tkinter/COM 冲突

### 功能块引脚关联

功能块引脚支持关联安全别名设备的通道：
- **输入引脚**：单选关联输入通道（RxPdo/SM=3）
- **输出引脚**：多选关联输出通道（TxPdo/SM=2）

### C 命名规则自动清理

所有名称字段（别名、组名、功能块名、变量名）自动符合 C 语言命名规则：
- 非法字符（`-`、`.`、空格、中文等）自动转换为 `_`
- 连续下划线合并为单个
- 首尾下划线自动去除
- 数字开头自动添加 `_` 前缀

**示例：**
| 输入 | 输出 |
|------|------|
| `InoSV680S-FSoE-SRA` | `InoSV680S_FSoE_SRA` |
| `EL1918, 8 digital inputs` | `EL1918_8_digital_inputs` |
| `123Device` | `_123Device` |

### 自动创建的系统设备

每个 TwinSAFE 组自动创建以下系统设备（不可编辑/删除）：
- **ErrorAcknowledgement**：错误确认信号
- **Run**：运行信号

## 配置文件保存

通过菜单 **文件 → 保存项目 JSON**，当前项目结构会保存为 JSON；下次可通过 **打开项目 JSON** 继续编辑。

## 设计要点

- 严格遵循 XSD 元素顺序（`TwinCATExport` → `GeneralInformation` → `TargetSystemConfiguration` → `ApplicationConfiguration`）。
- `FunctionBlock` 的设置字段仅当配置中提供时才输出。
- `PortId` 使用 `safety_ports.json` 中的十六进制值，符合 XSD `HexDecUInt32Value` 类型。
- 空的可选元素会被省略，避免 XSD 顺序/空值问题。
- 安全 IO 配置（RxPdo/TxPdo）按 XSD `ProcessImage` 类型实现。
- ID 自动生成规则遵循 PDF 7.2 规范。
- ESI 导入使用 SM 属性判断通道方向（SM=2→输出，SM=3→输入）。
- 所有名称字段自动清理为 C 命名规则（非法字符→`_`）。
- 设备库支持 VendorId、SubType、ProductCode 等完整设备信息。
- FW2 固件变体与基础型号共享相同 PDO 配置。

## 依赖

- Python 3.12+
- 内置 `tkinter`
- `pywin32`（TwinCAT Automation Interface 导入功能）
- 可选：`xmlschema`（完整 XSD 校验）

---

## 免责声明

本工具仅供学习和工程辅助使用，生成的 XML 文件不保证在所有场景下均能通过安全编译。在实际安全工程中使用前，请务必进行充分的测试和验证，确保满足相关安全标准和规范要求。
