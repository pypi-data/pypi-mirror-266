import torch
from torch import nn
from torch.nn import functional as F


class FinClipLoss(nn.Module):
    def __init__(self):
        pass
    
    def get_ground_truth(self, device, num_logits) -> torch.Tensor:
        pass
    
    
    def get_logits(self, ts_features, text_features, logit_scale):
        pass
    
    def forward(
        self, 
        ts_features: torch.Tensor, 
        text_features: torch.Tensor, 
        logit_scale: torch.Tensor, 
        output_dict: bool = False
    ):
        device = ts_features.device
        logits_per_ts, logits_per_text = self.get_logits(ts_features, text_features, logit_scale)

        labels = self.get_ground_truth(device, logits_per_ts.shape[0])

        total_loss = (
            F.cross_entropy(logits_per_ts, labels) +
            F.cross_entropy(logits_per_text, labels)
        ) / 2

        return {"contrastive_loss": total_loss} if output_dict else total_loss
    
    
__all__ = [
    'FinClipLoss',
]
