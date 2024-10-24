import os
import sys
sys.dont_write_bytecode = True
abs_path = 'data'


LVDT_data_files = {
    "LVDT_aircoil": {
        'aircoil': '/aircoil/LVDT_aircoil_default.h5',
        'magcore': '/aircoil/LVDT_magcore_default.h5',
        'combi'  : '/aircoil/LVDT_aircoil_magcore_default.h5',},
    "LVDT_alucld_od08": {
        'alucld_od08id07': '/alucld/LVDT_alucld_od08id07_l12.h5',
        'alucld_od08id06': '/alucld/LVDT_alucld_od08id06_l12.h5',
        'alucld_od08id05': '/alucld/LVDT_alucld_od08id05_l12.h5',
        'alucld_od08id04': '/alucld/LVDT_alucld_od08id04_l12.h5',
        },
    "LVDT_alucld_od10": {
        'alucld_od10id09': '/alucld/LVDT_alucld_od10id09_l12.h5',
        'alucld_od10id08': '/alucld/LVDT_alucld_od10id08_l12.h5',
        'alucld_od10id07': '/alucld/LVDT_alucld_od10id07_l12.h5',
        'alucld_od10id06': '/alucld/LVDT_alucld_od10id06_l12.h5',
        'alucld_od10id05': '/alucld/LVDT_alucld_od10id05_l12.h5',
        },
    "LVDT_alucld_od12": {
        'alucld_od12id11': '/alucld/LVDT_alucld_od12id11_l12.h5',
        'alucld_od12id10': '/alucld/LVDT_alucld_od12id10_l12.h5',
        'alucld_od12id09': '/alucld/LVDT_alucld_od12id09_l12.h5',
        'alucld_od12id08': '/alucld/LVDT_alucld_od12id08_l12.h5',
        'alucld_od12id07': '/alucld/LVDT_alucld_od12id07_l12.h5',
        'alucld_od12id06': '/alucld/LVDT_alucld_od12id06_l12.h5',
        },
    "LVDT_alucld_od14": {
        'alucld_od14id13': '/alucld/LVDT_alucld_od14id13_l12.h5',
        'alucld_od14id12': '/alucld/LVDT_alucld_od14id12_l12.h5',
        'alucld_od14id11': '/alucld/LVDT_alucld_od14id11_l12.h5',
        'alucld_od14id10': '/alucld/LVDT_alucld_od14id10_l12.h5',
        'alucld_od14id09': '/alucld/LVDT_alucld_od14id09_l12.h5',
        'alucld_od14id08': '/alucld/LVDT_alucld_od14id08_l12.h5',
        'alucld_od14id07': '/alucld/LVDT_alucld_od14id07_l12.h5',
        },

    "LVDT_alucld_od08_magcore_d04_l06": {
        'alucld_od08id07': '/alucld/LVDT_alucld_od08id07_l12_magcore_d04_l06.h5',
        'alucld_od08id06': '/alucld/LVDT_alucld_od08id06_l12_magcore_d04_l06.h5',
        'alucld_od08id05': '/alucld/LVDT_alucld_od08id05_l12_magcore_d04_l06.h5',
        'alucld_od08id04': '/alucld/LVDT_alucld_od08id04_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od10_magcore_d04_l06": {
        'alucld_od10id09': '/alucld/LVDT_alucld_od10id09_l12_magcore_d04_l06.h5',
        'alucld_od10id08': '/alucld/LVDT_alucld_od10id08_l12_magcore_d04_l06.h5',
        'alucld_od10id07': '/alucld/LVDT_alucld_od10id07_l12_magcore_d04_l06.h5',
        'alucld_od10id06': '/alucld/LVDT_alucld_od10id06_l12_magcore_d04_l06.h5',
        'alucld_od10id05': '/alucld/LVDT_alucld_od10id05_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od12_magcore_d04_l06": {
        'alucld_od12id11': '/alucld/LVDT_alucld_od12id11_l12_magcore_d04_l06.h5',
        'alucld_od12id10': '/alucld/LVDT_alucld_od12id10_l12_magcore_d04_l06.h5',
        'alucld_od12id09': '/alucld/LVDT_alucld_od12id09_l12_magcore_d04_l06.h5',
        'alucld_od12id08': '/alucld/LVDT_alucld_od12id08_l12_magcore_d04_l06.h5',
        'alucld_od12id07': '/alucld/LVDT_alucld_od12id07_l12_magcore_d04_l06.h5',
        'alucld_od12id06': '/alucld/LVDT_alucld_od12id06_l12_magcore_d04_l06.h5',
        },
    "LVDT_alucld_od14_magcore_d04_l06": {
        'alucld_od14id13': '/alucld/LVDT_alucld_od14id13_l12_magcore_d04_l06.h5',
        'alucld_od14id12': '/alucld/LVDT_alucld_od14id12_l12_magcore_d04_l06.h5',
        'alucld_od14id11': '/alucld/LVDT_alucld_od14id11_l12_magcore_d04_l06.h5',
        'alucld_od14id10': '/alucld/LVDT_alucld_od14id10_l12_magcore_d04_l06.h5',
        'alucld_od14id09': '/alucld/LVDT_alucld_od14id09_l12_magcore_d04_l06.h5',
        'alucld_od14id08': '/alucld/LVDT_alucld_od14id08_l12_magcore_d04_l06.h5',
        'alucld_od14id07': '/alucld/LVDT_alucld_od14id07_l12_magcore_d04_l06.h5',
        },
}

