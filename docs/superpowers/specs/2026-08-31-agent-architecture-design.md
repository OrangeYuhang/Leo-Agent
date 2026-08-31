# "私厨" Agent 管家 — 后端整体架构设计

- 日期: 2026-08-31
- 状态: 已确认(三个部分均经用户逐段确认)
- 范围: 后端 v1 架构设计;前端本轮不做设计,未来形态为多模块仪表盘

## 1. 背景与目标

个人学习 agent 全栈开发的项目("私厨" / Personal Chief),用于个人日常使用。四大能力域(PDD):

1. 个人知识库(RAG)
2. 系统琐事处理
3. 交流对话
4. 协助编码

部署形态为本机单用户,无认证、无多租户。主模型 DeepSeek(架构上 config 可切换)。

## 2. 已确认决策

| 决策点 | 结论 |
|---|---|
| 部署形态 | 本机单用户 |
| 系统琐事 | 有界工具集,agent 不执行任意 shell 命令 |
| 前端 | 本轮不做设计;后续为多模块仪表盘,API 契约即为各模块接口 |
| 主模型 | DeepSeek(`deepseek-chat`),config.json 可切换 |
| 记忆 | sqlite 会话历史 + 向量长期记忆(双轨) |
| 编码辅助 | 只读仓库工具(项目目录白名单) |
| 图片/文件存储 | 本地存储(`resource/uploads/`),删除 oss.py |
| 编排框架 | LangChain `create_agent`(v1);学完 LangGraph 后重构,迁移成本通过分层压到最小 |

## 3. 现状摘要

后端骨架已存在:`main.py`(FastAPI,CORS 全开,挂 `/api/v1` + SPA fallback)→ `api/v1/`(chat 三个端点是 `pass` 桩;oss.py 预签名上传)→ `agent/tools.py`(rag_summarize + web_search 两个工具)→ `rag/`(Chroma 入库/检索 + 总结链)。前端是 B站教程模板(无对接代码),`backend/static/` 是教程残留的 Next.js 占位文件。

关键缺口:无 agent 编排层、chat 端点未实现、无会话持久化、无长期记忆、无知识库管理 API、无测试框架、RAG 层存在类用反等 bug(见第 12 节)。

## 4. 总体架构

```
未来前端(多模块仪表盘)
        │ HTTP / SSE
        ▼
┌─ FastAPI (api/v1/) ──────────────────────────────┐
│  chat.py      聊天流式(SSE)+ 历史 + 清空           │
│  knowledge.py 知识库上传/列表/删除                 │
│  uploads.py   图片/文件本地上传(替换 oss.py)       │
│  tasks.py     待办/提醒 CRUD(仪表盘模块接口)       │
└──────┬───────────────────────────────────────────┘
       ▼
┌─ agent/ 编排层(薄)───────────────────────────────┐
│  skills_loader.py  扫描 skills/ 构建注册表         │
│  agent_factory.py  create_agent(人设+skill说明+工具)│
│  tools/  按域拆分的内置工具注册表                   │
└──────┬───────────────────────────────────────────┘
       ▼
┌─ services/ 服务层(厚,与编排解耦)──────────────────┐
│  rag/            知识库检索总结(现有,迁入)         │
│  memory_service.py  长期记忆(抽取→向量存→检索)     │
│  history_service.py  sqlite 会话消息               │
│  scheduler.py     APScheduler 提醒调度             │
│  system_service.py psutil 系统信息/白名单文件操作   │
│  code_service.py  只读代码仓库操作                 │
└──────┬───────────────────────────────────────────┘
       ▼
resource/  chroma_db  history.db  uploads/  workspace/  prompts/  md5.txt
backend/skills/  各技能自包含目录(SKILL.md + 可选 tools.py)
```

**分层原则(核心):**

- **编排层薄、服务层厚**:`create_agent` 只负责"模型 + prompt + 工具"组装;所有业务逻辑在 services。将来换 LangGraph 只重写 `agent/` 层,`api/`、`services/`、`resource/` 不动。
- **工具即接口**:每个工具背后调一个 service,工具函数只做参数校验、结果格式化和错误转换。未来 supervisor 多 agent 只需把工具重新分组挂到不同 agent 上。
- **API 层不碰业务实现**:只做参数校验与响应包装。

## 5. 一次对话的数据流

1. `POST /chat/stream {message, thread_id}` → `history_service` 载入该会话历史
2. `memory_service` 用当前消息检索长期记忆,把 top-k 相关事实注入 system prompt
3. `create_agent` 循环:模型决策 → 调工具(知识库/搜索/系统/编码/记忆)→ 结果回填 → 直到产出最终回答;token 经 SSE 流式推给前端
4. 会话结束:消息落 sqlite;后台任务从对话中抽取重要事实写入长期记忆库

## 6. Skills 动态注入机制

每个 skill 是 `backend/skills/` 下的自包含目录:

