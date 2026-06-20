# HFSS Design Optimizer

`hfss-design-optimizer` is a Codex skill for AI-assisted HFSS design workflows. It helps Codex generate MATLAB scripts that use the bundled HFSS-MATLAB-API to create AEDT projects, run HFSS scripts, export simulation results, optimize design parameters, reproduce RF/microwave structures from papers, and learn reusable design methods from paper plus simulation-file bundles.

This skill is designed around a local MATLAB-to-HFSS scripting flow:

```text
Codex design request
  -> MATLAB driver script
  -> HFSS VBScript (.vbs)
  -> Ansys Electronics Desktop project (.aedt)
  -> exported CSV / Touchstone / MATLAB result data
  -> optimization or literature comparison
```

## Features

- Generate HFSS models from natural-language RF, microwave, and antenna requirements.
- Use the bundled `assets/hfss-api-master` MATLAB API package for geometry, boundaries, ports, analysis setup, and result export.
- Create reusable MATLAB scripts and HFSS VBScript files.
- Support common antenna workflows such as dipoles, microstrip patches, arrays, horns, and literature reproduction models.
- Guide parameter sweeps and optimization loops for S-parameters, resonance frequency, bandwidth, gain, and paper-curve fitting.
- Parse exported HFSS CSV reports for quick result summaries.
- Validate generated MATLAB scripts before running HFSS.
- Analyze paper plus simulation-file bundles and summarize innovation points, model gaps, and reusable skill-improvement candidates.

## Repository Layout

```text
hfss-design-optimizer/
  SKILL.md
  README.md
  agents/
    openai.yaml
  assets/
    hfss-api-master/
    templates/
      basic_hfss_project.m
      patch_antenna_project.m
      parametric_sweep_project.m
      literature_reproduction_project.m
  references/
    api-map.md
    common-hfss-patterns.md
    design-workflow.md
    hfss-batch-troubleshooting.md
    fast-approximation.md
    literature-replication.md
    local-config.md
    optimization-workflow.md
    research-bundle-learning.md
  scripts/
    collect_api_signatures.ps1
    analyze_research_bundle.py
    parse_hfss_csv.py
    summarize_hfss_log.py
    validate_matlab_hfss_script.py
```

## Requirements

- Windows
- Codex with local skills support
- MATLAB
- Ansys Electronics Desktop / HFSS
- Bundled HFSS-MATLAB-API package at `assets/hfss-api-master`
- Python 3 for helper scripts
- PowerShell for API signature collection

Important for GitHub users: the bundled MATLAB API is portable, but the HFSS executable path is machine-specific. Every user must verify or edit the local `ansysedt.exe` path before running HFSS scripts.

The current default local paths are:

```text
HFSS executable:
F:\AnsysEM\v221\Win64\ansysedt.exe

HFSS-MATLAB-API root:
F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master
```

If your paths differ, update:

- `SKILL.md`
- `references/local-config.md`
- MATLAB templates under `assets/templates/`

For this workstation the default HFSS launcher is `F:\AnsysEM\v221\Win64\ansysedt.exe`. If HFSS is installed somewhere else, update `hfssExePath` in the generated MATLAB script, `references/local-config.md`, and any template you plan to reuse.

## Deployment Plan

### 1. Prepare The API Package

The HFSS-MATLAB-API package is bundled in the skill at:

```text
F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master
```

Confirm that it contains folders such as:

```text
3dmodeler/
analysis/
boundary/
general/
mesh/
radiation/
reporter/
```

### 2. Confirm HFSS Path

Confirm that the HFSS executable exists:

```text
F:\AnsysEM\v221\Win64\ansysedt.exe
```

In MATLAB scripts, this path is used as:

```matlab
hfssExePath = 'F:\AnsysEM\v221\Win64\ansysedt.exe';
```

If HFSS is installed somewhere else, change `hfssExePath` before launching a solve. Common Ansys installations use different version folders and may live under `C:\Program Files\AnsysEM\...\Win64\ansysedt.exe`; do not assume the repository default works after cloning from GitHub.

### 3. Install As A Codex Skill

Copy this folder into the local Codex skills directory:

```powershell
$skillsDir = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force $skillsDir
Copy-Item -Recurse -Force .\hfss-design-optimizer $skillsDir
```

After copying, the skill should exist at:

```text
C:\Users\<UserName>\.codex\skills\hfss-design-optimizer
```

Restart or open a new Codex session so the skill metadata can be discovered.

### 4. Validate The Skill

If you have the Codex skill validation script available, run:

```powershell
python C:\Users\<UserName>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<UserName>\.codex\skills\hfss-design-optimizer
```

Expected result:

```text
Skill is valid!
```

### 5. Validate MATLAB Templates

From the repository root:

```powershell
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\basic_hfss_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\patch_antenna_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\parametric_sweep_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\literature_reproduction_project.m
```

