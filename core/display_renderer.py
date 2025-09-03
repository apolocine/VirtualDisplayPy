"""
🎨 Display Renderer - Visual Display Engine
Date: 03/09/2025
Description: Rendering engine for virtual displays with multiple themes and effects
"""

import math
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from models.display_config import (
    DisplayTheme, VirtualDisplayConfig, DISPLAY_THEMES
)


@dataclass
class RenderedDisplay:
    """Rendered display image and metadata"""
    image: Image.Image
    width: int
    height: int
    theme: DisplayTheme
    content: List[str]
    timestamp: datetime
    
    # Visual properties
    background_color: str
    text_color: str
    border_color: str
    font_size: int
    
    # Effects
    cursor_visible: bool = False
    cursor_position: Tuple[int, int] = (0, 0)
    is_blinking: bool = False


class DisplayRenderer:
    """
    Visual rendering engine for virtual displays
    Supports LCD, LED, OLED themes with realistic effects
    """
    
    def __init__(self):
        self.font_cache: Dict[int, ImageFont.FreeTypeFont] = {}
        self.theme_cache: Dict[str, Dict[str, Any]] = {}
        
        # Default display dimensions
        self.base_char_width = 12
        self.base_char_height = 16
        self.border_width = 10
        self.line_spacing = 2
        
        # Animation state
        self.cursor_blink_state = True
        self.last_blink_time = datetime.now()
        
    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get cached font or create new one"""
        if size not in self.font_cache:
            try:
                # Try to load a monospace font
                self.font_cache[size] = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size
                )
            except (OSError, IOError):
                try:
                    # Fallback to default font
                    self.font_cache[size] = ImageFont.load_default()
                except:
                    # Last resort - create basic font
                    self.font_cache[size] = ImageFont.load_default()
        
        return self.font_cache[size]
    
    def calculate_display_size(self, config: VirtualDisplayConfig) -> Tuple[int, int]:
        """Calculate display dimensions based on configuration"""
        char_width = self.base_char_width * (config.font_size / 14)
        char_height = self.base_char_height * (config.font_size / 14)
        
        width = int(config.line_length * char_width + 2 * self.border_width)
        height = int(config.display_lines * char_height + 
                    (config.display_lines - 1) * self.line_spacing + 
                    2 * self.border_width)
        
        return width, height
    
    def render_display(self, config: VirtualDisplayConfig, content: List[str]) -> RenderedDisplay:
        """Render a complete display with content"""
        # Get theme colors
        theme_info = DISPLAY_THEMES[config.theme]
        colors = theme_info["colors"]
        
        # Calculate display size
        width, height = self.calculate_display_size(config)
        
        # Create image
        image = Image.new('RGB', (width, height), colors["bg"])
        draw = ImageDraw.Draw(image)
        
        # Draw border
        self._draw_border(draw, width, height, colors["border"])
        
        # Draw display content
        self._draw_content(draw, config, content, colors, width, height)
        
        # Draw cursor if visible
        if config.cursor_visible:
            self._draw_cursor(draw, config, colors, width, height)
        
        # Apply visual effects
        image = self._apply_visual_effects(image, config)
        
        return RenderedDisplay(
            image=image,
            width=width,
            height=height,
            theme=config.theme,
            content=content.copy(),
            timestamp=datetime.now(),
            background_color=colors["bg"],
            text_color=colors["text"],
            border_color=colors["border"],
            font_size=config.font_size,
            cursor_visible=config.cursor_visible,
            cursor_position=(0, 0),  # Will be updated
            is_blinking=config.blinking_cursor
        )
    
    def _draw_border(self, draw: ImageDraw.Draw, width: int, height: int, border_color: str):
        """Draw display border"""
        # Outer border
        draw.rectangle(
            [0, 0, width-1, height-1],
            outline=border_color,
            width=2
        )
        
        # Inner border (recessed effect)
        draw.rectangle(
            [3, 3, width-4, height-4],
            outline=self._darken_color(border_color),
            width=1
        )
    
    def _draw_content(self, draw: ImageDraw.Draw, config: VirtualDisplayConfig, 
                     content: List[str], colors: Dict[str, str], width: int, height: int):
        """Draw text content on display"""
        font = self.get_font(config.font_size)
        
        # Calculate character dimensions
        char_width = self.base_char_width * (config.font_size / 14)
        char_height = self.base_char_height * (config.font_size / 14)
        
        for line_idx in range(min(len(content), config.display_lines)):
            text = content[line_idx] if line_idx < len(content) else ""
            
            # Pad or truncate to line length
            if len(text) > config.line_length:
                text = text[:config.line_length]
            else:
                text = text.ljust(config.line_length)
            
            # Calculate line position
            y = self.border_width + line_idx * (char_height + self.line_spacing)
            
            # Apply alignment
            alignment = config.alignment[line_idx] if line_idx < len(config.alignment) else "left"
            
            if alignment == "center":
                x = (width - len(text) * char_width) // 2
            elif alignment == "right":
                x = width - self.border_width - len(text) * char_width
            else:  # left
                x = self.border_width
            
            # Draw text with glow effect for certain themes
            if config.theme in [DisplayTheme.LED_RED, DisplayTheme.VFD_CYAN]:
                self._draw_text_with_glow(draw, text, x, y, font, colors["text"])
            else:
                draw.text((x, y), text, font=font, fill=colors["text"])
            
            # Draw character separators for LCD themes
            if config.theme in [DisplayTheme.LCD_GREEN, DisplayTheme.LCD_BLUE]:
                self._draw_character_grid(draw, x, y, char_width, char_height, 
                                        len(text), colors["border"])
    
    def _draw_text_with_glow(self, draw: ImageDraw.Draw, text: str, x: int, y: int, 
                            font: ImageFont.FreeTypeFont, color: str):
        """Draw text with glow effect for LED/VFD displays"""
        # Draw glow (multiple offset copies with reduced opacity)
        glow_color = self._adjust_color_brightness(color, 0.3)
        
        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=glow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)
    
    def _draw_character_grid(self, draw: ImageDraw.Draw, x: int, y: int, 
                           char_width: float, char_height: float, char_count: int, color: str):
        """Draw character separator grid for LCD displays"""
        grid_color = self._adjust_color_brightness(color, 0.1)
        
        # Vertical separators
        for i in range(char_count + 1):
            line_x = int(x + i * char_width)
            draw.line([line_x, y, line_x, y + char_height], fill=grid_color, width=1)
        
        # Horizontal separators
        draw.line([x, y, x + char_count * char_width, y], fill=grid_color, width=1)
        draw.line([x, y + char_height, x + char_count * char_width, y + char_height], 
                 fill=grid_color, width=1)
    
    def _draw_cursor(self, draw: ImageDraw.Draw, config: VirtualDisplayConfig, 
                    colors: Dict[str, str], width: int, height: int):
        """Draw cursor at current position"""
        if not config.cursor_visible:
            return
        
        # Update cursor blink state
        now = datetime.now()
        if (now - self.last_blink_time).total_seconds() > 0.5:  # 500ms blink
            self.cursor_blink_state = not self.cursor_blink_state
            self.last_blink_time = now
        
        if config.blinking_cursor and not self.cursor_blink_state:
            return  # Don't draw cursor during blink off phase
        
        # Calculate cursor position (assume position 0,0 for now)
        char_width = self.base_char_width * (config.font_size / 14)
        char_height = self.base_char_height * (config.font_size / 14)
        
        cursor_x = self.border_width
        cursor_y = self.border_width + char_height - 3
        cursor_width = int(char_width)
        cursor_height = 2
        
        # Draw cursor
        draw.rectangle(
            [cursor_x, cursor_y, cursor_x + cursor_width, cursor_y + cursor_height],
            fill=colors["text"]
        )
    
    def _apply_visual_effects(self, image: Image.Image, config: VirtualDisplayConfig) -> Image.Image:
        """Apply visual effects based on theme and settings"""
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        # Apply brightness adjustment
        brightness_factor = config.brightness / 100.0
        img_array = (img_array * brightness_factor).astype(np.uint8)
        
        # Apply contrast adjustment
        contrast_factor = config.contrast / 100.0
        img_array = np.clip((img_array - 128) * contrast_factor + 128, 0, 255).astype(np.uint8)
        
        # Theme-specific effects
        if config.theme == DisplayTheme.LCD_GREEN:
            img_array = self._apply_lcd_effect(img_array)
        elif config.theme == DisplayTheme.OLED_WHITE:
            img_array = self._apply_oled_effect(img_array)
        elif config.theme in [DisplayTheme.LED_RED, DisplayTheme.VFD_CYAN]:
            img_array = self._apply_glow_effect(img_array)
        
        return Image.fromarray(img_array)
    
    def _apply_lcd_effect(self, img_array: np.ndarray) -> np.ndarray:
        """Apply LCD display effect with subtle scanlines"""
        height, width = img_array.shape[:2]
        
        # Add subtle horizontal scanlines
        for y in range(0, height, 2):
            if y < height:
                img_array[y] = (img_array[y] * 0.95).astype(np.uint8)
        
        return img_array
    
    def _apply_oled_effect(self, img_array: np.ndarray) -> np.ndarray:
        """Apply OLED display effect with deeper blacks"""
        # Enhance contrast for OLED-like appearance
        img_array = np.where(img_array < 50, 0, img_array)  # Deeper blacks
        return img_array
    
    def _apply_glow_effect(self, img_array: np.ndarray) -> np.ndarray:
        """Apply glow effect for LED/VFD displays"""
        # This would ideally use Gaussian blur, but we'll simulate with simple averaging
        height, width = img_array.shape[:2]
        
        # Simple glow simulation - brighten non-black areas
        mask = np.any(img_array > 50, axis=2)
        for i in range(3):  # RGB channels
            channel = img_array[:, :, i]
            glowed = np.where(mask, np.minimum(channel * 1.1, 255), channel)
            img_array[:, :, i] = glowed.astype(np.uint8)
        
        return img_array
    
    def _darken_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Darken a hex color by a factor"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _adjust_color_brightness(self, hex_color: str, brightness: float) -> str:
        """Adjust color brightness (0.0 = black, 1.0 = original, >1.0 = brighter)"""
        hex_color = hex_color.lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = min(255, int(r * brightness))
        g = min(255, int(g * brightness))
        b = min(255, int(b * brightness))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def render_status_indicators(self, config: VirtualDisplayConfig, 
                               is_receiving: bool = False, is_transmitting: bool = False,
                               connection_status: str = "disconnected") -> Image.Image:
        """Render status indicators for display"""
        width, height = self.calculate_display_size(config)
        indicator_height = 20
        
        # Create status bar image
        status_image = Image.new('RGB', (width, indicator_height), "#2a2a2a")
        draw = ImageDraw.Draw(status_image)
        
        # Draw port name
        font = self.get_font(12)
        draw.text((5, 2), config.port_name, font=font, fill="#ffffff")
        
        # Draw connection status indicator
        status_color = {
            "connected": "#00ff00",
            "disconnected": "#888888",
            "error": "#ff0000",
            "timeout": "#ffaa00"
        }.get(connection_status, "#888888")
        
        draw.ellipse([width-60, 5, width-50, 15], fill=status_color)
        
        # Draw RX/TX indicators
        if is_receiving:
            draw.text((width-45, 2), "RX", font=font, fill="#00ff00")
        
        if is_transmitting:
            draw.text((width-25, 2), "TX", font=font, fill="#ff8800")
        
        return status_image
    
    def create_display_preview(self, config: VirtualDisplayConfig) -> Image.Image:
        """Create a preview of empty display with configuration"""
        empty_content = [""] * config.display_lines
        rendered = self.render_display(config, empty_content)
        return rendered.image
    
    def export_display_image(self, rendered_display: RenderedDisplay, 
                           file_path: str, format: str = "PNG"):
        """Export rendered display to image file"""
        rendered_display.image.save(file_path, format=format)
    
    def clear_cache(self):
        """Clear rendering caches"""
        self.font_cache.clear()
        self.theme_cache.clear()