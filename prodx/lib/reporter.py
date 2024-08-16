from.classifier import build_model,classify


def report(dataset,text):  
    accuarcy, precision = build_model(dataset)

    print("Model has been built")
    print("Accuracy: ",accuarcy)
    
    print("Predicting.....")
    classify(text)
    