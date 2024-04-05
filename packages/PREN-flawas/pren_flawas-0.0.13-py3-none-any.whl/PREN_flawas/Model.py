import torch
from PIL import Image

def _init_():
    model_load = torch.jit.load('model/model_scripted.pt')
    model_load.eval()

def visualize_model_predictions(model,img_path):
    was_training = model.training
    model.eval()

    img = Image.open(img_path)
    img = data_transforms['test'](img)
    img = img.unsqueeze(0)
    img = img.to(device)

    with torch.no_grad():
        outputs = model(img)
        _, preds = torch.max(outputs, 1)
        
        detected_label = class_names[preds[0]]
        cubes = detected_label.split("-")

        model.train(mode=was_training)
        return cubes