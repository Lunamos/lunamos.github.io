#!/usr/bin/env python3
"""Build the static MechInterp Notes library. No third-party dependencies."""

from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TRACKS = {
    "reasoning": ("Reasoning faithfulness", "surface trace", "#b38e80"),
    "behavior": ("Agent behavior", "trajectory", "#9eaea3"),
    "latent": ("Latent mechanism", "hidden state", "#9dabb7"),
    "position": ("Research agenda", "position", "#a493a2"),
}

PAPERS = [
    {
        "slug": "thinking-drafts-faithfulness",
        "title": "Measuring the Faithfulness of Thinking Drafts in Large Reasoning Models",
        "zh": "推理草稿真的决定答案吗？",
        "authors": "Zidi Xiong, Shan Chen, Zhenting Qi, Himabindu Lakkaraju",
        "date": "2025-05-28",
        "venue": "Preprint",
        "arxiv": "2505.13774",
        "track": "reasoning",
        "time": "12 min",
        "tags": ["CoT", "Counterfactual", "Faithfulness", "LRM"],
        "question": "当 reasoning model 写下几十步 thinking draft 时，这些步骤究竟参与了结论形成，还是只是一个可以被答案阶段绕开的文本界面？",
        "verdict": "论文用文本层反事实干预发现：模型只选择性地遵循中间步骤，对 backtracking 更敏感；最终答案阶段又经常引入草稿之外的新推理。因此，监控 thinking draft 并不天然等于监控决策过程。",
        "context": [
            "Reasoning model 通常先生成不可直接展示的 thinking draft，再由 answer stage 生成最终回答。传统 CoT faithfulness 常在用户输入里放提示或偏见，再看模型是否在 CoT 中提及它；这最多说明输入影响了文本，不能说明草稿内部的某一步是否真正改变后续计算。",
            "这篇工作的关键移动，是把干预位置从 input 移到 draft 本身。它不声称读取模型的神经机制，而是测试表面推理链在生成过程中的因果作用。"
        ],
        "method": [
            ("准备草稿", "在 GPQA Diamond 与 MMLU global facts 上，使用 DeepSeek-R1、Qwen3-32B 或被测模型自身生成的 thinking drafts。"),
            ("插入反事实", "在草稿初段、中段或末段插入 Shift Mapping 或 Corrupt Option，并分别伪装成继续推理与显式 backtracking。"),
            ("继续生成", "让六个开源 reasoning models 从被干预位置继续完成草稿，记录它们是纠正错误、顺着错误走，还是忽略该步骤。"),
            ("检查答案阶段", "比较草稿结论与最终答案，并判断 answer stage 是否加入了草稿中没有的新推理。")
        ],
        "findings": [
            ("Backtracking 是更强的控制信号", "多数模型对伪装成“重新考虑”的反事实步骤更敏感，对普通 continue step 则可能沿原有轨迹继续。作者推测 backtracking 像一次 attention reset，但这不是内部机制证明。"),
            ("显式纠错比盲目跟随更忠实", "当模型主动发现并纠正插入错误时，草稿后续通常更一致；单纯跟随错误步骤的影响更依赖位置和任务。"),
            ("草稿结论与最终答案可以脱钩", "Answer stage 经常补充新的推理，甚至不遵循草稿结论。这直接削弱了“只监控 draft 就能控制最终答案”的假设。"),
            ("规模不是唯一变量", "更大的蒸馏模型总体更忠实，但模型家族、RLVR 方式、任务推理强度和草稿来源都会改变结果。")
        ],
        "audits": [
            ("强证据", "反事实直接写进推理过程，比相关性或让模型自评更接近因果测试；同时系统改变步骤类型与插入位置。"),
            ("主要局限", "干预仍发生在文本 token 层，并未访问 hidden states；Shift Mapping 与选项污染也主要适合选择题式任务。"),
            ("不能推出", "不能由此断言模型内部没有忠实推理，也不能把“不跟随错误步骤”简单算作不忠实：模型可能正确识别并拒绝异常。"),
            ("下一步", "将同一文本干预与 activation patching 对齐，寻找“步骤被接受/拒绝”时的内部状态差异，再做 mediation test。")
        ],
        "connection": "这篇适合当作 Agent trace 干预的最小范式：不要只统计某个 reasoning pattern 是否出现，而要修改它并观察后续行为。如果你研究 Coding Agent 的 false completion，可以在保持环境状态不变时插入/删除验证结论，测它是否真正决定 submit，再把效应定位到 hidden state。",
        "questions": [
            ("为什么忽略错误步骤会被判为不忠实？", "作者的定义关注草稿步骤是否因果影响结论，因此无声忽略会降低分数；但从能力角度它可能是好事。更合理的区分是显式纠错、隐式鲁棒和真正未读取。"),
            ("它属于 mechanistic interpretability 吗？", "严格说不是。它是对 surface reasoning trace 的因果行为测试，没有定位内部组件；但它能产生非常好的 mech-interp 假设和 clean/corrupted pairs。"),
            ("如何扩展到开放式 Coding Agent？", "把选项映射换成可验证的程序状态命题，例如“测试已经全部通过”或“文件 X 定义了目标函数”，然后观察 search/edit/verify 行为是否因干预改变。")
        ],
    },
    {
        "slug": "rfeval",
        "title": "RFEval: Benchmarking Reasoning Faithfulness under Counterfactual Reasoning Intervention in Large Reasoning Models",
        "zh": "正确答案，可能来自不一致的推理",
        "authors": "Yunseok Han, Yejoon Lee, Jaeyoung Do",
        "date": "2026-02-19",
        "venue": "Preprint",
        "arxiv": "2602.17053",
        "track": "reasoning",
        "time": "14 min",
        "tags": ["Benchmark", "RL", "Counterfactual", "Faithfulness"],
        "question": "能否在不依赖正确率的情况下，大规模检验 reasoning trace 是否内部一致，并且真的对输出具有因果影响？",
        "verdict": "RFEval 将 faithfulness 定义为 stance consistency 与 causal influence 的合取。在 7,186 个实例、7 类任务和 12 个开源模型上，49.73% 的输出至少违反其中一项；主要问题是不一致，而不是完全没有因果响应。",
        "context": [
            "Accuracy 回答“答案对不对”，faithfulness 回答“答案是否由模型写出的理由导出”。一个模型可以给出正确答案却在 reasoning 中支持另一个选项，也可以写出连贯推理但在关键前提被反转后仍坚持原答案。",
            "RFEval 的贡献不是再次用 LLM 判断 CoT 好不好，而是先定义两个可检验条件，再围绕它们构造对比式反事实。"
        ],
        "method": [
            ("抽取 stance", "把原始输出展平为 reasoning、explanation 与 answer，识别每一部分实际支持的立场。"),
            ("构造干预", "对 reasoning 中的前提、目标或结论做 output-level counterfactual intervention，而不是只改用户问题。"),
            ("检查一致性", "原始与干预后输出都必须在 reasoning、explanation、answer 之间保持 stance consistency。"),
            ("检查因果影响", "若反事实改变了推理立场，后续 explanation 或 answer 应发生相应改变；两项同时满足才记为 faithful。")
        ],
        "findings": [
            ("49.73% 不是“全部 CoT 的普遍失败率”", "它是 12 个开源模型在 RFEval 七类任务和特定判据下的结果。最常见失败来自 stance inconsistency，说明模型常写出不能支持自己答案的文本。"),
            ("任务结构比表面难度更关键", "数学与代码等答案收敛、判定脆弱的任务中问题更集中；开放式表达任务允许多条合理路线，判定也更困难。"),
            ("RL-style post-training 可能伤害 faithfulness", "同家族消融显示，在 SFT 上加入主要优化最终正确性的 RL-style objective，可能保持 accuracy 却降低一致性和因果影响。作者认为 reward 没有显式约束理由结构。"),
            ("Accuracy 不是可靠代理", "控制模型与任务后，accuracy-faithfulness 关联弱且统计不显著；因此报告 benchmark 分数不能替代单独的 faithfulness audit。")
        ],
        "audits": [
            ("强证据", "样本规模大、任务类型多，并用人工审查校验自动 evaluator；stance 提取 micro-F1 0.952，整体判定 accuracy 0.938。"),
            ("主要局限", "核心判断仍依赖 LLM evaluator；反事实是否自然、是否唯一对应目标 reasoning stance，都可能影响结论。"),
            ("谨慎解释 RL", "论文给的是特定模型家族内的观察，不足以证明 RLVR 普遍降低忠实度；reward、数据与生成协议可能共同作用。"),
            ("工业启发", "后训练应把 final correctness 与 process integrity 分开评测；否则 reward hacking 可以表现为更会给正确答案、更不会保持理由一致。")
        ],
        "connection": "它很适合作为你做 trace-level indicators 时的方法论参照：先把 Bad Pattern 写成两个或三个可判定条件，再构造能够让不同解释产生不同预测的 intervention。真正有价值的指标不是和失败相关，而是在控制模型、任务难度和长度后仍有增量，并能指导训练目标。",
        "questions": [
            ("49.7% 能直接写进面试回答吗？", "可以，但必须同时说清 12 个开源模型、7 类任务、7,186 个实例和 RFEval 的定义，不能泛化成“所有 reasoning model 一半不忠实”。"),
            ("为什么 stance consistency 也算 faithfulness？", "因为即使最终答案随干预改变，如果 reasoning、解释和答案彼此矛盾，表面 trace 仍无法作为可靠监督或监控信号。"),
            ("怎样把它用于训练？", "可以把一致性与反事实响应做成独立 reward 或 rejection criterion，但必须防止模型只学会表面格式一致；最好再用 latent intervention 检查内部路径。")
        ],
    },
    {
        "slug": "interpretable-traces-unexpected-outcomes",
        "title": "Interpretable Traces, Unexpected Outcomes: Investigating the Disconnect in Trace-Based Knowledge Distillation",
        "zh": "最容易读懂的推理，不一定最适合训练",
        "authors": "Siddhant Bhambri, Upasana Biswas, Subbarao Kambhampati",
        "date": "2026-04-16",
        "venue": "ACL 2026",
        "arxiv": "2505.13792",
        "track": "reasoning",
        "time": "11 min",
        "tags": ["Distillation", "Human Study", "CoT", "Supervision"],
        "question": "作为蒸馏监督的 reasoning trace，必须语义正确、简洁而且让人易懂，才能训练出更好的模型吗？",
        "verdict": "答案是否定的：trace 的逐步正确性、下游答案准确率和人类可理解性是三个不同目标。冗长 R1 traces 带来最佳下游性能，却被 100 位参与者评为最难理解、认知负担最高。",
        "context": [
            "很多 distillation 工作默认：教师的 CoT 越正确、越可解释，学生学得越好。但标准 token-level SFT 并不直接要求学生真正执行这些步骤；trace 也可能只是提供更多语言模式、搜索轨迹或计算 token。",
            "论文通过可验证的规则分解生成“步骤正确/步骤错误但最终答案相同”的训练数据，试图把 trace semantics 与 final label 解耦。"
        ],
        "method": [
            ("构造可验证 traces", "在三类 QA 数据上把问题分解成分类与信息检索步骤，算法性检查每个中间步骤是否正确。"),
            ("控制最终答案", "训练样本始终提供正确 final answer，只改变中间 trace 是正确、错误、R1 原始、R1 摘要还是 post-hoc explanation。"),
            ("训练与评测", "在 Llama 与 Qwen 系列上做 SFT，分别评估最终答案和生成 trace 的步骤准确率。"),
            ("人类研究", "100 位参与者用 5 点量表评价不同 trace 的可理解性，并用 NASA-TLX 风格指标评价认知负担。")
        ],
        "findings": [
            ("正确 trace 不保证正确答案", "实验中，正确中间步骤只在 28% 的测试问题上导向正确最终解；错误 traces 也没有稳定破坏答案表现。"),
            ("R1 traces 训练性能最好", "尽管原始 R1 trace 冗长且步骤难验证，用它做 SFT 得到的 final solution accuracy 最强，优于更整洁的算法分解或 post-hoc 解释。"),
            ("性能与用户可读性反向", "参与者给 R1 traces 的平均 interpretability 3.39/5、cognitive load 4.59/5：它们最有效，却最不适合直接展示。"),
            ("训练接口与用户接口应分开", "面向优化的 latent/surface scratchpad 可以保留搜索与冗余；面向用户的解释应重新压缩、验证和组织，而不是直接暴露训练 trace。")
        ],
        "audits": [
            ("强证据", "通过始终固定正确 final answer，论文能更干净地研究中间语义；又加入人类研究，不把“可解释”交给单一 LLM judge。"),
            ("主要局限", "实验集中于可规则分解的 QA，较小学生模型和 SFT；它不能直接说明 frontier reasoning model 的在线内部计算。"),
            ("关键混杂", "R1 traces 更长，意味着更多 token、更多模式与更大有效监督预算。若不匹配 token/compute，很难判断收益来自何种语义。"),
            ("不能推出", "不能因此说 trace correctness 不重要；在安全、数学证明或需要过程审计的场景，错误中间步骤本身就是部署风险。")
        ],
        "connection": "这篇会帮助你把“Agent training environment 的质量”和“展示给人看的 rubric/trace”分开。训练数据可以保留有用的探索过程，但评测与产品层需要生成更短、更可核验的解释；两者不能用一个 readability 指标统一优化。",
        "questions": [
            ("为什么错误 trace 仍能训练出会答题的模型？", "Token-level SFT 可能主要学习输入-答案映射、局部模式或额外计算长度，并不保证逐步执行教师算法；错误步骤也可能被模型当作可忽略噪声。"),
            ("这是否支持隐藏 CoT？", "它支持“训练 scratchpad 与用户解释分离”，但不是政策论证。是否隐藏还涉及安全监控、隐私、可验证性和产品风险。"),
            ("更强的实验怎样做？", "匹配所有 trace 类型的 token 数、训练 FLOPs 与信息量，再加入 activation-level mediation，观察学生是否形成不同内部算法。")
        ],
    },
    {
        "slug": "actonomy",
        "title": "How to Interpret Agent Behavior",
        "zh": "先给 Agent 行为一套共同语言",
        "authors": "Jie Gao et al.",
        "date": "2026-05-13",
        "venue": "Preprint",
        "arxiv": "2605.13625",
        "track": "behavior",
        "time": "12 min",
        "tags": ["Taxonomy", "Agent", "Trajectory", "Observability"],
        "question": "当 Claude Code、Codex 一类 Agent 连续运行数小时，如何把自然语言 trace 转换成可比较、可扩展且不依赖临时标签的行为描述？",
        "verdict": "ACT·ONOMY 用 Grounded Theory 建立了 10 个 actions、46 个 subactions、120 个叶子类别的三层 taxonomy，并提供自动标注与扩展协议。它建立的是行为层公共语言，而不是模型内部机制。",
        "context": [
            "长时 Agent 的日志同时包含 planning、reasoning、retrieval、tool execution、evaluation 与 reflection。每个团队都能做一套 dashboard，但如果 action 边界与命名不同，跨模型、跨 scaffold 的比较就不成立。",
            "ACT·ONOMY 借用定性研究中的 Grounded Theory：不是先拍脑袋列 failure modes，而是从已有文献和真实描述中反复编码、合并、审计，形成 living taxonomy。"
        ],
        "method": [
            ("建立语料", "从相关论文中收集 565 条 Agent 行为描述，由六位作者共同审查并迭代 codebook。"),
            ("形成层级", "将行为组织为 10 个顶层 actions、46 个 subactions 和 120 个 grounded leaf descriptions。"),
            ("验证标注", "人类标注员验证清晰度；LLM pipeline 在 held-out trajectories 上逐句给出带原文证据的标签。"),
            ("持续扩展", "开放 repository、自动分析工具和 extension protocol，使新领域可以添加类别而不破坏上层可比性。")
        ],
        "findings": [
            ("自动标注具有较高一致性", "论文报告自动 pipeline 与人工编码在每一层 Cohen's κ 都高于 0.81；这说明 taxonomy 至少能被比较稳定地操作化。"),
            ("同一 Agent 会形成行为画像", "不同 trajectories 的 retrieval、planning、evaluation、reflection 占比可聚合成 profile，用于发现 scaffold 与任务差异。"),
            ("细粒度组合揭示 failure precursor", "例如若出现完成声明、缺少验证、忽略外部反馈等叶子标签组合，可以描述“未验证仍提交”，比一个宽泛 hallucination 标签更可行动。"),
            ("Taxonomy 是描述层，不是根因层", "它能指出行为何时发生、怎样共现，却不能仅凭标签判断是模型、环境、memory、tool policy 还是任务本身造成。")
        ],
        "audits": [
            ("强证据", "构建过程透明，发布 codebook 与扩展协议；不只报告分类 accuracy，还强调引用原 trace 作为 grounded evidence。"),
            ("主要局限", "初始 taxonomy 来自有限文献中的 565 条描述，天然偏向已被研究的 Agent 类型与英语任务。"),
            ("自动化风险", "LLM annotator 可能把解释性语言误当实际行为；商业 API 更新也会让同一 pipeline 漂移。"),
            ("合理定位", "它属于 behavior interpretability / observability，是做 mechanistic hypothesis 的上游，不应直接包装成 circuit-level explanation。")
        ],
        "connection": "你做 Coding Agent Bad Pattern 的优势，是已经处在这篇工作的下一步：不仅要有 taxonomy，还要验证某个 pattern 与效率、未来失败和干预收益的关系。你可以把自己的 10+ indicators 映射到 ACT·ONOMY 上层，再保留 StepFun 特有的 long-horizon / context-efficiency 叶子指标。",
        "questions": [
            ("为什么不用一个强 LLM 直接总结 trace？", "自由总结难以跨样本统计，也容易改变粒度和术语。固定 taxonomy 提供可复现单位，同时引用原句让人审计。"),
            ("κ>0.81 是否说明标签客观真实？", "只说明在给定 codebook 下两套标注较一致，不证明分类覆盖完整、对失败有预测力或具有因果意义。"),
            ("什么时候应该增加新类别？", "当大量 grounded examples 稳定落入 unclassified，或现有叶子无法区分会导致不同干预的行为时；不应为单个有趣案例无限增殖标签。")
        ],
    },
    {
        "slug": "traceprobe",
        "title": "What Resolve Rate Hides: Trajectory Structure Diagnostics for Coding Agents",
        "zh": "Resolve Rate 看不见的过程差异",
        "authors": "Rui Shu et al.",
        "date": "2026-07-07",
        "venue": "Preprint",
        "arxiv": "2607.06184",
        "track": "behavior",
        "time": "13 min",
        "tags": ["Coding Agent", "SWE-Bench", "Failure Analysis", "Trace"],
        "question": "两个 Coding Agent 都通过测试，或者都失败了，怎样判断谁更早找到相关代码、谁做了更多无效工作，以及失败从哪里开始分叉？",
        "verdict": "TraceProbe 将异构轨迹规范成九类 actions，用 Insight 检测单条轨迹 anti-pattern，用 Converge 对齐同任务的两次运行。它证明过程指标能补充 resolve rate，但多数 anti-pattern 更像任务难度线索，而不是单次运行的根因诊断器。",
        "context": [
            "Resolve rate 是极低带宽的结果信号：它不知道 Agent 搜索了多少无关文件、反复撤销了多少 patch，也不知道一次成功是否只是高成本重试后的偶然。",
            "TraceProbe 的价值不在于引入一个更复杂总分，而是保留可审计的结构：每个 action 做了什么、产生什么 effect，以及两条同任务轨迹在哪个层次开始偏离。"
        ],
        "method": [
            ("Normalize", "把不同产品的 search/read/edit/test/reason traces 转成九类 canonical actions，并确定性标注 action effect。"),
            ("Insight", "用冻结规则检测 search loop、verification skip、unsupported completion 等单轨迹 anti-pattern。"),
            ("Converge", "将待分析轨迹与同任务 resolved reference 做动态对齐，从 file、function、edit stability 与 completion behavior 等层次定位分歧。"),
            ("Evaluate", "在 SWE-Bench Verified 的 2,500 条轨迹、五个 production settings 上比较结果、任务难度与过程指标，并测试迁移。")
        ],
        "findings": [
            ("Search loop 是最稳定的警告", "多种 anti-pattern 随任务难度一起增加，未必解释单次失败；search loop 在冻结阈值和跨 benchmark 检查中相对稳定。"),
            ("文件粒度过粗", "成功与失败可能都访问正确文件；真正区分轨迹的是选中了哪个 function、修改是否保留、以及最后是否留下未解决 dead end。"),
            ("成功轨迹也有质量差异", "相同 resolve 结果下，有的 Agent 很早触达 task-relevant code，有的经历大量 failed work。过程 profile 能揭示成本、时延和稳定性差别。"),
            ("指标不能冒充 root cause", "作者明确说 TraceProbe 不是 resolve rate 替代品，也不是 per-run causal oracle；它的作用是提出检查优先级和 failure hypothesis。")
        ],
        "audits": [
            ("强证据", "真实 production settings、同任务 same-outcome controls、阈值冻结以及 reference sensitivity 检查，避免只用失败/成功做粗糙相关。"),
            ("主要局限", "主要基于 SWE-Bench 与其 tests，行为效果受 benchmark scaffold 和 telemetry 定义约束；非 Python 迁移仍有限。"),
            ("指标悖论", "某 pattern 在 failed runs 更多，可能只是困难任务让 Agent 运行更久；必须控制任务和 trajectory length。"),
            ("最重要的下一步", "把稳定 pattern 变成干预：限制重复搜索、强制验证或提前切换策略，观察 matched tasks 上成功率和成本是否改善。")
        ],
        "connection": "这是与你 StepFun 经历最接近的论文。你面试时可以用它说明自己为什么强调“validated indicators”：Bad Pattern 必须区分任务难度信号、早期失败预测器与可干预根因，并且要跨模型比较命中率，而不是挑几个 trace 讲故事。",
        "questions": [
            ("同 resolve rate 为什么还需要 trace metric？", "部署关心的不只是完成，还关心 tokens、时延、失败恢复、可重复性和风险。同结果的过程质量会影响成本与下一次任务的鲁棒性。"),
            ("规则指标会不会不如 LLM judge？", "规则覆盖有限但可审计、可冻结、可跨版本比较；LLM judge 更灵活却有漂移和叙事偏差。合理方案是规则负责核心信号，LLM 用于发现候选和解释。"),
            ("如何证明 search loop 是因果问题？", "当前论文还没有证明。需要对 matched tasks 修改 search policy 或设置 loop breaker，再测成功率、触达相关代码时间和副作用。")
        ],
    },
    {
        "slug": "latent-programming-horizons",
        "title": "Latent Programming Horizons in Coding Agents",
        "zh": "Agent 在写代码之前，是否已经预见未来？",
        "authors": "André Silva, Han Tu, Martin Monperrus",
        "date": "2026-07-06",
        "venue": "Preprint",
        "arxiv": "2607.05188",
        "track": "latent",
        "time": "15 min",
        "tags": ["Linear Probe", "Residual Stream", "Coding Agent", "Planning"],
        "question": "Coding Agent 每次调用模型时的 residual stream，是否编码当前代码的真实状态，甚至编码尚未发生的未来 edit 会带来什么结果？",
        "verdict": "线性 probe 能从 hidden states 解码编译、测试、进展和 regression，full correctness AUC 最高 0.83；对未来程序性质的预测在约 25 步前仍高于随机。但这证明的是 decodability，不是 Agent 因果使用了这些方向。",
        "context": [
            "行为轨迹只能告诉我们 Agent 做了什么。这篇论文第一次把真实代码仓库中的长程 editing trajectory 与每一步语言模型的 residual stream 对齐，让“当前程序状态”成为有外部执行器验证的 latent label。",
            "它提出 latent programming horizon：若当前 hidden state 能预测 k 步之后代码的性质，模型内部可能已经形成关于未来轨迹的表示。但“表示未来”也可能只是读取当前进度和任务难度。"
        ],
        "method": [
            ("收集轨迹", "两个 open-weight models 在 mini-swe-agent scaffold 上运行 SWE-Bench Verified 与 SWE-Bench Pro，共 22,714 条 trajectories、1,231 个任务。"),
            ("提取状态", "在每个 Agent step 抽取不同 Transformer 层的 residual-stream vector，并把它与当时 checkout 的代码版本对齐。"),
            ("定义外部标签", "实际运行 parser 与 tests，标注 well-formedness、full correctness、partial correctness 和 regression。"),
            ("训练 horizon probes", "逻辑回归既预测当前 k=0 的属性，也预测 k=1…50 步之后的程序属性；使用 shuffled-label control 与跨数据集迁移。")
        ],
        "findings": [
            ("当前程序状态线性可解码", "Full correctness 最高 AUC 0.83，partial correctness 最高约 0.84；well-formedness 因标签极不平衡，在 Verified 上接近随机。"),
            ("中间层信号最强", "两个模型、两个数据集和多数属性都呈 inverted-U：浅层弱，中间层峰值，最终层略降，可能因为后层更贴近 next-token prediction。"),
            ("表示可跨 benchmark 迁移", "Full/partial correctness probes 跨 Verified 与 Pro 不重训仍达到约 0.63-0.78 AUC，通常只下降 0.04-0.09。"),
            ("未来 edit 在当前状态中可预测", "随着 k 增大信号衰减，但直到约 25 步仍高于随机。它可能是规划表示，也可能混入 trajectory progress、任务难度或策略惯性。")
        ],
        "audits": [
            ("强证据", "标签由真实编译和测试产生，样本量大，并做了 shuffled control、layer sweep 与跨 benchmark transfer。"),
            ("主要局限", "只有两个模型、一个 mini-swe-agent scaffold 和两个 SWE benchmarks；frontier closed models 是否相同未知。"),
            ("核心因果缺口", "Probe 高 AUC 只说明信息可读。模型可能完全不使用 probe direction 做 action selection；作者也明确把 steering 留给未来工作。"),
            ("最关键的混杂", "未来成功可由当前是否接近完成、任务难度、trajectory length 等预测。需要 matched-prefix、time-to-go controls 与 intervention 才能支持真正 look-ahead。")
        ],
        "connection": "这是最适合你继续做的接口：先用 StepFun 的 failure taxonomy 定义外部 label，再从 hidden states 找到能够提前预测 context inefficiency、false completion 或 abnormal termination 的 feature；随后用 FLAS 或局部 steering 做干预。这样正好形成“行为诊断 → 表征定位 → 因果控制”。",
        "questions": [
            ("AUC 0.83 是否说明 Agent 知道代码正确？", "只能说某个线性读出器能从 hidden state 恢复相关信息。要说 Agent“知道并使用”，需要干预该表示并改变 edit、test 或 submit 行为。"),
            ("25 步 horizon 会不会只是 task difficulty？", "完全可能。应在同任务、多 seed、相同当前 tests 与相似剩余步数的 prefixes 间比较，并做 residualization 或 matched controls。"),
            ("下一步最漂亮的实验是什么？", "在模型准备做高风险 edit 前，沿 regression probe 或 SAE feature 做低强度干预，测试是否促使它先验证、改变 edit，且不只是让输出更保守。")
        ],
    },
    {
        "slug": "reasoning-is-latent",
        "title": "LLM Reasoning Is Latent, Not the Chain of Thought",
        "zh": "Reasoning 的研究对象到底是什么？",
        "authors": "Wenshuo Wang",
        "date": "2026-04-17",
        "venue": "Position paper",
        "arxiv": "2604.15726",
        "track": "position",
        "time": "10 min",
        "tags": ["Position", "Latent State", "CoT", "Compute"],
        "question": "CoT 提升性能时，真正起作用的是可见文本、隐藏状态轨迹，还是仅仅因为模型获得了更多串行计算预算？",
        "verdict": "作者主张将 latent-state trajectory 作为默认研究对象，但不是宣布 CoT 无用。论文用 H1/H2/H0 强迫实验分别控制 latent state、surface trace 与 serial compute；它是一份研究议程，不是单篇决定性实证。",
        "context": [
            "很多论文把“有 CoT 比没有 CoT 更准”直接解释成语言化步骤参与了推理，但这个对比同时增加了 token 数、迭代次数和隐藏状态演化机会。相反，probe 读出 hidden state 也不能排除它只是相关副产物。",
            "这篇 position paper 最有用的地方是把三种常被混在一起的解释写成可竞争假设，而不是它的标题式结论。"
        ],
        "method": [
            ("H2: Surface mediation", "推理主要由显式 CoT 文本承载；在 compute 固定时，改变 trace 应稳定改变答案，保留 trace 应能挽救行为。"),
            ("H0: Compute null", "收益主要来自更多 serial compute、搜索或采样预算；换一种中间表示只要预算相当，也应恢复大部分收益。"),
            ("H1: Latent mediation", "任务相关 hidden-state trajectory 是主要中介；latent commitment 可以早于或独立于语言化 trace，并接受直接干预。"),
            ("三臂对照", "理想实验分别操纵 surface S、latent Z、budget B，预先写明什么结果支持一项并反驳另一项。")
        ],
        "findings": [
            ("作者认为 H1 是默认工作假设", "现有证据显示 surface CoT 常不完整，特定 hidden states 能早期预测行为，latent intervention 有时又能直接改变结果。"),
            ("H2 在特定制度下仍成立", "当外部系统强制后续执行显式计划、检索步骤或形式证明时，surface trace 成为 constitutive state，而不只是展示文本。"),
            ("H0 在搜索密集任务中很强", "更多采样、回溯和 token budget 本身可以带来收益；若不匹配 compute，CoT 与 latent method 的比较都可能误判。"),
            ("核心贡献是可证伪设计", "论文要求报告每个实验臂改变了 S/Z/B 中哪些变量，并寻找能够让三个假设产生不同预测的 setting。")
        ],
        "audits": [
            ("价值", "提供很好的 reviewer checklist：看到任何 reasoning gain，都先问 surface、latent 与 compute 是否一起变化。"),
            ("证据等级", "它是 position paper 和文献综合；标题比证据更强，不应引用为“已经证明 reasoning 不在 CoT”。"),
            ("概念难点", "Surface token 本身也会改变后续 hidden states，Z 与 S 很难完全正交；latent intervention 还可能改变有效 compute。"),
            ("使用方式", "把 H1/H2/H0 当实验设计工具，而不是阵营标签。不同任务、scaffold 与监督制度可能落在不同 regime。")
        ],
        "connection": "它为 FLAS 与 Agent Interp 提供了一个很好的研究 framing：比较 surface prompt/CoT intervention、matched-compute baseline 和 activation trajectory intervention。只有在相同 token 与采样预算下，FLAS 仍表现出更稳定的因果控制，才能说收益来自 latent-state dynamics。",
        "questions": [
            ("为什么标题不能照单全收？", "因为论文自己也承认 H2 与 H0 有局部适用 regime，且大量证据来自文献综合；正确表述是“作者建议把 H1 作为默认工作假设”。"),
            ("怎样匹配 serial compute？", "至少控制生成 token、forward passes、采样数、工具调用与 wall-clock/compute；不同表示长度带来的缓存和并行差异也应报告。"),
            ("FLAS 怎样进入三假设框架？", "FLAS 属于 Z intervention；应与等 norm 的固定 steering、等 token 的 CoT prompt、以及纯增加 decoding budget 的 B baseline 比较。")
        ],
    },
]

