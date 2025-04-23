# test_pdf.py

import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# путь к шрифту относительно корня проекта
dejavu_path = os.path.join('posts', 'utils', 'fonts', 'DejaVuSans.ttf')

# проверяем, что файл действительно есть
print("Test font exists:", os.path.isfile(dejavu_path))

# регистрируем шрифт под именем 'DejaVuSans'
pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))

# создаём простой PDF
c = canvas.Canvas("test.pdf")
c.setFont("DejaVuSans", 24)
c.drawString(100, 750, "Тест: кириллица должна отобразиться")
c.save()

print("test.pdf создан")
