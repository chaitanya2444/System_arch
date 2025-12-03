import os
import time
from typing import Dict, Set, List, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class PDFService:
    """Service for generating PDF reports"""

    def __init__(self, output_dir: str = "generated_pdfs"):
        """
        Initialize PDF service
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_step_by_step_flow(self, features: List[str]) -> List[str]:
        """
        Generate implementation steps based on features
        
        Args:
            features: List of feature names from Figma
            
        Returns:
            List of step descriptions
        """
        steps = [
            "Step 1: Set up the development environment - Install Python, required libraries (Streamlit, FastAPI, SQLAlchemy, etc.).",
            "Step 2: Initialize the project structure - Create directories for frontend (Streamlit app) and backend (FastAPI server)."
        ]
        
        for i, feature in enumerate(features, start=3):
            steps.append(f"Step {i}: Implement the '{feature}' feature in the frontend using Streamlit components (e.g., buttons, forms based on Figma design).")
            steps.append(f"Step {i}.1: Add corresponding backend endpoints in FastAPI for '{feature}' (e.g., API routes for data handling).")
        
        steps.extend([
            "Step N: Integrate frontend with backend via API calls.",
            "Step N+1: Set up database (SQLite) and connect to backend.",
            "Step N+2: Test the application end-to-end.",
            "Step N+3: Deploy the application (e.g., to Heroku or Vercel)."
        ])
        
        return steps

    def draw_architecture_diagram(self, c: canvas.Canvas) -> None:
        """
        Draw system architecture diagram on PDF canvas
        
        Args:
            c: ReportLab canvas object
        """
        # Define colors
        box_color = HexColor('#4A90E2')
        arrow_color = HexColor('#2E5C8A')
        
        # Draw Frontend box
        c.setFillColor(box_color)
        c.setStrokeColor(black)
        c.rect(1*inch, 7*inch, 2*inch, 1*inch, fill=0)
        c.setFillColor(black)
        c.drawString(1.2*inch, 7.5*inch, "Frontend")
        c.drawString(1.2*inch, 7.3*inch, "(Streamlit)")

        # Draw Backend box
        c.setFillColor(box_color)
        c.rect(4*inch, 7*inch, 2*inch, 1*inch, fill=0)
        c.setFillColor(black)
        c.drawString(4.2*inch, 7.5*inch, "Backend")
        c.drawString(4.2*inch, 7.3*inch, "(FastAPI)")

        # Draw Database box
        c.setFillColor(box_color)
        c.rect(7*inch, 7*inch, 2*inch, 1*inch, fill=0)
        c.setFillColor(black)
        c.drawString(7.2*inch, 7.5*inch, "Database")
        c.drawString(7.2*inch, 7.3*inch, "(SQLite)")

        # Draw arrows
        c.setStrokeColor(arrow_color)
        c.setLineWidth(2)
        c.line(3*inch, 7.5*inch, 4*inch, 7.5*inch)  # Frontend to Backend
        c.line(6*inch, 7.5*inch, 7*inch, 7.5*inch)  # Backend to Database

        # Arrow labels
        c.setFillColor(arrow_color)
        c.drawString(3.2*inch, 7.6*inch, "API Calls")
        c.drawString(6.2*inch, 7.6*inch, "DB Queries")

    def generate_pdf(
        self,
        figma_data: Dict[str, Any],
        report_data: Optional[Dict[str, Any]],
        fonts: Set[str],
        texts: List[str],
        components: Dict[str, str],
        styles: Dict[str, str],
        project_structure: str,
        features: List[str]
    ) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            figma_data: Complete Figma API response
            report_data: Optional additional report data
            fonts: Set of fonts used in design
            texts: List of text elements
            components: Dictionary of components
            styles: Dictionary of styles
            project_structure: Hierarchical structure string
            features: List of features
            
        Returns:
            Path to generated PDF file
        """
        # Generate unique filename
        timestamp = int(time.time())
        pdf_filename = f"project_architecture_{timestamp}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Title
        y_pos = height - inch
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, y_pos, "System Architecture Report")
        y_pos -= 0.3 * inch
        
        c.setFont("Helvetica", 10)
        c.drawString(inch, y_pos, f"Generated from Figma: {figma_data.get('name', 'Untitled')}")
        y_pos -= 0.5 * inch

        # Components Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_pos, "Components:")
        y_pos -= 0.25 * inch
        c.setFont("Helvetica", 10)
        
        if components:
            for comp_id, name in list(components.items())[:20]:  # Limit to 20
                if y_pos < inch:
                    c.showPage()
                    y_pos = height - inch
                c.drawString(1.5 * inch, y_pos, f"• {name}")
                y_pos -= 0.2 * inch
        else:
            c.drawString(1.5 * inch, y_pos, "No components found")
            y_pos -= 0.2 * inch
        y_pos -= 0.3 * inch

        # Styles Section
        if y_pos < 2 * inch:
            c.showPage()
            y_pos = height - inch
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_pos, "Styles:")
        y_pos -= 0.25 * inch
        c.setFont("Helvetica", 10)
        
        if styles:
            for style_id, name in list(styles.items())[:20]:  # Limit to 20
                if y_pos < inch:
                    c.showPage()
                    y_pos = height - inch
                c.drawString(1.5 * inch, y_pos, f"• {name}")
                y_pos -= 0.2 * inch
        else:
            c.drawString(1.5 * inch, y_pos, "No styles found")
            y_pos -= 0.2 * inch
        y_pos -= 0.3 * inch

        # Fonts Section
        if y_pos < 2 * inch:
            c.showPage()
            y_pos = height - inch
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_pos, "Fonts:")
        y_pos -= 0.25 * inch
        c.setFont("Helvetica", 10)
        
        if fonts:
            for font in sorted(fonts):
                if y_pos < inch:
                    c.showPage()
                    y_pos = height - inch
                c.drawString(1.5 * inch, y_pos, f"• {font}")
                y_pos -= 0.2 * inch
        else:
            c.drawString(1.5 * inch, y_pos, "No fonts found")
            y_pos -= 0.2 * inch
        y_pos -= 0.3 * inch

        # Text Elements Section
        if y_pos < 2 * inch:
            c.showPage()
            y_pos = height - inch
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_pos, "Text Elements (sample):")
        y_pos -= 0.25 * inch
        c.setFont("Helvetica", 10)
        
        for text in texts[:15]:  # Limit to first 15
            if y_pos < inch:
                c.showPage()
                y_pos = height - inch
            display_text = text[:70] + "..." if len(text) > 70 else text
            c.drawString(1.5 * inch, y_pos, f"• {display_text}")
            y_pos -= 0.2 * inch
        y_pos -= 0.3 * inch

        # Project Structure Section
        c.showPage()
        y_pos = height - inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y_pos, "Project Structure:")
        y_pos -= 0.25 * inch
        c.setFont("Courier", 8)
        
        structure_lines = project_structure.split('\n')
        for line in structure_lines[:50]:  # Limit to 50 lines
            if y_pos < inch:
                c.showPage()
                y_pos = height - inch
            if line.strip():
                c.drawString(1.2 * inch, y_pos, line[:90])
                y_pos -= 0.15 * inch

        # Report Data Section (if provided)
        if report_data:
            c.showPage()
            y_pos = height - inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, y_pos, "Additional Report Details:")
            y_pos -= 0.25 * inch
            c.setFont("Helvetica", 10)
            
            for key, value in report_data.items():
                if y_pos < inch:
                    c.showPage()
                    y_pos = height - inch
                value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                c.drawString(1.5 * inch, y_pos, f"{key}: {value_str}")
                y_pos -= 0.2 * inch

        # Step-by-Step Flow
        c.showPage()
        y_pos = height - inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_pos, "Implementation Flow:")
        y_pos -= 0.4 * inch
        c.setFont("Helvetica", 9)
        
        steps = self.generate_step_by_step_flow(features)
        for step in steps:
            if y_pos < inch:
                c.showPage()
                y_pos = height - inch
            # Wrap long steps
            if len(step) > 85:
                words = step.split()
                line = ""
                for word in words:
                    if len(line + word) < 85:
                        line += word + " "
                    else:
                        c.drawString(1.2 * inch, y_pos, line)
                        y_pos -= 0.18 * inch
                        line = "  " + word + " "
                if line:
                    c.drawString(1.2 * inch, y_pos, line)
                    y_pos -= 0.18 * inch
            else:
                c.drawString(1.2 * inch, y_pos, step)
                y_pos -= 0.18 * inch

        # System Architecture Diagram
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, height - inch, "System Architecture Diagram")
        self.draw_architecture_diagram(c)

        # Save PDF
        c.save()

        return pdf_path

    def generate_enhanced_pdf(
        self,
        figma_data: Dict[str, Any],
        gemini_analysis: Dict[str, Any],
        fonts: Set[str],
        texts: List[str],
        components: Dict[str, str],
        styles: Dict[str, str],
        ascii_diagram: Optional[str] = None
    ) -> str:
        """
        Generate enhanced PDF report with Gemini AI analysis

        Args:
            figma_data: Complete Figma API response
            gemini_analysis: Comprehensive analysis from Gemini API
            fonts: Set of fonts used in design
            texts: List of text elements
            components: Dictionary of components
            styles: Dictionary of styles

        Returns:
            Path to generated PDF file
        """
        # Generate unique filename
        timestamp = int(time.time())
        pdf_filename = f"architecture_report_{timestamp}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)

        # Create PDF document with platypus
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles_sheet = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles_sheet['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles_sheet['Heading2'],
            fontSize=16,
            textColor=HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        )

        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles_sheet['Heading3'],
            fontSize=13,
            textColor=HexColor('#4b5563'),
            spaceAfter=8,
            spaceBefore=8
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles_sheet['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )

        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("System Architecture Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Design: {figma_data.get('name', 'Untitled')}", styles_sheet['Normal']))
        story.append(Paragraph(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles_sheet['Normal']))
        story.append(PageBreak())

        # Table of Contents
        story.append(Paragraph("Table of Contents", heading_style))
        story.append(Spacer(1, 0.2*inch))
        toc_items = [
            "1. Project Overview",
            "2. Design Analysis",
            "3. Pages & Routes",
            "4. Feature Specifications",
            "5. User Flow",
            "6. Implementation Guide",
            "7. Technical Stack",
            "8. Design Assets"
        ]
        for item in toc_items:
            story.append(Paragraph(item, body_style))
        story.append(PageBreak())

        # 1. Project Overview
        design_analysis = gemini_analysis.get('design_analysis', {})
        story.append(Paragraph("1. Project Overview", heading_style))
        story.append(Spacer(1, 0.1*inch))

        if 'project_overview' in design_analysis:
            story.append(Paragraph(f"<b>Overview:</b> {design_analysis['project_overview']}", body_style))

        if 'application_type' in design_analysis:
            story.append(Paragraph(f"<b>Application Type:</b> {design_analysis['application_type']}", body_style))

        if 'target_users' in design_analysis:
            story.append(Paragraph(f"<b>Target Users:</b> {design_analysis['target_users']}", body_style))

        if 'key_features' in design_analysis and design_analysis['key_features']:
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("<b>Key Features:</b>", body_style))
            for feature in design_analysis['key_features']:
                story.append(Paragraph(f"• {feature}", body_style))

        story.append(PageBreak())

        # 2. Design Analysis
        story.append(Paragraph("2. Design Analysis", heading_style))
        story.append(Spacer(1, 0.1*inch))

        # Components
        story.append(Paragraph("Components", subheading_style))
        if components:
            comp_list = list(components.items())[:20]
            for comp_id, name in comp_list:
                story.append(Paragraph(f"• {name}", body_style))
        else:
            story.append(Paragraph("No components found", body_style))

        story.append(Spacer(1, 0.2*inch))

        # Styles
        story.append(Paragraph("Styles", subheading_style))
        if styles:
            style_list = list(styles.items())[:20]
            for style_id, name in style_list:
                story.append(Paragraph(f"• {name}", body_style))
        else:
            story.append(Paragraph("No styles found", body_style))

        story.append(Spacer(1, 0.2*inch))

        # Fonts
        story.append(Paragraph("Typography", subheading_style))
        if fonts:
            for font in sorted(fonts):
                story.append(Paragraph(f"• {font}", body_style))
        else:
            story.append(Paragraph("No fonts found", body_style))

        story.append(PageBreak())

        # 3. Pages & Routes
        pages_analysis = gemini_analysis.get('pages_analysis', [])
        story.append(Paragraph("3. Pages & Route Mapping", heading_style))
        story.append(Spacer(1, 0.1*inch))

        for idx, page in enumerate(pages_analysis, 1):
            story.append(Paragraph(f"3.{idx} {page.get('page_name', 'Unknown Page')}", subheading_style))
            story.append(Paragraph(f"<b>Route:</b> {page.get('suggested_route', '/')}", body_style))
            story.append(Paragraph(f"<b>Purpose:</b> {page.get('page_purpose', 'N/A')}", body_style))
            story.append(Paragraph(f"<b>Priority:</b> {page.get('implementation_priority', 'Medium')}", body_style))

            if page.get('user_interactions'):
                story.append(Paragraph("<b>User Interactions:</b>", body_style))
                for interaction in page['user_interactions']:
                    story.append(Paragraph(f"• {interaction}", body_style))

            if page.get('connected_pages'):
                story.append(Paragraph(f"<b>Connected To:</b> {', '.join(page['connected_pages'])}", body_style))

            if page.get('developer_notes'):
                story.append(Paragraph(f"<b>Notes:</b> {page['developer_notes']}", body_style))

            story.append(Spacer(1, 0.2*inch))

        if pages_analysis:
            story.append(PageBreak())

        # 4. Feature Specifications
        feature_specs = gemini_analysis.get('feature_specifications', [])
        story.append(Paragraph("4. Feature Specifications", heading_style))
        story.append(Spacer(1, 0.1*inch))

        for idx, feature in enumerate(feature_specs, 1):
            story.append(Paragraph(f"4.{idx} {feature.get('feature_name', 'Feature')}", subheading_style))
            story.append(Paragraph(feature.get('description', 'No description'), body_style))

            if feature.get('user_stories'):
                story.append(Paragraph("<b>User Stories:</b>", body_style))
                for story_item in feature['user_stories']:
                    story.append(Paragraph(f"• {story_item}", body_style))

            if feature.get('api_endpoints_needed'):
                story.append(Paragraph("<b>API Endpoints:</b>", body_style))
                for endpoint in feature['api_endpoints_needed']:
                    story.append(Paragraph(f"• {endpoint}", body_style))

            if feature.get('technical_requirements'):
                story.append(Paragraph("<b>Technical Requirements:</b>", body_style))
                for req in feature['technical_requirements']:
                    story.append(Paragraph(f"• {req}", body_style))

            story.append(Spacer(1, 0.2*inch))

        if feature_specs:
            story.append(PageBreak())

        # 5. User Flow
        user_flow = gemini_analysis.get('user_flow', '')
        story.append(Paragraph("5. User Flow", heading_style))
        story.append(Spacer(1, 0.1*inch))
        if user_flow:
            # Split by lines and add as paragraphs
            for line in user_flow.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, body_style))
        else:
            story.append(Paragraph("User flow not generated", body_style))

        story.append(PageBreak())

        # 6. Implementation Guide
        impl_guide = gemini_analysis.get('implementation_guide', {})
        story.append(Paragraph("6. Implementation Guide", heading_style))
        story.append(Spacer(1, 0.1*inch))

        # Implementation phases
        phases = impl_guide.get('implementation_phases', [])
        for phase in phases:
            story.append(Paragraph(phase.get('phase', 'Phase'), subheading_style))
            if phase.get('duration_estimate'):
                story.append(Paragraph(f"<b>Duration:</b> {phase['duration_estimate']}", body_style))

            for step in phase.get('steps', []):
                story.append(Paragraph(
                    f"<b>Step {step.get('step_number', '?')}:</b> {step.get('title', 'Step')}",
                    body_style
                ))
                story.append(Paragraph(step.get('description', ''), body_style))

                if step.get('deliverables'):
                    story.append(Paragraph("<b>Deliverables:</b>", body_style))
                    for deliverable in step['deliverables']:
                        story.append(Paragraph(f"• {deliverable}", body_style))

            story.append(Spacer(1, 0.2*inch))

        # Routing structure
        if impl_guide.get('routing_structure'):
            story.append(Paragraph("Routing Structure", subheading_style))
            routing = impl_guide['routing_structure']
            if routing.get('description'):
                story.append(Paragraph(routing['description'], body_style))

            if routing.get('routes'):
                for route in routing['routes']:
                    story.append(Paragraph(
                        f"<b>{route.get('path', '/')}</b> → {route.get('component', 'Component')}: {route.get('description', '')}",
                        body_style
                    ))

        story.append(PageBreak())

        # 7. Technical Stack
        story.append(Paragraph("7. Technical Stack Recommendations", heading_style))
        story.append(Spacer(1, 0.1*inch))

        tech_stack = design_analysis.get('technical_stack_recommendations', {})
        if tech_stack.get('frontend'):
            story.append(Paragraph("<b>Frontend:</b>", subheading_style))
            for tech in tech_stack['frontend']:
                story.append(Paragraph(f"• {tech}", body_style))

        if tech_stack.get('backend'):
            story.append(Paragraph("<b>Backend:</b>", subheading_style))
            for tech in tech_stack['backend']:
                story.append(Paragraph(f"• {tech}", body_style))

        if tech_stack.get('database'):
            story.append(Paragraph("<b>Database:</b>", subheading_style))
            story.append(Paragraph(f"• {tech_stack['database']}", body_style))

        if tech_stack.get('additional_tools'):
            story.append(Paragraph("<b>Additional Tools:</b>", subheading_style))
            for tool in tech_stack['additional_tools']:
                story.append(Paragraph(f"• {tool}", body_style))

        # Add new page for ASCII diagram
        story.append(PageBreak())
        
        # 8. System Architecture Diagram
        story.append(Paragraph("8. System Architecture Diagram", heading_style))
        story.append(Spacer(1, 0.3*inch))
        
        if ascii_diagram:
            try:
                # Create enhanced ASCII style with larger font and better visibility
                ascii_style = ParagraphStyle(
                    'ASCIIStyle',
                    parent=styles_sheet['Code'],
                    fontSize=12,  # Larger font size
                    fontName='Courier-Bold',  # Bold font for better visibility
                    leftIndent=0.5*inch,
                    rightIndent=0.5*inch,
                    spaceAfter=6,
                    spaceBefore=6,
                    alignment=TA_CENTER,  # Center the diagram
                    textColor=HexColor('#000000')  # Pure black for maximum contrast
                )
                
                story.append(Spacer(1, 0.2*inch))
                
                # Split diagram into lines and add each as a paragraph
                diagram_lines = ascii_diagram.split('\n')
                for line in diagram_lines:
                    if line.strip():  # Only add non-empty lines
                        # Escape HTML characters and preserve spaces
                        escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"<font name='Courier-Bold' size='12'>{escaped_line}</font>", ascii_style))
                    else:
                        story.append(Spacer(1, 0.1*inch))  # Add space for empty lines
                
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph("Generated ASCII architecture diagram based on Figma design analysis", body_style))
            except Exception as e:
                print(f"Error adding ASCII diagram to PDF: {str(e)}")
                story.append(Paragraph("ASCII diagram generation failed", body_style))
        else:
            story.append(Paragraph("No architecture diagram generated", body_style))

        # Build PDF
        doc.build(story)

        return pdf_path
