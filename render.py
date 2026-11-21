from collections import Counter
from pathlib import Path
import math
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SCALE = 3
PAPER = '#f6f1e5'
INK = '#191919'
RED = '#7f1d1d'
GREEN = '#14532d'
SEA = '#5b7186'
SAND = '#e2d8bc'
RULE = '#b9ad98'
image = Image.new('RGB', (1024 * SCALE, 1024 * SCALE), PAPER)
draw = ImageDraw.Draw(image)


def font(size, kind='body'):
    names = {'body': 'NotoSans-Condensed', 'bold': 'NotoSans-CondensedBold',
             'head': 'NotoSerifDisplay-Bold', 'mast': 'NotoSerifDisplay-Black'}
    path = Path('/usr/share/fonts/truetype/noto') / (names[kind] + '.ttf')
    if not path.exists():
        path = Path('/usr/share/fonts/truetype/dejavu') / (
            'DejaVuSerif-Bold.ttf' if kind in ('head', 'mast') else 'DejaVuSans.ttf')
    return ImageFont.truetype(str(path), round(size * SCALE))


def width(text, size, kind='body'):
    if '−' in text:
        return sum(draw.textlength(piece, font=font(size, kind)) for piece in text.split('−')) / SCALE + text.count('−') * draw.textlength('−', font=minus_font(size)) / SCALE
    return draw.textlength(text, font=font(size, kind)) / SCALE


def minus_font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', round(size * SCALE))


def text(position, value, size=11, kind='body', fill=INK, anchor=None):
    if '−' in value:
        x, y = (round(item * SCALE) for item in position)
        if anchor == 'mt':
            x -= width(value, size, kind) * SCALE / 2
        elif anchor == 'rt':
            x -= width(value, size, kind) * SCALE
        primary = font(size, kind)
        baseline = y - primary.getbbox(value, anchor='ls')[1]
        for index, piece in enumerate(value.split('−')):
            if index:
                fallback = minus_font(size)
                draw.text((x, baseline), '−', font=fallback, fill=fill, anchor='ls')
                x += draw.textlength('−', font=fallback)
            draw.text((x, baseline), piece, font=primary, fill=fill, anchor='ls')
            x += draw.textlength(piece, font=primary)
        return
    draw.text(tuple(round(item * SCALE) for item in position), value,
              font=font(size, kind), fill=fill, anchor=anchor or 'lt')


def line(points, fill=RULE, thickness=0.6):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
              fill=fill, width=max(1, round(thickness * SCALE)))


def rect(box, fill, outline=None, thickness=1):
    draw.rectangle(tuple(round(item * SCALE) for item in box), fill=fill,
                   outline=outline, width=round(thickness * SCALE))


def ellipse(box, fill, outline=None, thickness=1):
    draw.ellipse(tuple(round(item * SCALE) for item in box), fill=fill,
                 outline=outline, width=round(thickness * SCALE))


def polygon(points, fill):
    draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill)


def wrap(value, available, size=11, kind='body'):
    rows = []
    current = ''
    for word in value.split():
        candidate = (current + ' ' + word).strip()
        if width(candidate, size, kind) > available:
            if not current:
                raise ValueError('Word exceeds column: ' + word)
            rows.append(current)
            current = word
        else:
            current = candidate
    if current:
        rows.append(current)
    return rows


def paragraph(value, x, y, available, size=11, kind='body', leading=None,
              fill=INK, max_rows=None):
    rows = wrap(value, available, size, kind)
    if max_rows is not None and len(rows) > max_rows:
        raise ValueError(f'Text needs {len(rows)} rows, allowed {max_rows}: {value}')
    for index, row in enumerate(rows):
        text((x, y + index * (leading or size * 1.16)), row, size, kind, fill)
    return len(rows) * (leading or size * 1.16)


