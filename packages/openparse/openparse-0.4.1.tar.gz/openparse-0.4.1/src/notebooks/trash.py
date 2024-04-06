from typing import Tuple, List, Sequence, Optional, Union
from pathlib import Path
import re
import torch  # type: ignore
import tokenizers as tk  # type: ignore
from PIL import Image  # type: ignore

from torchvision import transforms  # type: ignore
from torch import nn, Tensor  # type: ignore
from functools import partial
import warnings

from .tabular_transformer import EncoderDecoder, ImgLinearBackbone, Encoder, Decoder
from .utils import (
    subsequent_mask,
    pred_token_within_range,
    greedy_sampling,
    cell_str_to_token_list,
    html_str_to_token_list,
    build_table_from_html_and_cell,
    html_table_template,
    bbox_str_to_token_list,
)
from .tokens import VALID_HTML_TOKEN, VALID_BBOX_TOKEN, INVALID_CELL_TOKEN
from .unitable_model import (
    structure_model,
    structure_vocab,
    bbox_vocab,
    bbox_model,
    cell_vocab,
    cell_model,
)
from .config import device

device = torch.device("cpu")


warnings.filterwarnings("ignore")


def autoregressive_decode(
    model: EncoderDecoder,
    image: Tensor,
    prefix: Sequence[int],
    max_decode_len: int,
    eos_id: int,
    token_whitelist: Optional[list[int]] = None,
    token_blacklist: Optional[list[int]] = None,
) -> Tensor:
    model.eval()
    with torch.no_grad():
        memory = model.encode(image)
        context = (
            torch.tensor(prefix, dtype=torch.int32).repeat(image.shape[0], 1).to(device)
        )

    for _ in range(max_decode_len):
        eos_flag = [eos_id in k for k in context]
        if all(eos_flag):
            break

        with torch.no_grad():
            causal_mask = subsequent_mask(context.shape[1]).to(device)
            logits = model.decode(
                memory, context, tgt_mask=causal_mask, tgt_padding_mask=None  # type: ignore
            )
            logits = model.generator(logits)[:, -1, :]

        logits = pred_token_within_range(
            logits.detach(),
            white_list=token_whitelist,
            black_list=token_blacklist,
        )

        next_probs, next_tokens = greedy_sampling(logits)
        context = torch.cat([context, next_tokens], dim=1)
    return context


def image_to_tensor(image: Image, size: Tuple[int, int]) -> Tensor:
    T = transforms.Compose(
        [
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.86597056, 0.88463002, 0.87491087],
                std=[0.20686628, 0.18201602, 0.18485524],
            ),
        ]
    )
    image_tensor = T(image)
    image_tensor = image_tensor.to(device).unsqueeze(0)

    return image_tensor


def rescale_bbox(
    bbox: Sequence[Sequence[float]], src: Tuple[int, int], tgt: Tuple[int, int]
) -> Sequence[Sequence[float]]:
    assert len(src) == len(tgt) == 2
    ratio = [tgt[0] / src[0], tgt[1] / src[1]] * 2
    bbox = [[int(round(i * j)) for i, j in zip(entry, ratio)] for entry in bbox]
    return bbox


image_path = "/Users/sergey/Developer/experiments/unitable/dataset/mini_pubtabnet/val/PMC2753619_002_00.png"
image = Image.open(image_path).convert("RGB")
image_size = image.size

#################
### STRUCTURE ###
#################


# Image transformation
image_tensor = image_to_tensor(image, size=(448, 448))

# Inference
pred_html = autoregressive_decode(
    model=structure_model,
    image=image_tensor,
    prefix=[structure_vocab.token_to_id("[html]")],
    max_decode_len=512,
    eos_id=structure_vocab.token_to_id("<eos>"),
    token_whitelist=[structure_vocab.token_to_id(i) for i in VALID_HTML_TOKEN],
    token_blacklist=None,
)

# Convert token id to token text
pred_html = pred_html.detach().cpu().numpy()[0]
pred_html = structure_vocab.decode(pred_html, skip_special_tokens=False)
pred_html = html_str_to_token_list(pred_html)


############
### BBOX ###
############


# Image transformation
image_tensor = image_to_tensor(image, size=(448, 448))

# Inference
pred_bbox = autoregressive_decode(
    model=bbox_model,
    image=image_tensor,
    prefix=[bbox_vocab.token_to_id("[bbox]")],
    max_decode_len=1024,
    eos_id=bbox_vocab.token_to_id("<eos>"),
    token_whitelist=[bbox_vocab.token_to_id(i) for i in VALID_BBOX_TOKEN[:449]],
    token_blacklist=None,
)

# Convert token id to token text
pred_bbox = pred_bbox.detach().cpu().numpy()[0]
pred_bbox = bbox_vocab.decode(pred_bbox, skip_special_tokens=False)
# Visualize detected bbox
pred_bbox = bbox_str_to_token_list(pred_bbox)
pred_bbox = rescale_bbox(pred_bbox, src=(448, 448), tgt=image_size)


####################
### CELL CONTENT ###
####################


# Cell image cropping and transformation
image_tensor = [
    image_to_tensor(image.crop(bbox), size=(112, 448)) for bbox in pred_bbox
]
image_tensor = torch.cat(image_tensor, dim=0)


# Inference
pred_cell = autoregressive_decode(
    model=cell_model,
    image=image_tensor,
    prefix=[cell_vocab.token_to_id("[cell]")],
    max_decode_len=200,
    eos_id=cell_vocab.token_to_id("<eos>"),
    token_whitelist=None,
    token_blacklist=[cell_vocab.token_to_id(i) for i in INVALID_CELL_TOKEN],
)

# Convert token id to token text
pred_cell = pred_cell.detach().cpu().numpy()
pred_cell = cell_vocab.decode_batch(pred_cell, skip_special_tokens=False)
pred_cell = [cell_str_to_token_list(i) for i in pred_cell]
pred_cell = [re.sub(r"(\d).\s+(\d)", r"\1.\2", i) for i in pred_cell]

# print(pred_cell)

# Combine the table structure and cell content
pred_code = build_table_from_html_and_cell(pred_html, pred_cell)
pred_code = "".join(pred_code)
pred_code = html_table_template(pred_code)


from IPython.core.display import display, HTML

display(HTML(pred_code))
