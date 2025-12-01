from fastapi import FastAPI, HTTPException
from fastapi_offline import FastAPIOffline
from pydantic import BaseModel
from typing import List, Optional
import csv
import os
from dotenv import load_dotenv
from utils import CommonUtils

# 加载 .env 文件
load_dotenv()

app = FastAPIOffline(
    title="Text Processing API", 
    description="API for text processing with full-width/half-width conversion and number extraction"
)

class TextProcessRequest(BaseModel):
    text: str

class TextProcessResponse(BaseModel):
    result: str

class NumberExtractionResponse(BaseModel):
    numbers: List[float]
    first_int: Optional[int]
    first_float: Optional[float]
    first_str: Optional[str]

class SaveToCsvRequest(BaseModel):
    content: str
    filename: str

@app.get("/")
async def root():
    return {"message": "Text Processing API with FastAPI"}

@app.get("/convert/half-width")
async def convert_to_half_width(text: str):
    """将文本转换为半角字符"""
    try:
        result = CommonUtils.to_half_angle(text)
        return TextProcessResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/convert/full-width")
async def convert_to_full_width(text: str):
    """将文本转换为全角字符"""
    try:
        result = CommonUtils.to_full_angle(text)
        return TextProcessResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/extract/numbers")
async def extract_numbers(text: str):
    """从文本中提取所有数字"""
    try:
        numbers = CommonUtils.extract_numbers(text)
        first_int = CommonUtils.extract_first_number_as_int(text)
        first_float = CommonUtils.extract_first_number_as_float(text)
        first_str = CommonUtils.extract_first_number_as_str(text)
        
        return NumberExtractionResponse(
            numbers=numbers,
            first_int=first_int,
            first_float=first_float,
            first_str=first_str
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/save/csv")
async def save_to_csv(request: SaveToCsvRequest):
    """将内容转换为全角并保存为CSV文件"""
    try:
        full_width_content = CommonUtils.to_full_angle(request.content)
        
        # 从环境变量获取输出路径，默认为 'output'
        output_path = os.getenv('CSV_OUTPUT_PATH', 'output')
        
        # 确保有目录来存储文件
        os.makedirs(output_path, exist_ok=True)
        
        # 定义文件路径
        file_path = os.path.join(output_path, request.filename)
        
        # 写入CSV文件
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # 将全角内容按行分割写入
            lines = full_width_content.split('\n')
            for line in lines:
                writer.writerow([line])
        
        return {"message": "File saved successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)