STORIES = [
    (1, 'EUROPE', 'War & security', 'Russian missiles come down in Poland', ''),
    (2, 'EUROPE', 'Climate', 'COP31 runs into overtime, no deal', 'Antalya talks pass their Friday deadline; the draft still names no fossil fuels.'),
    (3, 'AMERICAS', 'Markets & business', 'Wall Street slides into correction', 'S&P 500 −3.7%, Nasdaq −5.3% as AI shares sink; Anthropic −11% after its debut.'),
    (4, 'EUROPE', 'Politics', 'UK and EU sign Brussels deals', 'Food checks go from 2028, carbon markets link, 100,000 youth places a side.'),
    (5, 'MID EAST', 'War & security', 'Saudi–Houthi escalation', 'Three missiles downed over Riyadh; the coalition strikes Hodeidah port.'),
    (6, 'EUROPE', 'War & security', "Russia strikes Kyiv's bridges", 'Three crossings hit; at Kryvyi Rih 2 die and 42 are hurt, four of them children.'),
    (7, 'ASIA', 'Politics', 'Shenzhen summit ends in a declaration', 'Trump, Xi, Putin on nuclear war and oil; humans to keep control of military AI.'),
    (8, 'ASIA', 'Justice', 'Myanmar rejects the genocide ruling', "Naypyidaw calls Thursday's World Court verdict 'unfair'; China objects too."),
    (9, 'MID EAST', 'War & security', 'EU: keep the Gaza ceasefire', 'Brussels appeals to Israel as a drone strike kills one in Gaza.'),
    (10, 'AMERICAS', 'Tech & AI', "Trump threatens a ban and a 'tremendous tax' on US firms building AI data centres overseas.", ''),
    (11, 'AMERICAS', 'Tech & AI', 'House panel: US approved sales of nearly 900,000 AI chips to Chinese firms in six months.', ''),
    (12, 'ASIA', 'Politics', 'Rubio confirms a Quad business forum for early 2027, after the Manila summit.', ''),
    (13, 'ASIA', 'Markets & business', 'IndusInd Bank fires its ex-CEO Kathpalia and claws back his pay to 2020.', ''),
    (14, 'AMERICAS', 'Justice', 'US court: the 2022 $1.7tn spending law was passed unconstitutionally, by proxy votes.', ''),
    (15, 'AMERICAS', 'Politics', "A judge rejects Trump's revamp of a $4bn homelessness programme.", ''),
    (16, 'AMERICAS', 'Politics', "Mamdani plans to close New York's Rikers Island jail by 2032.", ''),
    (17, 'AMERICAS', 'Justice', 'Los Angeles jury convicts Jonathan Rinderknecht of starting the Palisades Fire.', ''),
    (18, 'AMERICAS', 'Justice', 'US teen pleads not guilty in a plot to attack an Indian shrine in Illinois.', ''),
    (19, 'AMERICAS', 'Politics', 'Congress scrambles to avert a shutdown amid Iran tensions.', ''),
    (20, 'ASIA', 'Politics', "Bangladesh's PM blames India and the Awami League for the latest violence.", ''),
    (21, 'MID EAST', 'War & security', 'Iraqi forces retake Jurf al-Sakhar after 12 years under Kataib Hezbollah.', ''),
    (22, 'WORLD', 'Aid & society', 'The UN cuts its food-aid target despite looming hunger.', ''),
    (23, 'WORLD', 'Justice', "Reuters: at least 17 women from ex-Soviet states drawn into Epstein's network.", ''),
    (24, 'EUROPE', 'Justice', 'Spain frees US donor James Cox over an FBI translation error.', ''),
    (25, 'EUROPE', 'Justice', 'French police officers sentenced over the beating of producer Michel Zecler.', ''),
    (26, 'EUROPE', 'Politics', 'Rival Czech rallies clash over the future of state media.', ''),
    (27, 'EUROPE', 'Politics', 'Denmark, the US and Greenland sign a security deal to ease strains.', ''),
    (28, 'EUROPE', 'War & security', 'UK official: Britain has carried out cyber attacks on Moscow.', ''),
    (29, 'AFRICA', 'Aid & society', 'Nearly 600 women killed in South Africa within three months.', ''),
    (30, 'ASIA', 'Politics', 'Malaysia removes a post announcing Rohingya resettlement to Turkey.', ''),
    (31, 'EUROPE', 'Politics', 'EU grants €1bn more in military aid to Ukraine: drones, air defence.', ''),
    (32, 'EUROPE', 'Politics', "Berlin hosts a 'coalition of the willing' on Ukraine, with Zelenskyy.", ''),
    (33, 'SPORT', 'Sport', 'Cricket: Rahul 93 not out as India reach 239-1 in Wellington.', ''),
    (34, 'SPORT', 'Sport', 'Cricket: Hazlewood backs Cummins as the sandpaper row reignites.', ''),
    (35, 'SPORT', 'Sport', 'Rugby: Mostert in for injured Nortje as the Springboks face Ireland in Dublin.', ''),
]


