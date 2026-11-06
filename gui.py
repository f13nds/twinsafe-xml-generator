"""
TwinSAFE XML 配置生成器 —— 桌面图形界面（tkinter）
"""
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, Any, List

from config_model import (
    TwinSAFEProject, GeneralInformation, TargetSystemConfiguration,
    TwinSAFEGroup, FunctionBlock, Port, SafetyAliasDevice,
    StandardAliasDevice, ApplicationConfiguration, Mapping,
    ProcessImage, ProcessImageElement
)
from port_library import get_port_library
from beckhoff_io_library import (
    get_device_display_list, parse_device_key,
    create_alias_device_from_library, get_device_info
)
from xml_generator import TwinSAFEXmlGenerator
from xsd_validator import validate_with_xsd


def validate_c_identifier(name: str) -> tuple:
    """校验是否符合 C 语言变量命名规则
    
    规则：
    - 只能包含字母、数字、下划线
    - 不能以数字开头
    - 不能为空
    
    Returns:
        (bool, str): (是否合法, 错误提示)
    """
    if not name:
        return False, "名称不能为空"
    if name[0].isdigit():
        return False, f"'{name}' 不能以数字开头"
    for i, ch in enumerate(name):
        if not (ch.isalnum() or ch == '_'):
            return False, f"'{name}' 包含非法字符 '{ch}'，只允许字母、数字和下划线"
    return True, ""


def resource_path(relative_path: str) -> str:
    """兼容 PyInstaller 打包后的资源文件路径"""
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

DEFAULT_XSD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def center_window_on_mouse(window, width=None, height=None):
    """将窗口居中显示在鼠标所在的屏幕位置
    
    Args:
        window: tk.Toplevel 或 tk.Tk 窗口
        width: 窗口宽度（可选，如果不提供则从窗口获取）
        height: 窗口高度（可选，如果不提供则从窗口获取）
    """
    # 获取鼠标位置
    mouse_x = window.winfo_pointerx()
    mouse_y = window.winfo_pointery()
    
    # 获取屏幕尺寸
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # 获取窗口尺寸
    if width is None or height is None:
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
    
    # 计算居中位置（相对于鼠标位置）
    x = mouse_x - width // 2
    y = mouse_y - height // 2
    
    # 确保窗口在屏幕范围内
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + width > screen_width:
        x = screen_width - width
    if y + height > screen_height:
        y = screen_height - height
    
    # 设置窗口位置
    window.geometry(f"{width}x{height}+{x}+{y}")


