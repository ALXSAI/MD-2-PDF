import ctypes

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import ImageFont


class MDPrinter():
    def __init__(self, name, end_margins=30):
        self.c = canvas.Canvas(name, pagesize=A4, bottomup=0)
        self.heigth, self.width = A4
        self.curheight = 10
        self.lines = []
        self.end_margins = end_margins
        self.line_length = (self.width - 2 * self.end_margins)*0.45

    def read_md(self, dir):
        file = open(dir, 'r')
        self.lines = file.readlines()
        for i in range(0, len(self.lines)):
            self.lines[i] = self.lines[i][0:-1]

    def draw_file(self):
        for i in self.lines:
            if i[0:3] == "---":
                self.c.line(x1=0, y1=self.curheight, x2=self.width, y2=self.curheight)
                self.next_line()
            else:
                font = self.get_font_size(i)
                size = self.get_text_dimensions(i,font)[0]
                if size >= self.line_length:
                    self.draw_long_text(font, i)
                else:
                    self.draw_text(i)

    def next_line(self, mod=1.0):
        if self.curheight >= self.heigth:
            self.end_page()
            self.curheight = 0
        else:
            self.curheight += 10 * mod

    def get_text_dimensions(self, text, points, font='Helvetica'):
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)

        return size.cx, size.cy

    def draw_long_text(self, font, text):
        text2 = text
        if self.get_text_dimensions(text=text2, points=font)[0] < self.line_length:
            self.draw_text(text2)
        else:
            temp = ""
            for i in range(0, len(text2)):
                if self.get_text_dimensions(text=text2[0:i], points=font)[0] <= self.line_length:
                    temp += text2[i]
                else:
                    text2 = text2[i:]
                    self.draw_text(temp)
                    break
            print("First part : " + temp)
            print("Second part : " + text2)
            self.draw_long_text(font, text2)

    def get_font_size(self,text):
        if text[0:4] == "####":
            self.c.setFont("Helvetica", 14)
            mod = 14
        elif text[0:3] == "###":
            self.c.setFont("Helvetica", 16)
            mod = 16
        elif text[0:2] == "##":
            self.c.setFont("Helvetica", 18)
            mod = 18
        elif text[0:1] == "#":
            self.c.setFont("Helvetica", 20)
            mod = 20
        else:
            self.c.setFont("Helvetica", 10)
            mod = 10
        return mod

    def draw_text(self, text):
        mod = self.get_font_size(text)
        if mod == 20:
            text = text[1:]
        elif mod == 18:
            text = text[2:]
        elif mod == 16:
            text = text[3:]
        elif mod == 14:
            text = text[4:]
        self.curheight -= (10 - 10 * mod / 10)
        self.c.drawString(self.end_margins, self.curheight, text)
        self.next_line(mod=mod / 10)

    def end_page(self):
        self.c.showPage()

    def save(self):
        self.c.save()


printer = MDPrinter("Test.pdf")
printer.read_md("J&DM-1.md")
printer.draw_file()
printer.end_page()
printer.save()
