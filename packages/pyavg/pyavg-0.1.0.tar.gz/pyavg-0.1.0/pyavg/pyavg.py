import sys
import os
import math
import time
import pygame
from typing import Any, Union, Tuple, Callable
import types

NEXT_TEXT = pygame.event.custom_type()
END_CHAPTER = pygame.event.custom_type()
UI_LAYER = 100
_default_manager = None

class Font:
    def __init__(self, path=None, size=36, color=(255, 255, 255), bold=False, italic=False):
        self.path = path
        self.font_size = size
        try:
            self.font = pygame.font.Font(path, size)
        except:
            self.font = pygame.font.SysFont(path, size)
        if bold:
            self.font.set_bold(True)
        if italic:
            self.font.set_italic(True)
        self.color = color
        
    def render(self, text, antialias=True, color=None, bg_color=None):
        if color is None:
            color = self.color
        return self.font.render(text, antialias, color, bg_color)
    
    def set_path(self, path):
        self.path = path
        self.font = pygame.font.Font(self.path, self.font_size)
    
    def set_size(self, size):
        self.font_size = size
        self.font = pygame.font.Font(self.path, self.font_size)
        
    def copy(self, path=None, size=None, color=None, bold=None, italic=None):
        if path is None:
            path = self.path
        if size is None:
            size = self.font_size
        if color is None:
            color = self.color
        if bold is None:
            bold = self.bold
        if italic is None:
            italic = self.italic
        return Font(path, size, color, bold, italic)
        
    def __getattr__(self, name):
        return getattr(self.font, name)
        
class Transform:
    def __init__(self, scale=None, angle=0.0, xflip=False, yflip=False, blur=0):
        self.scale = scale or [1, 1]
        self.scale = list(self.scale)
        self.angle = angle
        self.xflip = xflip
        self.yflip = yflip
        self._blur = blur
        
    @property
    def blur(self):
        return self._blur
    
    @blur.setter
    def blur(self, value):
        self._blur = int(value)
        
    def transform(self, surface):
        new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        new_surface.blit(surface, (0, 0))
        if self.xflip or self.yflip:
            new_surface = pygame.transform.flip(new_surface, self.xflip, self.yflip)
        if self.scale != [1, 1]:
            new_surface = pygame.transform.smoothscale_by(new_surface, (self.scale))
        if self.angle != 0:
            new_surface = pygame.transform.rotate(new_surface, self.angle)
        if self.blur > 0:
            new_surface = pygame.transform.gaussian_blur(new_surface, self.blur)
        return new_surface
    
