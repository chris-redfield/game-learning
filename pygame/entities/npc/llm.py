"""
LLM Module for NPC Dialogue Generation using Ollama
"""

import subprocess
import requests
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import deque
from entities.npc.prompts import get_dialog

@dataclass
class LLMConfig:
    """Configuration settings for the LLM"""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"  # default model = gemma 3
    max_tokens: int = 50  # Keep responses short for game dialogue
    temperature: float = 0.5  # Add some creativity to dialogue
    timeout: int = 30  # Timeout for API calls
    log_level: str = "INFO"
    dialogue_history_length: int = 20  # Number of dialogue entries to keep in memory

class DialogueLLM:
    """Handles LLM-based dialogue generation for NPCs"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.setup_logging()
        self.is_available = False
        self.last_check_time = 0
        self.check_interval = 60  # Check server availability every 60 seconds
        
        # Initialize dialogue history management
        # Key: npc_name, Value: deque of dialogue entries
        self.dialogue_histories: Dict[str, deque] = {}
        
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
    
    def add_dialogue_to_history(self, npc_name: str, dialogue: str, speaker: str = "npc"):
        """
        Add a dialogue entry to the NPC's conversation history.
        
        Args:
            npc_name (str): Name of the NPC
            dialogue (str): The dialogue text
            speaker (str): Who spoke ("npc" or "player")
        """
        if npc_name not in self.dialogue_histories:
            self.dialogue_histories[npc_name] = deque(maxlen=self.config.dialogue_history_length)
        
        # Add timestamp for better context
        timestamp = time.strftime("%H:%M")
        entry = f"[{timestamp}] {speaker.upper()}: {dialogue}"
        self.dialogue_histories[npc_name].append(entry)
        
        self.logger.debug(f"Added dialogue to {npc_name}'s history: {entry}")
    
    def get_dialogue_history(self, npc_name: str) -> str:
        """
        Get the formatted dialogue history for an NPC.
        
        Args:
            npc_name (str): Name of the NPC
            
        Returns:
            str: Formatted dialogue history or empty string if no history
        """
        if npc_name not in self.dialogue_histories or not self.dialogue_histories[npc_name]:
            return "No previous conversations."
        
        return "\n".join(self.dialogue_histories[npc_name])
    
    def clear_dialogue_history(self, npc_name: str):
        """
        Clear the dialogue history for a specific NPC.
        
        Args:
            npc_name (str): Name of the NPC
        """
        if npc_name in self.dialogue_histories:
            self.dialogue_histories[npc_name].clear()
            self.logger.info(f"Cleared dialogue history for {npc_name}")
    
    def clear_all_dialogue_histories(self):
        """Clear all dialogue histories."""
        self.dialogue_histories.clear()
        self.logger.info("Cleared all dialogue histories")
    
    def generate_dialogue(self, npc_name: str, player_data: Dict[str, Any], context: str = "", character_type: str = "default") -> Optional[str]:
        """
        Generate dialogue for an NPC based on player data and context.
        
        Args:
            npc_name (str): Name of the NPC
            player_data (Dict[str, Any]): Player's current state
            context (str): Current context/situation
            character_type (str): Type of character for prompt selection
            
        Returns:
            Optional[str]: Generated dialogue or None if generation failed
        """
        if not self.check_availability():
            return None
        
        # Build the prompt with player information and dialogue history
        prompt = self._build_prompt(npc_name, player_data, context, character_type)
        
        # Call the AI model
        try:
            response = self._call_ollama(prompt)
            print("model response:", response)
            if response:
                # Clean up the response
                dialogue = response.strip()
                # Remove quotes if present
                if dialogue.startswith('"') and dialogue.endswith('"'):
                    dialogue = dialogue[1:-1]
                # Ensure it's not too long
                if len(dialogue) > 500:
                    dialogue = dialogue[:500] + "..."
                
                # Add the generated dialogue to history
                self.add_dialogue_to_history(npc_name, dialogue, "npc")
                
                return dialogue
            return None
        except Exception as e:
            self.logger.error(f"Error generating dialogue: {e}")
            return None
    
    def _build_prompt(self, npc_name: str, player_data: Dict[str, Any], context: str, character_type: str = "default") -> str:
        """
        Build the prompt for dialogue generation using character templates.
        
        Args:
            npc_name (str): Name of the NPC
            player_data (Dict[str, Any]): Player's current state
            context (str): Current context/situation
            character_type (str): Type of character for prompt selection
            
        Returns:
            str: Complete formatted prompt
        """
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
        
        # Get dialogue history
        previous_interactions = self.get_dialogue_history(npc_name)
        
        # Get the appropriate prompt template
        prompt_template = get_dialog(character_type)
        
        # Format the prompt with all the data
        prompt = prompt_template.format(
            npc_name=npc_name,
            level=level,
            health=health,
            max_health=max_health,
            stats_str=stats_str,
            skills_str=skills_str,
            location=location,
            context=context if context else "The player is nearby and might interact with you.",
            max_tokens=self.config.max_tokens,
            previous_interactions=previous_interactions
        )
        
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

def get_dialogue_for_npc(npc_name: str, player_data: Dict[str, Any], context: str = "", character_type: str = "default") -> Optional[str]:
    """
    Convenience function to generate dialogue.
    
    Args:
        npc_name (str): Name of the NPC
        player_data (Dict[str, Any]): Player's current state
        context (str): Current context/situation
        character_type (str): Type of character for prompt selection
        
    Returns:
        Optional[str]: Generated dialogue or None if generation failed
    """
    return dialogue_llm.generate_dialogue(npc_name, player_data, context, character_type)

def add_player_dialogue(npc_name: str, player_message: str):
    """
    Add a player's message to the dialogue history.
    
    Args:
        npc_name (str): Name of the NPC the player is talking to
        player_message (str): What the player said
    """
    dialogue_llm.add_dialogue_to_history(npc_name, player_message, "player")

def get_dialogue_history_for_npc(npc_name: str) -> str:
    """
    Get the dialogue history for a specific NPC.
    
    Args:
        npc_name (str): Name of the NPC
        
    Returns:
        str: Formatted dialogue history
    """
    return dialogue_llm.get_dialogue_history(npc_name)

def clear_npc_dialogue_history(npc_name: str):
    """
    Clear dialogue history for a specific NPC.
    
    Args:
        npc_name (str): Name of the NPC
    """
    dialogue_llm.clear_dialogue_history(npc_name)