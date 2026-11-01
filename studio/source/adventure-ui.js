/* UI shared by the editor preview and the compiled offline runtime. */
(function(){
'use strict';
const api=window.GagarinAdventure,el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const isImageSource=src=>typeof src==='string'&&(/^data:image\/(svg\+xml|webp|png|jpeg);base64,/.test(src)||/^web-assets\/[a-f0-9]{64}\.(webp|png|svg|jpe?g)$/.test(src));
const CSS=`
.ga-root{position:fixed;inset:0;z-index:125;pointer-events:none;font:15px/1.55 'Segoe UI',sans-serif;color:#e6edf1}
.ga-inventory{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px}.ga-item img{width:100%;height:125px;object-fit:contain;display:block}.ga-item{display:flex;flex-direction:column;align-items:center;text-align:center!important;gap:8px}.ga-panel{pointer-events:auto;background:#111d24f5;border:1px solid #607581;border-radius:12px;padding:16px;box-shadow:0 12px 50px #0004}
.ga-actions{position:absolute;left:16px;bottom:72px;width:252px;max-height:min(38vh,360px);overflow:auto;scrollbar-width:thin}
.ga-nav{position:absolute;right:16px;bottom:72px;width:192px;max-height:min(38vh,360px);overflow:auto;scrollbar-width:thin}
.ga-root h2{font-size:18px;margin:0 0 10px}.ga-root h3{font-size:13px;letter-spacing:.07em;color:#a5c1cc;margin:14px 0 7px}
.ga-root button,.ga-root select,.ga-root input{font:inherit;color:inherit;border:1px solid #6a818e;border-radius:7px;background:#23343e;padding:10px;min-height:43px}
.ga-root button{cursor:pointer;text-align:left}.ga-root button:hover:not(:disabled){background:#355263}.ga-root button:focus-visible{outline:3px solid #efd689;outline-offset:2px}.ga-root button:disabled{opacity:.6;cursor:default}
.ga-actions button,.ga-nav button{width:100%;margin:4px 0}.ga-muted{font-size:12px;color:#b6c6ce}.ga-slot{font-size:12px;color:#f0dca4;border-left:3px solid #bda46c;padding:6px 10px;background:#242b2d;margin:10px 0}
.ga-modal{pointer-events:auto;position:absolute;inset:0;background:#071017b8;display:flex;align-items:center;justify-content:center;padding:24px;backdrop-filter:blur(5px)}
.ga-dialog{background:#14242d;border:1px solid #7a909c;border-radius:14px;padding:26px;width:min(880px,96vw);max-height:90vh;overflow:auto;box-shadow:0 24px 90px #0009}
.ga-dialog pre{white-space:pre-wrap;overflow-wrap:anywhere;font:17px/1.7 Georgia,serif;background:#e7e3d7;color:#26353a;padding:22px;border-radius:6px;margin:12px 0}
.ga-document-art{display:block;width:100%;max-height:48vh;object-fit:contain;background:#0d1519;border:1px solid #607581;border-radius:7px;margin:12px 0 16px}.ga-document-art-caption{font-size:11px;letter-spacing:.08em;color:#a9bdc5;text-transform:uppercase;margin:4px 0}
.ga-dialog label{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:10px 0}.ga-dialog input{width:160px}.ga-dialog select{max-width:60%}.ga-row{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0}.ga-row button{flex:1;min-width:110px}.ga-error{color:#ffcc9f;white-space:pre-wrap}.ga-scene{font-size:20px;line-height:1.6;padding:18px 0}.ga-caption{border-top:1px solid #67808c;padding:16px 0;white-space:pre-wrap}.ga-progress{width:100%;accent-color:#b9d1dd}.ga-variant[hidden]{display:none!important}.ga-variant{position:absolute;left:50%;bottom:20px;transform:translateX(-50%);max-width:45vw;text-align:center;background:#13232be8;padding:8px 15px;border:1px solid #607581;border-radius:7px;font-size:12px}
.ga-root .ga-panel{background:linear-gradient(145deg,#111c21ed,#0a1217eb);border:1px solid #b4c5c52e;border-radius:10px;padding:12px;box-shadow:0 8px 28px #0004}
.ga-panel h2{font-size:14px;font-weight:500;margin:0 0 8px;color:#ded8c8}.ga-panel h3{font-size:10px;letter-spacing:.14em;margin:8px 0;color:#8fa5ad}
.ga-root .ga-panel button{font-size:12px;line-height:1.35;min-height:36px;padding:8px 10px;margin:2px 0;border-color:#b4c5c526;background:#d4e1de09;border-radius:5px}
.ga-root .ga-panel button:hover:not(:disabled){background:#c6dfdc18;border-color:#a9c9c380}.ga-panel .ga-muted,.ga-panel details{font-size:11px}.ga-panel details{padding:5px 0;color:#a5b6bb}.ga-panel summary{cursor:pointer}
.ga-variant{display:none}.ga-hotspots{position:absolute;inset:0;pointer-events:none}.ga-hotspots[hidden]{display:none}
.ga-root .ga-hotspot{position:absolute;pointer-events:auto;width:44px;height:44px;min-height:44px;padding:0;transform:translate(-50%,-50%);border:0;background:transparent;border-radius:50%;display:grid;place-items:center}
.ga-root .ga-hotspot[hidden]{display:none}
.ga-hotspot:before{content:'';width:12px;height:12px;border:1px solid #f0e3bf;border-radius:50%;background:#17252dd9;box-shadow:0 0 0 4px #0b14146b,0 2px 8px #000b;transition:background .15s,box-shadow .15s}
.ga-root .ga-hotspot:hover,.ga-root .ga-hotspot:focus-visible{background:transparent}.ga-hotspot:hover:before,.ga-hotspot:focus-visible:before{background:#f0e3bf;box-shadow:0 0 0 5px #dfd0aa24,0 2px 8px #000b}
.ga-hotspot span{display:none;position:absolute;top:44px;left:50%;transform:translateX(calc(-50% + var(--label-offset,0px)));width:max-content;max-width:min(210px,45vw);padding:6px 10px;background:#0d181ff2;border:1px solid #e1d6b747;border-radius:5px;font-size:12px;line-height:1.4;text-align:center;color:#eee9dd;pointer-events:none}
.ga-hotspot[data-label-side="above"] span{top:auto;bottom:44px}
.ga-hotspot:hover span,.ga-hotspot:focus span{display:block}.ga-map-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.ga-map-room{padding:12px;border:1px solid #ffffff24;border-radius:7px}.ga-map-room[aria-current]{border-color:#c8b582;background:#c8b5820c}.ga-map-room h3{margin-top:0}.ga-map-room p{font-size:12px;color:#aabcc3;margin:6px 0}
@media(max-width:800px){.ga-actions{width:calc(56vw - 20px);left:10px;bottom:68px;max-height:32vh}.ga-nav{width:calc(44vw - 10px);right:10px;bottom:68px;max-height:32vh}.ga-root .ga-panel{padding:8px}.ga-panel h2{font-size:12px}.ga-panel .ga-muted{display:none}.ga-dialog{padding:16px}.ga-dialog label{display:block}.ga-dialog select{max-width:100%}}
@media(max-height:500px){.ga-actions,.ga-nav{max-height:45vh;bottom:12px}.ga-actions{left:10px}.ga-nav{right:10px}}
@media(prefers-reduced-motion:reduce){.ga-hotspot:before{transition:none}}

/* Field journal: navigation stays separate from the reading surface. */
.ga-journal-nav{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0}.ga-journal-nav button{flex:1;min-width:120px;font-size:13px}.ga-journal-nav button[aria-pressed="true"]{border-color:#d0bb86;background:#393b32;color:#f3e8cd}
.ga-journal-search{display:block!important;margin:12px 0!important}.ga-journal-search[hidden]{display:none!important}.ga-journal-search input{box-sizing:border-box;width:100%;margin-top:6px;background:#0d1a21}
.ga-journal-list{display:grid;gap:9px}.ga-journal-entry{padding:14px 16px;border:1px solid #abc3c326;border-radius:7px;background:#0c171c66}.ga-journal-entry p{white-space:pre-wrap;margin:6px 0}.ga-journal-entry .ga-caption{padding:10px 0}.ga-journal-list>button{width:100%}
.ga-reader-tools{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:12px 0}.ga-reader-tools button{min-width:44px;text-align:center}.ga-reader-tools span{font-size:12px;color:#bbc9ca}.ga-reader-paper{font-size:var(--reader-size,18px)!important;line-height:1.85!important;max-width:66ch;margin:18px auto!important;tab-size:4}
.ga-facsimile{margin:12px 0;border:1px solid #b8c7c43d;border-radius:8px;padding:12px}.ga-facsimile summary{cursor:pointer;color:#d8cba7}.ga-facsimile-scroll{max-height:58vh;overflow:auto;overscroll-behavior:contain;margin-top:10px}.ga-facsimile img{display:block;max-height:none;max-width:100%;width:auto;height:auto;margin:auto;object-fit:contain}.ga-facsimile[data-zoom="true"] img{width:160%;max-width:none}
.ga-inventory-note{color:#b8c7c9;font-size:13px}.ga-item .ga-muted{font-size:11px}.ga-notice{position:absolute;top:90px;left:50%;transform:translateX(-50%);max-width:min(430px,80vw);padding:10px 16px;background:#101e23f2;border:1px solid #cdb78370;border-radius:7px;box-shadow:0 8px 24px #0005;font-size:13px;text-align:center;white-space:pre-line;pointer-events:none}.ga-notice[hidden]{display:none}
@media(max-width:520px){.ga-modal{padding:10px}.ga-dialog{max-height:calc(100dvh - 20px);box-sizing:border-box;width:100%}.ga-dialog pre.ga-reader-paper{padding:16px}.ga-journal-nav button{min-width:calc(50% - 6px)}.ga-notice{top:78px}.ga-journal-search input{width:100%}}

/* The player can travel directly; the object list is a secondary aid. */
.ga-root::before{content:'';position:absolute;inset:auto 0 0;height:190px;background:linear-gradient(transparent,#03080bab);pointer-events:none}
.ga-fieldbar{position:absolute;inset:auto 24px 20px;display:grid;grid-template-columns:minmax(230px,320px) minmax(0,1fr);align-items:end;gap:28px;padding-right:184px;pointer-events:none}
.ga-dock{position:static;display:flex;flex-wrap:wrap;gap:4px;pointer-events:auto;padding:0;width:100%;max-width:none;background:transparent;border:0;box-shadow:none}
.ga-root .ga-dock button{font-size:12px;min-height:40px;padding:8px 12px;border-color:#d4e2d026;background:#10191de0;white-space:nowrap;border-radius:5px}
.ga-root .ga-dock button[aria-expanded="true"]{background:#c6b77a24;border-color:#d1bf8180;color:#f4e7bd}
.ga-root .ga-dock .ga-objective{width:100%;min-height:44px;padding:4px 0 9px;border:0;background:transparent;text-align:left;white-space:normal;pointer-events:auto;font-size:13px;line-height:1.5;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;color:#eee1ba;text-shadow:0 1px 6px #000}
.ga-objective::before{content:'ТЕКУЩАЯ ЦЕЛЬ';display:block;font-size:9px;letter-spacing:.15em;color:#bcb69f;margin-bottom:3px}
.ga-root .ga-dock .ga-objective:hover{color:#fff3c8;text-decoration:underline;text-underline-offset:3px}
.ga-dock[hidden],.ga-panel[hidden],.ga-nav[hidden],.ga-exits[hidden],.ga-fieldbar[hidden]{display:none!important}
.ga-root .ga-nav{position:static;pointer-events:none;display:flex;align-items:end;align-content:end;flex-wrap:wrap;gap:5px;width:auto;max-height:none;overflow:visible;padding:0;border:0;background:transparent;box-shadow:none}
.ga-route-heading{width:100%;font-size:9px;letter-spacing:.15em;color:#c0c7c3;text-shadow:0 1px 6px #000;margin:0 0 3px}
.ga-root .ga-nav .ga-route{pointer-events:auto;display:flex;align-items:center;gap:8px;width:auto;min-height:40px;margin:0;padding:8px 11px;border:1px solid #d7dfd23b;border-radius:5px;background:#0c161ce6;font-size:12px;line-height:1.4;color:#e1e6df}
.ga-route kbd{font:10px/1.4 Consolas,monospace;color:#9ba9aa;border-left:1px solid #aebfbb30;padding-left:7px}
.ga-root .ga-nav .ga-route:hover{background:#26352eea;border-color:#d0bd8d99}
.ga-root .ga-nav .ga-route.ga-recommended{background:#292a20ed;border-color:#d6bf7a;color:#f5e8c1}
.ga-root .ga-nav .ga-route[aria-disabled="true"]{color:#acb4b4;border-color:#b2bfba21;background:#10191dc9}
.ga-route-lock{font-size:10px;color:#a4aaa8}
.ga-root .ga-actions{left:24px;bottom:145px;width:300px;max-height:calc(100dvh - 230px)}
.ga-panel .ga-panel-close{width:auto!important;float:right;min-height:32px!important;padding:5px 9px!important;font-size:11px!important}
.ga-root .ga-panel button.ga-recommended{border-left:3px solid #d2bc7c;background:#ccb16c18}
.ga-current-step{font-size:12px;line-height:1.5;color:#e3d7b5;margin:10px 0}
.ga-exits{position:absolute;inset:0;pointer-events:none}
.ga-root .ga-exit[hidden]{display:none!important}
.ga-root .ga-exit{position:absolute;pointer-events:auto;transform:translate(-50%,-50%);display:flex;gap:8px;align-items:center;min-height:44px;max-width:200px;padding:6px 11px;border:1px solid #e6dbba85;border-radius:5px;background:#0c151cd9;color:#f3ead3;font-size:12px;box-shadow:0 3px 15px #0005;white-space:nowrap}
.ga-exit::before{content:'↗';font-size:20px;font-weight:400;line-height:1}
.ga-root .ga-exit.ga-recommended{border-color:#ecd095;background:#28271ce6}
.ga-root .ga-exit:hover{background:#3b4133ee;border-color:#ffe2a6}
.ga-modal{background:#040a10a8;backdrop-filter:blur(4px)}
.ga-dialog:not(.ga-ending){position:relative;padding:26px;width:min(820px,calc(100vw - 32px));max-height:calc(100dvh - 100px);background:#101b20;border-color:#abbeb438;border-radius:9px;scrollbar-width:thin;scrollbar-color:#6b7775 #101b20}
.ga-dialog>h2{padding-right:34px}
.ga-root .ga-dialog-close{position:sticky;top:0;float:right;width:32px;min-height:32px;margin:-8px -8px 0 4px;padding:0;text-align:center;font-size:21px;line-height:1;border-color:#abbeb430;background:#162329;z-index:2}
.ga-ending .ga-dialog-close{display:none}
body:has(.ga-modal) #gameLanguage{display:none}
body:has(.ga-modal) #gs-quick{top:16px;left:auto;right:16px}
.ga-modal:not(:has(.ga-ending)){padding:70px 16px 20px}
@media(max-width:1100px){.ga-fieldbar{padding-right:0;gap:20px;grid-template-columns:minmax(210px,280px) minmax(0,1fr)}.ga-root .ga-dock .ga-objective{font-size:12px}.ga-root .ga-nav .ga-route{padding:7px 9px;font-size:11px}.ga-route kbd{display:none}}
@media(max-width:680px){.ga-notice{top:112px}.ga-fieldbar{inset:auto 14px 14px;display:flex;flex-direction:column;align-items:stretch;gap:12px}.ga-root .ga-nav{order:0;gap:4px;max-height:none;overflow:visible}.ga-dock{order:1}.ga-root .ga-dock button{min-height:40px}.ga-root .ga-dock .ga-objective{padding:0 0 6px;font-size:12px;min-height:38px}.ga-objective::before{font-size:8px;margin-bottom:1px}.ga-root .ga-nav .ga-route{min-height:44px;padding:9px;font-size:11px}.ga-root .ga-actions{left:14px;bottom:270px;width:min(310px,calc(100vw - 28px));max-height:calc(100dvh - 390px)}.ga-dialog:not(.ga-ending){padding:18px;width:100%;max-height:calc(100dvh - 92px)}}
@media(max-height:500px) and (min-width:681px){.ga-fieldbar{inset:auto 16px 12px;gap:22px;grid-template-columns:245px minmax(0,1fr)}.ga-root .ga-dock .ga-objective{font-size:11px;min-height:30px;-webkit-line-clamp:1}.ga-objective::before{display:none}.ga-root .ga-dock button{min-height:36px;padding:6px 10px;font-size:11px}.ga-root .ga-nav .ga-route{min-height:34px;padding:6px 9px}.ga-route-heading{font-size:8px}.ga-root .ga-actions{left:16px;bottom:95px;max-height:calc(100dvh - 165px)}.ga-modal:not(:has(.ga-ending)){padding:60px 16px 12px}.ga-dialog:not(.ga-ending){padding:18px;max-height:calc(100dvh - 76px)}}
.ga-task-heading{margin:4px 0 8px}.ga-task-brief{color:#c7d0cf;line-height:1.65}.ga-task-current{display:flex;gap:16px;align-items:flex-start;padding:18px;border:1px solid #c7b47a66;border-radius:9px;background:linear-gradient(130deg,#c7b47a0e,#101c20);margin:16px 0}.ga-task-current h3{font-size:18px;line-height:1.45;margin:3px 0 8px}.ga-task-current p{margin:4px 0}.ga-task-eyebrow{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#d1bd88}.ga-task-thumb{width:118px;height:88px;object-fit:contain;flex:none;border-radius:5px;background:#080e11}.ga-task-route{font-size:12px;color:#acbfbb;line-height:1.6}.ga-task-controls{display:flex;gap:8px;flex-wrap:wrap}.ga-task-controls button{font-size:13px}.ga-task-history{margin:14px 0;padding:12px 0;border-top:1px solid #b5c6c32b}.ga-task-history summary{cursor:pointer;color:#bacbc6;line-height:1.5}.ga-task-history li{margin:9px 0;color:#9db4a8;line-height:1.5}.ga-task-branch{margin-top:24px;padding-top:18px;border-top:1px solid #bbc8c13b}.ga-task-branch h3{margin:6px 0}.ga-task-hint{margin:12px 0;padding:10px 13px;border:1px solid #b4c5bd26;border-radius:6px}.ga-task-hint summary{cursor:pointer;color:#d6c79e}.ga-task-hint p{line-height:1.6}.ga-map-room.ga-map-target{border-color:#d0b979;background:#c4ae6b14}.ga-map-room.ga-map-next{box-shadow:inset 3px 0 #d0b979}.ga-map-purpose{color:#d9c58b;font-size:12px}
.ga-inspection{margin:10px 0 16px;display:flex;gap:12px;align-items:center}.ga-dialog .ga-inspection>button{padding:0;border:1px solid #9bb1b24d;background:#060d11;flex:none;width:180px;overflow:hidden;border-radius:7px}.ga-inspection img{display:block;width:100%;height:114px;object-fit:cover}.ga-inspection figcaption{font-size:12px;color:#acbfbc;line-height:1.6}.ga-inspection figcaption span{display:block;color:#d5c392;margin-top:4px}.ga-dialog.ga-art-view{max-width:1100px}.ga-art-view .ga-document-art{max-height:calc(100dvh - 185px);width:100%;object-fit:contain}

@media(max-width:520px){.ga-task-current{gap:10px;padding:13px}.ga-task-current h3{font-size:16px}.ga-task-thumb{width:76px;height:66px}.ga-task-controls button{flex:1}.ga-inspection{gap:9px}.ga-dialog .ga-inspection>button{width:126px}.ga-inspection img{height:84px}}
@media(max-height:500px){.ga-root .ga-dock .ga-objective{min-height:16px;-webkit-line-clamp:1}.ga-task-current{padding:12px}.ga-task-thumb{height:64px}.ga-art-view .ga-document-art{max-height:calc(100dvh - 165px)}}

.ga-dialog.ga-tasks>h2{margin:0 0 10px}.ga-dialog.ga-tasks .ga-journal-nav{margin:8px 0 16px}.ga-dialog .ga-task-heading{font-size:20px;line-height:1.35;letter-spacing:normal;text-transform:none;color:#e8debd;margin:4px 0 8px}.ga-dialog .ga-task-current h3{font-size:18px;line-height:1.45;letter-spacing:normal;text-transform:none;color:#e6ded0;margin:3px 0 8px}.ga-dialog.ga-tasks p.ga-task-eyebrow{margin:4px 0}.ga-dialog.ga-tasks p.ga-task-brief{font-size:14px;margin:6px 0 12px}.ga-dialog.ga-tasks .ga-task-current{margin:10px 0;padding:14px}
@media(max-height:500px) and (min-width:640px){.ga-dialog.ga-tasks{padding:16px}.ga-dialog.ga-tasks>h2{font-size:17px;margin-bottom:5px}.ga-dialog.ga-tasks .ga-journal-nav{margin:5px 0 10px}.ga-dialog.ga-tasks .ga-journal-nav button{min-height:30px;padding:5px 8px;font-size:11px}.ga-dialog.ga-tasks>.ga-journal-list{grid-template-columns:minmax(180px,.85fr) minmax(260px,1.2fr);gap:6px 14px}.ga-tasks>.ga-journal-list>.ga-task-eyebrow{grid-column:1;grid-row:1}.ga-tasks>.ga-journal-list>.ga-task-heading{grid-column:1;grid-row:2;font-size:17px}.ga-tasks>.ga-journal-list>.ga-task-brief{grid-column:1;grid-row:3;font-size:12px;line-height:1.5}.ga-dialog.ga-tasks>.ga-journal-list>.ga-task-current{grid-column:2;grid-row:1/span 3;margin:0;padding:10px;gap:10px}.ga-dialog.ga-tasks .ga-task-current h3{font-size:15px}.ga-dialog.ga-tasks .ga-task-thumb{width:64px;height:58px}.ga-tasks>.ga-journal-list>.ga-task-controls{grid-column:2;grid-row:4}.ga-tasks>.ga-journal-list>.ga-task-hint{grid-column:1;grid-row:4;margin:0}.ga-tasks>.ga-journal-list>.ga-task-history,.ga-tasks>.ga-journal-list>.ga-task-branch{grid-column:1/-1}.ga-dialog.ga-tasks .ga-task-controls button{min-height:32px;padding:6px 9px;font-size:12px}}

@media(max-height:500px) and (min-width:681px){.ga-fieldbar{display:flex;flex-direction:column;align-items:stretch;gap:10px}.ga-nav{order:0}.ga-dock{order:1;flex-wrap:nowrap;align-items:center}.ga-root .ga-dock .ga-objective{flex:1;width:auto;min-width:0;min-height:36px;padding:0 10px 0 0;display:-webkit-box;-webkit-line-clamp:2;white-space:normal}.ga-root .ga-dock button:not(.ga-objective){flex:none}.ga-root .ga-actions{bottom:145px;max-height:calc(100dvh - 215px)}}

/* Instruments share canonical controls; their displays mirror entered values only. */
.ga-instrument-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:12px;margin:18px 0}.ga-instrument-field{padding:14px;border:1px solid #acbfc438;border-radius:9px;background:linear-gradient(150deg,#0a151bbf,#1b2a2cb0)}
.ga-dialog .ga-instrument-field>label{display:flex;flex-direction:column;align-items:stretch;gap:8px;margin:0;font-size:13px;color:#cad4d2}.ga-instrument-field input[type=number]{width:100%;text-align:center;font:22px/1.3 Consolas,monospace;background:#0a1519;color:#e9dba9}.ga-instrument-field select{width:100%;max-width:100%}
.ga-meter{display:block;width:160px;height:132px;max-width:100%;margin:4px auto}.ga-meter-face{fill:none;stroke:#61777b;stroke-width:3}.ga-meter-needle{stroke:#ddc887;stroke-width:3;stroke-linecap:round}.ga-meter text{fill:#a9bfc1;font:11px Consolas,monospace}.ga-instrument-value{text-align:center;display:block;font:18px/1.4 Consolas,monospace;color:#eadba5;margin:3px 0 10px}
.ga-adjust{display:flex;align-items:center;gap:7px}.ga-root .ga-adjust button{width:44px;min-width:44px;text-align:center;font-size:20px;padding:5px}.ga-root .ga-adjust input[type=range]{width:100%;min-width:0;flex:1;min-height:44px;padding:0;border:0;accent-color:#d5c18a;background:transparent}
.ga-sequence{display:grid;grid-template-columns:repeat(auto-fit,minmax(85px,1fr));gap:8px;list-style:none;padding:0;margin:14px 0}.ga-sequence li{min-height:58px;padding:8px;border:1px solid #91a6aa42;border-radius:7px;background:#0d1a20;text-align:center;font-size:13px}.ga-sequence li[data-filled=true]{border-color:#cbbb82a0;background:#cbbb8210;color:#eee2b9}.ga-sequence small{display:block;font-size:10px;color:#98adae;margin-bottom:3px}
.ga-attempt{font-size:12px;line-height:1.6;color:#d9c9a5;padding:8px 11px;border-left:2px solid #b7a576;background:#b7a5760c}.ga-reference{margin:12px 0;padding:12px;border:1px solid #b5c6c32c;border-radius:7px}.ga-reference>summary{cursor:pointer;color:#d5c7a8;font-size:13px}.ga-result{padding:10px 13px;border:1px solid #c3ba8a44;border-radius:6px;color:#e2d5a9;background:#c3ba8a0b}
@media(max-width:520px){.ga-instrument-grid{grid-template-columns:1fr}.ga-meter{height:112px}.ga-sequence{grid-template-columns:repeat(auto-fit,minmax(70px,1fr))}}

.ga-physical{margin:18px 0;padding:14px;border:1px solid #b9c8bd44;border-radius:10px;background:#071318}.ga-physical-board{position:relative;width:100%;touch-action:none;user-select:none}.ga-physical-board>svg{display:block;width:100%;height:auto}.ga-physical [role=slider],.ga-physical .ga-punch-layer{cursor:grab;outline:none}.ga-physical [role=slider]:focus-visible,.ga-physical .ga-punch-layer:focus-visible{filter:drop-shadow(0 0 5px #fff2b0)}.ga-physical-status{font-size:13px;color:#c9d4c6;min-height:24px;margin:10px 0 0}.ga-physical svg text{font:13px Consolas,monospace;fill:#d6dfd4}.ga-antenna{aspect-ratio:640/300;min-height:280px}.ga-antenna>svg{position:absolute;inset:0;height:100%;pointer-events:none}.ga-root .ga-antenna button{position:absolute;width:130px;min-height:44px;padding:7px 9px;font-size:12px;text-align:center;z-index:1}.ga-antenna [data-cable]{left:10px}.ga-antenna [data-socket]{right:10px}.ga-antenna [aria-pressed=true]{outline:2px solid #d9c891;outline-offset:2px}
@media(max-width:520px){.ga-physical{padding:8px}.ga-root .ga-antenna button{width:105px;font-size:11px}.ga-antenna [data-cable]{left:0}.ga-antenna [data-socket]{right:0}}

.ga-dialog.ga-ending{width:min(1200px,98vw);background:#060c10;padding:0;overflow:hidden;border-color:#c3bf9b44;position:relative;display:flex;flex-direction:column}.ga-ending h2{position:static;flex:0 0 auto;text-align:center;padding:13px 24px;text-shadow:0 2px 10px #000;margin:0;font-size:18px}.ga-ending>.ga-document-art{width:100%;height:min(54vh,600px);max-height:none;object-fit:contain;flex:0 0 auto;border:0;border-radius:0;margin:0;animation:ga-ending-reveal 1.2s ease-out both}.ga-ending-body{padding:22px 26px;background:linear-gradient(#0d171c,#070e12);max-height:none;min-height:0;overflow:auto;flex:1}.ga-ending-body .ga-scene{font:20px/1.6 Georgia,serif;padding:0 0 8px}.ga-ending-body .ga-caption{font-size:14px}.ga-ending-body button{margin:6px 8px 2px 0}.ga-credits{white-space:pre-line;line-height:2;text-align:center;padding:22px 10px}.ga-ending-progress{height:2px;background:#465651;margin:0}.ga-ending-progress span{display:block;height:100%;background:#d0c18e;width:var(--ending-read,0%)}
body:has(.ga-ending) #gameLanguage{display:none}body:has(.ga-ending) #gs-quick{top:16px;left:auto;right:16px}.ga-modal:has(.ga-ending){padding-top:72px}.ga-dialog.ga-ending{max-height:calc(100dvh - 96px)}
@media(max-height:520px) and (min-width:640px){.ga-dialog.ga-ending{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);height:calc(100dvh - 96px)}.ga-ending h2{grid-column:1/-1;padding:10px 18px;font-size:16px}.ga-dialog.ga-ending>.ga-document-art{grid-column:1;grid-row:2;height:100%;max-height:100%;min-height:0}.ga-ending-progress{display:none}.ga-dialog.ga-ending>.ga-ending-body{grid-column:2;grid-row:2;max-height:none;min-height:0;padding:14px 18px}.ga-dialog.ga-ending .ga-ending-body .ga-scene{font-size:16px;line-height:1.5}}
@keyframes ga-ending-reveal{from{filter:brightness(.78)}to{filter:brightness(1)}}@media(prefers-reduced-motion:reduce){.ga-ending>.ga-document-art{animation:none}}@media(max-height:600px){.ga-ending>.ga-document-art{height:46vh}.ga-ending-body{max-height:44vh;padding:14px 18px}.ga-ending-body .ga-scene{font-size:17px}}


/* Quiet environmental cues remain compact so the room itself stays in view. */
.ga-modal:has(.ga-ambient-scene){background:transparent;backdrop-filter:none;display:flex;justify-content:flex-start;align-items:flex-end;padding:16px 16px 124px;pointer-events:none}
.ga-modal .ga-dialog.ga-ambient-scene{pointer-events:auto;width:min(420px,calc(100vw - 32px));max-height:min(42vh,360px);padding:14px 18px;background:#101b20ed;border:1px solid #aebbb155;box-shadow:0 10px 34px #0009}
.ga-dialog.ga-ambient-scene h2{font-size:13px;letter-spacing:.08em;margin:0 0 6px;color:#bcc8c1}
.ga-dialog.ga-ambient-scene .ga-scene{margin:6px 0 12px;font-size:15px;line-height:1.55}
@media(max-width:640px){.ga-modal:has(.ga-ambient-scene){padding:12px 12px 112px}.ga-modal .ga-dialog.ga-ambient-scene{width:100%;max-height:38vh}}

.ga-ambient-line{position:absolute;top:92px;left:24px;z-index:2;pointer-events:none;max-width:min(440px,calc(100vw - 48px));padding:12px 18px 13px;border-left:2px solid #b9ae8cbb;background:linear-gradient(90deg,#071014e8,#071014a5 78%,transparent);color:#e6e9e1;text-shadow:0 1px 8px #000;animation:ga-ambient-appear .65s ease both}
.ga-ambient-line[hidden]{display:none!important}.ga-ambient-line small{display:block;font-size:9px;letter-spacing:.19em;color:#abbcb8}.ga-ambient-line p{margin:6px 0 0;line-height:1.6;font:14px/1.6 Georgia,serif}
@keyframes ga-ambient-appear{from{opacity:0;transform:translateX(-9px)}to{opacity:1;transform:translateX(0)}}
@media(max-width:680px){.ga-ambient-line{top:76px;left:14px;max-width:calc(100vw - 28px);padding:9px 12px}.ga-ambient-line p{font-size:13px}}
@media(prefers-reduced-motion:reduce){.ga-ambient-line{animation:none}}


.ga-dock .ga-next-action{border-color:#cbb879aa!important;background:#3b3521e8!important;color:#f5e4b5!important;font-weight:600;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ga-dock .ga-next-action::before{content:'E';display:inline-flex;align-items:center;justify-content:center;border:1px solid #d6c18880;color:#ecd9a3;width:20px;height:20px;margin-right:9px;border-radius:4px;font:11px Consolas,monospace}
.ga-dock .ga-next-action:hover{background:#51482beb!important}
.ga-dock .ga-next-action[hidden]{display:none!important}
@media(max-width:680px){.ga-dock .ga-next-action{font-size:12px;flex:1;white-space:normal}.ga-dock .ga-next-action::before{display:none}}
/* Optional scan of physical interaction markers. */
.ga-root .ga-actions .ga-scan-control{border-color:#b7a77a70;background:#b7a77a0d;color:#e3d3a9;margin:5px 0 10px}
.ga-root.ga-scanning .ga-hotspot:not([hidden]) span{display:block;pointer-events:none}
.ga-root.ga-scanning .ga-hotspot:not([hidden])::before{box-shadow:0 0 0 5px #b5a47b21,0 0 14px #e0cca358}
@media(max-width:680px){
 .ga-root .ga-nav{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;max-width:100%;padding:0 0 5px}
 .ga-root .ga-nav .ga-route{flex:0 0 auto}
 .ga-root .ga-nav .ga-route-heading{display:none}
}

.ga-root .ga-unavailable{margin:12px 0 2px;border-top:1px solid #b8c3b72b;padding:11px 0;color:#9facaa}
.ga-root .ga-unavailable>summary{cursor:pointer;font-size:11px;color:#a7b5b0;line-height:1.5}
.ga-root .ga-unavailable-item{padding:10px 0;border-bottom:1px solid #b8c3b718}
.ga-root .ga-unavailable-item strong{font-size:12px;font-weight:500;color:#bfc7bd}
.ga-root .ga-unavailable-item p{font-size:11px;line-height:1.5;margin:4px 0 0}


/* In-world optional decisions: brief, spatial, and no full-screen document card. */
.ga-modal:has(.ga-dialog.ga-field-choice){background:transparent;backdrop-filter:none;display:flex;justify-content:flex-start;align-items:flex-end;padding:20px 22px 142px;pointer-events:none}
.ga-modal .ga-dialog.ga-field-choice{pointer-events:auto;width:min(490px,calc(100vw - 44px));max-height:min(72vh,560px);padding:19px 22px 18px;background:#0c171cfa;border:1px solid #c9c0a46e;box-shadow:0 20px 54px #000a;border-radius:7px}
.ga-dialog.ga-field-choice h2{font:500 18px/1.35 Georgia,serif;letter-spacing:0;color:#e8e0c9;margin:0 0 9px}
.ga-dialog.ga-field-choice pre{background:none;color:#c6cfcb;border:0;border-left:2px solid #bdaf8268;border-radius:0;font:15px/1.65 Georgia,serif;padding:3px 0 3px 13px;margin:12px 0 16px;white-space:pre-wrap}
.ga-root .ga-dialog.ga-field-choice>button:not(.ga-dialog-close){display:block;width:100%;min-height:44px;margin:6px 0;padding:10px 13px;border-color:#bcb18f55;background:#bdac7e0a;color:#e7e0d0;font-size:13px}
.ga-root .ga-dialog.ga-field-choice>button:not(.ga-dialog-close):hover{border-color:#dcc690a0;background:#a8966929}
.ga-dialog.ga-field-choice .ga-error{margin:3px 0;font-size:12px}
@media(max-width:680px){.ga-modal:has(.ga-dialog.ga-field-choice){padding:12px 12px 100px}.ga-modal .ga-dialog.ga-field-choice{width:100%;padding:13px 16px;max-height:calc(100dvh - 140px)}.ga-dialog.ga-field-choice h2{font-size:16px}.ga-dialog.ga-field-choice pre{font-size:14px}}
@media(max-height:500px) and (min-width:681px){.ga-modal:has(.ga-dialog.ga-field-choice){padding:8px 12px 64px}.ga-modal .ga-dialog.ga-field-choice{padding:9px 15px;max-height:calc(100dvh - 74px)}.ga-dialog.ga-field-choice pre{margin:5px 0;font-size:13px}}


.ga-root .ga-intro-tip{display:block;flex:1 0 100%;font:10px/1.5 'Segoe UI',sans-serif;color:#b6c4be;letter-spacing:.015em;opacity:.88;padding:2px 0 0}
.ga-root .ga-intro-tip[hidden]{display:none!important}
@media(max-width:680px){.ga-root .ga-intro-tip{font-size:10px;line-height:1.35;padding:0}}


.ga-root .ga-hotspot.ga-investigation::before{width:10px;height:10px;background:#342e24e8;border-color:#c9bc9788;box-shadow:0 0 0 4px #0b14147a,0 2px 8px #0008}
.ga-root .ga-hotspot.ga-investigation:hover::before,.ga-root .ga-hotspot.ga-investigation:focus-visible::before{background:#d7c598;border-color:#f4e2bb;box-shadow:0 0 0 5px #ddc8a122,0 2px 8px #0008}


/* Field investigations are tactile miniatures, not full-screen question cards. */
.ga-root .ga-field-board{border-top:1px solid #bcb18b36;padding:12px 0 6px;margin:3px 0 8px}
.ga-field-instruction{font:12px/1.5 'Segoe UI',sans-serif!important;color:#b7c5c0;margin:0 0 10px!important}
.ga-field-stage{position:relative;width:100%;height:150px;overflow:hidden;border:1px solid #778c8973;border-radius:5px;background:radial-gradient(ellipse at 55% 35%,#223034,#081116 83%)}
.ga-root .ga-field-range-label{display:block;margin:10px 0 2px;color:#c6d0c9;font-size:12px}
.ga-root .ga-field-range-label input[type=range]{display:block;width:100%;min-height:38px;border:0;padding:0;background:none;accent-color:#d4c08a;cursor:ew-resize}
.ga-field-status{font-size:11px;line-height:1.5;min-height:18px;color:#aab9b3;margin:4px 0 2px}
.ga-field-reveal{font:14px/1.55 Georgia,serif;color:#e9dfbd;border-left:2px solid #d6c0899c;padding:6px 12px;background:#d6c0890b;margin:10px 0}
.ga-field-reveal[hidden],.ga-field-options[hidden]{display:none!important}
.ga-field-options{display:grid;grid-template-columns:1fr;gap:6px;margin:10px 0 4px}
.ga-root .ga-dialog.ga-field-choice .ga-field-options button{width:100%;min-height:44px;padding:10px 12px;border-color:#bcb18f63;background:#bdac7e17;color:#e7e0d0;font-size:13px;text-align:left}
.ga-root .ga-dialog.ga-field-choice .ga-field-options button:hover{border-color:#f0d9a1;background:#a896693d}
.ga-field-object{position:absolute;top:21%;left:15%;right:15%;height:63%;border:1px solid #a6b3ab6d;display:grid;place-items:center}
.ga-field-object-label{font:13px/1.5 Consolas,monospace;letter-spacing:.12em;color:#a8b7a7;text-shadow:0 1px #000}
.ga-task-slide .ga-field-stage{background:linear-gradient(120deg,#3d3830,#191b1b 60%,#2b2a21)}
.ga-task-slide .ga-field-object{top:20%;bottom:20%;height:auto;background:#a79a79;color:#272920;box-shadow:0 8px 20px #0006;transform:translateX(var(--shift,0%))}
.ga-task-slide .ga-field-object-label{color:#2c2920;transform:rotate(-3deg)}
.ga-task-slide .ga-field-stage::after{content:'04 / ПРИЁМ';position:absolute;top:35%;left:21%;font:13px/1.6 Consolas,monospace;color:#c8c4a4;z-index:0}
.ga-task-slide .ga-field-object{z-index:1}
.ga-task-focus .ga-field-stage{background:radial-gradient(ellipse at center,#283b3d 2%,#080d0e 72%)}
.ga-task-focus .ga-field-object{left:34%;right:34%;top:4%;bottom:4%;height:auto;border:3px solid #839e9b;border-radius:50%;background:radial-gradient(circle,#203236,#080d11);filter:blur(4px)}
.ga-task-focus .ga-field-object-label{color:#b1c0af;font-size:10px;letter-spacing:.05em;white-space:nowrap}
.ga-task-tap .ga-field-stage{display:grid;place-items:center;background:repeating-linear-gradient(90deg,#151f22 0 16px,#182528 16px 18px)}
.ga-field-dial{width:125px;height:125px;border:8px solid #485458;border-radius:50%;display:grid;place-items:center;background:#1e2c30;box-shadow:inset 0 0 20px #000b,0 3px 18px #0008;position:relative}
.ga-field-dial::after{content:'';position:absolute;left:50%;top:5px;height:18px;width:3px;background:#d5c28b;transform-origin:50% 52px;transform:translateX(-50%) rotate(var(--turn,0deg));transition:transform .16s}
.ga-field-dial-number{font:26px Consolas,monospace;color:#ddcd9b}
.ga-root .ga-field-advance{width:100%;min-height:44px;margin:8px 0;border-color:#bcb18f63;background:#bdac7e1c;color:#e6d9be;text-align:center}
.ga-task-trace .ga-field-stage{background:linear-gradient(145deg,#353d41,#141c21 60%,#293236)}
.ga-field-drop{position:absolute;transform:translate(-50%,-50%);width:46px;height:46px;min-height:46px!important;border:0!important;background:transparent!important;border-radius:50%!important;padding:0!important}
.ga-field-drop::after{content:'';display:block;width:13px;height:19px;margin:auto;border-radius:65% 60% 70% 75%;transform:rotate(35deg);background:#8aafaf;box-shadow:inset 2px 2px 6px #d5ebef88,0 0 12px #98c1c160}
.ga-field-drop.ga-traced::after{background:#d7c48e;box-shadow:0 0 0 4px #d7c48e2d}
.ga-field-drop:disabled{opacity:.75}
.ga-task-wipe .ga-field-stage{touch-action:none;cursor:ew-resize;background:linear-gradient(145deg,#738583,#283a40 36%,#657478 65%,#16252a)}
.ga-task-wipe .ga-field-stage::before{content:'';position:absolute;inset:-40px -15%;background:repeating-linear-gradient(110deg,#e4e7de88 0 2px,#9fb8b95c 3px 11px);opacity:calc(1 - var(--cleared-number,0));pointer-events:none}
.ga-task-wipe .ga-field-stage::after{content:'';position:absolute;left:28%;top:30%;width:43%;height:34%;border:2px solid #d4daceaa;border-bottom:0;transform:rotate(-16deg);border-radius:50% 50% 0 0;opacity:var(--reveal,0);pointer-events:none}
@media(max-width:680px){.ga-field-stage{height:118px}.ga-field-dial{width:100px;height:100px}.ga-field-instruction{font-size:11px!important}.ga-root .ga-field-board{padding:8px 0 2px}}


.ga-task-tune .ga-field-stage{background:linear-gradient(#1b292d,#0c171c 64%,#27302b)}
.ga-task-tune .ga-field-object{height:72px;top:25%;left:10%;right:10%;border:3px solid #687871;background:repeating-linear-gradient(90deg,#afab875b 0 1px,transparent 1px 22px),linear-gradient(#1b2424,#1c3338);box-shadow:0 4px 14px #0006}
.ga-task-tune .ga-field-object::after{content:'';position:absolute;left:var(--needle,0%);top:7px;bottom:7px;width:2px;background:#ddcc9c;box-shadow:0 0 10px #e3d4af8c}
.ga-task-tune .ga-field-object-label{font-size:13px;color:#c0cbba;letter-spacing:.1em}
.ga-task-listen .ga-field-stage{display:grid;place-items:center;background:radial-gradient(ellipse,#263938,#0b1719)}
.ga-task-listen .ga-field-dial{border:3px solid #6b817c;border-radius:50%;background:repeating-radial-gradient(circle,#354d4c 0 1px,transparent 2px 17px),#132123}
.ga-task-listen .ga-field-dial::after{background:#b9b59c;opacity:.6}
.ga-task-listen .ga-field-dial-number{font:24px Georgia,serif;letter-spacing:8px;color:#d8cfb4}


/* Main story hardware: tactile consoles with the original input/answer logic. */
.ga-root .ga-hardware{margin:12px 0;padding:13px;background:linear-gradient(155deg,#1a2629,#0c151a 75%);border:1px solid #75898491;border-radius:7px;box-shadow:inset 0 0 18px #0005,0 6px 20px #0005}
.ga-root .ga-hardware-heading{display:flex;flex-direction:column;gap:2px;margin-bottom:13px;padding-bottom:8px;border-bottom:1px solid #8a9d9175;color:#e3dfcb}
.ga-root .ga-hardware-kicker{font:10px/1.3 Consolas,monospace;letter-spacing:.18em;color:#adb7a7}
.ga-root .ga-hardware-heading strong{font:500 15px/1.4 Georgia,serif;letter-spacing:.02em}
.ga-root .ga-hardware-board{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(205px,100%),1fr));gap:11px}
.ga-root .ga-hardware-control{min-width:0;padding:10px 11px;background:#081115b0;border:1px solid #63736e77;border-radius:4px;position:relative}
.ga-root .ga-hardware-control-title{font:12px/1.4 'Segoe UI',sans-serif;color:#c8d3c8;min-height:18px;margin:0 0 12px}
.ga-root .ga-hardware-gauge{min-height:76px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:13px;background:radial-gradient(ellipse,#1f3334,#0d191b 80%);border:1px solid #5d716a70;border-radius:4px;box-shadow:inset 0 0 15px #0009}
.ga-root .ga-hardware-number{font:26px/1 Consolas,monospace;color:#dfd6b7;letter-spacing:.04em;text-shadow:0 0 14px #d4c48e30}
.ga-root .ga-hardware-track{width:76%;height:7px;border-radius:1px;background:repeating-linear-gradient(90deg,#395149 0 2px,#1b2524 2px 7px);border:1px solid #75877f6a;overflow:hidden}
.ga-root .ga-hardware-fill{display:block;width:var(--level,0%);height:100%;background:linear-gradient(90deg,#7c9890,#d4c28d);box-shadow:0 0 10px #d7bf8177}
.ga-root .ga-hardware-adjust{display:flex;align-items:center;gap:5px;margin-top:10px}
.ga-root .ga-hardware-adjust button{min-width:39px;min-height:42px;text-align:center!important;padding:4px 8px;background:#243330;border-color:#6b8077}
.ga-root .ga-hardware-adjust input[type=range]{min-width:0;flex:1;width:100%;padding:0;margin:0;border:none;min-height:36px;background:transparent;accent-color:#d3bf85}
.ga-root .ga-hardware-switches{display:flex;flex-wrap:wrap;gap:6px;align-content:flex-start}
.ga-root .ga-hardware-switch{flex:1 1 auto;min-height:45px;padding:6px 10px;text-align:center!important;font:12px/1.35 Consolas,monospace;background:#1e2a28;border:1px solid #6c8076;transition:background .12s,border-color .12s}
.ga-root .ga-hardware-switch[aria-pressed=true]{color:#f1e6c8;border-color:#e0c789;background:#615a3980;box-shadow:inset 0 0 8px #dac58c24}
.ga-root .ga-hardware-status{min-height:17px;margin:11px 0 0;font:11px/1.5 Consolas,monospace;color:#99b1a8}
.ga-root .ga-hardware-precise{margin-top:4px}
.ga-root .ga-sequence-machine{padding:13px 12px;background:linear-gradient(140deg,#27302c,#111a1e 70%);border:1px solid #83918672;border-radius:5px;box-shadow:inset 0 0 18px #0007}
.ga-root .ga-sequence-instruction{margin:0 0 9px;color:#c4cab9;font:12px/1.5 Georgia,serif}
.ga-root .ga-sequence-status{font:11px/1.4 Consolas,monospace;color:#b6c9be}
.ga-root .ga-sequence-machine .ga-sequence{display:flex;gap:6px;flex-wrap:wrap;margin:7px 0 13px;padding:0;list-style:none}
.ga-root .ga-sequence-machine .ga-sequence li{flex:1 1 66px;min-width:66px;max-width:130px;min-height:52px;display:flex;flex-direction:column;gap:4px;padding:7px;border:1px dashed #7a918277;border-radius:4px;background:#0b1417ad;color:#d9dcc8}
.ga-root .ga-sequence-machine .ga-sequence li[data-filled=true]{border-style:solid;border-color:#cfbc89;background:#695f3940}
.ga-root .ga-sequence-machine .ga-sequence li small{font:9px/1.2 Consolas,monospace;color:#a1ad9e}
.ga-root .ga-sequence-machine .ga-sequence li span{font:11px/1.3 'Segoe UI',sans-serif;overflow-wrap:anywhere}
.ga-root .ga-sequence-props{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:8px;align-items:stretch;margin:5px 0 13px}
.ga-root .ga-sequence-prop{min-height:74px;display:flex;justify-content:center;align-items:flex-end;position:relative;text-align:center!important;padding:28px 8px 10px;border:1px solid #8e9c8d;border-radius:5px;background:linear-gradient(155deg,#36413a,#1c2b2a 60%,#29302c);color:#efe9d4;box-shadow:inset 0 1px #ffffff16,0 4px 8px #0005;font:12px/1.3 'Segoe UI',sans-serif}
.ga-root .ga-sequence-prop:before{content:'';position:absolute;top:8px;left:50%;transform:translateX(-50%);width:28px;height:15px;border:2px solid #b8b9a1;border-radius:4px;box-shadow:inset 0 3px 7px #0009}
.ga-root .ga-sequence-prop[data-used=true]{border-color:#c6b37d;background:linear-gradient(155deg,#4b5039,#242c2a)}
.ga-root .ga-sequence-prop:focus-visible{outline:2px solid #e1ca91;outline-offset:2px}
.ga-root .ga-sequence-prop:hover{border-color:#e4d2a5}
.ga-root .ga-sequence-tools{display:flex;flex-wrap:wrap;gap:8px}
.ga-root .ga-sequence-tools button{flex:1 1 125px;min-height:42px;padding:8px 10px;font-size:12px;background:#26322e}
.ga-root .ga-sequence-tea_sequence .ga-sequence-prop{background:linear-gradient(160deg,#454039,#272623 75%);border-color:#998b76}
.ga-root .ga-sequence-plumb_seq .ga-sequence-prop{background:linear-gradient(160deg,#334449,#14252a 75%);border-color:#72909a}
.ga-root .ga-sequence-cooking .ga-sequence-prop{background:linear-gradient(160deg,#424239,#25251f 75%);border-color:#888c6a}
.ga-root .ga-sequence-vhs_assemble .ga-sequence-prop{background:linear-gradient(160deg,#3b3a3a,#1c2425 75%);border-color:#92969a}
@media(max-width:680px){.ga-root .ga-hardware{padding:9px}.ga-root .ga-hardware-board{grid-template-columns:1fr;gap:7px}.ga-root .ga-hardware-control{padding:8px}.ga-root .ga-hardware-gauge{min-height:56px}.ga-root .ga-hardware-number{font-size:20px}.ga-root .ga-sequence-machine{padding:9px}.ga-root .ga-sequence-props{grid-template-columns:repeat(2,minmax(0,1fr))}.ga-root .ga-sequence-prop{min-height:58px}}


.ga-root .ga-hardware-knob{display:grid;place-items:center;position:relative;width:86px;height:66px;min-height:66px;border-radius:40px;background:radial-gradient(circle at 37% 27%,#354c49,#1a2b2b 58%,#101d1f);border:3px solid #708981;box-shadow:inset 0 3px 9px #090d10c2,0 4px 10px #0007;text-align:center!important;padding:8px}
.ga-root .ga-hardware-knob::before{content:'';position:absolute;top:2px;left:calc(50% - 1px);width:2px;height:10px;background:#d6c695;transform-origin:1px 30px;transform:rotate(var(--angle,0deg));box-shadow:0 0 4px #ddca9977}
.ga-root .ga-hardware-knob:hover{border-color:#d0c499;background:radial-gradient(circle at 37% 27%,#405951,#1a2b2b 58%,#101d1f)}
.ga-root .ga-hardware-knob:focus-visible{outline:2px solid #ddca99;outline-offset:3px}
.ga-root .ga-hardware-number{pointer-events:none;font-size:22px}
@media(max-width:680px){.ga-root .ga-hardware-knob{width:80px;height:58px;min-height:58px}.ga-root .ga-hardware-number{font-size:19px}}


/* Optional physical investigation board: simple collected paper slips, not a new HUD. */
.ga-root .ga-evidence-eyebrow{font:10px/1.4 Consolas,monospace;letter-spacing:.18em;color:#a8baa9;margin:4px 0}
.ga-root .ga-evidence-summary{font:13px/1.5 Consolas,monospace;color:#e4d9b4;margin:5px 0 8px}
.ga-root .ga-evidence-explain{font:13px/1.6 Georgia,serif;color:#b8c9c4;margin:6px 0 15px;max-width:74ch}
.ga-root .ga-evidence-board{display:grid;grid-template-columns:1fr;gap:14px}
.ga-root .ga-evidence-case{border:1px solid #8d957a55;background:linear-gradient(145deg,#1c2524,#0e171b 68%);padding:15px;border-radius:5px;box-shadow:0 7px 18px #0004}
.ga-root .ga-evidence-case[data-status=ready]{border-color:#dac18b7d}
.ga-root .ga-evidence-case[data-status=linked]{border-color:#a9b99d62}
.ga-root .ga-evidence-case h3{font:500 18px/1.35 Georgia,serif;color:#e4ddc5;letter-spacing:.01em;margin:5px 0 14px}
.ga-root .ga-evidence-status{font:9px/1.5 Consolas,monospace;letter-spacing:.15em;color:#93b0a7}
.ga-root .ga-evidence-slips{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}
.ga-root .ga-evidence-slip{display:flex;flex-direction:column;align-items:flex-start;gap:5px;min-width:0;min-height:120px;text-align:left;padding:13px 12px;background:linear-gradient(135deg,#c6c2ab,#999788);border:1px solid #d7d2b6;border-radius:2px;color:#262924;font:12px/1.45 Georgia,serif;box-shadow:0 5px 15px #0005;transition:transform .12s,border-color .12s;overflow-wrap:anywhere}
.ga-root .ga-evidence-slip small{font:10px/1.4 Consolas,monospace;color:#525a52}
.ga-root .ga-evidence-slip strong{font:600 15px/1.35 Georgia,serif;color:#1e2926}
.ga-root .ga-evidence-slip p{font:12px/1.5 Georgia,serif;color:#37433c;margin:0}
.ga-root .ga-evidence-slip[data-missing=true]{background:repeating-linear-gradient(128deg,#172124,#172124 8px,#1b2829 8px,#1b2829 16px);border-style:dashed;border-color:#506661;color:#8ca09a;opacity:.72}
.ga-root .ga-evidence-slip[data-missing=true] small,.ga-root .ga-evidence-slip[data-missing=true] strong,.ga-root .ga-evidence-slip[data-missing=true] p{color:#91a6a0}
.ga-root .ga-evidence-slip[aria-pressed=true]{border:2px solid #e5ca8d;transform:translateY(-3px);box-shadow:0 2px 0 #d3bc8a,0 9px 20px #0007}
.ga-root .ga-evidence-slip:disabled{cursor:default}
.ga-root .ga-evidence-case[data-status=linked] .ga-evidence-slip:not([data-missing]){opacity:.84}
.ga-root .ga-evidence-controls{display:flex;justify-content:flex-end;margin-top:11px}
.ga-root .ga-evidence-connect{background:#61573b;border-color:#cbb17a;color:#f7ebcb;font-size:13px;font-weight:600;min-height:43px;text-align:center}
.ga-root .ga-evidence-conclusion{margin:12px 0 7px;padding:10px 12px;border-left:2px solid #cfc08e;background:#cfc08e12;font:14px/1.65 Georgia,serif;color:#e5e0cd}
.ga-root .ga-evidence-footnote{display:block;margin:11px 0 0;font-size:11px;line-height:1.4;color:#9ab0a5}
@media(max-width:640px){.ga-root .ga-evidence-case{padding:11px}.ga-root .ga-evidence-slips{gap:7px}.ga-root .ga-evidence-slip{padding:9px;min-height:100px}.ga-root .ga-evidence-slip strong{font-size:13px}.ga-root .ga-evidence-slip p{font-size:11px}.ga-root .ga-evidence-case h3{font-size:16px}}

`;

class UI{
 ensureVoice(){if(this.voice)return this.voice;if(!api.VoiceQueue||!this.hooks.voice)return null;
  this.voice=new api.VoiceQueue({resolve:id=>this.data.voiceAssets?.[id]?this.hooks.voice(this.data.voiceAssets[id]):null,volume:()=>this.hooks.volume?.()??1,
   createAudio:()=>{const a=el('audio');a.className='ga-voice';a.hidden=true;this.root.append(a);return a;},
   blocked:(reason,id)=>{this.voiceRetry?.remove();this.voiceRetry=null;if(!reason||!this.box?.isConnected)return;
    if(reason==='gesture'){this.voiceRetry=this.button(this.box,'Озвучить реплики',()=>this.voice.play());}
    else this.voiceRetry=el('p','Запись '+id+' недоступна. Текст реплики остаётся на экране.','ga-muted');if(reason!=='gesture')this.box.append(this.voiceRetry);}});return this.voice;
 }
 speakLines(lines){this.stopVoice?.();this.ensureVoice()?.enqueue((lines||[]).map(l=>l.id).filter(Boolean));}
 stopVoice(){this.voice?.stop();}
 setVoicePaused(paused){this.voice?.setPaused(paused);if(paused){this.resumeVoiceMedia=!!this.voiceMediaElement&&!this.voiceMediaElement.paused;this.voiceMediaElement?.pause();}else if(this.resumeVoiceMedia){this.resumeVoiceMedia=false;this.voiceMediaElement?.play()?.catch?.(()=>{});}}
 syncVoiceVolume(){this.voice?.syncVolume();if(this.voiceMediaElement)this.voiceMediaElement.volume=Math.max(0,Math.min(1,this.hooks.volume?.()??1));}
 showArt(parent,src,alt='Сюжетная иллюстрация'){
  if(!src||!isImageSource(src))return;
  const img=el('img');img.src=src;img.alt=alt;img.className='ga-document-art';parent.append(img);
 }
 constructor(data,hooks={}){this.data=data;this.hooks=hooks;this.root=el('div',undefined,'ga-root');this.root.hidden=true;this.root.setAttribute('translate','no');this.root.append(el('style',CSS));this.left=el('section',undefined,'ga-panel ga-actions');this.right=el('nav',undefined,'ga-nav');this.right.setAttribute('aria-label','Выходы из комнаты');this.exits=el('div',undefined,'ga-exits');this.exits.setAttribute('aria-label','Двери в панораме');this.variant=el('div',undefined,'ga-variant');this.hotspots=el('div',undefined,'ga-hotspots');this.hotspots.setAttribute('aria-label','Объекты в панораме');this.notice=el('div',undefined,'ga-notice');this.notice.setAttribute('role','status');this.notice.setAttribute('aria-live','polite');this.notice.hidden=true;this.ambientLine=el('aside',undefined,'ga-ambient-line');this.ambientLine.hidden=true;this.ambientLine.setAttribute('role','status');this.ambientLine.setAttribute('aria-live','polite');this.dock=el('nav',undefined,'ga-dock');this.dock.setAttribute('aria-label','Управление сменой');this.objective=this.button(this.dock,'',()=>this.journal(this.data.playerGuidance?'tasks':'observations'));this.objective.className='ga-objective';this.quickAction=this.button(this.dock,'',()=>this.openRecommended());this.quickAction.className='ga-next-action';this.quickAction.hidden=true;this.quickAction.title='Выполнить ближайший доступный шаг · E';this.previousRoom=null;this.hudPanel=null;const uid='ga-hud-'+(UI.serial=(UI.serial||0)+1);this.left.id=uid+'-objects';this.right.id=uid+'-routes';this.objectsButton=this.button(this.dock,'Объекты',()=>this.toggleHUD('objects'));this.objectsButton.setAttribute('aria-controls',this.left.id);this.objectsButton.title='Объекты в комнате · H';this.button(this.dock,'Журнал',()=>this.journal()).title='Журнал и инвентарь · I / J';this.button(this.dock,'Схема',()=>this.map()).title='Схема станции · M';this.fieldbar=el('div',undefined,'ga-fieldbar');this.introTip=el('span','Мышь — осмотр комнаты. Q — показать предметы. E — действие или переход.','ga-intro-tip');this.dock.append(this.introTip);this.hasScanned=false;
 this.fieldbar.append(this.dock,this.right);this.root.append(this.hotspots,this.exits,this.left,this.variant,this.notice,this.ambientLine,this.fieldbar);document.body.append(this.root);this.pendingLines=[];this.engine=new api.Engine(data,{line:l=>this.pendingLines.push(l),change:()=>{this.render();hooks.change?.();},death:n=>{this.death=n;},progress:()=>hooks.progress?.()});this.last=performance.now();this.timer=setInterval(()=>this.tick(),150);this.onKey=e=>{if(this.root.hidden||!this.active())return;if(e.key==='Escape'&&!this.dialog&&this.hudPanel){e.preventDefault();e.stopImmediatePropagation();this.toggleHUD(this.hudPanel);return;}if(!this.dialog&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!e.repeat&&!e.target.closest?.('input,textarea,select,[contenteditable=true]')){const digit=/^Digit([1-9])$/.exec(e.code||'');if(digit){const target=this.right.querySelector('[data-route-key="'+digit[1]+'"]');if(target){e.preventDefault();e.stopImmediatePropagation();target.click();}return;}const key=e.code||e.key,run={KeyI:()=>this.journal(),KeyJ:()=>this.journal(),KeyM:()=>this.map(),KeyH:()=>this.toggleHUD('objects'),KeyR:()=>this.focusExits(),KeyE:()=>this.openRecommended(),KeyQ:()=>this.scanScene(),Backspace:()=>this.goPrevious()}[key];if(run){e.preventDefault();e.stopImmediatePropagation();run();return;}}if(e.key==='Escape'&&this.dialog){e.preventDefault();e.stopImmediatePropagation();this.close();}else if(e.key==='Tab'&&this.dialog){const nodes=[...this.box.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),summary,[tabindex="0"]')].filter(n=>n.getClientRects().length);const first=nodes[0],last=nodes.at(-1);if(!first){e.preventDefault();this.box.focus();}else if(!this.box.contains(document.activeElement)){e.preventDefault();(e.shiftKey?last:first).focus();}else if(e.shiftKey&&(document.activeElement===first||document.activeElement===this.box)){e.preventDefault();last.focus();}else if(!e.shiftKey&&(document.activeElement===last||document.activeElement===this.box)){e.preventDefault();first.focus();}}};window.addEventListener('keydown',this.onKey,true);this.onLayout=()=>this.physicalPaint?.();window.addEventListener('resize',this.onLayout);}
 destroy(){clearTimeout(this.scanTimer);clearTimeout(this.ambientTimer);clearTimeout(this.noticeTimer);this.stopVoice?.();clearInterval(this.timer);this.disposeMedia?.();window.removeEventListener('keydown',this.onKey,true);window.removeEventListener('resize',this.onLayout);this.root.remove();}
 active(){return !this.hooks.paused?.();}
 reset(){this.hasScanned=false;this.previousRoom=null;this.hudPanel=null;this.clearNotice();this.clearAmbient?.();if(typeof clearTimeout==='function')clearTimeout(this.scanTimer);this.root.classList?.remove('ga-scanning');this.lastAmbientRoom=null;this.journalSection=null;this.journalQueries={};this.voicedEndings=new Set();this.endingShown=false;this.pendingLines=[];this.death=null;this.close(false);this.engine.reset();this.engine.start();this.root.hidden=false;this.render();}
 load(s){const validated=this.engine.normalize(s);this.hasScanned=false;this.previousRoom=null;this.hudPanel=null;this.clearNotice();this.clearAmbient?.();if(typeof clearTimeout==='function')clearTimeout(this.scanTimer);this.root.classList?.remove('ga-scanning');this.lastAmbientRoom=null;this.journalSection=null;this.journalQueries={};this.voicedEndings=new Set(validated.ended?[validated.ended]:[]);this.endingShown=false;this.pendingLines=[];this.death=null;this.close(false);this.engine.load(validated);this.root.hidden=false;this.sync();}
 snapshot(){return this.engine.export();}
 sync(){this.hooks.variant?.(this.engine.state.room,this.engine.state.variants[this.engine.state.room]);if(this.engine.state.room!==this.hooks.room?.())this.hooks.go?.(this.engine.state.room);this.render();}
 tick(){const now=performance.now(),dt=Math.min(1,(now-this.last)/1000);this.last=now;if(this.root.hidden)return;this.root.style.visibility=this.active()?'visible':'hidden';this.voice?.setPaused(!this.active());this.syncVoiceVolume();if(!this.active())return;if(!this.dialog&&this.ambientRemaining>0){
 this.ambientRemaining-=dt;
 if(this.ambientRemaining<=0){
  const next=(this.ambientQueue||[]).shift();
  this.clearAmbient(false);
  if(next&&(!next.room||next.room===this.engine.state.room))this.showAmbient(next);
 }
}if(this.mediaTick)this.mediaTick(dt);if(this.endingTick)this.endingTick(dt);if(this.dialog){this.engine.flush(dt);return;}if(this.hooks.staging?.())return;const ev=this.engine.flush(dt);if(ev)this.scene(ev);else if(this.engine.state.ended&&!this.endingShown)this.ending();}
 button(parent,label,fn,disabled=false){const b=el('button',label);b.type='button';b.disabled=disabled;b.onclick=fn;parent.append(b);return b;}
 scanScene(){
  if(this.dialog||!this.active()||this.engine.state.ended)return false;
  this.hasScanned=true;this.updateHUD();
  // An inspection must always give a usable result, even without visible markers
  // in a heavily staged panorama or in a room with no authored sign object.
  this.hudPanel='objects';this.updateHUD();
  clearTimeout(this.scanTimer);this.root.classList.add('ga-scanning');
  const available=this.engine.actions();
  const target=this.guide()?.action;
  if(target?.room===this.engine.state.room&&this.engine.eligible(target))
   this.hooks.focusAction?.(target.id);
  if(!available.length)this.notify('Здесь пока нечего исследовать. Проверьте соседние помещения и журнал задач.');
  this.scanTimer=setTimeout(()=>this.root.classList.remove('ga-scanning'),5200);
  return true;
 }
 render(){if(!this.engine)return;const s=this.engine.state;if(this.lastAmbientRoom!==s.room){this.clearAmbient();this.lastAmbientRoom=s.room;}this.left.replaceChildren();this.right.replaceChildren();const quest=this.data.quests.find(q=>q.chapter===s.chapter),guide=this.guide();this.button(this.left,'Свернуть',()=>this.toggleHUD('objects')).className='ga-panel-close';this.button(this.left,'Показать метки в панораме · Q',()=>this.scanScene()).className='ga-scan-control';this.left.append(el('h3','ОСМОТРЕТЬ КОМНАТУ'),el('h2',this.data.rooms.find(r=>r.id===s.room)?.name||''));
 const available=this.engine.actions();for(const a of available){const b=this.button(this.left,a.label,()=>this.openAction(a.id));b.dataset.actionId=a.id;if(a.id===guide?.action?.id)b.classList.add('ga-recommended');}
 if(!available.length)this.left.append(el('p','Осмотрите соседние помещения.','ga-muted'));
 const pending=this.data.actions.filter(a=>a.room===s.room&&a.when?.min===s.chapter&&!s.done.includes(a.id)&&!available.includes(a));
 if(pending.length){
  const group=el('details',undefined,'ga-unavailable');
  group.append(el('summary','Ещё недоступно · '+pending.length));
  for(const a of pending.slice(0,6)){
   const item=el('div',undefined,'ga-unavailable-item');
   item.append(el('strong',a.label));
   const req=this.requirementHints(a.when).join('; ')||'Продолжите расследование.';
   item.append(el('p',req,'ga-muted'));group.append(item);
  }
  this.left.append(group);
 }
 const links=this.data.links.filter(l=>l.from===s.room);if(links.length)this.right.append(el('p','ВЫХОДЫ · КЛИК ИЛИ 1–9','ga-route-heading'));
 for(const [index,l] of links.entries()){
  const name=this.data.rooms.find(r=>r.id===l.to)?.name,enabled=api.test(l.when,s)&&!s.ended;
  const returning=l.to===this.previousRoom;const b=this.button(this.right,(returning?'← ':'→ ')+name,()=>this.enterRoom(l.to));b.className='ga-route'+(returning?' ga-return':'');b.dataset.routeTo=l.to;b.setAttribute('aria-label','→ '+name);
  if(index<9){b.dataset.routeKey=String(index+1);const key=el('kbd',String(index+1));key.setAttribute('aria-hidden','true');b.append(key);}
  b.disabled=!enabled;b.setAttribute('aria-disabled',String(!enabled));if(!enabled){const lock=el('span','Закрыто','ga-route-lock');lock.setAttribute('aria-hidden','true');b.append(lock);b.title=l.locked||'Переход пока закрыт';b.setAttribute('aria-description',b.title);}
  else if(l.to===guide?.route?.[0]){b.classList.add('ga-recommended');b.title='Путь к текущей цели';}else if(returning){b.title='Вернуться в '+name+' · Backspace';b.setAttribute('aria-keyshortcuts','Backspace');}
 }
 const room=this.data.rooms.find(r=>r.id===s.room),authored=room?.variantAssets?.[s.variants[s.room]]||(room?.approvedBaseArt&&s.variants[s.room]===room.default_variant);this.updateHUD();// Technical variant IDs and missing-art warnings belong in editor diagnostics, not the horror HUD.
 this.variant.textContent='';this.variant.hidden=true;
 }
 guidanceRoute(target){
  const s=this.engine.state;if(s.room===target)return [];
  const queue=[[s.room,[]]],seen=new Set();
  while(queue.length){const[room,path]=queue.shift();if(room===target)return path;if(seen.has(room))continue;seen.add(room);for(const link of this.data.links.filter(l=>l.from===room&&api.test(l.when,s)))queue.push([link.to,[...path,link.to]]);}
  return null;
 }
 guide(entry=null){
  const s=this.engine.state;if(s.ended&&!entry)return null;
  const quest=this.data.quests.find(q=>q.chapter===s.chapter);entry=entry||this.data.playerGuidance?.quests?.[quest?.id];if(!entry)return null;
  const steps=entry.steps.filter(step=>api.test(step.when,s)),done=step=>step.complete?api.test(step.complete,s):s.done.includes(step.action);
  // A task can be temporarily locked while another step in this chapter is playable.
  // Prefer a reachable, available task in the current room, then one along an open route.
  // Never unlock or auto-complete an action: this only selects player-facing guidance.
  const unfinished=steps.filter(step=>!done(step));
  const candidates=unfinished.map(step=>({step,action:this.data.actions.find(a=>a.id===step.action)}))
   .filter(v=>v.action&&!s.ended&&api.test(v.action.when,s)&&(!v.action.once||!s.done.includes(v.action.id)))
   .map(v=>({...v,route:this.guidanceRoute(v.action.room)}))
   .filter(v=>v.route!==null);
  const chosen=candidates.find(v=>v.action.room===s.room)||candidates[0];
  const step=chosen?.step||unfinished[0],action=step&&this.data.actions.find(a=>a.id===step.action);
  return {entry,quest,steps,completed:steps.filter(done),step,action,route:action?this.guidanceRoute(action.room):null};
 }
 guideArt(action){if(!action)return null;const props=this.data.illustratedProps,pickup=action.effects?.find(x=>x.item)?.item;return this.data.inventoryArt?.[pickup]||props?.image?.[props?.action?.[action.id]];}
 guideDocument(id){const doc=this.data.documents.find(d=>d.id===id);if(!doc||!this.engine.state.documents.includes(id))return;const b=this.panel(this.documentTitle(doc));this.documentView(b,doc);this.button(b,'К задачам',()=>this.journal('tasks'));}
 openRecommended(){
  if(this.dialog||!this.active()||this.engine?.state.ended)return false;
  const guide=this.guide(),action=guide?.action,s=this.engine.state;
  if(action?.room===s.room&&this.engine.eligible(action)){this.openAction(action.id);return true;}
  // Move only to the next adjacent room through the existing locked-door rules.
  if(guide?.route?.length)return this.enterRoom(guide.route[0]);
  // If authored guidance is blocked, the player can still investigate locally
  // instead of pressing a button that apparently does nothing.
  const local=this.engine.actions()[0];
  if(local){this.openAction(local.id);return true;}
  if(action?.room===s.room){this.notify('Сначала подготовьте оборудование или прочитайте найденные материалы. Подробности — в журнале.');return false;}
  this.notify('Здесь нет доступных действий. Проверьте соседние помещения или журнал задач.');
  return false;
 }
 guideObjects(target=null){this.close();if(this.dialog)return;if(this.hudPanel!=='objects')this.toggleHUD('objects');const id=target||this.guide()?.action?.id;[...this.left.querySelectorAll('[data-action-id]')].find(n=>n.dataset.actionId===id)?.focus();}
 taskCard(parent,guide){
  if(!guide)return;const s=this.engine.state,{entry,steps,completed,step,action,route}=guide;
  if(!step){parent.append(el('p','План обхода выполнен. Закройте журнал и дождитесь завершения наблюдения.','ga-muted'));return;}
  const card=el('article',undefined,'ga-task-current');card.setAttribute('aria-label','Текущий шаг');card.dataset.actionId=action.id;const src=this.guideArt(action);
  if(src){const img=el('img');img.className='ga-task-thumb';img.alt='';img.src=src;img.loading='lazy';img.decoding='async';card.append(img);}
  const body=el('div');body.append(el('p','Сейчас · '+(completed.length+1)+' / '+steps.length,'ga-task-eyebrow'),el('h3',step.text));const roomName=id=>this.data.rooms.find(r=>r.id===id)?.name||'';
  body.append(el('p',s.room===action.room?'Вы на месте · '+roomName(action.room):'Куда идти: '+roomName(action.room),'ga-task-route'));
  if(route?.length)body.append(el('p','Путь: '+[s.room,...route].map(roomName).join(' → '),'ga-task-route'));
  else if(route===null)body.append(el('p','Прямой путь пока закрыт. Сначала завершите доступное взаимодействие в текущем помещении.','ga-task-route'));
  card.append(body);parent.append(card);const controls=el('div',undefined,'ga-task-controls');
  const here=s.room===action.room,ready=here&&this.engine.eligible(action),waiting=here&&!ready;
  this.button(controls,ready?'Осмотреть / выполнить сейчас':waiting?'Вернуться к осмотру':'Показать путь на схеме',
   ()=>{if(ready){this.close();this.openAction(action.id);}else if(waiting)this.close();else this.map(action.room);},
   !here&&route===null);
  if(ready&&this.hooks.canFocusAction?.(action.id)){
   this.button(controls,'Показать предмет в комнате',()=>{
    this.close();
    if(!this.hooks.focusAction?.(action.id))this.guideObjects(action.id);
   });
  }
  parent.append(controls);
  if(step.hint){const help=el('details',undefined,'ga-task-hint');help.append(el('summary','Нужна подсказка'),el('p',step.hint));for(const id of step.references||[]){if(!s.documents.includes(id))continue;const doc=this.data.documents.find(d=>d.id===id);if(doc)this.button(help,'Прочитать: '+this.documentTitle(doc),()=>this.guideDocument(id));}parent.append(help);}
  if(completed.length){const history=el('details',undefined,'ga-task-history');history.append(el('summary','Сделано в этой задаче · '+completed.length));const list=el('ol');for(const previous of completed)list.append(el('li',previous.text));history.append(list);parent.append(history);}
 }
 taskJournal(parent){
  const s=this.engine.state,current=this.guide(),quest=this.data.quests.find(q=>q.chapter===s.chapter);
  parent.append(el('p',s.ended?'СМЕНА ЗАВЕРШЕНА':'ОСНОВНАЯ ЗАДАЧА','ga-task-eyebrow'),el('h3',s.ended?'Журнал завершённой смены':quest?.title||'Обход станции','ga-task-heading'));
  if(current){parent.append(el('p',current.entry.brief,'ga-task-brief'));this.taskCard(parent,current);}
  else parent.append(el('p',s.ended?'Найденные документы и записи сохранены в разделах журнала.':'Осмотрите доступные объекты в помещении.','ga-muted'));
  for(const branch of this.data.playerGuidance?.branches||[]){if(!api.test(branch.when,s))continue;const box=el('section',undefined,'ga-task-branch');box.setAttribute('aria-label',branch.title);box.append(el('p',branch.kind,'ga-task-eyebrow'),el('h3',branch.title));
   if(api.test(branch.complete,s)){box.append(el('p',branch.completionText||'Задача выполнена.','ga-task-brief'));if(s.documents.includes(branch.completionDocument))this.button(box,branch.completionLabel||'Открыть документ',()=>this.guideDocument(branch.completionDocument));}
   else if(s.ended)box.append(el('p','Эта задача не завершена в прошедшей смене.','ga-muted'));
   else{box.append(el('p',branch.brief,'ga-task-brief'));this.taskCard(box,this.guide(branch));}parent.append(box);
  }
  const previous=this.data.quests.filter(q=>s.flags[q.id+'_DONE']);if(previous.length){const history=el('details',undefined,'ga-task-history');history.append(el('summary','Завершённые задачи · '+previous.length));const list=el('ol');for(const q of previous)list.append(el('li',q.title));history.append(list);parent.append(history);}
 }
 inspection(id){const a=this.data.actions.find(a=>a.id===id),meta=this.data.illustratedProps?.inspections?.[id];if(!a||!meta)return;const b=this.panel(a.label+' · крупный план');b.classList.add('ga-art-view');this.showArt(b,this.data.illustratedProps.image[meta.image],meta.alt);this.button(b,'К прибору',()=>this.openAction(id));}
 inspectionPreview(parent,a,src,meta){const figure=el('figure',undefined,'ga-inspection'),zoom=this.button(figure,'',()=>this.inspection(a.id));zoom.setAttribute('aria-label','Рассмотреть: '+meta.alt);const img=el('img');img.src=src;img.alt=meta.alt;img.decoding='async';zoom.append(img);const caption=el('figcaption',meta.alt);caption.append(el('span','Нажмите на изображение, чтобы рассмотреть.'));figure.append(caption);parent.append(figure);}
 enterRoom(id){
  if(this.dialog||!this.active()||this.travelling||this.engine.state.ended)return false;
  const link=this.data.links.find(l=>l.from===this.engine.state.room&&l.to===id);if(!link)return false;
  if(!api.test(link.when,this.engine.state)){this.notify(link.locked||'Переход пока закрыт.');return false;}
  this.travelling=true;try{const from=this.engine.state.room;if(!this.engine.enter(id))return false;this.previousRoom=from;this.hudPanel=null;this.sync();return true;}finally{this.travelling=false;}
 }
 goPrevious(){
  const room=this.previousRoom,s=this.engine.state;
  if(!room||!this.data.links.some(l=>l.from===s.room&&l.to===room&&api.test(l.when,s)))return false;
  return this.enterRoom(room);
 }
 focusExits(){this.hudPanel=null;this.updateHUD();(this.right.querySelector('.ga-recommended')||this.right.querySelector('[aria-disabled="false"]'))?.focus();}
 toggleHUD(panel){if(panel==='routes'){this.focusExits();return;}this.hudPanel=this.hudPanel===panel?null:panel;this.updateHUD();if(this.hudPanel)(this.left.querySelector('[data-action-id]')||this.left.querySelector('button:not(:disabled):not(.ga-panel-close)'))?.focus();else this.objectsButton?.focus();}
 updateHUD(){if(!this.dock)return;const modal=!!this.dialog;
 if(this.introTip)this.introTip.hidden=modal||this.hasScanned||!this.active()||this.engine.state.chapter!==1||this.engine.state.done.includes('take_BADGE04');this.fieldbar.hidden=modal;this.dock.hidden=modal;this.left.hidden=modal||this.hudPanel!=='objects';this.right.hidden=modal||!!this.engine?.state.ended;this.exits.hidden=modal||!this.active();this.objectsButton.setAttribute('aria-expanded',String(!this.left.hidden));const count=this.engine?.actions().length??0;this.objectsButton.textContent='Объекты · '+count;
 const guide=this.guide(),target=guide?.action,ready=!!target&&target.room===this.engine.state.room&&this.engine.eligible(target);
 const nextRoom=guide?.route?.[0],canMove=!!nextRoom&&this.data.links.some(l=>l.from===this.engine.state.room&&l.to===nextRoom&&api.test(l.when,this.engine.state));
 const otherAction=!ready&&!canMove?this.engine.actions()[0]:null;
 this.quickAction.hidden=modal||!(ready||canMove||otherAction)||!this.active();
 if(ready){this.quickAction.textContent='Осмотреть: '+target.label;this.quickAction.dataset.actionId=target.id;this.quickAction.title=target.label+' · E';}
 else if(canMove){const name=this.data.rooms.find(r=>r.id===nextRoom)?.name||'соседнее помещение';this.quickAction.removeAttribute('data-action-id');this.quickAction.textContent='Идти: '+name;this.quickAction.title='Перейти в '+name+' · E';}
 else if(otherAction){this.quickAction.dataset.actionId=otherAction.id;this.quickAction.textContent='Исследовать: '+otherAction.label;this.quickAction.title=otherAction.label+' · E';}
 else this.quickAction.removeAttribute('data-action-id');
 const title=this.data.quests.find(q=>q.chapter===this.engine?.state.chapter)?.title;const next=this.guide()?.step?.text;this.objective.textContent=this.engine?.state.ended?'Смена завершена · журнал':next||title||'Станция «Маяк-9»';this.objective.title=(title||'Журнал смены')+' · открыть задачи';this.objective.setAttribute('aria-label','Текущая цель: '+this.objective.textContent+'. Открыть задачи');if(title)this.objectsButton.title=title+' · H';}
 itemName(id){const names={BADGE04:'Бейдж оператора 04',ARCHIVE_KEY:'Ключ архива',STORAGE_KEY:'Ключ кладовой',FUSE_3:'Предохранитель №3',VHS_V01:'Кассета V01',P17_SAMPLE:'Проба P-17',FLASHLIGHT:'Фонарь',ANTENNA_KEY:'Ключ антенны',BEACON:'Аварийный маячок',VHS_FRAGMENT_A:'Фрагмент плёнки А',VHS_FRAGMENT_B:'Фрагмент плёнки Б',PUNCHCARD_RU:'Русская перфокарта',PUNCHCARD_DE:'Немецкая перфокарта',VHS_V03:'Личная кассета Петра',SHUTTER_PIN:'Стопор створки'};if(names[id])return names[id];return this.data.actions.find(a=>a.effects?.some(e=>e.item===id))?.label||id;}
 documentTitle(doc){return this.data.actions.find(a=>a.template==='document'&&a.document===doc.id)?.label||doc.title;}
 documentView(parent,doc){
 if(!doc){parent.append(el('p','Документ недоступен.','ga-muted'));return;}
 const artId=this.data.illustratedProps?.document?.[doc.id],src=artId&&this.data.illustratedProps?.image?.[artId];
 if(src&&isImageSource(src)){
  const original=el('details',undefined,'ga-facsimile');original.open=false;original.append(el('summary','Оригинал документа'));const tools=el('div',undefined,'ga-reader-tools'),scroll=el('div',undefined,'ga-facsimile-scroll'),img=el('img');img.alt=this.documentTitle(doc);img.loading='eager';img.decoding='async';img.src=src;
  const zoom=this.button(tools,'Увеличить оригинал',()=>{const expanded=original.dataset.zoom!=='true';original.dataset.zoom=String(expanded);zoom.textContent=expanded?'По ширине окна':'Увеличить оригинал';zoom.setAttribute('aria-pressed',String(expanded));});zoom.setAttribute('aria-pressed','false');scroll.tabIndex=0;scroll.setAttribute('aria-label','Оригинал: прокрутка изображения');scroll.append(img);original.append(tools,scroll);img.onerror=()=>original.remove();parent.append(original);
 }
 const tools=el('div',undefined,'ga-reader-tools'),paper=el('pre',doc.text,'ga-reader-paper'),size=el('span');
 const update=()=>{this.readerSize=Math.max(16,Math.min(26,this.readerSize||18));paper.style.setProperty('--reader-size',this.readerSize+'px');size.textContent='Размер текста: '+this.readerSize;smaller.disabled=this.readerSize<=16;larger.disabled=this.readerSize>=26;};
 const smaller=this.button(tools,'А−',()=>{this.readerSize-=2;update();}),larger=this.button(tools,'А+',()=>{this.readerSize+=2;update();});smaller.setAttribute('aria-label','Уменьшить текст документа');larger.setAttribute('aria-label','Увеличить текст документа');tools.append(size);parent.append(tools,paper);update();
 }
 clearNotice(){clearTimeout(this.noticeTimer);if(this.notice){this.notice.hidden=true;this.notice.textContent='';}}
 clearAmbient(dropQueue=true){
 clearTimeout(this.ambientTimer);
 this.ambientRemaining=0;
 this.ambientCurrent=null;
 if(dropQueue)this.ambientQueue=[];
 if(this.ambientLine){this.ambientLine.hidden=true;this.ambientLine.replaceChildren();}
}
 showAmbient(e){
 if(!this.ambientLine)return;
 if(this.ambientRemaining>0&&!this.ambientLine.hidden){
  if(this.ambientCurrent===e.id||this.ambientQueue?.some(item=>item.id===e.id))return;
  // Keep a short readable sequence. Every observation remains in the journal.
  (this.ambientQueue||(this.ambientQueue=[])).push(e);
  if(this.ambientQueue.length>3)this.ambientQueue.shift();
  return;
 }
 this.clearAmbient(false);
 this.ambientCurrent=e.id;
 this.hooks.cue?.(e);
 const label=el('small',e.ambientLabel||'НАБЛЮДЕНИЕ'),line=el('p',e.presentation);
 this.ambientLine.append(label,line);
 this.ambientLine.hidden=false;
 this.ambientRemaining=Math.max(5,Math.min(9,e.presentation.length*.065));
}
 notify(text){this.clearNotice();if(!text)return;this.notice.textContent=text;this.notice.hidden=false;this.noticeTimer=setTimeout(()=>this.clearNotice(),5000);}
 requirementHints(c){
 if(!c||api.test(c,this.engine.state))return [];
 if(typeof c==='string'){const doc=this.data.documents.find(d=>'FOUND_'+d.id===c);if(doc)return ['Прочитать: '+this.documentTitle(doc)];const action=this.data.actions.find(a=>a.id===c)||this.data.actions.find(a=>a.effects?.some(fx=>fx.set?.[c]===true));return action?[action.label]:[];}
 if(Array.isArray(c))return [...new Set(c.flatMap(x=>this.requirementHints(x)))];
 const hints=[];if(c.item&&!this.engine.state.inventory.includes(c.item))hints.push('Нужен предмет: '+this.itemName(c.item));if(c.all)hints.push(...this.requirementHints(c.all));if(c.any&&!c.any.some(x=>api.test(x,this.engine.state))){const options=c.any.flatMap(x=>this.requirementHints(x));if(options.length)hints.push('Одно из действий: '+options.join(' / '));}return [...new Set(hints)];
 }
 itemActions(id){const needs=c=>!!c&&typeof c==='object'&&(Array.isArray(c)?c.some(needs):c.item===id||(c.all||[]).some(needs)||(c.any||[]).some(needs));return this.engine.actions().filter(a=>needs(a.when));}
 inspectItem(id){if(!this.engine.state.inventory.includes(id))return;const b=this.panel(this.itemName(id));this.showArt(b,this.data.inventoryArt?.[id],this.itemName(id));const actions=this.itemActions(id);b.append(el('p',actions.length?'Можно использовать здесь:':'Предмет при вас. Подходящее взаимодействие появится у нужного оборудования.','ga-inventory-note'));for(const a of actions)this.button(b,a.label,()=>this.openAction(a.id));this.button(b,'К журналу',()=>this.journal('items'));}

 panel(title){if(!this.dialog)this.focusOrigin=document.activeElement;this.close(false);this.hotspots.hidden=true;this.engine.modal=true;this.dialog=el('div',undefined,'ga-modal');this.box=el('section',undefined,'ga-dialog');this.box.setAttribute('role','dialog');this.box.setAttribute('aria-label',title);this.box.setAttribute('aria-modal','true');this.box.tabIndex=-1;const close=this.button(this.box,'×',()=>this.close());close.className='ga-dialog-close';close.setAttribute('aria-label','Закрыть окно');this.box.append(el('h2',title));this.dialog.append(this.box);this.root.append(this.dialog);this.updateHUD();this.box.focus();return this.box;}
 close(refresh=true){this.endingTick=null;this.physicalPaint=null;this.instrumentHint=null;this.attemptLabel=null;this.error=null;this.stopVoice?.();const resume=refresh?this.afterScene:null;this.afterScene=null;const sceneCue=refresh?this.pendingSceneCue:null;this.pendingSceneCue=null;this.disposeMedia?.();this.disposeMedia=null;this.mediaTick=null;this.dialog?.remove();this.dialog=null;this.engine?.cancel();if(refresh){this.sync();if(sceneCue)this.hooks.cue?.(sceneCue);if(this.engine.state.ended)this.endingShown=false;if(resume)resume();if(this.dialog)return;this.restoreFocus?.();}}
 restoreFocus(){this.hotspots.hidden=!this.active();this.updateHUD();const origin=this.focusOrigin;this.focusOrigin=null;if(!this.active())return;const id=origin?.dataset?.actionId,alive=!id||this.engine.actions().some(a=>a.id===id);const candidates=[alive&&origin?.isConnected?origin:null,...this.left.querySelectorAll('[data-action-id]'),this.objectsButton];const target=candidates.find(n=>n&&n.getClientRects().length&&(!n.dataset.actionId||!id||n.dataset.actionId===id))||this.objectsButton;target?.focus();}

 isAmbientEvent(e){
  return !!e.ambient||(
   ['normal','quiet','trace','sound','object'].includes(e.category)
   &&e.priority==='optional'&&!e.lines?.length&&!e.timelineId
   &&!e.sceneArt&&!e.visualCue?.panoramaVariant
  );
 }
 scene(e){
  // Simple optional station observations belong in the space, not a blocking modal.
  // Audio, dialogue, evidence, authored art and mandatory story scenes retain full presentation.
  this.hooks.variant?.(this.engine.state.room,this.engine.state.variants[this.engine.state.room]);
  if(typeof this.isAmbientEvent==='function'&&this.isAmbientEvent(e)){this.showAmbient(e);return;}
  this.clearAmbient?.();if(e.timelineId)this.hooks.timeline?.(e.timelineId);const b=this.panel(e.category==='normal'?'Станция · наблюдение':'Наблюдение');this.pendingSceneCue=e;b.setAttribute?.('data-event-id',e.id);const sceneArt=this.hooks.sceneArt?.(e);if(['normal','quiet','trace','sound','object','mirror','spatial','future','outdoor'].includes(e.category)&&!e.lines?.length&&!sceneArt&&!e.timelineId&&!e.visualCue?.mode)b.classList.add('ga-ambient-scene');if(sceneArt){if(e.visualCue?.mode!=='panorama')this.showArt(b,sceneArt,e.presentation);}b.append(el('div',e.presentation,'ga-scene'));for(const l of e.lines||[])b.append(el('div',l.speaker+'\n'+l.text,'ga-caption'));this.speakLines?.(e.lines);this.button(b,'Продолжить',()=>this.close());}
 map(target=null){
 const s=this.engine.state,b=this.panel('Схема помещений'),grid=el('div',undefined,'ga-map-grid'),names=Object.fromEntries(this.data.rooms.map(r=>[r.id,r.name]));
 const path=target?this.guidanceRoute(target):null;
 if(target&&names[target]){b.append(el('p','Цель: '+names[target],'ga-map-purpose'));if(path?.length)b.append(el('p','Путь: '+[s.room,...path].map(id=>names[id]).join(' → '),'ga-task-route'));}
 b.append(el('p','Выберите соседнее помещение. Закрытые переходы требуют подготовки.','ga-muted'),grid);
 for(const r of this.data.rooms){const card=el('section',undefined,'ga-map-room');card.append(el('h3',r.name));if(r.id===target){card.classList.add('ga-map-target');card.append(el('p','Текущая цель','ga-map-purpose'));}if(r.id===path?.[0]){card.classList.add('ga-map-next');card.append(el('p','Следующий переход по пути к цели','ga-map-purpose'));}
 if(r.id===s.room){card.setAttribute('aria-current','location');card.append(el('p','Вы здесь'));}else{const link=this.data.links.find(l=>l.from===s.room&&l.to===r.id);if(link){const enabled=api.test(link.when,s)&&!s.ended;this.button(card,'→ '+r.name,()=>{this.close();this.enterRoom(r.id);},!enabled);if(!enabled)card.append(el('p',link.locked||'Переход пока закрыт.'));}else card.append(el('p','Через соседние помещения'));}
 const destinations=this.data.links.filter(l=>l.from===r.id).map(l=>names[l.to]);if(destinations.length)card.append(el('p','Связи: '+destinations.join(' · ')));grid.append(card);}
 this.button(b,'Закрыть',()=>this.close());
 }
 evidenceReadyCases(state=this.engine.state){
  return (this.data.evidenceCases||[]).filter(c=>
   !state.flags['TV_CASE_'+c.id]&&c.fragments.length===2&&c.fragments.every(f=>!!state.flags[f.flag]));
 }
 linkEvidenceCase(id){
  const caseFile=(this.data.evidenceCases||[]).find(c=>c.id===id);
  const state=this.engine.state,key='TV_CASE_'+id;
  if(!caseFile||state.flags[key]||caseFile.fragments.length!==2||
   !caseFile.fragments.every(f=>!!state.flags[f.flag]))return false;
  state.flags[key]=true;
  state.journal.push({id:key,time:state.clock,text:'Сопоставление улик: '+caseFile.title+'. '+caseFile.deduction,lines:[]});
  this.engine.changed();
  this.journal('cases');
  return true;
 }
 evidenceJournal(parent){
  const cases=this.data.evidenceCases||[],state=this.engine.state;
  if(!cases.length){parent.append(el('p','Материалы для сопоставления пока не найдены.','ga-muted'));return;}
  const linked=cases.filter(c=>state.flags['TV_CASE_'+c.id]).length;
  const found=cases.reduce((n,c)=>n+c.fragments.filter(f=>state.flags[f.flag]).length,0);
  parent.append(el('p','МАТЕРИАЛЫ РАССЛЕДОВАНИЯ','ga-evidence-eyebrow'));
  parent.append(el('p','Фрагментов: '+found+' / '+(cases.length*2)+' · установлено связей: '+linked+' / '+cases.length,'ga-evidence-summary'));
  parent.append(el('p','Найдите следы в разных помещениях. Когда оба фрагмента доступны, выберите их и сопоставьте. Это дополнительное расследование: основные задания не зависят от него.','ga-evidence-explain'));
  const board=el('div',undefined,'ga-evidence-board');parent.append(board);
  for(const caseFile of cases){
   const solved=!!state.flags['TV_CASE_'+caseFile.id],
    available=caseFile.fragments.filter(f=>!!state.flags[f.flag]).length,
    ready=available===caseFile.fragments.length;
   const card=el('article',undefined,'ga-evidence-case');
   card.dataset.status=solved?'linked':ready?'ready':'incomplete';
   card.append(el('small',solved?'СОПОСТАВЛЕНО':ready?'МОЖНО СОПОСТАВИТЬ':'НЕПОЛНЫЕ ДАННЫЕ','ga-evidence-status'));
   card.append(el('h3',caseFile.title));
   const slips=el('div',undefined,'ga-evidence-slips');
   const selected=new Set();
   const controls=el('div',undefined,'ga-evidence-controls');
   const connect=this.button(controls,'Сопоставить два фрагмента',()=>this.linkEvidenceCase(caseFile.id),true);
   connect.className='ga-evidence-connect';
   for(const fragment of caseFile.fragments){
    const known=!!state.flags[fragment.flag],slip=this.button(slips,'',()=>{
     if(!known||solved)return;
     if(selected.has(fragment.flag))selected.delete(fragment.flag);
     else selected.add(fragment.flag);
     slip.setAttribute('aria-pressed',String(selected.has(fragment.flag)));
     connect.disabled=selected.size!==caseFile.fragments.length;
    },!known||solved);
    slip.className='ga-evidence-slip';
    slip.setAttribute('aria-pressed','false');
    slip.append(el('small',known?(this.data.rooms.find(r=>r.id===fragment.room)?.name||'Станция'):'Не исследовано'),
     el('strong',known?fragment.label:'???'),
     el('p',known?fragment.detail:'Поищите необычные детали в других помещениях.'));
    if(!known)slip.dataset.missing='true';
   }
   card.append(slips);
   if(solved){
    card.append(el('p',caseFile.deduction,'ga-evidence-conclusion'));
    card.append(el('small','Вывод сохранён в журнале. Станция может отозваться на него позднее.','ga-evidence-footnote'));
   }else if(ready)card.append(controls);
   else card.append(el('p','Осталось найти: '+(caseFile.fragments.length-available),'ga-evidence-footnote'));
   board.append(card);
  }
 }
 journal(section=this.journalSection||'items'){
 this.journalSection=section;const s=this.engine.state,b=this.panel('Журнал станции');if(section==='tasks')b.classList.add('ga-tasks');
 const cases=this.data.evidenceCases||[],caseReady=this.evidenceReadyCases(s).length,caseLinked=cases.filter(c=>s.flags['TV_CASE_'+c.id]).length;
 const sections=[...(this.data.playerGuidance?[['tasks','Задачи',null]]:[]),...(cases.length?[['cases','Улики',caseReady?caseReady+' новые':caseLinked+'/'+cases.length]]:[]),['items','Предметы',s.inventory.length],['documents','Документы',s.documents.length],['recordings','Записи',this.data.media.filter(m=>s.flags['WATCHED_'+m.id]||s.flags['HEARD_'+m.id]).length],['observations','Наблюдения',s.journal.length]];
 const nav=el('div',undefined,'ga-journal-nav');nav.setAttribute('aria-label','Разделы журнала');for(const [key,label,count]of sections){const button=this.button(nav,count===null?label:label+' · '+count,()=>this.journal(key));button.setAttribute('aria-pressed',String(key===section));}b.append(nav);
 const label=el('label','Поиск в разделе','ga-journal-search'),search=el('input');search.type='search';search.placeholder='Слово, название или фраза';search.value=this.journalQueries?.[section]||'';label.append(search);b.append(label);
 const count=el('p',undefined,'ga-muted'),content=el('div',undefined,'ga-journal-list');count.setAttribute('role','status');count.setAttribute('aria-live','polite');b.append(count,content);label.hidden=section==='tasks'||section==='cases';count.hidden=section==='tasks'||section==='cases';
 const paint=()=>{(this.journalQueries||(this.journalQueries={}))[section]=search.value;const query=search.value.trim().toLocaleLowerCase('ru'),matches=text=>!query||String(text).toLocaleLowerCase('ru').includes(query);content.replaceChildren();let shown=0;
 if(section==='tasks'){this.taskJournal(content);return;}
 if(section==='cases'){this.evidenceJournal(content);return;}
 if(section==='items'){const grid=el('div',undefined,'ga-inventory');content.append(grid);for(const id of s.inventory){if(!matches(this.itemName(id)))continue;shown++;const card=this.button(grid,'',()=>this.inspectItem(id));card.className='ga-item';const src=this.data.inventoryArt?.[id];if(src){const img=el('img');img.src=src;img.alt='';img.loading='lazy';img.decoding='async';card.append(img);}card.append(el('span',this.itemName(id)));if(this.itemActions(id).length)card.append(el('span','Можно использовать здесь','ga-muted'));}}
 else if(section==='documents'){for(const id of s.documents){const d=this.data.documents.find(d=>d.id===id);if(!d||!matches(d.title+' '+d.text))continue;shown++;this.button(content,this.documentTitle(d),()=>{const box=this.panel(this.documentTitle(d));this.documentView(box,d);this.button(box,'К журналу',()=>this.journal('documents'));});}}
 else if(section==='recordings'){for(const m of this.data.media.filter(m=>s.flags['WATCHED_'+m.id]||s.flags['HEARD_'+m.id])){if(!matches(m.id+' '+m.title+' '+(m.transcript?.length?m.transcript:(m.frames||[])).map(l=>l.text).join(' ')))continue;shown++;this.button(content,m.id+' · '+m.title,()=>this.playMedia(m,null));}}
 else{for(const entry of [...s.journal].reverse()){if(!matches(entry.text+' '+(entry.lines||[]).map(l=>l.speaker+' '+l.text).join(' ')))continue;shown++;const card=el('article',undefined,'ga-journal-entry');card.append(el('p',entry.text));for(const l of entry.lines||[])card.append(el('div',l.speaker+'\n'+l.text,'ga-caption'));content.append(card);}const completed=this.data.quests.filter(q=>s.flags[q.id+'_DONE']&&matches(q.title));if(completed.length){content.append(el('h3','ВЫПОЛНЕННЫЕ ЗАДАЧИ'));for(const q of completed)content.append(el('p','✓ '+q.title));shown+=completed.length;}}
 count.textContent=shown?'Найдено: '+shown:query?'Совпадений нет.':section==='items'?'Пока нет предметов.':'В этом разделе пока нет записей.';
 };search.oninput=paint;paint();this.button(b,'Закрыть',()=>this.close());
 }

 instrumentAttempts(a){if(!this.attemptLabel)return;const errors=this.engine.state.errors[a.id]||0;this.attemptLabel.textContent=a.deathAfter?'Опасный прибор · ошибок до возврата к контрольной точке: '+(a.deathAfter-errors%a.deathAfter):errors?'Ошибок при настройке: '+errors:'Промежуточная настройка сохраняется.';}
 instrumentReferences(parent,a){const ids=new Set([...(a.hint||'').matchAll(/\bD\d{2}\b/g)].map(m=>m[0]));for(const m of JSON.stringify(a.when||{}).matchAll(/FOUND_(D\d{2})/g))ids.add(m[1]);for(const id of ids){if(!this.engine.state.documents.includes(id))continue;const doc=this.data.documents.find(d=>d.id===id);if(!doc)continue;const details=el('details',undefined,'ga-reference');details.append(el('summary','Свериться с документом: '+this.documentTitle(doc)));this.documentView(details,doc);parent.append(details);}}
 sequenceControl(parent,a){
  let selected=this.engine.actionInput(a.id);
  const tactile=['TEA_SEQUENCE','PLUMB_SEQ','COOKING','VHS_ASSEMBLE'].includes(a.id);
  const host=tactile?el('section',undefined,'ga-sequence-machine ga-sequence-'+a.id.toLowerCase()):parent;
  if(tactile){
   host.append(el('p','Выполняйте действия непосредственно с предметами. Порядок важен.','ga-sequence-instruction'));
   parent.append(host);
  }
  const status=el('div',undefined,'ga-muted ga-sequence-status');
  status.setAttribute('role','status');
  status.setAttribute('aria-live','polite');
  const slots=el('ol',undefined,'ga-sequence');
  host.append(status,slots);
  const row=el('div',undefined,'ga-row'+(tactile?' ga-sequence-props':''));
  if(tactile)row.setAttribute('role','group');
  host.append(row);
  const tokens=[];
  const tools=el('div',undefined,'ga-row ga-sequence-tools');
  host.append(tools);
  const undo=this.button(tools,'Отменить шаг',()=>{
   selected.pop();
   this.engine.actionInput(a.id,selected);
   paint();
  });
  this.button(tools,'Начать заново',()=>{
   selected=[];
   this.engine.actionInput(a.id,selected);
   paint();
   if(this.error)this.error.textContent='';
  });
  const paint=()=>{
   slots.replaceChildren();
   for(let i=0;i<a.answer.length;i++){
    const slot=el('li');
    slot.dataset.filled=String(i<selected.length);
    slot.append(el('small','ШАГ '+(i+1)),el('span',selected[i]??'—'));
    slots.append(slot);
   }
   status.textContent='Порядок действий · '+selected.length+' / '+a.answer.length;
   undo.disabled=!selected.length;
   for(const [i,b]of tokens){
    const consumed=selected.filter(v=>String(v)===String(a.buttons[i])).length;
    b.dataset.used=consumed>0?'true':'false';
    b.setAttribute('aria-pressed',String(consumed>0));
   }
  };
  for(const [i,token]of a.buttons.entries()){
   const b=this.button(row,token,()=>{
    selected.push(token);
    if(String(selected.at(-1))!==String(a.answer[selected.length-1])){
     const result=this.submit(a,selected,true);
     if(result?.death)return;
     selected=[];
     this.engine.actionInput(a.id,selected);
     paint();
    }else if(selected.length===a.answer.length){
     this.submit(a,selected);
    }else{
     this.engine.actionInput(a.id,selected);
     paint();
    }
   });
   if(tactile){
    b.classList.add('ga-sequence-prop');
    b.dataset.propIndex=String(i);
    b.title='Использовать: '+token;
   }
   tokens.push([i,b]);
  }
  paint();
 }
 hardwareInstrument(parent,a,fields,grid){
  const host=el('section',undefined,'ga-hardware ga-device-'+a.id.toLowerCase());
  const heading=el('header',undefined,'ga-hardware-heading');
  heading.append(el('span','МОДУЛЬ УПРАВЛЕНИЯ','ga-hardware-kicker'),el('strong',a.label));
  const board=el('div',undefined,'ga-hardware-board'),status=el('p','Регулируйте органы управления. Затем проверьте результат.','ga-hardware-status');
  status.setAttribute('role','status');
  host.append(heading,board,status);
  parent.insertBefore(host,grid);
  const precise=el('details',undefined,'ga-reference ga-hardware-precise');
  precise.append(el('summary','Точное управление и ввод с клавиатуры'));
  parent.insertBefore(precise,grid);
  precise.append(grid);
  const set=(i,value)=>{
   const node=fields[i];
   node.value=String(value);
   node.dispatchEvent(new Event(node.tagName==='SELECT'?'change':'input',{bubbles:true}));
  };
  const controls=[];
  for(const [i,f] of a.fields.entries()){
   const card=el('section',undefined,'ga-hardware-control');
   card.append(el('p',f.label,'ga-hardware-control-title'));
   if(f.options){
    const variants=el('div',undefined,'ga-hardware-switches'),buttons=[];
    if(f.options.length<=7){
     for(const choice of f.options){
      const b=this.button(variants,String(choice),()=>set(i,choice));
      b.className='ga-hardware-switch';
      b.setAttribute('aria-label',f.label+': '+choice);
      buttons.push([b,choice]);
     }
    }else{
     const cycle=this.button(variants,'Переключить',()=>{
      const index=f.options.indexOf(fields[i].value);
      set(i,f.options[(index+1)%f.options.length]);
     });
     cycle.className='ga-hardware-switch ga-hardware-cycle';
     buttons.push([cycle,null]);
    }
    card.append(variants);
    controls.push(()=>{
     for(const [b,v]of buttons){
      const picked=v!==null&&String(fields[i].value)===String(v);
      b.setAttribute('aria-pressed',String(picked));
      if(v===null)b.textContent=fields[i].value||'Выбрать режим';
     }
    });
   }else{
    const min=Number.isFinite(Number(f.min))?Number(f.min):0;
    const max=Number.isFinite(Number(f.max))?Number(f.max):100;
    const step=Number(f.step)>0?Number(f.step):1;
    const adjust=delta=>{
     const current=fields[i].value===''?min:Number(fields[i].value);
     const rounded=min+Math.round((current+delta*step-min)/step)*step;
     const value=Math.min(max,Math.max(min,Number(rounded.toFixed(6))));
     set(i,value);
    };
    const face=el('div',undefined,'ga-hardware-gauge');
    const knob=el('button',undefined,'ga-hardware-knob');
    knob.type='button';
    knob.setAttribute('role','slider');
    knob.setAttribute('aria-label',f.label+' — поворотная рукоять');
    knob.setAttribute('aria-valuemin',String(min));
    knob.setAttribute('aria-valuemax',String(max));
    const number=el('output',undefined,'ga-hardware-number');
    knob.append(number);
    let dragging=null;
    knob.onpointerdown=e=>{
     if(e.pointerType==='mouse'&&e.button!==0)return;
     dragging={id:e.pointerId,x:e.clientX,value:fields[i].value!==''?Number(fields[i].value):min,moved:false};
     knob.setPointerCapture(e.pointerId);
    };
    knob.onpointermove=e=>{
     if(!dragging||e.pointerId!==dragging.id)return;
     const dx=e.clientX-dragging.x;
     if(Math.abs(dx)>=4){
      dragging.moved=true;
      const units=Math.round(dx/15);
      const target=dragging.value+units*step;
      set(i,Math.max(min,Math.min(max,Number((min+Math.round((target-min)/step)*step).toFixed(6)))));
     }
    };
    knob.onpointerup=e=>{
     if(!dragging||e.pointerId!==dragging.id)return;
     if(!dragging.moved)adjust(1);
     dragging=null;
    };
    knob.onpointercancel=()=>{dragging=null;};
    knob.onkeydown=e=>{
     const delta={'ArrowLeft':-1,'ArrowDown':-1,'ArrowRight':1,'ArrowUp':1}[e.key];
     if(delta){e.preventDefault();e.stopPropagation();adjust(delta);}
    };
    const track=el('div',undefined,'ga-hardware-track');
    track.append(el('span',undefined,'ga-hardware-fill'));
    const row=el('div',undefined,'ga-hardware-adjust');
    const less=this.button(row,'−',()=>adjust(-1));
    less.setAttribute('aria-label','Уменьшить '+f.label);
    const range=el('input');range.type='range';range.min=String(min);range.max=String(max);range.step=String(step);
    range.setAttribute('aria-label',f.label+' — ползунок');
    range.oninput=()=>set(i,range.value);
    row.append(range);
    const more=this.button(row,'+',()=>adjust(1));
    more.setAttribute('aria-label','Увеличить '+f.label);
    face.append(knob,track);
    card.append(face,row);
    controls.push(()=>{
     const current=fields[i].value;
     const val=current===''?NaN:Number(current);
     const ratio=Number.isFinite(val)&&max>min?Math.max(0,Math.min(1,(val-min)/(max-min))):0;
     number.textContent=current===''?'—':current;
     knob.style.setProperty('--angle',(-130+ratio*260).toFixed(1)+'deg');
     knob.setAttribute('aria-valuenow',Number.isFinite(val)?String(val):String(min));
     face.style.setProperty('--level',(ratio*100).toFixed(2)+'%');
     range.value=Number.isFinite(val)?String(val):String(min);
     less.disabled=Number.isFinite(val)&&val<=min;
     more.disabled=Number.isFinite(val)&&val>=max;
    });
   }
   board.append(card);
  }
  this.physicalPaint=()=>{
   for(const update of controls)update();
   const valid=fields.filter(field=>field.checkValidity()&&field.value!=='').length;
   status.textContent='Настроено: '+valid+' из '+fields.length+'. Проверка прибора выполняется отдельно.';
  };
  this.physicalPaint();
 }
 physicalInstrument(parent,a,fields,grid){
 const mainHardware=['POWER_BASIC','RADIO_TUNE','CORES_MARKING','MICROSCOPE','WAVE_PHASE','AIRLOCK_EQUALIZE','CARDIOMATCH','TIMELINE_SYNC','NODE_POWER','NODE_OBSERVER','SHUTTERS','POWER_OFF','ANALOG_READINGS_OK','OBSERVER_SELECT'];
 if(mainHardware.includes(a.id))return this.hardwareInstrument(parent,a,fields,grid);
 if(!['PUNCHCARD_OVERLAY','SPECTRUM_MATCH','ANTENNA'].includes(a.id))return;
 const host=el('section',undefined,'ga-physical'),board=el('div',undefined,'ga-physical-board'),status=el('p',undefined,'ga-physical-status');status.setAttribute('role','status');host.append(board,status);parent.insertBefore(host,grid);const precise=el('details',undefined,'ga-reference');precise.append(el('summary','Точная настройка с клавиатуры'));parent.insertBefore(precise,grid);precise.append(grid);
 const ns='http://www.w3.org/2000/svg',S=(tag,attrs={},text)=>{const node=document.createElementNS(ns,tag);for(const [key,value]of Object.entries(attrs))node.setAttribute(key,String(value));if(text!==undefined)node.textContent=text;return node;};
 const set=(index,value)=>{fields[index].value=String(value);fields[index].dispatchEvent(new Event(fields[index].tagName==='SELECT'?'change':'input',{bubbles:true}));};
 const value=i=>Number(fields[i].value)||0,clampValue=(i,v)=>Math.max(Number(fields[i].min||0),Math.min(Number(fields[i].max||100),v));
 if(a.id==='PUNCHCARD_OVERLAY'){
  status.textContent='Наложите перфокарты и совместите угловые кресты. Карту можно двигать мышью, пальцем или стрелками.';
  const svg=S('svg',{viewBox:'0 0 640 340','aria-label':'Стол совмещения двух перфокарт'}),fixed=S('g'),moving=S('g',{tabindex:0,role:'button','aria-label':'Подвижная перфокарта','data-punch-layer':'true',class:'ga-punch-layer'});board.append(svg);svg.append(fixed,moving);
  const card=(group,id)=>{group.append(S('rect',{x:110,y:80,width:420,height:180,rx:8,fill:'#c8c8ab',stroke:'#ecdfb0','fill-opacity':.7}));const src=this.data.inventoryArt?.[id];if(src)group.append(S('image',{x:110,y:80,width:420,height:180,href:src,'preserveAspectRatio':'xMidYMid meet',opacity:.42}));for(let row=0;row<4;row++)for(let col=0;col<12;col++)if((row*7+col*3)%5<2)group.append(S('rect',{x:150+col*27,y:112+row*30,width:9,height:14,fill:'#14272a',opacity:.7}));for(const [x,y]of [[128,98],[512,242]])group.append(S('path',{d:'M '+(x-10)+' '+y+' h20 M '+x+' '+(y-10)+' v20',stroke:'#302e24','stroke-width':3}));};card(fixed,'PUNCHCARD_RU');card(moving,'PUNCHCARD_DE');const index=S('text',{x:320,y:181,'text-anchor':'middle','font-size':35,style:'font-size:35px;fill:#f6e8b1;paint-order:stroke;stroke:#17282a;stroke-width:4'},'0-4');svg.append(index);
  this.physicalPaint=()=>{moving.setAttribute('transform','translate('+(value(0)*24)+' '+(value(1)*16)+')');index.setAttribute('opacity',String(Math.max(0,1-(Math.abs(value(0))+Math.abs(value(1)))/1.5)));moving.setAttribute('aria-label','Подвижная перфокарта: сдвиг '+value(0)+', '+value(1));};
  let drag=null;moving.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,vx:value(0),vy:value(1),id:e.pointerId};moving.setPointerCapture(e.pointerId);e.preventDefault();};moving.onpointermove=e=>{if(!drag||e.pointerId!==drag.id)return;const scale=640/svg.getBoundingClientRect().width;set(0,clampValue(0,Math.round(drag.vx+(e.clientX-drag.x)*scale/24)));set(1,clampValue(1,Math.round(drag.vy+(e.clientY-drag.y)*scale/16)));};moving.onpointerup=moving.onpointercancel=()=>{drag=null;};moving.onkeydown=e=>{const delta={ArrowLeft:[0,-1],ArrowRight:[0,1],ArrowUp:[1,-1],ArrowDown:[1,1]}[e.key];if(delta){e.preventDefault();set(delta[0],clampValue(delta[0],value(delta[0])+delta[1]));}};
 }else if(a.id==='SPECTRUM_MATCH'){
  status.textContent='Сдвиньте каждый фрагмент до совпадения зубцов с контрольным следом. Для выбранного фрагмента работают стрелки влево и вправо.';const svg=S('svg',{viewBox:'0 0 640 280','aria-label':'Три дорожки совмещения спектра'});board.append(svg);const strips=[];
  const tooth=(x,y,i)=>'M '+x+' '+y+' h9 v-'+(14+i*4)+' h10 v'+(14+i*4)+' h9 v-36 h12 v36 h9 v-'+(22-i*3)+' h11 v'+(22-i*3)+' h6';
  for(let i=0;i<3;i++){const y=61+i*84;svg.append(S('text',{x:10,y:y-37},'ФРАГМЕНТ '+(i+1)),S('path',{d:'M 35 '+(y+5)+' H 615',stroke:'#456066','stroke-width':1}),S('path',{d:tooth(42+Number(a.answer[i])*68,y,i),fill:'none',stroke:'#bdc6ad','stroke-width':7,opacity:.35}));for(let slot=0;slot<=7;slot++)svg.append(S('path',{d:'M '+(42+slot*68)+' '+(y+4)+' v6',stroke:'#63787b'}));const strip=S('g',{tabindex:0,role:'slider','aria-label':'Фрагмент '+(i+1),'aria-valuemin':0,'aria-valuemax':7,'data-strip':i});strip.append(S('rect',{x:-8,y:-45,width:84,height:58,fill:'transparent'}),S('path',{d:tooth(0,0,i),fill:'none',stroke:['#d8c28a','#a8c9bf','#c7b7d0'][i],'stroke-width':3}));svg.append(strip);strips.push({strip,y});let drag=null;strip.onpointerdown=e=>{drag={x:e.clientX,v:value(i),id:e.pointerId};strip.setPointerCapture(e.pointerId);e.preventDefault();};strip.onpointermove=e=>{if(!drag||e.pointerId!==drag.id)return;set(i,clampValue(i,Math.round(drag.v+(e.clientX-drag.x)*640/svg.getBoundingClientRect().width/68)));};strip.onpointerup=strip.onpointercancel=()=>{drag=null;};strip.onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();set(i,clampValue(i,value(i)+(e.key==='ArrowRight'?1:-1)));}};}
  this.physicalPaint=()=>{for(let i=0;i<strips.length;i++){strips[i].strip.setAttribute('transform','translate('+(42+value(i)*68)+' '+strips[i].y+')');strips[i].strip.setAttribute('aria-valuenow',value(i));}};
 }else{
  board.classList.add('ga-antenna');status.textContent='Выберите кабель и гнездо либо перетащите конец кабеля. Повреждённую линию можно оставить отключённой.';const svg=S('svg',{viewBox:'0 0 640 300','aria-hidden':'true',preserveAspectRatio:'none'});board.append(svg);let selected=null,suppress=false;const sources=[],sockets=[],colors=['#d4bf85','#a6c2c9','#c5b0b8','#b2b2a4'];
  const connect=(index,dest)=>{if(dest!=='отключён'&&fields.some((n,i)=>i!==index&&n.value===dest)){status.textContent='Гнездо '+dest+' уже занято. Сначала отсоедините другой кабель.';return;}set(index,dest);selected=null;status.textContent=a.fields[index].label+' → '+(dest==='отключён'?'отключён':'гнездо '+dest);this.physicalPaint();};
  for(let i=0;i<fields.length;i++){const y=45+i*70,button=this.button(board,a.fields[i].label,()=>{if(suppress){suppress=false;return;}selected=i;this.physicalPaint();});button.dataset.cable=i;button.style.top='calc('+(y/3)+'% - 22px)';sources.push(button);let drag=null;button.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,id:e.pointerId};button.setPointerCapture(e.pointerId);};button.onpointerup=e=>{if(!drag)return;const moved=Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>7;drag=null;if(moved){suppress=true;const target=document.elementFromPoint(e.clientX,e.clientY)?.closest('[data-socket]');if(target&&board.contains(target))connect(i,target.dataset.socket);}};button.onpointercancel=()=>{drag=null;};}
  for(const [i,dest]of ['1','2','3','отключён'].entries()){const y=45+i*70,button=this.button(board,dest==='отключён'?'Отключено':'Гнездо '+dest,()=>{if(selected===null){status.textContent='Сначала выберите кабель слева.';return;}connect(selected,dest);});button.dataset.socket=dest;button.style.top='calc('+(y/3)+'% - 22px)';sockets.push(button);}
  this.physicalPaint=()=>{svg.replaceChildren();for(let i=0;i<fields.length;i++){sources[i].setAttribute('aria-pressed',String(selected===i));const dest=['1','2','3','отключён'].indexOf(fields[i].value);if(dest>=0){const base=board.getBoundingClientRect(),sr=sources[i].getBoundingClientRect(),dr=sockets[dest].getBoundingClientRect(),sx=(sr.right-base.left)/base.width*640,sy=(sr.top+sr.height/2-base.top)/base.height*300,dx=(dr.left-base.left)/base.width*640,dy=(dr.top+dr.height/2-base.top)/base.height*300;svg.append(S('path',{d:'M '+sx+' '+sy+' C 280 '+sy+', 360 '+dy+', '+dx+' '+dy,fill:'none',stroke:colors[i],'stroke-width':selected===i?5:3,'stroke-dasharray':i===3?'7 6':i===2?'3 3':'none'}));}}};
 }
 this.physicalPaint();requestAnimationFrame(()=>this.physicalPaint?.());
 }
 instrumentControls(parent,a){const fields=[],saved=this.engine.actionInput(a.id),grid=el('div',undefined,'ga-instrument-grid');parent.append(grid);const save=()=>{this.engine.actionInput(a.id,fields.map(n=>n.value));if(this.error)this.error.textContent='';this.physicalPaint?.();};
 for(const [index,f]of a.fields.entries()){const card=el('section',undefined,'ga-instrument-field'),row=el('label',f.label);let n;
 if(f.options){n=el('select');n.required=true;n.append(new Option('Выберите…',''));for(const value of f.options)n.append(new Option(value,value));n.value=saved[index]??'';n.onchange=save;row.append(n);card.append(row);}
 else{n=el('input');n.type='number';n.inputMode='decimal';n.required=true;if(f.min!==undefined)n.min=f.min;if(f.max!==undefined)n.max=f.max;n.step=f.step||1;n.value=saved[index]!==undefined&&saved[index]!==''?saved[index]:String(f.min??0);row.append(n);card.append(row);
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 160 132');svg.setAttribute('aria-hidden','true');svg.classList.add('ga-meter');const face=document.createElementNS(ns,'path');face.setAttribute('d','M 24.6 110 A 64 64 0 1 1 135.4 110');face.classList.add('ga-meter-face');svg.append(face);for(const [x,anchor,value]of [[12,'start',f.min??0],[148,'end',f.max??100]]){const text=document.createElementNS(ns,'text');text.setAttribute('x',x);text.setAttribute('y',129);text.setAttribute('text-anchor',anchor);text.textContent=value;svg.append(text);}const needle=document.createElementNS(ns,'line');needle.setAttribute('x1',80);needle.setAttribute('y1',78);needle.setAttribute('x2',80);needle.setAttribute('y2',24);needle.classList.add('ga-meter-needle');svg.append(needle);card.append(svg);const output=el('output',undefined,'ga-instrument-value'),tools=el('div',undefined,'ga-adjust'),range=el('input');range.type='range';range.min=f.min??0;range.max=f.max??100;range.step=f.step||1;range.setAttribute('aria-label',f.label+' — шкала');card.append(output,tools);
 const update=(persist=true)=>{const value=n.value,number=Number(value),valid=value!==''&&Number.isFinite(number),lo=Number(range.min),hi=Number(range.max),ratio=valid&&hi>lo?Math.max(0,Math.min(1,(number-lo)/(hi-lo))):0;needle.setAttribute('transform','rotate('+(-120+240*ratio)+' 80 78)');output.textContent=valid?(a.template==='timeline'?Math.floor(number/60).toString().padStart(2,'0')+':'+Math.floor(number%60).toString().padStart(2,'0'):value):'—';if(valid)range.value=value;minus.disabled=valid&&number<=lo;plus.disabled=valid&&number>=hi;if(persist)save();};
 const adjust=direction=>{if(n.value==='')n.value=String(f.min??0);try{direction>0?n.stepUp():n.stepDown();}catch(_){return;}update();};const minus=this.button(tools,'−',()=>adjust(-1)),plus=this.button(tools,'+',()=>adjust(1));minus.setAttribute('aria-label','Уменьшить: '+f.label);plus.setAttribute('aria-label','Увеличить: '+f.label);tools.insertBefore(range,plus);range.oninput=()=>{n.value=range.value;update();};n.oninput=()=>update();update(false);
 const description=el('p','Диапазон: '+(f.min??0)+'…'+(f.max??100)+' · шаг '+(f.step||1),'ga-muted');card.append(description);
 }
 fields.push(n);grid.append(card);}
 this.physicalInstrument(parent,a,fields,grid);
 this.button(parent,a.template==='triple_dial'?'КОНТРОЛЬ':'Проверить',()=>{const invalid=fields.find(n=>!n.checkValidity());if(invalid){if(this.error)this.error.textContent='Заполните все поля в указанном диапазоне.';const details=invalid.closest('details');if(details)details.open=true;invalid.focus();invalid.reportValidity();return;}this.submit(a,fields.map(n=>n.value),true);});
 }
 fieldTask(parent,a){
  const spec=a.fieldTask;
  if(!spec)return parent;
  const board=el('section',undefined,'ga-field-board ga-task-'+spec.kind);
  const help=el('p',spec.instruction,'ga-field-instruction');
  const stage=el('div',undefined,'ga-field-stage');
  const status=el('p','Осмотрите предмет.','ga-field-status');
  status.setAttribute('role','status');
  const reveal=el('p',spec.reveal||'Деталь обнаружена.','ga-field-reveal');
  reveal.hidden=true;
  const options=el('div',undefined,'ga-field-options');
  options.hidden=true;
  let finished=false;
  const finish=()=>{
   if(finished)return;
   finished=true;
   status.textContent='Осмотр завершён. Выберите, что сделать с находкой.';
   reveal.hidden=false;
   options.hidden=false;
   options.querySelector('button:not(:disabled)')?.focus({preventScroll:true});
  };
  board.append(help,stage,status,reveal);
  parent.append(board,options);
  if(spec.kind==='slide'||spec.kind==='focus'||spec.kind==='tune'){
   const object=el('div',undefined,'ga-field-object');
   const note=el('span',spec.kind==='slide'?'УЧЁТ / ВЫДАЧА':spec.kind==='tune'?'84.6 / МГц':'ОБРАЗЕЦ / 17','ga-field-object-label');
   object.append(note);
   stage.append(object);
   const row=el('label',spec.kind==='slide'?'Сдвинуть ярлык':spec.kind==='tune'?'Настройка частоты':'Вращение микровинта','ga-field-range-label');
   const range=el('input');range.type='range';range.min='0';range.max='100';range.step='1';
   range.value=spec.kind==='slide'?'0':spec.kind==='tune'?'26':'12';range.setAttribute('aria-label',row.textContent);
   const update=()=>{
    const value=Number(range.value);
    if(spec.kind==='slide'){
     object.style.setProperty('--shift',(value*.45)+'%');
     status.textContent='Ярлык отогнут: '+value+'%';
     if(value>=88)finish();
    }else if(spec.kind==='tune'){
     object.style.setProperty('--needle',value+'%');
     const drift=Math.abs(value-72);
     status.textContent=drift<=5?'В эфире слышен слабый вдох.':'Слышен только обычный шум приёмника.';
     if(drift<=4)finish();
    }else{
     const blur=Math.max(0,Math.abs(value-64)*.16);
     object.style.filter='blur('+blur.toFixed(1)+'px)';
     status.textContent=blur<.8?'Контур почти совпал.':'Линия ещё не в фокусе.';
     if(Math.abs(value-64)<=4)finish();
    }
   };
   range.oninput=update;
   row.append(range);board.insertBefore(row,status);update();
  }else if(spec.kind==='tap'||spec.kind==='listen'){
   const dial=el('div',undefined,'ga-field-dial');
   const number=el('output','00','ga-field-dial-number');
   dial.append(number);stage.append(dial);
   const control=this.button(board,spec.kind==='listen'?'Прислушаться':'Повернуть рукоять',()=>{
    const count=Math.min(3,Number(number.dataset.turns||0)+1);
    number.dataset.turns=String(count);
    number.textContent=spec.kind==='listen'?'·'.repeat(count):String(count).padStart(2,'0');
    dial.style.setProperty('--turn',count*118+'deg');
    status.textContent=spec.kind==='listen'?'Услышано повторений: '+count+' из 3.':'Поворот '+count+' из 3 · щелчок… щелчок.';
    if(count===3){control.disabled=true;finish();}
   });
   control.className='ga-field-advance';
  }else if(spec.kind==='trace'){
   stage.classList.add('ga-field-drops');
   let next=0;
   const points=[[18,70],[48,46],[79,28]];
   const dots=points.map(([x,y],i)=>{
    const dot=this.button(stage,'',()=>{
     if(i!==next||finished)return;
     dot.classList.add('ga-traced');
     next++;
     status.textContent=next<3?'Прослежено капель: '+next+' из 3':'След ведёт к стене.';
     if(next===3)finish();
     else dots[next].disabled=false;
    },i!==0);
    dot.className='ga-field-drop';dot.style.left=x+'%';dot.style.top=y+'%';
    dot.setAttribute('aria-label','Капля '+(i+1));
    return dot;
   });
  }else if(spec.kind==='wipe'){
   stage.classList.add('ga-field-glass');
   stage.setAttribute('role','img');stage.setAttribute('aria-label','Запотевшее стекло шлюза');
   let wiped=0,active=null;
   const progress=delta=>{
    if(finished)return;
    wiped=Math.min(100,wiped+delta);
    stage.style.setProperty('--cleared',wiped+'%');stage.style.setProperty('--cleared-number',String(wiped/100));stage.style.setProperty('--reveal',String(wiped/100));
    status.textContent='Стекло очищено на '+Math.round(wiped)+'%';
    if(wiped>=95)finish();
   };
   stage.onpointerdown=e=>{
    if(e.pointerType==='mouse'&&e.button!==0)return;
    active={id:e.pointerId,x:e.clientX,y:e.clientY};
    stage.setPointerCapture(e.pointerId);
   };
   stage.onpointermove=e=>{
    if(!active||active.id!==e.pointerId)return;
    const delta=Math.hypot(e.clientX-active.x,e.clientY-active.y);
    if(delta>3){progress(delta/Math.max(1,stage.clientWidth)*110);active.x=e.clientX;active.y=e.clientY;}
   };
   stage.onpointerup=stage.onpointercancel=()=>{active=null;};
   const control=this.button(board,'Протереть стекло',()=>progress(25));
   control.className='ga-field-advance';
   const complete=finish;
   // Keep the keyboard alternative in sync with pointer completion.
   const old=stage.onpointermove;
   stage.onpointermove=e=>{old(e);if(finished)control.disabled=true;};
   const clicked=control.onclick;
   control.onclick=()=>{clicked();if(finished)control.disabled=true;};
  }else{
   options.hidden=false;
   status.textContent='Выберите действие.';
  }
  return options;
 }
 openAction(id){const a=this.engine.begin(id);if(!a)return;if(a.startSignal){this.engine.modal=false;const ev=this.engine.flush(0);this.engine.modal=true;if(ev){
  // Quiet pre-action cues must not strand the engine in modal=true with no window.
  // Only a full cinematic scene defers the intended object interaction.
  if(this.isAmbientEvent(ev))this.scene(ev);
  else{this.scene(ev);this.afterScene=()=>this.openAction(id);return;}
 }}const b=this.panel(a.label);
 if(a.fieldChoice)b.classList.add('ga-field-choice');
 this.currentAction=id;const art=this.data.illustratedProps;if(a.template!=='document'&&a.template!=='media'&&!a.fieldChoice){const src=art?.image?.[art?.action?.[id]],inspection=art?.inspections?.[id];if(src&&inspection)this.inspectionPreview(b,a,src,inspection);else this.showArt(b,src,a.label);}
 const pickup=a.effects?.find(fx=>fx.item)?.item;if(pickup)this.showArt(b,this.data.inventoryArt?.[pickup],this.itemName(pickup));
 if(a.template==='media'){this.playMedia(this.data.media.find(m=>m.id===a.media),a);return;}
 if(a.template==='document'){this.documentView(b,this.data.documents.find(d=>d.id===a.document));this.button(b,a.readLabel||'Сохранить в журнале',()=>this.submit(a,null));}
 else if(a.template==='choice'||a.template==='sequence_choice'){if(a.text)b.append(el('pre',a.text));const choices=a.fieldTask?this.fieldTask(b,a):b;for(const op of a.options){const valid=api.test(op.when,this.engine.state);this.button(choices,op.label,()=>{if(a.confirm)this.confirmAction(a,op.value,op.label);else this.submit(a,op.value);},!valid);if(!valid)choices.append(el('p',op.locked,'ga-muted'));}}
 else if(a.template==='sequence'||a.template==='order')this.sequenceControl(b,a);
 else if(a.answer)this.instrumentControls(b,a);
 else{if(a.text)b.append(el('pre',a.text));this.button(b,'Выполнить',()=>a.confirm?this.confirmAction(a,null,a.label):this.submit(a,null));}
 if(a.answer){this.attemptLabel=el('p',undefined,'ga-attempt');this.attemptLabel.setAttribute('role','status');b.append(this.attemptLabel);this.instrumentAttempts(a);this.instrumentReferences(b,a);}if(a.hint){const d=el('details',undefined,'ga-reference');d.open=(this.engine.state.errors[a.id]||0)>=2;d.append(el('summary','Инструкция к прибору'),el('p',a.hint));this.instrumentHint=d;b.append(d);}this.error=el('p',undefined,'ga-error');this.error.setAttribute('aria-live','polite');b.append(this.error);this.button(b,'Закрыть',()=>this.close());}
 confirmAction(a,value,label){const b=this.panel('Подтверждение');b.append(el('h3',label),el('p',a.confirm));this.button(b,'Подтвердить'+(a.template==='sequence_choice'?' и подписать':''),()=>this.submit(a,value));this.button(b,'Вернуться',()=>this.openAction(a.id));}
 submit(a,value,keep=false){const before={items:[...this.engine.state.inventory],documents:[...this.engine.state.documents],chapter:this.engine.state.chapter};const oldGoal=this.guide()?.action?.id,wasReady=new Set(this.evidenceReadyCases().map(c=>c.id));const r=this.engine.answer(a.id,value);if(r.death||this.death){const message=this.death||r.message;this.death=null;this.close(false);this.sync();const b=this.panel('Возврат к локальному чекпоинту');b.append(el('p',message),el('p','Выполненные до чекпоинта действия сохранены.'));if(a.deathHelp||a.hint)b.append(el('pre',a.deathHelp||a.hint));this.button(b,'Повторить узел',()=>this.close());return r;}
 if(!r.ok){if(this.error)this.error.textContent=r.message;this.instrumentAttempts(a);if(this.instrumentHint&&(this.engine.state.errors[a.id]||0)>=2){this.instrumentHint.open=true;if(this.error&&r.message===a.hint)this.error.textContent='Показания не совпали. Инструкция раскрыта ниже.';}return r;}const after=this.engine.state,messages=[];for(const id of after.inventory.filter(id=>!before.items.includes(id)))messages.push('Получено: '+this.itemName(id));for(const id of before.items.filter(id=>!after.inventory.includes(id)))messages.push('Использовано: '+this.itemName(id));if(after.documents.some(id=>!before.documents.includes(id)))messages.push('Документ сохранён в журнале');if(after.chapter!==before.chapter)messages.push(this.data.quests.find(q=>q.chapter===after.chapter)?.title||'Новая задача');if(!messages.length)messages.push('Выполнено: '+a.label);
 const newCases=this.evidenceReadyCases().filter(c=>!wasReady.has(c.id));
 if(newCases.length)messages.push('Найдена связь между уликами. Откройте раздел «Улики» в журнале.');
 const next=this.guide();if(a.id===oldGoal&&next?.step&&next.action?.id!==a.id)messages.push('Дальше: '+next.step.text);
 this.notify(messages.join('\n'));this.close(false);this.sync();if(this.pendingLines.length){const lines=this.pendingLines.splice(0),b=this.panel('Эфир');b.append(el('p','Выполнено: '+a.label,'ga-result'));for(const line of lines)b.append(el('pre',line.text));this.speakLines(lines);this.button(b,'Продолжить',()=>this.close());}else this.restoreFocus?.();return r;}
 playMedia(m,a,back=null){const b=this.panel(m.id+' · '+m.title);const warning=el('div','Запись '+m.id+' · доступен текстовый режим','ga-muted');b.append(warning);const art=this.data.illustratedProps;this.showArt(b,art?.image?.[art?.action?.['watch_'+m.id]],m.title);let t=0,started=false,frame=0,finished=false;const voiced=new Set(),voiceCues=()=>{const due=(m.voiceCues||[]).filter(c=>c.at<=t&&!voiced.has(c.id));for(const c of due)voiced.add(c.id);if(due.length)this.ensureVoice()?.enqueue(due.map(c=>c.id));};const time=el('div','00:00','ga-muted'),scene=el('div',m.frames[0]?.text||'','ga-scene'),progress=el('progress',undefined,'ga-progress');progress.max=m.duration;progress.value=0;b.append(time,progress,scene);
 const transcript=el('details');transcript.open=false;transcript.append(el('summary','Текст записи'));for(const l of m.transcript||[])transcript.append(el('pre',l.text));if(!m.transcript?.length)transcript.append(el('pre',m.frames.map(f=>f.text).join('\n')));b.append(transcript);
 const row=el('div',undefined,'ga-row');b.append(row);const play=this.button(row,'PLAY',()=>{started=!started;this.voice?.setPaused(!started,true);if(started)voiceCues();play.textContent=started?'Пауза':'PLAY';video?.[started?'play':'pause']()?.catch?.(()=>{video?.pause();video?.remove();warning.textContent='Ошибка воспроизведения '+m.id+'. Продолжите текстовую раскадровку.';video=null;});});
 const done=()=>{if(finished)return;finished=true;started=false;this.stopVoice?.();scene.textContent='Запись окончена.';if(a)this.button(b,'Завершить просмотр',()=>this.submit(a,null));else this.button(b,back?'К финалу':'В журнал',()=>back?back():this.journal());};
 this.button(row,'Следующий фрагмент · текстовый режим',()=>{started=false;this.stopVoice?.();play.textContent='PLAY';video?.pause();t=m.frames[frame]?.end||m.duration;frame++;if(frame>=m.frames.length)done();else scene.textContent=m.frames[frame].text;progress.value=t;time.textContent=Math.floor(t/60).toString().padStart(2,'0')+':'+Math.floor(t%60).toString().padStart(2,'0');});
 let video=null,objectURL=null;const asset=this.hooks.media?.(m.id);if(asset){video=document.createElement(m.kind==='audio'?'audio':'video');video.controls=true;video.style.maxWidth='100%';objectURL=asset.url;video.src=objectURL;b.insertBefore(video,time);warning.textContent='Запись '+m.id;video.onerror=()=>{warning.textContent='ОШИБКА ЗАГРУЗКИ: '+m.id+'. Доступна полная текстовая раскадровка.';video.remove();video=null;};video.onplay=()=>{started=true;this.voice?.setPaused(false,true);t=video.currentTime;voiceCues();play.textContent='Пауза';};video.onpause=()=>{started=false;this.voice?.setPaused(true,true);play.textContent='PLAY';};video.onseeking=()=>{this.stopVoice?.();for(const c of m.voiceCues||[])if(c.at<video.currentTime)voiced.add(c.id);};video.onended=done;video.onloadedmetadata=()=>{if(m.kind==='audio'&&Number.isFinite(video.duration))progress.max=video.duration;};this.voiceMediaElement=video;this.syncVoiceVolume();}
 this.mediaTick=dt=>{if(!started||finished)return;t=video?video.currentTime:t+dt;voiceCues();progress.value=t;time.textContent=Math.floor(t/60).toString().padStart(2,'0')+':'+Math.floor(t%60).toString().padStart(2,'0');frame=Math.max(0,m.frames.findIndex(f=>t>=f.start&&t<f.end));scene.textContent=m.frames[frame]?.text||m.frames.at(-1)?.text||'';if(t>=m.duration&&!video)done();};this.disposeMedia=()=>{this.voiceMediaElement=null;if(video){video.onplay=video.onpause=video.onended=video.onseeking=video.onloadedmetadata=null;video.pause();video.removeAttribute('src');video.load();}if(objectURL?.startsWith('blob:'))URL.revokeObjectURL(objectURL);};this.button(b,'Закрыть без отметки просмотра',()=>back?back():this.close());}
 restoreCheckpoint(){const cp=this.engine.state.checkpoint;if(!cp)return;const b=this.panel('Загрузить чекпоинт');b.append(el('p','Текущие изменения после контрольной точки будут заменены.'));this.button(b,'Загрузить',()=>{const save=api.copy(cp.state);save.checkpoint=api.copy(cp);this.endingShown=false;this.load(save);this.sync();});this.button(b,'Отмена',()=>this.close());}
 ending(frame=0){this.endingShown=true;const mode=this.engine.state.ended,e=this.data.endings[mode];const shell=this.panel(e.title);shell.classList.add('ga-ending');this.showArt(shell,e.image,e.title);const progress=el('div',undefined,'ga-ending-progress'),fill=el('span');progress.append(fill);const b=el('div',undefined,'ga-ending-body');shell.append(progress,b);const shots=this.data.endingScenes?.[mode]||[{caption:e.text}],shot=shots[Math.min(frame,shots.length-1)];b.append(el('div',shot.caption,'ga-scene'),el('p',(frame+1)+' / '+shots.length,'ga-muted'));if(frame<shots.length-1){const next=this.button(b,'Продолжить финал',()=>this.ending(frame+1));next.disabled=true;let shown=0;const reading=Math.max(2.8,Math.min(9,shot.caption.split(/\s+/).length/3));this.endingTick=dt=>{shown+=dt;fill.style.width=Math.min(100,shown/reading*100)+'%';if(shown>=1.2)next.disabled=false;};return;}fill.style.width='100%';for(const entry of this.engine.state.journal.filter(j=>j.ending===mode))for(const line of entry.lines||[])b.append(el('div',line.speaker+'\n'+line.text,'ga-caption'));for(const id of e.extraLines||[]){const line=this.data.dialogues.find(l=>l.id===id);if(line)b.append(el('pre',line.text));}const voicedEnding=this.voicedEndings||(this.voicedEndings=new Set());if(!voicedEnding.has(mode)){voicedEnding.add(mode);const lines=this.engine.state.journal.filter(j=>j.ending===mode).flatMap(j=>j.lines||[]);for(const id of e.extraLines||[]){const line=this.data.dialogues.find(l=>l.id===id);if(line)lines.push(line);}this.speakLines(lines);}if(e.media)this.button(b,'Посмотреть эпилог',()=>this.playMedia(this.data.media.find(m=>m.id===e.media),null,()=>this.ending(shots.length-1)));
 this.button(b,'Титры',()=>{const box=this.panel(this.data.title);box.append(el('div',this.data.credits||'','ga-credits'));this.button(box,'К финалу',()=>this.ending(shots.length-1));this.button(box,'Следующая проверка',()=>{this.engine.apply([{set:{POST_CREDITS:true}}]);this.engine.changed();const p=this.panel('Журнал следующей смены');p.append(el('pre',e.postcredit||''));this.button(p,'Загрузить до панели',()=>this.restoreCheckpoint());this.button(p,'Новая игра',()=>this.hooks.newGame?.());});});}

}
api.UI=UI;
})();
