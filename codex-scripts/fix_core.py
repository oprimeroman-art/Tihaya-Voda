from paths import *
p=STUDIO/'source/adventure-core.js'
s=p.read_text(encoding='utf-8')
s=s.replace("if(x.ending){this.checkpoint('before_final_confirmation');",'if(x.ending){')
s=s.replace('advance(){for(const q','advance(){if(this.state.ended)return;for(const q')
s=s.replace('this.modal=false;if(!this.state.done.includes(id))',"this.modal=false;if(fx.some(x=>x.ending))this.checkpoint('before_final_confirmation');if(!this.state.done.includes(id))")
s=s.replace("this.state.pending=this.state.pending.filter(p=>!this.state.fired.includes(p.id));", "this.state.pending=[...new Map([...this.state.pending,...old.pending].map(p=>[p.id,p])).values()].filter(p=>!this.state.fired.includes(p.id));")
s=s.replace('this.state.journal.push({id:e.id,text:e.presentation,lines:e.lines||[],time:this.state.clock});this.changed();return e;',"this.state.journal.push({id:e.id,text:e.presentation,lines:e.lines||[],time:this.state.clock});this.signal('event:'+e.id);this.changed();return e;")
p.write_text(s,encoding='utf-8')
