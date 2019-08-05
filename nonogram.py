#!/usr/bin/env python3
import argparse
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from satsolver import solve


class Nonogram(object):
    def __init__(self, filepath):
        img = Image.open(filepath).convert('RGB')
        self.col_number, self.row_number = img.size
        self.data_matrix = np.zeros(shape=(self.col_number, self.row_number), dtype=int)
        self.cols, self.rows = self.count_pixels(img)
        self.row_padding = max(map(len, self.cols))
        self.col_padding = max(map(len, self.rows))
        self.is_solved = False
        self.image_padding = 5
        self.scale = 1
        self._pixel_size = 20
        self._font_size = 12
        self._font_padding_x = 2
        self._font_padding_y = 3
        self._pixel_padding = 3
        self.font = 'DejaVuSans.ttf'
        self.background_color = '#161618'
        self.grid_bold_color = '#ee4d2e'
        self.grid_color = '#444'
        self.font_color = '#fff'
        self._grid_width = 1

    @property
    def pixel_padding(self):
        return int(self._pixel_padding * self.scale)

    @property
    def pixel_size(self):
        return int(self._pixel_size * self.scale)

    @property
    def font_size(self):
        return int(self._font_size * self.scale)

    @property
    def font_padding_x(self):
        return int(self._font_padding_x * self.scale)

    @property
    def font_padding_y(self):
        return int(self._font_padding_y * self.scale)

    @property
    def grid_width(self):
        return int(self._grid_width * self.scale)

    @property
    def grid_bold_width(self):
        return int(self._grid_width * self.scale * 2)

    def save(self, filepath, solve: bool):
        width, height = self.col_number + self.col_padding, self.row_number + self.row_padding
        width *= self.pixel_size
        height *= self.pixel_size
        width += self.image_padding * 2
        height += self.image_padding * 2
        out = Image.new('RGB', (width, height), self.background_color)
        self.draw_grid(out)
        self.draw_numbers(out)
        if solve:
            self.solve()
            self.draw_board(out)
        out.save(filepath)

    def save_json(self, filepath):
        with open(filepath, 'w') as f:
            json.dump([self.rows, self.cols], f)

    def solve(self) -> None:
        solve(self.rows, self.cols, self.data_matrix)

    def draw_board(self, img) -> None:
        """Draws fields inside self.data_matrix. Used for solving the board"""
        draw = ImageDraw.Draw(img)
        for x, col in enumerate(self.data_matrix):
            for y, value in enumerate(col):
                x_pixel = x * self.pixel_size + self.col_padding * self.pixel_size + self.image_padding
                y_pixel = y * self.pixel_size + self.row_padding * self.pixel_size + self.image_padding
                if value > 0:
                    padding = self.pixel_padding
                    coordinates = (x_pixel + padding, y_pixel + padding,
                                   x_pixel + self.pixel_size - padding,
                                   y_pixel + self.pixel_size - padding)
                    draw.rectangle(coordinates, fill=self.font_color)
                elif value < 0:
                    padding = self.pixel_padding
                    coordinates = (x_pixel + padding, y_pixel + padding,
                                   x_pixel + self.pixel_size - padding,
                                   y_pixel + self.pixel_size - padding)
                    draw.line(coordinates, fill=self.font_color)
                    coordinates = (coordinates[0], coordinates[3], coordinates[2], coordinates[1])
                    draw.line(coordinates, fill=self.font_color)

    def draw_numbers(self, img) -> None:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font, size=self.font_size)
        x = self.col_padding * self.pixel_size + self.image_padding + self.font_padding_x
        for col in self.cols:
            y = (self.row_padding - 1) * self.pixel_size + self.image_padding + self.font_padding_y
            for value in col[::-1]:
                if value < 10:
                    additional_space = self.font_size / 3
                else:
                    additional_space = 0
                draw.text((x + additional_space, y), str(value), font=font, fill=self.font_color)
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
                draw.text((x + additional_space, y), str(value), font=font, fill=self.font_color)
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
            draw.line((x, self.image_padding, x, height - self.image_padding), fill=self.grid_bold_color,
                      width=self.grid_bold_width)
        # draw.line((width - self.image_padding, self.image_padding, width - self.image_padding, height - self.image_padding), fill=self.grid_bold_color, width=self.grid_bold_width)
        for y in range(self.image_padding + self.row_padding * self.pixel_size, height, self.pixel_size * 5):
            draw.line((self.image_padding, y, width - self.image_padding, y), fill=self.grid_bold_color,
                      width=self.grid_bold_width)
            # draw.line((self.image_padding, height - self.image_padding, width - self.image_padding, height - self.image_padding), fill=self.grid_bold_color, width=self.grid_bold_width)

    def count_pixels(self, img):
        width, height = img.size

        def count(count_axis, secondary_axis, get_pixel_value):
            result = []
            counter = 0
            for i in range(secondary_axis):
                row = []
                for j in range(count_axis):
                    value = get_pixel_value(i, j)
                    if value:
                        counter += 1
                    if not value or j == count_axis - 1:
                        if counter != 0:
                            row.append(counter)
                        counter = 0
                result.append(row)
            return result

        cols = count(height, width, lambda x, y: self.value_of(img, x, y))
        rows = count(width, height, lambda y, x: self.value_of(img, x, y))
        return cols, rows

    def value_of(self, img, x, y):
        r, g, b = img.getpixel((x, y))
        return False if (r + g + b) / 3 > 127 else True


def hexcolor(value) -> str:
    if value.startswith('#'):
        value = value[1:]
    valid_chars = '0123456789abcdefABCDEF'
    for c in value:
        if c not in valid_chars:
            raise ValueError('Invalid color, color must be provided in hex')
    if len(value) != 3 and len(value) != 6:
        raise ValueError('Invalid color, must be exactly 3 or 6 characters long')
    return '#{0}'.format(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to the image that should be nonofied')
    parser.add_argument('output', help='Path for the generated nonogram')
    parser.add_argument('-s', '--scale', default=1, help='Scaling of the output image', type=float)
    parser.add_argument('-bc', '--background-color', default='#fff', help='Background color', type=hexcolor)
    parser.add_argument('-fc', '--font-color', default='#000', help='Font color', type=hexcolor)
    parser.add_argument('-gc', '--grid-color', default='#888', help='Grid color', type=hexcolor)
    parser.add_argument('-gbc', '--grid-bold-color', default='#000', help='Grid bold color', type=hexcolor)
    parser.add_argument('-pp', '--pixel-padding', default=3, help='Scaling of the output image', type=float)
    parser.add_argument('--solve', action='store_true', help='Generate images which solve the puzzle')
    parser.add_argument('--json', help='JSON output path', type=str)
    args = parser.parse_args()
    try:
        nonogram = Nonogram(args.filepath)
    except IOError as e:
        sys.exit('Error: {0}'.format(e.strerror))
    nonogram.scale = args.scale
    nonogram.background_color = args.background_color
    nonogram.grid_bold_color = args.grid_bold_color
    nonogram.grid_color = args.grid_color
    nonogram.font_color = args.font_color
    nonogram._pixel_padding = args.pixel_padding
    nonogram.save(args.output, args.solve)
    if args.json:
        nonogram.save_json(args.json)
