# import torch.nn as nn

# class DropPath(nn.Module):
#     """Drop paths (Stochastic Depth) per sample  (when applied in main path of residual blocks)."""

#     def __init__(self, drop_prob=None):
#         super().__init__()
#         self.drop_prob = drop_prob

#     def forward(self, x):
#         return self.drop_path(x, self.drop_prob, self.training)

#     def extra_repr(self):
#         return f"p={self.drop_prob}"

#     def drop_path(x, drop_prob: float = 0., training: bool = False, scale_by_keep: bool = True):
#         """Drop paths (Stochastic Depth) per sample (when applied in main path of residual blocks).

#         This is the same as the DropConnect impl I created for EfficientNet, etc networks, however,
#         the original name is misleading as 'Drop Connect' is a different form of dropout in a separate paper...
#         See discussion: https://github.com/tensorflow/tpu/issues/494#issuecomment-532968956 ... I've opted for
#         changing the layer and argument names to 'drop path' rather than mix DropConnect as a layer name and use
#         'survival rate' as the argument.

#         """
#         if drop_prob == 0. or not training:
#             return x
#         keep_prob = 1 - drop_prob
#         shape = (x.shape[0],) + (1,) * (x.ndim - 1)  # work with diff dim tensors, not just 2D ConvNets
#         random_tensor = x.new_empty(shape).bernoulli_(keep_prob)
#         if keep_prob > 0.0 and scale_by_keep:
#             random_tensor.div_(keep_prob)
#         return x * random_tensor
