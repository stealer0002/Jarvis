"""
File system operation tools
For reading, writing, and managing files and directories
"""

import os
import shutil
from pathlib import Path
from core.tools import tool


@tool(
    name="read_file",
    description="Lê o conteúdo de um arquivo de texto. Use para ler documentos, código, configurações, etc.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho completo do arquivo a ler"
            },
            "encoding": {
                "type": "string",
                "description": "Encoding do arquivo (padrão: utf-8)"
            }
        },
        "required": ["path"]
    }
)
def read_file(path: str, encoding: str = "utf-8") -> dict:
    """Read content from a text file."""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return {"success": False, "error": f"Arquivo não encontrado: {path}"}
        
        if not file_path.is_file():
            return {"success": False, "error": f"Não é um arquivo: {path}"}
        
        content = file_path.read_text(encoding=encoding)
        return {
            "success": True,
            "path": str(file_path.absolute()),
            "size": len(content),
            "content": content
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="write_file",
    description="Escreve conteúdo em um arquivo. Cria o arquivo se não existir, substitui se existir.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho completo do arquivo a escrever"
            },
            "content": {
                "type": "string",
                "description": "Conteúdo a escrever no arquivo"
            },
            "append": {
                "type": "boolean",
                "description": "Se True, adiciona ao final do arquivo em vez de substituir"
            },
            "encoding": {
                "type": "string",
                "description": "Encoding do arquivo (padrão: utf-8)"
            }
        },
        "required": ["path", "content"]
    }
)
def write_file(path: str, content: str, append: bool = False, encoding: str = "utf-8") -> dict:
    """Write content to a file."""
    try:
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = "a" if append else "w"
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        action = "adicionado a" if append else "escrito em"
        return {
            "success": True,
            "action": f"Conteúdo {action} {file_path.name}",
            "path": str(file_path.absolute()),
            "bytes_written": len(content.encode(encoding))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="list_directory",
    description="Lista o conteúdo de uma pasta/diretório.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho da pasta a listar. Use '.' para pasta atual, '~' para home"
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Se True, mostra arquivos ocultos"
            }
        },
        "required": ["path"]
    }
)
def list_directory(path: str, show_hidden: bool = False) -> dict:
    """List contents of a directory."""
    try:
        # Handle special paths
        if path == "~":
            dir_path = Path.home()
        else:
            dir_path = Path(path)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Pasta não encontrada: {path}"}
        
        if not dir_path.is_dir():
            return {"success": False, "error": f"Não é uma pasta: {path}"}
        
        items = []
        for item in dir_path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            item_info = {
                "name": item.name,
                "type": "folder" if item.is_dir() else "file"
            }
            
            if item.is_file():
                try:
                    item_info["size"] = item.stat().st_size
                except:
                    item_info["size"] = 0
            
            items.append(item_info)
        
        # Sort: folders first, then files, alphabetically
        items.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))
        
        return {
            "success": True,
            "path": str(dir_path.absolute()),
            "count": len(items),
            "items": items
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="create_directory",
    description="Cria uma nova pasta/diretório.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho da pasta a criar"
            }
        },
        "required": ["path"]
    }
)
def create_directory(path: str) -> dict:
    """Create a new directory."""
    try:
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "action": f"Pasta criada: {dir_path.name}",
            "path": str(dir_path.absolute())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="delete_file",
    description="Deleta um arquivo ou pasta. CUIDADO: ação irreversível!",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho do arquivo ou pasta a deletar"
            }
        },
        "required": ["path"]
    }
)
def delete_file(path: str) -> dict:
    """Delete a file or directory."""
    try:
        target = Path(path)
        
        if not target.exists():
            return {"success": False, "error": f"Não encontrado: {path}"}
        
        if target.is_file():
            target.unlink()
            return {
                "success": True,
                "action": f"Arquivo deletado: {target.name}"
            }
        else:
            shutil.rmtree(target)
            return {
                "success": True,
                "action": f"Pasta deletada: {target.name}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="move_file",
    description="Move ou renomeia um arquivo ou pasta.",
    parameters={
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "Caminho de origem"
            },
            "destination": {
                "type": "string",
                "description": "Caminho de destino"
            }
        },
        "required": ["source", "destination"]
    }
)
def move_file(source: str, destination: str) -> dict:
    """Move or rename a file or directory."""
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return {"success": False, "error": f"Origem não encontrada: {source}"}
        
        # Create destination parent if needed
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src), str(dst))
        return {
            "success": True,
            "action": f"Movido {src.name} para {dst}",
            "source": str(src.absolute()),
            "destination": str(dst.absolute())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="copy_file",
    description="Copia um arquivo ou pasta para outro local.",
    parameters={
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "Caminho de origem"
            },
            "destination": {
                "type": "string",
                "description": "Caminho de destino"
            }
        },
        "required": ["source", "destination"]
    }
)
def copy_file(source: str, destination: str) -> dict:
    """Copy a file or directory."""
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return {"success": False, "error": f"Origem não encontrada: {source}"}
        
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if src.is_file():
            shutil.copy2(str(src), str(dst))
        else:
            shutil.copytree(str(src), str(dst))
        
        return {
            "success": True,
            "action": f"Copiado {src.name} para {dst}",
            "source": str(src.absolute()),
            "destination": str(dst.absolute())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_file_info",
    description="Retorna informações detalhadas sobre um arquivo.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho do arquivo"
            }
        },
        "required": ["path"]
    }
)
def get_file_info(path: str) -> dict:
    """Get detailed file information."""
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            return {"success": False, "error": f"Não encontrado: {path}"}
        
        stat = file_path.stat()
        
        return {
            "success": True,
            "name": file_path.name,
            "path": str(file_path.absolute()),
            "type": "folder" if file_path.is_dir() else "file",
            "size_bytes": stat.st_size,
            "size_readable": _format_size(stat.st_size),
            "extension": file_path.suffix if file_path.is_file() else None,
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