```
skills/
  <skill-name>/
    SKILL.md      # 角色说明 + 触发条件 + 使用步骤(注入 system prompt)
    tools.py      # 可选:该 skill 专属的 @tool 定义
```

- **启动时扫描注册**:`skills_loader.py` 遍历 `skills/` 解析注册表。加新 skill = 加目录,不改核心代码。
- **组装时注入**:系统提示 = 基础人设 + 每个启用 skill 的 SKILL.md 内容;工具列表 = 内置工具 + skill 工具。
- **开关控制**:`config.json` 的 `skills.enabled` 列表。
- **与编排框架正交**:将来换 LangGraph 时 loader 与 skill 目录原样保留。
- v1 不做按需检索注入(工具少,全量注入);工具多时再演进为按语义路由 skill。

v1 交付示例 skill `file-organizer`(扫描目录 + 分类移动,复用 system_service 的白名单文件操作),同时验证 prompt 注入与工具贡献两条路径。

## 7. API 契约

全部挂 `/api/v1` 下。即未来仪表盘各模块的接口。

### chat.py(重写现有桩)

| 端点 | 说明 |
|---|---|
| `POST /chat/stream` | SSE 流式对话。body `{message, image_url?, thread_id}`(`image_url` 保留,v1 DeepSeek 不消费图片,留给未来多模态模型) |
| `GET /chat/messages?thread_id=` | 历史消息列表 |
| `DELETE /chat/messages?thread_id=` | 清空会话 |

SSE 事件协议:

- `event: token` — 增量文本(前端打字机效果)
- `event: tool_start` / `event: tool_end` — 工具调用起止(未来前端显示"agent 正在做…")
- `event: done` — 结束,携带 `message_id`
- `event: error` — 出错

### knowledge.py(新增)

| 端点 | 说明 |
|---|---|
| `POST /knowledge/upload` | multipart 上传 txt/pdf,复用 md5 去重入库逻辑 |
| `GET /knowledge/files` | 已入库文件清单 |
| `DELETE /knowledge/files/{file_hash}` | 删除文件及向量(入库时把 md5 写入 Chroma metadata,删除按 metadata 过滤) |

### uploads.py(替换 oss.py)

| 端点 | 说明 |
|---|---|
| `POST /uploads/image` | 存 `resource/uploads/`,校验扩展名 + 大小上限(10MB),返回本地访问 URL |

### tasks.py(新增;agent 工具与仪表盘共用 service)

| 端点 | 说明 |
|---|---|
| `GET/POST/PATCH/DELETE /tasks` | 待办 CRUD |
| `GET/POST/DELETE /reminders` | 提醒 CRUD |

提醒调度:APScheduler,到期置 `due` 并尝试 Linux 系统通知(`notify-send`),失败仅记日志;服务重启时从 sqlite 恢复未到期提醒。

## 8. 数据层

### SQLite(`resource/history.db`)

| 表 | 字段要点 |
|---|---|
| `threads` | id, title(首条消息截断), created_at, updated_at |
| `messages` | id, thread_id, role(user/assistant), content, tool_calls(JSON), created_at |
| `todos` | id, content, done, created_at, completed_at |
| `reminders` | id, content, remind_at, status(pending/due/dismissed), created_at |

### Chroma(两个 collection,同一 persist_directory)

- `knowledge` — 知识库文档块(现有逻辑迁入,collection 名改为可配置)
- `memory` — 长期记忆事实条目,metadata 含时间戳与来源 thread_id

### 长期记忆流水线(独立于编排层)

- **写入**:对话结束后,后台任务用主模型按固定 prompt(存放于 `resource/prompts/memory_extract_prompt.txt`)抽取"值得长期记住的事实"(偏好、决定、事件),逐条写入 `memory` collection
- **检索**:下次对话开始前,用当前消息检索 top-k 相关事实注入 system prompt
- **显式操作**:agent 可用 `save_memory` / `recall_memory` 工具主动读写

## 9. 工具清单与安全边界

### v1 内置工具(约 12 个,`agent/tools/` 按域分包)

| 域 | 工具 | 说明 |
|---|---|---|
| 知识库 | `knowledge_search(query)` | 现有 rag_summarize 重构,检索+总结 |
| 网络 | `web_search(query)` | 现有 Tavily 保留 |
| 系统 | `get_system_status()` | psutil:磁盘/内存/CPU/时间(只读) |
| 系统 | `list_directory(path?)` / `read_text_file(path)` / `move_file(src, dst)` | 仅限白名单工作目录 |
| 系统 | `add_todo / list_todos / complete_todo` | 待办,与 `/tasks` API 共用 service |
| 系统 | `add_reminder(content, remind_at) / list_reminders` | 提醒,与 `/reminders` API 共用 service |
| 编码 | `list_code_directory / read_code_file / grep_code` | 只读,限定项目白名单 |
| 记忆 | `save_memory(content)` / `recall_memory(query)` | 显式写/查长期记忆 |

### 安全边界(硬性)

