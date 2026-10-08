"""One-time visual selection. IDs refer to the reviewed originals contact sheets."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json

ROOT=Path(__file__).resolve().parent.parent
records=json.loads((ROOT/'_preview/originals-inventory.json').read_text(encoding='utf8'))
by_id={r['id']:r for r in records}
maltese={7,8,9,10,11,12,13,15,16,18,20,21,22,23,24,25,35,37,41,43,45,74,75,76,77,78,79,80,89}
# Previously exported crops of the same exposure: retain the complete original.
cropped_copies={1:196,213:116,214:116,219:113,220:113,221:115,222:115,232:52,
250:114,251:101,252:105,253:104,254:109,255:96,256:92,257:28,258:68,261:72,262:55}
# x/y centre and width in percent. Group photographs use the complete frame.
crops={
2:(50,50,100),3:(50,50,100),4:(49,43,92),5:(49,44,93),
7:(50,50,56),8:(56,50,56),9:(52,50,56),12:(53,55,90),13:(53,55,90),
14:(48,49,94),15:(46,53,84),16:(43,55,90),17:(48,50,94),18:(49,43,86),19:(54,51,88),
22:(49,58,72),24:(50,51,73),25:(50,45,90),26:(45,51,85),27:(44,51,86),28:(50,46,92),29:(50,44,96),30:(44,50,94),
31:(51,47,75),32:(48,39,88),33:(50,45,80),34:(45,47,78),35:(55,63,73),36:(50,50,75),37:(51,51,78),38:(51,47,95),39:(52,51,74),40:(50,52,75),
41:(47,49,78),42:(47,50,76),43:(47,50,100),44:(47,49,81),45:(50,64,86),46:(50,45,80),47:(50,51,74),48:(54,51,72),49:(49,47,83),50:(54,47,85),
51:(51,51,82),52:(53,44,72),53:(50,51,77),54:(52,46,82),55:(50,47,87),56:(50,49,84),57:(52,52,85),58:(49,48,95),59:(50,51,77),60:(50,51,75),
61:(51,43,88),62:(48,49,82),63:(52,45,89),64:(54,47,84),65:(51,48,91),66:(54,46,91),67:(53,47,82),68:(51,46,88),69:(52,49,77),70:(52,44,92),
71:(51,43,90),72:(50,43,84),73:(53,48,93),75:(52,43,86),79:(65,50,56.25),81:(52,53,78),82:(53,54,78),83:(52,49,76),84:(51,49,81),85:(51,46,88),
86:(51,53,76),87:(50,51,100),88:(50,52,88),89:(50,53,82),90:(52,45,95),91:(51,47,85),92:(48,50,95),93:(53,51,100),94:(50,47,100),95:(51,46,89),
96:(46,49,75),97:(50,46,90),98:(53,51,88),99:(49,43,91),100:(49,44,91),101:(51,44,92),102:(51,49,84),103:(52,56,100),104:(51,48,91),
105:(51,47,90),107:(51,44,91),108:(52,52,81),109:(49,45,91),110:(51,51,100),111:(51,52,100),112:(51,49,89),113:(58,48,76),114:(52,52,100),115:(53,52,87),
116:(52,50,75),117:(51,50,75),118:(51,50,75),119:(51,49,83),120:(51,48,92)
}
groups={10,11,20,23,74,76,77,78,80,196}
# Short factual descriptions of what is actually visible, without invented names.
alts={
7:'Biały maltańczyk wśród jesiennych liści',8:'Maltańczyk na rękach w ogrodzie',9:'Biały maltańczyk na tle zieleni',10:'Dwa białe maltańczyki razem w domu',11:'Trzy szczenięta maltańczyka na miękkim kocu',
12:'Maltańczyk na brzoskwiniowym kocu',13:'Odpoczywający maltańczyk na brzoskwiniowym kocu',15:'Maltańczyk w ogrodzie przy zabawkach',16:'Maltańczyk obok donicy z kwiatami',18:'Maltańczyk trzymany na rękach w ogrodzie',
20:'Dwa maltańczyki z pomarańczową piłeczką',22:'Maltańczyk leżący obok pomarańczowej piłeczki',23:'Dwa maltańczyki podczas zabawy w domu',24:'Biały maltańczyk odpoczywający w domu',25:'Szczenię maltańczyka na dłoni opiekuna',
35:'Maltańczyk przy wiklinowym fotelu',37:'Maltańczyk na białym kocu w ogrodzie',41:'Maltańczyk na turkusowym kocu wśród kwiatów',43:'Maltańczyk odpoczywający na szarej sofie',45:'Maltańczyk odpoczywający na tarasie',
74:'Dwa szczenięta maltańczyka na różowej pościeli',75:'Szczenię maltańczyka obok dłoni opiekuna',76:'Maltańczyki na sofie obok pluszowej zabawki',77:'Maltańczyki odpoczywające na ciemnym kocu',78:'Maltańczyki podczas zabawy przy sofie',79:'Portret szczenięcia maltańczyka na dłoni',80:'Maltańczyki i ich pluszowa zabawka',89:'Maltańczyk na trawie w ogrodzie',
196:'Cztery szczenięta Chihuahua odpoczywające razem',2:'Trzy szczenięta Chihuahua na różowym kocu',3:'Szczenięta Chihuahua przytulone na kocu'
}
old_crops=json.loads((ROOT/'_preview/chihuahua-import.json').read_text(encoding='utf-8-sig'))
old_by_src={'assets/photos/chihuahua-2026/'+p['file']:p for p in old_crops}
canonical={}
for r in sorted(records,key=lambda r:(0 if r['src'] in old_by_src else 1,r['id'])):
    if r['id']==6 or r['id'] in cropped_copies: continue
    canonical.setdefault(r['pixels'],r)
chosen=list(canonical.values())
alias_map={r['src']:canonical[r['pixels']]['src'] for r in records if r['id']!=6 and r['id'] not in cropped_copies}
for a,b in cropped_copies.items(): alias_map[by_id[a]['src']]=alias_map[by_id[b]['src']]
photos=[]
for r in chosen:
    n=r['id'];src=r['src'];w,h=r['size']
    same_ids={x['id'] for x in records if x['pixels']==r['pixels']}
    breed='maltanczyki' if same_ids & maltese else 'chihuahua'
    group=n in groups
    if src in old_by_src:
        old=old_by_src[src];rect=old['rect']
    else:
        cx,cy,wp=crops.get(n,(50,50,100));cw=min(w*wp/100,h*.75);ch=cw/.75
        left=max(0,min(w-cw,w*cx/100-cw/2));top=max(0,min(h-ch,h*cy/100-ch/2));rect=[left,top,cw,ch]
    left,top,cw,ch=rect
    x=left/(w-cw)*100 if w>cw else 50;y=top/(h-ch)*100 if h>ch else 50
    if src in old_by_src:
        num=old_by_src[src]['id'];color='Czarny' if num<=14 else 'Czarny podpalany' if num<=23 else 'Szary podpalany' if num<=31 else 'Czekoladowy' if num<=54 or 62<=num<=66 else 'Szary'
        alt=f'{color} Chihuahua na '+('białym kocu w ogrodzie' if num<=66 else 'zdjęciu z codziennych chwil')
    else: alt=alts.get(n,'Chihuahua '+('na rękach opiekuna' if n in {4,5,28,29,32,33,34,36,44,49,50,53,54,56,59,62,64,65,66,67,70,71,73,85,95,97,99,100,101,105,107,109,112,113,116,117,118,119,120} else 'z rodzinnej hodowli Bajeczne Urwisy'))
    photos.append({'id':n,'breed':breed,'src':src,'alt':alt,'width':w,'height':h,'crop':rect,'x':round(x,3),'y':round(y,3),'scale':round(min(w,h*.75)/cw,5),'fit':'contain' if group else 'cover','aliases':[a for a,b in alias_map.items() if b==src and a!=src]})
photos.sort(key=lambda p:(p['breed'],0 if p['src'] in old_by_src else 1,p['id']))
data=ROOT/'data';data.mkdir(exist_ok=True)
(data/'gallery-photos.json').write_text(json.dumps({'photos':photos,'excluded':[{'src':by_id[6]['src'],'reason':'Logo, nie fotografia psa'}]},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for start in range(0,len(photos),36):
    s=Image.new('RGB',(1200,6*286),(245,242,236));d=ImageDraw.Draw(s)
    for j,p in enumerate(photos[start:start+36]):
        im=ImageOps.exif_transpose(Image.open(ROOT/p['src'])).convert('RGB')
        if p['fit']=='contain': im=ImageOps.contain(im,(192,256))
        else:
            x,y,w,h=p['crop'];im=im.crop((x,y,x+w,y+h)).resize((192,256),Image.Resampling.LANCZOS)
        x=(j%6)*200;y=(j//6)*286;s.paste(im,(x+(192-im.width)//2,y+(256-im.height)//2));d.text((x+5,y+260),f"{p['id']} | {p['breed']}",fill='black')
    s.save(ROOT/f'_preview/gallery-review-{start//36+1}.jpg',quality=90)
print(json.dumps({'photos':len(photos),'breeds':{b:sum(p['breed']==b for p in photos) for b in ('chihuahua','maltanczyki')},'aliasCopies':sum(len(p['aliases']) for p in photos)},ensure_ascii=False))
