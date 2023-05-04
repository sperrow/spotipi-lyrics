import os
import configparser

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

class MatrixText(object):
    def __init__(self):
        # Configuration file
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, '../config/rgb_options.ini')

        # Configuration for the matrix
        config = configparser.ConfigParser()
        config.read(filename)
        options = RGBMatrixOptions()
        options.rows = int(config['DEFAULT']['rows'])
        options.cols = int(config['DEFAULT']['columns'])
        options.chain_length = int(config['DEFAULT']['chain_length'])
        options.parallel = int(config['DEFAULT']['parallel'])
        options.hardware_mapping = config['DEFAULT']['hardware_mapping']
        options.gpio_slowdown = int(config['DEFAULT']['gpio_slowdown'])
        options.brightness = int(config['DEFAULT']['brightness'])
        options.limit_refresh_rate_hz = int(config['DEFAULT']['refresh_rate'])

        self.matrix = RGBMatrix(options=options)

        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        font_path = os.path.join(dir, "../fonts/4x6.bdf")
        self.font = graphics.Font()
        self.font.LoadFont(font_path)
        self.textColor = graphics.Color(223, 255, 223)
        self.textColor2 = graphics.Color(52, 255, 103)
        self.line_len = 16
        self.line_height = 8

    def displayText(self, line_1, line_2):
        self.offscreen_canvas.Clear()
        self.canvas_y = 6

        self.breakLine(line_1, self.textColor)
        if (len(line_2) > 0):
            self.breakLine(line_2, self.textColor2)
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def breakLine(self, line, color):
        char_pos = 0
        while char_pos < len(line):
            while line[char_pos].isspace():
                char_pos += 1
            line_text = line[char_pos:char_pos+self.line_len]
            graphics.DrawText(self.offscreen_canvas,
                              self.font, 0, self.canvas_y, color, line_text)
            char_pos += self.line_len
            self.canvas_y += self.line_height
