import requests
from urllib.parse import urlparse
from typing import Dict, Set, List, Any


class FigmaService:
    """Service for interacting with Figma API"""

    @staticmethod
    def parse_figma_key(link: str) -> str:
        """
        Extract Figma file key from URL
        
        Args:
            link: Figma file URL
            
        Returns:
            File key string
            
        Raises:
            ValueError: If URL format is invalid
        """
        parsed_url = urlparse(link)
        path_parts = parsed_url.path.split('/')
        
        # Try 'file' path (standard Figma URLs)
        if 'file' in path_parts:
            file_index = path_parts.index('file')
            if file_index + 1 < len(path_parts):
                return path_parts[file_index + 1]
        
        # Try 'design' path (newer Figma URLs)
        if 'design' in path_parts:
            design_index = path_parts.index('design')
            if design_index + 1 < len(path_parts):
                return path_parts[design_index + 1]
        
        # Try 'make' path (Figma Make URLs for duplicated community files)
        if 'make' in path_parts:
            make_index = path_parts.index('make')
            if make_index + 1 < len(path_parts):
                return path_parts[make_index + 1]
        
        raise ValueError("Invalid Figma link format. Expected format: https://www.figma.com/file/{key}/..., https://www.figma.com/design/{key}/..., or https://www.figma.com/make/{key}/...")

    @staticmethod
    def fetch_figma_data(key: str, token: str) -> Dict[str, Any]:
        """
        Fetch Figma file data from API
        
        Args:
            key: Figma file key
            token: Figma access token
            
        Returns:
            Figma file data as dictionary
            
        Raises:
            requests.HTTPError: If API request fails
            ValueError: If token format is invalid
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate token format
        if not token or not token.strip():
            logger.error("Figma token is empty")
            raise ValueError("Figma access token cannot be empty")
        
        token = token.strip()
        if not token.startswith('figd_'):
            logger.warning(f"Figma token format may be invalid. Expected format: figd_... (got: {token[:10]}...)")
        
        url = f"https://api.figma.com/v1/files/{key}"
        headers = {"X-Figma-Token": token}
        
        try:
            logger.info(f"Fetching Figma data for file key: {key}")
            response = requests.get(url, headers=headers, timeout=30)
            
            # Handle specific HTTP errors with detailed messages
            if response.status_code == 403:
                error_detail = "403 Forbidden"
                try:
                    error_data = response.json()
                    if 'err' in error_data:
                        error_detail = error_data['err']
                except:
                    pass
                
                logger.error(f"Figma API 403 Forbidden. File key: {key}, Error: {error_detail}")
                raise requests.HTTPError(
                    f"403 Forbidden: {error_detail}. "
                    "Possible causes:\n"
                    "1. Invalid or expired Figma access token\n"
                    "2. Token doesn't have permission to access this file\n"
                    "3. File is private/restricted and token lacks access\n"
                    "4. Token format is incorrect (should start with 'figd_')\n\n"
                    "Solutions:\n"
                    "- Verify your token at: https://www.figma.com/settings\n"
                    "- Ensure the file is shared with your account\n"
                    "- Generate a new token if the current one is expired"
                )
            elif response.status_code == 401:
                logger.error("Figma API 401 Unauthorized. Invalid token format or expired token.")
                raise requests.HTTPError(
                    "401 Unauthorized: Invalid Figma access token. "
                    "Please check:\n"
                    "1. Token is correct and hasn't expired\n"
                    "2. Token format is correct (starts with 'figd_')\n"
                    "3. Generate a new token at: https://www.figma.com/settings"
                )
            elif response.status_code == 404:
                logger.error("Figma API 404 Not Found. File key: %s", key)
                raise requests.HTTPError(
                    f"404 Not Found: Figma file not found. "
                    "Please verify:\n"
                    "1. The Figma link is correct\n"
                    "2. The file exists and hasn't been deleted\n"
                    "3. The file key in the URL is valid"
                )
            elif response.status_code == 429:
                # Rate limit exceeded
                retry_after = response.headers.get('Retry-After', 'unknown')
                error_detail = f"429 Too Many Requests"
                try:
                    error_data = response.json()
                    if 'err' in error_data:
                        error_detail = error_data['err']
                except:
                    pass
                
                logger.warning(f"Figma API rate limit exceeded. Retry-After: {retry_after} seconds")
                retry_message = ""
                if retry_after != 'unknown':
                    try:
                        retry_seconds = int(retry_after)
                        retry_message = f"\n\nPlease wait approximately {retry_seconds} seconds before trying again."
                    except:
                        retry_message = f"\n\nPlease wait before trying again (Retry-After: {retry_after})."
                
                raise requests.HTTPError(
                    f"429 Too Many Requests: {error_detail}. "
                    "You've exceeded Figma API rate limits.\n\n"
                    "Figma API Rate Limits:\n"
                    "- Free tier: ~200 requests per minute\n"
                    "- Paid tier: Higher limits\n\n"
                    "What to do:\n"
                    "1. Wait a few minutes before trying again\n"
                    "2. Reduce the frequency of requests\n"
                    "3. Consider upgrading your Figma plan for higher limits\n"
                    "4. Check Figma API status: https://status.figma.com" +
                    retry_message
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout as e:
            logger.error("Figma API request timed out")
            raise requests.HTTPError("Request to Figma API timed out. Please try again.") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Figma API request failed: {str(e)}")
            raise requests.HTTPError(f"Figma API request failed: {str(e)}") from e

    @staticmethod
    def extract_fonts(node: Dict[str, Any], fonts: Set[str] = None) -> Set[str]:
        """
        Recursively extract all fonts used in the design
        
        Args:
            node: Figma node dictionary
            fonts: Set to accumulate fonts (used for recursion)
            
        Returns:
            Set of font family names
        """
        if fonts is None:
            fonts = set()
        
        if 'children' in node:
            for child in node['children']:
                FigmaService.extract_fonts(child, fonts)
        
        if node.get('type') == 'TEXT' and 'style' in node:
            font_family = node['style'].get('fontFamily')
            if font_family:
                fonts.add(font_family)
        
        return fonts

    @staticmethod
    def extract_texts(node: Dict[str, Any], texts: List[str] = None) -> List[str]:
        """
        Recursively extract all text content from the design
        
        Args:
            node: Figma node dictionary
            texts: List to accumulate text content (used for recursion)
            
        Returns:
            List of text strings
        """
        if texts is None:
            texts = []
        
        if 'children' in node:
            for child in node['children']:
                FigmaService.extract_texts(child, texts)
        
        if node.get('type') == 'TEXT' and 'characters' in node:
            texts.append(node['characters'])
        
        return texts

    @staticmethod
    def extract_components(components_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract component names from Figma components dictionary
        
        Args:
            components_dict: Components dictionary from Figma API
            
        Returns:
            Dictionary mapping component IDs to names
        """
        return {comp_id: details['name'] for comp_id, details in components_dict.items()}

    @staticmethod
    def extract_styles(styles_dict: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract style names from Figma styles dictionary
        
        Args:
            styles_dict: Styles dictionary from Figma API
            
        Returns:
            Dictionary mapping style IDs to names
        """
        return {style_id: details['name'] for style_id, details in styles_dict.items()}

    @staticmethod
    def get_project_structure(node: Dict[str, Any], level: int = 0) -> str:
        """
        Build a hierarchical string representation of the project structure
        
        Args:
            node: Figma node dictionary
            level: Current indentation level
            
        Returns:
            Formatted string showing project hierarchy
        """
        struct = '  ' * level + f"{node['name']} ({node['type']})\n"
        
        if 'children' in node:
            for child in node['children']:
                struct += FigmaService.get_project_structure(child, level + 1)
        
        return struct

    @staticmethod
    def get_features(document: Dict[str, Any]) -> List[str]:
        """
        Extract feature names from canvas elements
        
        Args:
            document: Figma document node
            
        Returns:
            List of feature/canvas names
        """
        return [
            child['name'] 
            for child in document.get('children', []) 
            if child['type'] == 'CANVAS'
        ]
