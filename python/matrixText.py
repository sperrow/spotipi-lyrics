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
        self.textColor1 = graphics.Color(223, 255, 223)
        self.textColor2 = graphics.Color(52, 255, 103)
        self.line_len = 16
        self.line_height = 8
        self.max_lines = 4
        self.scroll_speed = 2

    def displayText(self, line_1, line_2, scroll_counter=0, is_lyrics=True):
        self.offscreen_canvas.Clear()
        fragments_1 = self.breakText(line_1)
        fragments_2 = self.breakText(line_2)
        self.draw(fragments_1, fragments_2, scroll_counter, is_lyrics)
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
    
    def breakText(self, line):
        char_pos = 0
        fragments = []
        while char_pos < len(line):
            while line[char_pos].isspace():
                char_pos += 1
            line_text = line[char_pos:char_pos+self.line_len]
            fragments.append(line_text)
            char_pos += self.line_len
        return fragments
    
    def draw(self, fragments_1, fragments_2, scroll_counter, is_lyrics=True):
        self.canvas_y = 6
        show_2 = True
        if (scroll_counter > 0):
            scroll_height = scroll_counter * self.scroll_speed
            line_count = len(fragments_1)
            if (not is_lyrics):
                # count both line_1 and line_2 (i.e., title and artist)
                line_count += len(fragments_2)
            if (line_count > self.max_lines):
                # reset to initial height if it's been scrolling for a while
                reset = (line_count - 3) * self.line_height
                scroll_height = scroll_height % reset
                self.canvas_y -= scroll_height
                # line_2 should be shown if it's the artist, not if it's a lyric
                show_2 = not is_lyrics
        
        for fragment in fragments_1:
            graphics.DrawText(self.offscreen_canvas, self.font, 0, self.canvas_y, self.textColor1, fragment)
            self.canvas_y += self.line_height
        if (show_2):
            for fragment in fragments_2:
                graphics.DrawText(self.offscreen_canvas, self.font, 0, self.canvas_y, self.textColor2, fragment)
                self.canvas_y += self.line_height

    def clear(self):
        self.offscreen_canvas.Clear()
        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)