def counts_bar(y, labels, field):
    counts = Counter(story[field] for story in STORIES)
    assert sum(counts.values()) == 35
    values = [f'{label} {counts[label]}' for label in labels]
    total = sum(width(value, 11, 'bold') for value in values)
    gap = (976 - total) / (len(values) - 1)
    assert gap > 3
    x = 24
    for value in values:
        text((x, y), value, 11, 'bold', GREEN)
        x += width(value, 11, 'bold') + gap


def star(x, y, radius=6, color=RED):
    polygon([(x + math.sin(index * math.pi / 5) * (radius if index % 2 == 0 else radius * .42),
              y - math.cos(index * math.pi / 5) * (radius if index % 2 == 0 else radius * .42))
             for index in range(10)], color)


def lead_map():
    rect((24, 260, 480, 333), SAND)
    polygon([(24, 260), (310, 260), (274, 269), (219, 272), (178, 266), (136, 276), (84, 275), (24, 281)], SEA)
    poland = [(145, 267), (202, 271), (247, 266), (283, 272), (303, 286),
              (294, 302), (315, 318), (288, 330), (251, 326), (230, 330),
              (195, 328), (167, 326), (155, 311), (143, 298)]
    polygon(poland, '#f2eacb')
    line(poland + [poland[0]], '#9c927d', 1)
    line([(303, 286), (294, 302), (315, 318), (288, 330)], INK, 2)
    text((42, 263), 'BALTIC SEA', 11, 'bold', PAPER)
    text((180, 279), 'POLAND', 16, 'bold')
    text((365, 311), 'UKRAINE', 15, 'bold')
    for x, y, label, dx, dy in [(238, 303, 'WARSAW', -49, -1), (236, 321, 'KRAKÓW', -54, 0),
                                (322, 322, 'LVIV', 8, 0), (420, 289, 'KYIV', 9, -5)]:
        ellipse((x - 2, y - 2, x + 2, y + 2), INK)
        text((x + dx, y + dy), label, 11, 'bold')
    star(299, 318, 8)
    text((331, 267), 'CRASH SITE', 11, 'bold', RED)
    line([(337, 280), (309, 308)], RED, 1)
    points = [(464 - index * 8, 280 + (index / 20) ** 2 * 32) for index in range(21)]
    for index in range(0, 20, 2):
        line(points[index:index + 2], RED, 2)
    polygon([(299, 318), (312, 305), (317, 316)], RED)


