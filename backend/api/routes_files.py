"""
文件相关路由
路径: /api/files/*
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import uuid

from models import MarkdownConvertRequest, MarkdownConvertResponse, BatchMarkdownConvertResponse

router = APIRouter(prefix="/api/files", tags=["files"])

# 文件内容存储（简单的内存存储，生产环境应使用数据库或缓存）
file_storage = {}


def get_file_storage() -> dict:
    """获取文件存储实例"""
    return file_storage


@router.post("/parse", response_model=BatchMarkdownConvertResponse)
async def parse_files(files: List[UploadFile] = File(...)):
    """
    批量解析文件为 Markdown
    
    参数:
        files: 上传的文件列表
    
    返回:
        BatchMarkdownConvertResponse 包含所有文件的解析结果
    """
    try:
        print(f"📁 收到 {len(files)} 个文件解析请求")
        
        # 导入 marker 库
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="Marker 库未安装，请运行: pip install marker-pdf"
            )
        
        # 加载模型（只加载一次）
        models = create_model_dict()
        converter = PdfConverter(artifact_dict=models)
        
        results = []
        
        for file in files:
            try:
                print(f"📄 处理文件: {file.filename}")
                
                # 保存临时文件
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    tmp_path = tmp.name
                
                # 转换为 Markdown
                try:
                    rendered = converter(tmp_path)
                    markdown = rendered.markdown
                    metadata = rendered.metadata
                    
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "markdown": markdown,
                        "metadata": metadata,
                        "error": None
                    })
                    
                    print(f"✅ {file.filename} 解析成功")
                
                except Exception as e:
                    print(f"❌ {file.filename} 解析失败: {e}")
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "markdown": "",
                        "metadata": {},
                        "error": str(e)
                    })
                
                finally:
                    # 删除临时文件
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            except Exception as e:
                print(f"❌ {file.filename} 处理失败: {e}")
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "markdown": "",
                    "metadata": {},
                    "error": str(e)
                })
        
        # 为每个成功的文件生成 ID 并存储内容
        for result in results:
            if result.get("success", False):
                file_id = str(uuid.uuid4())
                result["file_id"] = file_id
                
                # 存储文件内容到内存（包含文件名和 markdown 内容）
                file_storage[file_id] = {
                    "filename": result.get("filename", "unknown"),
                    "markdown": result.get("markdown", ""),
                    "metadata": result.get("metadata", {})
                }
            else:
                result["file_id"] = None
        
        # 统计结果
        success_count = sum(1 for r in results if r.get("success", False))
        failed_count = len(results) - success_count
        
        print(f"📊 解析完成: 成功 {success_count}, 失败 {failed_count}")
        
        return BatchMarkdownConvertResponse(
            results=results,
            total=len(results),
            success_count=success_count,
            failed_count=failed_count
        )
    
    except Exception as e:
        print(f"❌ 批量解析错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@router.post("/convert", response_model=MarkdownConvertResponse)
async def convert_file(file: UploadFile = File(...)):
    """
    单个文件转换为 Markdown
    
    参数:
        file: 上传的文件
    
    返回:
        MarkdownConvertResponse 包含转换结果
    """
    try:
        print(f"📄 单文件转换请求: {file.filename}")
        
        # 导入 marker 库
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="Marker 库未安装，请运行: pip install marker-pdf"
            )
        
        # 加载模型
        models = create_model_dict()
        converter = PdfConverter(artifact_dict=models)
        
        # 保存临时文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # 转换为 Markdown
            rendered = converter(tmp_path)
            markdown = rendered.markdown
            metadata = rendered.metadata
            
            # 生成文件 ID 并存储
            file_id = str(uuid.uuid4())
            file_storage[file_id] = {
                "filename": file.filename,
                "markdown": markdown,
                "metadata": metadata
            }
            
            print(f"✅ {file.filename} 转换成功")
            
            return MarkdownConvertResponse(
                filename=file.filename,
                markdown=markdown,
                metadata=metadata,
                file_id=file_id
            )
        
        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        print(f"❌ 文件转换错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"文件转换失败: {str(e)}")


@router.get("/storage/{file_id}")
async def get_file_content(file_id: str):
    """
    获取已存储的文件内容
    
    参数:
        file_id: 文件 ID
    
    返回:
        文件内容
    """
    if file_id in file_storage:
        return file_storage[file_id]
    else:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.delete("/storage/{file_id}")
async def delete_file_content(file_id: str):
    """
    删除已存储的文件内容
    
    参数:
        file_id: 文件 ID
    
    返回:
        删除结果
    """
    if file_id in file_storage:
        del file_storage[file_id]
        return {"message": "文件已删除", "file_id": file_id}
    else:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/storage")
async def list_stored_files():
    """
    列出所有已存储的文件
    
    返回:
        文件列表
    """
    files = [
        {
            "file_id": file_id,
            "filename": data.get("filename", "unknown"),
            "size": len(data.get("markdown", ""))
        }
        for file_id, data in file_storage.items()
    ]
    
    return {
        "files": files,
        "total": len(files)
    }


@router.delete("/storage")
async def clear_all_files():
    """
    清除所有已存储的文件
    
    返回:
        清除结果
    """
    count = len(file_storage)
    file_storage.clear()
    
    return {
        "message": f"已清除 {count} 个文件",
        "cleared_count": count
    }

