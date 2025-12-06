

import os
import logging

logger = logging.getLogger(__name__)

class GeminiConfig:
    def __init__(self):
        self.api_key = None
        self.model_name = 'gemini-2.5-flash'
        self.setup_api_key()
    
    def setup_api_key(self):
        # Method 1: Environment variable
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            logger.info(" Gemini API key loaded")
            return
        
        # Method 2: Config file
        try:
            with open('gemini_api_key.txt', 'r') as f:
                self.api_key = f.read().strip()
            logger.info("Gemini API key loaded from file")
        except:
            logger.warning(" No Gemini API key - using basic analysis only")
    
    def get_api_key(self):
        return self.api_key
    
    def is_configured(self):
        return self.api_key is not None

# Global instance
gemini_config = GeminiConfig()
