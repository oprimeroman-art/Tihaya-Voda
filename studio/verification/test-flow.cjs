const fs=require('fs'),assert=require('assert/strict'),path=require('path');
const root=path.resolve(__dirname,'../..');
const out=path.join(root,'reports');
const {Engine,test}=require(root+'/studio/source/adventure-core.js');
const data=JSON.parse(fs.readFileSync(root+'/studio/content/TIHAYA_VODA/adventure.json','utf8'));
let e=new Engine(data),count=0,seen=new Set(),checks=[];
function drain(){let ev;for(let i=0;i<150;i++){ev=e.flush(70);if(!ev)break;seen.add(ev.id);} }
function go(dest){if(e.state.room===dest)return;const queue=[[e.state.room,[]]],visited=new Set();let route;
 while(queue.length){const [r,steps]=queue.shift();if(r===dest){route=steps;break;}if(visited.has(r))continue;visited.add(r);for(const l of data.links.filter(l=>l.from===r&&test(l.when,e.state)))queue.push([l.to,[...steps,l.to]]);}
 assert(route,'No route '+e.state.room+'→'+dest+' chapter '+e.state.chapter);for(const r of route){assert(e.enter(r));drain();}}
function doA(id,value){const a=data.actions.find(a=>a.id===id);assert(a,id);go(a.room);assert(e.begin(id),'Unavailable '+id+' ch'+e.state.chapter+' '+JSON.stringify(e.state.flags));const r=e.answer(id,value??a.answer??a.options?.[0]?.value);assert(r.ok,id+': '+r.message);drain();count++;return r;}
function chapter(n){assert.equal(e.state.chapter,n);checks.push('Q'+String(n-1).padStart(2,'0')+' complete');}
e.start();drain();
doA('take_BADGE04');doA('take_STORAGE_KEY');doA('read_D01');doA('TEA_SEQUENCE');doA('sign_shift');doA('take_FUSE_3');doA('install_fuse3');chapter(2);
assert([...seen].every(id=>Number(id.slice(1))<8));checks.push('No horror before completion of Q02');
doA('read_D28');doA('POWER_BASIC');doA('CORES_MARKING');doA('RADIO_TUNE');doA('send_report');chapter(3);
doA('read_D19');doA('PLUMB_SEQ');doA('watch_V01');go('C');doA('mirror03');go('A');go('D');doA('cabinet_message');doA('archive_return');chapter(4);
doA('read_D20');doA('count_cans');doA('read_D16');doA('COOKING');doA('mirror04');doA('mirror04_away');doA('mirror04_again');doA('mirror04_third');doA('plate_choice','LEFT');
const plate=e.export();e.load(plate);assert.equal(e.state.flags.SECOND_PLATE,'LEFT');checks.push('Plate choice survives save/load');go('C');go('B');go('C');go('A');
const mainPlate=e.export();e.load(plate);e.state.flags.SECOND_PLATE='REMOVED';go('C');go('B');e.load(mainPlate);
doA('dinner_exit');chapter(5);doA('take_P17_SAMPLE');doA('SPECTRUM_MATCH');doA('MICROSCOPE');doA('read_D06');doA('hidden_enter');doA('read_D03');doA('hidden_exit');chapter(6);
go('A');go('I');go('B');doA('WAVE_PHASE');doA('watch_A02');doA('watch_A01');doA('read_D02');doA('read_D27');doA('mirror06');doA('mirror06_again');doA('read_D07');doA('flip_acts');chapter(7);
checks.push('Both radio messages work in reverse order');
doA('read_D22');for(const id of ['FLASHLIGHT','ANTENNA_KEY','BEACON'])doA('take_'+id);for(let i=1;i<=3;i++)doA('ice_'+i);doA('ANTENNA');go('J');
assert.equal(e.state.checkpoint.name,'before_airlock_pressure');e.begin('outer_door');e.answer('outer_door');assert(e.state.flags.ANTENNA);assert.equal(e.state.room,'J');assert.equal(e.state.flags.DEATHS,1);checks.push('Airlock death retains antenna and restores J');drain();
doA('glass07');doA('AIRLOCK_EQUALIZE');doA('inner_door');chapter(8);go('A');go('B');
for(const id of ['VHS_FRAGMENT_A','VHS_FRAGMENT_B'])doA('take_'+id);doA('read_D23');doA('VHS_ASSEMBLE');doA('watch_V02');doA('read_D13');doA('read_D29');doA('read_D05');doA('take_VHS_V03');doA('watch_V03');doA('petr_letter');go('B');go('A');doA('wet_towel');chapter(9);
for(const id of ['D04','D09','D21'])doA('read_'+id);doA('take_PUNCHCARD_RU');doA('take_PUNCHCARD_DE');doA('PUNCHCARD_OVERLAY');doA('scan_uv');doA('enter_1978');doA('read_D08');doA('read_D12');doA('calibration_plate');doA('watch_V06');doA('watch_V09');doA('watch_A03');doA('exit_1978');chapter(10);
doA('read_D17');doA('read_D18');doA('watch_A04');doA('CARDIOMATCH');doA('medic10');doA('TIMELINE_SYNC');doA('watch_V04');doA('late10');doA('read_D14');doA('read_D11');doA('read_D15');doA('watch_V08');
for(const id of ['handwriting_floor','backward_clock','reversed_exit_arrow'])doA(id);doA('leave_N');go('B');doA('false_act','NO');chapter(11);
go('A');go('F');go('B');doA('blanket11');doA('watch_V01B');
checks.push('Corridor clues accepted in noncanonical order');
const branch=e.export();
for(const mode of ['A','B','C','D']){
 e=new Engine(data);e.load(branch);doA('NODE_POWER');doA('NODE_MEMORY',mode==='D'?'PETR':'TRUTH');doA('NODE_OBSERVER',mode==='B'?2:1);
 const saved=e.export();e.load(saved);assert.deepEqual(e.export(),saved);checks.push(mode+': parallel node save exact');
 go('L');e.begin('SHUTTERS');for(let i=0;i<4;i++)e.answer('SHUTTERS',['wrong']);assert(e.state.flags.NODE_POWER_DONE&&e.state.flags.NODE_MEMORY_DONE&&e.state.flags.NODE_OBSERVER_DONE);assert.equal(e.state.room,'L');assert(!e.state.flags.SHUTTERS_SAFE);checks.push(mode+': shutters local death preserves all nodes');drain();
 doA('SHUTTERS');doA('name_reply');chapter(12);doA('second_window');doA('third_window');doA('POWER_OFF');doA('take_SHUTTER_PIN');doA('PIN_INSERT');doA('ANALOG_READINGS_OK');doA('OBSERVER_SELECT');
 if(mode==='C'){doA('NODE_MEMORY','PETR');let c=data.actions.find(a=>a.id==='FINAL_PANEL').options.find(o=>o.value==='C');assert(!test(c.when,e.state));doA('NODE_MEMORY','ARCHIVE');assert(test(c.when,e.state));checks.push('Tape can change after panel preparation, before signature');}
 doA('FINAL_PANEL',mode);assert.equal(e.state.ended,mode);assert.equal(e.state.checkpoint.name,'before_final_confirmation');assert.equal(e.state.checkpoint.state.ended,false);assert(!e.state.checkpoint.state.done.includes('FINAL_PANEL'));e.signal('ending_done');drain();checks.push('ENDING_'+mode+' reached through actions');
 fs.writeFileSync(path.join(out,'CHECKPOINT_'+mode+'.json'),JSON.stringify(e.state.checkpoint.state,null,2));
}
// Baseline route has no requirement on optional media for A.
const minimal=new Engine(data);minimal.load(branch);for(const k of ['WATCHED_V03','PETR_LETTER_DONE','FOUND_D04','FOUND_ACT_BOTH'])delete minimal.state.flags[k];assert(test(data.actions.find(a=>a.id==='FINAL_PANEL').options[0].when,minimal.state));checks.push('Ending A has no optional-evidence condition');
e=new Engine(data);e.state.chapter=3;e.state.flags.Q02_DONE=true;e.state.room='H';e.signal('v01_end');e.modal=true;assert.equal(e.flush(100),null);assert(!e.state.fired.includes('E010'));e.modal=false;assert.equal(e.flush(0).id,'E010');e.signal('v01_end');assert.equal(e.flush(0),null);checks.push('Event defers during modal and fires once');
assert.equal(data.events.length,112);assert.equal(new Set(data.events.map(x=>x.id)).size,112);
assert.equal(data.documents.length,30);assert.equal(data.dialogues.length,53);
// A fresh, complete route that never acquires the optional personal tape/letter.
e=new Engine(data);e.start();drain();
for(const id of ['take_BADGE04','take_STORAGE_KEY','TEA_SEQUENCE','sign_shift','take_FUSE_3','install_fuse3','POWER_BASIC','CORES_MARKING','RADIO_TUNE','send_report','read_D19','PLUMB_SEQ','watch_V01'])doA(id);
go('C');doA('cabinet_message');
for(const id of ['archive_return','read_D20','count_cans','COOKING','plate_choice','dinner_exit','take_P17_SAMPLE','SPECTRUM_MATCH','MICROSCOPE','hidden_enter','read_D03','hidden_exit','WAVE_PHASE','watch_A01','watch_A02','read_D07','flip_acts','take_FLASHLIGHT','take_ANTENNA_KEY','take_BEACON','ice_1','ice_2','ice_3','ANTENNA','AIRLOCK_EQUALIZE','inner_door','take_VHS_FRAGMENT_A','take_VHS_FRAGMENT_B','VHS_ASSEMBLE','watch_V02','wet_towel','read_D09','take_PUNCHCARD_RU','take_PUNCHCARD_DE','PUNCHCARD_OVERLAY','scan_uv','enter_1978','read_D08','read_D12','calibration_plate','exit_1978','read_D17','read_D18','CARDIOMATCH','TIMELINE_SYNC','watch_V04','backward_clock','reversed_exit_arrow','handwriting_floor','leave_N','false_act','NODE_POWER','NODE_MEMORY','NODE_OBSERVER','SHUTTERS','name_reply','second_window','POWER_OFF','take_SHUTTER_PIN','PIN_INSERT','ANALOG_READINGS_OK','OBSERVER_SELECT'])doA(id);
assert(!e.state.flags.WATCHED_V03&&!e.state.flags.PETR_LETTER_DONE&&!e.state.flags.FOUND_D04);doA('FINAL_PANEL','A');assert.equal(e.state.ended,'A');checks.push('Fresh mandatory-only route reaches A with no V03, Petr letter or D04');
for(const mode of ['B','C','D']){
 const snapshot=JSON.parse(fs.readFileSync(path.join(out,'CHECKPOINT_'+mode+'.json'),'utf8'));
 const option=data.actions.find(a=>a.id==='FINAL_PANEL').options.find(o=>o.value===mode);assert(test(option.when,snapshot));
 for(const key of option.when.all||[]){const bad=structuredClone(snapshot);bad.flags[key]=false;assert(!test(option.when,bad),mode+' missing '+key);}
 for(const [key,value] of Object.entries(option.when.eq||{})){const bad=structuredClone(snapshot);bad.flags[key]=typeof value==='boolean'?!value:typeof value==='number'?99:'NONE';assert(!test(option.when,bad),mode+' mismatched '+key);}
 for(const key of Object.keys(option.when.in||{})){const bad=structuredClone(snapshot);bad.flags[key]='NONE';assert(!test(option.when,bad),mode+' invalid '+key);}
 checks.push('Each individual missing condition locks '+mode+' with authored explanation');
}
const result={passed:true,actions:count,checks,eventsObserved:[...seen].sort(),eventsNotObserved:data.events.filter(x=>!seen.has(x.id)).map(x=>x.id),note:'Deterministic model route tests. Does not measure human play time or validate missing artistic media.'};
fs.writeFileSync(path.join(out,'MODEL_TEST_REPORT.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({passed:true,actions:count,checks:checks.length,eventsObserved:seen.size,eventsNotObserved:result.eventsNotObserved}));
