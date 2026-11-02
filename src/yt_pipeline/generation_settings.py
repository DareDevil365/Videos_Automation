"""Plan economical generation settings and operate explicit sidebar bindings.

Capabilities are calibrated from the provider UI, not invented by the model.
No setting falls back silently when unsupported.
"""
import math
import re

from .core import Held

SETTING_NAMES={'aspect_ratio','resolution','duration_seconds','thinking_level','temperature',
               'frame_rate','output_mode','grounding','image_search'}


def validate_settings(settings):
    if not isinstance(settings,dict) or settings.keys()-SETTING_NAMES:
        raise ValueError('Unknown generation setting; supply an object of supported sidebar values')
    result=dict(settings)
    for name,value in result.items():
        if name in ('duration_seconds','temperature','frame_rate'):
            if type(value) not in (int,float) or not math.isfinite(value) or value<0:
                raise ValueError('Numeric generation settings must be finite and nonnegative')
            if name!='temperature' and value==0:raise ValueError('Duration and frame rate must be positive')
        elif name in ('grounding','image_search'):
            if type(value) is not bool:raise ValueError('Tool settings must be true or false')
        elif not isinstance(value,str) or not 1<=len(value)<=80:
            raise ValueError('Sidebar labels must be nonempty bounded strings')
    return result


def plan_settings(kind,requirements,capabilities):
    """Smallest adequate *known supported* size/duration; explicit on failure."""
    if kind not in ('image','video'):raise ValueError('Unknown generation media kind')
    if not isinstance(requirements,dict) or not isinstance(capabilities,dict):raise ValueError('Requirements and capabilities must be objects')
    def positive(key,default):
        value=requirements.get(key,default)
        if type(value) not in (int,float) or not math.isfinite(value) or value<=0:raise ValueError('Shot dimensions/duration must be positive finite numbers')
        return value
    width=positive('slot_width',720);height=positive('slot_height',1280);zoom=positive('zoom',1)
    ratio=requirements.get('aspect_ratio','9:16')
    ratios=capabilities.get('aspect_ratios',[])
    if ratio not in ratios:raise Held('generation_capability','Requested aspect ratio is not in the calibrated supported choices')
    rw,rh=[int(v) for v in ratio.split(':')]
    if rw<=0 or rh<=0:raise ValueError('Invalid aspect ratio')
    # A cover crop needs a source large enough in BOTH dimensions after zoom.
    scale=max(width*zoom/rw,height*zoom/rh)
    required_width=rw*scale;required_height=rh*scale
    sizes=capabilities.get('resolutions',[])
    eligible=[v for v in sizes if isinstance(v,dict) and v.get('width',0)>=required_width and v.get('height',0)>=required_height]
    if not eligible:raise Held('generation_resolution','No calibrated resolution covers the requested panel/crop; revise the shot')
    size=min(eligible,key=lambda v:v['width']*v['height'])
    settings={'aspect_ratio':ratio,'resolution':size['label']}
    duration=None
    if kind=='video':
        duration=positive('usable_seconds',3)
        margin=requirements.get('trim_margin_seconds',0)
        if type(margin) not in (int,float) or not math.isfinite(margin) or margin<0:raise ValueError('Trim margin must be nonnegative')
        supported=[v for v in capabilities.get('durations_seconds',[]) if type(v) in (int,float) and math.isfinite(v) and v>=duration+margin]
        if not supported:raise Held('generation_duration','No supported duration covers this shot; split it or revise the requested duration')
        settings['duration_seconds']=min(supported)
    thinking=capabilities.get('thinking_levels',[])
    if thinking:
        complexity=requirements.get('complexity','simple')
        if complexity not in ('simple','complex'):raise ValueError('Shot complexity must be simple or complex')
        settings['thinking_level']=thinking[-1] if complexity=='complex' else thinking[0]
    for tool in ('grounding','image_search'):
        if tool in capabilities.get('optional_tools',[]):settings[tool]=False
    return {'settings':validate_settings(settings),'usable_seconds':duration,
            'reason':'Smallest adequate calibrated resolution and shortest supported duration; no automatic 4K or High preset.'}


