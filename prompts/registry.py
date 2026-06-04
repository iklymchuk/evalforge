"""Discovery and loading of prompt templates from a directory."""

from pathlib import Path
from prompts.template import PromptTemplate


class PromptNotFoundError(Exception):
    """Raised when the requested prompt name or version doesn't exist."""

class PromptRegistry:
    """Loads prompt YAML files from a directory tree.
    
    Expected layout:
        <root>/
            <prompt_name>/  
                v1.yaml
                v2.yaml
                ...
    """
    def __init__(self, root: str | Path = "prompts"):
        self.root = Path(root)
        if not self.root.exists():
            raise FileNotFoundError(f"Prompts directory not found: '{self.root}'")
    
    def get(self, name: str, version: int | None = None) -> PromptTemplate:
        """Load a prompt by name. If version is None, returns the latest."""
        prompt_dir = self.root / name
        if not prompt_dir.is_dir():
            raise PromptNotFoundError(f"Prompt not found: '{name!r}'")

        versions = self._available_versions(prompt_dir)
        if not versions:
            raise PromptNotFoundError(f"No versions found for prompt: '{name!r}'")
        
        if version is None:
            version = max(versions)
        elif version not in versions:
            raise PromptNotFoundError(f"Version {version} not found for '{name!r}'. Available: {sorted(versions)}")
        
        return PromptTemplate.from_yaml(prompt_dir / f"v{version}.yaml")
    
    def list_prompts(self) -> dict[str, list[int]]:
        """Return a map of prompt name -> sorted list of available versions."""
        result = {}
        for prompt_dir in sorted(self.root.iterdir()):
            if prompt_dir.is_dir():
                versions = self._available_versions(prompt_dir)
                if versions:
                    result[prompt_dir.name] = sorted(versions)
        return result
    
    @staticmethod
    def _available_versions(prompt_dir: Path) -> list[int]:
        versions = []
        for file in prompt_dir.glob("v*.yaml"):
            try:
                versions.append(int(file.stem.lstrip("v")))
            except ValueError:
                continue
        return versions
        
        
        
        
            
        
        

