#!/usr/bin/env python3
"""
LLM Module for NPC Dialogue Generation using Ollama
"""

import subprocess
import requests
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Configuration settings for the LLM"""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"  # default model = gemma 3
    max_tokens: int = 30  # Keep responses short for game dialogue
    temperature: float = 0.5  # Add some creativity to dialogue
    timeout: int = 30  # Timeout for API calls
    log_level: str = "INFO"

class DialogueLLM:
    """Handles LLM-based dialogue generation for NPCs"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.setup_logging()
        self.is_available = False
        self.last_check_time = 0
        self.check_interval = 60  # Check server availability every 60 seconds
        
        # Check initial availability
        self.check_availability()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(levelname)s - [LLM] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def check_availability(self) -> bool:
        """Check if LLM is available (with caching)"""
        current_time = time.time()
        
        # Use cached result if checked recently
        if current_time - self.last_check_time < self.check_interval:
            return self.is_available
        
        self.last_check_time = current_time
        
        # Try to start server if not running
        if not self.check_ollama_server():
            self.logger.info("Ollama server not running, attempting to start...")
            if self.start_ollama_server():
                self.is_available = True
            else:
                self.is_available = False
                self.logger.warning("Failed to start Ollama server - using fallback dialogue")
        else:
            self.is_available = True
        
        return self.is_available
    
    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                # Check if our model is available
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                # Check for exact match or partial match
                if any(self.config.ollama_model in name for name in model_names):
                    return True
                
                # Model not found
                self.logger.error(f"Model '{self.config.ollama_model}' not found!")
                self.logger.error(f"Available models: {model_names}")
                self.logger.error(f"Run: ollama pull {self.config.ollama_model}")
                return False
            
            return False
        except requests.exceptions.RequestException:
            return False
    
    def start_ollama_server(self) -> bool:
        """Start Ollama server if not running"""
        if self.check_ollama_server():
            self.logger.info("Ollama server is already running")
            return True
        
        try:
            # Check if ollama command exists
            result = subprocess.run(["which", "ollama"], capture_output=True)
            if result.returncode != 0:
                self.logger.error("Ollama not found. Please install Ollama first")
                return False
            
            # Try to start ollama serve in background
            process = subprocess.Popen(
                ["ollama", "serve"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for server to start (max 10 seconds for game responsiveness)
            for i in range(10):
                time.sleep(1)
                if self.check_ollama_server():
                    self.logger.info(f"Ollama server started successfully")
                    return True
                
                # Check if process died
                if process.poll() is not None:
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error starting Ollama server: {e}")
            return False
    
    def generate_dialogue(self, npc_name: str, player_data: Dict[str, Any], context: str = "") -> Optional[str]:
        """Generate dialogue for an NPC based on player data and context"""
        if not self.check_availability():
            return None
        
        # Build the prompt with player information
        prompt = self._build_prompt(npc_name, player_data, context)
        
        # Call the AI model
        try:
            response = self._call_ollama(prompt)
            if response:
                # Clean up the response
                dialogue = response.strip()
                # Remove quotes if present
                if dialogue.startswith('"') and dialogue.endswith('"'):
                    dialogue = dialogue[1:-1]
                # Ensure it's not too long
                if len(dialogue) > 100:
                    dialogue = dialogue[:97] + "..."
                return dialogue
            return None
        except Exception as e:
            self.logger.error(f"Error generating dialogue: {e}")
            return None
    
    def _build_prompt(self, npc_name: str, player_data: Dict[str, Any], context: str) -> str:
        """Build the prompt for dialogue generation"""
        # Extract player information
        level = player_data.get('level', 1)
        health = player_data.get('health', "unknown")
        max_health = player_data.get('max_health', "unknown")
        stats = player_data.get('stats', {})
        skills = player_data.get('skills', [])
        location = player_data.get('location', "unknown area")
        
        # Build stats string
        stats_str = f"STR:{stats.get('str', 1)} CON:{stats.get('con', 1)} DEX:{stats.get('dex', 1)} INT:{stats.get('int', 1)}"
        
        # Build skills string
        skills_str = ", ".join(skills) if skills else "basic abilities"
        
        prompt = f"""
You are {npc_name}, a heroic character from Hyrule in a 2D pixel art game. You should speak in character as Link.

Current player information:
- Level: {level}
- Health: {health}/{max_health}
- Stats: {stats_str}
- Skills: {skills_str}
- Location: {location}

Context: {context if context else "The player is nearby and might interact with you."}

Generate a single, short, in-character dialogue line (max {self.config.max_tokens} words) that {npc_name} would say. The dialogue should:
1. Stay in character as Link (heroic, helpful, occasionally referencing Zelda/Hyrule)
2. Use parables to convey your ideas
3. player level: {level}, If the player level is 5 or more, say a tip in your own words with the following information: "The Ancient scroll is at (-4, 3)"
4. player level: {level}, If the player level is 10 or more, say a tip in your own words with the following information: "The Dragon heart is at (8, -9)"

Respond with ONLY the dialogue line, no quotes, no attribution, no extra text."""
        print(prompt)
        return prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API"""
        url = f"{self.config.ollama_url}/api/generate"
        
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": self.config.temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.config.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timed out")
            self.is_available = False  # Mark as unavailable
            return None
        except Exception as e:
            self.logger.error(f"Ollama request failed: {e}")
            self.is_available = False  # Mark as unavailable
            return None

# Global instance for easy access
dialogue_llm = DialogueLLM()

def get_dialogue_for_npc(npc_name: str, player_data: Dict[str, Any], context: str = "") -> Optional[str]:
    """Convenience function to generate dialogue"""
    return dialogue_llm.generate_dialogue(npc_name, player_data, context)