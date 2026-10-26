'use strict';
// Authored interactions only. No injected flags, checkpoints or chapter changes.
const route=[
 'take_BADGE04','take_STORAGE_KEY','read_D01','TEA_SEQUENCE','sign_shift','take_FUSE_3','install_fuse3',
 'read_D28','POWER_BASIC','CORES_MARKING','RADIO_TUNE','send_report',
 'read_D19','PLUMB_SEQ','watch_V01', {room:'C'},'mirror03',{room:'A'},{room:'D'},'cabinet_message','archive_return',
 'read_D20','count_cans','read_D16','COOKING','mirror04','mirror04_away','mirror04_again','mirror04_third', ['plate_choice','LEFT'],
 {room:'C'},{room:'B'},{room:'C'},{room:'A'},'dinner_exit',
 'take_P17_SAMPLE','SPECTRUM_MATCH','MICROSCOPE','read_D06','hidden_enter','read_D03','hidden_exit',
 {room:'A'},{room:'I'},{room:'B'},'WAVE_PHASE','watch_A02','watch_A01','read_D02','read_D27','mirror06','mirror06_again','read_D07','flip_acts',
 'read_D22','take_FLASHLIGHT','take_ANTENNA_KEY','take_BEACON','ice_1','ice_2','ice_3','ANTENNA','glass07','AIRLOCK_EQUALIZE','inner_door',
 {room:'A'},{room:'B'},'take_VHS_FRAGMENT_A','take_VHS_FRAGMENT_B','read_D23','VHS_ASSEMBLE','watch_V02','read_D13','read_D29','read_D05','take_VHS_V03','watch_V03','petr_letter',
 {room:'B'},{room:'A'},'wet_towel','read_D04','read_D09','read_D21','take_PUNCHCARD_RU','take_PUNCHCARD_DE','PUNCHCARD_OVERLAY','scan_uv','enter_1978',
 'read_D08','read_D12','calibration_plate','watch_V06','watch_V09','watch_A03','exit_1978',
 'read_D17','read_D18','watch_A04','CARDIOMATCH','medic10','TIMELINE_SYNC','watch_V04','late10','read_D14','read_D11','read_D15','watch_V08',
 'handwriting_floor','backward_clock','reversed_exit_arrow','leave_N',{room:'B'},['false_act','NO'],
 {room:'A'},{room:'F'},{room:'B'},'blanket11','watch_V01B',
 'NODE_POWER', ['NODE_MEMORY',mode=>mode==='D'?'PETR':'TRUTH'], ['NODE_OBSERVER',mode=>mode==='B'?2:1],
 'SHUTTERS','name_reply','second_window','third_window','POWER_OFF','take_SHUTTER_PIN','PIN_INSERT','ANALOG_READINGS_OK','OBSERVER_SELECT',
 ['FINAL_PANEL',mode=>mode]
];
module.exports={route};
