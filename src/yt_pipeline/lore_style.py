"""Script-focus decisions for hybrid comic art; author annotations, not pixel taste scores."""
from copy import deepcopy

from .core import Held


# Ordinal editorial estimates, not measured recognition probabilities.
PROFILES = {
    'doom': dict(detail=2, geometric_clarity=3),
    'thor': dict(detail=3, geometric_clarity=2),
    'bill': dict(detail=3, geometric_clarity=1),
    'hellboy': dict(detail=2, geometric_clarity=3),
    'vision': dict(detail=3, geometric_clarity=2),
    'white_vision': dict(detail=3, geometric_clarity=2),
    'wanda': dict(detail=3, geometric_clarity=2),
    'spider_man': dict(detail=2, geometric_clarity=3),
    'tony': dict(detail=2, geometric_clarity=2),
    'pepper': dict(detail=3, geometric_clarity=1),
    'monk': dict(detail=0, geometric_clarity=3),
    'doc_ock': dict(detail=2, geometric_clarity=3),
    'aunt_may': dict(detail=2, geometric_clarity=2),
}
FOCUSES = ('identity','emotion','action','object','mechanism','location')
MOTIONS = ('hold','gesture','contact','transformation','combat')


def decide_style(direction, profiles=None):
    """Choose each layer independently, prioritizing the story's important action."""
    if not isinstance(direction,dict):
        raise Held('lore_style','Supply one visual-direction object for each directed beat.')
    focus=direction.get('focus');motion=direction.get('motion','hold')
    if focus not in FOCUSES or motion not in MOTIONS:
        raise Held('lore_style','Use a supported focus and movement description.')
    people=direction.get('characters',[])
    if not isinstance(people,list) or len(people)>5 or any(not isinstance(p,str) for p in people) or len(set(people))!=len(people):
        raise Held('lore_style','Use up to five distinct character IDs.')
    props=direction.get('props',[])
    if not isinstance(props,list) or len(props)>5 or any(not isinstance(p,dict) for p in props):
        raise Held('lore_style','Use up to five explicit prop descriptions.')
    profiles={**PROFILES,**(profiles or {})}
    characters={}
    for who in people:
        profile=profiles.get(who)
        if not isinstance(profile,dict) or any(type(profile.get(k)) is not int or not 0<=profile[k]<=3 for k in ('detail','geometric_clarity')):
            raise Held('lore_style',f'Give {who} detail and geometric_clarity ratings from 0 to 3.')
        physical=motion in ('contact','transformation','combat')
        if physical and (profile['geometric_clarity']>=2 or focus in ('object','mechanism')):
            style='geometric';why='Show contact, changing state and consequence with controllable geometry.'
        elif physical and profile['geometric_clarity']<2:
            style='cutout';why='A difficult face or lookalike costume needs its likeness; use anchored limbs or reframe the action.'
        elif focus in ('identity','emotion') or profile['detail']>=3:
            style='cutout';why='Recognition, facial detail or a complex costume is carrying this shot.'
        else:
            style='geometric';why='A clear silhouette can carry this action without photographic detail.'
        characters[who]={'representation':style,'reason':why,'motion_requirement':'rigged' if style=='cutout' and physical else 'pose'}
    objects=[]
    for prop in props:
        name=prop.get('id')
        if not isinstance(name,str) or not name or len(name)>80:
            raise Held('lore_style','Name each important prop with a short ID.')
        for key in ('changes_state','readable_detail','appearance_matters'):
            if key in prop and type(prop[key]) is not bool:
                raise Held('lore_style','Prop change/detail flags must be booleans.')
        if prop.get('changes_state') or focus=='mechanism':
            style='geometric';why='Its state or mechanism must visibly change and remain consistent.'
        elif prop.get('readable_detail') or prop.get('appearance_matters'):
            style='cutout';why='The real appearance, surface, inscription or exact detail is the point of this insert.'
        else:
            style='geometric';why='Keep supporting props simple and subordinate to the important element.'
        objects.append({'id':name,'representation':style,'reason':why})
    environment=direction.get('setting',{})
    if not isinstance(environment,dict) or set(environment)-{'needs_layout','appearance_matters','atmosphere'} or any(type(v) is not bool for v in environment.values()):
        raise Held('lore_style','Use boolean layout, appearance or atmosphere flags for the setting.')
    if environment.get('needs_layout'):
        setting='geometric';setting_reason='The geography, structure or spatial relationship must stay clear and controllable.'
    elif focus=='location' or environment.get('appearance_matters') or environment.get('atmosphere'):
        setting='photographic';setting_reason='The appearance, atmosphere or scale of the place carries useful information.'
    else:
        setting='geometric';setting_reason='A quiet drawn setting keeps identity, movement or the explanation readable.'
    return {'focus':focus,'motion':motion,'characters':characters,'props':objects,
            'setting':{'representation':setting,'reason':setting_reason},
            'continuity':'Keep the same costume, colors and identifying features across representations. Change medium at a meaningful cut.'}


def _default_direction(scene):
    kind=scene['kind']
    if kind in ('mask_fitting','forge','mask_cooling','hot_mask'):
        return {'focus':'object','motion':'contact' if kind in ('mask_fitting','forge') else 'transformation',
                'characters':['doom'] if kind=='mask_fitting' else ['monk'] if kind=='forge' else [],
                'props':[{'id':'mask','changes_state':True}]}
    if kind.startswith('thor_') or kind in ('bill_lifts','bill_fleet','stormbreaker_forged'):
        people=[] if kind=='stormbreaker_forged' else ['bill'] if kind in ('thor_hammer_hook','bill_lifts','bill_fleet') else ['thor','bill']
        return {'focus':'identity' if kind in ('thor_hammer_hook','thor_two_hammers') else 'action',
                'motion':'hold' if kind in ('thor_hammer_hook','thor_two_hammers','bill_fleet') else 'contact',
                'characters':people,'props':[{'id':'hammer','changes_state':True}]}
    return None


def plan_styles(scenes, request):
    config=request.get('visual_selection')
    if config is None:
        return None
    if not isinstance(config,dict) or config.get('mode','auto') not in ('auto','authored'):
        raise Held('lore_style','Choose auto or authored visual selection.')
    if config.get('mode')=='authored':
        return {'version':1,'mode':'authored','scenes':{}}
    shots=config.get('shots',{});profiles=config.get('profiles',{})
    ids={s['unit_id'] for s in scenes}
    if not isinstance(shots,dict) or set(shots)-ids or not isinstance(profiles,dict):
        raise Held('lore_style','Visual directions must reference actual script beat IDs.')
    result={}
    for scene in scenes:
        direction=shots.get(scene['unit_id'],_default_direction(scene))
        if direction is None:
            result[scene['unit_id']]={'status':'authored','reason':'Keep this existing recipe; no semantic direction was supplied for a new choice.'}
        else:
            result[scene['unit_id']]={'status':'selected',**decide_style(direction,profiles)}
    return {'version':1,'mode':'auto','scenes':result,
            'scope':'The assistant interprets the script and supplies focus/action. Rules select representations; registered assets and renderer capabilities are checked separately.'}


def attach_styles(scenes, request):
    result=plan_styles(scenes,request)
    if result:
        for scene in scenes:
            choice=result['scenes'].get(scene['unit_id'])
            if choice and choice['status']=='selected':
                scene['visual_style']=deepcopy(choice)
    return result
