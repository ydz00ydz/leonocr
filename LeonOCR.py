import uvicorn
from fastapi import FastAPI, Body
import base64
import ddddocr
from io import BytesIO
from PIL import Image
import logging

'''
pip install uvicorn
pip install fastapi
pip install base64
pip install ddddocr
手动测试时，base64数据得把开头的"data:image/jpeg;base64,"删掉
'''

app = FastAPI(title='OCR开发文档', description='通用验证码识别-Leon', version="1.0.0")


@app.post("/general_captcha", summary='识别图片内文字', description='普通图片验证码识别，上传图片的Base64编码', tags=['图片验证码识别'])
async def general_captcha(ImageBase64: str = Body(..., title='验证码图片Bse64文本', embed=True)):
    try:
        base64_data = base64.b64decode(ImageBase64)
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = ocr.classification(base64_data)
        return {"code": 200, "result": res}
    except Exception as ex:
        logging.exception(ex)
        return {"code": 500, "msg": str(ex)}


@app.post("/arithmetic_captcha", summary='识别算术验证码', description='算术题验证码识别，上传图片的Base64编码，提供两个返回，自行取值分割文本并识别',
          tags=['图片验证码识别'])
async def arithmetic_captcha(ImageBase64: str = Body(..., title='验证码图片Bse64文本', embed=True)):
    try:
        base64_data = base64.b64decode(ImageBase64)
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = ocr.classification(base64_data)

        zhi = "Calculation error"
        if "+" or '-' or 'x' or '/' not in res:
            zhi = "Calculation error"
        if '+' in res:
            zhi = int(res.split('+')[0]) + int(res.split('+')[1][:-1])
        if '-' in res:
            zhi = int(res.split('-')[0]) - int(res.split('-')[1][:-1])
        if 'x' in res:
            zhi = int(res.split('x')[0]) * int(res.split('x')[1][:-1])
        if 'X' in res:
            zhi = int(res.split('X')[0]) * int(res.split('X')[1][:-1])
        if '÷' in res:
            zhi = int(res.split('÷')[0]) / int(res.split('÷')[1][:-1])

        return {"code": 200,
                "solution_result": zhi,
                "raw_result": res
                }
    except Exception as ex:
        logging.exception(ex)
        return {"code": 500, "msg": str(ex)}


@app.post("/slide_alone_gap", summary='缺口为滑动的单独图片，返回坐标', description='识别模型1：缺口图片为单独图片', tags=['滑块验证码识别'])
async def slide_alone_gap(Gap_ImageBase64: str = Body(..., title='滑块缺口图片的Bse64文本', embed=True),
                          Background_ImageBase64: str = Body(..., title='背景图片的Bse64文本', embed=True)):
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.slide_match(base64.b64decode(Gap_ImageBase64), base64.b64decode(Background_ImageBase64),
                          simple_target=True)
    return {"result": res}


@app.post("/slide_comparison", summary='缺口原图和完整原图识别，无单独滑动的缺口图片，返回坐标', description='识别模型2：一张为有缺口原图，一张为完整原图',
          tags=['滑块验证码识别'])
async def slide_comparison(HaveGap_ImageBase64: str = Body(..., title='拥有缺口图片的Bse64文本', embed=True),
                           Full_ImageBase64: str = Body(..., title='完整背景图片的Bse64文本', embed=True)):
    ocr = ddddocr.DdddOcr(det=False, ocr=False)
    res = ocr.slide_comparison(base64.b64decode(HaveGap_ImageBase64), base64.b64decode(Full_ImageBase64))
    return {"result": res}


@app.post("/click_word", summary='文字点选验证码识别，返回坐标', description='点选识别返回坐标', tags=['点选类验证码'])
async def click_word(ClickChoice_ImageBase64: str = Body(..., title='点选图片的Base64编码', embed=True)):
    ocr1 = ddddocr.DdddOcr(show_ad=False)
    ocr2 = ddddocr.DdddOcr(det=True, show_ad=False)

    res = ocr2.detection(base64.b64decode(ClickChoice_ImageBase64))
    if __name__ == '__main__':
        img = Image.open(BytesIO(base64.b64decode(ClickChoice_ImageBase64)))
        res = ocr2.detection(base64.b64decode(ClickChoice_ImageBase64))
        result = {}
        for box in res:
            x1, y1, x2, y2 = box

            result[ocr1.classification(img.crop(box))] = [x1 + ((y1 - x1) // 2), x2 + ((y2 - x2) // 2)]  # 文字位置

    return {"result": result}


if __name__ == '__main__':
    print('''
                    开发文档：http://localhost:6688/docs
    ''')

    uvicorn.run(app, port=6688, host="0.0.0.0")