def _one(page,selector):
    if not isinstance(selector,str) or not selector:raise Held('browser_setting_binding','A requested setting has no calibrated selector')
    items=page.locator(selector)
    visible=[items.nth(i) for i in range(items.count()) if items.nth(i).is_visible()]
    if len(visible)!=1:raise Held('browser_setting_control','A sidebar setting is absent or ambiguous; recalibrate before generation')
    return visible[0]


def _read(control,binding):
    read=binding.get('read','checked' if binding.get('type')=='checkbox' else ('value' if binding.get('type') in ('select','input','slider') else 'text'))
    if read=='value':return control.input_value().strip()
    if read=='checked':return control.is_checked()
    if read=='text':return control.inner_text().strip()
    if read=='attribute':return control.get_attribute(binding.get('attribute','aria-valuenow'))
    raise Held('browser_setting_binding','Unknown sidebar read-back mode')


def apply_settings(page,settings,bindings,timeout_ms=5000,verify_only=False):
    """Apply and read back native inputs, switches and custom dropdowns.

    Only explicit selectors/values are used. No DOM scripts or generated code.
    """
    settings=validate_settings(settings);observed={}
    for name,value in settings.items():
        binding=bindings.get(name)
        if not isinstance(binding,dict):raise Held('browser_setting_binding',f'No calibrated sidebar binding for {name}; no generation submitted')
        selector=binding.get('selector');control=_one(page,selector);kind=binding.get('type')
        key=str(value).lower() if isinstance(value,bool) else str(value)
        mapped=binding.get('values',{}).get(key,key)
        if verify_only:pass
        elif kind=='select':control.select_option(value=str(mapped),timeout=timeout_ms)
        elif kind=='input':control.fill(str(mapped),timeout=timeout_ms);control.press('Tab')
        elif kind=='slider':
            try:
                start=float(control.get_attribute('min') or binding.get('min',0))
                end=float(control.get_attribute('max') or binding.get('max',100))
                step=float(control.get_attribute('step') or binding.get('step',1))
                target=float(mapped);steps=(target-start)/step
                if step<=0 or not start<=target<=end or not math.isfinite(steps) or abs(steps-round(steps))>1e-6 or steps>1000:raise ValueError()
            except (ValueError,TypeError,ZeroDivisionError):raise Held('browser_setting_option',f'The requested {name} is outside the calibrated slider range/step')
            control.press('Home',timeout=timeout_ms)
            for _ in range(round(steps)):control.press('ArrowRight',timeout=timeout_ms)
        elif kind=='checkbox':control.set_checked(value,timeout=timeout_ms)
        elif kind=='dropdown':
            control.click(timeout=timeout_ms)
            # A scoped option selector plus exact visible label avoids matching another menu.
            options=page.locator(binding.get('option_selector','[role="option"]')).filter(has_text=re.compile('^'+re.escape(str(mapped))+'$'))
            choices=[options.nth(i) for i in range(options.count()) if options.nth(i).is_visible()]
            if len(choices)!=1:raise Held('browser_setting_option',f'The requested {name} option is unavailable or ambiguous')
            choices[0].click(timeout=timeout_ms)
        elif kind!='readonly':raise Held('browser_setting_binding','Unsupported sidebar control type')
        # Provider frameworks can update the label asynchronously after a selection.
        import time
        deadline=time.monotonic()+timeout_ms/1000
        expected=binding.get('observed_values',{}).get(key,value if isinstance(value,bool) else mapped)
        while True:
            actual=_read(_one(page,binding.get('verify_selector',selector)),binding)
            matches=actual==expected if isinstance(actual,bool) else str(actual)==str(expected)
            if name in ('duration_seconds','temperature','frame_rate'):
                try:matches=math.isclose(float(actual),float(expected),rel_tol=1e-6,abs_tol=1e-6)
                except (ValueError,TypeError):pass
            if matches:break
            if time.monotonic()>=deadline:raise Held('browser_setting_mismatch',f'Sidebar read-back differs for {name}; generation stopped')
            page.wait_for_timeout(100)
        observed[name]={'requested':value,'observed':actual}
    return observed
