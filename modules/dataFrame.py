import os
import sys
sys.dont_write_bytecode = True
abs_path = 'data'

LVDT_data_files = {
    "LVDT_aircoil": {
        'aircoil': '/aircoil/LVDT_aircoil_default.h5',
        'magcore': '/aircoil/LVDT_magcore_default.h5',
        'combi': '/aircoil/LVDT_aircoil_magcore_default.h5',},
    "LVDT_alucld_od08": {
        'id07_od08': '/alucld/LVDT_alucld_id07_od08_l12.h5',
        'id06_od08': '/alucld/LVDT_alucld_id06_od08_l12.h5',
        'id05_od08': '/alucld/LVDT_alucld_id05_od08_l12.h5',
        'id04_od08': '/alucld/LVDT_alucld_id04_od08_l12.h5',
        },
    "LVDT_alucld_od10": {
        'id09_od10': '/alucld/LVDT_alucld_id09_od10_l12.h5',
        'id08_od10': '/alucld/LVDT_alucld_id08_od10_l12.h5',
        'id07_od10': '/alucld/LVDT_alucld_id07_od10_l12.h5',
        'id06_od10': '/alucld/LVDT_alucld_id06_od10_l12.h5',
        'id05_od10': '/alucld/LVDT_alucld_id05_od10_l12.h5',
        },
    "LVDT_alucld_od12": {
        'id11_od12': '/alucld/LVDT_alucld_id11_od12_l12.h5',
        'id10_od12': '/alucld/LVDT_alucld_id10_od12_l12.h5',
        'id09_od12': '/alucld/LVDT_alucld_id09_od12_l12.h5',
        'id08_od12': '/alucld/LVDT_alucld_id08_od12_l12.h5',
        'id07_od12': '/alucld/LVDT_alucld_id07_od12_l12.h5',
        'id06_od12': '/alucld/LVDT_alucld_id06_od12_l12.h5',
        },
    "LVDT_alucld_od14": {
        'id13_od14': '/alucld/LVDT_alucld_id13_od14_l12.h5',
        'id12_od14': '/alucld/LVDT_alucld_id12_od14_l12.h5',
        'id11_od14': '/alucld/LVDT_alucld_id11_od14_l12.h5',
        'id10_od14': '/alucld/LVDT_alucld_id10_od14_l12.h5',
        'id09_od14': '/alucld/LVDT_alucld_id09_od14_l12.h5',
        'id08_od14': '/alucld/LVDT_alucld_id08_od14_l12.h5',
        'id07_od14': '/alucld/LVDT_alucld_id07_od14_l12.h5',
        },

    "LVDT_alucld_od08_magcore_d04_l06": {
        'id07_od08': '/alucld/LVDT_alucld_id07_od08_l12_magcore_d04_l06.h5',
        'id06_od08': '/alucld/LVDT_alucld_id06_od08_l12_magcore_d04_l06.h5',
        'id05_od08': '/alucld/LVDT_alucld_id05_od08_l12_magcore_d04_l06.h5',
        'id04_od08': '/alucld/LVDT_alucld_id04_od08_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od10_magcore_d04_l06": {
        'id09_od10': '/alucld/LVDT_alucld_id09_od10_l12_magcore_d04_l06.h5',
        'id08_od10': '/alucld/LVDT_alucld_id08_od10_l12_magcore_d04_l06.h5',
        'id07_od10': '/alucld/LVDT_alucld_id07_od10_l12_magcore_d04_l06.h5',
        'id06_od10': '/alucld/LVDT_alucld_id06_od10_l12_magcore_d04_l06.h5',
        'id05_od10': '/alucld/LVDT_alucld_id05_od10_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od12_magcore_d04_l06": {
        'id11_od12': '/alucld/LVDT_alucld_id11_od12_l12_magcore_d04_l06.h5',
        'id10_od12': '/alucld/LVDT_alucld_id10_od12_l12_magcore_d04_l06.h5',
        'id09_od12': '/alucld/LVDT_alucld_id09_od12_l12_magcore_d04_l06.h5',
        'id08_od12': '/alucld/LVDT_alucld_id08_od12_l12_magcore_d04_l06.h5',
        'id07_od12': '/alucld/LVDT_alucld_id07_od12_l12_magcore_d04_l06.h5',
        'id06_od12': '/alucld/LVDT_alucld_id06_od12_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od14_magcore_d04_l06": {
        'id13_od14': '/alucld/LVDT_alucld_id13_od14_l12_magcore_d04_l06.h5',
        'id12_od14': '/alucld/LVDT_alucld_id12_od14_l12_magcore_d04_l06.h5',
        'id11_od14': '/alucld/LVDT_alucld_id11_od14_l12_magcore_d04_l06.h5',
        'id10_od14': '/alucld/LVDT_alucld_id10_od14_l12_magcore_d04_l06.h5',
        'id09_od14': '/alucld/LVDT_alucld_id09_od14_l12_magcore_d04_l06.h5',
        'id08_od14': '/alucld/LVDT_alucld_id08_od14_l12_magcore_d04_l06.h5',
        'id07_od14': '/alucld/LVDT_alucld_id07_od14_l12_magcore_d04_l06.h5',
        },
}


