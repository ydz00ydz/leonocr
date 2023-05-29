import ddddocr

ocr = ddddocr.DdddOcr()

with open(r"D:\WorkSpace\Python\LeonOCR\img\6ph9.jfif", 'rb') as f:
    image = f.read()

res = ocr.classification(image)
print(res)