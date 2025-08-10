# I盘PDF文件处理工具

## 📁 文件结构

本目录包含专门用于处理I盘PDF文件的工具集合：

```
tests/i_drive_processing/
├── process_i_drive_pdfs.py      # 主要的PDF处理脚本
├── test_i_drive_script.py      # 环境测试脚本
├── run_i_drive_processing.bat  # Windows批处理文件
├── run_i_drive_processing.ps1  # PowerShell脚本
├── I_DRIVE_PROCESSING_README.md # 详细功能说明
├── 快速开始.md                  # 快速开始指南
└── README.md                   # 本文件
```

## 🚀 使用方法

### 方法1：使用批处理文件（推荐Windows用户）
1. 双击 `run_i_drive_processing.bat`
2. 脚本会自动检查环境并开始处理

### 方法2：使用PowerShell脚本
1. 右键 `run_i_drive_processing.ps1`
2. 选择"使用PowerShell运行"

### 方法3：直接运行Python脚本
```bash
# 从项目根目录运行
python tests/i_drive_processing/process_i_drive_pdfs.py
```

### 方法4：先测试环境
```bash
# 从项目根目录运行
python tests/i_drive_processing/test_i_drive_script.py
```

## ⚠️ 重要说明

- **路径已修复**：所有脚本现在都可以从 `tests/i_drive_processing/` 目录正常运行
- **自动路径调整**：脚本会自动切换到项目根目录，确保所有相对路径正确
- **依赖检查**：批处理和PowerShell脚本会自动检查并安装必要的依赖包

## 📊 功能特性

- ✅ 递归扫描 `I:\1T硬盘D` 下的所有PDF文件
- ✅ 只处理PDF首页（提高效率）
- ✅ 使用第一特征（白色背景+黑色文字）验证
- ✅ 使用第二特征（两条长黑横线）验证
- ✅ 符合条件的PDF自动复制到 `jc` 文件夹
- ✅ 详细日志保存到 `tests/logs` 目录
- ✅ 完整的处理统计和报告

## 🔧 环境要求

- Python 3.7+
- 必要的Python包（见项目根目录的 `requirements.txt`）
- 访问 `I:\1T硬盘D` 的权限
- Windows系统（批处理和PowerShell脚本）

## 📝 日志文件

处理完成后，日志文件将保存在：
```
tests/logs/i_drive_processing_YYYYMMDD_HHMMSS.log
```

## 🆘 故障排除

如果遇到问题：
1. 先运行 `test_i_drive_script.py` 检查环境
2. 确保I盘已连接且可访问
3. 检查Python环境和依赖包
4. 查看日志文件了解详细错误信息

## 📞 技术支持

如有问题，请查看：
- `I_DRIVE_PROCESSING_README.md` - 详细功能说明
- `快速开始.md` - 快速开始指南
- 项目根目录的 `README.md` - 项目总体说明