VC_data_files = {
    "VC_alucld_od08id07": {
        'mag_od08id07_l04': '/alucld/VC_alucld_od08id07_l12_magcore_d07_l04.h5',
        'mag_od08id07_l06': '/alucld/VC_alucld_od08id07_l12_magcore_d07_l06.h5',
        'mag_od08id07_l08': '/alucld/VC_alucld_od08id07_l12_magcore_d07_l08.h5',
        'mag_od08id07_l10': '/alucld/VC_alucld_od08id07_l12_magcore_d07_l10.h5',
        'mag_od08id07_l12': '/alucld/VC_alucld_od08id07_l12_magcore_d07_l12.h5',
        },
    "VC_alucld_od08id06": {
        'mag_od08id06_l04': '/alucld/VC_alucld_od08id06_l12_magcore_d06_l04.h5',
        'mag_od08id06_l06': '/alucld/VC_alucld_od08id06_l12_magcore_d06_l06.h5',
        'mag_od08id06_l08': '/alucld/VC_alucld_od08id06_l12_magcore_d06_l08.h5',
        'mag_od08id06_l10': '/alucld/VC_alucld_od08id06_l12_magcore_d06_l10.h5',
        'mag_od08id06_l12': '/alucld/VC_alucld_od08id06_l12_magcore_d06_l12.h5',
        },
    "VC_alucld_od10id09": {
        'mag_od10id09_l04': '/alucld/VC_alucld_od10id09_l12_magcore_d09_l04.h5',
        'mag_od10id09_l06': '/alucld/VC_alucld_od10id09_l12_magcore_d09_l06.h5',
        'mag_od10id09_l08': '/alucld/VC_alucld_od10id09_l12_magcore_d09_l08.h5',
        'mag_od10id09_l10': '/alucld/VC_alucld_od10id09_l12_magcore_d09_l10.h5',
        'mag_od10id09_l12': '/alucld/VC_alucld_od10id09_l12_magcore_d09_l12.h5',
        },
    "VC_alucld_od10id08": {
        'mag_od10id08_l04': '/alucld/VC_alucld_od10id08_l12_magcore_d08_l04.h5',
        'mag_od10id08_l06': '/alucld/VC_alucld_od10id08_l12_magcore_d08_l06.h5',
        'mag_od10id08_l08': '/alucld/VC_alucld_od10id08_l12_magcore_d08_l08.h5',
        'mag_od10id08_l10': '/alucld/VC_alucld_od10id08_l12_magcore_d08_l10.h5',
        'mag_od10id08_l12': '/alucld/VC_alucld_od10id08_l12_magcore_d08_l12.h5',
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