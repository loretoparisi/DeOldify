from fastai.core import *
from fastai.torch_core import *
from fastai.vision import *
from fastai.vision.gan import AdaptiveLoss

_conv_args = dict(leaky=0.2, norm_type=NormType.Spectral)

def _conv(ni:int, nf:int, ks:int=3, stride:int=1, **kwargs):
    return conv_layer(ni, nf, ks=ks, stride=stride, **_conv_args, **kwargs)

#TODO:  Merge with fastai core.  Just removed dense block.
def gan_critic2(n_channels:int=3, nf:int=256, n_blocks:int=3, p:int=0.15):
    "Critic to train a `GAN`."
    layers = [
        _conv(n_channels, nf, ks=4, stride=2),
        nn.Dropout2d(p/2)]
    for i in range(n_blocks):
        layers += [
            nn.Dropout2d(p),
            _conv(nf, nf*2, ks=4, stride=2, self_attention=(i==0))]
        nf *= 2
    layers += [
        _conv(nf, 1, ks=4, bias=False, padding=0, use_activ=False),
        Flatten()]
    return nn.Sequential(*layers)

def colorize_crit_learner(data:ImageDataBunch, loss_critic=AdaptiveLoss(nn.BCEWithLogitsLoss()), nf:int=256)->Learner:
    return Learner(data, gan_critic2(nf=nf), metrics=None, loss_func=loss_critic, wd=1e-3)