# 📅 Daka Tracker - 个人打卡、收益与牙套提醒工具

Daka Tracker 是一个轻量级 Python 命令行工具，用于记录每日打卡、追踪当月收益，并在查看状态时提醒隐形牙套的更换进度。

## ✨ 主要功能

- **打卡与收益追踪**：按单价、每日上限和每月封顶自动计算已获收益。
- **当日进度**：状态页会显示今日已打卡次数与每日上限。
- **动态预测**：根据当前进度估算本月最高可获收益；无法达到封顶时会显示损失警告。
- **考勤补位分析**：计算达到封顶前还能缺勤多少次，以及需要多少次周末补卡；机会不足时会直接提示无法达成及预计损失。
- **缺勤统计**：自动列出当月漏打卡的工作日。
- **自动月结**：新月份第一次运行时，自动归档上月收益。
- **隐形牙套提醒**：按配置计算当前牙套副数和距下次更换的天数，更换当天会高亮提醒。

## 🚀 快速开始

### 1. 准备环境

确保已安装 Python 3。本项目不需要额外的第三方依赖。

### 2. 使用命令

| 命令 | 说明 |
| --- | --- |
| `python3 daka/daka.py` | 正式打卡：增加一次有效打卡并显示当前状态 |
| `python3 daka/daka.py s` | 查看当前进度、预测、缺勤与牙套提醒 |
| `python3 daka/daka.py 9:30` | 记录一个可疑时间点，不计入有效打卡和收益 |
| `python3 daka/daka.py h` | 查看往月收益记录 |

## 🔥 配置快捷别名

为了更方便地打卡，可以将脚本配置为 `dk` 命令。

### Linux / macOS（zsh 或 bash）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias dk='python3 /path/to/project/daka/daka.py'
```

保存后执行 `source ~/.zshrc` 或 `source ~/.bashrc`，之后即可使用 `dk`、`dk s` 和 `dk h`。

### Windows（PowerShell）

在 PowerShell 配置文件中添加：

```powershell
function dk {
    python "C:\path\to\project\daka\daka.py" $args
}
```

重启 PowerShell 后即可使用。

## ⚙️ 打卡配置

可在 `daka/daka.py` 顶部调整：

- `CAP`：每月收益上限，默认为 `1000`。
- `PRICE`：单次有效打卡收益，默认为 `20`。
- `MAX_DAILY`：每日有效打卡上限，默认为 `2`。

## 🦷 牙套提醒配置

牙套计划位于 `daka/aligner_config.json`：

```json
{
  "start_date": "2026-08-27",
  "start_tray": 51,
  "end_tray": null,
  "default_days": 7,
  "special_days": {}
}
```

- `start_date`：`start_tray` 开始佩戴的日期，格式为 `YYYY-MM-DD`。
- `start_tray`：计划起始的牙套副数。
- `end_tray`：最后一副牙套；不限定结束副数时设为 `null`。
- `default_days`：每副默认佩戴天数。
- `special_days`：按副数覆盖佩戴天数，例如 `{"53": 10}` 表示第 53 副佩戴 10 天。

如果不需要牙套提醒，将 `daka/daka.py` 中的 `ALIGNER_REMINDER_ENABLED` 设为 `False`。

## 📂 数据存储

打卡数据保存在 `daka/daka_status.json` 中。脚本会自动创建和更新该文件，也可根据实际需要手动修改；修改前建议先备份。