class Mask:
    def __init__(self, size=None, bilt_special=pygame.BLEND_RGBA_MULT, color:list=None):
        size = size or [100, 100]
        if isinstance(bilt_special, str):
            bilt_special = getattr(pygame, bilt_special)
        self.bilt_special = bilt_special
        self.mask = pygame.Surface(size, pygame.SRCALPHA)
        self.color = list(color or [255, 255, 255])
        self.clear()
        
    @property
    def size(self):
        return self.mask.get_size()
    
    def clear(self):
        self.fill(self.color + [255])
        
    def fill(self, color):
        self.mask.fill(color)
    
    def apply(self, surface:pygame.Surface, bilt_special=None, transform=True):
        if isinstance(bilt_special, str):
            bilt_special = getattr(pygame, bilt_special)
        elif bilt_special is None:
            bilt_special = self.bilt_special
            
        new_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        new_surface.blit(surface, (0, 0))
        if transform:
            mask = pygame.transform.smoothscale(self.mask, surface.get_size())
        else:
            mask = self.mask
        new_surface.blit(mask, (0, 0), special_flags=bilt_special)
        return new_surface
    
    def set_blinds(self, width_ratio=0.5, num_blinds=3, direction="horizontal", color:list=None):
        mask_size = self.size
        if color:
            color = list(color)
        else:
            color = self.color 
        self.fill([0, 0, 0, 0])
        if direction == 'horizontal':
            blind_height = mask_size[1] // num_blinds
            width = int(mask_size[0] * width_ratio)
            for i in range(num_blinds):
                pygame.draw.rect(self.mask, color + [255], (0, i * blind_height, mask_size[0], width))
        elif direction == 'vertical':
            blind_width = mask_size[0] // num_blinds
            width = int(mask_size[1] * width_ratio)
            for i in range(num_blinds):
                pygame.draw.rect(self.mask, color + [255], (i * blind_width, 0, width, mask_size[1]))
       
    def set_expanding_box(self, size_ratio=0.5, start_position=None, color:list=None):
        self.fill([0, 0, 0, 0])
        mask_size = self.size
        if color:
            color = list(color)
        else:
            color = self.color 
        if start_position is None:
            start_position = (mask_size[0] // 2, mask_size[1] // 2)
        rect_width = int(mask_size[0] * size_ratio)
        rect_height = int(mask_size[1] * size_ratio)
        rect_top = start_position[1] - rect_height // 2
        rect_left = start_position[0] - rect_width // 2
        pygame.draw.rect(self.mask, color + [255], (rect_left, rect_top, rect_width, rect_height))
    
class BaseSurface(pygame.Surface):
    def __init__(self, transform=None, mask=None):
        self.transform = transform
        self.mask = mask
        self.parent_surface = None
        
    def my_surface(self):
        return pygame.Surface((0,0), flags=pygame.SRCALPHA)

    def redraw(self):
        surface = self.my_surface()
        if self.mask:
            surface = self.mask.apply(surface)
        if self.transform:
            surface = self.transform.transform(surface)
        super().__init__(surface.get_size(), flags=pygame.SRCALPHA)
        self.blit(surface, (0, 0))
        if self.parent_surface:
            self.parent_surface.on_child_redraw()
    
class GameSurface(BaseSurface):
    def __init__(self, surface=None, transform=None, mask=None):
        super().__init__(transform, mask)
        self.surface = surface
        self.redraw()
        
    def my_surface(self):
        return self.surface

class TextSurface(BaseSurface):
    def __init__(self, text="", font=None, limit_size = (-1, -1), style=None, transform=None, mask=None):
        super().__init__(transform, mask)
        self.text = text
        self.font = font or Font()
        self.limit_size = limit_size
        self.set_style(style)
        self.redraw()
        
    @property
    def words(self):
        return list(self.text)
    
    # @property
    # def background_color():
    #     pass
    
    @property
    def is_showing(self):
        if self.style["style"] == "typewriter":
            return self.style["data"]["show_count"] < len(self.words)
        return False
    
    def set_style(self, style):
        if not style:
            style = {"style":"normal", "data":{}}
        elif isinstance(style, str):
            style = {"style":style, "data":{}}
        if style.get("data") is None:
            style["data"] = {}
        if style["style"] == "typewriter":
            if "elapsed_time" not in style["data"]:
                style["data"]["elapsed_time"] = 0
            if "font_interval" not in style["data"]:
                style["data"]["font_interval"] = 0.1
            if "show_count" not in style["data"]:
                style["data"]["show_count"] = 1
        self.style = style
        self.redraw()
        
    def my_surface(self):
        self.word_surfaces = []
        for word in self.words:
            self.word_surfaces.append(self.font.render(word, True))
           
        size = self._calculate_size()
        text_surface = pygame.Surface(size, flags=pygame.SRCALPHA)
        if self.word_surfaces:
            x = 0
            y = 0
            for i, word_surface in enumerate(self.word_surfaces):
                if self.style["style"] == "typewriter" and i >= self.style["data"]["show_count"]:
                    break
                if x + word_surface.get_width() > size[0]:
                    if self.style["style"] == "typewriter":
                        x = 0
                        y += word_surface.get_height()
                    else:
                        break
                text_surface.blit(word_surface, (x, y))
                x += word_surface.get_width()
                if y > size[1]:
                    break
            if y == 0:
                actual_width = min(size[0], x)
            else:
                actual_width = size[0]
            actual_height = min(y + word_surface.get_height(), size[1])
            text_surface = text_surface.subsurface(pygame.Rect((0, 0), (actual_width, actual_height)))
        return text_surface
            
    def skip(self):
        if self.style["style"] == "typewriter":
            self.style["data"]["show_count"] = len(self.words)
            self.redraw()
            
    def update(self, delta_time):
        need_redraw = False
        if not self.is_showing:
            return
        if self.style["style"] == "typewriter":
            data = self.style["data"]
            data["elapsed_time"] += delta_time
            if data["elapsed_time"] >= data["font_interval"]:
                data["elapsed_time"] = 0
                data["show_count"] += 1
                need_redraw = True
        if need_redraw:
            self.redraw()
                
    def _calculate_size(self):
        text_surface = self.font.render(self.text, True)
        x, _ = text_surface.get_size()
        y = 10000
        if self.limit_size[0] > 0 and x > self.limit_size[0]:
            x = self.limit_size[0]
        if self.limit_size[1] > 0 and y > self.limit_size[1]:
            y = self.limit_size[1]
        return x, y

    def set_text(self, text):
        self.text = text
        if self.style["style"] == "typewriter":
            data = self.style["data"]
            data["elapsed_time"] = 0
            data["show_count"] = 1
        self.redraw()

class ImageSurface(BaseSurface):
    def __init__(self, path, transform=None, mask=None):
        super().__init__(transform, mask)
        self.path = self._check_file_extension(path)
        self.rebuild()
        
    @staticmethod
    def _check_file_extension(path):
        if not os.path.isfile(path):
            for ext in ['.png', '.jpg', '.bmp']:
                new_path = path + ext
                if os.path.isfile(new_path):
                    return new_path
        return path
    
    def rebuild(self):
        self.image = pygame.image.load(self.path).convert_alpha()
        self.redraw()
        
    def my_surface(self):
        return self.image
            
class CombinedSurface(BaseSurface):
    def __init__(self, size, surfaces=None, transform=None, mask=None):
        super().__init__(transform, mask)
        self.size = size
        self.surfaces = []
        if surfaces:
            for surf_data in surfaces:
                self.add_surface(*surf_data, redraw=False)
        self.redraw()
        
    def my_surface(self):
        combined_surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        for surface, position, _ in self.surfaces:
            combined_surface.blit(surface, position)
        return combined_surface
            
    def on_child_redraw(self):
        self.redraw()

    def add_surface(self, surface, position=(0, 0), tag=None, index=None, redraw=True):
        if hasattr(surface, 'parent_surface'):
            surface.parent_surface = self
        if index is not None:
            self.surfaces.insert(index, [surface, position, tag])
        else:
            self.surfaces.append([surface, position, tag])
        
        if redraw:
            self.redraw()
            
    def remove_surface(self, tag):
        surfaces_to_remove = []
        for surf_data in self.surfaces:
            if surf_data[2] == tag:
                surfaces_to_remove.append(surf_data)
    
        for surf_data in surfaces_to_remove:
            surface = surf_data[0]
            if hasattr(surface, 'parent_surface'):
                surface.parent_surface = None
            self.surfaces.remove(surf_data)
        
    def update(self, delta_time: float):
        for surf_data in self.surfaces:
            surface = surf_data[0]
            if hasattr(surface, 'update'):
                surface.update(delta_time)

    def move_surface(self, tag, new_position):
        for surf_data in self.surfaces:
            if surf_data[2] == tag:
                surf_data[1] = new_position

    def get_surface(self, tag):
        for surface, position, t in self.surfaces:
            if t == tag:
                return surface

    def set_surface(self, tag, surface, position=(0, 0), redraw=True):
        for surf_data in self.surfaces:
            if surf_data[2] == tag:
                if hasattr(surf_data[0], 'parent_surface'):
                    surf_data[0].parent_surface = None
                surf_data[0] = surface
                if hasattr(surface, 'parent_surface'):
                    surface.parent_surface = self
                if redraw:
                    self.redraw()
                return
        self.add_surface(surface, position, tag, redraw)
            
    def __getitem__(self, tag):
        return self.get_surface(tag)
            
    def __setitem__(self, tag, surface):
        self.set_surface(tag, surface)
    
class StateSurface(BaseSurface):
    def __init__(self, transform=None, mask=None):
        super().__init__(transform, mask)
        self.states = {}
        self.current_state = None
        
    @property
    def current_surface(self):
        return self.states[self.current_state]
    
    def add_state(self, state_name, surface):
        self.states[state_name] = surface
        
    def remove_state(self, state_name):
        self.states.pop(state_name, None)
        
    def switch_state(self, state_name):
        self.current_state = state_name
        self.redraw()
        
    def update(self, delta_time: float):
        if hasattr(self.current_surface, 'update'):
            self.current_surface.update(delta_time)
            
    def my_surface(self):
        return self.current_surface
        
    def redraw(self):
        if self.current_state is not None:
            super().redraw()
            
    def on_child_redraw(self):
        self.redraw()
        
class RectSurface(BaseSurface):
    def __init__(self, size:list=None, color:list=None, border_color:list=None, border_width=0, transform=None, mask=None):
        super().__init__(transform, mask)
        self.size = size or [100, 100]
        self.color = color or [255, 255, 255, 255]
        self.border_color = border_color or [0, 0, 0, 255]
        self.border_width = border_width
        self.redraw()

    def my_surface(self):
        surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        surface.fill(self.color)
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, pygame.Rect((0, 0), self.size), self.border_width)
        return surface
        
