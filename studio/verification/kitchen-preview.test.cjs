/* Offline B_NORMAL opt-in preview regression. No browser dependencies. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'game/index.html'),'utf8');
const project=JSON.parse(fs.readFileSync(path.join(root,'game-project/project.json'),'utf8'));
const segment=html.match(/<script>\s*\/\* KITCHEN_QA_PREVIEW_BEGIN \*\/([\s\S]*?)\/\* KITCHEN_QA_PREVIEW_END \*\/\s*<\/script>/);
assert(segment,'The existing player HTML must contain exactly one opt-in art layer');
assert.equal((html.match(/KITCHEN_QA_PREVIEW_BEGIN/g)||[]).length,1);
const a=project.rooms.find(x=>x.id==='B');
const actions=a.objects.map(o=>({id:o.id, tourKey:o.tourKey,corners:JSON.parse(JSON.stringify(o.corners))}));
function evaluate(search){
 const game={name:'ПОЛЯРНАЯ СМЕНА',panoramas:{B:{data:'base64original',mime:'image/png'}},rooms:[{id:'B',objects:JSON.parse(JSON.stringify(actions))}]};
 const callbacks=[];
 const window={BUILT_GAME:game,location:{search}};
 const document={addEventListener(_name,fn){callbacks.push(fn);},body:{appendChild(){}},createElement(){return {style:{}}}};
 vm.runInNewContext(segment[1],{window,document,URLSearchParams,console});
 return {game,callbacks};
}
const normal=evaluate('');
assert.equal(normal.game.name,'ПОЛЯРНАЯ СМЕНА');
assert.equal(normal.game.panoramas.B.mime,'image/png');
assert.equal(normal.game.panoramas.B.data,'base64original');
assert.deepEqual(normal.game.rooms[0].objects,actions);
assert.equal(normal.callbacks.length,0);
const qa=evaluate('?qa-kitchen=1');
assert(qa.game.name.includes('QA'),'QA game title must isolate its SAVE_KEY fingerprint');
assert.equal(qa.game.panoramas.B.mime,'image/webp');
assert(qa.game.panoramas.B.data.length>300000,'must embed an offline self-contained panorama');
assert.equal(qa.callbacks.length,1);
const objects=qa.game.rooms[0].objects;
assert.equal(objects.length,11);
assert(objects.every(o=>o.corners.length===4 && o.corners.every(p=>p.u>=0&&p.u<=1&&p.v>=0&&p.v<=1)));
const plate=objects.find(o=>o.tourKey==='ga:plate_choice');
assert(plate.corners[0].u>.9&&plate.corners[1].u<.1,'plate hotspot wraps 0/1 sphere seam');
const suhov=objects.find(o=>o.tourKey==='ga:watch_A05');
assert(suhov.corners[0].u>.8&&suhov.corners[1].u<.9,'Suhov audio must target intercom near the door');
assert(objects.some((o,i)=>JSON.stringify(o.corners)!==JSON.stringify(actions[i].corners)));
function unwrapped(c){const b=c[0].u;return c.map(p=>({u:b+((((p.u-b)+.5)%1+1)%1-.5),v:p.v}));}
function objectHit(p,o){const q=unwrapped(o.corners),b=q[0].u,u=b+((((p.u-b)+.5)%1+1)%1-.5);let inside=false;for(let i=0,j=3;i<4;j=i++){const a=q[i],c=q[j];if((a.v>p.v)!==(c.v>p.v)&&u<(c.u-a.u)*(p.v-a.v)/(c.v-a.v)+a.u)inside=!inside;}return inside;}
assert(objectHit({u:.996,v:.68},plate),'seam-left longitude must be hit');
assert(objectHit({u:.025,v:.68},plate),'seam-right longitude must also hit');
assert(!objectHit({u:.50,v:.68},plate),'seam hotspot must not cover half of the room');
assert(objectHit({u:.84,v:.51},suhov));
const origProject=project.rooms.find(r=>r.id==='B');
assert.equal(origProject.file,'rooms/B/original.png','real production project must not be replaced');
console.log('PASS: opt-in kitchen art, isolated QA saves, normal game unchanged, all 11 native hotspots, seamless plate objectHit');
