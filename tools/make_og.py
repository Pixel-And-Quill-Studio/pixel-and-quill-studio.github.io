"""Builds public/og-<lang>.png (1200x630 share images, one per language, from that language's Sentence screenshots, English ones when the language has none) and og.png (= English). Run from public/.
Japanese and Korean need a CJK font: set OG_FONT_JA / OG_FONT_KO to a static Regular Noto Sans JP / KR (SIL OFL; instance the variable font at wght=400 first) or install fonts-noto-cjk."""
import json,os,shutil
from PIL import Image,ImageDraw,ImageFont,ImageFilter
G=[x for x in json.load(open('../src/data/games.json'))['games'] if x['slug']=='sentence'][0]
SUB=G['subtitle']; TAG={k:v.split('\n') for k,v in G['hero_tagline'].items()}
CJK={'ja':os.environ.get('OG_FONT_JA','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
     'ko':os.environ.get('OG_FONT_KO','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')}
DEJAVU='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(path,size):
  f=ImageFont.truetype(path,size)
  try: f.set_variation_by_axes([400])  # variable CJK fonts default to their thinnest weight
  except Exception: pass
  return f
for L in ['en','fr','es','pt-BR','de','it','ja','ko']:
  TF=CJK.get(L,DEJAVU)
  W,H=1200,630; im=Image.new('RGB',(W,H),(11,11,13)); d=ImageDraw.Draw(im)
  for r in range(700,0,-10):
    c=int(42*(1-r/700)); d.ellipse((150-r,-200-r,150+r,-200+r),fill=(c+11,int(c*.86)+11,int(c*.5)+13))
  base=f'assets/games/sentence/shots/{L.lower()}/'
  if not os.path.isdir(base): base='assets/games/sentence/shots/en/'
  for x,y,s,n in [(700,95,.5,'loss'),(1060,95,.5,'win'),(880,45,.56,'card')]:
    w,h=int(540*s),int(960*s); p=Image.open(base+n+'.webp').convert('RGB').resize((w,h),Image.LANCZOS)
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),18,fill=255)
    sd=Image.new('RGBA',(w+40,h+40),(0,0,0,0)); ImageDraw.Draw(sd).rounded_rectangle((20,20,w+20,h+20),18,fill=(0,0,0,200)); sd=sd.filter(ImageFilter.GaussianBlur(12))
    im.paste(sd,(x-w//2-20,y-10),sd); im.paste(p,(x-w//2,y),m)
    ImageDraw.Draw(im).rounded_rectangle((x-w//2,y,x+w//2-1,y+h-1),18,outline=(184,151,90),width=2)
  dr=ImageDraw.Draw(im)
  f1=ImageFont.truetype('assets/PlayfairDisplaySC-Black.ttf',72); f2=F(TF,28)
  sz=28
  while max(F(TF,sz).getlength(x) for x in TAG[L])>490: sz-=1
  f2=F(TF,sz)
  f3=ImageFont.truetype('assets/AllertaStencil-Regular.ttf',22)
  dr.text((58,160),'SENTENCE',font=f1,fill=(224,194,122)); dr.text((62,252),SUB[L].upper(),font=f3 if L not in CJK else F(TF,22),fill=(184,151,90))
  dr.text((60,320),TAG[L][0],font=f2,fill=(232,227,214)); dr.text((60,360),TAG[L][1],font=f2,fill=(232,227,214))
  dr.text((62,500),'PIXEL & QUILL STUDIO',font=f3,fill=(169,162,147)); dr.text((62,532),'ANDROID - GOOGLE PLAY',font=f3,fill=(169,162,147))
  im.save(f'og-{L.lower()}.png',optimize=True)
shutil.copy('og-en.png','og.png')
