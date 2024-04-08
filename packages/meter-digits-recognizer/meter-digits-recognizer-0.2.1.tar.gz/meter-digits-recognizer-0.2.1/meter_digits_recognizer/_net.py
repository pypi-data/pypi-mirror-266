import PIL
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

__all__ = ["Net"]


class Net(nn.Module):
    test_transform = transforms.Compose([
        transforms.ToTensor()
    ]) 

    if hasattr(transforms, "InterpolationMode"):
        interp_kwargs = dict(interpolation=transforms.InterpolationMode.BILINEAR)
    else:
        interp_kwargs = dict(resample=PIL.Image.BILINEAR)
    train_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.ColorJitter(brightness=0.1),
        transforms.RandomAffine(5.0,  translate=(0.1, 0.1), scale=(1.0, 1.2),
            ),
    ])

    def __init__(self):
        nn.Module.__init__(self)
        self.n_filters1 = 32
        self.n_filters2 = self.n_filters1
        self.n_filters3 = 2 * self.n_filters1
        self.n_filters4 = 2 * self.n_filters1
        self.n_filters5 = 4 * self.n_filters1
        self.n_filters6 = 4 * self.n_filters1
        self.n_fc_input = 2 * 4 * self.n_filters6
        self.input_size = (20, 32)


        self.conv1 = nn.Conv2d(3, self.n_filters1, 3, padding=1, bias=False)
        self.batchnorm1 = nn.BatchNorm2d(self.n_filters1)
        self.conv2 = nn.Conv2d(self.n_filters1, self.n_filters2, 3, padding=1, bias=False)
        self.batchnorm2 = nn.BatchNorm2d(self.n_filters2)
        self.pool1 = nn.MaxPool2d(2, 2) # 10, 16

        self.conv3 = nn.Conv2d(self.n_filters2, self.n_filters3, 3, padding=1, bias=False)
        self.batchnorm3 = nn.BatchNorm2d(self.n_filters3)
        self.conv4 = nn.Conv2d(self.n_filters3, self.n_filters4, 3, padding=1, bias=False)
        self.batchnorm4 = nn.BatchNorm2d(self.n_filters4)
        self.pool2 = nn.MaxPool2d(2, 2) # 5, 8

        self.conv5 = nn.Conv2d(self.n_filters4, self.n_filters5, 3, padding=1, bias=False)
        self.batchnorm5 = nn.BatchNorm2d(self.n_filters5)
        self.conv6 = nn.Conv2d(self.n_filters5, self.n_filters6, 3, padding=1, bias=False)
        self.batchnorm6 = nn.BatchNorm2d(self.n_filters6)
        self.pool3 = nn.MaxPool2d(2, 2) # 2, 4

        self.drop = nn.Dropout(p=0.4)
        self.fc = nn.Linear(self.n_fc_input, 11)

    def forward(self, x):
        x = F.relu(self.batchnorm1(self.conv1(x)))
        x = F.relu(self.batchnorm2(self.conv2(x)))
        x = self.pool1(x)
        
        x = F.relu(self.batchnorm3(self.conv3(x)))
        x = F.relu(self.batchnorm4(self.conv4(x)))
        x = self.pool2(x)

        x = F.relu(self.batchnorm5(self.conv5(x)))
        x = F.relu(self.batchnorm6(self.conv6(x)))
        x = self.pool3(x)
    
        x = x.view(-1, self.n_fc_input)
        x = self.fc(self.drop(x))
        return x
