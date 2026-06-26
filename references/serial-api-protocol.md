# ScanPen 串口 API 验证协议

## 默认设备

默认配置来自 `assets/configs/default_scanInfo.json`：

- AP 日志/命令串口：`cskApLog`，默认 `COM6`，`921600`。
- CP 耗时日志串口：`cskCpLog`，默认 `COM3`，`921600`。

如现场端口变化，优先通过 `--ap COMx --cp COMy --baud 921600` 覆盖；不要直接改动历史结果。

## 核心命令

- 心跳/版本：`version`
  - 成功依据：AP 日志匹配 `hearCmdRes`，出现 `fw_version: ...`；最好同时匹配 `Return: 0`。
- 翻译：`trans_start <language> "<text>"`
  - `language=1` 通常用于中文输入，`language=2` 通常用于英文输入。
  - 成功依据：AP 日志匹配 `transRes`，出现 `lis_trans_get_result:...`。
  - 耗时依据：CP 日志匹配 `transInit`、`transCost`、`transTotal`。
- TTS：先发 `xtts_stop`，再发 `xtts_start <role> <vol> <speed> "<text>"`
  - 成功依据：AP 日志匹配 `ttsEnd`，出现 `[tts] stop...`。
  - 耗时依据：CP 日志匹配 `ttsInit`、`ttsCost`、可选 `ttsSpeed`。

## 推荐判定标准

一次基础验证通过需同时满足：

1. AP 与 CP 串口均能打开。
2. `version` 能返回 `fw_version` 和 `Return: 0`。
3. 翻译命令能返回 `transRes`，并至少采集到 CP 侧 `transCost`。
4. TTS 命令能返回 `ttsEnd`，并至少采集到 CP 侧 `ttsCost`。

压测通过标准可按项目要求调整，常用口径是：所有迭代无超时、无 dump/backtrace、串口不中断，且关键耗时指标在可接受区间内。

## 常见异常排查

- 串口打开失败：先运行 `--mode list-ports`，确认 AP/CP 端口号是否变化，或是否被其他串口工具占用。
- 版本有返回但翻译/TTS 超时：检查固件版本、资源版本、正则是否仍匹配最新日志格式。
- 只有 AP 有日志、CP 无耗时：检查 CP 串口号、CP 日志开关和波特率。
- 中文显示为乱码：在 Windows 批处理中已执行 `chcp 65001`；仍异常时用 PowerShell 直接运行 Python 命令并确认文件为 UTF-8。
- 原始脚本不能运行：使用 `scripts/legacy_scanpenApiTest_fixed.py` 或优先使用 `scripts/scanpen_api_runner.py`。
