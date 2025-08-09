# PDF标准文档分类系统 - 生产环境

## 🏗️ 部署完成

系统已成功部署到生产环境，包含以下组件：

### 📁 目录结构
```
pdf-classifier/
├── input_pdfs/          # 放置待处理的PDF文件
├── jc/                 # 匹配成功的PDF文件输出
├── logs/               # 系统日志
├── templates/          # 模板文件
├── backup/             # 备份文件
├── reports/            # 处理报告
├── main.py             # 主程序
├── pdf_processor.py    # 核心处理器
└── deployment_config.json  # 部署配置
```

### 🚀 快速使用

#### 方法1：批处理脚本（推荐）
- Windows: 双击 `run_classification.bat`
- Linux/macOS: 运行 `./run_classification.sh`

#### 方法2：命令行
```bash
# 处理input_pdfs目录的文件
python main.py input_pdfs

# 查看帮助
python main.py --help
```

#### 方法3：自动监控
```bash
# 启动监控服务（自动处理新文件）
python monitor.py
```

### 📋 使用流程

1. **放置文件**：将PDF文件复制到 `input_pdfs/` 目录
2. **运行处理**：执行批处理脚本或命令行
3. **查看结果**：检查 `jc/` 目录中的匹配文件
4. **查看日志**：检查 `pdf_classify.log` 了解处理详情

### 📊 系统监控

- **处理日志**：`pdf_classify.log`
- **处理报告**：`reports/` 目录
- **系统配置**：`deployment_config.json`

### 🔧 配置调整

编辑 `deployment_config.json` 修改系统参数：
- 超时时间
- 验证阈值  
- OCR配置
- 目录路径

### 📞 技术支持

- 查看详细文档：`USAGE_GUIDE.md`
- 运行诊断：`python demo.py`
- 测试功能：`python test_features.py`

---
部署时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统版本：2.0.0
