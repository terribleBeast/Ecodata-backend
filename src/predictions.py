import numpy as np
import torch
from torchvision import io
from torchvision import transforms as T
from torchvision.models import resnet50

dict_weights = torch.load(
    "D:\\projects\\EcoData\\backend\\models\\best_val_loss_model_ckpt.pth",
    weights_only=False,
    # map_location="cpu",
)
model = resnet50(weights=None)
model.fc = torch.nn.Linear(2048, 2)
model.load_state_dict(dict_weights["model_state_dict"])
img_shape = 224
imges = [
    "D:\\Downloads\\Image_1002 (1).jpg",
    "D:\\Downloads\\Image_997.jpg",
    "D:\\Downloads\\Image_1000.jpg",
    "D:\\Downloads\\Image_1007.jpg",
]
read_imgs = [io.read_image(img_path, mode=io.ImageReadMode.RGB) for img_path in imges]

# print(img_file)

# img_np = np.fromstring(img, dtype=np.uint8)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()


def image_preprocessing(image):
    pipeline = T.Compose(
        [
            T.Resize(img_shape),
            # T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    return pipeline(image)


def get_prediction(image):
    prep_img = image_preprocessing(image / 255.0)
    prep_img = torch.unsqueeze(prep_img, dim=0).to(device)
    outputs = model(prep_img)
    probs = torch.softmax(outputs, dim=1)
    return probs


# print(img_file.shape)
# for img in read_imgs:
#     print(get_prediction(img))
