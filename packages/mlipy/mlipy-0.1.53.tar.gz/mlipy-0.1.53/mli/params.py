__all__ = [
    'Message',
    'LlamaCppParams',
    'CandleParams',
    'ModelParams',
]

from typing import TypedDict, Optional, Required


class Message(TypedDict):
    role: Required[str]
    content: Required[str]


class LlamaCppParams(TypedDict):
    engine: str                             # 'llama.cpp'
    executable: Optional[str]               # 'main'
    model_id: str                           # creator of model
    creator_model_id: str                   # creator of model
    model: Optional[str]                    # model name
    mmproj: Optional[str]                   # path to a multimodal projector file for LLaVA. see examples/llava/README.md
    chatml: Optional[bool]                  # False
    n_predict: Optional[int]                # -2
    ctx_size: Optional[int]                 # size of the prompt context (default: 512, 0 = loaded from model)
    batch_size: Optional[int]               # 0 (load from model)
    temp: Optional[float]                   # 0.8
    n_gpu_layers: Optional[int]             # 0 (max usually 35)
    top_k: Optional[int]                    # 40
    top_p: Optional[float]                  # 0.9
    stop: Optional[list[str]]               # []
    prompt: Optional[str]                   # | prompt xor messages
    messages: Optional[list[Message]]       # |
    file: Optional[str]                     # / prompt file (path) to start generation
    image: Optional[str]                    # path to an image file. use with multimodal models
    no_display_prompt: Optional[bool]       # True
    split_mode: Optional[str]               # 'none', 'layer' (default), 'row'
    tensor_split: Optional[str]             # None, e.g. '3,1'
    main_gpu: Optional[int]                 # None, e.g. 0 (default)
    seed: Optional[int]                     # -1 (default)
    threads: Optional[int]                  # 16 (default)
    grammar: Optional[str]                  # BNF-like grammar to constrain generations (see samples in grammars/ dir)
    grammar_file: Optional[str]             # file to read grammar from
    cfg_negative_prompt: Optional[str]      # negative prompt to use for guidance. (default: empty)
    cfg_scale: Optional[float]              # strength of guidance (default: 1.000000, 1.0 = disable)
    rope_scaling: Optional[str]             # none,linear,yarn
    rope_scale: Optional[int | float]       # RoPE context scaling factor, expands context by a factor of N
    rope_freq_base: Optional[int | float]   # RoPE base frequency, used by NTK-aware scaling (default: loaded from model)
    rope_freq_scale: Optional[int | float]  # RoPE frequency scaling factor, expands context by a factor of 1/N
    cont_batching: Optional[bool]           # enable continuous batching (a.k.a dynamic batching) (default: disabled)
    prompt_to_file: Optional[bool]          # save prompt to file 
    image_to_file: Optional[bool]           # base64 encoded image to be saved to file


class CandleParams(TypedDict):
    engine: str                             # 'candle'
    executable: Optional[str]               # 'phi', 'stable-lm', 'llama', 'mistral', 'quantized'
    model_id: str
    creator_model_id: str
    model: Optional[str]
    cpu: Optional[bool]                     # False
    temperature: Optional[int]              # 0.8
    top_p: Optional[int]                    # 0.9
    sample_len: Optional[int]               # 100
    quantized: Optional[bool]               # False
    use_flash_attn: Optional[bool]          # False
    stop: Optional[list[str]]               # []
    prompt: Optional[str]                   # | prompt xor messages
    messages: Optional[list[Message]]       # /


ModelParams: type = LlamaCppParams | CandleParams
