from __future__ import annotations

import math
import types
from dataclasses import dataclass
from typing import Any
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Optional

import pyarrow as pa
import pyarrow.compute as pc
import torch
import torch.nn.functional as F
from transformers import AutoModel
from transformers import AutoTokenizer
from transformers import tokenization_utils_base


@dataclass
class ModelContainer:
    tokenizer: tokenization_utils_base.PreTrainedTokenizerBase
    model: torch.nn.Module

    @classmethod
    def load(cls, filename: str, device_name: str) -> ModelContainer:
        with torch.device(device_name):
            return cls(
                tokenizer=AutoTokenizer.from_pretrained(filename),
                model=AutoModel.from_pretrained(filename, use_safetensors=True).eval(),
            )


# Follows pattern from: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
def _mean_pooling(*, token_embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    input_mask_expanded = attention_mask.unsqueeze(dim=-1).expand(token_embeddings.size()).to(token_embeddings.dtype)
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    sum_mask = torch.sum(input_mask_expanded, dim=1)
    # NOTE: clamps to 1e-9 to avoid NaN from the division
    return sum_embeddings / torch.clamp(sum_mask, min=1e-9)


def _embed_pytorch_core_logic(
    *,
    strings: List[str],
    tokenizer: tokenization_utils_base.PreTrainedTokenizerBase,
    model: torch.nn.Module,
) -> torch.Tensor:
    # NOTE: we do the tokenization inline becauase our interchange format is arrow, and this allows
    # us to construct tensors directly on the appropriate device.
    # This is an expedient decision and has not yet been validated as the "right" approach.
    encoded_input = tokenizer(strings, padding=True, truncation=True, return_tensors="pt")

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # TODO: encapsulate this as its own nn.Module so we can have a single nn.Module representation of our model.
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    sentence_embeddings = _mean_pooling(
        token_embeddings=token_embeddings, attention_mask=encoded_input["attention_mask"]
    )
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
    return sentence_embeddings


def _convert_pytorch_to_arrow(sentence_embeddings: torch.Tensor, num_nulls_end: int = 0) -> pa.Array:
    if len(sentence_embeddings.shape) != 2:
        msg = f"Cannot convert torch.Tensor of shape: {sentence_embeddings.shape}, must be a 2d tensor."
        raise ValueError(msg)
    if sentence_embeddings.dtype != torch.float32:
        msg = f"Cannot convert torch.Tensor of dtype: {sentence_embeddings.dtype}, must be torch.float32."
        raise ValueError(msg)

    sentence_embeddings = sentence_embeddings.cpu().numpy()

    # NOTE: we need to convert our sentence_embeddings to a list and pad it with any nulls.
    sentence_embeddings = [*sentence_embeddings, *(None for _ in range(num_nulls_end))]

    # NOTE: using dynamic sized pyarrow list due to https://github.com/apache/arrow/issues/35697
    return pa.array(list(sentence_embeddings), type=pa.list_(pa.float32()))


def _embed_pytorch(
    *,
    batch: pa.RecordBatch,
    tokenizer: tokenization_utils_base.PreTrainedTokenizerBase,
    model: torch.nn.Module,
    input_column_name: str,
    output_column_name: str,
) -> pa.RecordBatch:
    input_column = batch.column(input_column_name)
    null_index = pc.index(pc.is_null(input_column), pa.scalar(True)).as_py()
    if null_index == 0:
        # NOTE: this case means that they are all null! Short circuit and create the embeddings directly.
        sentence_embeddings = pa.nulls(len(input_column), pa.list_(pa.float32()))
    else:
        if null_index > -1:
            rest_null = pc.all(pc.is_null(input_column.slice(null_index))).as_py()
            if not rest_null:
                msg = "Unexpected non-null values after null, maybe not sorting correctly"
                raise ValueError(msg)
            input_strings = input_column.slice(length=null_index).to_pylist()
        else:
            input_strings = input_column.to_pylist()

        sentence_embeddings = _embed_pytorch_core_logic(strings=input_strings, tokenizer=tokenizer, model=model)

        num_nulls = len(input_column) - null_index if null_index > -1 else 0
        sentence_embeddings = _convert_pytorch_to_arrow(sentence_embeddings, num_nulls_end=num_nulls)

    batch_with_results = pa.RecordBatch.from_arrays(
        [*batch.columns, sentence_embeddings],
        schema=batch.schema.append(pa.field(output_column_name, sentence_embeddings.type)),
    )
    return batch_with_results


def embed_pytorch(
    batch: pa.RecordBatch,
    *,
    model: ModelContainer,
    input_column_name: str,
    output_column_name: str,
    device_name: str = "cpu",
) -> pa.RecordBatch:
    with torch.device(device_name):
        return _embed_pytorch(
            batch=batch,
            tokenizer=model.tokenizer,
            model=model.model,
            input_column_name=input_column_name,
            output_column_name=output_column_name,
        )


class ImmutableFuncConfig:
    def __init__(self, **kwargs):
        self._data = types.MappingProxyType(dict(**kwargs))

    def load(self):
        return self

    def kwargs(self) -> Mapping[str, Any]:
        return self._data


@dataclass
class EmbedPytorchFuncConfig:
    _model_filename: str
    _device_name: str
    _extra_kwargs: Mapping[str, Any]

    # NOTE: these are late init objects
    _final_kwargs: Optional[Mapping[str, Any]] = None

    @classmethod
    def create(
        cls, model_filename: str, device_name: str, input_column_name: str, output_column_name: str
    ) -> EmbedPytorchFuncConfig:
        return cls(
            _model_filename=model_filename,
            _device_name=device_name,
            _extra_kwargs=types.MappingProxyType(
                {
                    "device_name": device_name,
                    "input_column_name": input_column_name,
                    "output_column_name": output_column_name,
                }
            ),
        )

    def load(self):
        model_container = ModelContainer.load(self._model_filename, device_name=self._device_name)
        self._final_kwargs = types.MappingProxyType(dict(model=model_container, **self._extra_kwargs))
        return self

    def kwargs(self) -> Mapping[str, Any]:
        if self._final_kwargs is None:
            msg = "`load` must be called prior to calling `kwargs`."
            raise ValueError(msg)
        return self._final_kwargs


def dynamic_token_batching(batch: pa.RecordBatch, *, token_budget: int, column_name: str) -> Iterator[pa.RecordBatch]:
    """Split the batch into a set of microbatches.

    The logic for the split is as follows:
    1. token_budget is specified
    2. the data should be sorted according to the sentence length of the "column_name" column.
    3. we calculate how many rows can fit within our token budget w/ padding
    4. the other data in that row should still be maintained
    """
    captions = batch.column(column_name)

    lengths = pc.utf8_length(captions)
    sorted_indices = pc.array_sort_indices(lengths, order="descending")

    index = 0

    while index < batch.num_rows:
        # Estimated tokens is based on an average token length of 4 chars + 2 tokens for the start/end tokens.
        string_length = lengths[sorted_indices[index].as_py()].as_py()
        if string_length:
            estimated_num_tokens = 2 + math.ceil(string_length / 4)

            #  Calculate the number of rows we can support according to our token budget (assumes padding)
            #  This is simply `budget // estimated_token_count` since our data is sorted by length desc.
            #  NOTE: we ensure that we always take one item in the case that our token budget is smaller than
            #  a single row.
            num_rows = max((token_budget // estimated_num_tokens), 1)
            end = min(index + num_rows, batch.num_rows)
            batch_indices = sorted_indices.slice(index, end - index)
            yield batch.take(batch_indices)
            index = end
        else:
            # NOTE: this case means the rest are all empty. Make the batch the rest of the data!
            # Default slice is unbounded to the end.
            batch_indices = sorted_indices.slice(index)
            yield batch.take(batch_indices)
            index = batch.num_rows


class DynamicBatchingFuncConfig(ImmutableFuncConfig):
    @classmethod
    def create(cls, token_budget: int, column_name: str) -> DynamicBatchingFuncConfig:
        return cls(token_budget=token_budget, column_name=column_name)
