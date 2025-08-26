"""Gemma 270M model loader and configuration for spacy-llm integration"""

import os
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from spacy_llm.registry import registry
    from spacy_llm.models.hf.base import HuggingFace
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("HuggingFace transformers not available. LLM features disabled.")

logger = logging.getLogger(__name__)

class GemmaModel:
    """Wrapper for Gemma 270M model with caching and optimization for serverless deployment"""
    
    def __init__(
        self,
        model_name: str = "google/gemma-3-270m",
        cache_dir: Optional[str] = None,
        device: str = "cpu",
        quantization: bool = True,
        max_new_tokens: int = 100,
        temperature: float = 0.3,
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir or self._get_cache_dir()
        self.device = device
        self.quantization = quantization
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        
        self._model = None
        self._tokenizer = None
        self._pipeline = None
        
    def _get_cache_dir(self) -> str:
        """Get appropriate cache directory for the environment"""
        if os.environ.get('VERCEL'):
            # Use Vercel's tmp directory for caching
            cache_dir = "/tmp/huggingface_models"
        else:
            # Use local cache directory
            cache_dir = str(Path.home() / ".cache" / "huggingface" / "transformers")
        
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    def _load_model(self):
        """Lazy load the model and tokenizer"""
        if self._model is not None:
            return
            
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace transformers not available")
        
        try:
            logger.info(f"Loading Gemma model: {self.model_name}")
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            # Configure model loading parameters
            model_kwargs = {
                "cache_dir": self.cache_dir,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
                "device_map": "auto" if self.device != "cpu" else None,
                "trust_remote_code": True,
            }
            
            # Add quantization if enabled and not on CPU
            if self.quantization and self.device != "cpu":
                model_kwargs["load_in_8bit"] = True
            
            # Load model
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Create text generation pipeline
            self._pipeline = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                device=0 if self.device != "cpu" else -1,
                return_full_text=False,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id,
            )
            
            logger.info("Gemma model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Gemma model: {e}")
            raise
    
    def __call__(self, prompts: List[str]) -> List[str]:
        """Generate responses for the given prompts"""
        if not HF_AVAILABLE:
            raise RuntimeError("HuggingFace transformers not available")
        
        # Lazy load model on first use
        if self._pipeline is None:
            self._load_model()
        
        try:
            responses = []
            for prompt in prompts:
                # Generate response
                result = self._pipeline(prompt)
                
                if result and len(result) > 0:
                    response = result[0]['generated_text'].strip()
                    responses.append(response)
                else:
                    responses.append("")
            
            return responses
            
        except Exception as e:
            logger.error(f"Error generating responses: {e}")
            # Return empty responses to allow fallback
            return [""] * len(prompts)
    
    def is_available(self) -> bool:
        """Check if the model can be loaded"""
        return HF_AVAILABLE

# Global model instance for reuse across requests
_gemma_instance: Optional[GemmaModel] = None

def get_gemma_model() -> GemmaModel:
    """Get a singleton Gemma model instance"""
    global _gemma_instance
    
    if _gemma_instance is None:
        _gemma_instance = GemmaModel()
    
    return _gemma_instance

def preload_gemma():
    """Preload the Gemma model (useful for warm-up)"""
    try:
        model = get_gemma_model()
        # Trigger model loading with a simple prompt
        model(["Test prompt"])
        logger.info("Gemma model preloaded successfully")
    except Exception as e:
        logger.warning(f"Failed to preload Gemma model: {e}")

# Register the model with spacy-llm if HuggingFace is available
if HF_AVAILABLE:
    @registry.llm_models("thoughtrambler.gemma270m.v1")
    def gemma_270m_model(
        model_name: str = "google/gemma-3-270m",
        cache_dir: Optional[str] = None,
        device: str = "cpu",
        quantization: bool = True,
        max_new_tokens: int = 100,
        temperature: float = 0.3,
    ) -> GemmaModel:
        """Factory function to create Gemma 270M model for spacy-llm"""
        return GemmaModel(
            model_name=model_name,
            cache_dir=cache_dir,
            device=device,
            quantization=quantization,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )

    # Alternative HuggingFace integration for spacy-llm
    @registry.llm_models("thoughtrambler.gemma270m_hf.v1")
    def gemma_270m_hf_model(
        model_name: str = "google/gemma-3-270m",
        max_new_tokens: int = 100,
        temperature: float = 0.3,
        device: str = "cpu",
    ) -> HuggingFace:
        """Factory function to create Gemma 270M via spacy-llm's HuggingFace wrapper"""
        config = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "device": device,
            "torch_dtype": "float16" if device != "cpu" else "float32",
            "load_in_8bit": device != "cpu",  # Use quantization if not on CPU
        }
        
        return HuggingFace(model=model_name, config=config)
else:
    logger.warning("HuggingFace not available. Gemma models will not be registered.")