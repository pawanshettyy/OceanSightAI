import os
import json
import base64
from io import BytesIO
from PIL import Image
import openai

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class OpenAISpeciesIdentificationService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def identify_marine_species(self, image_data, location="Indian Ocean"):
        """
        Identify marine species from image using OpenAI Vision API
        
        Args:
            image_data: Base64 encoded image data or file-like object
            location: Geographic location context for better identification
            
        Returns:
            dict: Species identification results
        """
        try:
            # Convert image to base64 if needed
            if hasattr(image_data, 'read'):
                # File-like object
                image_bytes = image_data.read()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
            elif isinstance(image_data, bytes):
                base64_image = base64.b64encode(image_data).decode('utf-8')
            else:
                # Assume it's already base64
                base64_image = image_data
            
            # Create prompt for Indian marine species identification
            prompt = f"""
            You are a marine biologist expert specializing in Indian Ocean marine life. 
            Analyze this image and identify the marine species. Focus specifically on species 
            found in Indian waters including the Arabian Sea, Bay of Bengal, and Indian Ocean.
            
            Location context: {location}
            
            Please provide your analysis in the following JSON format:
            {{
                "identified": true/false,
                "scientific_name": "Species scientific name",
                "common_name": "Common name in English",
                "species_type": "fish/mammal/invertebrate/coral/algae",
                "conservation_status": "critically endangered/endangered/vulnerable/near threatened/least concern",
                "threat_level": "critical/high/medium/low",
                "confidence": 0-100,
                "habitat": "Description of habitat",
                "description": "Brief description of the species",
                "indian_ocean_distribution": "Where in Indian waters this species is found",
                "conservation_notes": "Any conservation concerns specific to Indian waters",
                "recommendations": ["List of conservation recommendations"],
                "error": "Error message if identification failed"
            }}
            
            If you cannot identify the species or if it's not a marine organism, 
            set "identified" to false and provide an appropriate error message.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please identify this marine species:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content or '{"error": "No response content"}')
            return result
            
        except Exception as e:
            return {
                "identified": False,
                "error": f"Error during species identification: {str(e)}",
                "confidence": 0
            }
    
    def get_species_conservation_advice(self, species_name, location="Indian Ocean"):
        """
        Get conservation advice for a specific species
        """
        try:
            prompt = f"""
            Provide conservation advice for {species_name} specifically in {location} region.
            Focus on Indian marine conservation efforts and local threats.
            
            Respond in JSON format:
            {{
                "species": "{species_name}",
                "current_status": "Current conservation status",
                "main_threats": ["List of main threats in Indian waters"],
                "conservation_actions": ["Current conservation efforts"],
                "recommendations": ["Recommended actions"],
                "success_stories": ["Any success stories in the region"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a marine conservation expert specializing in Indian Ocean ecosystems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content or '{"error": "No response content"}')
            
        except Exception as e:
            return {
                "error": f"Error getting conservation advice: {str(e)}"
            }
    
    def analyze_ecosystem_health(self, ocean_data):
        """
        Analyze ecosystem health based on oceanographic data
        """
        try:
            data_summary = f"""
            Temperature: {ocean_data.get('temperature', 'N/A')}°C
            Salinity: {ocean_data.get('salinity', 'N/A')} PSU
            pH Level: {ocean_data.get('ph_level', 'N/A')}
            Location: {ocean_data.get('location', 'Unknown')}
            """
            
            prompt = f"""
            As a marine ecosystem expert, analyze this oceanographic data from Indian waters:
            
            {data_summary}
            
            Provide assessment in JSON format:
            {{
                "ecosystem_health": "excellent/good/fair/poor/critical",
                "health_score": 0-100,
                "key_indicators": ["List of key health indicators"],
                "concerns": ["Any environmental concerns"],
                "trends": "Description of likely trends",
                "recommendations": ["Management recommendations"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are an oceanographic data analyst specializing in Indian Ocean marine ecosystems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=600
            )
            
            return json.loads(response.choices[0].message.content or '{"error": "No response content"}')
            
        except Exception as e:
            return {
                "error": f"Error analyzing ecosystem health: {str(e)}"
            }