EN = {
    "thinking-drafts-faithfulness": {
        "zh": "Do Thinking Drafts Actually Determine the Answer?",
        "question": "When a reasoning model writes dozens of intermediate steps, do those steps causally shape its conclusion, or are they a textual interface that the answer stage can bypass?",
        "verdict": "Text-level counterfactual interventions show selective faithfulness: models respond more strongly to backtracking steps, while the answer stage often adds reasoning absent from the draft. Monitoring the draft is therefore not equivalent to monitoring the decision process.",
        "context": [
            "Reasoning models commonly produce a hidden thinking draft before an answer stage writes the user-facing response. Earlier faithfulness tests often inserted hints into the user prompt and checked whether the model mentioned them; that does not tell us whether a particular step inside the draft actually affects later computation.",
            "This paper moves the intervention from the input into the draft. It tests the causal role of surface reasoning, not the neural mechanism underneath it."
        ],
        "method": [
            ("Prepare drafts", "Use GPQA Diamond and the global-facts subset of MMLU, with drafts produced by DeepSeek-R1, Qwen3-32B, or the evaluated model itself."),
            ("Insert counterfactuals", "Add Shift Mapping or Corrupt Option statements at early, middle, or late positions, framed either as continued reasoning or explicit backtracking."),
            ("Resume generation", "Ask six open reasoning models to continue and classify whether they correct, follow, or ignore the inserted step."),
            ("Audit the answer stage", "Compare the draft conclusion with the final answer and detect reasoning newly introduced after the draft.")
        ],
        "findings": [
            ("Backtracking is a stronger control signal", "Most models react more to counterfactuals framed as reconsideration. Ordinary continuation steps are more likely to be ignored along an established trajectory."),
            ("Explicit correction is more faithful than blind following", "When a model notices and rejects the injected error, later reasoning is usually more coherent; following behavior depends more on position and task."),
            ("Draft and answer can decouple", "The answer stage often performs additional reasoning or contradicts the draft conclusion, weakening the assumption that draft monitoring controls the answer."),
            ("Scale is not the only variable", "Model family, RLVR recipe, task intensity, and draft source all affect measured faithfulness.")
        ],
        "audits": [
            ("Strong evidence", "Directly editing the reasoning process is more causal than correlation or self-evaluation, and the study varies step type and location."),
            ("Main limitation", "Interventions remain at the token level and focus on multiple-choice-like tasks; no hidden state or component is localized."),
            ("What it does not show", "It does not prove that internal reasoning is absent. Ignoring a bad step may reflect robust rejection rather than unfaithfulness."),
            ("Next experiment", "Align the same textual interventions with activation patching, then test whether internal states mediate accepting or rejecting the step.")
        ],
        "connection": "This is a minimal template for intervening on agent traces: do not only count a reasoning pattern; edit it and test downstream behavior. For false completion in coding agents, insert or remove a verification claim while holding the environment fixed, then localize the effect in hidden states.",
        "questions": [
            ("Why can ignoring an incorrect step count as unfaithful?", "The definition asks whether a stated step causally affects the conclusion. A better analysis should separate explicit correction, silent robustness, and genuine non-use."),
            ("Is this mechanistic interpretability?", "Not strictly. It is a causal behavioral test of the surface trace, but it creates excellent clean/corrupted pairs for mechanistic work."),
            ("How would this extend to coding agents?", "Replace option mappings with verifiable program-state claims, such as whether tests pass or which file defines the target behavior, and observe search, edit, verification, and submission decisions.")
        ],
    },
    "rfeval": {
        "zh": "A Correct Answer Can Rest on Inconsistent Reasoning",
        "question": "Can reasoning faithfulness be evaluated at scale, independently of answer accuracy, by testing both internal consistency and causal responsiveness?",
        "verdict": "RFEval defines faithfulness as the conjunction of stance consistency and causal influence. Across 7,186 instances, seven tasks, and twelve open models, 49.73% of outputs violate at least one condition, mostly through inconsistency rather than total causal insensitivity.",
        "context": [
            "Accuracy asks whether an answer is correct; faithfulness asks whether the stated reasons support and determine that answer. A model may answer correctly while its reasoning supports another option, or keep the same answer after a key premise is reversed.",
            "RFEval first defines two testable conditions and then builds contrastive interventions around them, instead of asking a judge whether a chain of thought merely looks good."
        ],
        "method": [
            ("Extract stances", "Flatten reasoning, explanation, and answer, then identify the position supported by each part."),
            ("Construct interventions", "Apply output-level counterfactual changes to premises, goals, or conclusions rather than modifying only the user question."),
            ("Test consistency", "Both original and intervened outputs must maintain a coherent stance across reasoning, explanation, and answer."),
            ("Test causal influence", "When the reasoning stance changes, a downstream explanation or answer should change accordingly; both criteria are required.")
        ],
        "findings": [
            ("49.73% is benchmark-specific", "The number describes twelve open models under RFEval's tasks and definitions, not a universal failure rate for all chains of thought."),
            ("Task structure matters", "Failures concentrate in brittle, convergent domains such as math and code, where a local contradiction more sharply affects the solution."),
            ("RL-style post-training may reduce faithfulness", "Within-family comparisons suggest that optimizing final correctness can preserve accuracy while weakening stance consistency and causal influence."),
            ("Accuracy is a poor proxy", "After controlling for model and task, the accuracy-faithfulness relationship is weak and statistically insignificant.")
        ],
        "audits": [
            ("Strong evidence", "The benchmark is large and diverse, and human checks validate its automated evaluator: stance extraction micro-F1 is 0.952 and overall judgment accuracy 0.938."),
            ("Main limitation", "The core judgment still depends on an LLM evaluator, and the naturalness and uniqueness of counterfactuals can affect results."),
            ("Interpret RL carefully", "The evidence is from specific model families and recipes; it does not prove that RLVR generally reduces faithfulness."),
            ("Deployment lesson", "Post-training should evaluate final correctness and process integrity separately, otherwise reward hacking may appear as correct answers with incoherent rationales.")
        ],
        "connection": "This is a useful model for validating trace-level indicators: define executable conditions, construct interventions that separate competing explanations, and test incremental value after controlling for model, task difficulty, and length.",
        "questions": [
            ("Can I quote the 49.7% number in an interview?", "Yes, but include the twelve open models, seven tasks, 7,186 instances, and RFEval's definition. Do not generalize it to all reasoning models."),
            ("Why is stance consistency part of faithfulness?", "Even if an answer reacts to intervention, a trace that contradicts its own conclusion is unreliable as supervision or monitoring evidence."),
            ("How might it become a training signal?", "Consistency and counterfactual responsiveness can be separate rewards or filters, but latent checks are needed to prevent superficial formatting compliance.")
        ],
    },
    "interpretable-traces-unexpected-outcomes": {
        "zh": "The Easiest Reasoning to Read Is Not Always the Best Training Signal",
        "question": "Must a reasoning trace be semantically correct, concise, and easy for people to understand in order to train a better student model?",
        "verdict": "Step correctness, downstream answer accuracy, and human interpretability are distinct objectives. Verbose R1 traces give the best downstream performance, yet 100 participants rate them least interpretable and most cognitively demanding.",
        "context": [
            "Trace distillation often assumes that a more correct and readable teacher chain produces a better student. Token-level SFT, however, does not force the student to execute the teacher's algorithm; traces may provide useful patterns, search histories, or simply more compute tokens.",
            "The paper separates trace semantics from the final label by constructing verifiable traces that can be correct or incorrect while always pairing them with the correct answer."
        ],
        "method": [
            ("Build verifiable traces", "Decompose three QA datasets into classification and retrieval steps whose intermediate correctness can be checked algorithmically."),
            ("Hold the answer fixed", "Always provide the correct final answer while varying correct, incorrect, raw R1, summarized R1, and post-hoc traces."),
            ("Train and evaluate", "Fine-tune Llama and Qwen models, then measure both final answers and generated step accuracy."),
            ("Run a human study", "One hundred participants rate interpretability on a five-point scale and cognitive load with NASA-TLX-style measures.")
        ],
        "findings": [
            ("Correct traces do not guarantee correct answers", "Correct intermediate steps lead to correct test answers in only 28% of cases; incorrect traces do not consistently damage final accuracy."),
            ("Raw R1 traces train best", "Despite their length and noisy structure, R1 traces produce the strongest final solution accuracy."),
            ("Performance and readability diverge", "R1 traces receive mean interpretability 3.39/5 and cognitive load 4.59/5: effective as supervision, poor as a user explanation."),
            ("Training and explanation interfaces should differ", "A training scratchpad may preserve search and redundancy; a user-facing explanation should be separately compressed and verified.")
        ],
        "audits": [
            ("Strong evidence", "The final answer is held fixed while intermediate semantics vary, and interpretability is evaluated with people rather than only an LLM judge."),
            ("Main limitation", "Experiments focus on rule-decomposable QA, smaller student models, and SFT; they do not directly reveal online computation in frontier models."),
            ("Key confound", "R1 traces are longer, hence carry more tokens, patterns, and supervision budget. Token and compute matching are necessary to isolate semantic value."),
            ("What it does not show", "It does not make trace correctness irrelevant in safety, proof, or process-audit settings where an invalid intermediate step is itself a risk.")
        ],
        "connection": "It helps separate the quality of an agent training environment from the trace or explanation shown to a human. Training can preserve useful exploration, while evaluation and product layers should produce shorter, verifiable accounts.",
        "questions": [
            ("Why can an incorrect trace still teach a model to answer?", "SFT may learn input-answer mappings, local patterns, or extra computation length without executing the teacher's algorithm; bad steps can become ignorable noise."),
            ("Does this support hiding chain of thought?", "It supports separating training scratchpads from user explanations, but deployment policy also depends on safety monitoring, privacy, and verifiability."),
            ("What would a stronger experiment control?", "Match token count, FLOPs, and information content across traces, then use activation-level mediation to test whether students learn different internal algorithms.")
        ],
    },
    "actonomy": {
        "zh": "A Shared Language for Agent Behavior",
        "question": "When agents such as Claude Code and Codex run for hours, how can free-form traces become comparable, extensible behavioral descriptions rather than ad hoc labels?",
        "verdict": "ACT·ONOMY uses Grounded Theory to build a three-level taxonomy with 10 actions, 46 subactions, and 120 leaf categories, plus automated annotation and an extension protocol. It is a language for behavior, not a neural mechanism.",
        "context": [
            "Long-running agent logs mix planning, reasoning, retrieval, tool execution, evaluation, and reflection. Teams can each build dashboards, but comparisons fail when action boundaries and naming differ.",
            "ACT·ONOMY derives a living taxonomy by repeatedly coding, merging, and auditing descriptions from the literature and real examples rather than inventing a fixed failure list upfront."
        ],
        "method": [
            ("Construct the corpus", "Collect 565 agent-behavior descriptions from relevant papers and have six authors review and iteratively code them."),
            ("Build the hierarchy", "Organize behavior into 10 top-level actions, 46 subactions, and 120 grounded leaf descriptions."),
            ("Validate annotation", "Use human annotators and an LLM pipeline that labels held-out trajectories while quoting supporting trace spans."),
            ("Support extension", "Release the repository, automated analysis tool, and protocol for adding domain categories without losing top-level comparability.")
        ],
        "findings": [
            ("Automated labels are reasonably consistent", "The paper reports Cohen's kappa above 0.81 at every level between the pipeline and human coding."),
            ("Agents acquire behavioral profiles", "Retrieval, planning, evaluation, and reflection distributions can be aggregated across trajectories to compare scaffolds and tasks."),
            ("Leaf combinations expose precursors", "Completion claims combined with missing verification and ignored feedback can describe a specific submit-without-verifying pattern."),
            ("A taxonomy is not a root cause", "It describes what happens and what co-occurs, but cannot alone assign failure to the model, environment, memory, tool policy, or task.")
        ],
        "audits": [
            ("Strong evidence", "The construction process and codebook are public, and automated labels remain grounded in quoted trace evidence."),
            ("Main limitation", "The initial 565 descriptions reflect the agent types, English tasks, and failures already emphasized by the literature."),
            ("Automation risk", "An LLM annotator can mistake explanatory language for behavior, and changing commercial APIs can shift labels."),
            ("Proper scope", "This is behavior interpretability and observability: an upstream layer for mechanistic hypotheses, not a circuit explanation.")
        ],
        "connection": "Your coding-agent work begins where this paper stops: a taxonomy becomes valuable only when indicators predict future failure or efficiency and guide useful interventions. Your long-horizon and context-efficiency indicators can map onto ACT·ONOMY while preserving domain-specific leaves.",
        "questions": [
            ("Why not let a strong LLM summarize every trace?", "Free summaries change granularity and vocabulary across samples. A fixed taxonomy enables statistics and version comparison, while quoted spans preserve auditability."),
            ("Does kappa above 0.81 make the categories objectively true?", "No. It shows agreement under a codebook, not completeness, predictive power, or causality."),
            ("When should a new category be added?", "When many grounded examples consistently fall outside the codebook, or when one existing leaf merges behaviors that require different interventions.")
        ],
    },
    "traceprobe": {
        "zh": "What Resolve Rate Hides About the Process",
        "question": "When two coding agents both pass or both fail, how can we compare who reached relevant code earlier, wasted more work, or first diverged from a successful trajectory?",
        "verdict": "TraceProbe normalizes traces into nine actions, detects per-run anti-patterns with Insight, and aligns same-task runs with Converge. Process metrics complement resolve rate, but most anti-patterns are difficulty clues rather than per-run root causes.",
        "context": [
            "Resolve rate is a low-bandwidth outcome: it hides irrelevant search, reverted patches, and accidental success after expensive retries.",
            "TraceProbe preserves auditable structure instead of creating another opaque total score: what each action did, what effect it had, and where two runs on the same task diverged."
        ],
        "method": [
            ("Normalize", "Map heterogeneous search, read, edit, test, and reasoning events to nine canonical actions with deterministic effect labels."),
            ("Insight", "Apply frozen rules for search loops, verification skips, unsupported completion, and related single-trajectory anti-patterns."),
            ("Converge", "Align a candidate run with a resolved run of the same task and localize divergence at file, function, edit-stability, and completion levels."),
            ("Evaluate", "Analyze 2,500 SWE-Bench Verified trajectories from five production settings, including task controls and transfer tests.")
        ],
        "findings": [
            ("Search loops are the most stable warning", "Many patterns rise with task difficulty and do not explain an individual failure; search loops remain comparatively stable after threshold freezing and transfer."),
            ("File-level analysis is too coarse", "Successful and failed runs often open the same files. Function selection, surviving edits, and unresolved dead ends better localize divergence."),
            ("Resolved runs differ in quality", "At equal outcomes, some agents reach relevant code early while others accumulate failed work, cost, and latency."),
            ("Diagnostics are not causal oracles", "The authors explicitly frame TraceProbe as a source of inspection priorities and failure hypotheses, not a replacement for resolve rate or root-cause proof.")
        ],
        "audits": [
            ("Strong evidence", "The study uses production traces, same-task and same-outcome controls, frozen thresholds, and reference-sensitivity checks."),
            ("Main limitation", "SWE-Bench tests, scaffolds, and telemetry shape the labels; transfer beyond this software-engineering setting remains limited."),
            ("Metric paradox", "A pattern may be more frequent in failed runs simply because hard tasks make agents run longer; task and length controls are essential."),
            ("Next experiment", "Turn stable patterns into interventions such as loop breakers or forced verification and measure matched-task success, cost, and side effects.")
        ],
        "connection": "This paper is closest to your StepFun experience. It gives precise language for why indicators must be validated: distinguish difficulty signals, early failure predictors, and actionable causes, then compare their hit rates across models rather than narrating selected traces.",
        "questions": [
            ("Why do traces matter at equal resolve rate?", "Deployment also cares about tokens, latency, recovery, reproducibility, and risk. Equal outcomes can hide very different process quality."),
            ("Are rules inferior to an LLM judge?", "Rules are limited but auditable and stable across versions; LLM judges are flexible but drift. Use rules for core metrics and LLMs for candidate discovery and explanation."),
            ("How would you prove a search loop is causal?", "Change the search policy or add a loop breaker on matched tasks, then measure success, time to relevant code, and unintended conservatism.")
        ],
    },
    "latent-programming-horizons": {
        "zh": "Does an Agent Anticipate Code Before It Writes It?",
        "question": "Does the residual stream at each coding-agent step encode the current program's real state, and even the consequences of edits that have not happened yet?",
        "verdict": "Linear probes decode compilation, test outcomes, progress, and regressions, with full-correctness AUC up to 0.83. Future program properties remain predictable about 25 steps ahead. This establishes decodability, not causal use by the agent.",
        "context": [
            "Behavioral traces tell us what an agent did. This paper aligns residual streams from long, real-repository editing trajectories with program states verified by external execution.",
            "Its latent programming horizon asks whether the present hidden state predicts properties k steps in the future. That may reflect planning, but it may also reveal current progress, task difficulty, or policy inertia."
        ],
        "method": [
            ("Collect trajectories", "Run two open-weight models with mini-swe-agent on SWE-Bench Verified and Pro, yielding 22,714 trajectories over 1,231 tasks."),
            ("Extract states", "Record residual-stream vectors across Transformer layers at every agent step and align them with the checked-out code version."),
            ("Create external labels", "Run parsers and tests to label well-formedness, full correctness, partial correctness, and regression."),
            ("Train horizon probes", "Fit logistic regressions for current properties and k=1…50 future states, with shuffled-label controls and cross-benchmark transfer.")
        ],
        "findings": [
            ("Current program state is linearly decodable", "Full correctness reaches AUC 0.83 and partial correctness about 0.84; well-formedness is near chance on Verified because labels are highly imbalanced."),
            ("Signal peaks in middle layers", "Across models, datasets, and properties, an inverted-U pattern appears: weak early layers, a middle-layer peak, then a small final-layer decline."),
            ("Representations transfer across benchmarks", "Full and partial-correctness probes retain roughly 0.63-0.78 AUC without retraining, typically dropping only 0.04-0.09."),
            ("Future edits are predictable now", "Signal decays with horizon but remains above chance to roughly 25 steps, consistent with either planning or trajectory-level confounds.")
        ],
        "audits": [
            ("Strong evidence", "Labels come from real compilation and tests, with large samples, shuffled controls, layer sweeps, and cross-benchmark transfer."),
            ("Main limitation", "Only two models, one mini-swe-agent scaffold, and two SWE benchmarks are studied; frontier closed models may differ."),
            ("Core causal gap", "Probe AUC shows readable information. The model may never use the probe direction to choose actions; steering is explicitly left for future work."),
            ("Main confound", "Future success can be predicted from proximity to completion, task difficulty, or trajectory length. Matched-prefix and time-to-go controls are needed.")
        ],
        "connection": "This is a direct bridge for your work: define external labels from StepFun failure patterns, find hidden features that predict context inefficiency or false completion early, then intervene with FLAS or local steering. The full loop is behavior diagnosis, representation localization, and causal control.",
        "questions": [
            ("Does AUC 0.83 mean the agent knows the code is correct?", "It means a linear reader can recover correlated information. Knowledge and use require an intervention that changes editing, testing, or submission behavior."),
            ("Could the 25-step horizon be task difficulty?", "Yes. Compare multiple seeds within the same task and matched prefixes with equal current tests and remaining steps, then residualize obvious progress signals."),
            ("What is the cleanest next experiment?", "Before a risky edit, steer a regression probe or SAE feature and test whether the agent verifies or changes the edit without merely becoming globally conservative.")
        ],
    },
    "reasoning-is-latent": {
        "zh": "What Is the Right Object of Study for Reasoning?",
        "question": "When chain of thought improves performance, is the cause visible text, a latent-state trajectory, or simply more serial computation?",
        "verdict": "The author proposes latent-state trajectories as the default object of study, without declaring surface CoT irrelevant. H1/H2/H0 force experiments to separate latent state, visible trace, and serial compute. This is a research agenda, not decisive single-paper evidence.",
        "context": [
            "Comparing CoT with no CoT changes token count, iterations, and hidden-state evolution at once. Conversely, reading information with a probe does not show that the model uses it.",
            "The paper's main value is to cast three common explanations as competing, falsifiable hypotheses rather than camps."
        ],
        "method": [
            ("H2: Surface mediation", "Explicit CoT carries reasoning; under matched compute, changing the trace should reliably change answers and preserving it should rescue behavior."),
            ("H0: Compute null", "Benefits mainly come from serial compute, search, or sampling. Another intermediate representation with the same budget should recover most gains."),
            ("H1: Latent mediation", "Task-relevant hidden-state trajectories are the main mediator; latent commitments can precede or diverge from verbalized thought and support direct intervention."),
            ("Three-arm comparison", "Ideal studies manipulate surface S, latent Z, and budget B separately and specify in advance which outcome discriminates among them.")
        ],
        "findings": [
            ("H1 is proposed as the default working hypothesis", "Surface CoT is often incomplete, hidden states can predict behavior early, and latent interventions sometimes change outcomes directly."),
            ("H2 still holds in constitutive regimes", "When an external system forces later execution of an explicit plan, retrieval step, or formal proof, the trace becomes operational state rather than display text."),
            ("H0 is strong in search-heavy tasks", "Sampling, backtracking, and token budget can themselves improve performance; unmatched compute makes both CoT and latent methods difficult to interpret."),
            ("The contribution is falsifiable design", "Every experiment should state which of S, Z, and B it changes and seek outcomes that support one explanation while weakening another.")
        ],
        "audits": [
            ("Value", "It provides a useful reviewer checklist: whenever reasoning improves, ask whether surface form, latent dynamics, and compute moved together."),
            ("Evidence level", "This is a position paper and literature synthesis. Its title is stronger than its evidence; it does not prove that reasoning is never in CoT."),
            ("Conceptual difficulty", "Surface tokens alter later hidden states, so S and Z are not orthogonal; latent interventions can also change effective computation."),
            ("How to use it", "Treat H1/H2/H0 as experimental tools. Different tasks, scaffolds, and supervision regimes may occupy different regions.")
        ],
        "connection": "It gives FLAS and agent interpretability a clean framing: compare surface prompt or CoT interventions, matched-compute baselines, and activation-trajectory interventions. A latent-mechanism claim is strongest only when FLAS wins at equal token and sampling budgets.",
        "questions": [
            ("Why should the title not be repeated as fact?", "The paper itself allows local H2 and H0 regimes and largely synthesizes prior work. The precise claim is that H1 is a useful default working hypothesis."),
            ("How should serial compute be matched?", "Control generated tokens, forward passes, samples, tool calls, and compute or wall-clock cost; report cache and parallelism differences as well."),
            ("Where does FLAS fit?", "FLAS is a Z intervention. Compare it with matched-norm fixed steering, equal-token CoT prompting, and a pure decoding-budget baseline.")
        ],
    },
}


