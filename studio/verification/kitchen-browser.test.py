#!/usr/bin/env python3
"""Real Chromium QA of in-game B_NORMAL opt-in preview, not a synthetic scene mock.

Usage:
    python -m pip install playwright
    python -m playwright install --with-deps chromium
    python studio/verification/kitchen-browser.test.py

Keeps the original playable game, scenario project, and normal saves unchanged.
"""
import hashlib
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/'game/index.html'
assert FILE.is_file(), 'Must run inside the existing Tihaya-Voda repository'

def data(page,expression,arg=None):
    return page.evaluate(expression,arg)

def dom_click(page,locator):
    assert locator.count(), 'Expected interactive button missing'
    locator.first.evaluate('(button) => button.click()')

def assert_no_dialog(page):
    """Dismiss queued narration, never dismiss an unrecognized gameplay modal."""
    for _ in range(7):
        page.wait_for_timeout(180)
        dialog=page.get_by_role('dialog')
        if not dialog.count():return
        continue_button=dialog.first.get_by_role('button',name='Продолжить',exact=True)
        if not continue_button.count():
            raise AssertionError('Unexpected blocking modal: '+dialog.first.inner_text()[:160])
        dom_click(page,continue_button)
    assert not page.get_by_role('dialog').count(), 'Narration did not clear'

def aim(page,action):
    outcome=data(page,"""(action)=>{
        const object=current().objects.find(x=>x.tourKey==='ga:'+action);
        if(!object)throw Error('No action object '+action);
        const points=unwrapped(object.corners);
        const u=norm(points.reduce((acc,p)=>acc+p.u,0)/4);
        const v=points.reduce((acc,p)=>acc+p.v,0)/4;
        yaw=(u-.5)*2*Math.PI;pitch=(.5-v)*Math.PI;refresh();
        return {u,v,visible:object.visible,
            hit:objectAt(innerWidth/2,innerHeight/2)?.tourKey};
    }""",action)
    assert outcome['visible'], f'Gameplay action {action} is not eligible'
    assert outcome['hit']=='ga:'+action, f'Hotspot {action} is obscured by {outcome["hit"]}'
    return outcome