class AnimationUtls:
    @staticmethod
    def stop(x):
        return 0
    
    @staticmethod
    def linear_easing(x):
        return x 

    @staticmethod
    def spring_easing(x):
        return 1 - math.cos(x * (math.pi / 2))

    @staticmethod
    def radial_easing(x):
        return  math.sin(x * (math.pi / 2))

    @staticmethod
    def swing_easing(x):
        return 0.5 - 0.5 * math.cos(x * math.pi)

    @staticmethod
    def breathing_easing(x):
        return (-math.cos(x * (2 * math.pi)) + 1) / 2

    @staticmethod
    def cubic_easing(x):
        return 0.5 - 4 * (0.5 - x) ** 3

    @staticmethod
    def bounce_easing(x):
        if x < (1 / 2.75):
            return 7.5625 * x ** 2
        elif x < (2 / 2.75):
            x -= (1.5 / 2.75)
            return 7.5625 * x ** 2 + 0.75
        elif x < (2.5 / 2.75):
            x -= (2.25 / 2.75)
            return 7.5625 * x ** 2 + 0.9375
        else:
            x -= (2.625 / 2.75)
            return 7.5625 * x ** 2 + 0.984375
    
    @staticmethod
    def smooth_step(x):
        t = max(0, min(1, x))
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def compose(*easing_funcs):
        def composed_function(x):
            for func in easing_funcs:
                x = func(x)
            return x
        return composed_function
    
    @staticmethod
    # Higher-order function to generate the inverse of a given easing function.
    def inverse(easing_func):
        def func(x):
            return easing_func(1 - x)
        return func

    @staticmethod
    # Higher-order function to concatenate multiple easing functions.
    def concatenate(*easing_funcs):
        def func(x):
            segment = 1.0 / len(easing_funcs)
            idx = int(x // segment)
            idx = max(0, min(len(easing_funcs)-1, idx))
            sub_x = (x % segment) / segment
            return easing_funcs[idx](sub_x)
        return func

    @staticmethod
    def average(*easing_funcs):
        def result_func(x):
            values = (func(x) for func in easing_funcs)
            return sum(values) / len(values)
        return result_func

    @staticmethod
    def product(*easing_funcs):
        def result_func(x):
            value = 1
            for func in easing_funcs:
                value *= func(x)
            return value
        return result_func 

    @staticmethod
    # Higher-order function to generate the reverse of the y-values of a given easing function.
    def reverse_y(easing_func):
        def func(x):
            return 1 - easing_func(x)
        return func
    
    @staticmethod
    def loop(easing_func):
        def func(x):
            x = x % 1
            return easing_func(x)
        return func
    
    @staticmethod
    def jump(variable:str="y", value=-20, time=1, func=None):
        if not func:
            func = AnimationUtls.linear_easing
        return [{"t":0, variable:0, variable+"_func":func}, {"t":time/2, variable:value}, {"t":time, variable:0}]
    
    @staticmethod
    def shake(variable:str="x", value=20, time=1, func=None):
        if not func:
            func = AnimationUtls.linear_easing
        return [{"t":0, variable:0, variable+"_func":func}, {"t":time/4, variable:value}, {"t":time*3/4, variable:-value}, {"t":time, variable:0}]
        
class Animation:
    def __init__(self, sprite, states:list=None, relative=True, pivot:list=None):
        self.time = 0
        self.sprite = sprite
        self.relative = relative
        self.pivot = pivot or [0.5, 0.5]
        self.functions = {"stop":AnimationUtls.stop,
                          "linear":AnimationUtls.linear_easing,
                          "spring":AnimationUtls.spring_easing,
                          "radial":AnimationUtls.radial_easing,
                          "swing":AnimationUtls.swing_easing,
                          "breathing":AnimationUtls.breathing_easing,
                          "cubic":AnimationUtls.cubic_easing,
                          "bounce":AnimationUtls.bounce_easing,
                          "smooth_step":AnimationUtls.smooth_step}
        self.set_states(states, relative) # states:{"t":float, str:Any}
        self.is_need_redraw = False
        self._temp = {}
        self._temp_delta = {}
      
    @property
    def transform(self):
        if hasattr(self.sprite.image, 'transform'):
            if not self.sprite.image.transform:
                self.sprite.image.transform = Transform()
            return self.sprite.image.transform
      
    @property
    def mask(self):
        if hasattr(self.sprite.image, 'mask'):
            if not self.sprite.image.mask:
                self.sprite.image.mask = Mask()
            return self.sprite.image.mask
        
    def set_states(self, states=None, relative=True):
        if not states:
            states = []
        for state in states:
            for key in state:
                if key == "set_mask_color":
                    state[key] = list(state[key])
        self.states = states     
        self.relative = relative
        
    def play(self, time=0.0):
        self.time = time

    def last_state(self, variable:str, time=0.0):
        last_occurrence = None
        for state in self.states:
            if state["t"] <= time and variable in state:
                last_occurrence = state
        return last_occurrence

    def next_state(self, variable:str, time=0.0):
        next_occurrence = None
        for state in self.states:
            if state["t"] > time and variable in state:
                next_occurrence = state
                break
        return next_occurrence
    
    def current_value(self, variable:str):
        last_state = self.last_state(variable, self.time)
        next_state = self.next_state(variable, self.time)
        if last_state:
            if next_state:
                function = last_state.get(variable+"_func", "linear")
                if not callable(function):
                    function = self.functions[function]
                x = (self.time - last_state["t"]) / (next_state["t"] - last_state["t"])
                if isinstance(last_state[variable], list):
                    current_value = [last_state[variable][i] + function(x) * (next_state[variable][i] - last_state[variable][i]) for i in range(len(last_state[variable]))]
                else:
                    current_value = last_state[variable] + function(x) * (next_state[variable] - last_state[variable])
                return current_value
            else:
                return last_state[variable]
        else:
            return None
    
    def update(self, delta_time=0.03):
        self.time += delta_time
        variables = set()
        for state in self.states:
            variables |= state.keys()
        for variable in variables:
            if variable == "t" or variable.endswith("_func"):
                continue
            current_value = self.current_value(variable)
            if current_value is None:
                continue
            if current_value != self._temp.get(variable):
                if self.relative and not variable.startswith("set_"):
                    delta_value = current_value - self._temp.get(variable, 0) + self._temp_delta.get(variable, 0)
                    value = self.get_value(variable) + delta_value
                    self.set_value(variable, value)
                    self._temp_delta[variable] = value - self.get_value(variable) 
                else:
                    self.set_value(variable, current_value)
                self._temp[variable] = current_value
                
        if self.is_need_redraw:
            rect_before = self.sprite.image.get_rect()
            pivot_before = [rect_before.width * self.pivot[0], rect_before.height * self.pivot[1]]
            self.sprite.redraw()
            rect_after = self.sprite.image.get_rect()
            pivot_after = [rect_after.width * self.pivot[0],  rect_after.height * self.pivot[1]]
            delta_x = pivot_before[0] - pivot_after[0] + self._temp_delta.get("x", 0)
            delta_y = pivot_before[1] - pivot_after[1] + self._temp_delta.get("y", 0)
            self.sprite.rect.left += int(delta_x)
            self.sprite.rect.top += int(delta_y)
            self._temp_delta["x"] = delta_x - int(delta_x)
            self._temp_delta["y"] = delta_y - int(delta_y)
            self.is_need_redraw = False
            
    def get_value(self, variable:str):
        if variable == "x":
            return self.sprite.rect.centerx
        elif variable == "y":
            return self.sprite.rect.centery 
        elif variable == "alpha":
            return self.sprite.image.get_alpha()
        elif variable == "scale_x":
            if self.transform:
                return self.transform.scale[0]
        elif variable == "scale_y":
            if self.transform:
                return self.transform.scale[1]
        elif variable == "angle":
            if self.transform:
                return self.transform.angle
        elif variable == "xflip":
            if self.transform:
                return self.transform.xflip
        elif variable == "yflip":
            if self.transform:
                return self.transform.yflip
        elif variable == "blur":
            if self.transform:
                return self.transform.blur
        
    def set_value(self, variable:str, value):
        if variable == "x":
            self.sprite.rect.centerx = value
        elif variable == "y":
            self.sprite.rect.centery = value
        elif variable == "alpha":
            self.sprite.image.set_alpha(value)
        elif variable == "scale_x":
            if self.transform:
                self.transform.scale[0] = value
                self.is_need_redraw = True
        elif variable == "scale_y":
            if self.transform:
                self.transform.scale[1] = value
                self.is_need_redraw = True
        elif variable == "angle":
            if self.transform:
                self.transform.angle = value
                self.is_need_redraw = True
        elif variable == "xflip":
            if self.transform:
                self.transform.xflip = bool(value)
                self.is_need_redraw = True
        elif variable == "yflip":
            if self.transform:
                self.transform.yflip = bool(value)
                self.is_need_redraw = True
        elif variable == "blur":
            if self.transform:
                self.transform.blur = value
                self.is_need_redraw = True
        elif variable == "set_mask_color":
            if self.mask:
                self.mask.fill(value)
                self.is_need_redraw = True
        elif variable == "set_blinds":
            if self.mask:
                self.mask.set_blinds(value)
                self.is_need_redraw = True
        elif variable == "set_expanding_box":
            if self.mask:
                self.mask.set_expanding_box(value)
                self.is_need_redraw = True
            
class Layout:
    def __init__(self, col=-1, horizontal_spacing=0, vertical_spacing=0, rect_width=0, rect_height=0, left=0, top=0, function=None):
        self.col = col
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        self.rect_width = rect_width
        self.rect_height = rect_height
        self.left = left
        self.top = top
        self.function = function or self.grid_function
        
    def initialize_by_gap(self, col=-1, gap=0, rect_width=0, rect_height=0, left=None, top=None, function=None):
        self.col = col
        self.rect_width = rect_width
        self.rect_height = rect_height
        self.horizontal_gap = gap
        self.vertical_gap = gap
        if top is None:
            top = gap
        self.top = top
        if left is None:
            left = gap
        self.left = left
        self.function = function or self.grid_function
        
    def initialize_by_rect(self, col=-1, rect:pygame.Rect=None, horizontal_spacing=0, vertical_spacing=0, function=None):
        self.col = col
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        if not rect:
            rect = pygame.Rect(0, 0, 0, 0)
        self.rect_width = rect.width
        self.rect_height = rect.height
        self.left = rect.left
        self.top = rect.top
        self.function = function or self.grid_function
        
    def grid_function(self, index):
        if self.col > 0:
            return index % self.col, index // self.col
        else:
            return index, 0
        
    @property
    def rect_size(self):
        return [self.rect_width, self.rect_height]
        
    @property
    def horizontal_gap(self):
        return self.horizontal_spacing - self.rect_width
        
    @horizontal_gap.setter
    def horizontal_gap(self, value=0):
        self.horizontal_spacing = self.rect_width + value
        
    @property
    def vertical_gap(self):
        return self.vertical_spacing - self.rect_height
        
    @vertical_gap.setter
    def vertical_gap(self, value=0):
        self.vertical_spacing = self.rect_height + value
        
    def get_position_by_xy(self, x=0, y=0):
        return pygame.Vector2(self.left + x * self.horizontal_spacing, self.top + y * self.vertical_spacing)
        
    def get_rect_by_xy(self, x=0, y=0):
        return pygame.Rect(self.get_position_by_xy(x, y), (self.rect_width, self.rect_height))
        
    def get_position(self, index=0):
        return self.get_position_by_xy(*self.function(index))
        
    def get_rect(self, index=0):
        return self.get_rect_by_xy(*self.function(index))

class GameSprite(pygame.sprite.DirtySprite):
    def __init__(self, manager=None, layer=0, animation=None):
        super().__init__()
        self.layer = layer
        self.is_hovered = False
        self.is_show = True
        if not manager:
            manager = _default_manager
        self.manager = manager
        self.sub_objects = []
        self.image = pygame.Surface((0,0))
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.set_animation(animation)
        self.manager.sprite_group.add(self)
        
    def draw(self, screen):
        if self.alive():
            screen.blit(self.image, self.rect)
        
    def redraw(self):
        if getattr(self.image, "redraw"):
            self.image.redraw()
        
    @property
    def is_mouse_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)
        
    def update(self, delta_time: float):
        if not self.alive():
            return
        if self.animation:
            self.animation.update(delta_time)
        if not self.is_show:
            return
        if hasattr(self.image, 'update'):
            self.image.update(delta_time)
            
        super().update(delta_time)
        if self.is_mouse_hover and not self.is_hovered:
            self.is_hovered = True
            self.on_hovered()
        if not self.is_mouse_hover and self.is_hovered:
            self.is_hovered = False
            self.on_unhovered()
            
    def set_animation(self, animation=None, relative=True, pivot:list=None):
        if not animation:
            self.animation = None
            return
        if not isinstance(animation, Animation):
            animation = Animation(self, animation, relative, pivot)
        self.animation = animation
        
    def play_animation(self, time=0.0):
        if self.animation:
            self.animation.play(time)
            
    def on_hovered(self):
        pass
            
    def on_unhovered(self):
        pass
        
    def process_event(self, event):
        return False
    
    def kill(self) -> None:
        self.manager.sprite_group.remove(self)
        for obj in self.sub_objects:
            obj.kill()
        self.sub_objects.clear()
        super().kill()

