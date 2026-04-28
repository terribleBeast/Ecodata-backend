import numpy as np
import torch
from torchvision import io
from torchvision import transforms as T
from torchvision.models import resnet50

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
img_shape = 224


def load_model(model_name: str):
    dict_weights = torch.load(
        "D:\\projects\\EcoData\\backend\\src\\models\\" + model_name,
        weights_only=False,
        # map_location="cpu",
    )
    model = resnet50(weights=None)
    model.fc = torch.nn.Linear(2048, 2)
    model.load_state_dict(dict_weights["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def image_preprocessing(image):
    pipeline = T.Compose(
        [
            T.Resize(img_shape),
            # T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    return pipeline(image)


def get_prediction(image, model):
    prep_img = image_preprocessing(image / 255.0)
    prep_img = torch.unsqueeze(prep_img, dim=0).to(device)
    outputs = model(prep_img)
    probs = torch.softmax(outputs, dim=1).to("cpu")
    return float(probs[0][1]) * 100