class ProcessImageDialog(tk.Toplevel):
    """安全IO配置对话框 (RxPdo/TxPdo)"""

    def __init__(self, parent, pi: Optional[ProcessImage], title="安全IO配置"):
        super().__init__(parent)
        self.title(title)
        self.result: Optional[ProcessImage] = None
        self.pi = pi or ProcessImage()
        self._build_ui()
        self.transient(parent)
        self.grab_set()
        # 居中显示在鼠标位置
        center_window_on_mouse(self, 700, 500)

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)
        ttk.Label(top, text="BitSize:").pack(side=tk.LEFT)
        self.bitsize_var = tk.StringVar(value=str(self.pi.BitSize))
        ttk.Entry(top, textvariable=self.bitsize_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="添加元素", command=self._add_element).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="删除选中", command=self._delete_element).pack(side=tk.LEFT, padx=5)

        cols = ("Id", "Name", "Alias", "Type", "BitOffset", "BitSize")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._refresh_tree()

        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self._ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in self.pi.Elements:
            self.tree.insert("", tk.END, values=(e.Id, e.Name, e.Alias, e.Type, e.BitOffset, e.BitSize))

    def _add_element(self):
        idx = len(self.pi.Elements) + 1
        elem = ProcessImageElement(Id=f"Elem{idx}", Name=f"IO_{idx}", Type="BIT", BitOffset=0, BitSize=1)
        self.pi.Elements.append(elem)
        self._refresh_tree()

    def _delete_element(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.pi.Elements.pop(idx)
        self._refresh_tree()

    def _ok(self):
        try:
            self.pi.BitSize = int(self.bitsize_var.get())
        except ValueError:
            pass
        self.result = self.pi
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
        self.result = None
        self.destroy()


class AliasDeviceDialog(tk.Toplevel):
    """安全别名设备配置对话框"""

    def __init__(self, parent, device: Optional[SafetyAliasDevice] = None, next_device_id: str = "", next_connection_id: int = 1, next_safe_address: int = 1, safety_plc_type: str = "", existing_alias_names: set = None, existing_safe_addresses: set = None, is_safety_plc: bool = False):
        super().__init__(parent)
        self.title("编辑安全别名设备" if device else "添加安全别名设备")
        self.result = None  # 单个设备或设备列表
        self.next_device_id = next_device_id or "g1_a1"
        self.next_connection_id = next_connection_id
        self.next_safe_address = next_safe_address
        self.safety_plc_type = safety_plc_type
        self.existing_alias_names = existing_alias_names or set()
        self.existing_safe_addresses = existing_safe_addresses or set()
        self.is_safety_plc = is_safety_plc  # 安全PLC设备：仅允许修改 AliasName
        self._last_device_key = ""  # 上一次自动填入的设备型号（用于判断是否更新别名）
        self.is_edit_mode = device is not None  # 编辑模式标记
        self.device = device or SafetyAliasDevice(
            Id=self.next_device_id, AliasName="", VendorId=2, SubType=1,
            ConnectionId=self.next_connection_id, SafeAddress=self.next_safe_address, Watchdog=100
        )
        self._build_ui()
        self.transient(parent)
        self.grab_set()
        # 居中显示在鼠标位置
        center_window_on_mouse(self, 500, 350)

    def _build_ui(self):
        
        # =========================================================
        # 倍福安全IO设备选择（编辑模式下只读显示）
        # =========================================================
        device_frame = ttk.LabelFrame(self, text="设备信息", padding=10)
        device_frame.pack(fill=tk.X, padx=10, pady=5)

        if self.is_edit_mode:
            # 编辑模式：只读显示设备型号
            model = self._get_device_model_name()
            ttk.Label(device_frame, text="设备型号:").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(device_frame, text=model, foreground="gray").grid(row=0, column=1, sticky=tk.W, pady=2)
        else:
            # 添加模式：可选设备型号（仅显示型号）
            ttk.Label(device_frame, text="设备型号:").grid(row=0, column=0, sticky=tk.W, pady=2)
            if self.safety_plc_type == "EL6900":
                allowed_keys = {"EL1904", "EL2904"}
                device_values = [d for d in get_device_display_list() if d in allowed_keys]
            else:
                device_values = get_device_display_list()
            self.device_combo = ttk.Combobox(device_frame, state="readonly", width=40,
                                             values=device_values)
            self.device_combo.grid(row=0, column=1, sticky=tk.EW, pady=2)
            self.device_combo.bind("<<ComboboxSelected>>", self._on_device_selected)

        device_frame.columnconfigure(1, weight=1)

        # =========================================================
        # 基本参数（别名、SafeAddress、Watchdog）
        # =========================================================
        fields_frame = ttk.LabelFrame(self, text="基本参数", padding=10)
        fields_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entries = {}
        # 安全PLC设备编辑时：仅显示 AliasName
        if self.is_edit_mode and self.is_safety_plc:
            fields = [("别名", "AliasName")]
        else:
            fields = [
                ("别名", "AliasName"),
                ("SafeAddress", "SafeAddress"),
                ("Watchdog", "Watchdog"),
            ]
        for row, (label, key) in enumerate(fields):
            ttk.Label(fields_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            ent = ttk.Entry(fields_frame, width=37)
            ent.grid(row=row, column=1, sticky=tk.EW, pady=2)
            val = getattr(self.device, key, "")
            ent.insert(0, str(val) if val is not None else "")
            self.entries[key] = ent
        
        # 添加数量输入框（批量添加，仅添加模式显示）
        row_count = len(fields)
        if not self.is_edit_mode:
            ttk.Label(fields_frame, text="添加数量").grid(row=row_count, column=0, sticky=tk.W, pady=2)
            self.quantity_var = tk.IntVar(value=1)
            qty_spin = ttk.Spinbox(fields_frame, from_=1, to=100, textvariable=self.quantity_var, width=10)
            qty_spin.grid(row=row_count, column=1, sticky=tk.W, pady=2)

        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self._ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)

    def _get_device_model_name(self):
        """获取当前设备型号缩写"""
        subtype_map = {190: "EL1904", 290: "EL2904", 17827710: "EL1918",
                       526206: "EP1918", 526245: "EP1957", 527206: "EP2918"}
        if self.device and hasattr(self.device, 'SubType'):
            return subtype_map.get(self.device.SubType, f"SubType={self.device.SubType}")
        return "未知"

    # =============================================================
    # 倍福设备选择（选择后自动填充参数）
    # =============================================================
    def _on_device_selected(self, event):
        display = self.device_combo.get()
        if not display:
            return
        device_key = display.strip()
        info = get_device_info(device_key)
        if info:
            # 更新默认别名（始终使用当前选中的设备型号）
            current_alias = self.entries["AliasName"].get().strip()
            # 如果别名为空或等于上一次自动填入的型号，更新为新设备型号
            if not current_alias or current_alias == self._last_device_key:
                self.entries["AliasName"].delete(0, tk.END)
                self.entries["AliasName"].insert(0, device_key)
            self._last_device_key = device_key
            
            # 自动创建设备配置（无需按钮）
            self._auto_fill_device_config(device_key)

    def _auto_fill_device_config(self, device_key):
        """自动填充设备配置"""
        try:
            # 获取当前用户输入的参数
            current_alias = self.entries["AliasName"].get()
            current_watchdog = self.entries["Watchdog"].get()

            # 使用全局唯一的 SafeAddress
            safe_addr = self.next_safe_address
            watchdog = int(current_watchdog) if current_watchdog else 100

            # 创建设备配置
            # 如果是编辑模式，保留原有的 ConnectionId；如果是新增模式，使用自动递增的 ConnectionId
            if self.device and hasattr(self.device, 'ConnectionId') and self.device.ConnectionId:
                conn_id = self.device.ConnectionId  # 保留原有的 ConnectionId
            else:
                conn_id = self.next_connection_id  # 使用自动递增的 ConnectionId

            self.device = create_alias_device_from_library(
                device_key,
                alias_name=current_alias or device_key,
                safe_address=safe_addr,
                connection_id=conn_id,
                watchdog=watchdog,
                device_id=self.next_device_id
            )

            # 更新 UI
            self._update_ui_from_device()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _update_ui_from_device(self):
        d = self.device
        self._set_entry(self.entries["AliasName"], d.AliasName)
        self._set_entry(self.entries["SafeAddress"], d.SafeAddress)
        self._set_entry(self.entries["Watchdog"], d.Watchdog)

    def _set_entry(self, widget, value):
        if isinstance(widget, ttk.Combobox):
            widget.set(str(value) if value is not None else "")
        else:
            widget.delete(0, tk.END)
            widget.insert(0, str(value) if value is not None else "")

    def _make_unique_alias(self, base_name, used_names):
        """生成不重复的别名名称
        
        Args:
            base_name: 基础名称
            used_names: 已使用的名称集合
        
        Returns:
            str: 唯一的别名名称
        """
        # 先尝试基础名称
        if base_name not in used_names:
            return base_name
        
        # 尝试 base_name_1, base_name_2, ... 直到找到唯一名称
        n = 1
        while True:
            candidate = f"{base_name}_{n}"
            if candidate not in used_names:
                return candidate
            n += 1

    def _ok(self):
        # 获取用户输入的基础参数
        base_alias = self.entries["AliasName"].get().strip()
        safe_addr_str = self.entries.get("SafeAddress")
        safe_addr_str = safe_addr_str.get().strip() if safe_addr_str else ""
        watchdog_str = self.entries.get("Watchdog")
        watchdog_str = watchdog_str.get().strip() if watchdog_str else ""
        watchdog = int(watchdog_str) if watchdog_str else 100
        
        # ===== 编辑模式 =====
        if self.is_edit_mode:
            # 校验别名不能为空
            if not base_alias:
                messagebox.showwarning("校验失败", "别名不能为空")
                return
            
            # 校验别名符合 C 变量命名规则
            ok, msg = validate_c_identifier(base_alias)
            if not ok:
                messagebox.showwarning("校验失败", f"别名{msg}")
                return
            
            # 校验别名唯一性（同组内，排除自身）
            if self.existing_alias_names and base_alias in self.existing_alias_names:
                messagebox.showwarning("校验失败", f"别名 '{base_alias}' 在当前组内已存在，请使用其他名称")
                return
            
            # 安全PLC设备仅修改 AliasName
            if self.is_safety_plc:
                self.device.AliasName = base_alias
                self.result = self.device
                self.destroy()
                return
            
            # 普通设备：校验 SafeAddress
            try:
                safe_addr = int(safe_addr_str)
                if safe_addr < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                messagebox.showwarning("校验失败", "SafeAddress 必须为非负整数")
                return
            
            # 校验 SafeAddress 全局唯一（排除自身）
            if safe_addr in self.existing_safe_addresses:
                messagebox.showwarning("校验失败", f"SafeAddress {safe_addr} 在项目中已被其他设备使用，请使用其他地址")
                return
            
            self.device.AliasName = base_alias
            self.device.SafeAddress = safe_addr
            self.device.Watchdog = watchdog
            self.result = self.device
            self.destroy()
            return
        
        # ===== 添加模式（原有逻辑不变） =====
        # 校验别名符合 C 变量命名规则
        if base_alias:
            ok, msg = validate_c_identifier(base_alias)
            if not ok:
                messagebox.showwarning("校验失败", f"别名{msg}")
                return
        
        display = self.device_combo.get()
        if not display:
            messagebox.showwarning("提示", "请先选择设备型号")
            return
        
        device_key = parse_device_key(display)
        info = get_device_info(device_key)
        
        if not info:
            messagebox.showerror("错误", f"未找到设备信息: {device_key}")
            return
        
        # 获取数量
        try:
            quantity = self.quantity_var.get()
            if quantity < 1:
                quantity = 1
        except Exception:
            quantity = 1
        
        if quantity == 1:
            # 单个设备模式
            safe_addr_str = self.entries["SafeAddress"].get().strip()
            safe_addr = int(safe_addr_str) if safe_addr_str else self.next_safe_address
            
            if not base_alias:
                base_alias = f"{device_key}_{self.next_device_id.split('_')[-1]}"
            
            dev = create_alias_device_from_library(
                device_key,
                alias_name=base_alias,
                safe_address=safe_addr,
                connection_id=self.next_connection_id,
                watchdog=watchdog,
                device_id=self.next_device_id
            )
            self.result = dev
        else:
            # 批量创建模式
            devices = []
            from beckhoff_io_library import BECKHOFF_SAFETY_DEVICES
            dev_info = BECKHOFF_SAFETY_DEVICES.get(device_key, {})
            default_name = dev_info.get("name", device_key)
            
            # 解析基础ID号
            base_id = self.next_device_id
            if "_a" in base_id:
                prefix = base_id.rsplit("_a", 1)[0]
                start_num = int(base_id.rsplit("_a", 1)[1])
            else:
                prefix = base_id
                start_num = 1
            
            current_safe_addr = self.next_safe_address
            current_conn_id = self.next_connection_id
            
            # 收集已使用的别名（包括已有的和本次批量中已生成的）
            used_names = set(self.existing_alias_names)
            
            for i in range(quantity):
                # 生成设备ID
                dev_id = f"{prefix}_a{start_num + i}"
                
                # 生成AliasName（确保全局唯一）
                if base_alias and quantity > 1:
                    alias_name = self._make_unique_alias(f"{base_alias}", used_names)
                elif base_alias:
                    alias_name = self._make_unique_alias(base_alias, used_names)
                else:
                    alias_name = self._make_unique_alias(default_name, used_names)
                
                used_names.add(alias_name)
                
                # 创建设备
                dev = create_alias_device_from_library(
                    device_key,
                    alias_name=alias_name,
                    safe_address=current_safe_addr,
                    connection_id=current_conn_id,
                    watchdog=watchdog,
                    device_id=dev_id
                )
                devices.append(dev)
                print(f"  Created device {i+1}: {dev_id} alias={alias_name} safe_addr={current_safe_addr}")
                
                # 递增 SafeAddress 和 ConnectionId
                current_safe_addr += 1
                current_conn_id += 1
            
            self.result = devices
            print(f"  Total devices created: {len(devices)}")
        
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class TwinSAFEConfiguratorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TwinSAFE XML 配置生成器")
        self.root.geometry("1200x800")

        self.project = TwinSAFEProject()
        self.lib = get_port_library()
        self.current_file: Optional[str] = None

        # 关闭窗口时弹窗确认是否保存
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_menu()
        self._build_main_layout()
        self._new_project()

    def _on_close(self):
        """关闭程序时提示是否保存项目配置"""
        result = messagebox.askyesnocancel(
            "保存项目",
            "是否保存项目配置？\n\n是 - 保存为 JSON 文件后退出\n否 - 不保存直接退出\n取消 - 返回继续编辑"
        )
        if result is None:
            # 取消：不退出
            return
        elif result:
            # 是：保存后退出
            saved = self._save_project()
            if not saved:
                # 用户取消了保存对话框，不退出
                return
        # 否或保存成功后退出
        self.root.destroy()

    # ------------------------------------------------------------------
    # 菜单
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建项目", command=self._new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="打开项目 JSON", command=self._open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="保存项目 JSON", command=self._save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        gen_menu = tk.Menu(menubar, tearoff=0)
        gen_menu.add_command(label="生成 XML", command=self._generate_xml)
        gen_menu.add_command(label="校验 XML", command=self._validate_xml)
        menubar.add_cascade(label="生成", menu=gen_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="说明", command=self._open_readme)
        help_menu.add_separator()
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)
        self.root.bind("<Control-n>", lambda e: self._new_project())
        self.root.bind("<Control-o>", lambda e: self._open_project())
        self.root.bind("<Control-s>", lambda e: self._save_project())

    def _open_readme(self):
        """打开 README.md 文件"""
        import os
        import subprocess
        readme_path = resource_path("README.md")
        if os.path.exists(readme_path):
            try:
                os.startfile(readme_path)
            except AttributeError:
                # 非 Windows 系统
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", readme_path])
            self.log_message(f"打开说明文档: {readme_path}")
        else:
            messagebox.showwarning("提示", f"未找到 README.md 文件: {readme_path}")

    def _show_about(self):
        """显示关于对话框"""
        about_win = tk.Toplevel(self.root)
        about_win.title("关于")
        about_win.resizable(False, False)
        about_win.transient(self.root)
        about_win.grab_set()
        
        frame = ttk.Frame(about_win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="TwinSAFE XML 配置生成器", font=("", 14, "bold")).pack(pady=(0, 5))
        ttk.Label(frame, text="作者: Will").pack(pady=2)
        ttk.Label(frame, text="用于生成 TwinCAT3 Safety Editor 导出 XML 文件").pack(pady=2)
        
        ttk.Button(frame, text="确定", command=about_win.destroy).pack(pady=(10, 0))
        
        about_win.update_idletasks()
        center_window_on_mouse(about_win, 350, 200)

    # ------------------------------------------------------------------
    # 主布局
    # ------------------------------------------------------------------
    def _build_main_layout(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="项目结构").pack(anchor=tk.W, pady=(0, 5))
        self.tree = ttk.Treeview(left_frame, selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_project_tab()
        self._build_group_tab()
        self._build_fb_tab()
        self._build_alias_tab()

        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(bottom, text="生成 XML", command=self._generate_xml).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom, text="校验 XML", command=self._validate_xml).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom, text="打开项目目录", command=self._open_project_dir).pack(side=tk.LEFT, padx=5)

        ttk.Label(bottom, text="作者: Will", foreground="gray").pack(side=tk.RIGHT, padx=(0, 10))
        self.status = ttk.Label(bottom, text="就绪", relief=tk.SUNKEN)
        self.status.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        self.log = scrolledtext.ScrolledText(self.root, height=8, state=tk.DISABLED)
        self.log.pack(fill=tk.X, padx=5, pady=(0, 5))

    # ------------------------------------------------------------------
    # 项目信息 Tab
    # ------------------------------------------------------------------
    def _build_project_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="项目信息")

        frame = ttk.LabelFrame(tab, text="基本信息", padding=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        self.entries_project = {}
        for row, (label, key) in enumerate([
            ("项目名称", "ProjectName"),
            ("作者", "Author"),
        ]):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            ent = ttk.Entry(frame, width=50)
            ent.grid(row=row, column=1, sticky=tk.EW, pady=3)
            ent.bind("<KeyRelease>", lambda e, k=key: self._update_project_from_entries(k))
            self.entries_project[key] = ent

        frame2 = ttk.LabelFrame(tab, text="目标系统", padding=10)
        frame2.pack(fill=tk.X, padx=5, pady=5)
        self.entries_target = {}
        # 不显示 ID、类型、版本号、IoPath
        target_fields = [
            ("SafeAddress", "SafeAddress"),
            ("安全PLC", "SubType"),
        ]
        for row, (label, key) in enumerate(target_fields):
            ttk.Label(frame2, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            if key == "SubType":
                values = ["EL6900", "EL6910", "EL1918", "EP1918", "EP1957", "EP2918"]
                cb = ttk.Combobox(frame2, values=values, state="readonly", width=48)
                cb.grid(row=row, column=1, sticky=tk.EW, pady=3)
                cb.bind("<<ComboboxSelected>>", lambda e, k=key: self._update_target_from_entries(k))
                self.entries_target[key] = cb
            else:
                ent = ttk.Entry(frame2, width=50)
                ent.grid(row=row, column=1, sticky=tk.EW, pady=3)
                ent.bind("<KeyRelease>", lambda e, k=key: self._update_target_from_entries(k))
                self.entries_target[key] = ent

        ttk.Button(tab, text="应用并刷新结构树", command=self._refresh_tree).pack(anchor=tk.W, padx=5, pady=10)

    # ------------------------------------------------------------------
    # TwinSAFE 组 Tab
    # ------------------------------------------------------------------
    def _build_group_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="TwinSAFE 组")

        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top, text="添加组", command=self._add_group).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="删除选中组", command=self._delete_group).pack(side=tk.LEFT, padx=3)

        self.group_listbox = tk.Listbox(tab, height=8)
        self.group_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.group_listbox.bind("<<ListboxSelect>>", self._on_group_select)

        self.group_detail = ttk.LabelFrame(tab, text="组属性", padding=10)
        self.group_detail.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.entries_group = {}
        # 不显示 ID、OrderId、PassificationAllowed 等选项
        for row, (label, key) in enumerate([
            ("名称", "Name"),
            ("MapDiag", "MapDiag"), ("MapState", "MapState"),
            ("Comment", "Comment"),
        ]):
            ttk.Label(self.group_detail, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            if key in ("MapDiag", "MapState"):
                cb = ttk.Combobox(self.group_detail, values=["true", "false"], state="readonly", width=48)
                cb.grid(row=row, column=1, sticky=tk.EW, pady=3)
                cb.bind("<<ComboboxSelected>>", lambda e: self._sync_group_from_entries())
                self.entries_group[key] = cb
            else:
                ent = ttk.Entry(self.group_detail, width=50)
                ent.grid(row=row, column=1, sticky=tk.EW, pady=3)
                ent.bind("<KeyRelease>", lambda e: self._sync_group_from_entries())
                ent.bind("<FocusOut>", lambda e: self._sync_group_from_entries())
                self.entries_group[key] = ent

    # ------------------------------------------------------------------
    # 功能块 Tab（含引脚映射）
    # ------------------------------------------------------------------
    def _build_fb_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="功能块")

        # 顶部：添加/删除 FB
        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top, text="选择 FB 类型:").pack(side=tk.LEFT)
        self.fb_type_var = tk.StringVar()
        # 允许显示的 FB 类型（其他保留在库中供后续使用）
        _VISIBLE_FB_TYPES = [
            "FBEstop", "FBMon", "FBAnd", "FBOr", "FBDecouple",
            "FBOpmode", "FBTwohand", "FBEdm", "FBMuting",
            "FBRs", "FBSr", "FBTof", "FBTon", "FBTon2", "FBConnShutdown",
        ]
        visible_fb_types = [t for t in self.lib.get_fb_types() if t in _VISIBLE_FB_TYPES]
        self.fb_type_combo = ttk.Combobox(top, textvariable=self.fb_type_var,
                                          values=visible_fb_types, state="readonly", width=25)
        self.fb_type_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="添加 FB", command=self._add_fb).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="删除选中 FB", command=self._delete_fb).pack(side=tk.LEFT, padx=3)

        # 主面板：左侧 FB 列表，右侧 FB 属性 + 引脚映射
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧：FB 列表
        left = ttk.Frame(paned, width=200)
        paned.add(left, weight=1)
        ttk.Label(left, text="功能块列表").pack(anchor=tk.W)
        self.fb_listbox = tk.Listbox(left)
        self.fb_listbox.pack(fill=tk.BOTH, expand=True)
        self.fb_listbox.bind("<<ListboxSelect>>", self._on_fb_select)

        # 右侧
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # FB 属性
        self.fb_detail = ttk.LabelFrame(right, text="FB 属性", padding=10)
        self.fb_detail.pack(fill=tk.X, padx=5, pady=5)
        self.entries_fb = {}
        # 不显示 ID、OrderId
        fb_fields = [("名称", "Name"), ("MapState", "MapState"), ("MapDiag", "MapDiag"), ("Comment", "Comment")]
        for row, (label, key) in enumerate(fb_fields):
            ttk.Label(self.fb_detail, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            if key in ("MapState", "MapDiag"):
                cb = ttk.Combobox(self.fb_detail, values=["true", "false"], state="readonly", width=40)
                cb.grid(row=row, column=1, sticky=tk.EW, pady=2)
                cb.bind("<<ComboboxSelected>>", lambda e: self._sync_fb_from_entries())
                self.entries_fb[key] = cb
            else:
                ent = ttk.Entry(self.fb_detail, width=42)
                ent.grid(row=row, column=1, sticky=tk.EW, pady=2)
                ent.bind("<KeyRelease>", lambda e: self._sync_fb_from_entries())
                ent.bind("<FocusOut>", lambda e: self._sync_fb_from_entries())
                self.entries_fb[key] = ent

        # 引脚映射
        pin_frame = ttk.LabelFrame(right, text="引脚配置", padding=10)
        pin_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 说明文字
        desc_text = "说明: 勾选启用引脚后，可输入变量名并关联安全别名设备的通道。\n"
        desc_text += "关联通道用于建立功能块引脚与安全IO设备之间的映射关系。"
        desc_label = ttk.Label(pin_frame, text=desc_text, foreground="gray", wraplength=600)
        desc_label.pack(fill=tk.X, pady=(0, 5))

        # 引脚标题行（不显示 PortId）- 使用可拖动布局
        header_frame = ttk.Frame(pin_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header_frame, text="启用", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="引脚名", width=15).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="类型", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="变量名", width=20).pack(side=tk.LEFT, padx=2)
        
        # 可拖动的分隔条
        self.channel_separator = ttk.Separator(header_frame, orient=tk.VERTICAL)
        self.channel_separator.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        
        ttk.Label(header_frame, text="关联别名设备通道").pack(side=tk.LEFT, padx=2)

        # 引脚列表容器（可滚动）
        pin_container = ttk.Frame(pin_frame)
        pin_container.pack(fill=tk.BOTH, expand=True)

        # 使用 Canvas + Frame 实现滚动
        pin_canvas = tk.Canvas(pin_container)
        pin_scrollbar = ttk.Scrollbar(pin_container, orient=tk.VERTICAL, command=pin_canvas.yview)
        self.pin_scroll_frame = ttk.Frame(pin_canvas)

        self.pin_scroll_frame.bind("<Configure>",
                                   lambda e: pin_canvas.configure(scrollregion=pin_canvas.bbox("all")))
        pin_canvas.create_window((0, 0), window=self.pin_scroll_frame, anchor="nw")
        pin_canvas.configure(yscrollcommand=pin_scrollbar.set)

        pin_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pin_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 存储引脚控件
        self.pin_widgets = {}  # source_id -> {"enabled": BooleanVar, "var_entry": Entry, "frame": Frame}
        self.pin_enabled = {}  # source_id -> bool
        self.pin_var_names = {}  # source_id -> var_name
        self.pin_target_ids = {}  # source_id -> target_id (别名设备通道)
        self.current_fb = None  # 当前选中的功能块
        self.current_group = None  # 当前选中的组
        self.selected_output_channels = set()  # 已选择的输出通道 (target_id)
        self.channel_column_width = 50  # 通道列默认宽度（可拖动调整）

    def _rebuild_pin_state_from_fb(self, fb):
        """从 Port.Active 和 Mappings 重建引脚状态（用于 JSON 导入后恢复）
        
        Args:
            fb: FunctionBlock 对象
        """
        if not fb:
            return
        
        mappings = self.project.ApplicationConfiguration.Mappings
        
        # 处理所有引脚（输出和输入）
        for port in fb.Outports + fb.Inports:
            source_id = port.Id
            
            # 从 Port.Active 恢复启用状态
            self.pin_enabled[source_id] = port.Active
            
            if not port.Active:
                continue
            
            # 从 Mappings 恢复变量名和通道关联
            # 输入引脚: TargetId=pin_id, SourceId=channel_id
            # 输出引脚: SourceId=pin_id, TargetId=channel_id
            target_ids = []
            var_name = ""
            
            # 判断引脚类型：Outports 在前，Inports 在后
            is_output = port in fb.Outports
            
            for m in mappings:
                if is_output:
                    # 输出引脚：只匹配 SourceId == pin_id 的映射
                    if m.SourceId == source_id:
                        target_ids.append(m.TargetId)
                        if m.LocalVarName:
                            var_name = m.LocalVarName
                else:
                    # 输入引脚：只匹配 TargetId == pin_id 的映射
                    if m.TargetId == source_id:
                        target_ids.append(m.SourceId)
                        if m.LocalVarName:
                            var_name = m.LocalVarName
            
            if target_ids:
                self.pin_target_ids[source_id] = target_ids
            if var_name:
                self.pin_var_names[source_id] = var_name

    def _refresh_pin_tree(self, fb=None):
        """刷新当前 FB 的引脚列表"""
        # 清除旧的引脚控件
        for widget in self.pin_scroll_frame.winfo_children():
            widget.destroy()
        self.pin_widgets.clear()

        # 如果没有传入 fb，从当前选择获取
        if fb is None:
            g = self._current_group()
            if not g:
                return
            sel = self.fb_listbox.curselection()
            if not sel:
                return
            fb = g.FunctionBlocks[sel[0]]
        
        # 从项目数据重建引脚状态（JSON 导入后恢复启用状态、变量名、通道关联）
        self._rebuild_pin_state_from_fb(fb)

        # 获取别名设备通道列表（按引脚类型过滤）
        output_channels = self._get_alias_channels(pin_type="输出")
        input_channels = self._get_alias_channels(pin_type="输入")

        # 显示输出引脚（只显示输出通道）
        for port in fb.Outports:
            self._create_pin_row(port, "输出", output_channels)

        # 显示输入引脚（只显示输入通道）
        for port in fb.Inports:
            self._create_pin_row(port, "输入", input_channels)

    def _get_alias_channels(self, pin_type=None):
        """获取当前组别名设备的通道列表，返回 [(显示名, target_id), ...]
        
        Args:
            pin_type: "输入" 只返回输入通道(RxPdo), "输出" 只返回输出通道(TxPdo), None 返回所有
        """
        channels = []
        g = self._current_group()  # 只获取当前组的设备
        if not g:
            return channels
        for dev in g.AliasDevices:
            dev_name = dev.AliasName or dev.Id
            # 跳过 ErrorAcknowledgement 和 Run 设备
            if dev_name in ("ErrorAcknowledgement", "Run"):
                continue
            # RxPdo 通道（输入）
            if pin_type != "输出" and hasattr(dev, 'RxPdo') and dev.RxPdo:
                for elem in dev.RxPdo.Elements:
                    display = f"{dev_name}.{elem.Name}"
                    channels.append((display, elem.Id))
            # TxPdo 通道（输出）
            if pin_type != "输入" and hasattr(dev, 'TxPdo') and dev.TxPdo:
                for elem in dev.TxPdo.Elements:
                    display = f"{dev_name}.{elem.Name}"
                    channels.append((display, elem.Id))
        return channels

    def _create_pin_row(self, port, pin_type, alias_channels):
        """创建一行引脚配置"""
        source_id = port.Id
        pin_name = port.PortName or port.Alias
        enabled = self.pin_enabled.get(source_id, False)
        var_name = self.pin_var_names.get(source_id, "")
        target_ids = self.pin_target_ids.get(source_id, [])

        # 创建行框架
        row_frame = ttk.Frame(self.pin_scroll_frame)
        row_frame.pack(fill=tk.X, pady=1)

        # 启用复选框
        enabled_var = tk.BooleanVar(value=enabled)
        chk = ttk.Checkbutton(row_frame, variable=enabled_var, width=4,
                              command=lambda: self._on_pin_toggle(source_id, enabled_var, port))
        chk.pack(side=tk.LEFT, padx=2)

        # 引脚名
        ttk.Label(row_frame, text=pin_name, width=15, anchor=tk.W).pack(side=tk.LEFT, padx=2)

        # 类型
        type_color = "blue" if pin_type == "输出" else "green"
        ttk.Label(row_frame, text=pin_type, width=6, foreground=type_color).pack(side=tk.LEFT, padx=2)

        # 变量名输入框（禁用状态时不可编辑）
        var_entry = ttk.Entry(row_frame, width=20)
        var_entry.pack(side=tk.LEFT, padx=2)
        var_entry.insert(0, var_name)

        # 别名设备通道选择
        if pin_type == "输出":
            # 输出引脚：使用下拉方式选择（支持多选）
            channel_frame = ttk.Frame(row_frame)
            channel_frame.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            # 显示已选择的通道
            selected_display = self._get_selected_channels_display(source_id, target_ids, alias_channels)
            
            channel_combo = ttk.Combobox(channel_frame, width=50, state="readonly")
            channel_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            channel_combo.set(selected_display if selected_display else "点击选择通道")
            
            # 绑定点击事件，打开多选对话框
            channel_combo.bind("<Button-1>",
                              lambda e, sid=source_id, channels=alias_channels:
                              self._open_channel_selector(sid, channels))
            
            if not enabled:
                channel_combo.configure(state="disabled")
            
            # 存储控件引用
            channel_widget = channel_combo
        else:
            # 输入引脚：使用 Combobox 下拉单选
            channel_display = ""
            for display, tid in alias_channels:
                if tid == (target_ids[0] if target_ids else ""):
                    channel_display = display
                    break

            channel_combo = ttk.Combobox(row_frame, width=50, values=[d for d, _ in alias_channels])
            channel_combo.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            if channel_display:
                channel_combo.set(channel_display)

            if not enabled:
                channel_combo.configure(state="disabled")
            else:
                channel_combo.configure(state="readonly")

            # 绑定事件
            channel_combo.bind("<<ComboboxSelected>>",
                               lambda e, sid=source_id, combo=channel_combo, channels=alias_channels:
                               self._on_channel_selected(sid, combo, channels))
            
            channel_widget = channel_combo

        # 绑定变量名事件
        var_entry.bind("<FocusOut>", lambda e, sid=source_id, entry=var_entry: self._on_var_changed(sid, entry))
        var_entry.bind("<Return>", lambda e, sid=source_id, entry=var_entry: self._on_var_changed(sid, entry))

        # 存储控件引用和 Port 对象
        self.pin_widgets[source_id] = {
            "enabled_var": enabled_var,
            "var_entry": var_entry,
            "channel_widget": channel_widget,
            "frame": row_frame,
            "pin_type": pin_type,
            "port": port,  # 存储 Port 对象引用
            "pin_name": pin_name,  # 存储引脚名称用于生成变量名
        }

    def _get_available_output_channels(self, current_source_id, alias_channels):
        """获取可用的输出通道（排除已被其他输出引脚选择的通道）"""
        available = []
        for display, tid in alias_channels:
            # 检查是否已被其他输出引脚选择
            is_selected_by_other = False
            for sid, selected_tids in self.pin_target_ids.items():
                if sid != current_source_id and tid in selected_tids:
                    is_selected_by_other = True
                    break
            if not is_selected_by_other:
                available.append((display, tid))
        return available

    def _get_short_channel_name(self, display_name):
        """获取简化的通道显示名称（解决名称过长问题）
        
        例如: "EL1918, 8 digital inputs (FW 2)_1.FSIN Module 1.Input" -> "FSIN Module 1.Input"
        使用 rsplit 从最后一个 "." 分割，避免设备名称中包含 "." 的问题
        """
        # 如果包含 "."，从最后一个 "." 分割，取后面的部分
        if "." in display_name:
            return display_name.rsplit(".", 1)[1]
        return display_name

    def _get_selected_channels_display(self, source_id, target_ids, alias_channels):
        """获取已选择通道的显示文本"""
        if not target_ids:
            return ""
        display_names = []
        for tid in target_ids:
            for d, t in alias_channels:
                if t == tid:
                    display_names.append(d)  # 使用完整显示名称
                    break
        return ", ".join(display_names)

    def _open_channel_selector(self, source_id, alias_channels):
        """打开输出引脚通道多选对话框"""
        # 获取可用通道
        available_channels = self._get_available_output_channels(source_id, alias_channels)
        
        if not available_channels:
            messagebox.showinfo("提示", "没有可用的通道")
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择输出通道")
        dialog.transient(self.root)
        dialog.grab_set()
        # 居中显示在鼠标位置
        center_window_on_mouse(dialog, 550, 400)
        
        ttk.Label(dialog, text="请选择输出通道（可多选）:").pack(padx=10, pady=5, anchor=tk.W)
        
        # 通道列表
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 单选模式使用 SINGLE，多选模式使用 MULTIPLE
        selectmode = tk.MULTIPLE
        listbox = tk.Listbox(listbox_frame, selectmode=selectmode, height=15, font=("Microsoft YaHei", 9))
        scrollbar_y = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar_x = ttk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL, command=listbox.xview)
        listbox.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        # 添加可用通道（使用完整显示名称）
        display_to_tid = {}
        for display, tid in available_channels:
            listbox.insert(tk.END, display)
            display_to_tid[display] = tid
        
        # 选中已选择的通道
        current_targets = self.pin_target_ids.get(source_id, [])
        for display, tid in available_channels:
            if tid in current_targets:
                idx = list(listbox.get(0, tk.END)).index(display)
                listbox.selection_set(idx)
        
        def on_ok():
            selected_indices = listbox.curselection()
            selected_tids = []
            for idx in selected_indices:
                display = listbox.get(idx)
                if display in display_to_tid:
                    selected_tids.append(display_to_tid[display])
            
            # 更新已选择的输出通道
            self.pin_target_ids[source_id] = selected_tids
            
            # 更新显示
            if source_id in self.pin_widgets:
                combo = self.pin_widgets[source_id].get("channel_widget")
                if combo and isinstance(combo, ttk.Combobox):
                    display_text = self._get_selected_channels_display(source_id, self.pin_target_ids[source_id], alias_channels)
                    combo.set(display_text if display_text else "点击选择通道")
            
            # 更新全局已选择的输出通道集合
            self._update_selected_output_channels()
            
            # 同步到 Mapping
            self._sync_output_pins_to_mapping()
            
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 按钮
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

    def _on_output_channels_selected(self, source_id, listbox, alias_channels):
        """输出引脚通道多选变更"""
        selected_indices = listbox.curselection()
        selected_tids = []
        for idx in selected_indices:
            display = listbox.get(idx)
            for d, tid in alias_channels:
                if d == display:
                    selected_tids.append(tid)
                    break
        
        # 更新已选择的输出通道
        self.pin_target_ids[source_id] = selected_tids
        
        # 更新全局已选择的输出通道集合
        self._update_selected_output_channels()
        
        # 同步到 Mapping
        self._sync_output_pins_to_mapping()

    def _on_pin_toggle(self, source_id, enabled_var, port):
        """引脚启用/禁用切换"""
        enabled = enabled_var.get()
        self.pin_enabled[source_id] = enabled

        # 直接更新 Port 的 Active 状态
        port.Active = enabled

        # 更新变量名输入框和通道选择控件状态
        if source_id in self.pin_widgets:
            widgets = self.pin_widgets[source_id]
            entry = widgets["var_entry"]
            channel_widget = widgets.get("channel_widget")
            pin_name = widgets.get("pin_name", "")
            
            if enabled:
                entry.configure(state="normal")
                # 如果是第一次启用且变量名为空，自动生成变量名
                if not entry.get().strip():
                    # 获取 FB 名称（从存储的引用）
                    fb_name = ""
                    if self.current_fb:
                        fb_name = self.current_fb.Name
                    # 自动生成变量名: FBName_PinName
                    auto_var_name = f"{fb_name}_{pin_name}" if fb_name and pin_name else pin_name
                    entry.insert(0, auto_var_name)
                    self.pin_var_names[source_id] = auto_var_name
                
                if channel_widget:
                    if isinstance(channel_widget, tk.Listbox):
                        channel_widget.configure(state="normal")
                    else:
                        channel_widget.configure(state="readonly")
            else:
                # 取消启用时，自动清除变量名和通道关联
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                entry.configure(state="disabled")
                self.pin_var_names.pop(source_id, None)
                
                if channel_widget:
                    if isinstance(channel_widget, tk.Listbox):
                        channel_widget.configure(state="normal")
                        channel_widget.selection_clear(0, tk.END)
                        channel_widget.configure(state="disabled")
                    elif isinstance(channel_widget, ttk.Combobox):
                        channel_widget.configure(state="normal")
                        channel_widget.set("")
                        channel_widget.configure(state="disabled")
                    else:
                        channel_widget.configure(state="disabled")
                
                # 清除通道关联
                self.pin_target_ids.pop(source_id, None)
                
                # 更新已选输出通道集合
                self._update_selected_output_channels()

        # 同步到 Mapping
        self._sync_pin_to_mapping(source_id, enabled)

    def _on_channel_selected(self, source_id, combo, alias_channels):
        """输入引脚通道选择变更"""
        display = combo.get()
        # 查找 target_id（使用完整显示名称匹配）
        target_id = ""
        for d, tid in alias_channels:
            if d == display:
                target_id = tid
                break
        self.pin_target_ids[source_id] = [target_id] if target_id else []

        # 同步到 Mapping
        if self.pin_enabled.get(source_id, False):
            self._sync_pin_to_mapping(source_id, True)

    def _update_selected_output_channels(self):
        """更新全局已选择的输出通道集合"""
        self.selected_output_channels.clear()
        for sid, tids in self.pin_target_ids.items():
            widgets = self.pin_widgets.get(sid, {})
            if widgets.get("pin_type") == "输出":
                for tid in tids:
                    self.selected_output_channels.add(tid)

    def _sync_output_pins_to_mapping(self):
        """同步所有输出引脚到 Mapping"""
        for sid in self.pin_target_ids:
            widgets = self.pin_widgets.get(sid, {})
            if widgets.get("pin_type") == "输出" and self.pin_enabled.get(sid, False):
                self._sync_pin_to_mapping(sid, True)

    def _on_var_changed(self, source_id, entry):
        """变量名变更"""
        var_name = entry.get().strip()
        if var_name:
            ok, msg = validate_c_identifier(var_name)
            if not ok:
                messagebox.showwarning("校验失败", f"变量名{msg}")
                return
        self.pin_var_names[source_id] = var_name

        # 同步到 Mapping
        if self.pin_enabled.get(source_id, False):
            self._sync_pin_to_mapping(source_id, True)

    def _sync_pin_to_mapping(self, pin_id, enabled):
        """同步引脚状态到 Mapping
        
        Mapping 规则 (PDF 7.2):
        1. FB 输入 <- 安全输入模块通道:
           TargetId = FB 输入引脚 ID
           SourceId = 安全输入模块通道 ID
        2. FB 输出 -> 安全输出模块通道:
           TargetId = 模块输出通道 ID
           SourceId = FB 输出引脚 ID
        """
        # 获取引脚类型和关联的模块通道
        pin_type = self.pin_widgets.get(pin_id, {}).get("pin_type", "")
        target_ids = self.pin_target_ids.get(pin_id, [])
        if isinstance(target_ids, str):
            target_ids = [target_ids] if target_ids else []
        
        var_name = self.pin_var_names.get(pin_id, "")
        
        if pin_type == "输入":
            # FB 输入引脚：TargetId 是 FB 引脚 ID
            module_channel_id = target_ids[0] if target_ids else ""
            
            # 查找现有映射
            existing = None
            for m in self.project.ApplicationConfiguration.Mappings:
                if m.TargetId == pin_id:
                    existing = m
                    break
            
            if enabled and module_channel_id:
                # FB 输入 <- 安全输入模块通道
                if existing:
                    existing.LocalVarName = var_name
                    existing.TargetId = pin_id
                    existing.SourceId = module_channel_id
                else:
                    m = Mapping(
                        TargetId=pin_id,          # FB 输入引脚 ID
                        SourceId=module_channel_id,  # 安全输入模块通道 ID
                        LocalVarName=var_name,
                    )
                    self.project.ApplicationConfiguration.Mappings.append(m)
            else:
                # 禁用时删除映射
                if existing:
                    self.project.ApplicationConfiguration.Mappings.remove(existing)
        else:
            # FB 输出引脚：SourceId 是 FB 引脚 ID，支持多个目标
            # 先删除该引脚的所有现有映射
            to_remove = []
            for m in self.project.ApplicationConfiguration.Mappings:
                if m.SourceId == pin_id:
                    to_remove.append(m)
            for m in to_remove:
                self.project.ApplicationConfiguration.Mappings.remove(m)
            
            # 为每个选中的输出通道创建映射
            if enabled:
                for module_channel_id in target_ids:
                    if module_channel_id:
                        m = Mapping(
                            SourceId=pin_id,          # FB 输出引脚 ID
                            TargetId=module_channel_id,  # 模块输出通道 ID
                            LocalVarName=var_name,
                        )
                        self.project.ApplicationConfiguration.Mappings.append(m)

    # ------------------------------------------------------------------
    # 别名设备 Tab
    # ------------------------------------------------------------------
    def _build_alias_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="别名设备")

        top = ttk.Frame(tab)
        top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top, text="添加安全别名设备", command=self._add_safety_alias).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="编辑选中设备", command=self._edit_alias).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="删除选中设备", command=self._delete_alias).pack(side=tk.LEFT, padx=3)

        # 显示 AliasName, 型号, SafeAddress, Watchdog
        cols = ("AliasName", "型号", "SafeAddress", "Watchdog")
        self.alias_tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        self.alias_tree.heading("AliasName", text="AliasName")
        self.alias_tree.heading("型号", text="型号")
        self.alias_tree.heading("SafeAddress", text="SafeAddress")
        self.alias_tree.heading("Watchdog", text="Watchdog")
        self.alias_tree.column("AliasName", width=250)
        self.alias_tree.column("型号", width=80)
        self.alias_tree.column("SafeAddress", width=100)
        self.alias_tree.column("Watchdog", width=100)
        self.alias_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._refresh_alias_tree()

    # ------------------------------------------------------------------
    # 项目操作
    # ------------------------------------------------------------------
    def _new_project(self):
        self.project = TwinSAFEProject()
        self.current_file = None
        group = TwinSAFEGroup(Id="g1", OrderId=0, Name="TwinSafeGroup1")
        # 添加 Group 输入信号 (参照 template.xml)
        group.GroupInputs = [
            Port(Id="g1_i1", PortId="16842752", Alias="RunStop", Active=True),
            Port(Id="g1_i2", PortId="16908288", Alias="ErrAck", Active=True),
            Port(Id="g1_i3", PortId="16973824", Alias="ModuleFault", Active=True),
        ]
        # 添加 StandardAliasDevice (ErrorAcknowledgement 和 Run 信号)
        from config_model import StandardAliasDevice, ProcessImage, ProcessImageElement
        group.AliasDevices = [
            StandardAliasDevice(
                Id="g1_a1", OrderId=1, AliasName="ErrorAcknowledgement",
                RxPdo=ProcessImage(BitSize=1, Elements=[
                    ProcessImageElement(Id="g1_a1_i1", Name="In", Type="BIT", BitOffset=0, BitSize=1),
                ])
            ),
            StandardAliasDevice(
                Id="g1_a2", OrderId=2, AliasName="Run",
                RxPdo=ProcessImage(BitSize=1, Elements=[
                    ProcessImageElement(Id="g1_a2_i1", Name="In", Type="BIT", BitOffset=0, BitSize=1),
                ])
            ),
        ]
        self.project.ApplicationConfiguration.TwinSAFEGroups.append(group)
        self.current_group = group  # 存储当前选中的组
        self.current_fb = None  # 清空当前 FB
        # 添加 Group 信号映射 (参照 template.xml)
        from config_model import Mapping
        self.project.ApplicationConfiguration.Mappings = [
            Mapping(TargetId="g1_i2", SourceId="g1_a1_i1", LocalVarName="GroupPort_ErrAck"),
            Mapping(TargetId="g1_i1", SourceId="g1_a2_i1", LocalVarName="GroupPort_RunStop"),
        ]
        self._refresh_ui()
        self.log_message("已创建新项目")

    def _open_project(self):
        path = filedialog.askopenfilename(defaultextension=".json",
                                          filetypes=[("JSON 项目", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.project = TwinSAFEProject._from_dict(data)
            self.current_file = path
            self._refresh_ui()
            self.log_message(f"已打开项目：{path}")
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def _save_project(self) -> bool:
        """保存项目配置，返回是否保存成功"""
        if not self.current_file:
            path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON 项目", "*.json")])
            if not path:
                return False
            self.current_file = path
        try:
            self.project.save(self.current_file)
            self.log_message(f"项目已保存：{self.current_file}")
            return True
        except Exception as e:
            messagebox.showerror("保存失败", str(e))
            return False

    # ------------------------------------------------------------------
    # 生成 / 校验
    # ------------------------------------------------------------------
    def _generate_xml(self):
        self._sync_from_ui()
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("TwinSAFE XML", "*.xml"), ("所有文件", "*.*")],
            initialfile="TwinSAFE_Export.xml"
        )
        if not path:
            return
        try:
            gen = TwinSAFEXmlGenerator(self.project)
            gen.generate_file(path)
            self.log_message(f"XML 已生成：{path}")
            self.status.config(text=f"已生成：{os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("生成失败", str(e))

    def _validate_xml(self):
        path = filedialog.askopenfilename(defaultextension=".xml",
                                          filetypes=[("XML 文件", "*.xml")])
        if not path:
            return
        result = validate_with_xsd(path)
        self.log_message(str(result))
        self.status.config(text="校验完成" if result.ok else "校验失败")

    def _open_project_dir(self):
        os.startfile(os.path.dirname(__file__) or ".")

    # ------------------------------------------------------------------
    # UI 同步
    # ------------------------------------------------------------------
    def _sync_from_ui(self):
        self._update_project_from_entries(None)
        self._update_target_from_entries(None)
        self._update_group()
        self._update_fb()

    def _refresh_ui(self):
        self._refresh_project_entries()
        self._refresh_target_entries()
        self._refresh_tree()
        self._refresh_group_list()
        self._refresh_fb_list()
        self._refresh_alias_tree()
        # 设置默认选中的组
        if self.project.ApplicationConfiguration.TwinSAFEGroups:
            self.current_group = self.project.ApplicationConfiguration.TwinSAFEGroups[0]
            self.current_fb = None

    def _refresh_project_entries(self):
        gi = self.project.GeneralInformation
        self._set_entry(self.entries_project["ProjectName"], gi.ProjectName)
        self._set_entry(self.entries_project["Author"], gi.Author)

    def _refresh_target_entries(self):
        t = self.project.TargetSystemConfiguration
        self._set_entry(self.entries_target["SafeAddress"], str(t.SafeAddress))
        self._set_entry(self.entries_target["SubType"], t.SubType)

    def _set_entry(self, widget, value):
        if isinstance(widget, ttk.Combobox):
            widget.set(value)
        else:
            widget.delete(0, tk.END)
            widget.insert(0, value if value is not None else "")

    def _update_project_from_entries(self, key=None):
        gi = self.project.GeneralInformation
        gi.ProjectName = self.entries_project["ProjectName"].get() or gi.ProjectName
        gi.Author = self.entries_project["Author"].get()

    def _update_target_from_entries(self, key=None):
        t = self.project.TargetSystemConfiguration
        try:
            t.SafeAddress = int(self.entries_target["SafeAddress"].get())
        except ValueError:
            pass
        old_subtype = t.SubType
        t.SubType = self.entries_target["SubType"].get() or t.SubType
        
        # 如果安全PLC类型变更，自动删除旧的安全PLC别名设备，添加新的
        if key == "SubType" and old_subtype != t.SubType:
            self._remove_safety_plc_device()
            if t.SubType in ("EL1918", "EP1918", "EP1957", "EP2918"):
                self._add_el1918_as_plc_device()

    # EL1918/EP系列设备的 SubType 列表（支持安全PLC双模式）
    _EL1918_LIKE_SUBTYPES = {17827710, 526206, 526245, 527206}
    _EL1918_LIKE_NAMES = {"EL1918", "EP1918", "EP1957", "EP2918"}

    def _remove_safety_plc_device(self):
        """自动删除 TwinSafeGroup1 中的安全PLC别名设备（ConnectionType=Local, SafeAddress=0）"""
        g = None
        for group in self.project.ApplicationConfiguration.TwinSAFEGroups:
            if group.Name == "TwinSafeGroup1" or group.Id == "g1":
                g = group
                break
        if not g:
            return
        
        # 查找并删除安全PLC设备
        to_remove = []
        for dev in g.AliasDevices:
            if (isinstance(dev, SafetyAliasDevice)
                    and hasattr(dev, 'ConnectionType') and dev.ConnectionType == "Local"
                    and hasattr(dev, 'SafeAddress') and dev.SafeAddress == 0):
                to_remove.append(dev)
        
        for dev in to_remove:
            g.AliasDevices.remove(dev)
            self.log_message(f"安全PLC变更，自动删除设备 {dev.Id} ({dev.AliasName})")
        
        if to_remove:
            self._refresh_alias_tree()
            self._refresh_tree()
            self._refresh_pin_tree()

    def _add_el1918_as_plc_device(self):
        """当安全PLC为EL1918/EP1918/EP1957/EP2918时，自动添加对应别名设备到TwinSafeGroup1"""
        from beckhoff_io_library import create_alias_device_from_library, BECKHOFF_SAFETY_DEVICES
        
        # 获取 TwinSafeGroup1
        g = None
        for group in self.project.ApplicationConfiguration.TwinSAFEGroups:
            if group.Name == "TwinSafeGroup1" or group.Id == "g1":
                g = group
                break
        
        if not g:
            messagebox.showwarning("提示", "未找到 TwinSafeGroup1，无法添加设备")
            return
        
        # 确定当前安全PLC设备类型
        plc_type = self.entries_target["SubType"].get() if "SubType" in self.entries_target else "EL1918"
        if plc_type not in self._EL1918_LIKE_NAMES:
            plc_type = "EL1918"
        
        # 映射到设备库key和SubType
        device_map = {"EL1918": ("EL1918", 17827710), "EP1918": ("EP1918", 526206), "EP1957": ("EP1957", 526245), "EP2918": ("EP2918", 527206)}
        device_key, target_subtype = device_map.get(plc_type, ("EL1918", 17827710))
        
        # 检查是否已存在同类型安全PLC设备
        for dev in g.AliasDevices:
            if hasattr(dev, 'SubType') and dev.SubType == target_subtype and dev.SafeAddress == 0 and dev.ConnectionType == "Local":
                messagebox.showinfo("提示", f"TwinSafeGroup1 中已存在 {plc_type} 安全PLC设备")
                return
        
        # 创建设备（作为安全PLC使用，ConnectionType=Local, SafeAddress=0）
        next_id = self._get_next_device_id()
        alias_name = "Local"  # 安全PLC设备默认别名
        
        # 检查 AliasName "Local" 是否已被占用（防止与手动添加的设备冲突）
        existing_names = {d.AliasName for d in g.AliasDevices if hasattr(d, 'AliasName') and d.AliasName}
        if alias_name in existing_names:
            alias_name = self._make_unique_alias(alias_name, existing_names)
        
        plc_device = create_alias_device_from_library(
            device_key,
            alias_name=alias_name,
            safe_address=0,
            connection_id=self._get_next_connection_id(),
            watchdog=100,
            device_id=next_id
        )
        # 设置为 Local 连接类型（作为安全PLC）
        plc_device.ConnectionType = "Local"
        
        g.AliasDevices.append(plc_device)
        self._refresh_alias_tree()
        self._refresh_tree()
        self._refresh_pin_tree()
        self.log_message(f"安全PLC为 {plc_type}，自动添加 {plc_type} 别名设备到 TwinSafeGroup1")

    # ------------------------------------------------------------------
    # 结构树
    # ------------------------------------------------------------------
    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        root = self.tree.insert("", tk.END, text="TwinSAFE Project", values=("root",), open=True)
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            g_node = self.tree.insert(root, tk.END, text=f"组: {g.Name or g.Id}", values=("group", g.Id), open=True)
            # 始终显示 AliasDevices 和 FB 子节点
            self.tree.insert(g_node, tk.END, text="AliasDevices", values=("alias_devices", g.Id))
            self.tree.insert(g_node, tk.END, text="FB", values=("fb_list", g.Id))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item.get("values", ())
        if not values:
            return
        kind = values[0]
        if kind == "root":
            # 顶层节点：显示项目信息页面，不显示功能块和别名设备
            self.notebook.select(self.notebook.tabs()[0])
        elif kind == "group":
            # 组节点：显示组属性页面，不显示功能块和别名设备
            self._select_group_by_id(values[1])
            self.notebook.select(self.notebook.tabs()[1])
        elif kind == "alias_devices":
            # AliasDevices节点：只显示别名设备页面
            self._select_group_by_id(values[1])
            self.notebook.select(self.notebook.tabs()[3])  # 别名设备 Tab
        elif kind == "fb_list":
            # FB节点：只显示功能块页面
            self._select_group_by_id(values[1])
            self.notebook.select(self.notebook.tabs()[2])  # 功能块 Tab

    # ------------------------------------------------------------------
    # 组管理
    # ------------------------------------------------------------------
    def _refresh_group_list(self):
        self.group_listbox.delete(0, tk.END)
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            self.group_listbox.insert(tk.END, g.Name)  # 只显示组名称

    def _add_group(self):
        idx = len(self.project.ApplicationConfiguration.TwinSAFEGroups) + 1
        # PDF 7.2: Group ID 格式 g{N}, OrderId 自动累加
        # 组名称统一为 TwinSafeGroup{N}
        g = TwinSAFEGroup(Id=f"g{idx}", OrderId=idx - 1, Name=f"TwinSafeGroup{idx}")
        
        # 自动创建 Group 输入信号
        g.GroupInputs = [
            Port(Id=f"{g.Id}_i1", PortId="16842752", Alias="RunStop", Active=True),
            Port(Id=f"{g.Id}_i2", PortId="16908288", Alias="ErrAck", Active=True),
            Port(Id=f"{g.Id}_i3", PortId="16973824", Alias="ModuleFault", Active=True),
        ]
        
        # 自动创建 StandardAliasDevice ErrorAcknowledgement
        from config_model import StandardAliasDevice, ProcessImage, ProcessImageElement, Mapping
        g.AliasDevices = [
            StandardAliasDevice(
                Id=f"{g.Id}_a1", OrderId=1, AliasName="ErrorAcknowledgement",
                RxPdo=ProcessImage(BitSize=1, Elements=[
                    ProcessImageElement(Id=f"{g.Id}_a1_i1", Name="In", Type="BIT", BitOffset=0, BitSize=1),
                ])
            ),
        ]
        
        # 自动创建 Mapping
        self.project.ApplicationConfiguration.Mappings.append(
            Mapping(TargetId=f"{g.Id}_i2", SourceId=f"{g.Id}_a1_i1", LocalVarName="GroupPort_ErrAck")
        )
        
        self.project.ApplicationConfiguration.TwinSAFEGroups.append(g)
        self.current_group = g  # 存储当前选中的组
        self._refresh_group_list()
        self._refresh_tree()
        self.log_message(f"添加组 {g.Id}")

    def _delete_group(self):
        sel = self.group_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        g = self.project.ApplicationConfiguration.TwinSAFEGroups.pop(idx)
        
        # 清理与该组相关的所有 Mapping（以组 ID 前缀匹配）
        gid = g.Id
        prefix = f"{gid}_"
        to_remove = []
        for m in self.project.ApplicationConfiguration.Mappings:
            if (m.TargetId and m.TargetId.startswith(prefix)) or \
               (m.SourceId and m.SourceId.startswith(prefix)):
                to_remove.append(m)
        for m in to_remove:
            self.project.ApplicationConfiguration.Mappings.remove(m)
        
        self._refresh_group_list()
        self._refresh_tree()
        self._refresh_alias_tree()
        self._refresh_fb_list()
        self._clear_pin_tree()
        self.log_message(f"删除组 {gid}（清理了 {len(to_remove)} 条相关 Mapping）")

    def _on_group_select(self, event):
        sel = self.group_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        g = self.project.ApplicationConfiguration.TwinSAFEGroups[idx]
        self.current_group = g  # 存储当前选中的组
        self._fill_group_entries(g)

    def _select_group_by_id(self, gid: str):
        for i, g in enumerate(self.project.ApplicationConfiguration.TwinSAFEGroups):
            if g.Id == gid:
                self.group_listbox.selection_clear(0, tk.END)
                self.group_listbox.selection_set(i)
                self.group_listbox.see(i)
                self.current_group = g  # 存储当前选中的组
                self.current_fb = None  # 清空当前 FB
                self._fill_group_entries(g)
                # 刷新别名设备和功能块列表（只显示当前组的数据）
                self._refresh_alias_tree()
                self._refresh_fb_list()
                # 清空引脚配置页面
                self._clear_pin_tree()
                break

    def _clear_pin_tree(self):
        """清空引脚配置页面"""
        for widget in self.pin_scroll_frame.winfo_children():
            widget.destroy()
        self.pin_widgets.clear()

    def _fill_group_entries(self, g: TwinSAFEGroup):
        self._set_entry(self.entries_group["Name"], g.Name)
        self._set_entry(self.entries_group["MapDiag"], "true" if g.MapDiag else "false")
        self._set_entry(self.entries_group["MapState"], "true" if g.MapState else "false")
        self._set_entry(self.entries_group["Comment"], g.Comment)

    def _sync_group_from_entries(self):
        """实时同步组属性（无弹窗校验，轻量级）"""
        g = self._current_group()
        if not g:
            return
        g.Name = self.entries_group["Name"].get().strip()
        g.MapDiag = self.entries_group["MapDiag"].get() == "true"
        g.MapState = self.entries_group["MapState"].get() == "true"
        g.Comment = self.entries_group["Comment"].get()
        self._refresh_group_list()
        self._refresh_tree()

    def _sync_fb_from_entries(self):
        """实时同步FB属性（无弹窗校验，轻量级）"""
        g = self._current_group()
        if not g:
            return
        fb = self.current_fb
        if not fb:
            sel = self.fb_listbox.curselection()
            if sel:
                fb = g.FunctionBlocks[sel[0]]
        if not fb:
            return
        fb.Name = self.entries_fb["Name"].get().strip()
        fb.MapState = self.entries_fb["MapState"].get() == "true"
        fb.MapDiag = self.entries_fb["MapDiag"].get() == "true"
        fb.Comment = self.entries_fb["Comment"].get()
        self._refresh_fb_list()
        self._refresh_tree()

    def _update_group(self):
        g = self._current_group()
        if not g:
            return
        new_name = self.entries_group["Name"].get().strip()
        ok, msg = validate_c_identifier(new_name)
        if not ok:
            messagebox.showwarning("校验失败", f"组名称{msg}")
            return
        g.Name = new_name
        g.MapDiag = self.entries_group["MapDiag"].get() == "true"
        g.MapState = self.entries_group["MapState"].get() == "true"
        g.Comment = self.entries_group["Comment"].get()
        self._refresh_group_list()
        self._refresh_tree()
        self.log_message(f"更新组 {g.Id}")

    # ------------------------------------------------------------------
    # FB 管理
    # ------------------------------------------------------------------
    def _current_group(self) -> Optional[TwinSAFEGroup]:
        # 优先使用存储的 current_group（避免按钮点击导致 selection 丢失）
        if self.current_group:
            return self.current_group
        sel = self.group_listbox.curselection()
        if not sel:
            return None
        return self.project.ApplicationConfiguration.TwinSAFEGroups[sel[0]]

    def _refresh_fb_list(self):
        self.fb_listbox.delete(0, tk.END)
        g = self._current_group()
        if not g:
            # 没有组时清空引脚配置
            self._clear_pin_tree()
            return
        for fb in g.FunctionBlocks:
            self.fb_listbox.insert(tk.END, fb.Name)  # 只显示名称
        # 如果没有 FB，清空引脚配置
        if not g.FunctionBlocks:
            self._clear_pin_tree()

    def _add_fb(self):
        g = self._current_group()
        if not g:
            messagebox.showwarning("提示", "请先选择一个 TwinSAFE 组")
            return
        fb_type = self.fb_type_var.get()
        if not fb_type:
            messagebox.showwarning("提示", "请先选择 FB 类型")
            return
        type_num = self.lib.get_fb_type_number(fb_type)
        idx = len(g.FunctionBlocks) + 1
        
        # 生成同类型唯一名称：fbMuting1, fbMuting2, ...
        existing_names = {fb.Name for fb in g.FunctionBlocks if fb.Name}
        prefix = f"fb{fb_type[2:]}"  # FB 前缀小写显示
        n = 1
        while f"{prefix}{n}" in existing_names:
            n += 1
        fb_name = f"{prefix}{n}"
        
        # PDF 7.2: FB ID 格式 {group}_n{network}_f{N}
        fb = FunctionBlock(
            Id=f"{g.Id}_n1_f{idx}",
            OrderId=idx,
            Name=fb_name,
            Type=type_num
        )
        # PDF 7.2: Inport ID 格式 {fb_id}_i{N}, Outport ID 格式 {fb_id}_o{N}
        for i, (name, info) in enumerate(self.lib.get_inports(fb_type).items(), 1):
            fb.Inports.append(Port(Id=f"{fb.Id}_i{i}", PortId=info["hex"], Alias=name, Active=False))  # 默认未启用
        for i, (name, info) in enumerate(self.lib.get_outports(fb_type).items(), 1):
            fb.Outports.append(Port(Id=f"{fb.Id}_o{i}", PortId=info["hex"], Alias=name, Active=False))  # 默认未启用
        g.FunctionBlocks.append(fb)
        self._refresh_fb_list()
        self._refresh_tree()
        # 自动选中新添加的 FB 并刷新引脚
        self.fb_listbox.selection_clear(0, tk.END)
        self.fb_listbox.selection_set(len(g.FunctionBlocks) - 1)
        self.current_fb = fb  # 存储当前选中的 FB
        self._fill_fb_entries(fb)
        self._refresh_pin_tree(fb)  # 直接传递 fb
        self.log_message(f"添加 FB {fb.Id} 到组 {g.Id}")

    def _delete_fb(self):
        g = self._current_group()
        if not g:
            return
        # 使用 current_fb 来确定要删除的 FB
        if not self.current_fb:
            messagebox.showwarning("提示", "请先选择一个功能块")
            return
        try:
            idx = g.FunctionBlocks.index(self.current_fb)
            fb = g.FunctionBlocks.pop(idx)
            self.current_fb = None
            self._refresh_fb_list()
            self._refresh_tree()
            # 清空引脚控件
            for widget in self.pin_scroll_frame.winfo_children():
                widget.destroy()
            self.pin_widgets.clear()
            self.log_message(f"删除 FB {fb.Id}")
        except ValueError:
            messagebox.showwarning("提示", "未找到选中的功能块")

    def _on_fb_select(self, event):
        g = self._current_group()
        if not g:
            return
        sel = self.fb_listbox.curselection()
        if not sel:
            return
        fb = g.FunctionBlocks[sel[0]]
        self.current_fb = fb  # 存储当前选中的 FB
        self._fill_fb_entries(fb)
        self._refresh_pin_tree()

    def _select_fb_by_id(self, gid: str, fbid: str):
        self._select_group_by_id(gid)
        g = self._current_group()
        if not g:
            return
        for i, fb in enumerate(g.FunctionBlocks):
            if fb.Id == fbid:
                self.fb_listbox.selection_clear(0, tk.END)
                self.fb_listbox.selection_set(i)
                self.fb_listbox.see(i)
                self._fill_fb_entries(fb)
                self.notebook.select(self.notebook.tabs()[2])
                break

    def _fill_fb_entries(self, fb: FunctionBlock):
        self._set_entry(self.entries_fb["Name"], fb.Name)
        self._set_entry(self.entries_fb["MapState"], "true" if fb.MapState else "false")
        self._set_entry(self.entries_fb["MapDiag"], "true" if fb.MapDiag else "false")
        self._set_entry(self.entries_fb["Comment"], fb.Comment)

    def _update_fb(self):
        g = self._current_group()
        if not g:
            return
        fb = self.current_fb
        if not fb:
            sel = self.fb_listbox.curselection()
            if sel:
                fb = g.FunctionBlocks[sel[0]]
        if not fb:
            return
        new_name = self.entries_fb["Name"].get().strip()
        ok, msg = validate_c_identifier(new_name)
        if not ok:
            messagebox.showwarning("校验失败", f"功能块名称{msg}")
            return
        fb.Name = new_name
        fb.MapState = self.entries_fb["MapState"].get() == "true"
        fb.MapDiag = self.entries_fb["MapDiag"].get() == "true"
        fb.Comment = self.entries_fb["Comment"].get()
        self._refresh_fb_list()
        self._refresh_tree()
        self.log_message(f"更新 FB {fb.Id}")

    # ------------------------------------------------------------------
    # 别名设备管理
    # ------------------------------------------------------------------
    # SubType -> 设备型号缩写 映射
    _SUBTYPE_MODEL_MAP = {
        190: "EL1904",
        290: "EL2904",
        17827710: "EL1918",
        526206: "EP1918",
        526245: "EP1957",
        527206: "EP2918",
    }

    def _get_device_model(self, dev):
        """获取设备型号缩写"""
        if isinstance(dev, SafetyAliasDevice):
            # 安全PLC设备（ConnectionType=Local, SafeAddress=0）显示 Local
            if hasattr(dev, 'ConnectionType') and dev.ConnectionType == "Local" and hasattr(dev, 'SafeAddress') and dev.SafeAddress == 0:
                return "Local"
            return self._SUBTYPE_MODEL_MAP.get(getattr(dev, 'SubType', 0), "未知")
        return "-"

    def _refresh_alias_tree(self):
        for item in self.alias_tree.get_children():
            self.alias_tree.delete(item)
        # 只显示当前组的别名设备
        g = self._current_group()
        if not g:
            return
        
        # 排序：StandardAliasDevice (ErrorAcknowledgement/Run) 在前，安全PLC设备（Local）紧跟 Run，其余在后
        std_devices = []
        plc_devices = []
        other_devices = []
        for dev in g.AliasDevices:
            if isinstance(dev, StandardAliasDevice):
                std_devices.append(dev)
            elif (isinstance(dev, SafetyAliasDevice)
                  and hasattr(dev, 'ConnectionType') and dev.ConnectionType == "Local"
                  and hasattr(dev, 'SafeAddress') and dev.SafeAddress == 0):
                plc_devices.append(dev)
            else:
                other_devices.append(dev)
        
        # 按顺序显示：标准设备 → 安全PLC设备 → 其他设备
        for dev in std_devices + plc_devices + other_devices:
            model = self._get_device_model(dev)
            if isinstance(dev, SafetyAliasDevice):
                # 安全PLC设备 SafeAddress 显示为 "-"（仅显示，不影响 XML 生成）
                is_plc = (hasattr(dev, 'ConnectionType') and dev.ConnectionType == "Local"
                          and hasattr(dev, 'SafeAddress') and dev.SafeAddress == 0)
                safe_addr_display = "-" if is_plc else dev.SafeAddress
                watchdog_display = "-" if is_plc else dev.Watchdog
                self.alias_tree.insert("", tk.END, values=(
                    dev.AliasName, model, safe_addr_display, watchdog_display
                ))
            else:
                self.alias_tree.insert("", tk.END, values=(
                    dev.AliasName, model, "-", "-"
                ))

    def _get_next_device_id(self) -> str:
        """自动生成下一个设备 ID (PDF 7.2: g{group}_a{N})"""
        g = self._current_group()
        if not g:
            return "g1_a1"
        # 统计当前组的设备数量
        existing_ids = set()
        for dev in g.AliasDevices:
            existing_ids.add(dev.Id)
        # 生成下一个可用 ID
        n = 1
        while True:
            dev_id = f"{g.Id}_a{n}"
            if dev_id not in existing_ids:
                return dev_id
            n += 1

    def _get_next_connection_id(self) -> int:
        """自动生成下一个 ConnectionId（全局唯一，自动递增）"""
        # 获取所有组所有设备的 ConnectionId（全局唯一）
        existing_conn_ids = set()
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            for dev in g.AliasDevices:
                if hasattr(dev, 'ConnectionId') and dev.ConnectionId:
                    existing_conn_ids.add(dev.ConnectionId)
        # 生成下一个可用 ConnectionId
        n = 1
        while n in existing_conn_ids:
            n += 1
        return n

    def _get_next_safe_address(self) -> int:
        """自动生成下一个 SafeAddress（全局唯一，包含安全PLC，自动递增）"""
        existing_safe_addrs = set()
        
        # 包含安全PLC的 SafeAddress
        if self.project.TargetSystemConfiguration and self.project.TargetSystemConfiguration.SafeAddress:
            existing_safe_addrs.add(self.project.TargetSystemConfiguration.SafeAddress)
        
        # 包含所有组所有别名设备的 SafeAddress
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            for dev in g.AliasDevices:
                if hasattr(dev, 'SafeAddress') and dev.SafeAddress:
                    existing_safe_addrs.add(dev.SafeAddress)
        
        # 生成下一个可用 SafeAddress
        n = 1
        while n in existing_safe_addrs:
            n += 1
        return n

    def _add_safety_alias(self):
        g = self._current_group()
        if not g:
            messagebox.showwarning("提示", "请先选择一个 TwinSAFE 组")
            return
        next_id = self._get_next_device_id()
        next_conn_id = self._get_next_connection_id()
        next_safe_addr = self._get_next_safe_address()
        
        # 获取当前安全PLC类型
        safety_plc_type = ""
        if "SubType" in self.entries_target:
            safety_plc_type = self.entries_target["SubType"].get()
        
        # 收集组内已有的别名名称
        existing_names = set()
        for dev in g.AliasDevices:
            if hasattr(dev, 'AliasName') and dev.AliasName:
                existing_names.add(dev.AliasName)
        
        dlg = AliasDeviceDialog(self.root, next_device_id=next_id, next_connection_id=next_conn_id, next_safe_address=next_safe_addr, safety_plc_type=safety_plc_type, existing_alias_names=existing_names)
        self.root.wait_window(dlg)
        if dlg.result:
            # 统一处理为列表
            devices = dlg.result if isinstance(dlg.result, list) else [dlg.result]
            
            added_count = 0
            for dev in devices:
                # 验证 AliasName 在同一组内唯一
                if not self._check_alias_name_unique(g, dev.AliasName):
                    messagebox.showwarning("提示", f"别名 '{dev.AliasName}' 在当前组内已存在，跳过该设备")
                    continue
                
                # EL1918/EP系列作为普通别名设备时，设置 ConnectionType 为 FSoEMaster
                if hasattr(dev, 'SubType') and dev.SubType in (17827710, 526206, 526245, 527206):
                    if dev.SafeAddress != 0 or dev.ConnectionType != "Local":
                        dev.ConnectionType = "FSoEMaster"
                        if dev.SafeAddress == 0:
                            dev.SafeAddress = self._get_next_safe_address()
                
                g.AliasDevices.append(dev)
                self.log_message(f"添加安全别名设备 {dev.Id} ({dev.AliasName})")
                added_count += 1
            
            if added_count > 0:
                self._refresh_alias_tree()
                self._refresh_tree()
                self._refresh_pin_tree()
                self.log_message(f"共添加 {added_count} 个安全别名设备")

    def _check_alias_name_unique(self, group, alias_name, exclude_dev=None):
        """检查 AliasName 在同一组内是否唯一
        
        Args:
            group: TwinSAFEGroup 对象
            alias_name: 要检查的别名名称
            exclude_dev: 排除的设备（编辑时排除自身）
        
        Returns:
            bool: True 表示唯一，False 表示重复
        """
        for dev in group.AliasDevices:
            if dev != exclude_dev and dev.AliasName == alias_name:
                return False
        return True

    def _collect_all_safe_addresses(self, exclude_dev=None):
        """收集项目中所有已使用的 SafeAddress
        
        Args:
            exclude_dev: 排除的设备（编辑时排除自身）
        
        Returns:
            set: 所有已使用的 SafeAddress 集合
        """
        addrs = set()
        # 安全PLC的 SafeAddress
        if self.project.TargetSystemConfiguration and self.project.TargetSystemConfiguration.SafeAddress:
            addrs.add(self.project.TargetSystemConfiguration.SafeAddress)
        # 所有组所有设备的 SafeAddress
        for grp in self.project.ApplicationConfiguration.TwinSAFEGroups:
            for d in grp.AliasDevices:
                if d != exclude_dev and hasattr(d, 'SafeAddress') and d.SafeAddress is not None:
                    addrs.add(d.SafeAddress)
        return addrs

    # EL1918/EP 系列安全 PLC 设备的 SubType 集合
    _SAFETY_PLC_SUBTYPES = {17827710, 526206, 526245, 527206}

    def _is_protected_device(self, dev, operation="delete"):
        """检查设备是否为受保护设备
        
        受保护设备包括：
        1. 自动生成的 StandardAliasDevice（ErrorAcknowledgement 和 Run 信号）：不允许编辑/删除
        2. 自动添加的安全PLC别名设备：不允许删除，编辑时仅允许修改 AliasName
        
        Args:
            dev: 设备对象
            operation: "edit" 或 "delete"
        
        Returns:
            (bool, str): (是否受保护, 保护原因)
        """
        # StandardAliasDevice (ErrorAcknowledgement / Run) 不允许编辑和删除
        if isinstance(dev, StandardAliasDevice):
            return True, f"'{dev.AliasName}' 是系统自动生成的信号，不允许编辑或删除"
        
        # 安全PLC自动添加的别名设备：不允许删除
        if isinstance(dev, SafetyAliasDevice):
            if (hasattr(dev, 'SubType') and dev.SubType in self._SAFETY_PLC_SUBTYPES
                    and dev.ConnectionType == "Local" and dev.SafeAddress == 0):
                if operation == "delete":
                    return True, f"'{dev.AliasName}' 是安全PLC设备，不允许删除"
                # edit 操作：不阻止，但只允许修改 AliasName
        
        return False, ""

    def _edit_alias(self):
        sel = self.alias_tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请先选择一个设备")
            return
        idx = self.alias_tree.index(sel[0])
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            for dev in g.AliasDevices:
                if idx == 0:
                    # 检查是否为受保护设备
                    protected, reason = self._is_protected_device(dev, operation="edit")
                    if protected:
                        messagebox.showwarning("提示", reason)
                        return
                    
                    if isinstance(dev, SafetyAliasDevice):
                        # 收集组内已有的别名名称（排除自身）
                        existing_names = set()
                        for d in g.AliasDevices:
                            if d != dev and hasattr(d, 'AliasName') and d.AliasName:
                                existing_names.add(d.AliasName)
                        # 收集全局已用的 SafeAddress（排除自身）
                        existing_addrs = self._collect_all_safe_addresses(exclude_dev=dev)
                        # 判断是否为安全PLC设备（仅允许修改 AliasName）
                        is_safety_plc = (hasattr(dev, 'ConnectionType') and dev.ConnectionType == "Local"
                                         and hasattr(dev, 'SafeAddress') and dev.SafeAddress == 0)
                        dlg = AliasDeviceDialog(self.root, dev, existing_alias_names=existing_names,
                                                existing_safe_addresses=existing_addrs, is_safety_plc=is_safety_plc)
                        self.root.wait_window(dlg)
                        if dlg.result:
                            # 二次验证 AliasName 在同一组内唯一（排除自身）
                            if not self._check_alias_name_unique(g, dlg.result.AliasName, exclude_dev=dev):
                                messagebox.showwarning("提示", f"别名 '{dlg.result.AliasName}' 在当前组内已存在，请使用其他名称")
                                return
                            # 二次验证 SafeAddress 全局唯一（排除自身）
                            if dlg.result.SafeAddress in self._collect_all_safe_addresses(exclude_dev=dev):
                                messagebox.showwarning("提示", f"SafeAddress {dlg.result.SafeAddress} 已被其他设备使用，请使用其他地址")
                                return
                            self._refresh_alias_tree()
                            self._refresh_tree()
                            self._refresh_pin_tree()  # 刷新功能块引脚的通道列表
                            self.log_message(f"更新安全别名设备 {dlg.result.Id}")
                    else:
                        messagebox.showinfo("提示", "该设备不支持编辑")
                    return
                idx -= 1

    def _delete_alias(self):
        sel = self.alias_tree.selection()
        if not sel:
            return
        idx = self.alias_tree.index(sel[0])
        for g in self.project.ApplicationConfiguration.TwinSAFEGroups:
            for i, dev in enumerate(g.AliasDevices):
                if idx == 0:
                    # 检查是否为受保护设备
                    protected, reason = self._is_protected_device(dev, operation="delete")
                    if protected:
                        messagebox.showwarning("提示", reason)
                        return
                    
                    g.AliasDevices.pop(i)
                    self._refresh_alias_tree()
                    self._refresh_tree()
                    self._refresh_pin_tree()  # 刷新功能块引脚的通道列表
                    self.log_message(f"删除设备 {dev.Id}")
                    return
                idx -= 1

    # ------------------------------------------------------------------
    # 日志
    # ------------------------------------------------------------------
    def log_message(self, msg: str):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = TwinSAFEConfiguratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
