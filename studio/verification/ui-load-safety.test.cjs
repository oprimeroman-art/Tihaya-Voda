const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const {Engine}=require('../source/adventure-core.js'),root=path.resolve(__dirname,'../..');
const d=JSON.parse(fs.readFileSync(path.join(root,'studio/content/TIHAYA_VODA/adventure.json')));
const window={GagarinAdventure:{Engine}};vm.runInNewContext(fs.readFileSync(path.join(root,'studio/source/adventure-ui.js'),'utf8'),{window,setTimeout,clearTimeout});
const ui=Object.create(window.GagarinAdventure.UI.prototype);ui.engine=new Engine(d);ui.engine.start();ui.endingShown=true;ui.pendingLines=['pending'];ui.death='retained';ui.root={hidden:true};let closed=false,synced=false;ui.close=()=>{closed=true;};ui.sync=()=>{synced=true;};
const before=ui.engine.export();assert.throws(()=>ui.load({...before,project:'foreign-project'}));assert.equal(closed,false);assert.deepEqual(ui.engine.export(),before);assert.equal(ui.endingShown,true);assert.deepEqual(ui.pendingLines,['pending']);assert.equal(ui.death,'retained');
ui.load(before);assert(closed&&synced);assert.equal(ui.root.hidden,false);assert.equal(ui.endingShown,false);assert.equal(ui.pendingLines.length,0);assert.equal(ui.death,null);
console.log('PASS: invalid UI load preserves the current dialog and session; valid load clears transient state and synchronizes');
