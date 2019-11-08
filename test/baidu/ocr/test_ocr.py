from minitools.baidu.ocr import BaiDuOcr

if __name__ == '__main__':
    ocr = BaiDuOcr()

    with open('1.png', 'rb') as img:
        print(ocr.webImage2word(img.read()))
