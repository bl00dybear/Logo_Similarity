import torch

from torchvision import models, transforms
from PIL import Image,ImageStat



class FeatureExtractor:
    def __init__(self, model_name="resnet50"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1) if model_name == "resnet50" else \
            models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)

        # remove last layer (fully connected layer) so that the model returns a feature embedding array
        # eval() prevents changes in parameters of the model
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1]).to(self.device).eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),                                                  # resize at 224x224 px
            transforms.ToTensor(),                                                          # convert image into a PyTorch tensor
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])    # normalize by mean and standard deviation
        ])

    def get_adaptive_background(self, image):
        stat = ImageStat.Stat(image)
        brightness = sum(stat.mean[:3]) / 3

        return (50, 50, 50) if brightness > 128 else (220, 220, 220)

    def preprocess_image(self, image_path):
        try:
            img = Image.open(image_path)

            if img.mode == "P" or img.mode == "LA":                                         # P = palette and LA = grayscale with alpha channel
                img = img.convert("RGBA")

            if img.mode == "RGBA":
                adaptive_bg = self.get_adaptive_background(img.convert("RGB"))
                background = Image.new("RGB", img.size, adaptive_bg)
                background.paste(img, mask=img.split()[3])
                img = background

            img = img.convert("RGB")
            img = img.resize((224, 224))
            return img
        except Exception as e:
            print(f"Error at preprocessing image: {image_path}: {e}")
            return None

    def extract_features(self, image_path):
        try:
            img = self.preprocess_image(image_path)
            if img is None:
                return None

            # convert image into a PyTorch tensor
            # unsqueeze(0) makes [C, H, W] to [N, C, H, W], adds a batch dimension in the beginning
            # because the model expects batch size even if we process a single image
            # .to() move execution to the GPU if possible
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)


            with torch.no_grad():
                features = self.model(img_tensor).squeeze().cpu().numpy()
                # each element in the vector represents the activation of a channel in the final convolutional layer
            return features
        except Exception as e:
            print(f"Error at processing image: {image_path}: {str(e)}")
            return None