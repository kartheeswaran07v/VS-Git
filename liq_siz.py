from formulae import meta_convert_P_T_FR_L
from main import db, pipeArea, N1, N2, N4, CV, FF, delPMax, power_level_liquid, valveDetails, trimExitVelocity, \
    reynoldsNumber, flP, getKCValue, valveSize, valveArea, rating, portArea, tex_new, fP
from liquid_noise_formulae import Lpe1m


def getOutputs(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
               inletTemp_form,
               iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form,
               cPresUnit_form,
               inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe,
               valveSize_form, vSizeUnit_form,
               seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected):
    # change into float/ num
    flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form, inletTemp_form, iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form, cPresUnit_form, inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe, valveSize_form, vSizeUnit_form, seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected = float(flowrate_form), fl_unit_form, float(inletPressure_form), iPresUnit_form, float(outletPressure_form), oPresUnit_form, float(inletTemp_form), iTempUnit_form, float(vaporPressure), vPresUnit_form, float(specificGravity), float(viscosity), float(xt_fl), float(criticalPressure_form), cPresUnit_form, float(inletPipeDia_form), iPipeUnit_form, iSch, float(outletPipeDia_form), oPipeUnit_form, oSch, float(densityPipe), float(sosPipe), float(valveSize_form), vSizeUnit_form, float(seatDia), seatDiaUnit, float(ratedCV), float(rw_noise), item_selected

    # check whether flowrate, pres and l are in correct units
    # 1. flowrate
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()
    thickness_pipe = float(i_pipearea_element.thickness)
    print(f"thickness: {thickness_pipe}")
    if fl_unit_form not in ['m3/hr', 'gpm']:
        flowrate_liq = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form,
                                             'm3/hr',
                                             specificGravity * 1000)
        fr_unit = 'm3/hr'
    else:
        fr_unit = fl_unit_form
        flowrate_liq = flowrate_form

    # 2. Pressure
    # A. inletPressure
    if iPresUnit_form not in ['kpa', 'bar', 'psia']:
        inletPressure_liq = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                  'bar', specificGravity * 1000)
        iPres_unit = 'bar'
    else:
        iPres_unit = iPresUnit_form
        inletPressure_liq = inletPressure_form

    # B. outletPressure
    if oPresUnit_form not in ['kpa', 'bar', 'psia']:
        outletPressure_liq = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                   'bar', specificGravity * 1000)
        oPres_unit = 'bar'
    else:
        oPres_unit = oPresUnit_form
        outletPressure_liq = outletPressure_form

    # C. vaporPressure
    if vPresUnit_form not in ['kpa', 'bar', 'psia']:
        vaporPressure = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'bar',
                                              specificGravity * 1000)
        vPres_unit = 'bar'
    else:
        vPres_unit = vPresUnit_form

    # D. Critical Pressure
    if cPresUnit_form not in ['kpa', 'bar', 'psia']:
        criticalPressure_liq = meta_convert_P_T_FR_L('P', criticalPressure_form,
                                                     cPresUnit_form, 'bar',
                                                     specificGravity * 1000)
        cPres_unit = 'bar'
    else:
        cPres_unit = cPresUnit_form
        criticalPressure_liq = criticalPressure_form

    # 3. Length
    if iPipeUnit_form not in ['mm']:
        inletPipeDia_liq = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form,
                                                 'mm',
                                                 specificGravity * 1000) - 2 * thickness_pipe
        iPipe_unit = 'mm'
    else:
        iPipe_unit = iPipeUnit_form
        inletPipeDia_liq = inletPipeDia_form - 2 * thickness_pipe

    if oPipeUnit_form not in ['mm']:
        outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                                  'mm', specificGravity * 1000) - 2 * thickness_pipe
        oPipe_unit = 'mm'
    else:
        oPipe_unit = oPipeUnit_form
        outletPipeDia_liq = outletPipeDia_form - 2 * thickness_pipe

    if vSizeUnit_form not in ['mm']:
        vSize_liq = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)
        vSize_unit = 'mm'
    else:
        vSize_unit = vSizeUnit_form
        vSize_liq = valveSize_form

    print(f"dia of pipe: {outletPipeDia_liq}, {inletPipeDia_liq}")

    service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                             'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                             'iPresUnit': iPres_unit,
                             'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                             'temp_unit': iTempUnit_form, 'sGravity': specificGravity,
                             'iPipeDia': inletPipeDia_liq,
                             'oPipeDia': outletPipeDia_liq,
                             'valveDia': vSize_liq, 'iPipeDiaUnit': iPipe_unit,
                             'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': vSize_unit,
                             'C': ratedCV, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl, 'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': 1, 'viscosity': viscosity}
    print(service_conditions_sf)

    service_conditions_1 = service_conditions_sf
    N1_val = N1[(service_conditions_1['flowrate_unit'], service_conditions_1['iPresUnit'])]
    N2_val = N2[service_conditions_1['valveDiaUnit']]
    N4_val = N4[(service_conditions_1['flowrate_unit'], service_conditions_1['valveDiaUnit'])]

    result_1 = CV(service_conditions_1['flowrate'], service_conditions_1['C'],
                  service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'],
                  service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                  service_conditions_1['oPres'],
                  service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                  service_conditions_1['vPres'],
                  service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                  service_conditions_1['viscosity'], thickness_pipe)

    result = CV(service_conditions_1['flowrate'], result_1,
                service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'],
                service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                service_conditions_1['oPres'],
                service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                service_conditions_1['vPres'],
                service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                service_conditions_1['viscosity'], thickness_pipe)
    ff_liq = FF(service_conditions_1['vPres'], service_conditions_1['cPres'])
    chokedP = delPMax(service_conditions_1['Fl'], ff_liq, service_conditions_1['iPres'],
                      service_conditions_1['vPres'])
    # chokedP = selectDelP(service_conditions_1['Fl'], service_conditions_1['cPres'],
    #                      service_conditions_1['iPres'],
    #                      service_conditions_1['vPres'], service_conditions_1['oPres'])

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    # convert form data in units of noise formulae
    valveDia_lnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'm', 1000)
    iPipeDia_lnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                            1000)
    oPipeDia_lnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'm',
                                            1000)
    seat_dia_lnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()

    iPipeSch_lnoise = meta_convert_P_T_FR_L('L', float(i_pipearea_element.thickness),
                                            'mm', 'm', 1000)
    flowrate_lnoise = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                            specificGravity * 1000) / 3600
    outletPressure_lnoise = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                  'pa', 1000)
    inletPressure_lnoise = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                 'pa', 1000)
    vPres_lnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'pa', 1000)
    # print(f"3 press: {outletPressure_lnoise, inletPressure_lnoise, vPres_lnoise}")
    # service conditions for 4 inch vale with 8 as line size. CVs need to be changed
    sc_liq_sizing = {'valveDia': valveDia_lnoise, 'ratedCV': ratedCV, 'reqCV': result, 'FL': xt_fl,
                     'FD': 0.42,
                     'iPipeDia': iPipeDia_lnoise, 'iPipeUnit': 'm', 'oPipeDia': oPipeDia_lnoise,
                     'oPipeUnit': 'm',
                     'internalPipeDia': oPipeDia_lnoise,
                     'inPipeDiaUnit': 'm', 'pipeWallThickness': iPipeSch_lnoise, 'speedSoundPipe': sosPipe,
                     'speedSoundPipeUnit': 'm/s',
                     'densityPipe': densityPipe, 'densityPipeUnit': 'kg/m3', 'speedSoundAir': 343,
                     'densityAir': 1293,
                     'massFlowRate': flowrate_lnoise, 'massFlowRateUnit': 'kg/s',
                     'iPressure': inletPressure_lnoise,
                     'iPresUnit': 'pa',
                     'oPressure': outletPressure_lnoise,
                     'oPresUnit': 'pa', 'vPressure': vPres_lnoise, 'densityLiq': specificGravity * 1000,
                     'speedSoundLiq': 1400,
                     'rw': rw_noise,
                     'seatDia': seat_dia_lnoise,
                     'fi': 8000}

    sc_1 = sc_liq_sizing
    summation = Lpe1m(sc_1['fi'], sc_1['FD'], sc_1['reqCV'], sc_1['iPressure'], sc_1['oPressure'],
                      sc_1['vPressure'],
                      sc_1['densityLiq'], sc_1['speedSoundLiq'], sc_1['massFlowRate'], sc_1['rw'],
                      sc_1['FL'],
                      sc_1['seatDia'], sc_1['valveDia'], sc_1['densityPipe'], sc_1['pipeWallThickness'],
                      sc_1['speedSoundPipe'],
                      sc_1['densityAir'], sc_1['internalPipeDia'], sc_1['speedSoundAir'],
                      sc_1['speedSoundPipe'])
    # summation = 56

    # Power Level
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                             'psia', specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                            'psia', specificGravity * 1000)
    pLevel = power_level_liquid(inletPressure_p, outletPressure_p, specificGravity, result)

    # convert flowrate and dias for velocities
    flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                       1000)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))
    vSize_v = round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'inch', specificGravity * 1000))

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'bar',
                                             1000)
    v_det_element = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    trimtype = v_det_element.body_v
    if trimtype == 'contour':
        t_caps = 'Contoured'
    elif trimtype == 'ported':
        t_caps = 'Cage'
    else:
        t_caps = 'other'

    tEX = trimExitVelocity(inletPressure_v, outletPressure_v, 1000 * specificGravity, t_caps,
                           'other')
    if v_det_element.flowCharacter_v == 1:
        flow_character = 'equal'
    else:
        flow_character = 'linear'
    # new trim exit velocity
    # for port area, travel filter not implemented

    port_area_ = db.session.query(portArea).filter_by(v_size=vSize_v, seat_bore=seatDia, trim_type=trimtype,
                                                      flow_char=flow_character).first()

    if port_area_:
        port_area = float(port_area_.area)
    else:
        port_area = 1
    tex_ = tex_new(result, ratedCV, port_area, flowrate_v / 3600, inletPressure_form, inletPressure_form, 1, 8314,
                   inletTemp_form, 'Liquid')

    # ipipeSch_v = meta_convert_P_T_FR_L('L', float(iPipeSch_form), iPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # opipeSch_v = meta_convert_P_T_FR_L('L', float(oPipeSch_form), oPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v, inletPipeDia_v,
    #                                               outletPipeDia_v,
    #                                               vSize_v)
    # print(flowrate_v, (inletPipeDia_v - ipipeSch_v),
    #       (outletPipeDia_v - opipeSch_v),
    #       vSize_v)
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()
    area_in2 = float(i_pipearea_element.area)
    a_i = 0.00064516 * area_in2
    iVelocity = flowrate_v / (3600 * a_i)

    o_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(outletPipeDia_v),
                                                              schedule=oSch).first()
    print(f"oPipedia: {outletPipeDia_v}, sch: {oSch}")
    area_in22 = float(o_pipearea_element.area)
    a_o = 0.00064516 * area_in22
    oVelocity = flowrate_v / (3600 * a_o)

    valve_element_current = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    rating_current = db.session.query(rating).filter_by(id=valve_element_current.rating).first()
    valvearea_element = db.session.query(valveArea).filter_by(rating=rating_current.size,
                                                              nominalPipeSize=vSize_v).first()
    v_area_in = float(valvearea_element.area)
    v_area = 0.00064516 * v_area_in
    pVelocity = flowrate_v / (3600 * v_area)

    data = {'cv': round(result, 3),
            'percent': 80,
            'spl': round(summation, 3),
            'iVelocity': iVelocity,
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(chokedP, 3),
            'texVelocity': round(tEX, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{rw_noise}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{vPresUnit_form}+{cPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+mm+mm+{iTempUnit_form}+sg"
    # update valve size in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    size_id = db.session.query(valveSize).filter_by(size=size_in_in).first()
    print(size_id)
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

    print(f"kc inputs: {size_in_in}, {trimtype}, {dp_kc}, {valve_type_.lower()}, {xt_fl},")
    Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)
    print(f"kc inputs: {size_in_in}, {trimtype}, {dp_kc}, {valve_type_.lower()}, {xt_fl}, {Kc}")

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_liq = round(FF(service_conditions_1['vPres'], service_conditions_1['cPres']), 2)
    Fd_liq = service_conditions_1['FD']
    FLP_liq = flP(result_1, service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'], N2_val,
                  service_conditions_1['Fl'])
    RE_number = reynoldsNumber(N4_val, service_conditions_1['FD'], service_conditions_1['flowrate'],
                               service_conditions_1['viscosity'], service_conditions_1['Fl'], N2_val,
                               service_conditions_1['iPipeDia'], N1_val, service_conditions_1['iPres'],
                               service_conditions_1['oPres'],
                               service_conditions_1['sGravity'])
    fp_liq = fP(result_1, service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'], service_conditions_1['oPipeDia'], N2_val)
    if chokedP == (service_conditions_1['iPres'] - service_conditions_1['oPres']):
        ff = 0.96
    else:
        ff = round(ff_liq, 3)

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, vPres_unit, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    print(
        f"AR facts: {inletPressure_form}, {outletPressure_form}, {inletPressure_form}, {vp_ar}, {vaporPressure}, {vPres_unit}")
    other_factors_string = f"{ff}+{Kc}+{Fd_liq}+{FLP_liq}+{RE_number}+{fp_liq}+{round(application_ratio, 3)}"

    result_list = [flowrate_form, inletPressure_form, outletPressure_form, inletTemp_form, specificGravity,
                   vaporPressure, viscosity, None,
                   valveSize_form, other_factors_string, round(result, 3), data['percent'],
                   round(summation, 3), round(iVelocity, 3),
                   round(oVelocity, 3), round(pVelocity, 3),
                   round(chokedP, 4), xt_fl, 1, tex_, pLevel, units_string, None, "Liquid",
                   criticalPressure_form, inletPipeDia_form,
                   outletPipeDia_form, iSch, oSch,
                   item_selected]

    return result_list
