import os


from PIL import Image, ImageDraw, ImageFont


from core.gantt.gantt_chart_data import GanttChartData


GREEN, RED, YELLOW, GRAY = (67, 160, 71), (229, 57, 53), (255, 193, 7), (158, 158, 158)
LINE, GRID, TEXT, BG = (25, 118, 210), (225, 225, 225), (30, 30, 30), (255, 255, 255)




_TTF = ['DejaVuSans.ttf', 'arial.ttf', 'Arial.ttf', 'Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/Arial.ttf', 'C:/Windows/Fonts/arial.ttf']
_HAS_TTF = False




def _font(size: int):
    """Fonte com acentos (TTF); se nenhuma existir, usa a padrão e rótulos sem acento."""
    global _HAS_TTF
    for name in _TTF:
        try:
            f = ImageFont.truetype(name, size)
            _HAS_TTF = True
            return f
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow antigo
        return ImageFont.load_default()




class ImageGenerator:
    """Desenha o Gantt: verde=execução, vermelho=sobrecarga, amarelo=espera,
    cinza=execução após o deadline, linha azul vertical=deadline absoluto."""


    def save(self, data: GanttChartData, path: str) -> None:
        # o eixo vai até o fim da simulação ou o maior deadline, o que for maior
        span = max(data.total_time, max(data.deadlines.values(), default=0))
        cell = max(10, min(32, 1400 // max(span, 1)))
        row_h, left, top = 36, 70, 60
        n = len(data.rows)
        width = left + cell * span + 30
        height = top + row_h * n + 80
        img = Image.new('RGB', (max(width, 920), height), BG)
        d = ImageDraw.Draw(img)
        f, fs = _font(14), _font(11)
        d.text((10, 10), f'Gantt - {data.title}', fill=TEXT, font=_font(18))


        step = 1 if cell >= 22 else 2 if cell >= 14 else 5
        for t in range(0, span + 1):
            x = left + t * cell
            d.line([(x, top), (x, top + row_h * n)], fill=GRID)
            if t % step == 0:
                d.text((x - 4, top - 18), str(t), fill=TEXT, font=fs)


        ypos = {pid: top + i * row_h for i, pid in enumerate(data.rows)}
        for pid, y in ypos.items():
            d.text((10, y + row_h // 2 - 7), pid, fill=TEXT, font=f)
            d.line([(left, y + row_h), (left + cell * span, y + row_h)], fill=GRID)


        color = {'exec': GREEN, 'overhead': RED, 'waiting': YELLOW, 'late': GRAY}
        for s in data.segments:
            y = ypos[s.pid]
            d.rectangle([left + s.start * cell, y + 6, left + s.end * cell, y + row_h - 6],
                        fill=color[s.kind], outline=BG)


        for pid, dl in data.deadlines.items():
            x, y = left + dl * cell, ypos[pid]
            d.line([(x, y + 1), (x, y + row_h - 1)], fill=LINE, width=3)


        ly = top + row_h * n + 25
        x = left
        labels = (('Execução', GREEN), ('Sobrecarga de contexto', RED), ('Espera', YELLOW),
                  ('Estouro de deadline', GRAY), ('Deadline (absoluto)', LINE))
        if not _HAS_TTF:
            labels = tuple((l.replace('ç', 'c').replace('ã', 'a'), c) for l, c in labels)
        for label, c in labels:
            d.rectangle([x, ly, x + 16, ly + 16], fill=c)
            d.text((x + 22, ly), label, fill=TEXT, font=f)
            x += 40 + int(d.textlength(label, font=f)) + 12
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        img.save(path)