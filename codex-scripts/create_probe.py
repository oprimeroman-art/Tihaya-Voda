from pathlib import Path
s=Path('work/browser-test.cjs').read_text(encoding='utf-8')
s=s[:s.index(" await navigate(path.join(out,'GAME/index.html'))")]+r'''
 for(const url of ['data:text/html,<h1>probe</h1>',require('url').pathToFileURL(studio+'/index.html').href,require('url').pathToFileURL(path.join(out,'GAME/index.html')).href]){
 console.log('URL',url);console.log('NAV',JSON.stringify(await cmd('Page.navigate',{url})));await sleep(1500);console.log('DOM',JSON.stringify(await ev('({href:location.href,ready:document.readyState,text:document.body?.innerText.slice(0,300)})')));}
 console.log('ERRORS',errors);
}catch(e){console.error(e);}finally{try{await cmd('Browser.close')}catch{}sock?.close();chrome.kill();}})();
'''
Path('work/probe.cjs').write_text(s,encoding='utf-8')
