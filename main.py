from fastapi import FastAPI, HTTPException
from fastapi_offline import FastAPIOffline
from pydantic import BaseModel
from typing import List, Optional
import csv
import os
import json
from dotenv import load_dotenv
from utils import CommonUtils

# .envファイルを読み込む
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
    """テキストを半角文字に変換する"""
    try:
        result = CommonUtils.to_half_angle(text)
        return TextProcessResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/convert/full-width")
async def convert_to_full_width(text: str):
    """テキストを全角文字に変換する"""
    try:
        result = CommonUtils.to_full_angle(text)
        return TextProcessResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/extract/numbers")
async def extract_numbers(text: str):
    """テキストからすべての数字を抽出する"""
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
    """コンテンツを全角に変換し、CSVファイルとして保存する"""
    try:
        full_width_content = CommonUtils.to_full_angle(request.content)
        
        # 環境変数から出力パスを取得、デフォルトは 'output'
        output_path = os.getenv('CSV_OUTPUT_PATH', 'output')
        
        # ファイルを保存するディレクトリを確認
        os.makedirs(output_path, exist_ok=True)
        
        # ファイルパスを定義
        file_path = os.path.join(output_path, request.filename)
        
        # CSVファイルに書き込む
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # 全角コンテンツを行ごとに分割して書き込む
            lines = full_width_content.split('\n')
            for line in lines:
                writer.writerow([line])
        
        return {"message": "ファイルが正常に保存されました", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getjson")
async def getjson():
    """同じディレクトリにあるsample.csvをJSONファイルに変換して返す"""
    try:
        # CSVファイルパス
        csv_file_path = os.path.join(os.path.dirname(__file__), "sample.csv")
        
        # ファイルが存在するか確認
        if not os.path.exists(csv_file_path):
            raise HTTPException(status_code=404, detail="sample.csvファイルが見つかりません")
        
        # CSVファイルを読み込み、JSONに変換
        data = []
        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            # CSVダイアレクトを検出
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for row in reader:
                data.append(row)
        
        return {"data": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="sample.csvファイルが見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