def draw_scene(number, x, y, w, h):
    backgrounds = {2: '#e9d9b6', 3: '#dbe1df', 4: '#dce3df', 5: '#e6d7c4',
                   6: '#d9e1e4', 7: '#dfded2', 8: '#e6dccb', 9: '#dce6da'}
    rect((x, y, x + w, y + h), backgrounds[number])
    base = y + h - 4
    center = x + w / 2
    if number == 2:
        ellipse((x + 18, y + 4, x + 35, y + 21), '#b97535')
        ellipse((center - 49, y + 10, center + 49, y + 47), GREEN)
        rect((center - 55, y + 26, center + 55, base), GREEN)
        for offset in (-30, -10, 10, 30):
            line([(center + offset, y + 17), (center + offset, base)], '#9eaf91', 1)
        ellipse((x + w - 44, y + 5, x + w - 20, y + 29), PAPER, INK)
        line([(x + w - 32, y + 9), (x + w - 32, y + 17), (x + w - 25, y + 19)], INK, 1.3)
    elif number == 3:
        for index, height in enumerate([12, 24, 18, 30, 21, 27, 15, 24]):
            rect((x + 14 + index * 26, base - height, x + 32 + index * 26, base), SEA)
        points = [(x + 12, y + 6), (x + 55, y + 13), (x + 84, y + 9),
                  (x + 123, y + 22), (x + 161, y + 20), (x + w - 18, base)]
        line(points, RED, 3)
        polygon([(x + w - 18, base), (x + w - 30, base - 3), (x + w - 21, base - 11)], RED)
    elif number == 4:
        rect((x + 44, y + 4, x + 84, y + 22), '#344c68')
        line([(x + 44, y + 4), (x + 84, y + 22)], PAPER, 3)
        line([(x + 84, y + 4), (x + 44, y + 22)], PAPER, 3)
        line([(x + 64, y + 4), (x + 64, y + 22)], RED, 4)
        line([(x + 44, y + 13), (x + 84, y + 13)], RED, 4)
        rect((x + 153, y + 4, x + 193, y + 22), '#334e78')
        for index in range(8):
            angle = index * math.pi / 4
            ellipse((x + 172 + 7 * math.cos(angle), y + 12 + 6 * math.sin(angle),
                     x + 174 + 7 * math.cos(angle), y + 14 + 6 * math.sin(angle)), '#dbbd61')
        rect((x + 32, base - 8, x + w - 32, base), '#8d7354')
        for offset in (-32, 0, 32):
            polygon([(center + offset - 12, base - 13), (center + offset + 8, base - 13),
                     (center + offset + 15, base - 5), (center + offset - 8, base - 5)], PAPER)
    elif number == 5:
        for index, height in enumerate([12, 20, 14, 27, 18, 22]):
            rect((x + 28 + index * 30, base - height, x + 47 + index * 30, base), '#a28b73')
        polygon([(center - 15, y + 5), (center + 15, y + 5), (center + 13, y + 21),
                 (center, y + 32), (center - 13, y + 21)], GREEN)
        for offset in (0, 30, 60):
            line([(x + 12 + offset, y + 5), (x + 43 + offset, y + 12)], RED, 1.5)
    elif number == 6:
        rect((x, base - 10, x + w, y + h), SEA)
        for offset in (37, 89, 151, 202):
            rect((x + offset, y + 15, x + offset + 7, base), '#7b7770')
        line([(x + 12, y + 17), (center - 7, y + 17)], INK, 4)
        line([(center + 10, y + 20), (x + w - 12, y + 17)], INK, 4)
        line([(center - 5, y + 11), (center + 1, y + 18), (center - 4, y + 26)], RED, 2)
    elif number == 7:
        for index, height in enumerate([12, 19, 27, 16, 22, 30, 17, 24]):
            rect((x + 14 + index * 27, base - height, x + 33 + index * 27, base), SEA)
        for index in range(3):
            fx = x + 61 + index * 48
            line([(fx, y + 3), (fx, base)], INK, 1)
            rect((fx, y + 3, fx + 31, y + 19), RED if index < 2 else PAPER)
            if index == 0:
                for offset in (4, 9, 14):
                    line([(fx, y + offset), (fx + 31, y + offset)], PAPER, 1)
                rect((fx, y + 3, fx + 12, y + 12), SEA)
            elif index == 1:
                star(fx + 8, y + 10, 4, '#e3c267')
            else:
                rect((fx, y + 9, fx + 31, y + 14), SEA)
                rect((fx, y + 14, fx + 31, y + 19), RED)
    elif number == 8:
        line([(center, y + 6), (center, base - 2)], INK, 3)
        line([(center - 44, y + 12), (center + 44, y + 12)], INK, 2)
        for offset in (-35, 35):
            line([(center + offset, y + 12), (center + offset - 14, y + 27),
                  (center + offset + 14, y + 27), (center + offset, y + 12)], RED, 1)
            polygon([(center + offset - 16, y + 27), (center + offset + 16, y + 27),
                     (center + offset + 8, y + 33), (center + offset - 8, y + 33)], RED)
        rect((center - 23, base - 3, center + 23, base), INK)
    else:
        rect((x + 23, base - 9, x + w - 23, base), '#aaa38f')
        for offset in range(30, int(w - 22), 25):
            line([(x + offset, base - 9), (x + offset, base)], PAPER)
        polygon([(center - 17, y + 22), (center - 43, y + 6), (center - 8, y + 12),
                 (center + 5, y + 5), (center + 15, y + 12), (center + 38, y + 10),
                 (center + 17, y + 19), (center + 2, y + 28)], PAPER)
        line([(center + 28, y + 19), (center + 54, y + 13)], GREEN, 1.5)
        for offset in (35, 43, 51):
            ellipse((center + offset, y + 10, center + offset + 5, y + 14), GREEN)


def illustration(number, x, y, w, h):
    global draw
    scene = Image.new('RGB', (round(w * SCALE), 39 * SCALE), PAPER)
    original_draw = draw
    draw = ImageDraw.Draw(scene)
    draw_scene(number, 0, 0, w, 39)
    draw = original_draw
    image.paste(scene.resize((round(w * SCALE), round(h * SCALE)), Image.Resampling.LANCZOS),
                (round(x * SCALE), round(y * SCALE)))


