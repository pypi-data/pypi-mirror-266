import torchvision
import torch.nn as nn
import torch

def get_model() -> nn.Module:
    mask_rcnn_v2 = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(progress=True,
                                                                         # weights=MaskRCNN_ResNet50_FPN_V2_Weights.COCO_V1,
                                                                         num_classes=4,
                                                                         # weights_backbone=torchvision.models.resnet.ResNet50_Weights.IMAGENET1K_V2,
                                                                         # rpn_nms_thresh=0.9,
                                                                         # box_nms_thresh=0.9,
                                                                         min_size=300,
                                                                         max_size=500)
    return mask_rcnn_v2


def load_model(model: nn.Module, path) -> nn.Module:
    state_dict = torch.load(path, map_location='cpu')
    state_dict = state_dict['model_state_dict'] if 'model_state_dict' in state_dict else state_dict
    model.load_state_dict(state_dict)
    model.eval()
    return model
