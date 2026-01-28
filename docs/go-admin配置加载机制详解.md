# go-admin 配置加载机制详解

## 配置加载流程图

```
main.go
  ↓
cmd.Execute()
  ↓
cmd/api/server.go::StartCmd.PreRun → setup()
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1. 注入扩展配置指针                                              │
│    config.ExtendConfig = &ext.ExtConfig                         │
│    // 将业务扩展配置挂载到 SDK 配置系统                          │
└─────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. 调用 SDK 配置初始化                                           │
│    config.Setup(                                                │
│        file.NewSource(file.WithPath(configYml)),  // 配置源     │
│        database.Setup,                             // 回调1     │
│        storage.Setup,                              // 回调2     │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────┐
  │ 2.1 创建 Settings 实例                         │
  │     _cfg = &Settings{                          │
  │         Settings: Config{                      │
  │             Application: ApplicationConfig,    │
  │             Logger: LoggerConfig,              │
  │             Database: DatabaseConfig,          │
  │             Extend: ExtendConfig, // 扩展配置  │
  │             ...                                │
  │         },                                     │
  │         callbacks: [database.Setup, storage.Setup] │
  │     }                                          │
  └────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────┐
  │ 2.2 创建 core/config 对象                      │
  │     config.DefaultConfig = config.NewConfig(   │
  │         config.WithSource(fileSource),         │
  │         config.WithEntity(_cfg),               │
  │     )                                          │
  └────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────────────┐
  │ 2.2.1 初始化配置加载器链                               │
  │       ┌──────────────────────────────────────┐        │
  │       │ File Source (文件源)                 │        │
  │       │ - 读取 config/settings.yml           │        │
  │       │ - 检测文件格式 (yaml/json/toml)      │        │
  │       │ - 返回原始字节数据                    │        │
  │       └────────────┬─────────────────────────┘        │
  │                    ↓                                   │
  │       ┌──────────────────────────────────────┐        │
  │       │ Encoder (编码器)                     │        │
  │       │ - YAML Encoder 解码文件内容           │        │
  │       │ - 转换为中间格式 map[string]interface{} │     │
  │       └────────────┬─────────────────────────┘        │
  │                    ↓                                   │
  │       ┌──────────────────────────────────────┐        │
  │       │ Memory Loader (内存加载器)            │        │
  │       │ - 将数据加载到内存                    │        │
  │       │ - 维护配置快照 (Snapshot)             │        │
  │       │ - 支持多源合并                        │        │
  │       └────────────┬─────────────────────────┘        │
  │                    ↓                                   │
  │       ┌──────────────────────────────────────┐        │
  │       │ JSON Reader (JSON 读取器)             │        │
  │       │ - 将中间格式统一转为 JSON             │        │
  │       │ - 提供路径查询能力 Get("a.b.c")       │        │
  │       │ - 类型转换 (String/Int/Bool...)      │        │
  │       └────────────┬─────────────────────────┘        │
  │                    ↓                                   │
  │       ┌──────────────────────────────────────┐        │
  │       │ Values 接口                          │        │
  │       │ - Scan() 扫描到结构体                 │        │
  │       │ - vals.Scan(&_cfg)                   │        │
  │       └──────────────────────────────────────┘        │
  └────────────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────┐
  │ 2.3 扫描配置到 Settings 结构体                  │
  │     vals.Scan(_cfg)                            │
  │     // 使用反射将配置数据填充到结构体           │
  │     // settings.application.port → ApplicationConfig.Port │
  └────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────┐
  │ 2.4 调用 _cfg.Init()                           │
  │     ├─ Logger.Setup() → 初始化 Zap 日志        │
  │     ├─ multiDatabase() → 处理多数据库配置      │
  │     └─ runCallback() → 执行回调函数            │
  │         ├─ database.Setup() → 初始化 GORM      │
  │         └─ storage.Setup() → 初始化缓存/队列   │
  └────────────────────────────────────────────────┘
       ↓
  ┌────────────────────────────────────────────────┐
  │ 2.5 启动配置监听协程 (go c.run())               │
  │     - 使用 fsnotify 监听文件变化                │
  │     - 文件变更时触发 OnChange()                 │
  │     - 热重载配置（无需重启服务）                │
  └────────────────────────────────────────────────┘
```

---

## 核心组件详解

### 1. 配置文件结构 (settings.yml)

```yaml
settings:                    # 根节点
  application:               # 应用配置
    mode: dev                # 运行模式
    host: 0.0.0.0           # 监听地址
    port: 8000              # 端口
  logger:                    # 日志配置
    path: temp/logs
    level: trace
  database:                  # 数据库配置
    driver: sqlite3
    source: go-admin-db.db
  jwt:                       # JWT 配置
    secret: go-admin
    timeout: 3600
  # ... 其他配置
```

### 2. 配置结构体映射

