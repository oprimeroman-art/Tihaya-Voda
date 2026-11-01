/* Panorama detail tiles: high-resolution UV compositing without touching source art. */
'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const runtime=fs.readFileSync(path.join(root,'studio/source/game-runtime.html'),'utf8');
const start=runtime.indexOf('/* PANORAMA_DETAIL_TILES_BEGIN');
const end=runtime.indexOf('/* PANORAMA_DETAIL_TILES_END */',start);
assert(start>0&&end>start,'tile implementation must remain in canonical runtime');
const source=runtime.slice(start,end+'/* PANORAMA_DETAIL_TILES_END */'.length);
const config=JSON.parse(fs.readFileSync(path.join(root,'production/panorama-detail-tiles.json'),'utf8'));
const flags={slippers:false,A_SHOES_SHIFTED:false};
const game={panoramaDetailTiles:config.tiles.map(t=>({...t,src:'panorama-detail/'+path.basename(t.path)}))};
const ctx={game,adventurePlayer:{engine:{state:{flags,done:[],variants:{A:'A_NORMAL'}}}},Map,Number,console,gl:null};
vm.createContext(ctx);
vm.runInContext(source+';this.test={detailAllowed,detailTilesFor,detailCpuPixel};',ctx);
const {detailAllowed,detailTilesFor,detailCpuPixel}=ctx.test;
const tile=game.panoramaDetailTiles[0];
assert.equal(detailAllowed(tile,ctx.adventurePlayer.engine.state,'A_NORMAL'),false);
flags.slippers=true;
assert.equal(detailAllowed(tile,ctx.adventurePlayer.engine.state,'A_NORMAL'),true);
assert.equal(detailTilesFor('A',.34).length,1);
flags.A_SHOES_SHIFTED=true;
assert.equal(detailTilesFor('A',.34).length,0,'later shoe anomaly restores the old image');
flags.A_SHOES_SHIFTED=false;
const rgba=new Uint8ClampedArray([10,20,30,255]),pixel={width:1,height:1,data:new Uint8ClampedArray([110,120,130,128])};
detailCpuPixel([{tile,entry:{pixel}}],.33,.75,rgba,0);
assert(Math.abs(rgba[0]-60)<2&&Math.abs(rgba[1]-70)<2);
const outside=new Uint8ClampedArray([10,20,30,255]);
detailCpuPixel([{tile,entry:{pixel}}],.1,.1,outside,0);
assert.equal(outside[0],10,'unaffected background remains byte-identical');
assert(runtime.includes('const PANORAMA_TILE_LIMIT=24'),'viewport tile budget is larger than four');
assert(runtime.includes('gpu.detailProgram=build(detailFs)'),'layers have an independent draw program');
assert(runtime.includes('gl.enable(gl.BLEND)'),'transparent tiles composite over the original panorama');
assert(runtime.includes('gl.uniform4f(layer.tileRect,...tile.rect)'),'GPU compositor sets each UV rect independently');
// 8K-style tile grids cannot silently truncate after four texture samplers.
const grid=[];
for(let row=0;row<4;row++)for(let col=0;col<8;col++){
 const id='grid_'+row+'_'+col;
 grid.push({id,room:'Z',src:id+'.png',priority:-10,
  rect:[col/8,row/4,(col+1)/8,(row+1)/4]});
}
game.panoramaDetailTiles=grid;
ctx.adventurePlayer.engine.state.variants.Z='Z_NORMAL';
const coverage=detailTilesFor('Z',.49,.49,.20,.34);
assert(coverage.length>4,'multiple 8K tiles remain visible concurrently');
assert(coverage.length<=24,'visible tiles are bounded');
const opposite=detailTilesFor('Z',.05,.49,.05,.12);
assert(opposite.length<coverage.length,'offscreen grid columns are not loaded');
const ui=fs.readFileSync(path.join(root,'studio/source/adventure-ui.js'),'utf8');
assert(ui.includes('if(a.instant&&'),'world micro-interactions must avoid giant modal');
console.log('PASS UV tile eligibility, story reversion, scalable WebGL overlay rendering, transparent pixel compositing and inline footwear action');
