#!/usr/bin/env node
'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
const ROOT=path.resolve(__dirname,'../..'),out=process.env.QA_OUTPUT;
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1280,height:900}}),errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.join(ROOT,'studio/index.html'));
 await p.locator('#projectFile').setInputFiles(process.env.QA_PROJECT_ZIP);
 await p.waitForFunction(()=>APP.rooms.length===16&&APP.story?.adventure?.illustratedProps?.item?.BADGE04,{},{timeout:60000});
 const expected=JSON.parse(fs.readFileSync(path.join(ROOT,'game-project/project.json'))).story.adventure;
 assert.deepEqual(await p.evaluate(()=>APP.story.adventure),expected,'editor import retains all canonical story data and illustrations');
 let download=p.waitForEvent('download',{timeout:90000});await p.locator('#saveAsProject').click();await (await download).saveAs(path.join(out,'EDITOR_PROJECT.zip'));
 download=p.waitForEvent('download',{timeout:120000});await p.locator('#compileGame').click();await (await download).saveAs(path.join(out,'EDITOR_GAME.zip'));
 assert.deepEqual(errors,[]);console.log('PASS: editor import, story/art exact match, editable project export, compiled game export, no browser errors');await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