#### sdk/config/config.go
```go
// 顶层配置容器
type Settings struct {
    Settings  Config `yaml:"settings"`  // 对应 YAML 的 settings 节点
    callbacks []func()                  // 初始化完成后的回调
}

// 配置集合
type Config struct {
    Application *Application          `yaml:"application"`
    Logger      *Logger               `yaml:"logger"`
    Database    *Database             `yaml:"database"`
    Databases   *map[string]*Database `yaml:"databases"` // 多数据库支持
    Jwt         *Jwt                  `yaml:"jwt"`
    Cache       *Cache                `yaml:"cache"`
    Queue       *Queue                `yaml:"queue"`
    Locker      *Locker               `yaml:"locker"`
    Extend      interface{}           `yaml:"extend"`    // 扩展配置
}
```

#### sdk/config/application.go
```go
type Application struct {
    ReadTimeout   int    // 读超时
    WriterTimeout int    // 写超时
    Host          string // 主机
    Port          int64  // 端口
    Name          string // 应用名
    JwtSecret     string // JWT 密钥（废弃，使用 Jwt.Secret）
    Mode          string // 运行模式
    DemoMsg       string // 演示环境提示
    EnableDP      bool   // 启用数据权限
}

// 全局配置对象（预初始化）
var ApplicationConfig = new(Application)
```

### 3. 配置源 (Source) - 文件读取层

#### config/source/file/file.go
```go
type file struct {
    path string          // 文件路径
    opts source.Options  // 选项（包含编码器）
}

func (f *file) Read() (*source.ChangeSet, error) {
    // 1. 打开文件
    fh, err := os.Open(f.path)
    
    // 2. 读取全部内容
    b, err := ioutil.ReadAll(fh)
    
    // 3. 获取文件信息（修改时间）
    info, err := fh.Stat()
    
    // 4. 创建 ChangeSet（变更集）
    cs := &source.ChangeSet{
        Format:    format(f.path, f.opts.Encoder), // yaml/json/toml
        Source:    "file",
        Timestamp: info.ModTime(),
        Data:      b,  // 原始字节数据
    }
    cs.Checksum = cs.Sum()  // 计算校验和（用于检测变更）
    
    return cs, nil
}
```

**format() 函数**：根据文件扩展名确定格式
```go
func format(p string, e encoder.Encoder) string {
    // settings.yml  → yaml
    // settings.json → json
    // settings.toml → toml
}
```

### 4. 编码器 (Encoder) - 格式解析层

支持的编码器：
- **YAML Encoder** (gopkg.in/yaml.v2)
- **JSON Encoder** (encoding/json)
- **TOML Encoder** (github.com/BurntSushi/toml)

```go
// config/encoder/yaml/yaml.go
func (y yamlEncoder) Decode(d []byte, v interface{}) error {
    return yaml.Unmarshal(d, v)  // YAML → map[string]interface{}
}

func (y yamlEncoder) Encode(v interface{}) ([]byte, error) {
    return yaml.Marshal(v)  // map[string]interface{} → YAML
}
```

### 5. 加载器 (Loader) - 内存管理层

#### config/loader/memory/memory.go
```go
type memory struct {
    sets    []*source.ChangeSet  // 所有配置源的变更集
    sources []source.Source      // 配置源列表
    snap    *loader.Snapshot     // 当前快照
    vals    reader.Values        // 当前值
    watchers *list.List          // 观察者列表
}

func (m *memory) Load(source ...source.Source) error {
    // 1. 从每个 Source 读取 ChangeSet
    for _, s := range source {
        cs, err := s.Read()
        m.sets = append(m.sets, cs)
    }
    
    // 2. 合并所有 ChangeSet（如果有多个配置文件）
    set, err := m.opts.Reader.Merge(m.sets...)
    
    // 3. 转换为 Values 接口
    m.vals, _ = m.opts.Reader.Values(set)
    
    // 4. 创建快照
    m.snap = &loader.Snapshot{
        ChangeSet: set,
        Version:   genVer(),  // 生成版本号
    }
    
    return nil
}
```

### 6. 读取器 (Reader) - 数据访问层

#### config/reader/json/json.go
```go
type jsonReader struct {
    opts reader.Options
    json encoder.Encoder  // JSON 编码器
}

func (j *jsonReader) Merge(changes ...*source.ChangeSet) (*source.ChangeSet, error) {
    var merged map[string]interface{}
    
    // 遍历所有变更集
    for _, m := range changes {
        // 1. 根据格式选择编码器（yaml/json/toml）
        codec, ok := j.opts.Encoding[m.Format]
        
        // 2. 解码为 map
        var data map[string]interface{}
        codec.Decode(m.Data, &data)
        
        // 3. 合并到 merged（使用 mergo 库）
        mergo.Map(&merged, data, mergo.WithOverride)
    }
    
    // 4. 统一编码为 JSON
    b, err := j.json.Encode(merged)
    
    // 5. 返回新的 ChangeSet
    return &source.ChangeSet{
        Data:   b,
        Format: "json",  // 统一格式
    }, nil
}

func (j *jsonReader) Values(ch *source.ChangeSet) (reader.Values, error) {
    return newValues(ch)  // 返回 Values 接口实现
}
```

