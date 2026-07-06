"""Export routes for generating markdown study documents."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from services.export_service import (
    generate_single_exam,
    generate_cross_year,
    generate_gap_prediction,
    save_export,
    list_exports,
)

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/single-exam")
async def export_single_exam(exam_year: str = ""):
    """Generate single exam walkthrough markdown."""
    try:
        content = generate_single_exam(exam_year)
        filename = f"{exam_year or '历年'}真题讲解.md"
        save_export(filename, content)
        return JSONResponse(content={"filename": filename, "content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/cross-year")
async def export_cross_year():
    """Generate cross-year comparison + cheat sheet."""
    try:
        content = generate_cross_year()
        filename = "跨卷速记卡.md"
        save_export(filename, content)
        return JSONResponse(content={"filename": filename, "content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/gap-prediction")
async def export_gap_prediction(year: str = ""):
    """Generate gap prediction for next exam."""
    try:
        content = generate_gap_prediction(year)
        filename = f"补漏预测_{year or '下次'}.md"
        save_export(filename, content)
        return JSONResponse(content={"filename": filename, "content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/download/{filename:path}")
async def download_export(filename: str):
    """Download a generated markdown file."""
    from services.export_service import EXPORT_DIR
    filepath = EXPORT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(str(filepath), filename=filename, media_type="text/markdown; charset=utf-8")


@router.get("/list")
async def list_export_files():
    """List all exported files."""
    exports = list_exports()
    return JSONResponse(content={"exports": exports})