- 文件类工具:传入路径 `realpath` 解析后必须落在白名单目录(`resource/workspace/`)内,拒绝 `..` 逃逸
- 编码类工具:只读 + 限定 config 的 `code.projects` 白名单
- **无任意 shell 执行、无任意代码执行** —— 全项目唯一硬边界
- 待办/提醒无危险操作

## 10. 错误处理

- 工具执行失败 → 转成可读字符串返回模型,让模型自行降级/重试/向用户解释;异常不穿透
- 模型调用失败(限流/网络)→ 指数退避重试一次,仍失败走 SSE `error` 事件
- SSE 客户端断开 → 取消生成,已生成部分仍落 sqlite
- FastAPI 全局异常处理器 → 统一 JSON 错误格式 + 日志

## 11. 测试策略

新增 pytest(当前后端零测试)。

- **services 层单测为主**:history CRUD、md5 去重、路径白名单(重点:逃逸用例)、记忆抽取输出解析
- **工具层**:mock 模型,测参数校验与错误转换
- **agent 循环**:stub 模型 + 固定工具做冒烟测试(create_agent 为黑盒,不追求覆盖率)
- 前端 vitest 已有,本轮不碰

## 12. 现有问题修复清单

| 问题 | 修复 |
|---|---|
| config `persist_directory: "/resource/chroma_db"` 前导 `/` 指向文件系统根目录 | 统一走 `get_abs_path`,改 `./resource/chroma_db` |
| config `md5_hex_store: "./resource/md5.text"` 与实际文件 `md5.txt` 不符 | 统一为 `md5.txt` |
| config 键 `summarize_prompt_path` 与 `prompt_loader.py` 读取的 `rag_summarize_prompt_path` 不一致 | 统一键名 |
| config `agent.model` / `embedding_model` / `summarise_model` 为空 | 填默认值:agent 与总结链用 `deepseek-chat`,embedding 用 DashScope `text-embedding-v3`(以账号实际可用为准) |
| `vector_store.py` 把 Tongyi 对话模型当 embedding 函数、`rag_service.py` 把 DashScopeEmbedding 当总结链 LLM —— 类用反,入库/总结实际跑不通 | embedding 用 DashScopeEmbedding,总结链用对话模型(主模型,可配置) |
| `rag_service.py:1` `from rag.vector_store` 缺 `backend.` 前缀 | 迁移时一并修复 |
| `data_path: "data"` 指向不存在的目录 | 明确知识库源文件目录,与上传 API 落地方案对齐 |

## 13. 目录与依赖调整

- `backend/rag/` → 迁入 `backend/services/rag/`
- `backend/agent/tools.py` → 拆为 `backend/agent/tools/{knowledge,web,system,coding,memory}_tools.py`
- 新增 `backend/services/{memory_service,history_service,scheduler,system_service,code_service}.py` 与 `backend/agent/{agent_factory,skills_loader}.py`
- `backend/skills/` 落位 skill 目录机制(含示例 `file-organizer`)
- 删除 `backend/api/v1/oss.py`;`resource/` 下新增 `uploads/`、`workspace/`、`history.db`
- 新增依赖:psutil、APScheduler、pytest(pixi.toml)

## 14. 实现里程碑

| 里程碑 | 内容 | 验收 |
|---|---|---|
| M0 地基修复 | config 修复、`rag/`→`services/rag/` 迁移、导入与类用反修复、pytest 落位 | 入库脚本跑通、检索返回结果 |
| M1 数据层 | sqlite history/todos/reminders + 各 service 骨架 | service 单测通过 |
| M2 最小闭环 | create_agent + SSE 流式 + 历史读写,仅挂 web_search | curl 可流式对话 |
| M3 能力扩展 | 知识库 API、全量工具挂载、长期记忆流水线 | agent 能查知识库/建待办/写记忆 |
| M4 skills + 调度 | skills loader + `file-organizer` 示例 + 提醒调度 | 加新 skill 不改核心代码 |
| M5 收尾 | 实现 uploads.py 本地存储、删 oss.py、文档更新 | 旧 OSS 链路移除干净 |

## 15. 非目标(v1 不做)

- 前端设计(后续多模块仪表盘单独设计)
- 认证/多用户/权限
- LangGraph 重构(学完后再做,架构已预留)
- 任意 shell/代码执行
- skill 按需检索注入(全量注入)
- 图片多模态消费(`image_url` 字段保留但模型不消费)
- 云端部署(OSS 等云依赖本轮移除)

## 16. 演进路线(预留,不在本轮计划内)

1. LangGraph 重构:`agent/` 层替换为状态图,checkpointer 接管会话状态;services/skills 不动
2. supervisor 多 agent:工具按域重新分组挂到专家 agent,主控路由
3. 前端多模块仪表盘:按本文 API 契约逐模块开发
4. 按需 skill 路由:工具增多后改为语义检索注入
5. 多模态:接入支持视觉的模型消费 `image_url`
