from archs import *
from archs.dncnn import DnCNN
from archs.cifar_resnet import resnet as resnet_cifar
from archs.memnet import MemNet
from archs.wrn import WideResNet
import archs.resnet18
from datasets import get_normalize_layer, get_input_center_layer
from torch.nn.functional import interpolate
from torchvision.models.resnet import resnet18, resnet34, resnet50

import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import sys

# Create a fake 'resnet18' module for unpickling
sys.modules['resnet18'] = archs.resnet18


IMAGENET_CLASSIFIERS = [
                        'resnet18', 
                        'resnet34', 
                        'resnet50',
                        ]

CIFAR10_CLASSIFIERS = [
                        'cifar_resnet110', 
                        'cifar_wrn', 'cifar_wrn40',
                        'VGG16', 'VGG19', 'ResNet18','PreActResNet18','GoogLeNet',
                        'DenseNet121','ResNeXt29_2x64d','MobileNet','MobileNetV2',
                        'SENet18','ShuffleNetV2','EfficientNetB0'
                        'imagenet32_resnet110', 'imagenet32_wrn',
                        ]

RESNET_SYNERGY_CLASSIFIERS = [
                        'resnet_normal', 'resnet_negative', 'resnet_hybrid',
                        'resnet_hybrid_neg', 'resnet_synergy_normal', 
                        'resnet_synergy_negative', 'resnet_synergy_all',
                        'resnet_synergy_trained_all'
                        ]

CLASSIFIERS_ARCHITECTURES = IMAGENET_CLASSIFIERS + CIFAR10_CLASSIFIERS

DENOISERS_ARCHITECTURES = ["cifar_dncnn", "cifar_dncnn_wide", "mnist_dncnn", "memnet", # cifar10 denoisers
                            'imagenet_dncnn', 'imagenet_memnet' # imagenet denoisers
                        ]

def get_architecture(arch: str, dataset: str, pytorch_pretrained: bool=False) -> torch.nn.Module:
    """ Return a neural network (with random weights)

    :param arch: the architecture - should be in the ARCHITECTURES list above
    :param dataset: the dataset - should be in the datasets.DATASETS list
    :return: a Pytorch module
    """
    ## ImageNet classifiers
    if arch == "resnet18" and dataset == "imagenet":
        model = torch.nn.DataParallel(resnet18(pretrained=pytorch_pretrained)).cuda()
        cudnn.benchmark = True
    elif arch == "resnet34" and dataset == "imagenet":
        model = torch.nn.DataParallel(resnet34(pretrained=pytorch_pretrained)).cuda()
        cudnn.benchmark = True
    elif arch == "resnet50" and dataset == "imagenet":
        model = torch.nn.DataParallel(resnet50(pretrained=pytorch_pretrained)).cuda()
        cudnn.benchmark = True

    ## Cifar classifiers
    elif arch == "cifar_resnet20":
        model = resnet_cifar(depth=20, num_classes=10).cuda()
    elif arch == "cifar_resnet110":
        model = resnet_cifar(depth=110, num_classes=10).cuda()
    elif arch == "imagenet32_resnet110":
        model = resnet_cifar(depth=110, num_classes=1000).cuda()
    elif arch == "imagenet32_wrn":
        model = WideResNet(depth=28, num_classes=1000, widen_factor=10).cuda()

    ## Resnet Synergy classifiers
    elif arch == "resnet_normal":
        model = ResNet18('normal', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_negative":
        model = ResNet18('negative', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_hybrid":
        model = ResNet18('hybrid_nor', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_hybrid_neg":
        model = ResNet18('hybrid_neg', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_synergy_normal":
        model = ResNet18('synergy_nor', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_synergy_negative":
        model = ResNet18('synergy_neg', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_synergy_all":
        model = ResNet18('synergy_all', num_in_channels=3, num_classes=10).cuda()
    elif arch == "resnet_synergy_trained_all":
        model = ResNet18('tr_synergy_all', num_in_channels=3, num_classes=10).cuda()

    # Cifar10 Models from https://github.com/kuangliu/pytorch-cifar
    # The 14 models we use in the paper as surrogate models 
    elif arch == "cifar_wrn":
        model = WideResNet(depth=28, num_classes=10, widen_factor=10).cuda()
    elif arch == "cifar_wrn40":
        model = WideResNet(depth=40, num_classes=10, widen_factor=10).cuda()
    elif arch == "VGG16":
        model = VGG('VGG16').cuda()
    elif arch == "VGG19":
        model = VGG('VGG19').cuda()
    elif arch == "ResNet18":
        model = ResNet18().cuda()
    elif arch == "PreActResNet18":
        model = PreActResNet18().cuda()
    elif arch == "GoogLeNet":
        model = GoogLeNet().cuda()
    elif arch == "DenseNet121":
        model = DenseNet121().cuda()
    elif arch == "ResNeXt29_2x64d":
        model = ResNeXt29_2x64d().cuda()
    elif arch == "MobileNet":
        model = MobileNet().cuda()
    elif arch == "MobileNetV2":
        model = MobileNetV2().cuda()
    elif arch == "SENet18":
        model = SENet18().cuda()
    elif arch == "ShuffleNetV2":
        model = ShuffleNetV2(1).cuda()
    elif arch == "EfficientNetB0":
        model = EfficientNetB0().cuda()

    ## Image Denoising Architectures
    elif arch == "cifar_dncnn":
        model = DnCNN(image_channels=3, depth=17, n_channels=64).cuda()
        return model
    elif arch == "cifar_dncnn_wide":
        model = DnCNN(image_channels=3, depth=17, n_channels=128).cuda()
        return model
    elif arch == 'mnist_dncnn':
        model = DnCNN(image_channels=1, depth=17, n_channels=64).cuda()
        return model
    elif arch == 'memnet':
        model = MemNet(in_channels=3, channels=64, num_memblock=3, num_resblock=6).cuda()
        return model
    elif arch == "imagenet_dncnn":
        model = torch.nn.DataParallel(DnCNN(image_channels=3, depth=17, n_channels=64)).cuda()
        cudnn.benchmark = True
        return model
    elif arch == 'imagenet_memnet':
        model = torch.nn.DataParallel(MemNet(in_channels=3, channels=64, num_memblock=3, num_resblock=6)).cuda()
        cudnn.benchmark = True
        return model
    else:
        raise Exception('Unknown architecture.')

    normalize_layer = get_normalize_layer(dataset)
    return torch.nn.Sequential(normalize_layer, model)

def load_resnet_synergy(checkpoint: str, dataset: str) -> torch.nn.Module:
    """ Load a ResNet Synergy architecture with pretrained weights if available.
    
    :param checkpoint: path to the checkpoint file
    :param dataset: the dataset - should be in the datasets.DATASETS list
    :return: a Pytorch module with the ResNet Synergy architecture
    """
    model = torch.load(checkpoint, weights_only=False)
    normalize_layer = get_normalize_layer(dataset)
    return torch.nn.Sequential(normalize_layer, model)
  
