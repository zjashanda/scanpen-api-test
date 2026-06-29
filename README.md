# scanpen-api-test

ScanPen 串口 API 验证和压测工作流。Use when Codex needs to validate ScanPen/scanpen devices over AP/CP serial ports, run version/translation/TTS checks, execute configurable pressure tests with scanInfo.json, analyze result logs, or reuse the bundled ScanPen API test scripts, configs, and corpus.

## Skill layout

- `agents/openai.yaml`
- `assets/configs/default_scanInfo.json`
- `assets/corpus/xwz.txt`
- `assets/corpus/zhxs.txt`
- `assets/legacy/scanpenApiTest_original.py`
- `assets/webpages/test1.html`
- `references/current-project-map.md`
- `references/serial-api-protocol.md`
- `scripts/legacy_scanpenApiTest_fixed.py`
- `scripts/run_scanpen_8_stress.bat`
- `scripts/run_scanpen_8_stress.ps1`
- `scripts/run_scanpen_api_test.bat`
- `scripts/scanpen_api_runner.py`
- `SKILL.md`

## Install the skill

Copy this folder into:

```text
~/.codex/skills/scanpen-api-test
```

Then restart Codex.

## Usage and workflow

## 概览

使用本 skill 处理 ScanPen 离线串口 API 验证与压测：读取 `scanInfo.json` 风格配置，打开 AP/CP 串口，下发 `version`、`trans_start`、`xtts_start` 命令，按配置中的正则判断接口是否可用，并保存结果、AP 日志、CP 日志。AP/CP 串口日志会边读取边流式写入结果目录，避免异常中断时完全丢失现场日志。

优先使用 `scripts/scanpen_api_runner.py` 和 `scripts/run_scanpen_api_test.bat`。只有在需要复现历史流程时，才使用 `scripts/legacy_scanpenApiTest_fixed.py`。

## 资源布局

- `scripts/scanpen_api_runner.py`：推荐入口，支持列串口、基础验证、循环压测、纯中文/纯英文/中英混合语料、按轮次随机语料类型、随机文本长度、串口日志流式落盘。
- `scripts/run_scanpen_api_test.bat`：Windows 便捷入口，顶部变量可直接修改端口、次数、文本、模式等参数。
- `scripts/legacy_scanpenApiTest_fixed.py`：原始脚本的缩进修复版，用于兼容历史压测流程。
- `assets/configs/default_scanInfo.json`：默认配置，AP=`COM6`，CP=`COM3`，baud=`921600`。
- `assets/corpus/zhxs.txt` / `assets/corpus/xwz.txt`：中英文压测语料。
- `assets/legacy/scanpenApiTest_original.py`：原始脚本备份，保留问题现场，不推荐直接运行。
- `references/current-project-map.md`：当前目录材料如何整理进 skill 的映射说明；需要追溯来源时读取。
- `references/serial-api-protocol.md`：命令、正则、判定标准和排障细节；遇到协议/日志疑问时读取。

## 运行前检查

1. 确认 Python 可用：`python --version`。
2. 确认依赖可用：`python -c "import serial; print(serial.__version__)"`。
3. 如缺少 pyserial，安装：`python -m pip install pyserial`。
4. 先列出串口，确认 AP/CP 端口没有变化：

```powershell
python C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\scanpen_api_runner.py --mode list-ports
```

## 基础验证流程

用于回答“接口还能不能用”。默认会验证版本、翻译、TTS，并在当前工作目录的 `result/` 下生成结果目录。

```powershell
python C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\scanpen_api_runner.py `
  --mode validate `
  --config C:\Users\Administrator\.codex\skills\scanpen-api-test\assets\configs\default_scanInfo.json `
  --ap COM6 `
  --cp COM3 `
  --baud 921600 `
  --text "你好" `
  --label scanpen-validate
