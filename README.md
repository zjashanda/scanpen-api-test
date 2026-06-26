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

使用本 skill 处理 ScanPen 离线串口 API 验证与压测：读取 `scanInfo.json` 风格配置，打开 AP/CP 串口，下发 `version`、`trans_start`、`xtts_start` 命令，按配置中的正则判断接口是否可用，并保存结果、AP 日志、CP 日志。

优先使用 `scripts/scanpen_api_runner.py` 和 `scripts/run_scanpen_api_test.bat`。只有在需要复现历史流程时，才使用 `scripts/legacy_scanpenApiTest_fixed.py`。

## 资源布局

- `scripts/scanpen_api_runner.py`：推荐入口，支持列串口、基础验证、循环压测、结果落盘。
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
  --corpus-kind chinese `
  --text-bytes 40 `
  --interval 1 `
  --label trans_tts_40byte
```

常用参数：

- `--count`：循环次数。
- `--ops`：压测项目，可取 `trans`、`tts`、`version`，用逗号组合，例如 `trans,tts`。
- `--text`：固定输入文本；提供该参数时不从语料截取。
- `--corpus-kind chinese|english`：未提供固定文本时使用中文或英文语料。
- `--text-bytes`：从语料截取的 UTF-8 字节上限，模拟 40/120 byte 等历史压测口径。
- `--language`：翻译语言参数，中文常用 `1`，英文常用 `2`。
- `--role --volume --speed`：TTS 参数。
- `--stop-on-fail`：遇到首个失败立即停止。
- `--dry-run`：只解析配置并打印将发送的命令，不打开串口。

## 批处理脚本

现场快速执行优先用批处理：

```cmd
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat validate
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat stress --count 200 --ops trans,tts --text-bytes 120
C:\Users\Administrator\.codex\skills\scanpen-api-test\scripts\run_scanpen_api_test.bat list-ports
```

修改 `scripts/run_scanpen_api_test.bat` 顶部变量即可适配不同需求：

- `MODE`：`list-ports`、`validate`、`stress`。
- `AP_PORT` / `CP_PORT` / `BAUD`：现场串口参数。
- `TEXT` / `LANGUAGE` / `ROLE` / `VOLUME` / `SPEED`：单次验证参数。
- `TEXT_B64`：UTF-8 base64 文本，默认是“你好”，用于避免 `.bat` 中文编码问题；若要用明文 ASCII，可清空 `TEXT_B64` 后修改 `TEXT`。
- `COUNT` / `OPS` / `TEXT_BYTES` / `CORPUS_KIND` / `INTERVAL`：压测参数。
- `RESULT_BASE` / `LABEL`：结果输出位置和标签。
- `EXTRA_ARGS`：放额外 Python 参数，例如 `--dry-run` 或 `--stop-on-fail`。

## 结果文件

每次 `validate` 或 `stress` 会生成一个时间戳结果目录，通常包含：

- `result.csv`：结构化结果，包含操作类型、文本、成功状态、翻译结果、TTS 结束信息、CP 侧耗时等。
- `summary.txt`：本次执行摘要。
- `scanPen_cskApLog_<PORT>.log`：AP 侧串口日志。
- `scanPen_cskCpLog_<PORT>.log`：CP 侧串口日志。

汇报结论时优先说明：串口是否打开、版本号、翻译是否返回、TTS 是否结束、关键耗时、结果目录路径。不要粘贴大段日志；只截取能证明结论的关键行。

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
