# copyright ############################### #
# This file is part of the Xcoll Package.   #
# Copyright (c) CERN, 2024.                 #
# ######################################### #


tmpAuxFile = open ('colldb_lhc_run3.yaml' ,'r'  )
CDByamlflag = True

twiss_fname = args.TFile[0]
tmpOptFile = AuxFile( twiss_fname )
NREMIT = float( args.EMIn[0] )    # normalised emmittance in [m]
MOMENTUM = float( args.pc[0] )    # [GeV/c]
GEOEMIT = NREMIT / (gamma*beta)   # gamma*beta = Pc / m

# Collision IPs not done!

BeamLine = TWISS_ELEMENTs()

    # Prototype list (collimator names and positions in PARKING region)
    lbp_fname  = "prototypes.lbp" #There is a better way...but enough for now!


    # output files:
    #     1- fort.3 insertion point list
    sixt_fname = outFileName + ".fort3.list"
    #     2- insertion.txt file
    injec_fname = outFileName + ".insertion.txt"
    #     3- FLUKA input file
    out_fname  = outFileName + ".inp"
    #     4- Log file
    log_fname  = outFileName + ".log"


                element = TWISS_ELEMENT()
                COLLID += 1
                element.ID = COLLID
                element.NAME = name.upper()
                if type(settings['gap']) is str:
                    if settings['gap'] not in data['Families']:
                        error_message ( "The gap family setting '" + settings['gap'] + "' for collimator " + name + " is not defined in Families!", True )
                    element.NSIG = NullGap( data['Families'][ settings['gap'] ]['gap'] )
                else:
                    element.NSIG = NullGap( settings['gap'] )
                element.MATERIAL = settings['material']
                element.LENGTH = settings['length']
                element.ANGLE = math.radians(settings.get('angle',0))
                if float(settings.get('offset',0)) != 0:
                    print ' collimator offset ignored for the time being...'
                element.TILT1 = math.radians(settings.get('tilt_right',0))
                element.TILT2 = math.radians(settings.get('tilt_left',0))
                element.BETX = 0.0
                element.BETY = 0.0
                element.SIGX = 0.0
                element.SIGY = 0.0
                element.HALFGAP = 0.0

EXCLUDED_COLL = [ 'TCRYO' ]