```

通过标准：

- AP/CP 串口均成功打开。
- `version` 匹配到 `fw_version`，并尽量匹配 `Return: 0`。
- `trans_start` 匹配到 `transRes`，CP 侧可采集 `transInit/transCost/transTotal`。
- `xtts_start` 匹配到 `ttsEnd`，CP 侧可采集 `ttsInit/ttsCost/ttsSpeed` 中的可用项。

如只想验证心跳和 TTS，可加 `--no-trans`；如只想验证心跳和翻译，可加 `--no-tts`。

## 压测流程

用于连续执行翻译/TTS，适合稳定性、耗时和回归验证。

```powershell
python C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\scanpen_api_runner.py `
  --mode stress `
  --config C:\Users\Administrator\.codex\skills\scanpen-api-test\assets\configs\default_scanInfo.json `
  --ap COM6 `
  --cp COM3 `
  --baud 921600 `
  --count 100 `
  --ops trans,tts `
  --corpus-kind random `
  --text-bytes 40 `
  --interval 1 `
  --label trans_tts_40byte
```

如需每轮随机长度，使用历史常用范围 40~120 byte：

```powershell
python C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\scanpen_api_runner.py `
  --mode stress `
  --config C:\Users\Administrator\.codex\skills\scanpen-api-test\assets\configs\default_scanInfo.json `
  --ap COM6 `
  --cp COM3 `
  --baud 921600 `
  --count 100 `
  --ops trans,tts `
  --corpus-kind random `
  --random-text-bytes `
  --min-text-bytes 40 `
  --max-text-bytes 120 `
  --interval 1 `
  --label trans_tts_kind_random_40_120byte
