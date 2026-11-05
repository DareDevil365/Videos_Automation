"""Registered GIF/still attachments; local frame-clock animation, never remote URLs."""
from PIL import Image,ImageOps,ImageSequence
from ..core import Held


class Attachment:
    def __init__(self,path):
        self.frames=[];self.ends=[];cursor=0
        with Image.open(path) as raw:
            if getattr(raw,'n_frames',1)>240:raise Held('chat_attachment','Keep reaction GIFs within 240 frames.')
            for frame in ImageSequence.Iterator(raw):
                tile=ImageOps.contain(frame.convert('RGBA'),(440,260),Image.Resampling.LANCZOS)
                canvas=Image.new('RGBA',(440,260));canvas.alpha_composite(tile,((440-tile.width)//2,(260-tile.height)//2))
                self.frames.append(canvas);cursor+=max(.04,min(2,frame.info.get('duration',100)/1000));self.ends.append(cursor)
        self.duration=cursor;self.animated=len(self.frames)>1

    def at(self,second):
        t=max(0,second)%self.duration
        return next(frame for frame,end in zip(self.frames,self.ends) if t<end)
