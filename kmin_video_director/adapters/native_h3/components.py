"""Public pinned LFS metadata only. No weights are bundled or downloaded.

Authority: https://huggingface.co/api/models/Comfy-Org/MiniMax-H3/revision/
e5eb578a89295337b8ff433a035929ce0279e0b6?blobs=true
"""
REVISION='e5eb578a89295337b8ff433a035929ce0279e0b6'
COMPONENTS={
    'model':('minimax_h3_ref2va_pruned_int8_convrot.safetensors',
             '9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779',20970379616),
    'clip':('qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
            '35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6',15687142551),
    'video_vae':('minimax_h3_video_vae_int8_convrot.safetensors',
                 '52a2c8c73583c86e4f41cdcce3a6ad0ea562987bc0bf3d60a0cef5f5c8e60c0e',2811065184),
    'audio_vae':('minimax_h3_audio_vae_fp32.safetensors',
                 '8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48',605254808),
    'patch':('minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors',
             '9c645c0a308c8af361efd43b409710f6f8fec0db297c29503e141a84991fed0c',2296635360),
}
DEFAULT_FILES={role:value[0] for role,value in COMPONENTS.items()}
