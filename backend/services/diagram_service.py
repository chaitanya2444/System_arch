import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple


class DiagramService:
    """Service for generating system architecture diagrams"""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
    def generate_diagram_prompt(self, figma_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Generate a unique diagram prompt based on Figma data and AI analysis"""
        
        # Extract key information
        project_name = figma_data.get('name', '')
        pages = []
        if 'document' in figma_data and 'children' in figma_data['document']:
            pages = [child.get('name', '') for child in figma_data['document']['children'] 
                    if child.get('type') == 'CANVAS']
        
        # Get AI analysis insights
        design_analysis = ai_analysis.get('design_analysis', {})
        app_type = design_analysis.get('application_type', '')
        tech_stack = design_analysis.get('technical_stack_recommendations', {})
        key_features = design_analysis.get('key_features', [])
        
        # Create unique prompt based on the specific project
        prompt = f"""
System Architecture Diagram for {project_name}:
- Application Type: {app_type}
- Pages/Screens: {', '.join(pages[:5])}
- Key Features: {', '.join(key_features[:3])}
- Frontend: {', '.join(tech_stack.get('frontend', [])[:2])}
- Backend: {', '.join(tech_stack.get('backend', [])[:2])}
- Database: {tech_stack.get('database', '')}

Create a clean, professional system architecture diagram showing:
1. User interface layer with the main pages
2. Application layer with key components
3. Data layer with database
4. External integrations
5. Data flow arrows between components

Style: Modern, minimalist, technical diagram with boxes, arrows, and labels. 
Colors: Blue and gray theme. No text overlay, clean architectural visualization.
"""
        return prompt.strip()

    def generate_diagram_hash(self, figma_link: str, figma_data: Dict[str, Any]) -> str:
        """Generate unique hash for caching diagrams"""
        # Create hash from figma link and key data points
        key_data = {
            'link': figma_link,
            'name': figma_data.get('name', ''),
            'pages': [child.get('name', '') for child in figma_data.get('document', {}).get('children', [])
                     if child.get('type') == 'CANVAS']
        }
        hash_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def extract_components_from_figma(self, figma_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> List[str]:
        """Extract dynamic component names from Figma data and AI analysis"""
        components = []
        
        # Get project name and pages
        project_name = figma_data.get('name', '')
        pages = []
        if 'document' in figma_data and 'children' in figma_data['document']:
            pages = [child.get('name', '') for child in figma_data['document']['children'] 
                    if child.get('type') == 'CANVAS']
        
        # Get AI analysis
        design_analysis = ai_analysis.get('design_analysis', {})
        app_type = design_analysis.get('application_type', '')
        tech_stack = design_analysis.get('technical_stack_recommendations', {})
        key_features = design_analysis.get('key_features', [])
        
        # Use LLM to generate dynamic components if available
        if self.llm_service:
            try:
                prompt = f"""
Based on this Figma project analysis, create a list of 4-6 architecture components:

Project: {project_name}
Type: {app_type}
Pages: {', '.join(pages[:3])}
Features: {', '.join(key_features[:3])}
Frontend: {', '.join(tech_stack.get('frontend', [])[:2])}
Backend: {', '.join(tech_stack.get('backend', [])[:2])}
Database: {tech_stack.get('database', '')}

Generate a JSON array of component names that represent the architecture flow:
["Component1", "Component2", "Component3", "Component4"]

Make them specific to this project. Start with user interaction, then UI layer, then backend services, then data storage.
Respond ONLY with the JSON array.
"""
                
                response = self.llm_service._generate_completion(prompt)
                # Clean response
                response = response.strip()
                if response.startswith('```'):
                    response = response.split('\n')[1:-1]
                    response = '\n'.join(response)
                
                try:
                    components = json.loads(response)
                    if isinstance(components, list) and len(components) >= 3:
                        return components[:6]  # Limit to 6 components
                except:
                    pass
            except Exception as e:
                print(f"LLM component generation failed: {str(e)}")
        
        # Fallback: only use actual data, no hardcoded defaults
        if app_type:
            components.append(f"{app_type} User")
        
        # Add specific pages from Figma
        if pages:
            for page in pages[:2]:  # Max 2 pages
                if page.strip():  # Only add non-empty page names
                    components.append(f"{page} Interface")
        
        # Add tech-specific components from AI analysis
        if tech_stack.get('frontend') and tech_stack['frontend']:
            components.append(f"{tech_stack['frontend'][0]} Layer")
        
        if tech_stack.get('backend') and tech_stack['backend']:
            components.append(f"{tech_stack['backend'][0]} API")
        
        if tech_stack.get('database') and tech_stack['database'].strip():
            components.append(f"{tech_stack['database']}")
        
        # Add feature-based components from AI analysis
        if key_features and key_features[0].strip():
            components.append(f"{key_features[0]} Module")
        
        # If no components were extracted, return minimal structure
        if not components:
            if project_name:
                components = [f"{project_name} System"]
            else:
                components = ["Application"]
        
        return components[:6]  # Limit to 6 components

    def create_ascii_box(self, text: str, width: int = None) -> List[str]:
        """Create ASCII box around text with clean lines"""
        if width is None:
            width = len(text) + 4
        
        # Ensure minimum width
        width = max(width, len(text) + 4)
        
        # Pad text to center it
        padding = (width - 2 - len(text)) // 2
        padded_text = " " * padding + text + " " * (width - 2 - len(text) - padding)
        
        # Use clean box drawing characters
        top_line = "+" + "-" * (width - 2) + "+"
        middle_line = "|" + padded_text + "|"
        bottom_line = "+" + "-" * (width - 2) + "+"
        
        return [top_line, middle_line, bottom_line]

    def create_vertical_arrow(self, width: int) -> List[str]:
        """Create vertical arrow centered"""
        center = (width - 1) // 2
        spaces = " " * center
        return [spaces + "|", spaces + "v"]

    def generate_ascii_diagram(self, figma_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Generate proper ASCII box diagram from Figma data"""
        # Extract components from Figma and AI analysis
        components = self.extract_components_from_figma(figma_data, ai_analysis)
        
        # Generate the diagram
        return self.create_box_diagram(components)

    def create_box_diagram(self, components: List[str]) -> str:
        """Create ASCII box diagram with components and arrows"""
        diagram_lines = []
        
        # Find the maximum width needed
        max_width = max(len(comp) + 4 for comp in components)
        max_width = max(max_width, 20)  # Minimum width
        
        for i, component in enumerate(components):
            # Create box for component
            box_lines = self.create_ascii_box(component, max_width)
            diagram_lines.extend(box_lines)
            
            # Add arrow to next component (except for last one)
            if i < len(components) - 1:
                arrow_lines = self.create_vertical_arrow(max_width)
                diagram_lines.extend(arrow_lines)
        
        return "\n".join(diagram_lines)

    def create_fallback_ascii_diagram(self, figma_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Create a simple fallback ASCII diagram"""
        # Use the same logic as the main diagram generation
        components = self.extract_components_from_figma(figma_data, ai_analysis)
        return self.create_box_diagram(components)

    def generate_architecture_diagram(
        self, 
        figma_link: str, 
        figma_data: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate unique ASCII architecture diagram for the Figma project
        
        Args:
            figma_link: The Figma file URL
            figma_data: Complete Figma file data
            ai_analysis: AI analysis results
            
        Returns:
            ASCII diagram as string
        """
        print("🎨 Generating ASCII system architecture diagram...")
        
        # Generate ASCII diagram
        ascii_diagram = self.generate_ascii_diagram(figma_data, ai_analysis)
        
        print("✅ Successfully generated ASCII diagram")
        return ascii_diagram