class Button(GameSprite):
    def __init__(self, background=None, pos=(0,0), manager=None, text="", command=None, font=None, layer=UI_LAYER, animation=None):
        super().__init__(manager, layer, animation)
        if not font:
            font = self.manager.font
        text_surface = TextSurface(text, font)
        if background:
            size = background.get_size()
        else:
            size = text_surface.get_size()
            background = pygame.Surface(size, flags=pygame.SRCALPHA)
        self.image = CombinedSurface(background.get_size(), [[background, (0, 0), "background"], [text_surface, (0, 0), "text"]])
        self.rect = background.get_rect()
        self.rect.topleft = pos
        self.text = text
        self.command = command
        
    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.command:
                    self.command()
                    return True
        return False
        
    def set_text(self, text):
        self.text = text
        self.image["text"].set_text(text)
        
class ButtonGroup(GameSprite):
    def __init__(self, background=None, button_background:Union[pygame.Surface, Callable]=None, buttons:list=None, pos=None, layout=None, manager=None, font:Union[Font, Callable]=None, layer=UI_LAYER-1, animation=None, button_class=Button):
        super().__init__(manager, layer, animation)
        self.layout = layout
        self.font = font
        self.button_class = button_class
        if background:
            self.image = background
        self.button_background = button_background
        self.rect = self.image.get_rect()
        if pos:
            self.rect.topleft = pos
        if buttons:
            for button in buttons:
                if isinstance(button, list):
                    self.create(*button)
                elif isinstance(button, dict):
                    self.create(button.get("text"), button.get("command"), button.get("pos"), button.get("background"), button.get("manager"), button.get("font"), button.get("layer"), button.get("animation"))
        
    def create(self, text="", command=None, pos:list=None, background=None, manager=None, font=None, layer=None, animation=None):
        if not background:
            background = self.button_background
        if not isinstance(background, pygame.Surface):
            background = background()
        if pos:    
            pos = pos
        elif self.layout:
            pos = self.layout.get_position(self.count)
        else:
            pos = [0, 0]
        pos = [pos[0] + self.rect.left, pos[1] + self.rect.top]
        if not font:
            font = self.font
        if not isinstance(font, Font):
            font = font()
        if layer is None:
            layer = self.layer + 1
        manager = manager or self.manager
        button = self.button_class(background=background, pos=pos, manager=manager, text=text, command=command, font=font, layer=layer, animation=animation)
        self.sub_objects.append(button)
        return button
        
    def set_position(self, pos):
        self.rect.topleft = pos
        for button in self.sub_objects:
            button.rect.topleft = (button.rect.left + pos[0] - self.rect.left, button.rect.top + pos[1] - self.rect.top)
            
    def update_layout(self):
        if self.layout:
            for index, button in enumerate(self.buttons):
                pos = self.layout.get_position(index)
                pos = [pos[0] + self.rect.left, pos[1] + self.rect.top]
                button.rect.topleft = pos
                
    def clear(self):
        self.sub_objects.clear()
                
    @property
    def count(self):
        return len(self.sub_objects)
    
    def __iter__(self):
        return iter(self.sub_objects)
    
    def __contains__(self, item):
        return item in self.sub_objects
    
