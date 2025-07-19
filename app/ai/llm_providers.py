from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import openai
import httpx
import os
from dataclasses import dataclass
import json

@dataclass
class ChartSuggestion:
    chart_type: str
    confidence: float
    reasoning: str
    config: Dict[str, Any]

@dataclass
class LLMResponse:
    chart_type: str
    title: str
    sql_query: str
    chart_config: Dict[str, Any]
    confidence: float
    reasoning: str

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        pass
    
    @abstractmethod
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        pass
    
    @abstractmethod
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        system_prompt = self._build_system_prompt(schema_context)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return LLMResponse(**result)
    
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        prompt = f"""
        Based on this data description: "{data_description}"
        
        Suggest the top 3 most appropriate chart types with confidence scores.
        Return as JSON array with: chart_type, confidence (0-1), reasoning, basic_config
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return [ChartSuggestion(**item) for item in result.get("suggestions", [])]
    
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        validation_prompt = f"""
        Validate if this chart configuration correctly represents the user's intent:
        
        Original prompt: "{original_prompt}"
        Chart config: {json.dumps(chart_config, indent=2)}
        
        Return JSON with: is_valid (boolean), issues (array), suggestions (array)
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": validation_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _build_system_prompt(self, schema_context: Dict[str, Any]) -> str:
        tables_info = ""
        if schema_context.get("tables"):
            for table in schema_context["tables"]:
                tables_info += f"\nTable: {table['name']}\n"
                for column in table.get("columns", []):
                    tables_info += f"  - {column['name']} ({column['type']})\n"
        
        return f"""
        You are a data visualization expert. Convert natural language requests into chart configurations.
        
        Available database schema:
        {tables_info}
        
        Return JSON with:
        - chart_type: bar, line, pie, area, scatter, heatmap, funnel, treemap
        - title: descriptive title
        - sql_query: SQL query using available tables
        - chart_config: complete chart configuration
        - confidence: 0-1 confidence score
        - reasoning: explanation of choices made
        
        Consider data types, relationships, and best visualization practices.
        """

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self._build_system_prompt(schema_context)},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
            )
            
            result = response.json()
            content = json.loads(result["choices"][0]["message"]["content"])
            return LLMResponse(**content)
    
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        # Similar implementation to OpenAI but using Groq API
        pass
    
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        # Similar implementation to OpenAI but using Groq API
        pass
    
    def _build_system_prompt(self, schema_context: Dict[str, Any]) -> str:
        # Same as OpenAI implementation
        return OpenAIProvider._build_system_prompt(self, schema_context)

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user", 
                            "content": f"{self._build_system_prompt(schema_context)}\n\nUser request: {prompt}"
                        }
                    ]
                }
            )
            
            result = response.json()
            content = json.loads(result["content"][0]["text"])
            return LLMResponse(**content)
    
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        # Claude implementation
        pass
    
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        # Claude implementation
        pass
    
    def _build_system_prompt(self, schema_context: Dict[str, Any]) -> str:
        return OpenAIProvider._build_system_prompt(self, schema_context)

class LocalLLMProvider(LLMProvider):
    """Provider for local LLMs via Ollama or similar"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{self._build_system_prompt(schema_context)}\n\nUser: {prompt}",
                    "format": "json",
                    "stream": False
                }
            )
            
            result = response.json()
            content = json.loads(result["response"])
            return LLMResponse(**content)
    
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        # Local LLM implementation
        pass
    
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        # Local LLM implementation
        pass
    
    def _build_system_prompt(self, schema_context: Dict[str, Any]) -> str:
        return OpenAIProvider._build_system_prompt(self, schema_context)

class LLMManager:
    """Manages multiple LLM providers with fallback support"""
    
    def __init__(self):
        self.providers = {}
        self.primary_provider = None
        self.fallback_order = []
    
    def add_provider(self, name: str, provider: LLMProvider, is_primary: bool = False):
        self.providers[name] = provider
        if is_primary:
            self.primary_provider = name
        self.fallback_order.append(name)
    
    async def generate_chart(self, prompt: str, schema_context: Dict[str, Any]) -> LLMResponse:
        """Try primary provider first, then fallbacks"""
        providers_to_try = [self.primary_provider] + [p for p in self.fallback_order if p != self.primary_provider]
        
        for provider_name in providers_to_try:
            if provider_name in self.providers:
                try:
                    return await self.providers[provider_name].generate_chart(prompt, schema_context)
                except Exception as e:
                    print(f"Provider {provider_name} failed: {e}")
                    continue
        
        raise Exception("All LLM providers failed")
    
    async def suggest_chart_type(self, data_description: str) -> List[ChartSuggestion]:
        """Get chart type suggestions from primary provider"""
        if self.primary_provider and self.primary_provider in self.providers:
            return await self.providers[self.primary_provider].suggest_chart_type(data_description)
        return []
    
    async def validate_chart(self, chart_config: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Validate chart with primary provider"""
        if self.primary_provider and self.primary_provider in self.providers:
            return await self.providers[self.primary_provider].validate_chart(chart_config, original_prompt)
        return {"is_valid": True, "issues": [], "suggestions": []}

# Initialize LLM manager
def create_llm_manager() -> LLMManager:
    manager = LLMManager()
    
    # Add providers based on available API keys
    if os.getenv("OPENAI_API_KEY"):
        manager.add_provider("openai", OpenAIProvider(os.getenv("OPENAI_API_KEY")), is_primary=True)
    
    if os.getenv("GROQ_API_KEY"):
        manager.add_provider("groq", GroqProvider(os.getenv("GROQ_API_KEY")))
    
    if os.getenv("CLAUDE_API_KEY"):
        manager.add_provider("claude", ClaudeProvider(os.getenv("CLAUDE_API_KEY")))
    
    # Always add local LLM as fallback
    manager.add_provider("local", LocalLLMProvider())
    
    return manager