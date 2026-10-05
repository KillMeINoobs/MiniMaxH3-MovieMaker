"""ComfyUI custom-node entry point; supports a namespaced filesystem package."""
if __package__:
    from .kmin_video_director.registration import build_registry
else:  # Direct import by CPU tooling in a worktree with a non-Python basename.
    from kmin_video_director.registration import build_registry

REGISTRY = build_registry()
NODE_CLASS_MAPPINGS = dict(REGISTRY.nodes)
NODE_DISPLAY_NAME_MAPPINGS = dict(REGISTRY.display_names)
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY", "REGISTRY"]
