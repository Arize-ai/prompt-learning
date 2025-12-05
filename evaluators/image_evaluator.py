"""
Image prompt evaluator for nano banana optimization.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
from google import genai
from google.genai import types

class ImagePromptEvaluator:
    """Evaluates image generation results for prompt optimization."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") 
        if not api_key:
            raise ValueError("Google API key required for image evaluation")
        
        self.client = genai.Client(api_key=api_key)
    
    def evaluate_images(self, images_dir: str, original_prompt: str) -> Dict[str, Any]:
        """
        Evaluate generated images and provide optimization feedback.
        
        Returns evaluation scores and improvement suggestions.
        """
        
        images_path = Path(images_dir)
        image_files = list(images_path.glob("*.png"))
        
        if not image_files:
            return {
                "error": "No images found in directory",
                "quality_score": 0,
                "consistency_score": 0,
                "improvements": ["Generate images first before evaluation"]
            }
        
        print(f"Evaluating {len(image_files)} images...")
        
        evaluations = []
        
        for img_path in image_files:
            try:
                # Use Gemini to evaluate the image
                evaluation = self._evaluate_single_image(img_path, original_prompt)
                evaluations.append(evaluation)
                
            except Exception as e:
                print(f"Error evaluating {img_path}: {e}")
        
        # Aggregate results
        if not evaluations:
            return {
                "error": "Failed to evaluate any images",
                "quality_score": 0,
                "consistency_score": 0,
                "improvements": ["Check image files and API access"]
            }
        
        return self._aggregate_evaluations(evaluations, original_prompt)
    
    def _evaluate_single_image(self, image_path: Path, original_prompt: str) -> Dict[str, Any]:
        """Evaluate a single image using Gemini vision."""
        
        from PIL import Image
        
        evaluation_prompt = f"""
        Analyze this generated image based on the original prompt: "{original_prompt}"
        
        Rate the image on a scale of 1-5 for:
        1. Prompt adherence (how well it matches the prompt)
        2. Visual quality (composition, lighting, detail)
        3. Artistic appeal (aesthetic value, creativity)
        
        Provide specific feedback on:
        - What works well
        - What could be improved
        - Suggestions for better prompt wording
        
        Format your response as:
        ADHERENCE: [score]
        QUALITY: [score] 
        APPEAL: [score]
        FEEDBACK: [specific feedback]
        IMPROVEMENTS: [prompt improvement suggestions]
        """
        
        # Load and send image to Gemini
        image = Image.open(image_path)
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[evaluation_prompt, image]
        )
        
        return self._parse_evaluation(response.text, str(image_path))
    
    def _parse_evaluation(self, response_text: str, image_path: str) -> Dict[str, Any]:
        """Parse evaluation response from Gemini."""
        
        evaluation = {
            "image_path": image_path,
            "adherence": 3,  # defaults
            "quality": 3,
            "appeal": 3,
            "feedback": "",
            "improvements": ""
        }
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith("ADHERENCE:"):
                try:
                    evaluation["adherence"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith("QUALITY:"):
                try:
                    evaluation["quality"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith("APPEAL:"):
                try:
                    evaluation["appeal"] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith("FEEDBACK:"):
                evaluation["feedback"] = line.split(':', 1)[1].strip()
            elif line.startswith("IMPROVEMENTS:"):
                evaluation["improvements"] = line.split(':', 1)[1].strip()
        
        return evaluation
    
    def _aggregate_evaluations(self, evaluations: List[Dict], original_prompt: str) -> Dict[str, Any]:
        """Aggregate individual image evaluations."""
        
        if not evaluations:
            return {"error": "No evaluations to aggregate"}
        
        # Calculate average scores
        avg_adherence = sum(e["adherence"] for e in evaluations) / len(evaluations)
        avg_quality = sum(e["quality"] for e in evaluations) / len(evaluations)
        avg_appeal = sum(e["appeal"] for e in evaluations) / len(evaluations)
        
        overall_score = (avg_adherence + avg_quality + avg_appeal) / 3
        
        # Collect all feedback and improvements
        all_feedback = [e["feedback"] for e in evaluations if e["feedback"]]
        all_improvements = [e["improvements"] for e in evaluations if e["improvements"]]
        
        # Calculate consistency (how similar the scores are)
        adherence_scores = [e["adherence"] for e in evaluations]
        consistency_score = 5 - (max(adherence_scores) - min(adherence_scores))  # Higher consistency = smaller range
        
        return {
            "image_count": len(evaluations),
            "adherence_score": round(avg_adherence, 1),
            "quality_score": round(avg_quality, 1), 
            "appeal_score": round(avg_appeal, 1),
            "overall_score": round(overall_score, 1),
            "consistency_score": max(1, consistency_score),  # Ensure minimum of 1
            "feedback": all_feedback,
            "improvements": all_improvements,
            "original_prompt": original_prompt,
            "individual_evaluations": evaluations
        }