# go-admin 自定义错误中间件 `CustomError` 加载与执行机制详解

本文说明 `CustomError` 中间件在 go-admin 中的注入位置、加载流程与执行逻辑，并结合源码给出调用链与常见问题提示。

## 概述
- 目标：统一捕获请求处理中发生的 `panic`，转为结构化 JSON 响应；支持自定义错误码与消息。
- 中间件实现：见 [go-admin/common/middleware/customerror.go](go-admin/common/middleware/customerror.go)。

## 加载与注入位置
`CustomError` 在应用启动时作为全局中间件被注入到 Gin 引擎：

- 中间件初始化入口： [go-admin/common/middleware/init.go](go-admin/common/middleware/init.go)

```go
func InitMiddleware(r *gin.Engine) {
    // ... 其他中间件
    // 自定义错误处理
    r.Use(CustomError)
    // ... 其他中间件
}
```

- 路由与引擎初始化： [go-admin/cmd/api/server.go](go-admin/cmd/api/server.go#L186)

```go
func initRouter() {
    // 获取或创建 *gin.Engine
    // ... 省略
    // 注入通用与业务中间件
    common.InitMiddleware(r)
}
```

结论：`CustomError` 在应用启动时被全局 `Use`，因此对所有进入引擎的请求生效，且执行顺序位于其注册位置之后的中间件与处理器之前的 `recover` 保护层。

## 执行机制详解
执行逻辑见 [go-admin/common/middleware/customerror.go](go-admin/common/middleware/customerror.go)：

```go
func CustomError(c *gin.Context) {
    defer func() {
        if err := recover(); err != nil {
            // 若已提前 Abort，则返回 200 空状态（兼容部分流程）
            if c.IsAborted() { c.Status(200) }
            switch errStr := err.(type) {
            case string:
                // 支持 "CustomError#<status>#<message>" 格式的自定义错误
                p := strings.Split(errStr, "#")
                if len(p) == 3 && p[0] == "CustomError" {
                    statusCode, e := strconv.Atoi(p[1])
                    if e != nil { break }
                    c.Status(statusCode)
                    // 打印日志（时间、方法、URL、IP、消息等）
                    // 响应体规范化：code=自定义状态码，msg=自定义消息
                    c.JSON(http.StatusOK, gin.H{ "code": statusCode, "msg": p[2] })
                } else {
                    // 普通字符串错误：统一按 500 返回
                    c.JSON(http.StatusOK, gin.H{ "code": 500, "msg": errStr })
                }
            case runtime.Error:
                // 运行时错误：按 500 返回
                c.JSON(http.StatusOK, gin.H{ "code": 500, "msg": errStr.Error() })
            default:
                // 其他类型：继续抛出，由上层处理（避免吞掉未知类型）
                panic(err)
            }
        }
    }()
    // 继续链路，交由后续中间件与处理器
    c.Next()
}
```

- 关键点：
  - 采用 `defer` + `recover` 捕获下游（后续中间件、处理器）抛出的异常。
  - 自定义错误协议：抛出 `panic("CustomError#<httpStatus>#<message>")` 可精准控制响应的 `code` 与 `msg`。
  - 统一响应：不论状态码如何，HTTP 层以 `200 OK` 返回，业务码在 `code` 字段中体现（这符合该项目的统一返回规范）。
  - 非协议字符串与 `runtime.Error` 统一按 `500` 处理；未知类型错误则原样抛出，避免误吞错误。

## 调用链与时序
- 全局注册：`r.Use(CustomError)` 在引擎上注册为首层错误保护中间件之一。
- 请求进入：Gin 按注册顺序执行中间件。
- 下游执行：后续中间件与控制器逻辑若出现 `panic`，由 `CustomError` 的 `recover` 捕获。
- 响应返回：根据协议或默认逻辑输出统一 JSON，结束请求或继续（视是否 `panic`）。

## 使用建议与注意事项
- 抛出自定义错误：在业务中需要自定义业务码与消息时，使用：

```go
panic("CustomError#403#无权限访问")
```

- 与其他中间件的关系：
  - `AuthCheckRole`、`PermissionAction` 等授权/数据范围中间件位于 `CustomError` 之后执行；其内部若抛出 `panic`，会被统一捕获并格式化返回。
  - 若某中间件或处理器显式 `c.Abort()` 并返回，`CustomError` 会设置 `200` 状态且不再覆盖响应体。

- 返回规范：HTTP 层固定 200，业务码与提示在 JSON `code` 与 `msg` 字段中；前端或调用方需以 `code` 判定业务状态。

## 参考文件
- 自定义错误中间件： [go-admin/common/middleware/customerror.go](go-admin/common/middleware/customerror.go)
- 中间件统一初始化： [go-admin/common/middleware/init.go](go-admin/common/middleware/init.go)
- 服务器路由初始化： [go-admin/cmd/api/server.go](go-admin/cmd/api/server.go)
