from minitools.picture.ziru import Ziru, ziru

if __name__ == '__main__':
    image = "4983571602.png"
    trainSet = "4983571602.txt"
    Ziru.createTrainingSet(image)
    zr = ziru()

    test_image = '9635804271.png'
    ziru = Ziru(trainSet)
    with open(test_image, 'rb') as f:
        body = f.read()
        print(ziru.get_price(body))
        print(zr.get_price(body))