class BranchButton(ButtonGroup):
    def __init__(self, options:list, manager=None, font=None, layer=UI_LAYER+1, animation=None):
        self.options = options
        layout = Layout(col=1, vertical_spacing=150, top = 250 - 75 * len(options))
        super().__init__(layout=layout, manager=manager, font=font, layer=layer, animation=animation)
        button_background = pygame.Surface((manager.width, 100), flags=pygame.SRCALPHA)
        button_background.fill((0, 0, 0))
        button_background.set_alpha(70)
        self.button_background = button_background
        for i, option in enumerate(options):
            button = self.create(option[0], lambda index=i:self.on_click(index))
            button.on_hovered = lambda btn=button: (btn.image["background"].set_alpha(150), btn.redraw())
            button.on_unhovered = lambda btn=button: (btn.image["background"].set_alpha(70), btn.redraw())
            
    def on_click(self, button_id):
        if len(self.options[button_id]) >= 2 and self.options[button_id][1]:
            self.options[button_id][1]()
        self.kill()
            
class TextField(GameSprite):
    def __init__(self, background=None, manager=None, content="", title="", style=None, animation=None):
        super().__init__(manager, UI_LAYER, animation)
        if not background:
            background = pygame.Surface((self.manager.width, 220), flags=pygame.SRCALPHA)
            background.fill((0, 0, 0))
        background.set_alpha(70)
        self.rect = background.get_rect()
        self.rect.topleft = (0, self.manager.size[1] - 220)
        self.font = self.manager.font.copy()
        self.font.color = (100, 255, 100)
        self.content = content
        self.title = title
        self.title_x = 0
        self.title_y = 65
        self.title_formatter = "{}:"
        self.content_x = 30
        self.content_y = 100
        self.content_width = 800
        self.instruct = TextSurface("按空格键以继续", self.font, transform=Transform(scale=[0.5, 0.5]))
        self.style = style
        self.image = CombinedSurface(background.get_size(), [[background, (0, 0), "background"]])
        self.rebuild()

    @property
    def is_showing(self):
        return self.image["content"].is_showing

    def rebuild(self):
        text_surface = TextSurface(self.content, self.font, limit_size=(self.content_width, -1), style=self.style) 
        title_surface = TextSurface(self.title, self.font.copy())
        background = self.image["background"]
        self.image = CombinedSurface(background.get_size(), [[background, (0, 0), "background"],
                                                             [text_surface, (self.content_x, self.content_y), "content"],
                                                            [title_surface, (self.title_x, self.title_y), "title"]])
        if self.is_hovered:
            self.image.add_surface(self.instruct, (1050, 200), "instruct")
        
    def redraw(self):
        self.image.redraw()

    def advance_text(self):
        if not self.is_showing:
            self.next_text()
        else:
            self.image["content"].skip()
        
    def next_text(self):
        pygame.event.post(pygame.event.Event(NEXT_TEXT, {}))
            
    def on_hovered(self):
        self.image["background"].set_alpha(150)
        self.image.add_surface(self.instruct, (1050, 200), "instruct")
        self.redraw()
            
    def on_unhovered(self):
        self.image["background"].set_alpha(70)
        self.image.remove_surface("instruct")
        self.redraw()

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1:
                    self.advance_text()
                    
    def say(self, text, character):
        self.image["title"].font.color = character.color
        self.set_title(character.name)
        self.set_content(text)
    
    def set_content(self, text=""):
        self.content = text
        self.image["content"].set_text(text)
    
    def set_title(self, text=""):
        self.title = text
        if text:
            text = self.title_formatter.format(text)
        self.image["title"].set_text(text)

    def set_style(self, style):
        self.image["content"].set_style(style)
        
