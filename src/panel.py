from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import cv2
import numpy as np
import os

def create_text_panel(arabic_text, messages=None, width=640, height=640):
    panel = np.ones((height, width, 3), dtype=np.uint8) * 255
    panel_pil = Image.fromarray(cv2.cvtColor(panel, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(panel_pil)
    font_path = "NotoSansArabic-VariableFont_wdth,wght.ttf" 
    if not os.path.exists(font_path):
        print(f"Error: Font file not found at {font_path}")
        exit(1)
    
    arabic_font = ImageFont.truetype(font_path, 30)

    text_box_height = int(height * 0.6)
    text_box_left = 20
    text_box_right = width - 20
    text_box_top = 20
    text_box_bottom = text_box_height
    draw.rectangle([text_box_left, text_box_top, text_box_right, text_box_bottom], 
                   fill=(230, 230, 230), outline=(180, 180, 180), width=2)

    cv2.putText(panel, "Text Box", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    if arabic_text:
        reshaped_text = arabic_reshaper.reshape(arabic_text)
        bidi_text = get_display(reshaped_text)
        
        max_width = text_box_right - text_box_left - 40  
        y = 60
        line_height = 40  
        max_chars = 30
        
        lines = []
        current_line = ""
        
        for char in bidi_text:
            if len(current_line) < max_chars:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=arabic_font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= max_width:
                x = text_box_right - text_width - 20
                draw.text((x, y), line, font=arabic_font, fill=(0, 0, 0))
                y += line_height
            if y + line_height > text_box_bottom:
                break

    panel = cv2.cvtColor(np.array(panel_pil), cv2.COLOR_RGB2BGR)

    msg_box_top = text_box_height + 40
    cv2.rectangle(panel, (20, msg_box_top), (width-20, height-20), (210, 210, 210), -1)
    cv2.rectangle(panel, (20, msg_box_top), (width-20, height-20), (180, 180, 180), 2)

    cv2.putText(panel, "Messages", (30, msg_box_top + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    if messages:
        y = msg_box_top + 80
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.7
        thickness = 2
        max_width = width - 60
        
        for msg in messages:
            words = msg.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                (w, _), _ = cv2.getTextSize(test_line, font, scale, thickness)
                
                if w <= max_width:
                    current_line = test_line
                else:
                    cv2.putText(panel, current_line, (40, y), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)
                    y += 40
                    current_line = word
            
            if current_line:
                cv2.putText(panel, current_line, (40, y), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)
                y += 40

    return panel