Each command should return `OK`.

## Usage

Invoke the skill directly in Codex:

```text
Use $hfss-design-optimizer to design a 2.45 GHz microstrip patch antenna and optimize S11.
```

Other useful prompts:

```text
Use $hfss-design-optimizer to generate an HFSS MATLAB script for a center-fed dipole at 150 MHz.
```

```text
Use $hfss-design-optimizer to reproduce the antenna structure from this paper and list missing simulation assumptions.
```

```text
Use $hfss-design-optimizer to sweep patch length and feed width, then export S11 as CSV.
```

```text
Use $hfss-design-optimizer to analyze this folder containing my paper, AEDT project, VBS/MATLAB scripts, and S-parameter exports; identify the innovation point and propose reusable HFSS design-method improvements.
```

## Typical Design Workflow

1. Describe the design target, frequency, substrate, materials, ports, and desired output.
2. Codex reads `SKILL.md` and the relevant files in `references/`.
3. Codex copies a MATLAB template from `assets/templates/`.
4. Codex edits the parameter block, geometry, boundaries, ports, analysis setup, and reports.
5. The generated MATLAB script writes a `.vbs` file.
6. HFSS runs the `.vbs` and saves an `.aedt` project.
7. HFSS exports result data.
8. Codex parses the data and proposes the next design or optimization step.

## MATLAB Script Pattern

Generated scripts should follow this structure:

```matlab
skillRoot = getenv('HFSS_DESIGN_OPTIMIZER_ROOT');
if isempty(skillRoot)
    skillRoot = 'F:\2026fall\HFSS_SKILL design\hfss-design-optimizer';
end
apiRoot = fullfile(skillRoot, 'assets', 'hfss-api-master');
if ~exist(apiRoot, 'dir')
    error('Bundled HFSS-MATLAB-API not found: %s', apiRoot);
end
addpath(apiRoot);
hfssIncludePaths([apiRoot filesep]);

hfssExePath = 'F:\AnsysEM\v221\Win64\ansysedt.exe';
tmpPrjFile = fullfile(pwd, 'design.aedt');
tmpScriptFile = fullfile(pwd, 'design.vbs');

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, 'Design1');

% Geometry, materials, ports, boundaries, setup, reports.

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

% Run manually after checking the generated VBS.
% hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);
```

## Running HFSS

While debugging, keep HFSS open after running the script:

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
```

For batch runs after the script is verified:

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, true, true);
```

Always close the script file with `fclose(fid)` before calling `hfssExecuteScript`.

Before calling `hfssExecuteScript`, confirm that `hfssExePath` points to the actual Ansys Electronics Desktop executable on the current machine. The skill can generate MATLAB/VBS files without HFSS, but solving requires a valid `ansysedt.exe` path.

## Result Parsing

For CSV reports exported from HFSS:

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py .\result.csv --target-ghz 2.45 --y-column S
```

For JSON output:

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py .\result.csv --target-ghz 2.45 --y-column S --json
```

To summarize the latest HFSS batch run in an appended AEDT log:

```powershell
python .\hfss-design-optimizer\scripts\summarize_hfss_log.py .\model.log --json
```

This is useful because AEDT appends old failures and new successful runs to the same log file.

## Literature Reproduction Workflow

When reproducing a paper, ask Codex to:

1. Extract all dimensions, materials, ports, boundaries, frequency ranges, and reported metrics.
2. Create an assumption table for missing information.
3. Generate a reproduction MATLAB script.
4. Export comparable HFSS data.
5. Compare simulation results against paper curves or tables.
6. Tune only parameters justified by paper ambiguity or manufacturing tolerance.

The detailed process is in `references/literature-replication.md`.

## Paper And Simulation Bundle Learning

When you place a paper and related simulation artifacts in one folder, the skill can create a compact learning summary:

```powershell
python .\hfss-design-optimizer\scripts\analyze_research_bundle.py "path\to\bundle" --json
```

The analyzer writes `.hfss_skill_learning\bundle_learning_summary.md` under the bundle. Use that summary to extract the claimed innovation, compare it against the HFSS model, identify missing assumptions, and decide which lessons should become reusable skill updates. The detailed process is in `references/research-bundle-learning.md`.

## Notes

- This skill does not replace HFSS validation. Always inspect the first generated model visually in HFSS.
- Port direction, boundary placement, and material assumptions strongly affect simulation results.
- Start with a single baseline run before launching a large optimization sweep.

## 中文说明

`hfss-design-optimizer` 是一个面向 Codex 的 HFSS 辅助设计 skill。它可以帮助 Codex 基于自然语言需求生成 MATLAB 脚本，并通过本地 HFSS-MATLAB-API 自动生成 HFSS VBScript，进一步创建 `.aedt` 工程、导出仿真结果、执行参数优化，以及根据论文复现射频/微波结构。

