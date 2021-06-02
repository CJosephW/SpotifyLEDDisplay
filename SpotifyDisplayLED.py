import time
import sys
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
from PIL import ImageDraw
import requests

class SpotifyDisplayLED():

    def __init__(self) -> None:
        
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.hardware_mapping = 'regular'
        options.chain_length = 2
        options.parallel = 2
        options.pixel_mapper_config = "V-mapper"
        options.gpio_slowdown = 4
        options.limit_refresh_rate_hz = 350
        options.brightness = 85
        self.matrix = RGBMatrix(options = options)
        

    def startDisplay(self, url="https://images.unsplash.com/photo-1613329671121-5d1cf551cc3f?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=933&q=80", progress=0, title="waiting for music"):
        if(title == "waiting for music"):
            canvas = self.matrix.CreateFrameCanvas()
            image = Image.open(requests.get(url, stream = True).raw)
            newsize = (64,64)
            image = image.resize(newsize)
            image.convert('RGB')
            draw = ImageDraw.Draw(image)
            canvas.SetImage(image)
            font = graphics.Font()
            font.LoadFont('./4x6.bdf')
            text_color = graphics.Color(255,255,255)
            my_text = title
            graphics.DrawText(canvas, font, 16, 5, text_color, title)
            canvas = self.matrix.SwapOnVSync(canvas)

        else:
            canvas = self.matrix.CreateFrameCanvas()
            image = Image.open(requests.get(url,stream = True).raw)
            image.convert('RGB')
            prog_width = int(progress * 64)
            draw = ImageDraw.Draw(image)
            if(prog_width > 1):
                draw.line((0, 1,prog_width, 1), fill=(0, 255, 0))
            canvas.SetImage(image)
            font = graphics.Font()
            font.LoadFont("./4x6.bdf")
            text_color = graphics.Color(0,0,0)
            my_text = title
            graphics.DrawText(canvas, font, 16, 5, text_color, title)
            canvas = self.matrix.SwapOnVSync(canvas)
        


