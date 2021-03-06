'''
Based on pytorch Imagenet example
from https://github.com/pytorch/examples/blob/master/imagenet/main.py
'''

from __future__ import print_function
import argparse
import os
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
from tqdm import tqdm
import random
import numpy as np

class ImageNet_Resnet18(torch.nn.Module):
    def __init__(self):
        super(ImageNet_Resnet18, self).__init__()
        self.model = torch.hub.load(
            "pytorch/vision:v0.6.0",
            "resnet18",
            pretrained=False,
	    num_classes=200,
        )

    def forward(self, input_data):
        return self.model(input_data)


class ImageNet_Resnet34(torch.nn.Module):
    def __init__(self):
        super(ImageNet_Resnet34, self).__init__()
        self.model = torch.hub.load(
            "pytorch/vision:v0.6.0",
            "resnet34",
            pretrained=False,
	    num_classes=200,
        )

    def forward(self, input_data):
        return self.model(input_data)


class ImageNet_Resnet50(torch.nn.Module):
    def __init__(self):
        super(ImageNet_Resnet50, self).__init__()
        self.model = torch.hub.load(
            "pytorch/vision:v0.6.0",
            "resnet50",
            pretrained=False,
	    num_classes=200,
        )

    def forward(self, input_data):
        return self.model(input_data)

class ImageNet_Resnet101(torch.nn.Module):
    def __init__(self):
        super(ImageNet_Resnet101, self).__init__()
        self.model = torch.hub.load(
            "pytorch/vision:v0.6.0",
            "resnet101",
            pretrained=False,
	    num_classes=200,
        )

    def forward(self, input_data):
        return self.model(input_data)

class ImageNet_Resnet152(torch.nn.Module):
    def __init__(self):
        super(ImageNet_Resnet152, self).__init__()
        self.model = torch.hub.load(
            "pytorch/vision:v0.6.0",
            "resnet152",
            pretrained=False,
	    num_classes=200,
        )

    def forward(self, input_data):
        return self.model(input_data)

def train(args, model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    tic = time.perf_counter()
    with tqdm(desc="Training", total=len(train_loader.dataset)) as pbar:
        training_loss_sum = 0.0
        processed_samples = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            training_loss_sum += loss.item()
            processed_samples += len(data)
            if processed_samples > 2000 or batch_idx == len(train_loader)-1: # to make update speed similar regardless of different batch sizes
                pbar.update(processed_samples)
                pbar.set_postfix_str("Training loss: %.3f" % (loss.item() / len(data)))
                processed_samples = 0
        pbar.set_postfix_str("Training loss: %.3f" % (training_loss_sum / len(train_loader.dataset))) # average loss of this epoch
    toc = time.perf_counter()
    print('Elapsed time of this training epoch: {:.3f}s'.format(toc-tic))

def test(model, device, test_loader, criterion):
    model.eval()
    tic = time.perf_counter()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    toc = time.perf_counter()
    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.1f}%)'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    print('Elapsed time of this testing: {:.3f}s\n'.format(toc-tic))


def main():
    parser = argparse.ArgumentParser(description='PyTorch ImageNet sample experiment')
    parser.add_argument('--data', metavar='DIR', required=True, help='path to tiny-imagenet-200 dataset directory')
    parser.add_argument('--batch_size', type=int, default=128, metavar='N',
                        help='input batch size for training (default: 128)')
    parser.add_argument('--test_batch_size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=10, metavar='N',
                        help='number of epochs to train (default: 10)')
    parser.add_argument('--lr', type=float, default=0.1, metavar='LR',
                        help='learning rate (default: 0.1)')
    parser.add_argument('--no_cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument("--gpu_num", default='0', metavar='N', help="gpu number (default: 0)")
    parser.add_argument("--model", default="resnet18", choices=MODEL_MAP.keys(), help="model")
    args = parser.parse_args()
    
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_num

    use_cuda = not args.no_cuda and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    random.seed(42)
    np.random.seed(42)

    print('Device: {}'.format(device))
    if use_cuda:
        print('VGA {}: {}\n'.format(int(args.gpu_num), torch.cuda.get_device_name()))

    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 2,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)
    
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    
    train_set = datasets.ImageFolder(
        os.path.join(args.data, 'train'),
        transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ]))
    test_set = datasets.ImageFolder(
        os.path.join(args.data, 'val'),
        transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize,
        ]))
    
    train_loader = torch.utils.data.DataLoader(train_set,**train_kwargs)
    test_loader = torch.utils.data.DataLoader(test_set, **test_kwargs)

    model = MODEL_MAP[args.model]().to(device)
    criterion = nn.CrossEntropyLoss(reduction='sum')
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=0.7)

    for epoch in range(1, args.epochs + 1):
        print("Training epoch {}".format(epoch))
        train(args, model, device, train_loader, optimizer, criterion, epoch)
        test(model, device, test_loader, criterion)
        scheduler.step()

MODEL_MAP = {
    "resnet18": ImageNet_Resnet18,
    "resnet34": ImageNet_Resnet34,
    "resnet50": ImageNet_Resnet50,
    "resnet101": ImageNet_Resnet101,
    "resnet152": ImageNet_Resnet152,
}

if __name__ == '__main__':
    main()
