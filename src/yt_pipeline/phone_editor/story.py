"""Story clock -> isolated conversation -> trusted screen/effect composition."""
from .contract import compile_beats
from .messenger import chat_frame
from .screens import event_screen


def elapsed_text(previous, current):
    minutes = lambda t: int(t[:2])*60+int(t[3:])
    difference = minutes(current)-minutes(previous)
    if difference >= 60:
        hours, rest = divmod(difference,60)
        return f'{hours} hour'+('s' if hours != 1 else '')+(f' {rest} min' if rest else '')+' later'
    return f'{difference} min later'


def story_frame(script, index, second, duration, typing, avatars=None, wallpapers=None):
    story=script['phone_story'];beats=compile_beats(script);beat=beats[index]
    thread=next(t for t in story['threads'] if t['id']==beat['thread_id'])
    contact=next(c for c in story['contacts'] if c['id']==thread['contact_id'])['name']
    # Include only already reached messages from THIS private thread. Returning
    # to it restores its own history; another chat's messages never leak across.
    indices=[i for i in range(index+1) if beats[i]['thread_id']==beat['thread_id']]
    conversation={**script,'units':[{**script['units'][i],'_story_time':beats[i]['time']} for i in indices]}
    prefix=beat['prefix_seconds'];local=max(0,second-prefix)
    battery=5 if any('low_battery'==event['type'] for row in beats[:index+1] for event in row['events']) else 82
    settings={'pov':story['pov'],'contact':contact,'theme':thread['theme'],'time':beat['time'],
              'battery':battery,'focus':index in (0,len(script['units'])-1) or (len(script['units'][index]['text'].split())<=4 and '?' in script['units'][index]['text']),'wallpaper':(wallpapers or {}).get(thread['id'])}
    picture,meta=chat_frame(conversation,len(indices)-1,local,max(.1,duration-prefix),typing,avatars,settings)
    meta.update(thread_id=thread['id'],screen='chat',prefix_seconds=prefix,phone_story=True)
    for event in beat['events']:
        if event['start']<=second<event['end']:
            kind=event['type'];progress=(second-event['start'])/(event['end']-event['start'])
            previous_time=beats[index-1]['time'] if index else beat['time']
            picture=event_screen(kind,progress,picture,contact=contact,time=beat['time'],text=script['units'][index]['text'],
                theme=thread['theme'],avatar=(avatars or {}).get(contact),elapsed_label=elapsed_text(previous_time,beat['time']) if any(e['type']=='time_jump' for e in beat['events']) else 'Today')
            # Notifications intentionally preview this incoming message; other
            # event screens never claim that the future chat bubble is visible.
            meta.update(screen=kind,message_arrived=kind=='notification',visible_unit_ids=[script['units'][index]['id']] if kind=='notification' else [])
            break
    return picture,meta
