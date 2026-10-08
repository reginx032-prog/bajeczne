"""Prepare reviewed, non-destructive photo crops for the supplied October batch."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('C:/Users/Admin/Desktop/psy')
rows = json.loads((OUT/'source-review.json').read_bytes())
new = [r for r in rows if r['status'] == 'new']

crops = [
    [220,260,840,1120], [230,240,840,1120], [190,240,840,1120],
    [210,220,900,1200], [160,100,900,1200],
    [160,350,900,1200], [100,420,840,1120], [200,320,840,1120],
    [220,300,840,1120], [200,260,840,1120],
    [250,290,840,1120], [150,220,900,1200], [310,400,840,1120], [220,180,900,1200],
    [270,350,840,1120], [270,340,840,1120], [150,200,960,1280], [170,160,960,1280],
    [180,200,900,1200], [60,120,960,1280], [90,160,900,1200],
    [160,120,900,1200], [250,150,900,1200],
    [90,120,960,1280], [100,100,960,1280], [240,80,900,1200],
    [280,100,900,1200], [210,120,900,1200], [120,60,900,1200],
    [240,60,900,1200], [0,240,900,1200],
    [130,100,900,1200], [0,40,960,1280], [20,60,960,1280],
    [20,70,960,1280], [170,180,960,1280], [100,150,960,1280],
]
assert len(crops) == len(new) == 37
dogs = [
    {'name':'Haczi','slug':'haczi','color':'Beżowy','coat':'Krótkowłosy','sex':'Samiec',
     'ask':'Hacziego','time':'20.58.19','crop':[140,180,960,960],
     'alt':'Haczi, beżowy piesek Chihuahua krótkowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Czaruś','slug':'czarus','color':'Liliowy','coat':'Długowłosy','sex':'Samiec',
     'ask':'Czarusia','time':'20.51.50','crop':[90,100,900,900],
     'alt':'Czaruś, liliowy piesek Chihuahua długowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Coddy','slug':'coddy','color':'Czekoladowy','coat':'Długowłosy','sex':'Samiec',
     'ask':'Coddy’ego','time':'20.49.10','crop':[80,80,1040,1040],
     'alt':'Coddy, czekoladowy piesek Chihuahua długowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Havana','slug':'havana','color':'Biało-beżowy','coat':'Krótkowłosy','sex':'Samica',
     'ask':'Havanę','time':'20.44.22','crop':[120,200,1080,1080],
     'alt':'Havana, biało-beżowa suczka Chihuahua krótkowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Heidi','slug':'heidi','color':'Czarny','coat':'Krótkowłosy','sex':'Samica',
     'ask':'Heidi','time':'20.42.29','crop':[170,170,900,900],
     'alt':'Heidi, czarna suczka Chihuahua krótkowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Hela','slug':'hela','color':'Niebieski','coat':'Krótkowłosy','sex':'Samica',
     'ask':'Helę','time':'20.38.38','crop':[180,410,780,780],
     'alt':'Hela, niebieska suczka Chihuahua krótkowłosego z hodowli Bajeczne Urwisy'},
    {'name':'Hana','slug':'hana','color':'Niebieski','coat':'Krótkowłosy','sex':'Samica',
     'ask':'Hanę','time':'20.34.29','crop':[160,240,900,900],
     'alt':'Hana, niebieska suczka Chihuahua krótkowłosego z hodowli Bajeczne Urwisy'},
]
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for start in range(0,len(new),15):
    group = new[start:start+15]
    sheet = Image.new('RGB',(1100,((len(group)+4)//5)*322),'#f7f4ee')
    draw = ImageDraw.Draw(sheet)
    for i,row in enumerate(group):
        crop = crops[start+i]
        row['crop'] = crop
        x,y,w,h = crop
        photo = ImageOps.exif_transpose(Image.open(SOURCE/row['file'])).convert('RGB')
        assert x >= 0 and y >= 0 and x+w <= photo.width and y+h <= photo.height
        thumb = photo.crop((x,y,x+w,y+h)).resize((210,280),Image.Resampling.LANCZOS)
        sx,sy = (i%5)*220,(i//5)*322
        sheet.paste(thumb,(sx+5,sy))
        draw.text((sx+5,sy+283),row['dog']+' '+row['file'].split(' at ')[1].replace('.jpeg',''),font=font,fill='#222')
    sheet.save(OUT/f'gallery-crops-{start//15+1}.jpg',quality=92)
sheet = Image.new('RGB',(1280,680),'#f7f4ee')
draw = ImageDraw.Draw(sheet)
for i,dog in enumerate(dogs):
    dog['file'] = f'WhatsApp Image 2026-10-07 at {dog["time"]}.jpeg'
    photo = ImageOps.exif_transpose(Image.open(SOURCE/dog['file'])).convert('RGB')
    x,y,w,h = dog['crop']
    assert x >= 0 and y >= 0 and x+w <= photo.width and y+h <= photo.height
    thumb = photo.crop((x,y,x+w,y+h)).resize((300,300),Image.Resampling.LANCZOS)
    sx,sy = (i%4)*320,(i//4)*340
    sheet.paste(thumb,(sx+10,sy))
    draw.text((sx+10,sy+308),dog['name'],font=font,fill='#222')
sheet.save(OUT/'card-crops.jpg',quality=93)
(OUT/'batch-plan.json').write_text(json.dumps({'photos':new,'dogs':dogs},ensure_ascii=False,indent=2),encoding='utf8')
print('Prepared 37 gallery crops and 7 square card portraits for review.')