```

常用参数：

- `--count`：循环次数。
- `--ops`：压测项目，可取 `trans`、`tts`、`version`，用逗号组合，例如 `trans,tts`。
- `--text`：固定输入文本；提供该参数时不从语料截取。
- `--corpus-kind chinese|english|mixed|random`：未提供固定文本时选择语料类型；`chinese` 表示单条纯中文，`english` 表示单条纯英文，`mixed` 表示单条中英混合，`random` 表示每轮从这三类中随机选择一种。
- `--text-bytes`：固定长度模式下从语料截取的 UTF-8 字节上限，模拟 40/120 byte 等历史压测口径。
- `--random-text-bytes`：压测时每轮随机文本长度；随机范围由 `--min-text-bytes` 和 `--max-text-bytes` 控制。
- `--min-text-bytes` / `--max-text-bytes`：随机长度范围，建议先使用历史口径 `40~120`。
- `--random-seed`：可选随机种子，用于复现同一组随机文本。
- `--language`：翻译语言参数，`0` 表示按语料类型自动选择，中文/混合用 `1`，英文用 `2`；也可手动指定 `1` 或 `2`。
- `--role --volume --speed`：TTS 参数。
- `--stop-on-fail`：仅遇到串口不可用、串口读写异常或设备疑似卡死等 fatal 问题时停止；普通接口超时/正则未匹配只记录到 `result.csv` 并继续压测。
- `--fatal-consecutive-failures`：与 `--stop-on-fail` 配合使用，连续 N 次接口失败且 AP 侧没有任何新日志活动时判定设备疑似卡死并停止该设备进程；默认 `3`，设为 `0` 可关闭该卡死阈值。
- `--dry-run`：只解析配置并打印将发送的命令，不打开串口。

## 批处理脚本

现场快速执行优先用批处理：

```cmd
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat validate
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat stress --count 200 --ops trans,tts --text-bytes 120
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat stress --count 200 --random-text-bytes --min-text-bytes 40 --max-text-bytes 120 --corpus-kind random
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat list-ports
```

8 台设备并行压测入口也随 skill 同步，仓库更新后可直接运行。默认结果目录为执行命令时当前目录下的 `result/`，不会写到 skill 目录：

```cmd
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_8_stress.bat 10 random 40 120 random
```

`run_scanpen_8_stress.bat` 会调用同目录下的 `run_scanpen_8_stress.ps1`，默认设备映射为 dev1 COM7/COM4、dev2 COM8/COM6、dev3 COM3/COM10、dev4 COM5/COM9、dev5 COM20/COM24、dev6 COM22/COM23、dev7 COM25/COM18、dev8 COM19/COM21。

修改 `scripts/run_scanpen_api_test.bat` 顶部变量即可适配不同需求：

- `MODE`：`list-ports`、`validate`、`stress`。
- `AP_PORT` / `CP_PORT` / `BAUD`：现场串口参数。
- `TEXT` / `LANGUAGE` / `ROLE` / `VOLUME` / `SPEED`：单次验证参数。
- `TEXT_B64`：UTF-8 base64 文本，用于避免 `.bat` 中文编码问题；`validate` 模式下若 `TEXT` 和 `TEXT_B64` 都为空，会自动使用“你好”；`stress` 模式下二者为空表示从语料生成文本。
- `COUNT` / `OPS` / `TEXT_BYTES` / `CORPUS_KIND` / `INTERVAL`：压测参数，`CORPUS_KIND` 可取 `chinese`、`english`、`mixed`、`random`。
- `RANDOM_TEXT_BYTES` / `MIN_TEXT_BYTES` / `MAX_TEXT_BYTES` / `RANDOM_SEED`：批处理内的随机长度参数；`RANDOM_TEXT_BYTES=1` 时启用每轮随机长度。
- `STOP_ON_FAIL` / `FATAL_CONSECUTIVE_FAILURES`：停止策略；`STOP_ON_FAIL=1` 时不会因为单次翻译/TTS 超时停止，只会在串口不可用或连续 N 次失败且 AP 无日志活动时停止该设备。
- `RESULT_BASE` / `LABEL`：结果输出位置和标签。
- `EXTRA_ARGS`：放额外 Python 参数，例如 `--dry-run` 或 `--stop-on-fail`。

## 结果文件

每次 `validate` 或 `stress` 会生成一个时间戳结果目录，通常包含：

- `result.csv`：结构化结果，包含操作类型、文本、成功状态、翻译结果、TTS 结束信息、CP 侧耗时、请求文本字节数、实际文本字节数、语料类型等。
- `summary.txt`：本次执行摘要。
- `scanPen_cskApLog_<PORT>.log`：AP 侧串口日志，运行过程中流式写入。
- `scanPen_cskCpLog_<PORT>.log`：CP 侧串口日志，运行过程中流式写入。

汇报结论时优先说明：串口是否打开、版本号、翻译是否返回、TTS 是否结束、关键耗时、结果目录路径。不要粘贴大段日志；只截取能证明结论的关键行。若压测被中断，优先查看已流式写入的 AP/CP 日志和已追加的 `result.csv`。

## 原始脚本兼容

历史原始脚本 `scanpenApiTest.py` 已保存在 `assets/legacy/scanpenApiTest_original.py`，原文件第 1081 行存在缩进错误。需要复现历史 `costTimeTest()` 流程时，用修复版：

```powershell
python C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\legacy_scanpenApiTest_fixed.py `
  -f C:\Users\Administrator\.codex\skills\scanpen-api-test\assets\configs\default_scanInfo.json `
  -n 20 `
  -b 120 `
  -l trans_tts_allType_120byte_cost
```

优先使用新 runner；只有当用户明确要求“按原脚本跑”或需要对比历史输出格式时才运行修复版。

## 排障顺序

1. 先运行 `--mode list-ports`，确认端口存在且未被占用。
2. 再运行 `--mode validate --dry-run`，确认配置和命令正确。
3. 再运行 `--mode validate`，看版本、翻译、TTS 三类结果。
4. 如果 AP 有结果但 CP 无耗时，优先检查 CP 端口和 CP 日志输出。
5. 如果正则匹配不到但日志里有类似信息，读取 `references/serial-api-protocol.md`，按最新日志格式更新配置正则。
6. 如果要分析历史目录结构或来源文件，读取 `references/current-project-map.md`。
