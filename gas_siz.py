from formulae import meta_convert_P_T_FR_L, conver_FR_noise, fLP, fP
from gas_noise_formulae import lpae_1m
from gas_velocity_iec import inletDensity, getGasVelocities
from main import pipeArea, db, N2, Cv_gas, xChoked_gas, fP_gas, sigmaEta_gas, power_level_gas, trimExitVelocityGas, \
    valveSize, valveDetails, getKCValue, xTP_gas, reynoldsNumber, portArea, tex_new


def getOutputsGas(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
                  inletTemp_form,
                  iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl,
                  criticalPressure_form,
                  cPresUnit_form,
                  inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe,
                  sosPipe,
                  valveSize_form, vSizeUnit_form,
                  seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, sg_choice, z_factor, sg_vale):
    fl_unit = fl_unit_form
    if fl_unit in ['m3/hr', 'scfh', 'gpm']:
        fl_bin = 1
    else:
        fl_bin = 2

    sg_unit = sg_choice
    if sg_unit == 'sg':
        sg_bin = 1
    else:
        sg_bin = 2

    def chooses_gas_fun(flunit, sgunit):
        eq_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
        return eq_dict[(flunit, sgunit)]

    sg__ = chooses_gas_fun(fl_bin, sg_bin)

    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()
    thickness_pipe = float(i_pipearea_element.thickness)
    thickness_in = meta_convert_P_T_FR_L('L', thickness_pipe, 'mm', 'inch', 1000)

    if sg__ == 1:
        # to be converted to scfh, psi, R, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'scfh',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'R',
                                          1000)
    elif sg__ == 2:
        # to be converted to m3/hr, kPa, C, in
        # 3. Pressure - 2*thickness_in
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'kpa',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'kpa',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)
    elif sg__ == 3:
        # to be converted to lbhr, psi, F, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        # print(iPipeUnit_form)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'lb/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'F',
                                          1000)
    else:
        # to be converted to kg/hr, bar, K, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'bar',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)

    print(f"dia of pipe: {outletPipeDia}, {inletPipeDia}")

    # python sizing function - gas

    inputDict_4 = {"inletPressure": inletPressure, "outletPressure": outletPressure,
                   "gamma": specificGravity,
                   "C": ratedCV,
                   "valveDia": vSize,
                   "inletDia": inletPipeDia,
                   "outletDia": outletPipeDia, "xT": float(xt_fl),
                   "compressibilityFactor": z_factor,
                   "flowRate": flowrate,
                   "temp": inletTemp, "sg": float(sg_vale), "sg_": sg__}

    print(inputDict_4)

    inputDict = inputDict_4
    N2_val = N2['inch']
    CV__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=CV__[0], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv1 = Cv__[0]

    xChoked = xChoked_gas(gamma=inputDict['gamma'], C=inputDict['C'], valveDia=inputDict['valveDia'],
                          inletDia=inputDict['inletDia'], outletDia=inputDict['outletDia'],
                          xT=inputDict['xT'], N2_value=N2_val)

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    inletPressure_gnoise = float(meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                       'pa',
                                                       1000))
    outletPressure_gnoise = float(meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                        'pa',
                                                        1000))
    # vaporPressure_gnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'pa',
    #                                              1000)
    flowrate_gnoise = conver_FR_noise(flowrate_form, fl_unit)
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    seat_dia_gnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)
    # summation1 = summation(C=113.863, inletPressure=inletPressure_noise, outletPressure=outletPressure_noise, density=specificGravity*1000,
    #                        vaporPressure=vaporPressure_noise,
    #                        speedS=4000, massFlowRate=flowrate_noise, Fd=0.23, densityPipe=7800, speedSinPipe=5000,
    #                        wallThicknessPipe=0.0002, internalPipeDia=inletPipeDia_noise, seatDia=0.1, valveDia=size_noise,
    #                        densityAir=1.293,
    #                        holeDia=0, rW=0.25)

    # molecular weight needs to be made on case to case basis = here we're taking 19.8, but it needs to come from form or table
    mw = float(sg_vale)
    if sg_unit == 'sg':
        mw = 22.4 * float(sg_vale)
    elif sg_unit == 'mw':
        mw = float(sg_vale)

    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)
    flp = fLP(Cv1, valveSize_form, inletPipeDia_form)
    fp = fP_gas(Cv1, valveSize_form, inletPipeDia_form, outletPipeDia_form, N2_val)
    sigmeta = sigmaEta_gas(valveSize_form, inletPipeDia_form, outletPipeDia_form)
    flowrate_gv = int(flowrate_form) / 3600
    inlet_density = inletDensity(inletPressure_gnoise, mw, 8314, temp_gnoise)
    # print('inlet density input:')
    # print(inletPressure_gnoise, mw, 8314, temp_gnoise)
    if sigmeta == 0:
        sigmeta = 0.86
    sc_initial_1 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': 175,
                    'No': 6,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': outletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2, 'Fp': fp,
                    'massFlowrate': flowrate_gnoise, 'massFlowrateUnit': 'kg/s',
                    'iPres': inletPressure_gnoise, 'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': 5.3,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw, 'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}

    sc_initial_2 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': Cv1, 'No': 1,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': inletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2,
                    'Fp': 0.98,
                    'massFlowrate': flowrate_gv, 'massFlowrateUnit': 'kg/s', 'iPres': inletPressure_gnoise,
                    'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': inlet_density,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw,
                    'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}

    sc_initial = sc_initial_2
    # print(sc_initial)

    summation1 = lpae_1m(sc_initial['specificHeatRatio_gamma'], sc_initial['iPres'], sc_initial['oPres'],
                         sc_initial['FLP'],
                         sc_initial['Fp'],
                         sc_initial['inletDensity'], sc_initial['massFlowrate'], sc_initial['aEta'],
                         sc_initial['R'],
                         sc_initial['iAbsTemp'],
                         sc_initial['molecularMass'], sc_initial['oPipeSize'],
                         sc_initial['internalPipeDia'], sc_initial['stp'],
                         sc_initial['No'],
                         sc_initial['A'], sc_initial['Iw'], sc_initial['reqCV'],
                         sc_initial['SpeedOfSoundinPipe_Cs'],
                         sc_initial['SpeedOfSoundInAir_Co'],
                         sc_initial['valveSize'], sc_initial['tS'], sc_initial['fs'],
                         sc_initial['atmPressure_pa'],
                         sc_initial['stdAtmPres_ps'], sc_initial['DensityPipe_Ps'], -3.002)

    print(f"gas summation: {summation1}")
    # summation1 = 97

    # convert flowrate and dias for velocities
    flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                       mw / 22.4)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))

    size_v = round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                         'inch', specificGravity * 1000))

    # get gas velocities
    inletPressure_gv = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa',
                                             1000)
    outletPressure_gv = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa',
                                              1000)
    flowrate_gv = flowrate_form / 3600
    print(f'flowrate_gv: {flowrate_gv}')
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)

    gas_vels = getGasVelocities(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv,
                                8314, temp_gnoise, mw, flowrate_gv,
                                size_gnoise, inletPipeDia_gnoise, outletPipeDia_gnoise)

    # Power Level
    # getting fr in lb/s
    flowrate_p = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                       specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa',
                                            1000)
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                             'pa',
                                             1000)
    pLevel = power_level_gas(specificGravity, inletPressure_p, outletPressure_p, flowrate_p, gas_vels[9])

    # print(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
    #       temp_gnoise, mw, flowrate_gv, size_gnoise,
    #       inletPipeDia_gnoise, outletPipeDia_gnoise)

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa',
                                             1000)
    # get tex pressure in psi
    inletPressure_tex = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'psia',
                                              1000)
    outletPressure_tex = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'psia',
                                               1000)

    tEX = trimExitVelocityGas(inletPressure_tex, outletPressure_tex) / 3.281
    print(
        f"tex: {tEX}, {inletPressure_tex}, {outletPressure_tex}, {inletPressure_tex - outletPressure_tex}")
    # print(summation1)
    iVelocity = gas_vels[6]
    oVelocity = gas_vels[7]
    pVelocity = gas_vels[8]

    data = {'cv': round(Cv1, 3),
            'percent': 83,
            'spl': round(summation1, 3),
            'iVelocity': round(iVelocity, 3),
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(xChoked, 4),
            'texVelocity': round(tEX, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{z_factor}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+mm+mm+{iTempUnit_form}+{sg_choice}"
    # update valve size in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    size_id = db.session.query(valveSize).filter_by(size=size_in_in).first()
    # print(size_id)
    item_selected.size = size_id
    # load case data with item ID
    # get valvetype - kc requirements
    v_det_element = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    valve_type_ = v_det_element.ratedCV
    trimtype = v_det_element.body_v
    outletPressure_psia = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                'psia', 1000)
    inletPressure_psia = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                               'psia', 1000)
    dp_kc = inletPressure_psia - outletPressure_psia
    Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_gas = 0.96
    Fd_gas = 1
    xtp = xTP_gas(inputDict['xT'], inputDict['C'], inputDict['valveDia'], inputDict['inletDia'],
                  inputDict['outletDia'], N2_val)
    N1_val = 0.865
    N4_val = 76000
    inletPressure_re = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar',
                                             1000)
    outletPressure_re = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'bar',
                                              1000)
    inletPipeDia_re = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'mm',
                                                  1000))
    flowrate_re = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                        mw / 22.4)
    RE_number = reynoldsNumber(N4_val, Fd_gas, flowrate_re,
                               1, 0.9, N2_val,
                               inletPipeDia_re, N1_val, inletPressure_re,
                               outletPressure_re,
                               mw / 22400)
    fpgas = fP(inputDict['C'], inputDict['valveDia'], inputDict['inletDia'], inputDict['outletDia'], N2_val)

    mac_sonic_list = [gas_vels[0], gas_vels[1], gas_vels[2],
                      gas_vels[3], gas_vels[4], gas_vels[5], gas_vels[9]]

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, iPresUnit_form, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    # other_factors_string = f"{Ff_gas}+{Kc}+{Fd_gas}+{xtp}+{RE_number}+{fpgas}"
    other_factors_string = f"{Cv__[1]}+{Cv__[2]}+{Cv__[3]}+{Cv__[4]}+{Cv__[5]}+{Cv__[6]}+{Cv__[7]}+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}"
    # print(other_factors_string)
    valve_det_element = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    # tex new
    if valve_det_element.flowCharacter_v == 1:
        flow_character = 'equal'
    else:
        flow_character = 'linear'
        # new trim exit velocity
        # for port area, travel filter not implemented
    port_area_ = db.session.query(portArea).filter_by(v_size=size_in_in, seat_bore=seatDia,
                                                      trim_type=trimtype,
                                                      flow_char=flow_character).first()
    if port_area_:
        port_area = float(port_area_.area)
    else:
        port_area = 1
    tex_ = tex_new(Cv1, ratedCV, port_area, flowrate_re / 3600, inletPressure_v, outletPressure_v, mw,
                   8314, temp_gnoise, 'Gas')

    result_list = [flowrate_form, inletPressure_form, outletPressure_form, inletTemp_form, specificGravity,
                   vaporPressure, viscosity, float(sg_vale), valveSize_form, other_factors_string,
                   round(Cv1, 3), data['percent'], data['spl'], data['iVelocity'], data['oVelocity'],
                   data['pVelocity'], round(data['choked'] * inletPressure_form, 3), float(xt_fl), 1, tex_,
                   pLevel, units_string, None, "Gas", round(criticalPressure_form, 3), inletPipeDia_form,
                   outletPipeDia_form, iSch, oSch, item_selected]

    return result_list





