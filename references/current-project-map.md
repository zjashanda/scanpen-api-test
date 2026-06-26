# 当前项目文件映射

本文件记录从 `X:\bsTestFolder\apiTest` 整理进 skill 的材料，供需要追溯原始工程时读取。

## 已整理到 skill 的文件

- `assets/configs/default_scanInfo.json`：来自 `scanInfo.json`，包含 scanPen 项目、AP/CP 串口号、波特率和日志正则。
- `assets/corpus/zhxs.txt`：来自 `zhxs.txt`，中文压测语料。
- `assets/corpus/xwz.txt`：来自 `xwz.txt`，英文压测语料。
- `assets/webpages/test1.html`：来自 `webpages/test1.html`，网页样例素材。
- `assets/legacy/scanpenApiTest_original.py`：原始压测脚本快照，保持原样备份。
- `scripts/legacy_scanpenApiTest_fixed.py`：基于原始脚本修复第 1081 行缩进后的可编译版本，保留原始测试流程。
- `scripts/scanpen_api_runner.py`：新整理的参数化验证/压测入口，推荐优先使用。
- `scripts/run_scanpen_api_test.bat`：Windows 批处理入口，适合现场快速修改参数执行。

## 原目录内容判断

- `scanInfo.json` 是当前硬件配置，已验证默认 AP=COM6、CP=COM3、baud=921600。
- `scanpenApiTest.py` 是历史串口 API 压测脚本；原文件存在缩进错误，不能直接运行。
- `result/` 下是历史结果目录，每轮通常包含：
  - `result.txt` 或 `result_*.txt`：翻译/TTS CSV 风格结果和耗时。
  - `output_log_*.log`：脚本运行日志。
  - `scanPen_cskApLog_*.log`：AP 侧串口日志。
  - `scanPen_cskCpLog_*.log`：CP 侧串口日志。

## 历史抽样结论

抽样查看过 2025-08-26 与 2025-08-27 的历史结果，日志中 AP/CP 串口能打开，`result.txt` 中记录了 `InfoType,txt,transRes,initTime,costTime,totalTime` 等字段，说明历史流程是通过 AP 串口下发命令、CP 串口采集耗时指标。