def story_grid():
    for index, story in enumerate(STORIES[1:9]):
        number, region, field, headline, deck = story
        x = 24 + (index % 4) * 247
        y = 337 + (index // 4) * 108
        if index % 4:
            line([(x - 6, y), (x - 6, y + 102)])
        illustration(number, x, y, 235, 25)
        field_label = {'War & security': 'WAR', 'Markets & business': 'MARKETS'}.get(field, field.upper())
        text((x, y + 29), f'{number} · {region} · {field_label}', 11, 'bold', RED)
        paragraph(headline, x, y + 43, 235, 16, 'head', 17, max_rows=2)
        paragraph(deck, x, y + 80, 235, 11, leading=11.5, max_rows=2)


CONTINENTS = [
    [(-168, 70), (-142, 70), (-125, 59), (-107, 73), (-82, 76), (-53, 54),
     (-67, 45), (-80, 25), (-98, 16), (-112, 29), (-125, 48), (-158, 58)],
    [(-74, 12), (-50, 3), (-35, -7), (-43, -24), (-66, -55), (-77, -27), (-81, -4)],
    [(-52, 60), (-25, 72), (-30, 83), (-54, 81), (-65, 68)],
    [(-11, 36), (-10, 57), (10, 71), (28, 70), (40, 56), (34, 34), (13, 36)],
    [(-17, 32), (8, 37), (33, 30), (50, 10), (39, -14), (19, -35), (10, -22), (-5, 3)],
    [(29, 70), (66, 76), (114, 73), (157, 66), (178, 53), (141, 43),
     (130, 31), (109, 20), (119, 3), (102, -5), (78, 8), (67, 26), (44, 12), (34, 35)],
    [(112, -12), (137, -10), (153, -23), (146, -39), (117, -35)],
    [(130, 33), (142, 44), (145, 35), (138, 30)],
    [(47, -13), (51, -16), (48, -26), (44, -23)],
    [(166, -34), (179, -39), (171, -47), (165, -44)],
]


def inside(x, y, points):
    result = False
    previous = points[-1]
    for current in points:
        if (current[1] > y) != (previous[1] > y):
            crossing = (previous[0] - current[0]) * (y - current[1]) / (previous[1] - current[1]) + current[0]
            if x < crossing:
                result = not result
        previous = current
    return result


def world_map():
    left, top, wide, high = 639, 704, 360, 155

    def project(lon, lat):
        return left + (lon + 180) / 360 * wide, top + (83 - lat) / 143 * high

    for latitude in range(-54, 82, 5):
        for longitude in range(-177, 179, 5):
            if any(inside(longitude, latitude, continent) for continent in CONTINENTS):
                x, y = project(longitude, latitude)
                ellipse((x - 1.1, y - 1.1, x + 1.1, y + 1.1), SEA)
    pins = [(1, 23, 50, 807, 676), (2, 31, 37, 864, 692),
            (3, -74, 41, 716, 733), (4, 4, 51, 767, 693),
            (5, 47, 25, 890, 789), (6, 31, 50, 858, 672),
            (7, 114, 23, 945, 772), (8, 96, 20, 923, 811),
            (9, 34, 31, 828, 799)]
    for number, lon, lat, px, py in pins:
        x, y = project(lon, lat)
        line([(x, y), (px, py)], RED, .7)
        ellipse((x - 2, y - 2, x + 2, y + 2), RED)
        ellipse((px - 8, py - 8, px + 8, py + 8), RED)
        text((px, py - 7), str(number), 11, 'bold', PAPER, 'mt')
    text((650, 871), '1 Poland   2 Antalya   3 New York', 11, 'bold')
    text((650, 886), '4 Brussels   5 Riyadh   6 Kyiv', 11, 'bold')
    text((650, 901), '7 Shenzhen   8 Myanmar   9 Gaza', 11, 'bold')


def render():
    text((24, 20), 'LATE EDITION · ALL THE NEWS OF ONE DAY ON ONE PAGE', 11, 'bold')
    text((1000, 20), 'No. 2026-325', 11, 'bold', anchor='rt')
    line([(24, 36), (1000, 36)], INK)
    masthead = 'THE WORLD IN ONE DAY'
    mast_size = 57
    while width(masthead, mast_size, 'mast') > 976:
        mast_size -= 1
    text((512, 41), masthead, mast_size, 'mast', anchor='mt')
    rect((24, 105, 1000, 131), RED)
    text((512, 110), 'SATURDAY, 21 NOVEMBER 2026 — 35 STORIES · 6 REGIONS · ONE PAGE', 14, 'bold', PAPER, 'mt')
    counts_bar(137, ['EUROPE', 'AMERICAS', 'ASIA', 'MID EAST', 'WORLD', 'AFRICA', 'SPORT'], 1)
    counts_bar(153, ['War & security', 'Politics', 'Justice', 'Markets & business', 'Tech & AI', 'Climate', 'Aid & society', 'Sport'], 2)
    line([(24, 170), (1000, 170)], INK, 1.5)
    text((24, 176), 'EUROPE · WAR & SECURITY — THE LEAD', 11, 'bold', RED)
    text((24, 191), 'Russian missiles come down in Poland', 37, 'head')
    paragraph("Two Russian missiles and a suspected drone came down inside Poland during Moscow's overnight attack on Ukraine. A Kh-101 crashed in the south-east; nobody was hurt. Warsaw calls it a deliberate provocation — NATO, a grave violation of its airspace.",
              24, 231, 976, 12, leading=14, max_rows=2)
    lead_map()
    for value, y in [("Danish Gripen jets scrambled as the missiles crossed.", 269),
                     ("PM Tusk spoke out as Ukraine's allies held a military exercise in Poland.", 291)]:
        ellipse((498, y + 4, 502, y + 8), RED)
        paragraph(value, 511, y, 479, 13, leading=15, max_rows=2)
    paragraph('Some 100 missiles were fired at Ukraine overnight; three Kyiv crossings were also hit (story 6).',
              511, 324, 479, 11, leading=12, max_rows=2)
    story_grid()
    line([(24, 555), (1000, 555)], INK, 1.5)
    figures = [('−3.7%', 'S&P 500, into correction'), ('~100', 'missiles fired at Ukraine overnight'),
               ('3', 'Houthi missiles downed over Riyadh'), ('14+', 'Iranian tankers massing at Kharg Island'),
               ('€1bn', 'new EU military aid to Ukraine'), ('$120bn', 'adaptation pledge dropped at COP31')]
    for index, (number, label) in enumerate(figures):
        x = 24 + index * (976 / 6)
        if index:
            line([(x - 5, 560), (x - 5, 608)])
        text((x + 75, 558), number, 26, 'head', RED, 'mt')
        rows = wrap(label, 151, 11)
        for row_index, row in enumerate(rows):
            text((x + 75, 588 + row_index * 12), row, 11, anchor='mt')
    line([(24, 617), (1000, 617)], INK)
    text((24, 623), 'ALSO ON SATURDAY 21 NOVEMBER', 15, 'bold')
    text((645, 623), 'WHERE IT HAPPENED', 15, 'bold')
    line([(628, 623), (628, 931)])
    heights = []
    for column in range(2):
        x = 24 + column * 302
        y = 646
        for number, region, field, headline, deck in STORIES[9 + column * 13:22 + column * 13]:
            value = f'{number} {region} — {headline}'
            rows = wrap(value, 290, 11)
            for row in rows:
                text((x, y), row, 11)
                y += 11
        heights.append(y)
    print('Brief column bottoms:', heights)
    assert max(heights) <= 934, heights
    world_map()
    rect((24, 938, 1000, 976), None, RED, 1)
    text((32, 944), 'DATE CHECK', 11, 'bold', RED)
    paragraph("— Left out on purpose because they broke before today: the World Court's Myanmar genocide ruling itself (Thursday 19 Nov) — today's story is the reaction; the Barcelona cancer-pill results (Friday 20 Nov); Cyclone Akvan's landfall in Odisha (Friday 20 Nov); Indonesia's vice-president resigning (Thursday 19 Nov).",
              108, 944, 882, 11, leading=12, max_rows=2)
    paragraph('Drawn entirely by program · Set in Noto Serif Display & Noto Sans Condensed · Every story happened or was first reported Saturday 21 November 2026. Sources: Reuters, BBC, CNN, Le Monde, The Guardian, UN News, PBS, NPR, Nation Press, AAP. Original drawings.',
              24, 981, 976, 11, leading=11.5, max_rows=2)
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'entry.png'
    image.resize((1024, 1024), Image.Resampling.LANCZOS).save(output, optimize=True)


if __name__ == '__main__':
    render()
