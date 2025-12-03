from groq import Groq
from typing import Dict, List, Any
import json


class GroqService:
    """Service for analyzing Figma designs using Groq API"""

    def __init__(self, api_key: str):
        """
        Initialize Groq service

        Args:
            api_key: Groq API key
        """
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Using Llama 3.3 70B for high-quality analysis

    def _generate_completion(self, prompt: str) -> str:
        """
        Generate completion using Groq API

        Args:
            prompt: The prompt to send to Groq

        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior software architect analyzing Figma design files. Always respond with valid JSON when requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def analyze_design_structure(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the overall design structure and provide insights

        Args:
            figma_data: Complete Figma file data

        Returns:
            Dictionary containing analysis results
        """
        document = figma_data.get('document', {})
        name = figma_data.get('name', 'Untitled Design')

        # Extract key information for analysis
        pages = []
        if 'children' in document:
            for child in document['children']:
                if child.get('type') == 'CANVAS':
                    pages.append({
                        'name': child.get('name', 'Untitled Page'),
                        'type': child.get('type'),
                        'children_count': len(child.get('children', []))
                    })

        prompt = f"""
You are a senior software architect analyzing a Figma design file.

Design Name: {name}
Total Pages/Canvases: {len(pages)}

Pages Overview:
{json.dumps(pages, indent=2)}

Based on this Figma design structure, provide a comprehensive analysis in the following JSON format:

{{
  "project_overview": "Brief description of what this application appears to be",
  "application_type": "Type of application (e.g., Web App, Mobile App, Dashboard, Landing Page, etc.)",
  "target_users": "Who are the target users",
  "key_features": ["Feature 1", "Feature 2", ...],
  "technical_stack_recommendations": {{
    "frontend": ["Recommended frameworks/libraries"],
    "backend": ["Recommended technologies"],
    "database": "Recommended database type",
    "additional_tools": ["Other recommended tools"]
  }},
  "architecture_overview": "High-level architecture description"
}}

Respond ONLY with valid JSON, no markdown formatting or additional text.
"""

        try:
            response_text = self._generate_completion(prompt)
            # Remove any markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            analysis = json.loads(response_text.strip())
            return analysis
        except Exception as e:
            return {
                "error": f"Failed to analyze design structure: {str(e)}",
                "project_overview": "Unable to generate analysis",
                "application_type": "Unknown",
                "target_users": "Unknown",
                "key_features": [],
                "technical_stack_recommendations": {},
                "architecture_overview": "Analysis unavailable"
            }

    def analyze_pages_and_routes(self, figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze each page/canvas and generate route mappings

        Args:
            figma_data: Complete Figma file data

        Returns:
            List of page analyses with route information
        """
        document = figma_data.get('document', {})
        pages_analysis = []

        if 'children' not in document:
            return pages_analysis

        for idx, child in enumerate(document['children']):
            if child.get('type') == 'CANVAS':
                page_name = child.get('name', f'Page {idx + 1}')

                # Extract components/frames within this page
                components_in_page = []
                if 'children' in child:
                    for component in child['children'][:10]:
                        components_in_page.append({
                            'name': component.get('name', 'Unnamed'),
                            'type': component.get('type', 'Unknown')
                        })

                prompt = f"""
Analyze this design page/screen from a Figma file:

Page Name: {page_name}
Components/Frames: {json.dumps(components_in_page, indent=2)}

Provide analysis in this JSON format:

{{
  "page_name": "{page_name}",
  "suggested_route": "URL route path (e.g., /home, /dashboard, /login)",
  "page_purpose": "What is this page for",
  "user_interactions": ["Interaction 1", "Interaction 2", ...],
  "connected_pages": ["Which pages this connects to"],
  "key_components": ["Important UI components"],
  "implementation_priority": "High/Medium/Low",
  "developer_notes": "Important notes for implementation"
}}

Respond ONLY with valid JSON, no markdown formatting or additional text.
"""

                try:
                    response_text = self._generate_completion(prompt)
                    response_text = response_text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.startswith('```'):
                        response_text = response_text[3:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]

                    page_analysis = json.loads(response_text.strip())
                    pages_analysis.append(page_analysis)
                except Exception as e:
                    pages_analysis.append({
                        "page_name": page_name,
                        "suggested_route": f"/{page_name.lower().replace(' ', '-')}",
                        "page_purpose": "Analysis failed",
                        "user_interactions": [],
                        "connected_pages": [],
                        "key_components": [],
                        "implementation_priority": "Medium",
                        "developer_notes": f"Error: {str(e)}"
                    })

        return pages_analysis

    def generate_user_flow(self, pages_analysis: List[Dict[str, Any]]) -> str:
        """
        Generate comprehensive user flow description

        Args:
            pages_analysis: List of analyzed pages

        Returns:
            User flow description as markdown text
        """
        prompt = f"""
Based on these analyzed pages from a design file:

{json.dumps(pages_analysis, indent=2)}

Create a comprehensive user flow description that explains:
1. How users navigate through the application
2. The typical user journey from entry to goal completion
3. Key decision points and branches
4. Page connections and navigation patterns

Provide a clear, structured markdown description of the user flow.
"""

        try:
            return self._generate_completion(prompt)
        except Exception as e:
            return f"Unable to generate user flow: {str(e)}"

    def generate_feature_specifications(self, figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate detailed feature specifications

        Args:
            figma_data: Complete Figma file data

        Returns:
            List of feature specifications
        """
        document = figma_data.get('document', {})

        # Extract all canvas names (potential features)
        features = []
        if 'children' in document:
            features = [
                child.get('name', 'Unnamed Feature')
                for child in document['children']
                if child.get('type') == 'CANVAS'
            ]

        if not features:
            return []

        prompt = f"""
You are documenting features for a software application based on Figma designs.

Identified Features/Pages:
{json.dumps(features, indent=2)}

For each feature, provide detailed specifications in this JSON format:

[
  {{
    "feature_name": "Name of the feature",
    "description": "Detailed description",
    "user_stories": ["As a user, I want to...", ...],
    "technical_requirements": ["Requirement 1", "Requirement 2", ...],
    "api_endpoints_needed": ["POST /api/...", "GET /api/...", ...],
    "database_models": ["Model 1", "Model 2", ...],
    "acceptance_criteria": ["Criteria 1", "Criteria 2", ...]
  }}
]

Respond ONLY with valid JSON array, no markdown formatting or additional text.
"""

        try:
            response_text = self._generate_completion(prompt)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            feature_specs = json.loads(response_text.strip())
            return feature_specs
        except Exception as e:
            return [{
                "feature_name": "Error",
                "description": f"Failed to generate specifications: {str(e)}",
                "user_stories": [],
                "technical_requirements": [],
                "api_endpoints_needed": [],
                "database_models": [],
                "acceptance_criteria": []
            }]

    def generate_implementation_guide(
        self,
        design_analysis: Dict[str, Any],
        pages_analysis: List[Dict[str, Any]],
        feature_specs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate step-by-step implementation guide

        Args:
            design_analysis: Overall design analysis
            pages_analysis: Individual page analyses
            feature_specs: Feature specifications

        Returns:
            Implementation guide with phases and steps
        """
        prompt = f"""
Create a comprehensive implementation guide for developers based on this analysis:

Design Overview:
{json.dumps(design_analysis, indent=2)}

Pages (first 5):
{json.dumps(pages_analysis[:5], indent=2)}

Features (first 5):
{json.dumps(feature_specs[:5], indent=2)}

Provide a structured implementation guide in this JSON format:

{{
  "implementation_phases": [
    {{
      "phase": "Phase 1: Setup & Foundation",
      "duration_estimate": "Time estimate",
      "steps": [
        {{
          "step_number": 1,
          "title": "Step title",
          "description": "What to do",
          "commands": ["Command examples if applicable"],
          "deliverables": ["What should be completed"]
        }}
      ]
    }}
  ],
  "routing_structure": {{
    "description": "How routes should be organized",
    "routes": [
      {{
        "path": "/route-path",
        "component": "ComponentName",
        "description": "Route purpose"
      }}
    ]
  }},
  "state_management_recommendations": "How to handle state",
  "testing_strategy": "Testing approach",
  "deployment_considerations": ["Consideration 1", "Consideration 2"]
}}

Respond ONLY with valid JSON, no markdown formatting or additional text.
"""

        try:
            response_text = self._generate_completion(prompt)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            implementation_guide = json.loads(response_text.strip())
            return implementation_guide
        except Exception as e:
            return {
                "error": f"Failed to generate implementation guide: {str(e)}",
                "implementation_phases": [],
                "routing_structure": {},
                "state_management_recommendations": "",
                "testing_strategy": "",
                "deployment_considerations": []
            }

    def analyze_complete_design(self, figma_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete analysis of the Figma design

        Args:
            figma_data: Complete Figma file data

        Returns:
            Comprehensive analysis results
        """
        print("🔍 Starting design structure analysis...")
        design_analysis = self.analyze_design_structure(figma_data)

        print("📄 Analyzing pages and routes...")
        pages_analysis = self.analyze_pages_and_routes(figma_data)

        print("✨ Generating feature specifications...")
        feature_specs = self.generate_feature_specifications(figma_data)

        print("🔄 Generating user flow...")
        user_flow = self.generate_user_flow(pages_analysis)

        print("📋 Creating implementation guide...")
        implementation_guide = self.generate_implementation_guide(
            design_analysis,
            pages_analysis,
            feature_specs
        )

        return {
            "design_analysis": design_analysis,
            "pages_analysis": pages_analysis,
            "feature_specifications": feature_specs,
            "user_flow": user_flow,
            "implementation_guide": implementation_guide
        }