VC_data_files = {
    "VC_alucld_id07_od08": {
        'mag_id07_od08_l04': '/alucld/VC_alucld_id07_od08_l12_magcore_d07_l04.h5',
        'mag_id07_od08_l06': '/alucld/VC_alucld_id07_od08_l12_magcore_d07_l06.h5',
        'mag_id07_od08_l08': '/alucld/VC_alucld_id07_od08_l12_magcore_d07_l08.h5',
        'mag_id07_od08_l10': '/alucld/VC_alucld_id07_od08_l12_magcore_d07_l10.h5',
        'mag_id07_od08_l12': '/alucld/VC_alucld_id07_od08_l12_magcore_d07_l12.h5',
        },
    "VC_alucld_id06_od08": {
        'mag_id06_od08_l04': '/alucld/VC_alucld_id06_od08_l12_magcore_d06_l04.h5',
        'mag_id06_od08_l06': '/alucld/VC_alucld_id06_od08_l12_magcore_d06_l06.h5',
        'mag_id06_od08_l08': '/alucld/VC_alucld_id06_od08_l12_magcore_d06_l08.h5',
        'mag_id06_od08_l10': '/alucld/VC_alucld_id06_od08_l12_magcore_d06_l10.h5',
        'mag_id06_od08_l12': '/alucld/VC_alucld_id06_od08_l12_magcore_d06_l12.h5',
        },
    "VC_alucld_id09_od10": {
        'mag_id09_od10_l04': '/alucld/VC_alucld_id09_od10_l12_magcore_d09_l04.h5',
        'mag_id09_od10_l06': '/alucld/VC_alucld_id09_od10_l12_magcore_d09_l06.h5',
        'mag_id09_od10_l08': '/alucld/VC_alucld_id09_od10_l12_magcore_d09_l08.h5',
        'mag_id09_od10_l10': '/alucld/VC_alucld_id09_od10_l12_magcore_d09_l10.h5',
        'mag_id09_od10_l12': '/alucld/VC_alucld_id09_od10_l12_magcore_d09_l12.h5',
        },
    "VC_alucld_id08_od10": {
        'mag_id08_od10_l04': '/alucld/VC_alucld_id08_od10_l12_magcore_d08_l04.h5',
        'mag_id08_od10_l06': '/alucld/VC_alucld_id08_od10_l12_magcore_d08_l06.h5',
        'mag_id08_od10_l08': '/alucld/VC_alucld_id08_od10_l12_magcore_d08_l08.h5',
        'mag_id08_od10_l10': '/alucld/VC_alucld_id08_od10_l12_magcore_d08_l10.h5',
        'mag_id08_od10_l12': '/alucld/VC_alucld_id08_od10_l12_magcore_d08_l12.h5',
        },
}

Magnet_data_files = {
    'LVDT_magcore_d04':{
        'l04': '/magcore/LVDT_magcore_d04_l04.h5',
        'l06': '/magcore/LVDT_magcore_d04_l06.h5',
        'l08': '/magcore/LVDT_magcore_d04_l08.h5',
        'l10': '/magcore/LVDT_magcore_d04_l10.h5',
        'l12': '/magcore/LVDT_magcore_d04_l12.h5',
        },
    'LVDT_magcore_d05':{
        'l04': '/magcore/LVDT_magcore_d05_l04.h5',
        'l06': '/magcore/LVDT_magcore_d05_l06.h5',
        'l08': '/magcore/LVDT_magcore_d05_l08.h5',
        'l10': '/magcore/LVDT_magcore_d05_l10.h5',
        'l12': '/magcore/LVDT_magcore_d05_l12.h5',
        },
    'LVDT_magcore_d06':{
        'l04': '/magcore/LVDT_magcore_d06_l04.h5',
        'l06': '/magcore/LVDT_magcore_d06_l06.h5',
        'l08': '/magcore/LVDT_magcore_d06_l08.h5',
        'l10': '/magcore/LVDT_magcore_d06_l10.h5',
        'l12': '/magcore/LVDT_magcore_d06_l12.h5',
        },
    'LVDT_magcore_d07':{    
        'l04': '/magcore/LVDT_magcore_d07_l04.h5',
        'l06': '/magcore/LVDT_magcore_d07_l06.h5',
        'l08': '/magcore/LVDT_magcore_d07_l08.h5',
        'l10': '/magcore/LVDT_magcore_d07_l10.h5',
        'l12': '/magcore/LVDT_magcore_d07_l12.h5',
        },
    'LVDT_magcore_d08':{
        'l04': '/magcore/LVDT_magcore_d08_l04.h5',
        'l06': '/magcore/LVDT_magcore_d08_l06.h5',
        'l08': '/magcore/LVDT_magcore_d08_l08.h5',
        'l10': '/magcore/LVDT_magcore_d08_l10.h5',
        'l12': '/magcore/LVDT_magcore_d08_l12.h5',
        },
}