整体工作链路如下：

```text
Codex 设计需求
  -> MATLAB 驱动脚本
  -> HFSS VBScript (.vbs)
  -> Ansys Electronics Desktop 工程 (.aedt)
  -> 导出的 CSV / Touchstone / MATLAB 结果数据
  -> 参数优化或文献结果对比
```

### 功能特性

- 根据自然语言描述生成 HFSS 模型。
- 使用内嵌的 `assets/hfss-api-master` MATLAB API 完成几何建模、材料、边界、端口、求解和结果导出。
- 自动生成可复用的 MATLAB 脚本和 HFSS VBScript 文件。
- 支持常见天线和微波结构流程，例如偶极子、微带贴片、阵列、喇叭天线和论文复现模型。
- 支持围绕 S 参数、谐振频率、带宽、增益和论文曲线拟合的参数扫描与优化。
- 可以解析 HFSS 导出的 CSV 报告，快速提取关键结果。
- 可以在运行 HFSS 前检查生成的 MATLAB 脚本结构是否完整。

### 目录结构

```text
hfss-design-optimizer/
  SKILL.md
  README.md
  agents/
    openai.yaml
  assets/
    hfss-api-master/
    templates/
      basic_hfss_project.m
      patch_antenna_project.m
      parametric_sweep_project.m
      literature_reproduction_project.m
  references/
    api-map.md
    common-hfss-patterns.md
    design-workflow.md
    hfss-batch-troubleshooting.md
    fast-approximation.md
    literature-replication.md
    local-config.md
    optimization-workflow.md
    research-bundle-learning.md
  scripts/
    collect_api_signatures.ps1
    analyze_research_bundle.py
    parse_hfss_csv.py
    summarize_hfss_log.py
    validate_matlab_hfss_script.py
```

### 环境要求

- Windows
- 支持本地 skills 的 Codex
- MATLAB
- Ansys Electronics Desktop / HFSS
- 内嵌 HFSS-MATLAB-API：`assets/hfss-api-master`
- Python 3，用于运行辅助脚本
- PowerShell，用于扫描 API 函数签名

GitHub 用户重要提醒：内嵌 MATLAB API 可以随仓库一起移动，但 HFSS 可执行文件路径是每台机器本地配置。运行 HFSS 脚本前，必须确认或修改 `ansysedt.exe` 的实际路径。

当前默认路径为：

```text
HFSS 可执行文件:
F:\AnsysEM\v221\Win64\ansysedt.exe

HFSS-MATLAB-API 根目录:
F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master
```

如果你的路径不同，需要修改：

- `SKILL.md`
- `references/local-config.md`
- `assets/templates/` 目录下的 MATLAB 模板

当前工作站默认 HFSS 启动器是 `F:\AnsysEM\v221\Win64\ansysedt.exe`。如果 HFSS 安装在其他位置，请修改生成脚本、`references/local-config.md` 和需要复用的模板中的 `hfssExePath`。

### 部署方案

第一步，确认 skill 内嵌 HFSS-MATLAB-API。

将 API 放在一个固定目录，例如：

```text
F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master
```

确认其中包含这些子目录：

```text
3dmodeler/
analysis/
boundary/
general/
mesh/
radiation/
reporter/
```

第二步，确认 HFSS 路径。

确认下面的 HFSS 可执行文件存在：

```text
F:\AnsysEM\v221\Win64\ansysedt.exe
```

在 MATLAB 脚本中会这样使用：

```matlab
hfssExePath = 'F:\AnsysEM\v221\Win64\ansysedt.exe';
```

第三步，安装为 Codex skill。

将整个 `hfss-design-optimizer` 文件夹复制到本地 Codex skills 目录：

```powershell
$skillsDir = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force $skillsDir
Copy-Item -Recurse -Force .\hfss-design-optimizer $skillsDir
```

安装后路径应类似：

```text
C:\Users\<UserName>\.codex\skills\hfss-design-optimizer
```

复制完成后，重启或新开一个 Codex 会话，让 Codex 重新发现 skill metadata。

第四步，验证 skill。

如果本地有 Codex skill 校验脚本，可以运行：

```powershell
python C:\Users\<UserName>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<UserName>\.codex\skills\hfss-design-optimizer
```

期望结果：

```text
Skill is valid!
```

第五步，验证 MATLAB 模板。

在仓库根目录运行：

```powershell
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\basic_hfss_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\patch_antenna_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\parametric_sweep_project.m
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py .\hfss-design-optimizer\assets\templates\literature_reproduction_project.m
```

每条命令都应返回 `OK`。

### 使用方法

在 Codex 中显式调用：

```text
Use $hfss-design-optimizer to design a 2.45 GHz microstrip patch antenna and optimize S11.
```

