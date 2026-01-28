"""
CLI - 命令行工具
dy-yun 企业级中后台应用框架 v0.1
"""
import typer
import uvicorn
from pathlib import Path

app = typer.Typer(help="dy-yun 企业级中后台应用框架 CLI")


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="监听地址"),
    port: int = typer.Option(8000, help="监听端口"),
    reload: bool = typer.Option(False, help="开发模式（热重载）"),
    config: str = typer.Option("config/settings.yaml", "-c", help="配置文件路径"),
):
    """
    启动 API 服务器
    """
    typer.echo(f"🚀 Starting dy-yun ...")
    typer.echo(f"📝 Config: {config}")
    typer.echo(f"🌐 Server will run at: http://{host}:{port}")
    typer.echo(f"📚 API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level="info",
    )


@app.command()
def migrate(
    action: str = typer.Argument(..., help="迁移操作: up, down, init"),
):
    """
    数据库迁移
    """
    typer.echo(f"🔄 Running migration: {action}")
    
    if action == "init":
        typer.echo("Initializing Alembic...")
        import subprocess
        subprocess.run(["alembic", "init", "migrations"])
    elif action == "up":
        typer.echo("Running migrations...")
        import subprocess
        subprocess.run(["alembic", "upgrade", "head"])
    elif action == "down":
        typer.echo("Rolling back migration...")
        import subprocess
        subprocess.run(["alembic", "downgrade", "-1"])
    else:
        typer.echo(f"❌ Unknown action: {action}", err=True)


@app.command()
def version():
    """
    显示版本信息
    """
    typer.echo("dy-yun - 基于 FastAPI企业级中后台应用框架")


@app.command()
def init_db():
    """初始化数据库表（仅用于开发）"""
    import asyncio
    from core import setup_database, create_tables, get_settings
    
    async def run():
        settings = get_settings()
        await setup_database(settings.database)
        await create_tables()
        typer.echo("✅ Database tables created successfully!")
    
    asyncio.run(run())


if __name__ == "__main__":
    app()
