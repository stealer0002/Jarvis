"""
Document tools - PDF reading and document processing
"""

from core.tools import tool


@tool(
    name="read_pdf",
    description="Lê o conteúdo de texto de um arquivo PDF. Útil para ler documentos, manuais, relatórios.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho absoluto para o arquivo PDF"
            },
            "max_pages": {
                "type": "integer",
                "description": "Número máximo de páginas para ler (padrão: 10)"
            }
        },
        "required": ["path"]
    }
)
def read_pdf(path: str, max_pages: int = 10) -> dict:
    """Read text content from a PDF file."""
    try:
        from pypdf import PdfReader
        import os
        
        if not os.path.exists(path):
            return {"success": False, "error": f"Arquivo não encontrado: {path}"}
        
        if not path.lower().endswith('.pdf'):
            return {"success": False, "error": "O arquivo deve ter extensão .pdf"}
        
        reader = PdfReader(path)
        total_pages = len(reader.pages)
        pages_to_read = min(max_pages, total_pages)
        
        content = []
        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            if page_text:
                content.append(f"--- Página {i+1} ---\n{page_text}")
        
        full_text = "\n\n".join(content)
        
        return {
            "success": True,
            "path": path,
            "total_pages": total_pages,
            "pages_read": pages_to_read,
            "content": full_text[:10000] if len(full_text) > 10000 else full_text
        }
    except ImportError:
        return {"success": False, "error": "pypdf não instalado. Use: pip install pypdf"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="read_text_file",
    description="Lê o conteúdo de um arquivo de texto (.txt, .md, .json, .csv, etc.).",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Caminho absoluto para o arquivo"
            },
            "encoding": {
                "type": "string",
                "description": "Encoding do arquivo (padrão: utf-8)"
            }
        },
        "required": ["path"]
    }
)
def read_text_file(path: str, encoding: str = "utf-8") -> dict:
    """Read content from a text file."""
    try:
        import os
        
        if not os.path.exists(path):
            return {"success": False, "error": f"Arquivo não encontrado: {path}"}
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return {
            "success": True,
            "path": path,
            "length": len(content),
            "content": content[:10000] if len(content) > 10000 else content
        }
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        try:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
            return {
                "success": True,
                "path": path,
                "encoding_used": "latin-1",
                "length": len(content),
                "content": content[:10000] if len(content) > 10000 else content
            }
        except Exception as e:
            return {"success": False, "error": f"Erro de encoding: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
