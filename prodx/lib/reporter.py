import classifier as classifier


def report(dataset,text):  
    accuarcy, precision = classifier.build_model(dataset)

    print("Model has been built")
    print("Accuracy: ",accuarcy)
    
    print("Predicting.....")
    classifier.classify(text)
    