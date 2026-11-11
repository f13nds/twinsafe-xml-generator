# -*- coding: utf-8 -*-
"""TwinCAT Automation Interface 导入安全项目（独立子进程）
根据文档 6.13.1 和 9.2 章节:
- ITcSysManager 通过 project.Object 获取
- XML 导入通过 ConsumeXml 而非 CreateChild
"""
import sys, os, time

def log(msg):
    print(msg, flush=True)

def retry_call(fn, desc, retries=10, delay=3):
    for i in range(retries):
        try:
            result = fn()
            if result is not None:
                return result
            log(f"    {desc} 第{i+1}次: 返回 None")
        except Exception as e:
            log(f"    {desc} 第{i+1}次: {e}")
        time.sleep(delay)
    return None

def main():
    if len(sys.argv) < 3:
        log("ERROR: 参数不足")
        sys.exit(1)

    sln_path = sys.argv[1]
    xml_path = sys.argv[2]
    project_name = sys.argv[3] if len(sys.argv) > 3 else ""

    if not project_name:
        project_name = os.path.splitext(os.path.basename(xml_path))[0]

    log(f"解决方案: {sln_path}")
    log(f"安全项目: {xml_path}")
    log(f"项目名称: {project_name}")

    try:
        import pythoncom
        pythoncom.CoInitialize()
        import win32com.client

        log("连接 TcXaeShell...")
        tc = win32com.client.Dispatch("TcXaeShell.DTE.17.0")

        log("打开解决方案...")
        tc.Solution.Open(sln_path)

        # 等待就绪
        for i in range(30):
            try:
                if tc.Solution.IsOpen:
                    break
            except Exception:
                pass
            time.sleep(2)
        log("解决方案已打开")

        try:
            # 获取 ITcSysManager（通过 project.Object，文档 6.13.1）
            log("获取 SystemManager (project.Object)...")
            projects = tc.Solution.Projects
            proj = projects.Item(1)
            sm = proj.Object  # 这是 ITcSysManager
            log(f"  SystemManager: {type(sm).__name__}")

            # 验证 LookupTreeItem 可用
            log("验证 LookupTreeItem...")
            test_item = retry_call(lambda: sm.LookupTreeItem("TIPC"), "LookupTreeItem(TIPC)", retries=5, delay=2)
            if test_item is not None:
                log(f"  TIPC: OK")
            else:
                log("  TIPC: 失败")

            # 查找 TISC
            log("查找 TISC...")
            safety = retry_call(lambda: sm.LookupTreeItem("TISC"), "LookupTreeItem(TISC)", retries=10, delay=3)
            if safety is None:
                log("ERROR: 未找到 TISC 节点")
                return
            log("TISC 节点找到")

            # 读取 XML 文件内容
            log("读取 XML 文件...")
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
            log(f"  XML 大小: {len(xml_content)} 字符")

            # 导入安全项目（文档 6.13.1: CreateChild 接受 .splcproj/.tfzip/XML）
            log(f"导入安全项目 '{project_name}'...")
            new_project = retry_call(
                lambda: safety.CreateChild(project_name, 0, "", xml_path),
                "CreateChild", retries=5, delay=3
            )
            if new_project is not None:
                log(f"SUCCESS: 安全项目导入成功: {project_name}")
            else:
                log("ERROR: CreateChild 返回 None")

        finally:
            log("保存并关闭解决方案...")
            try:
                tc.Solution.Close(True)
            except Exception as e:
                log(f"关闭时忽略: {e}")

    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