class ImageSprite(GameSprite):
    def __init__(self, image, manager=None, pos=(0,0), animation=None):
        self.image = None
        super().__init__(manager, animation=animation)
        self.image = ImageSurface(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def __getattr__(self, name):
        return getattr(self.image, name)
        
class TextSprite(GameSprite):
    def __init__(self, text="", font=None, manager=None, pos=(0,0), animation=None, limit_size = (-1, -1), style=None, transform=None):
        self.image = None
        super().__init__(manager, animation=animation)
        self.image = TextSurface(text, font, limit_size, style, transform)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
    @property
    def text(self):
        return self.image.text
    
    @text.setter
    def text(self, value):
        self.image.text = value
    
    def __getattr__(self, name):
        return getattr(self.image, name, None)
    
class Character:
    def __init__(self, name, manager=None, surface=None, color=pygame.Color('white')):
        self.manager = manager or _default_manager
        self.name = name
        self.color = color
        self.surface = surface
        self.manager.characters.append(self)
        
    def kill(self):
        self.manager.characters.remove(self)

class Scene:
    def __init__(self, surface=None, manager=None):
        if not manager:
            manager = _default_manager
        self.manager = manager
        if not surface:
            background = pygame.Surface(manager.size, flags=pygame.SRCALPHA)
            surface = CombinedSurface(background.get_size(), [[background, (0, 0), "background"]])
        self.surface = surface
        self.images = []
        
    def set_background(self, surface, **kwargs):
        if not isinstance(surface, pygame.Surface):
            surface = ImageSurface(surface)
            size = surface.get_size()
            surface.transform = Transform([self.manager.width/size[0], self.manager.height/size[1]])
            surface.redraw()

        if isinstance(self.surface, CombinedSurface):
            self.surface["background"] = surface
        else:
            self.surface = surface
        
        
    def draw(self, screen):
        screen.blit(self.surface, (0, 0))
        
    def load(self):
        pass
        
    def unload(self):
        self.manager.clear()
        
    def process_event(self, event):
        pass

class MainMenuScene(Scene):
    def __init__(self, surface=None, manager=None):
        super().__init__(surface, manager)
        self.surface.fill(pygame.Color('white'))
        self.buttons = []
        
    def load(self):
        self.buttons.append(Button(None, (0,0), self.manager, "开始游戏", lambda: self.manager.load_scene("InGame")))
        self.buttons.append(Button(None, (0,50), self.manager, "读取游戏", lambda: print("读取游戏")))
        self.buttons.append(Button(None, (0,100), self.manager, "设置", lambda: print(3)))
        self.buttons.append(Button(None, (0,150), self.manager, "关于", lambda: print(4)))
        self.buttons.append(Button(None, (0,200), self.manager, "帮助", lambda: print(5)))
        self.buttons.append(Button(None, (0,250), self.manager, "退出", lambda: sys.exit()))
        self.title = TextSprite("Title", Font(size=200), self.manager, (200, 300))
        self.title.set_animation([{"t":0, "alpha":0, "y":0}, {"t":10, "alpha":-255, "y":-100}])
        
    def draw(self, screen):
        super().draw(screen)
        
class LoadingScene(Scene):
    def __init__(self, surface=None, manager=None):
        super().__init__(surface, manager)
        buttons = []
        
class InGameScene(Scene):
    def __init__(self, surface=None, manager=None):
        super().__init__(surface, manager)
        self.images = []
        layout=Layout(1, vertical_spacing=50, rect_width=200, rect_height=50)
        self.buttons = ButtonGroup(layout=layout, manager=self.manager, button_background=lambda: RectSurface(self.buttons.layout.rect_size, (255, 255, 255, 100), (255, 255, 255),5), font = lambda: self.manager.font.copy(color = [241, 158, 194]))
        
    def load(self):
        self.buttons.create("返回主菜单", lambda: self.manager.load_scene("MainMenu"))
        self.buttons.create("跳转", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("回退", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("历史", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("读取", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("保存", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("快速保存", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("快速读取", lambda: self.manager.load_scene("InGame"))
        self.buttons.create("菜单", lambda: self.manager.load_scene("InGame"))
        def on_h(self):
            self.image["background"].color = [255, 255, 255, 150]
            self.image["background"].border_color = [255, 255, 0]
            self.image["background"].redraw()
            self.image["text"].font.color = [255, 255, 255]
            self.image["text"].redraw()
        def on_uh(self):
            self.image["background"].color = [255, 255, 255, 100]
            self.image["background"].border_color = [255, 255, 255]
            self.image["background"].redraw()
            self.image["text"].font.color = [241, 158, 194]
            self.image["text"].redraw()
        for button in self.buttons:
            button.on_hovered = types.MethodType(on_h, button)
            button.on_unhovered = types.MethodType(on_uh, button)
        self.text_field = TextField(None, self.manager, style="typewriter")
        self.manager.text_handler = self.text_field
        self.manager.continue_chapter()
        
    def set_background(self, surface, is_clear=True):
        if is_clear:
            self.clear_images()
        super().set_background(surface)
        
    def clear_images(self):
        for image in self.images:
            image.kill()
        self.images = []
        
    def unload(self):
        super().unload()
        self.manager.text_handler = None
        self.buttons.kill()
        
    def draw(self, screen):
        super().draw(screen)
         
class Chapter:
    def __init__(self, manager=None):
        if not manager:
            manager = _default_manager
        self.manager = manager
        self.screenplays = {"default":[]}
        self.current_operation_id = 0
        self.current_lable = "default"
        self.operations = {
            "say": self.say,
            "play_music": self.play_music,
            "set_background": self.set_background,
            "show_image": self.show_image,
            "show_character": self.show_character,
            "show_menu": self.show_menu,
            "end": self.end,
            "jump": self.jump
        }
    
    @property
    def current_screenplay(self):
        return self.screenplays.get(self.current_lable)
        
    @property
    def current_operation(self):
        return self.current_screenplay[self.current_operation_id]
        
    @staticmethod
    def _find_next_key(dictionary, key):
        keys_list = list(dictionary.keys())
        if key in keys_list:
            given_key_index = keys_list.index(key)
            if given_key_index + 1 < len(keys_list):
                return keys_list[given_key_index + 1]
        return None
    
    def do_operation(self, operation):
        name = operation["operation"]
        data = operation["data"]
        if name in self.operations:
            return self.operations[name](data)
        elif hasattr(self.manager):
            return getattr(self.manager, name)(data)
        else:
            print(f"wrong operation {name}")
            return False
    
    def say(self, data):
        self.manager.say(data["text"], data["character"])
        return True

    def play_music(self, data):
        self.manager.play_music(data["music"])

    def set_background(self, data):
        self.manager.set_background(data["surface"])

    def show_image(self, data):
        self.manager.show_image(data["image"], data["pos"], data["animation"])
        
    def hide_image(self, data):
        self.manager.hide_image(data["image"])
        
    def destory_image(self, data):
        self.manager.destory_image(data["image"])

    def show_character(self, data):
        # Implementation for show_character
        pass

    def show_menu(self, data):
        self.manager.show_menu(data["options"])
        return True

    def end(self):
        self.end()
        return True

    def jump(self, data):
        # Implementation for jump
        pass
    
    def next_operate(self):
        while True:
            if self.current_operation_id >= len(self.current_screenplay):
                self.end()
                return
            result = self.do_operation(self.current_operation)
            self.current_operation_id += 1
            if result:
                return
           
    def end(self):
        pygame.event.post(pygame.event.Event(END_CHAPTER, {}))

    def add_page(self, operation="say", data={}, screenplay=None, position=-1):
        if screenplay is None:
            screenplay = self.current_screenplay
        elif isinstance(screenplay, str):
            screenplay = self.screenplays[screenplay]
            
        page = {"operation": operation, "data": data}
        if position == -1:
            screenplay.append(page)
        else:
            screenplay.insert(position, page)

    def load(self):
        pass
    
    def load_dict(self, data):
        self.current_lable = data["current_lable"]
        self.current_operation_id = data["current_operation_id"]
    
    @property
    def save_dict(self):
        return {"current_lable":self.current_lable,
                "current_operation_id":self.current_operation_id}
        
class Manager:
    def __init__(self, screen:pygame.Surface, font:Font=None):
        global _default_manager
        if _default_manager is None:
            _default_manager = self
        self.screen = screen
        self.font = font or Font()
        self.font
        self.sprite_group = pygame.sprite.LayeredUpdates()
        self.text_handler = None
        self.event_handler = {}
        self.scenes = {}
        self.current_scene_name = ""
        self.characters = []
        self.default_character = Character("", color=(100, 255, 150))
        self.characters.append(self.default_character)
        self.chapter = None
        self.is_music_pause=False
        
    def load_scene(self, name:str):
        if self.current_scene_name:
            self.current_scene.unload()
        self.current_scene_name = name
        self.current_scene.load()
        
    @property
    def size(self):
        return self.screen.get_size()
        
    @property
    def width(self):
        return self.size[0]
        
    @property
    def height(self):
        return self.size[1]
    
    @property
    def current_scene(self):
        return self.scenes.get(self.current_scene_name)
    
    def continue_chapter(self):
        if self.chapter:
            self.chapter.next_operate()
    
    def clear(self):
        for sprite in self.sprite_group:
            sprite.kill()
        
    def draw(self):
        if self.current_scene:
            self.current_scene.draw(self.screen)
        self.sprite_group.draw(self.screen)
        
    def ensure_character(self, character:Union[Character, str]=None, allow_create=True):
        if isinstance(character, str):
            for c in self.characters:
                if c.name == character:
                    return c
            if allow_create:
                character = Character(character)
                self.characters.append(character)
                
        if character is None:
            return self.default_character
        return character
        
    def update(self, delta_time: float=0.03):
        for sprite in self.sprite_group:
            sprite.update(delta_time)
        
    def process_event(self, event:pygame.Event):
        if self.current_scene:
            self.current_scene.process_event(event)
        for sprite in self.sprite_group:
            sprite.process_event(event)
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.text_handler:
                    self.text_handler.advance_text()

    def switch_scene(self, scene_name:str):
        if scene_name in self.scenes:
            self.current_scene = scene_name
        else:
            print(f"Error: Scene '{scene_name}' not found.")
            
    def say(self, text="", character:Union[Character, str]=None):
        if not self.text_handler:
            return
        
        character = self.ensure_character(character)
        self.text_handler.say(text, character)
            
    def show_menu(self, options:list):
        self.branch_button = BranchButton(options, self)
        
    def show_image(self, image, pos=(0, 0), animation=None):
        image = ImageSprite(image, self, pos, animation)
        if hasattr(self.current_scene, "images"):
            self.current_scene.images.append(image)
        return image
    
    def hide_image(self, image):
        image.visible = False
        print("TODO")
    
    def destory_image(self, image):
        image.kill()
        print("TODO")
        
    def set_background(self, surface:pygame.Surface, is_clear=True):
        self.current_scene.set_background(surface, is_clear=is_clear)
    
    def play_music(self, music:str):
        pygame.mixer.music.load(music)
        pygame.mixer.music.play()
        
    def pause_music(self):
        self.is_music_pause = True
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        self.is_music_pause = False
        pygame.mixer.music.unpause()
          
class Game:
    def __init__(self, window_resolution: Tuple[int, int], font: Union[str, Font], name="Game Name"):
        pygame.init()
        self.screen = pygame.display.set_mode(window_resolution)
        self.name = name
        pygame.display.set_caption(name)
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        if isinstance(font, str):
            self.font = Font(font)
        else:
            self.font = font
        self.manager = Manager(self.screen, self.font)
        main_menu_scene = MainMenuScene(manager=self.manager)
        in_game_scene = InGameScene(manager=self.manager)
        self.manager.scenes["MainMenu"] = main_menu_scene
        self.manager.scenes["InGame"] = in_game_scene
        self.manager.load_scene("MainMenu")
        
    def run(self):
        while True:
            self.delta_time = self.clock.tick(60) / 1000
            self.manager.update(self.delta_time)
            self.process_events()
            self.game_logic()
            self.draw()
            pygame.display.update()
            
    def game_logic(self):
        pass

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            self.manager.process_event(event)
            self.process_event(event)
            
    def process_event(self, event):
        pass
                
    def draw(self):
        self.screen.fill(pygame.Color('white'))
        self.manager.draw()