def e(value: str) -> str:
    return escape(value, quote=True)


def shell(
    title: str,
    description: str,
    body: str,
    *,
    canonical: str,
    mech_prefix: str,
    root_prefix: str,
    extra_class: str = "",
) -> str:
    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script>(function(){{try{{var p=new URLSearchParams(location.search).get('lang');var l=(p==='cn'||p==='en')?p:(localStorage.getItem('site-lang')||'en');document.documentElement.dataset.lang=l;document.documentElement.lang=l==='cn'?'zh-CN':'en';}}catch(e){{}}}})();</script>
  <meta name="description" content="{e(description)}">
  <meta name="author" content="Zehao Jin">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(canonical)}">
  <title>{e(title)}</title>
  <link rel="icon" href="{root_prefix}static/assets/jzh.ico">
  <link rel="stylesheet" href="{mech_prefix}static/style.css?v=20260815c">
</head>
<body class="{e(extra_class)}">
  <div class="reading-progress" aria-hidden="true"></div>
  <header class="site-bar">
    <a class="brand" href="{mech_prefix}"><strong><span class="lang-cn">MechInterp 论文学习笔记</span><span class="lang-en">MechInterp Paper Study Notes</span></strong></a>
    <nav class="site-nav" aria-label="Site navigation"><a href="{root_prefix}"><span class="lang-cn">个人主页</span><span class="lang-en">Homepage</span></a><a href="{root_prefix}blog/">Blog</a><a href="{mech_prefix}"><span class="lang-cn">论文解读</span><span class="lang-en">Paper notes</span></a><button class="lang-toggle" data-language-toggle type="button" aria-label="Switch language">中文</button></nav>
  </header>
{body}
  <footer class="paper-footer"><span class="lang-cn">Zehao Jin · MechInterp 论文学习笔记 · 原文、解释与证据等级分开</span><span class="lang-en">Zehao Jin · MechInterp Paper Study Notes · Separating sources, interpretation, and evidence</span></footer>
  <script src="{mech_prefix}static/site.js?v=20260815c"></script>