def test():
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=[
            '--no-sandbox','--use-gl=angle','--use-angle=swiftshader',
            '--enable-webgl','--enable-unsafe-swiftshader'
        ])
        context=browser.new_context(viewport={'width':1280,'height':720})
        uri=FILE.as_uri()
        original=context.new_page()
        original.goto(uri,wait_until='load',timeout=25000)
        normal=data(original,"""() => ({
            name:game.name,mime:game.panoramas.B.mime,
            qaBanner:!!document.querySelector('#kitchen-qa-banner'),
            fp:gameFingerprint
        })""")
        assert normal['mime']=='image/png' and not normal['qaBanner'],normal
        original.close()

        page=context.new_page()
        page.on('pageerror',lambda exc: errors.append(str(exc)))
        page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
        page.goto(uri+'?qa-kitchen=1',wait_until='load',timeout=25000)
        qa=data(page,"""() => ({
            name:game.name,mime:game.panoramas.B.mime,
            qaBanner:!!document.querySelector('#kitchen-qa-banner'),
            fp:gameFingerprint
        })""")
        assert qa['mime']=='image/webp' and qa['qaBanner'],qa
        assert qa['fp']!=normal['fp'], 'QA SAVE_KEY and production SAVE_KEY must be independent'
        assert qa['name'].endswith('Kitchen QA')
        dom_click(page,page.get_by_role('button',name='Новая игра',exact=True))
        page.get_by_role('dialog').get_by_role('button',name='Продолжить').wait_for(timeout=15000)
        assert_no_dialog(page)
        dom_click(page,page.locator('.ga-actions').get_by_role('button',name='Взять бейдж ОПЕРАТОР-04'))
        page.get_by_role('dialog').get_by_role('button',name='Выполнить').wait_for(timeout=5000)
        dom_click(page,page.get_by_role('dialog').get_by_role('button',name='Выполнить'))
        page.wait_for_function("adventurePlayer.engine.state.done.includes('take_BADGE04')",timeout=5000)
        assert_no_dialog(page)
        for room,name in [('C','→ Коридор'),('B','→ Кухня')]:
            nav=page.locator('.ga-nav').get_by_role('button',name=name,exact=True)
            assert nav.is_enabled(), 'Story route blocked '+name
            dom_click(page,nav)
            page.wait_for_function("(target)=>roomId===target && adventurePlayer.engine.state.room===target",arg=room,timeout=15000)
            assert_no_dialog(page)
        assert data(page,"() => game.panoramas.B.mime")== 'image/webp'
        assert data(page,"() => cache.get('B')?.bitmap?.width")==2048
        assert data(page,"() => !!gl"), 'Actual WebGL context unavailable'
        visible=data(page,"() => current().objects.filter(o=>o.visible).map(o=>o.tourKey)")
        assert {'ga:TEA_SEQUENCE','ga:wash_cup','ga:read_D01'}.issubset(set(visible))

        # Four real graphical perspectives, not just synthetic longitude UV tests.
        screenshots=[]
        for yaw in (0,math.pi/2,math.pi,-math.pi/2):
            data(page,"(y)=>{yaw=y;pitch=0;refresh();}",yaw)
            page.wait_for_timeout(170)
            shot=page.screenshot(animations='disabled',timeout=15000)
            screenshots.append(hashlib.sha256(shot).hexdigest())
            assert len(shot)>20000, 'WebGL screenshot suspiciously empty'
        assert len(set(screenshots))==4, 'Camera rotation did not change the gameplay scene'

        # Both sides of wrapped plate must resolve through the *native* objectHit().
        seam=data(page,"""()=>{
            const p=current().objects.find(o=>o.tourKey==='ga:plate_choice');
            return [objectHit({u:.996,v:.68},p),
                    objectHit({u:.025,v:.68},p),
                    objectHit({u:.50,v:.68},p)]
        }""")
        assert seam==[True,True,False], '360 seam interaction geometry broken'
        aim(page,'TEA_SEQUENCE')
        page.mouse.click(640,360)
        page.get_by_role('dialog').get_by_role('button',name='вода',exact=True).wait_for(timeout=5000)
        for text in ('вода','нагрев','заварка','разлить'):
            dom_click(page,page.get_by_role('dialog').get_by_role('button',name=text,exact=True))
            page.wait_for_timeout(90)
        page.wait_for_function("adventurePlayer.engine.state.flags.TEA_DONE===true",timeout=5000)
        assert data(page,"()=>adventurePlayer.engine.state.done.includes('TEA_SEQUENCE')")
        assert_no_dialog(page)

        aim(page,'wash_cup')
        page.mouse.click(640,360)
        page.get_by_role('dialog').get_by_role('button',name='Выполнить').wait_for(timeout=5000)
        dom_click(page,page.get_by_role('dialog').get_by_role('button',name='Выполнить'))
        page.wait_for_function("adventurePlayer.engine.state.done.includes('wash_cup')",timeout=5000)
        assert_no_dialog(page)

        aim(page,'read_D01')
        page.mouse.click(640,360)
        page.get_by_role('dialog').wait_for(timeout=5000)
        assert 'ЗАПИСКА У ПЛИТЫ' in page.get_by_role('dialog').first.inner_text()
        assert not errors, f'Browser raised errors: {errors[:4]}'
        print('PASS: Chromium WebGL + real A → C → B route + four camera views')
        print('PASS: native TEA_SEQUENCE mouse input, tea puzzle completed, wash_cup completed, D01 opened')
        print('PASS: 360 plate seam hit from both sides, normal mode unchanged, QA saves isolated')
        browser.close()

if __name__=='__main__':test()
