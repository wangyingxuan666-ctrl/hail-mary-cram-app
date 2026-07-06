"""Analysis routes for frequency table and strategy."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.exam import FrequencyTable, ExamStrategy, GenerateFrequencyRequest, GenerateStrategyRequest
from services.frequency_analyzer import generate_frequency_table, get_cached_frequency_table
from services.explanation_generator import generate_strategy

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/frequency", response_model=FrequencyTable)
async def analyze_frequency(req: GenerateFrequencyRequest = GenerateFrequencyRequest()):
    """Scan all exam papers and generate a frequency table."""
    try:
        table = await generate_frequency_table(req.course_name)
        if not table.topics:
            raise HTTPException(status_code=400, detail="未找到任何真题。请先上传真题文件。")
        return table
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/frequency", response_model=FrequencyTable)
async def get_frequency():
    """Get the cached frequency table."""
    table = get_cached_frequency_table()
    return table


@router.post("/strategy", response_model=ExamStrategy)
async def analyze_strategy(req: GenerateStrategyRequest = GenerateStrategyRequest()):
    """Generate exam question selection strategy."""
    try:
        freq = get_cached_frequency_table()
        if not freq.topics:
            raise HTTPException(status_code=400, detail="请先生成频率表。")

        strategy_text = await generate_strategy(req.course_name)

        return ExamStrategy(
            questions=[],
            best_combination=strategy_text,
            expected_total="",
            skip_recommendation="",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略生成失败: {str(e)}")


@router.get("/strategy", response_model=ExamStrategy)
async def get_strategy():
    """Get the cached strategy if available."""
    return ExamStrategy()