#### config/reader/json/values.go
```go
type jsonValues struct {
    ch   *source.ChangeSet
    smap map[string]interface{}  // 解析后的 JSON 数据
}

// 路径查询
func (j *jsonValues) Get(path ...string) reader.Value {
    // 支持链式查询：Get("settings", "application", "port")
}

// 扫描到结构体
func (j *jsonValues) Scan(v interface{}) error {
    // 使用 JSON 反序列化
    dec := json.NewDecoder(bytes.NewReader(j.ch.Data))
    dec.UseNumber()  // 精确数字处理
    return dec.Decode(v)
}
```

### 7. 配置实体 (Entity) - 业务回调

```go
type Entity interface {
    OnChange()  // 配置变更时调用
}

// Settings 实现了 Entity 接口
func (e *Settings) OnChange() {
    e.init()
    log.Println("config change and reload")
}

func (e *Settings) init() {
    // 1. 重新初始化日志
    e.Settings.Logger.Setup()
    
    // 2. 处理多数据库配置
    e.Settings.multiDatabase()
    
    // 3. 执行注册的回调函数
    e.runCallback()
}
```

---

## 配置热更新机制

### 文件监听器 (Watcher)

#### config/source/file/watcher.go
```go
type watcher struct {
    f       *file
    fw      *fsnotify.Watcher  // fsnotify 文件系统监听器
    exit    chan bool
}

func (w *watcher) Next() (*source.ChangeSet, error) {
    for {
        select {
        case event := <-w.fw.Events:
            if event.Op == fsnotify.Write || event.Op == fsnotify.Rename {
                // 文件被修改或重命名，重新读取
                return w.f.Read()
            }
        case err := <-w.fw.Errors:
            return nil, err
        case <-w.exit:
            return nil, errors.New("watcher stopped")
        }
    }
}
```

### 配置监听协程

#### config/default.go
```go
func (c *config) run() {
    watch := func(w loader.Watcher) error {
        for {
            // 等待配置变更
            snap, err := w.Next()
            
            c.Lock()
            
            // 检查版本（避免重复处理）
            if c.snap.Version >= snap.Version {
                c.Unlock()
                continue
            }
            
            // 更新快照
            c.snap = snap
            
            // 重新解析配置
            c.vals, _ = c.opts.Reader.Values(snap.ChangeSet)
            
            // 扫描到实体
            if c.opts.Entity != nil {
                _ = c.vals.Scan(c.opts.Entity)
                c.opts.Entity.OnChange()  // 触发变更回调
            }
            
            c.Unlock()
        }
    }
    
    // 无限循环监听
    for {
        w, err := c.opts.Loader.Watch()
        if err != nil {
            time.Sleep(time.Second)
            continue
        }
        
        // 阻塞监听
        if err := watch(w); err != nil {
            time.Sleep(time.Second)
        }
    }
}
```

---

## 扩展配置机制

### 业务扩展配置

#### go-admin/config/extend.go
```go
var ExtConfig Extend

type Extend struct {
    AMap AMap  // 自定义配置结构
}

type AMap struct {
    Key string
}
```

### 配置文件示例
```yaml
settings:
  # ... 标准配置
  extend:              # 扩展配置节点
    amap:
      key: your-amap-key
```

### 使用方式
```go
// 1. 在 setup() 中注入
config.ExtendConfig = &ext.ExtConfig

// 2. 在业务代码中使用
import "go-admin/config"

func someFunc() {
    key := config.ExtConfig.AMap.Key
}
```

---

## 初始化回调机制

### 回调注册
```go
config.Setup(
    file.NewSource(file.WithPath(configYml)),
    database.Setup,   // 回调1：初始化数据库
    storage.Setup,    // 回调2：初始化缓存/队列
)
```

### 回调执行时机
1. **首次加载**: `_cfg.Init()` → `runCallback()`
2. **热更新**: `_cfg.OnChange()` → `init()` → `runCallback()`

### 回调示例：数据库初始化

#### common/database/initialize.go
```go
func Setup() {
    // 遍历所有数据库配置
    for k := range toolsConfig.DatabasesConfig {
        setupSimpleDatabase(k, toolsConfig.DatabasesConfig[k])
    }
}

func setupSimpleDatabase(host string, c *toolsConfig.Database) {
    // 1. 读取配置
    log.Infof("%s => %s", host, c.Source)
    
    // 2. 创建 GORM 实例
    db, err := gorm.Open(...)
    
    // 3. 初始化 Casbin 权限引擎
    e := mycasbin.Setup(db, "")
    
    // 4. 注册到 Runtime
    sdk.Runtime.SetDb(host, db)
    sdk.Runtime.SetCasbin(host, e)
}
```