也可以使用中文需求：

```text
Use $hfss-design-optimizer 帮我设计一个 2.45GHz 微带贴片天线，并优化 S11。
```

更多示例：

```text
Use $hfss-design-optimizer 生成一个 150MHz 中心馈电偶极子的 HFSS MATLAB 脚本。
```

```text
Use $hfss-design-optimizer 根据这篇论文复现天线结构，并列出缺失的仿真假设。
```

```text
Use $hfss-design-optimizer 扫描贴片长度和馈线宽度，并导出 S11 CSV。
```

```text
Use $hfss-design-optimizer 分析这个同时包含论文、AEDT 工程、VBS/MATLAB 脚本和 S 参数导出的文件夹，提取创新点并提出可复用的 HFSS 设计方法改进建议。
```

### 典型设计流程

1. 描述设计目标、工作频率、基板、材料、端口和需要导出的结果。
2. Codex 读取 `SKILL.md` 和 `references/` 中的相关流程文件。
3. Codex 从 `assets/templates/` 复制合适的 MATLAB 模板。
4. Codex 修改参数、几何体、边界、端口、求解设置和报告导出。
5. MATLAB 脚本生成 `.vbs` 文件。
6. HFSS 执行 `.vbs` 并保存 `.aedt` 工程。
7. HFSS 导出结果数据。
8. Codex 解析结果，并提出下一步优化或复现修正方案。

### MATLAB 脚本结构

生成脚本通常遵循下面结构：

```matlab
skillRoot = getenv('HFSS_DESIGN_OPTIMIZER_ROOT');
if isempty(skillRoot)
    skillRoot = 'F:\2026fall\HFSS_SKILL design\hfss-design-optimizer';
end
apiRoot = fullfile(skillRoot, 'assets', 'hfss-api-master');
if ~exist(apiRoot, 'dir')
    error('Bundled HFSS-MATLAB-API not found: %s', apiRoot);
end
addpath(apiRoot);
hfssIncludePaths([apiRoot filesep]);

hfssExePath = 'F:\AnsysEM\v221\Win64\ansysedt.exe';
tmpPrjFile = fullfile(pwd, 'design.aedt');
tmpScriptFile = fullfile(pwd, 'design.vbs');

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, 'Design1');

% 几何、材料、端口、边界、求解设置和报告。

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

% 检查生成的 VBS 后再运行。
% hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);
```

### 运行 HFSS

调试时建议让 HFSS 执行脚本后保持打开：

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
```

确认脚本无误后，可以使用批处理模式：

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, true, true);
```

注意：必须先 `fclose(fid)`，再调用 `hfssExecuteScript`。

调用 `hfssExecuteScript` 前，请确认 `hfssExePath` 指向当前机器真实存在的 Ansys Electronics Desktop 可执行文件。该 skill 可以在没有 HFSS 的情况下生成 MATLAB/VBS 文件，但真正求解必须依赖有效的 `ansysedt.exe` 路径。

### 结果解析

对于 HFSS 导出的 CSV 报告，可以运行：

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py .\result.csv --target-ghz 2.45 --y-column S
```

如果需要 JSON 输出：

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py .\result.csv --target-ghz 2.45 --y-column S --json
```

如果需要判断 HFSS 最新一次 batch 是否成功，可以运行：

```powershell
python .\hfss-design-optimizer\scripts\summarize_hfss_log.py .\model.log --json
```

这个脚本只分析日志里的最新一次 batch 段落，避免旧错误干扰判断。

### 文献复现流程

复现论文时，可以让 Codex 完成：

1. 提取论文中的尺寸、材料、端口、边界、频率范围和结果指标。
2. 为论文缺失信息建立假设表。
3. 生成复现用 MATLAB 脚本。
4. 导出可对比的 HFSS 数据。
5. 与论文中的曲线或表格进行对比。
6. 只针对论文模糊信息、加工误差或缺失细节进行合理调参。

详细流程见：

```text
references/literature-replication.md
```

### 论文与仿真文件 bundle 学习

当你把论文和相关仿真文件放在同一个文件夹中时，可以运行：

```powershell
python .\hfss-design-optimizer\scripts\analyze_research_bundle.py "path\to\bundle" --json
```

脚本会在该文件夹下生成 `.hfss_skill_learning\bundle_learning_summary.md`。使用这个摘要可以提取论文创新点、对照 HFSS 模型、定位缺失假设，并判断哪些经验值得沉淀成本地 skill 的通用设计方法。详细流程见 `references/research-bundle-learning.md`。

### 注意事项

- 这个 skill 不能替代 HFSS 工程检查。第一次生成模型后，仍然应该在 HFSS 中目视检查结构。
- 端口方向、边界位置和材料假设会显著影响仿真结果。
- 在启动大规模优化前，先完成一次可运行的基线仿真。
