import torch
from torchvision import transforms
from .net.cast_net import vgg, ADAIN_Encoder, Decoder
import numpy as np
import os

WEIGHT_AE_PATH = os.path.join(os.path.dirname(__file__), 'checkpoint/latest_net_AE.pth')
WEIGHT_DEC_CONTENT_PATH = os.path.join(os.path.dirname(__file__), 'checkpoint/latest_net_Dec_A.pth')
WEIGHT_DEC_STYLE_PATH = os.path.join(os.path.dirname(__file__), 'checkpoint/latest_net_Dec_B.pth')
RESIZE_VALUE = 256

class CAST():
    def __init__(self):
        # create model
        self.encoder = ADAIN_Encoder(vgg)
        self.decoder_content = Decoder()
        self.decoder_style = Decoder()
        # load weights
        self.encoder.load_state_dict(torch.load(WEIGHT_AE_PATH))
        self.decoder_content.load_state_dict(torch.load(WEIGHT_DEC_CONTENT_PATH))
        self.decoder_style.load_state_dict(torch.load(WEIGHT_DEC_STYLE_PATH))
        # change to eval mode
        self.encoder.eval()
        self.decoder_content.eval()
        self.decoder_style.eval()
    
    def transform(self, contents, styles, same_shape=False, preserve_content=True, preserve_style=True):
        if not preserve_style:
            resize = transforms.Resize((RESIZE_VALUE, RESIZE_VALUE))
            tensors_styles = torch.stack([resize(torch.from_numpy(style).permute(2,0,1).float())/127.5 - 1 for style in styles])
        else:
            min_size = np.min([style.shape[0:2] for style in styles], axis=0)
            resize = transforms.Resize((min_size[0], min_size[1]))
            tensors_styles = torch.stack([resize(torch.from_numpy(style).permute(2,0,1).float())/127.5 - 1 for style in styles])
        if not same_shape:
            results = []
            for content in contents:
                tensors_contents = torch.unsqueeze(torch.from_numpy(content).permute(2,0,1).float()/127.5 - 1, 0)
                height, width = tensors_contents.shape[2], tensors_contents.shape[3]
                if not preserve_content:
                    ratio = RESIZE_VALUE / max(tensors_contents.shape[1], tensors_contents.shape[2])
                    resize_height, resize_width = int(height * ratio), int(width * ratio)
                    tensors_contents = transforms.Resize((resize_height, resize_width))(tensors_contents)
                feats_contents = self.encoder(tensors_contents, tensors_styles)
                result = self.decoder_style(feats_contents)[0]
                result = transforms.Resize((height, width))(result)
                result = result.clamp(-1.0, 1.0).detach().float().numpy()
                result = ((result + 1) / 2.0 * 255.0).astype(np.uint8).transpose(1,2,0)
                results.append(result)
        else:
            if not preserve_content:
                height, width = tensors_contents.shape[2], tensors_contents.shape[3]
                ratio = RESIZE_VALUE / max(tensors_contents.shape[1], tensors_contents.shape[2])
                resize_height, resize_width = int(height * ratio), int(width * ratio)
                tensors_contents = transforms.Resize((resize_height, resize_width))(tensors_contents)
            tensors_contents = torch.from_numpy(np.array(contents)).permute(0, 3, 1, 2).float()/127.5 - 1
            feats_contents = self.encoder(tensors_contents, tensors_styles)
            results = self.decoder_style(feats_contents)
            if not preserve_content:
                results = transforms.Resize((height, width))(results)
            results = results.clamp(-1.0, 1.0).detach().float().numpy()
            results = ((results + 1) / 2.0 * 255.0).astype(np.uint8).transpose(0, 2, 3, 1)
        return results


if __name__ == '__main__':
    from PIL import Image
    input_dir = os.path.join(os.path.dirname(__file__), 'image/content/')
    style_dir = os.path.join(os.path.dirname(__file__), 'image/style/')
    output_dir = os.path.join(os.path.dirname(__file__), 'image/result/')
    files = os.listdir(input_dir)

    content = [np.array(Image.open(os.path.join(input_dir, name))) for name in files]
    style = [np.array(Image.open(os.path.join(style_dir, 'fauvism.jpg')))]

    cast = CAST()
    result = cast.transform(content, style, preserve_content=True, preserve_style=True)
    for index, name in enumerate(files):
        Image.fromarray(result[index]).save(os.path.join(output_dir, 'cast_'+name))