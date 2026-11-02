"""Rebuild the dated project blueprint with embedded fonts and vector diagrams.

Run from the repository root using a Python environment with ReportLab.
Content is an audited snapshot, not live provider or job state.
"""
from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/YouTube_Automation_System_Blueprint.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for key,file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(key,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
W,H=595.276,841.89
INK=HexColor('#242422'); MUTED=HexColor('#65645f'); PAPER=HexColor('#faf8f2')
ACC=HexColor('#ac4d2c'); PLUM=HexColor('#66526c'); LINE=HexColor('#d8d3c8'); TINT=HexColor('#eee9dd')
STYLE=ParagraphStyle('body',fontName='Body',fontSize=10.1,leading=14.6,textColor=INK)
SMALL=ParagraphStyle('small',parent=STYLE,fontSize=8.5,leading=11.7)
CELL=ParagraphStyle('cell',parent=STYLE,fontSize=8.8,leading=12)
BOLD=ParagraphStyle('label',parent=STYLE,fontName='Bold',fontSize=10.5,leading=14)
C=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
C.setTitle('YouTube Automation - System Blueprint')
C.setAuthor('Project documentation')
C.setSubject('Audited architecture, creative formats, AI roles, workflows and implementation roadmap')
pages=[]; Y=0

def para(s,width,style=STYLE):
    p=Paragraph(s,style); _,h=p.wrap(width,1000); return p,h

def check(y):
    if y<62:raise RuntimeError(f'Page {len(pages)} overflows: y={y:.1f}')

def text(s,style=STYLE,gap=8):
    global Y
    p,h=para(s,W-88,style);check(Y-h);p.drawOn(C,44,Y-h);Y-=h+gap

def sub(s):
    global Y
    Y-=6;text(s,BOLD,5)

def callout(title,body):
    global Y
    p,h=para(body,W-114,SMALL);height=h+40;check(Y-height)
    C.setFillColor(TINT);C.roundRect(44,Y-height,W-88,height,6,fill=1,stroke=0)
    C.setFillColor(ACC);C.rect(44,Y-height,3,height,fill=1,stroke=0)
    C.setFont('Bold',9.5);C.drawString(57,Y-16,title)
    p.drawOn(C,57,Y-29-h);Y-=height+12

def table(headers,rows,widths=None):
    global Y
    width=W-88
    widths=[width/len(headers)]*len(headers) if widths is None else [width*v/sum(widths) for v in widths]
    th=ParagraphStyle('th',parent=CELL,textColor=white,fontName='Bold')
    for ri,row in enumerate([headers]+rows):
        parts=[para(str(v),w-15,th if ri==0 else CELL) for v,w in zip(row,widths)]
        rh=max(h for _,h in parts)+15;check(Y-rh)
        C.setFillColor(INK if ri==0 else (TINT if ri%2 else PAPER));C.rect(44,Y-rh,width,rh,fill=1,stroke=0)
        x=44
        for (p,h),w in zip(parts,widths):p.drawOn(C,x+7,Y-7-h);x+=w
        C.setStrokeColor(LINE);C.setLineWidth(.35);C.line(44,Y-rh,W-44,Y-rh);Y-=rh
    Y-=12

def arrow(x1,y1,x2,y2):
    C.setStrokeColor(MUTED);C.setFillColor(MUTED);C.setLineWidth(.9);C.line(x1,y1,x2,y2)
    a=math.atan2(y2-y1,x2-x1);l=5
    p=C.beginPath();p.moveTo(x2,y2);p.lineTo(x2-l*math.cos(a-.5),y2-l*math.sin(a-.5));p.lineTo(x2-l*math.cos(a+.5),y2-l*math.sin(a+.5));p.close();C.drawPath(p,fill=1,stroke=0)

def flow(steps,caption='',cols=3):
    global Y
    bw=(W-88-18*(cols-1))/cols;bh=69;rows=math.ceil(len(steps)/cols);total=rows*bh+(rows-1)*24
    check(Y-total-25)
    for i,(title,body,kind) in enumerate(steps):
        r=i//cols;k=i%cols;x=44+k*(bw+18);y=Y-r*(bh+24)-bh
        C.setFillColor(TINT if kind!='ai' else HexColor('#e9e2eb'));C.setStrokeColor(PLUM if kind=='ai' else LINE)
        C.roundRect(x,y,bw,bh,5,fill=1,stroke=1)
        p,h=para(f'<b>{i+1}. {title}</b>',bw-16,SMALL);p.drawOn(C,x+8,y+bh-8-h)
        p,h=para(body,bw-16,SMALL);p.drawOn(C,x+8,y+bh-25-h)
        if k>0:arrow(x-17,y+bh/2,x-2,y+bh/2)
    Y-=total+9
    if caption:text(caption,SMALL,8)

def layout():
    global Y
    height=250;check(Y-height-20)
    schemes=[('Three blocks',[(.2,'Small caption strip'),(.4,'Visual A'),(.4,'Visual B')]),('Clip + gameplay',[(.55,'Source clip'),(.45,'Gameplay')]),('Single focus',[(1,'Full-frame footage<br/>+ small captions')])]
    for i,(label,blocks) in enumerate(schemes):
        x=58+i*170;y=Y-230;ww=130;hh=230
        C.setStrokeColor(INK);C.setFillColor(white);C.roundRect(x,y,ww,hh,8,fill=1,stroke=1)
        yy=Y
        for j,(frac,label2) in enumerate(blocks):
            bh=hh*frac;C.setFillColor([TINT,HexColor('#e9e2eb'),HexColor('#dedbd2')][j%3]);C.rect(x+3,yy-bh+3,ww-6,bh-6,fill=1,stroke=0)
            p,h=para(label2,ww-16,SMALL);p.drawOn(C,x+8,yy-bh/2-h/2);yy-=bh
        C.setFillColor(INK);C.setFont('Bold',9);C.drawCentredString(x+ww/2,y-17,label)
    Y-=height+15

def start(title,kicker='SYSTEM BLUEPRINT'):
    global Y
    if pages:C.showPage()
    pages.append(title)
    C.setFillColor(PAPER);C.rect(0,0,W,H,fill=1,stroke=0)
    C.setFillColor(ACC);C.setFont('Bold',8.3);C.drawString(44,H-40,kicker)
    C.setFillColor(INK);C.setFont('Bold',22);C.drawString(44,H-76,title)
    C.setStrokeColor(LINE);C.line(44,H-92,W-44,H-92)
    C.setFont('Body',8);C.setFillColor(MUTED);C.drawString(44,32,'YT AUTOMATION / AUDITED SNAPSHOT / 02 NOV 2026');C.drawRightString(W-44,32,f'{len(pages):02d}')
    C.bookmarkPage('p'+str(len(pages)));C.addOutlineEntry(title,'p'+str(len(pages)),level=0,closed=False)
    Y=H-112

exec((Path(__file__).with_name('blueprint_content.py')).read_text(encoding='utf-8'))
C.save()
print(f'Created {OUT} with {len(pages)} pages')
