import torch
import torch.distributed

from transformers import AutoTokenizer
from typing import Optional

from . import FlashCausalLM
from .custom_modeling.flash_rw_modeling import (
    RWConfig,
    FlashRWForCausalLM,
)
from ..utils import (
    initialize_torch_distributed,
    weight_files,
    Weights,
)


class FlashRWSharded(FlashCausalLM):
    def __init__(
        self,
        model_id: str,
        revision: Optional[str] = None,
        quantize: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
        trust_remote_code: bool = False,
    ):
        self.process_group, rank, world_size = initialize_torch_distributed()
        if torch.cuda.is_available():
            device = torch.device(f"cuda:{rank}")
            dtype = torch.float16 if dtype is None else dtype
        else:
            raise NotImplementedError("FlashRW is only available on GPU")

        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            revision=revision,
            padding_side="left",
            truncation_side="left",
            trust_remote_code=trust_remote_code,
        )

        config = RWConfig.from_pretrained(
            model_id, revision=revision, trust_remote_code=trust_remote_code
        )

        torch.distributed.barrier(group=self.process_group)
        filenames = weight_files(model_id, revision=revision, extension=".safetensors")
        weights = Weights(filenames, device, dtype, process_group=self.process_group)

        config.quantize = quantize

        model = FlashRWForCausalLM(config, weights)

        torch.distributed.barrier(group=self.process_group)
        super(FlashRWSharded, self).__init__(
            model=model.to(device),
            tokenizer=tokenizer,
            num_layers=len(model.transformer.h),
            num_kv_heads=model.transformer.cache_size,
            head_size=model.transformer.head_size,
            dtype=dtype,
            device=device,
            rank=rank,
            world_size=world_size,
        )
