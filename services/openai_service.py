# services/openai_service.py
import os
import base64
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

class OpenAISpeciesIdentificationService:
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            try:
                self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
    
    def identify_marine_species(self, image_data, location_context="ocean") -> Dict[str, Any]:
        """
        Identify marine species from image using OpenAI Vision API
        
        Args:
            image_data: Image data (bytes or base64 string)
            location_context: Geographic context for identification
        
        Returns:
            Dictionary with identification results
        """
        if not self.client:
            return {
                'identified': False,
                'error': 'OpenAI API not available or configured',
                'confidence': 0
            }
        
        try:
            # Convert image data to base64 if needed
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_base64 = image_data
            
            # Prepare the prompt for marine species identification
            prompt = f"""
            You are a marine biologist expert. Analyze this image and identify the marine species shown.
            Location context: {location_context}
            
            Please provide your analysis in the following JSON format:
            {{
                "identified": true/false,
                "scientific_name": "Species scientific name",
                "common_name": "Species common name", 
                "species_type": "fish/mammal/reptile/invertebrate/coral/algae",
                "confidence": 0-100,
                "conservation_status": "least concern/near threatened/vulnerable/endangered/critically endangered/extinct",
                "threat_level": "low/medium/high/critical",
                "habitat": "Brief habitat description",
                "description": "Brief species description and distinguishing features",
                "reasoning": "Why you identified this species"
            }}
            
            If you cannot identify the species or if it's not a marine organism, set "identified" to false and provide a brief explanation in the "reasoning" field.
            """
            
            # Make API call to OpenAI Vision
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            import json
            try:
                # Look for JSON in the response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = result_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # If no JSON found, create a basic response
                    result = {
                        'identified': False,
                        'error': 'Could not parse identification result',
                        'confidence': 0,
                        'reasoning': result_text
                    }
            except json.JSONDecodeError:
                result = {
                    'identified': False,
                    'error': 'Invalid JSON response from AI',
                    'confidence': 0,
                    'reasoning': result_text
                }
            
            logger.info(f"Species identification completed with confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI species identification error: {str(e)}")
            return {
                'identified': False,
                'error': f'API error: {str(e)}',
                'confidence': 0
            }
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return self.client is not None