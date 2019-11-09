from minitools.picture.ziru import Ziru

if __name__ == '__main__':
    image = "4983571602.png"
    trainSet = "4983571602.txt"
    Ziru.createTrainingSet(image)

    test_image = '9635804271.png'
    ziru = Ziru(trainSet)
    with open(test_image, 'rb') as f:
        print(ziru.get_price(f.read()))