</body>
</html>"""


def index_page() -> str:
    cards = []
    for paper in sorted(PAPERS, key=lambda item: item["date"], reverse=True):
        track_name, _, tone = TRACKS[paper["track"]]
        english = EN[paper["slug"]]
        search = " ".join([paper["title"], paper["zh"], english["zh"], track_name, *paper["tags"]]).lower()
        tags = "".join(f'<span class="tag">{e(tag)}</span>' for tag in paper["tags"][:3])
        cards.append(f"""
        <article class="paper-card" data-paper data-track="{e(paper['track'])}" data-search="{e(search)}" style="--tone:{tone}">
          <div class="evidence-spine" aria-hidden="true"></div>
          <div class="card-body">
            <div class="card-meta"><span>{e(track_name)}</span><span>{e(paper['date'][:4])}</span><span>{e(paper['venue'])}</span></div>
            <h3><a href="papers/{e(paper['slug'])}/"><span class="lang-cn">{e(paper['zh'])}</span><span class="lang-en">{e(english['zh'])}</span></a></h3>
            <p class="lang-cn">{e(paper['verdict'])}</p><p class="lang-en">{e(english['verdict'])}</p>
            <div class="card-bottom"><div class="tags">{tags}</div><a class="read-link" href="papers/{e(paper['slug'])}/"><span class="lang-cn">阅读 {e(paper['time'])} →</span><span class="lang-en">Read · {e(paper['time'])} →</span></a></div>
          </div>
        </article>""")
    body = f"""
  <main class="index-wrap">
    <section class="index-hero">
      <div>
        <div class="eyebrow">Reasoning · Agency · Internal Mechanisms</div>
        <h1 class="lang-cn">MechInterp<br>论文学习笔记</h1><h1 class="lang-en">MechInterp<br>Paper Study Notes</h1>
        <p class="lead lang-cn">面向研究与面试的论文解读。每篇都从问题、实验、证据和边界出发；不把漂亮的 trace 当作真实思维，也不把可解码的信息当作因果机制。</p>
        <p class="lead lang-en">Paper explainers for research and interviews. Each note starts from the question, experiment, evidence, and boundary: a persuasive trace is not necessarily thought, and decodable information is not necessarily a causal mechanism.</p>
      </div>
      <aside class="legend-board" aria-label="Evidence levels">
        <p class="lang-cn">按研究真正观察的对象分类，而不是按论文自己使用的术语分类。</p><p class="lang-en">Grouped by what a study actually observes, not by the label it gives itself.</p>
        <div class="legend">
          <div style="--tone:var(--clay)"><i></i><span><b>Surface trace</b><small class="lang-cn">文字推理是否一致、是否影响答案</small><small class="lang-en">Whether written reasoning is consistent and causal</small></span></div>
          <div style="--tone:var(--sage)"><i></i><span><b>Behavioral trajectory</b><small class="lang-cn">Agent 如何搜索、编辑与失败</small><small class="lang-en">How an agent searches, edits, and fails</small></span></div>
          <div style="--tone:var(--blue)"><i></i><span><b>Latent state</b><small class="lang-cn">隐藏状态表示什么，干预后是否改变行为</small><small class="lang-en">What hidden states encode and causally control</small></span></div>
        </div>
      </aside>
    </section>
    <section class="library" aria-labelledby="library-title">
      <div class="library-head"><div><div class="eyebrow">{len(PAPERS):02d} close readings</div><h2 id="library-title"><span class="lang-cn">论文解读</span><span class="lang-en">Paper explainers</span></h2></div><input class="search" data-search data-placeholder-cn="搜索 CoT、Agent、probe…" data-placeholder-en="Search CoT, Agent, probe…" type="search" placeholder="Search CoT, Agent, probe…" aria-label="Search papers"></div>
      <div class="filters" role="group" aria-label="Filter by research object">
        <button class="filter" data-filter="all" aria-pressed="true"><span class="lang-cn">全部</span><span class="lang-en">All</span></button>
        <button class="filter" data-filter="reasoning" aria-pressed="false">Reasoning faithfulness</button>
        <button class="filter" data-filter="behavior" aria-pressed="false">Agent behavior</button>
        <button class="filter" data-filter="latent" aria-pressed="false">Latent mechanism</button>
        <button class="filter" data-filter="position" aria-pressed="false">Research agenda</button>
      </div>
      <div class="paper-grid">{''.join(cards)}</div>
      <div class="empty lang-cn" data-empty>没有匹配的论文。试试更短的关键词。</div><div class="empty lang-en" data-empty>No matching paper. Try a shorter keyword.</div>
    </section>
  </main>"""
    return shell(
        "MechInterp Paper Study Notes · MechInterp 论文学习笔记",
        "Bilingual paper explainers on reasoning faithfulness, agent trajectories, and latent-state mechanisms.",
        body,
        canonical="https://zehaojin.com/mechinterp/",
        mech_prefix="./",
        root_prefix="../",
        extra_class="index-page",
    )


def section(section_id: str, label: str, title: str, content: str) -> str:
    return f'<section class="section" id="{section_id}"><div class="section-label">{e(label)}</div><h2>{e(title)}</h2>{content}</section>'


def paragraphs(items: list[str]) -> str:
    return "".join(f"<p>{e(item)}</p>" for item in items)


def render_article(data: dict, suffix: str, tone: str, is_en: bool) -> tuple[str, str]:
    method = "".join(
        f'<div class="method-step"><b>{idx:02d}</b><div><strong>{e(title)}</strong><span>{e(text)}</span></div></div>'
        for idx, (title, text) in enumerate(data["method"], 1)
    )
    findings = "".join(f'<div class="finding"><b>{e(title)}</b><p>{e(text)}</p></div>' for title, text in data["findings"])
    audits = "".join(f'<div class="audit" style="--tone:{tone}"><b>{e(title)}</b><p>{e(text)}</p></div>' for title, text in data["audits"])
    questions = "".join(f'<details><summary>{e(question)}</summary><p>{e(answer)}</p></details>' for question, answer in data["questions"])
    if is_en:
        headings = [
            ("question", "01 · Research question", "What is the paper actually asking?", f'<div class="question-box"><p>{e(data["question"])}</p></div>{paragraphs(data["context"])}'),
            ("method", "02 · Method", "How does the experiment make it testable?", f'<div class="method-flow">{method}</div>'),
            ("findings", "03 · Findings", "Results worth remembering", findings),
            ("audit", "04 · Evidence audit", "What the evidence supports - and what it does not", f'<div class="audit-grid">{audits}</div>'),
            ("connection", "05 · Research connection", "Why this matters for my research", f'<div class="takeaway"><b>ZEHAO&#39;S RESEARCH THREAD</b><p>{e(data["connection"])}</p></div>'),
            ("questions", "06 · Interview drill", "If the interviewer pushes further", f'<div class="questions">{questions}</div>'),
        ]
    else:
        headings = [
            ("question", "01 · Research question", "论文到底在问什么", f'<div class="question-box"><p>{e(data["question"])}</p></div>{paragraphs(data["context"])}'),
            ("method", "02 · Method", "实验是怎样把问题变得可检验的", f'<div class="method-flow">{method}</div>'),
            ("findings", "03 · Findings", "真正值得记住的结果", findings),
            ("audit", "04 · Evidence audit", "证据到了哪一层，哪里还没到", f'<div class="audit-grid">{audits}</div>'),
            ("connection", "05 · Research connection", "它为什么与你有关", f'<div class="takeaway"><b>ZEHAO&#39;S RESEARCH THREAD</b><p>{e(data["connection"])}</p></div>'),
            ("questions", "06 · Interview drill", "如果面试官继续追问", f'<div class="questions">{questions}</div>'),
        ]
    toc = "".join(f'<a href="#{sid}-{suffix}">{e(title)}</a>' for sid, _, title, _ in headings)
    article = "".join(section(f"{sid}-{suffix}", label, title, content) for sid, label, title, content in headings)
    return toc, article


def paper_page(paper: dict) -> str:
    track_name, track_object, tone = TRACKS[paper["track"]]
    english = EN[paper["slug"]]
    citation = f"{paper['authors']} ({paper['date'][:4]}). {paper['title']}. arXiv:{paper['arxiv']}."
    toc_cn, article_cn = render_article(paper, "cn", tone, False)
    toc_en, article_en = render_article(english, "en", tone, True)
    body = f"""
  <div class="paper-layout" style="--tone:{tone}">
    <aside class="paper-side"><a class="back" href="../../"><span class="lang-cn">← 返回论文解读</span><span class="lang-en">← Back to paper notes</span></a><div class="toc-label">ON THIS PAGE</div><nav class="toc lang-cn">{toc_cn}</nav><nav class="toc lang-en">{toc_en}</nav></aside>
    <main class="paper-main">
      <div class="paper-kicker"><span>{e(track_name)}</span><span>{e(track_object)}</span><span>{e(paper['venue'])}</span><span>{e(paper['date'])}</span></div>
      <h1><span class="lang-cn">{e(paper['zh'])}</span><span class="lang-en">{e(english['zh'])}</span></h1>
      <p class="paper-subtitle">{e(paper['title'])}</p>
      <div class="authors">{e(paper['authors'])}<div class="paper-actions"><a href="https://arxiv.org/abs/{e(paper['arxiv'])}" target="_blank" rel="noopener"><span class="lang-cn">原论文 ↗</span><span class="lang-en">Original paper ↗</span></a><button data-copy-citation="{e(citation)}"><span class="lang-cn">复制引用</span><span class="lang-en">Copy citation</span></button><button onclick="window.print()"><span class="lang-cn">打印 / PDF</span><span class="lang-en">Print / PDF</span></button></div></div>
      <div class="abstract-card lang-cn"><strong>30 秒结论</strong><p>{e(paper['verdict'])}</p></div><div class="abstract-card lang-en"><strong>30-SECOND TAKE</strong><p>{e(english['verdict'])}</p></div>
      <div class="lang-cn">{article_cn}</div><div class="lang-en">{article_en}</div>
    </main>
    <aside class="paper-rail"><div class="depth-card"><b>READING DEPTH</b><div class="lang-cn"><button data-depth="#question-cn">3 分钟 · 问题与结论</button><button data-depth="#method-cn">8 分钟 · 方法与结果</button><button data-depth="#audit-cn">深读 · 证据审计</button></div><div class="lang-en"><button data-depth="#question-en">3 min · Question and claim</button><button data-depth="#method-en">8 min · Method and results</button><button data-depth="#audit-en">Deep read · Evidence audit</button></div></div><div class="evidence-note"><span class="lang-cn">证据对象：<strong>{e(track_object)}</strong><br>页面把作者结论与本站审计分开呈现。</span><span class="lang-en">Evidence object: <strong>{e(track_object)}</strong><br>Author claims and editorial audit are presented separately.</span></div></aside>
  </div>"""
    return shell(
        f"{paper['title']} · MechInterp Paper Study Notes",
        english["verdict"],
        body,
        canonical=f"https://zehaojin.com/mechinterp/papers/{paper['slug']}/",
        mech_prefix="../../",
        root_prefix="../../../",
        extra_class="paper-page",
    )


def build() -> None:
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for paper in PAPERS:
        out = ROOT / "papers" / paper["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(paper_page(paper), encoding="utf-8")
    print(f"Built index + {len(PAPERS)} paper pages in {ROOT}")


if __name__ == "__main__":
    build()
