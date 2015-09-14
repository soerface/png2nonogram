import sys
from PIL import Image, ImageDraw, ImageFont

class Nonogram(object):

    def __init__(self, filepath):
        img = Image.open(filepath).convert('RGB')
        self.col_number, self.row_number = img.size

        self.cols, self.rows = self.count_pixels(img)
        self.row_padding = max(map(len, self.cols))
        self.col_padding = max(map(len, self.rows))
        self.image_padding = 5
        self.scale = 1
        self._pixel_size = 20
        self._font_size = 12
        self._font_padding_x = 2
        self._font_padding_y = 3
        self.font = 'DejaVuSans.ttf'
        self.background_color = '#161618'
        self.grid_bold_color = '#ee4d2e'
        self.grid_color = '#444'
        self.font_color = '#fff'
        self._grid_width = 1

    @property
    def pixel_size(self):
        return self._pixel_size * self.scale

    @property
    def font_size(self):
        return self._font_size * self.scale

    @property
    def font_padding_x(self):
        return self._font_padding_x * self.scale

    @property
    def font_padding_y(self):
        return self._font_padding_y * self.scale

    @property
    def grid_width(self):
        return self._grid_width * self.scale

    @property
    def grid_bold_width(self):
        return self._grid_width * self.scale * 2

    def save(self, filepath):
        width, height = self.col_number + self.col_padding, self.row_number + self.row_padding
        width *= self.pixel_size
        height *= self.pixel_size
        width += self.image_padding * 2
        height += self.image_padding * 2
        out = Image.new('RGB', (width, height), self.background_color)
        self.draw_grid(out)
        self.draw_numbers(out)
        out.save(filepath)

    def draw_numbers(self, img):
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font, size=self.font_size)
        x = self.col_padding * self.pixel_size + self.image_padding + self.font_padding_x
        for col in self.cols:
            y = (self.row_padding - 1 ) * self.pixel_size + self.image_padding + self.font_padding_y
            for value in col[::-1]:
                if value < 10:
                    additional_space = self.font_size / 3
                else:
                    additional_space = 0
                draw.text((x+additional_space, y), str(value), font=font, fill=self.font_color)
                y -= self.pixel_size
            x += self.pixel_size
        y = self.row_padding * self.pixel_size + self.image_padding + self.font_padding_y
        for row in self.rows:
            x = (self.col_padding - 1) * self.pixel_size + self.image_padding + self.font_padding_x
            for value in row[::-1]:
                if value < 10:
                    additional_space = self.font_size / 3
                else:
                    additional_space = 0
                draw.text((x+additional_space, y), str(value), font=font, fill=self.font_color)
                x -= self.pixel_size
            y += self.pixel_size

    def draw_grid(self, img):
        draw = ImageDraw.Draw(img)
        width, height = img.size
        column_counter = -self.col_padding
        for x in range(self.image_padding, width - self.image_padding, self.pixel_size):
            if column_counter >= 0:
                padding = self.image_padding
            else:
                padding = self.image_padding + self.row_padding * self.pixel_size
            if column_counter > -self.col_padding:
                draw.line((x, padding, x, height - self.image_padding), fill=self.grid_color, width=self.grid_width)
            column_counter += 1
        row_counter = -self.row_padding
        for y in range(self.image_padding, height - self.image_padding, self.pixel_size):
            if row_counter >= 0:
                padding = self.image_padding
            else:
                padding = self.image_padding + self.col_padding * self.pixel_size
            if row_counter > -self.row_padding:
                draw.line((padding, y, width - self.image_padding, y), fill=self.grid_color, width=self.grid_width)
            row_counter += 1
        for x in range(self.image_padding + self.col_padding * self.pixel_size, width, self.pixel_size * 5):
            draw.line((x, self.image_padding, x, height - self.image_padding), fill=self.grid_bold_color, width=self.grid_bold_width)
        # draw.line((width - self.image_padding, self.image_padding, width - self.image_padding, height - self.image_padding), fill=self.grid_bold_color, width=self.grid_bold_width)
        for y in range(self.image_padding + self.row_padding * self.pixel_size, height, self.pixel_size * 5):
            draw.line((self.image_padding, y, width - self.image_padding, y), fill=self.grid_bold_color, width=self.grid_bold_width)
        # draw.line((self.image_padding, height - self.image_padding, width - self.image_padding, height - self.image_padding), fill=self.grid_bold_color, width=self.grid_bold_width)

    def count_pixels(self, img):
        width, height = img.size

        result = {}
        rows = []
        counter = 0
        for y in range(0, height):
            row = []
            for x in range(0, width):
                value = self.value_of(img, x, y)
                if value:
                    counter += 1
                if not value or x == width - 1:
                    if counter != 0:
                        row.append(counter)
                    counter = 0
            rows.append(row)
        cols = []
        counter = 0
        for x in range(0, width):
            col = []
            for y in range(0, height):
                value = self.value_of(img, x, y)
                if value:
                    counter += 1
                if not value or y == height - 1:
                    if counter != 0:
                        col.append(counter)
                    counter = 0
            cols.append(col)
        return cols, rows

    def value_of(self, img, x, y):
        r, g, b = img.getpixel((x, y))
        return False if (r + g + b) / 3 > 127 else True

if __name__ == '__main__':
    nonogram = Nonogram(sys.argv[1])
    if len(sys.argv) > 2:
        nonogram.scale = int(sys.argv[2])
    nonogram.background_color = '#fff'
    nonogram.grid_bold_color = '#000'
    nonogram.grid_color = '#888'
    nonogram.font_color = '#000'
    nonogram.save('out.png')