import pytest
from dataclasses import dataclass
from core.llm.types import ModelRequest, Message
from core.llm.gateway import ModelGateway
from core.llm.registry import ProviderRegistry
from core.llm.router import ModelRouter, NoCompatibleModelError
from core.llm.capabilities import ModelCapabilities
from core.llm.errors import ModelUnavailableError

@dataclass
class MockModelInfo:
    model_id: str
    capabilities: ModelCapabilities

class MockProvider:
    def __init__(self, name, model_name, capabilities):
        self.name = name
        self.model_name = model_name
        self._capabilities = capabilities
        
    def generate(self, req, model):
        raise ModelUnavailableError("mock", provider=self.name, model=model)
        
    def capabilities(self):
        return self._capabilities
        
    def is_configured(self):
        return True
        
    def is_healthy(self):
        return True
        
    def list_models(self):
        return [MockModelInfo(model_id=self.model_name, capabilities=self._capabilities)]
        
    def get_model(self, model_id):
        return MockModelInfo(model_id=self.model_name, capabilities=self._capabilities)

def test_gateway_multimodal_capability_checking():
    registry = ProviderRegistry()
    
    def make_mock_text():
        return MockProvider("mock_text", "t1", ModelCapabilities(text_generation=True))
        
    def make_mock_vision():
        return MockProvider("mock_vision", "v1", ModelCapabilities(text_generation=True, vision=True))
        
    registry.register("mock_text", make_mock_text)
    registry.register("mock_vision", make_mock_vision)
    
    router = ModelRouter(registry)
    gateway = ModelGateway(registry=registry, router=router)
    
    # Text only request
    req1 = ModelRequest(messages=[Message(role="user", content="hello")])
    try:
        gateway.generate(req1, provider_id="mock_text")
    except ModelUnavailableError:
        pass
        
    # Multimodal request
    req2 = ModelRequest(messages=[Message(role="user", content="what is this", multimodal_parts=[{"type": "image", "data": b""}])])
    
    # We will override provider to force a failure
    with pytest.raises(NoCompatibleModelError):
        gateway.generate(req2, provider_id="mock_text")
        
    # Valid provider
    try:
        gateway.generate(req2, provider_id="mock_vision")
    except ModelUnavailableError:
        pass
    except Exception as e:
        if isinstance(e, NoCompatibleModelError):
            assert False, "Should have passed router"