---

## 配置访问方式

### 1. 通过全局配置对象
```go
import "github.com/go-admin-team/go-admin-core/sdk/config"

// 访问应用配置
port := config.ApplicationConfig.Port
host := config.ApplicationConfig.Host

// 访问数据库配置
dbConfig := config.DatabaseConfig.Source

// 访问日志配置
logLevel := config.LoggerConfig.Level
```

### 2. 通过 DefaultConfig 接口
```go
import "github.com/go-admin-team/go-admin-core/config"

// 获取原始配置值
val := config.Get("settings", "application", "port")
portInt := val.Int(8000)  // 默认值 8000

// 获取整个配置 Map
configMap := config.Map()

// 扫描到自定义结构体
var myConfig MyStruct
config.Scan(&myConfig)
```

### 3. 通过 sdk.Runtime
```go
import "github.com/go-admin-team/go-admin-core/sdk"

// 获取数据库实例（通过配置初始化后注册）
db := sdk.Runtime.GetDbByKey("*")

// 获取缓存适配器
cache := sdk.Runtime.GetCacheAdapter()
```

---

## 配置加载时序总结

```
时间线：
T0: main() 启动
T1: cmd/api/server.go::setup() 调用
T2: config.ExtendConfig 注入
T3: config.Setup() 开始
    ├─ T3.1: 创建 File Source
    ├─ T3.2: File Source 读取配置文件
    ├─ T3.3: YAML Encoder 解码
    ├─ T3.4: Memory Loader 加载到内存
    ├─ T3.5: JSON Reader 统一格式
    ├─ T3.6: Values.Scan() 扫描到结构体
    ├─ T3.7: _cfg.Init() 初始化
    │   ├─ Logger.Setup()
    │   ├─ multiDatabase()
    │   └─ runCallback()
    │       ├─ database.Setup()
    │       └─ storage.Setup()
    └─ T3.8: go c.run() 启动监听协程
T4: 配置加载完成，返回到 setup()
T5: run() 启动 Gin 服务器

热更新时序：
T100: 用户修改 settings.yml
T101: fsnotify 检测到文件变更
T102: watcher.Next() 返回新 ChangeSet
T103: c.run() 中的 watch() 处理变更
T104: vals.Scan(&_cfg) 重新扫描
T105: _cfg.OnChange() 触发回调
T106: Logger.Setup() + runCallback() 重新初始化
T107: 配置热更新完成（无需重启服务）
```

---

## 关键设计亮点

### 1. 分层架构
- **Source** - 数据源层（文件、环境变量、远程配置中心）
- **Encoder** - 编码层（支持多种格式）
- **Loader** - 加载层（内存管理、多源合并）
- **Reader** - 读取层（统一访问接口）
- **Entity** - 实体层（业务回调）

### 2. 统一格式转换
所有配置最终转换为 JSON 格式，简化内部处理逻辑。

### 3. 配置热更新
基于 fsnotify 的文件监听 + 观察者模式，实现配置热重载。

### 4. 扩展性
- 支持自定义 Source（如 Etcd、Consul）
- 支持自定义 Encoder（如 HCL）
- 支持扩展配置节点

### 5. 类型安全
通过结构体 Tag 映射 + 反射扫描，确保类型安全。

---

## 常见问题

### Q1: 支持哪些配置文件格式？
**A**: YAML、JSON、TOML，根据文件扩展名自动识别。

### Q2: 如何添加新的配置项？
**A**: 
1. 在 `sdk/config/*.go` 中定义结构体
2. 在 `Config` 结构体中添加字段
3. 在 `Setup()` 中初始化
4. 在配置文件中添加对应节点

### Q3: 配置热更新会影响哪些组件？
**A**: 
- Logger 会重新初始化
- 回调函数会重新执行（database.Setup、storage.Setup）
- 全局配置对象会更新

### Q4: 为什么不用 Viper？
**A**: 
- go-admin-core 自实现了更轻量的配置框架
- 更好的定制化（如多数据库配置）
- 支持配置变更回调机制

### Q5: 多数据库配置如何工作？
**A**:
```yaml
settings:
  databases:
    mysql-master:
      driver: mysql
      source: root:pwd@tcp(127.0.0.1:3306)/db?charset=utf8mb4
    postgres-slave:
      driver: postgres
      source: host=localhost user=postgres dbname=db
```
通过 `sdk.Runtime.GetDbByKey("mysql-master")` 访问。

---

**生成时间**: 2026年1月21日  
**分析版本**: go-admin v2.0.0
