# go-admin 权限中间件 `AuthCheckRole` 加载与执行机制详解

本文从代码角度解析 go-admin 中权限中间件 `AuthCheckRole` 的注入、加载与执行流程，并给出调用链时序、注意事项与常见问题排查。

## 概述
- 目标：基于 Casbin 与 JWT 的角色-接口授权校验。
- 关键中间件：`AuthCheckRole()`，定义于 [go-admin/common/middleware/permission.go](go-admin/common/middleware/permission.go)。
- 典型使用：在业务路由组中通过 `.Use(...)` 注入，例如 [go-admin/app/jobs/router/sys_job.go](go-admin/app/jobs/router/sys_job.go)。

## 注入位置与顺序
在业务路由组注册时，`AuthCheckRole` 作为 Gin 中间件被注入到认证链中，一般置于 JWT 中间件之后，以确保已获取到用户的 `claims`。

示例（见 [go-admin/app/jobs/router/sys_job.go](go-admin/app/jobs/router/sys_job.go)）：

```go
r := v1.Group("/sysjob").
    Use(authMiddleware.MiddlewareFunc()).   // JWT，解析并注入用户信息到上下文
    Use(middleware.AuthCheckRole())         // 基于 Casbin 的角色权限校验
```

- 顺序要点：
  - `authMiddleware.MiddlewareFunc()` 在前，负责把 JWT `claims` 写入上下文键 `jwtauth.JwtPayloadKey`。
  - `AuthCheckRole()` 在后，读取 `claims` 中的 `rolekey`，依据 Casbin 策略对当前 `path` + `method` 做访问判断。
  - 业务处理器（或其他如数据范围中间件 `actions.PermissionAction()`）通常在其后执行。

## 加载机制（进入请求时，中间件如何取到依赖对象）
`AuthCheckRole()` 的主体逻辑位于 [go-admin/common/middleware/permission.go](go-admin/common/middleware/permission.go)：

- 获取请求日志器：`api.GetRequestLogger(c)`，用于记录授权流程日志。
- 读取 JWT 载荷：`c.Get(jwtauth.JwtPayloadKey)`，得到 `jwtauth.MapClaims`，其中包含 `rolekey` 等用户角色标识。
- 获取 Casbin Enforcer：`sdk.Runtime.GetCasbinKey(c.Request.Host)`，按 `Host` 维度获取（或创建）对应的 Enforcer，用于 `Enforce()` 决策。
- 排除列表：遍历 `CasbinExclude`，对某些无需校验的接口（按 path + method 匹配）直接跳过授权逻辑。

## 执行流程（请求到达后的判定逻辑）
授权判定的关键路径如下（见 [go-admin/common/middleware/permission.go](go-admin/common/middleware/permission.go)）：

1. 读取 `rolekey`：`v["rolekey"]`。
2. 管理员直通：若 `rolekey == "admin"`，直接 `c.Next()` 放行。
3. 例外接口：若当前 `path`/`method` 命中 `CasbinExclude`，记录日志后 `c.Next()` 放行。
4. 策略校验：调用 `e.Enforce(v["rolekey"], c.Request.URL.Path, c.Request.Method)`。
   - 成功（`true`）：记录允许日志，`c.Next()` 继续后续中间件与处理器。
   - 失败（`false`）：返回 `403` JSON（`{"code": 403, "msg": "对不起，您没有该接口访问权限，请联系管理员"}`），`c.Abort()` 中断后续处理。
5. 异常处理：`Enforce` 过程中出现错误则返回 `500`（`response.Error`），并中止。

## 调用链时序（简化）
- 路由注册：业务路由组 `.Use(JWT).Use(AuthCheckRole).Use(其他中间件)...`。
- 请求进入：Gin 依序执行中间件。
  - JWT：解析令牌 → 把 `claims` 放入上下文（键：`jwtauth.JwtPayloadKey`）。
  - `AuthCheckRole`：读取 `claims.rolekey` → 获取 Enforcer → 排除检查 → `Enforce(role, path, method)` → 决定放行或拦截。
  - 其他（如 `actions.PermissionAction()`）：根据上下文继续数据范围等处理。
- 控制器/处理器：在授权通过后执行具体业务逻辑。

## 与数据范围控制的关系
- 权限校验是“能否进来”问题；数据范围是“进来后能看到多少”问题。
- 常见组合：在受保护接口中同时使用 `AuthCheckRole()` 与 `actions.PermissionAction()`，后者会把 `DataPermission` 写入上下文；查询时通过 `actions.Permission(table, p)` 应用范围约束。相关实现见 [go-admin/common/actions/permission.go](go-admin/common/actions/permission.go)。

## 配置与扩展建议
- Casbin 模型与策略：确保已正确加载模型与策略（按 Host 维度获取 Enforcer），策略中 `rolekey` 与路由的 `path`/`method` 一致。
- 管理员绕过：默认 `admin` 角色全权限，若需收敛可在中间件中调整逻辑。
- 排除列表：维护好 `CasbinExclude`，避免对健康检查、静态资源或登录等接口做不必要授权。
- 中间件顺序：JWT 必须在前，否则 `AuthCheckRole` 读取不到 `claims`。

## 常见问题与自检
- 403 提示但本应有权限：
  - 检查 `rolekey` 是否与策略一致（大小写、空格）。
  - 检查实际 `path` 是否匹配策略中的模式（`util.KeyMatch2` 支持路径模式）。
  - 查看是否被 `CasbinExclude` 误配置或未配置导致校验。
- 500 错误：多为 Enforcer 初始化或策略读取异常；确认 `sdk.Runtime.GetCasbinKey` 的初始化和策略加载。
- 未进入中间件：确认路由组确实 `.Use(middleware.AuthCheckRole())`，且未被其他中间件提前 `Abort`。

## 参考文件
- 中间件实现： [go-admin/common/middleware/permission.go](go-admin/common/middleware/permission.go)
- 业务路由注入示例： [go-admin/app/jobs/router/sys_job.go](go-admin/app/jobs/router/sys_job.go)
- 数据范围中间件： [go-admin/common/actions/permission.go](go-admin/common/actions/permission.go)
