import datetime

import pandas
# import pandas
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Float, or_
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import DetachedInstanceError
import math
import csv
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
# import pandas
from formulae import *
from liquid_noise_formulae import Lpe1m
from gas_noise_formulae import lpae_1m
from gas_velocity_iec import getGasVelocities, inletDensity
import os
from specsheet import createSpecSheet

# -----------^^^^^^^^^^^^^^----------------- IMPORT STATEMENTS -----------------^^^^^^^^^^^^^------------ #


## Constants
# todo = Constants
N5_mm = 0.00241  # in mm
N5_in = 1000
N6_kghr_kPa_kgm3 = 2.73
N6_kghr_bar_kgm3 = 27.3
N6_lbhr_psi_lbft3 = 63.3
N7_O_m3hr_kPa_C = 3.94  # input in Kelvin
N7_0_m3hr_bar_C = 394
N7_155_m3hr_kPa_C = 4.17
N7_155_m3hr_bar_C = 417
N7_60_scfh_psi_F = 1360  # input in R
N8_kghr_kPa_K = 0.498
N8_kghr_bar_K = 94.8
N8_lbhr_psi_K = 19.3
N9_O_m3hr_kPa_C = 21.2  # input in Kelvin
N9_0_m3hr_bar_C = 2120
N9_155_m3hr_kPa_C = 22.4
N9_155_m3hr_bar_C = 2240
N9_60_scfh_psi_F = 7320  # input in R

N1 = {('m3/hr', 'kpa'): 0.0865, ('m3/hr', 'bar'): 0.865, ('gpm', 'psia'): 1}
N2 = {'mm': 0.00214, 'inch': 890}
N4 = {('m3/hr', 'mm'): 76000, ('gpm', 'inch'): 173000}

# FR values for 56-40000

REv = [56, 66, 79, 94, 110, 130, 154, 188, 230, 278, 340, 471, 620, 980, 1560, 2470, 4600, 10200, 40000]
FR = [0.284, 0.32, 0.36, 0.4, 0.44, 0.48, 0.52, 0.56, 0.6, 0.64, 0.68, 0.72, 0.76, 0.8, 0.84, 0.88, 0.92, 0.96, 1]

# app configuration
app = Flask(__name__)

app.config['SECRET_KEY'] = "kkkkk"

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fcc_filled_db_v3.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# TODO ------------------------------------------ DB TABLE CREATION --------------------------------------- #

# CREATE TABLE IN DB
# class User(UserMixin, db.Model):
#     __tablename__ = "Users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String(100), unique=True)
#     password = Column(String(100))
#     name = Column(String(1000))
#
#     # relationships
#     # TODO 1 - Employee Master
#     employee = relationship("employeeMaster", back_populates="user")
#     # TODO 2 - roster Master
#     roster = relationship("rosterMaster", back_populates="user")
#     # TODO 3 - Time sheet master
#     timesheet = relationship("timesheetMaster", back_populates="user")
#     # TODO 4 - Leave Appln Master
#     leave = relationship("leaveApplicationMaster", back_populates="user")
#     # TODO 5 - Passport Appln Master
#     passport = relationship("passportApplicationMaster", back_populates="user")
#


# 1
class projectMaster(db.Model):
    __tablename__ = "projectMaster"
    id = Column(Integer, primary_key=True)
    quote = Column(Integer)
    received_date = Column(DateTime)
    work_order = Column(Integer)
    due_date = Column(DateTime)
    # relationship as parent
    item = relationship("itemMaster", back_populates="project")
    # relationship as child
    # TODO - Industry
    IndustryId = Column(Integer, ForeignKey("industryMaster.id"))
    industry = relationship("industryMaster", back_populates="project")
    # TODO - Region
    regionID = Column(Integer, ForeignKey("regionMaster.id"))
    region = relationship("regionMaster", back_populates="project")
    # TODO - Status
    statusID = Column(Integer, ForeignKey("statusMaster.id"))
    status = relationship("statusMaster", back_populates="project")
    # TODO - Customer
    customerID = Column(Integer, ForeignKey("customerMaster.id"))
    customer = relationship("customerMaster", back_populates="project")
    # TODO - Engineer
    engineerID = Column(Integer, ForeignKey("engineerMaster.id"))
    engineer = relationship("engineerMaster", back_populates="project")


# 2
class industryMaster(db.Model):  # TODO - Paandi ----- Done
    __tablename__ = "industryMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="industry")


# 3
class regionMaster(db.Model):  # TODO - Paandi  ------ Done
    __tablename__ = "regionMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="region")


# 4
class statusMaster(db.Model):  # TODO - Paandi     --------Done
    __tablename__ = "statusMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="status")


# 5
class customerMaster(db.Model):  # TODO - Paandi
    __tablename__ = "customerMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="customer")


# 6
class engineerMaster(db.Model):  # TODO - Paandi
    __tablename__ = "engineerMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="engineer")


# 7
class itemMaster(db.Model):
    __tablename__ = "itemMaster"
    id = Column(Integer, primary_key=True)
    alt = Column(String(300))
    tag_no = Column(String(300))
    unit_price = Column(String(300))
    qty = Column(String(300))
    # relationship as parent
    cases = relationship("itemCases", back_populates="item")
    valveDetails = relationship("valveDetails", back_populates="item")
    # relationship as child
    # TODO - Project
    projectID = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="item")
    # TODO - Serial
    serialID = Column(Integer, ForeignKey("valveSeries.id"))
    serial = relationship("valveSeries", back_populates="item")
    # TODO - Size
    sizeID = Column(Integer, ForeignKey("valveSize.id"))
    size = relationship("valveSize", back_populates="item")
    # TODO - Model
    modelID = Column(Integer, ForeignKey("modelMaster.id"))
    model = relationship("modelMaster", back_populates="item")
    # TODO - Type
    typeID = Column(Integer, ForeignKey("valveStyle.id"))
    type = relationship("valveStyle", back_populates="item")
    # TODO - Rating
    ratingID = Column(Integer, ForeignKey("rating.id"))
    rating = relationship("rating", back_populates="item")
    # TODO - Material
    materialID = Column(Integer, ForeignKey("materialMaster.id"))
    material = relationship("materialMaster", back_populates="item")


# 8
class modelMaster(db.Model):  # TODO - Paandi
    __tablename__ = "modelMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="model")


# 9
class valveSeries(db.Model):  # TODO - Paandi        -------Done
    __tablename__ = "valveSeries"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="serial")


# 10
class valveStyle(db.Model):  # TODO - Paandi
    __tablename__ = "valveStyle"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="type")


# 11
class valveSize(db.Model):  # TODO - Paandi
    __tablename__ = "valveSize"
    id = Column(Integer, primary_key=True)
    size = Column(Integer)  # in inches

    # relationship as master
    item = relationship("itemMaster", back_populates="size")


# 12
class rating(db.Model):  # TODO - Paandi
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True)
    size = Column(Integer)  # in inches

    # relationship as master
    item = relationship("itemMaster", back_populates="rating")


# 13
class materialMaster(db.Model):
    __tablename__ = "materialMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    max_temp = Column(Integer)
    min_temp = Column(Integer)

    # relationship as master
    item = relationship("itemMaster", back_populates="material")


# 13A
class itemCases(db.Model):
    __tablename__ = "itemCases"
    id = Column(Integer, primary_key=True)
    flowrate = Column(Integer)
    iPressure = Column(Integer)
    oPressure = Column(Integer)
    iTemp = Column(Integer)
    sGravity = Column(Integer)
    vPressure = Column(Integer)
    viscosity = Column(Integer)
    vaporMW = Column(Integer)
    vaporInlet = Column(Integer)
    vaporOutlet = Column(Integer)
    CV = Column(Integer)
    openPercent = Column(Integer)
    valveSPL = Column(Integer)
    iVelocity = Column(Integer)
    oVelocity = Column(Integer)
    pVelocity = Column(Integer)
    chokedDrop = Column(Integer)
    Xt = Column(Integer)
    warning = Column(Integer)
    trimExVelocity = Column(Integer)
    sigmaMR = Column(Integer)
    reqStage = Column(Integer)
    fluidName = Column(String(200))
    fluidState = Column(Integer)
    criticalPressure = Column(Integer)
    iPipeSize = Column(Integer)
    iPipeSizeSch = Column(Integer)
    oPipeSize = Column(Integer)
    oPipeSizeSch = Column(Integer)

    # relationship as child
    itemID = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship("itemMaster", back_populates="cases")


# 13B
class valveDetails(db.Model):
    __tablename__ = "valveDetails"
    id = Column(Integer, primary_key=True)
    # Valve Identification
    tag = Column(String(300))
    quantity = Column(Integer)
    application = Column(String(300))
    serial_no = Column(Integer)

    # Pressure Temp rating
    rating = Column(String(300))
    body_material = Column(String(300))
    shutOffDelP = Column(Integer)
    maxPressure = Column(Integer)
    maxTemp = Column(Integer)
    minTemp = Column(Integer)

    # Valve Selection
    valve_series = Column(String(300))
    valve_size = Column(Integer)
    rating_v = Column(String(300))
    ratedCV = Column(Integer)
    endConnection_v = Column(String(300))
    endFinish_v = Column(String(300))
    bonnetType_v = Column(String(300))
    bonnetExtDimension = Column(String(300))
    packingType_v = Column(String(300))
    trimType_v = Column(String(300))
    flowCharacter_v = Column(String(300))
    flowDirection_v = Column(String(300))
    seatLeakageClass_v = Column(String(300))

    # Material Selection
    body_v = Column(String(300))
    bonnet_v = Column(String(300))
    nde1 = Column(String(300))
    nde2 = Column(String(300))
    plug = Column(String(300))
    stem = Column(String(300))
    seat = Column(String(300))
    cage_clamp = Column(String(300))
    balanceScale = Column(String(300))
    packing = Column(String(300))
    stud_nut = Column(String(300))
    gasket = Column(String(300))

    # relationship as child
    itemID = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship("itemMaster", back_populates="valveDetails")


# 14
class standardMaster(db.Model):  # TODO - Paandi    ----------Done
    __tablename__ = "standardMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 15
class fluidType(db.Model):  # TODO - Paandi     -------Done
    __tablename__ = "fluidType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 16
class applicationMaster(db.Model):  # TODO - Paandi    -----------Done
    __tablename__ = "applicationMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 17 - rated cv - to be integrated

# 18
class endConnection(db.Model):  # TODO - Paandi    ----------Done
    __tablename__ = "endConnection"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 19
class endFinish(db.Model):  # TODO - Paandi      -------------Done
    __tablename__ = "endFinish"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 20
class bonnetType(db.Model):  # TODO - Paandi  -----------------Done
    __tablename__ = "bonnetType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 21
class packingType(db.Model):  # TODO - Paandi
    __tablename__ = "packingType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 21A
class packingMaterial(db.Model):  # TODO - Paandi     -----------Done
    __tablename__ = "packingMaterial"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 22
class trimType(db.Model):  # TODO - Paandi  -----------Done
    __tablename__ = "trimType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 23
class flowDirection(db.Model):  # TODO - Paandi  ............Done
    __tablename__ = "flowDirections"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 24
class seatLeakageClass(db.Model):  # TODO - Paandi    ..........Done
    __tablename__ = "seatLeakageClass"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 25
class bodyBonnet(db.Model):  # NDE  # TODO - Paandi
    __tablename__ = "bodyBonnet"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 26
class softPartsMaterial(db.Model):  # TODO - Paandi            ................Done
    __tablename__ = "softPartsMaterial"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 27
class fluidName(db.Model):  # TODO - Paandi          ----------------Done
    __tablename__ = "fluidName"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 28
class valveBalancing(db.Model):  # TODO - Paandi      --------------Done
    __tablename__ = "valveBalancing"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 29
class actuatorSeries(db.Model):  # TODO - Paandi          __________Done
    __tablename__ = "actuatorSeries"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 30
class actuatorSize(db.Model):  # TODO - Paandi
    __tablename__ = "actuatorSize"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 31
class handweel(db.Model):  # TODO - Paandi        ..........Done
    __tablename__ = "handweel"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 32
class travelStops(db.Model):  # TODO - Paandi       .............Done
    __tablename__ = "travelStops"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 33
class butterflyTable(db.Model):
    __tablename__ = "butterflyTable"
    id = Column(Integer, primary_key=True)
    typeID = Column(Integer)  # double or triple offset
    ratingID = Column(Integer)  # 150, 300, 600
    coeffID = Column(Integer)  # Cv, FL, Xt, FD
    size = Column(Integer)  # 3-30
    one = Column(Integer)  # All below are opening percentage
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)


# 34
class globeTable(db.Model):  # series 1000
    __tablename__ = "globeTable"
    id = Column(Integer, primary_key=True)
    trimTypeID = Column(Integer)  # Microspline, contoured, ported, mhc-1
    flow = Column(Integer)  # over, under, both
    coeffID = Column(Integer)  # Cv, FL, Xt, FD
    size = Column(Integer)  # 1-24
    charac = Column(Integer)  # linear, equal%
    one = Column(Integer)  # All below are opening percentage
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)
    ten = Column(Integer)


# 35
class schedule(db.Model):  # TODO - Paandi      ----------Done
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 36
class failAction(db.Model):  # TODO - Paandi  ----------Done
    __tablename__ = "failAction"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 37
class positionerMakeModel(db.Model):  # TODO - Paandi  ................Done
    __tablename__ = "positionerMakeModel"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 38
class airset(db.Model):  # TODO - Paandi           ................Done
    __tablename__ = "airset"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 39
class solenoidValve(db.Model):  # TODO - Paandi     ............Done
    __tablename__ = "solenoidValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 40
class lockValve(db.Model):  # TODO - Paandi          ............done
    __tablename__ = "lockValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 41
class qevBoosters(db.Model):  # TODO - Paandi        ...........Done
    __tablename__ = "qevBoosters"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 42
class pilotValve(db.Model):  # TODO - Paandi       ...........Done
    __tablename__ = "pilotValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 43
class switchPosition(db.Model):  # TODO - Paandi        ........DOne
    __tablename__ = "switchPosition"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 44
class IPConverter(db.Model):  # TODO - Paandi        -----------Done
    __tablename__ = "IPConverter"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 45
class airReceiver(db.Model):  # TODO - Paandi       ------------Done
    __tablename__ = "sirReceiver"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 46
class tubing(db.Model):  # TODO - Paandi            ----------------Done
    __tablename__ = "tubing"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 47
class fittings(db.Model):  # TODO - Paandi     ---------------Done
    __tablename__ = "fittings"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 48
class cleaning(db.Model):  # TODO - Paandi     .....................Done
    __tablename__ = "cleaning"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 49
class certification(db.Model):  # TODO - Paandi          --------------Done
    __tablename__ = "certification"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 50
class paintFinish(db.Model):  # TODO - Paandi       -------------------Done

    __tablename__ = "paintFinish"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 51
class paintCerts(db.Model):  # TODO - Paandi        .................Done

    __tablename__ = "paintCerts"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 52
class pipeArea(db.Model):  # TODO - Paandi        .................Done

    __tablename__ = "pipeArea"
    id = Column(Integer, primary_key=True)
    nominalDia = Column(String(300))
    nominalPipeSize = Column(String(300))
    outerDia = Column(String(300))
    schedule = Column(String(300))
    thickness = Column(String(300))
    area = Column(String(300))


# 53
class valveArea(db.Model):  # TODO - Paandi        .................Done

    __tablename__ = "valveArea"
    id = Column(Integer, primary_key=True)
    rating = Column(String(300))
    nominalPipeSize = Column(String(300))
    inMM = Column(String(300))
    inInch = Column(String(300))
    area = Column(String(300))


# 54
class kcTable(db.Model):  # TODO - Paandi        .................Done

    __tablename__ = "kcTable"
    id = Column(Integer, primary_key=True)
    valve_style = Column(String(300))
    min_size = Column(String(300))
    max_size = Column(String(300))
    trim_material = Column(String(300))
    trim_type = Column(String(300))
    min_pres = Column(String(300))
    max_pres = Column(String(300))
    kc_formula = Column(String(300))
    dummy1 = Column(String(300))
    dummy2 = Column(String(300))


# 55
class packingFriction(db.Model):
    __tablename__ = "packingFriction"
    id = Column(Integer, primary_key=True)
    stemDia = Column(String(20))
    pressure = Column(String(20))
    ptfe1 = Column(String(20))
    ptfe2 = Column(String(20))
    ptfer = Column(String(20))
    graphite = Column(String(20))


# 56
class seatLoad(db.Model):
    __tablename__ = "seatLoad"
    id = Column(Integer, primary_key=True)
    trimtype = Column(String(20))
    seatBore = Column(String(20))
    two = Column(String(20))
    three = Column(String(20))
    four = Column(String(20))
    five = Column(String(20))
    six = Column(String(20))


# 57
class actuatorData(db.Model):
    __tablename__ = "actuatorData"
    id = Column(Integer, primary_key=True)
    acSize = Column(String(20))
    travel = Column(String(20))
    sMin = Column(String(20))
    sMax = Column(String(20))
    failAction = Column(String(20))
    rate = Column(String(20))
    SFMin = Column(String(20))
    SFMax = Column(String(20))
    NATMax = Column(String(20))
    NATMin = Column(String(20))


# 57A
class actuatorDataVol(db.Model):
    __tablename__ = "actuatorDataVol"
    id = Column(Integer, primary_key=True)
    acSize = Column(String(20))
    travel = Column(String(20))
    sMin = Column(String(20))
    sMax = Column(String(20))
    failAction = Column(String(20))
    rate = Column(String(20))
    SFMin = Column(String(20))
    SFMax = Column(String(20))
    NATMax = Column(String(20))
    NATMin = Column(String(20))
    VM = Column(String(20))
    VO = Column(String(20))


# 58
class valveTypeMaterial(db.Model):
    __tablename__ = "valveTypeMaterial"
    id = Column(Integer, primary_key=True)
    data = Column(String(20))
    valveType = Column(String(20))
    name = Column(String(100))


# 59
class knValue(db.Model):
    __tablename__ = "knValue"
    id = Column(Integer, primary_key=True)
    portDia = Column(String(20))
    flowDir = Column(String(20))
    flowCharac = Column(String(100))
    trimType = Column(String(100))
    kn = Column(String(100))


# 60
class portArea(db.Model):
    __tablename__ = "portArea"
    id = Column(Integer, primary_key=True)
    model = Column(String(20))
    v_size = Column(String(20))
    seat_bore = Column(String(20))
    travel = Column(String(20))
    trim_type = Column(String(20))
    flow_char = Column(String(20))
    area = Column(String(20))


# 61
class hwThrust(db.Model):
    __tablename__ = "hwThrust"
    id = Column(Integer, primary_key=True)
    failAction = Column(String(20))
    mount = Column(String(20))
    ac_size = Column(String(20))
    max_thrust = Column(String(20))
    dia = Column(String(20))


# 62
class fluidDetails(db.Model):
    __tablename__ = "fluidDetails"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    specific_gravity = Column(Float)
    vapour_pressure = Column(Float)
    viscosity = Column(Float)
    critical_pressure = Column(Float)
    molecular_weight = Column(Float)
    specific_heat_ration = Column(Float)
    compressibility_factor = Column(Float)


# 63


#
# with app.app_context():
#     db.create_all()

# TODO ------------------------------------------ DATA INPUT TO THE DATABASE --------------------------------------- #

with app.app_context():
    # projects
    industry_element_1 = industryMaster.query.get(16)
    region_element_1 = regionMaster.query.get(2)
    status_element_1 = statusMaster.query.get(6)
    customer_element_1 = customerMaster.query.get(1)
    engineer_element_1 = engineerMaster.query.get(2)
    industry_element_2 = industryMaster.query.get(1)
    region_element_2 = regionMaster.query.get(1)
    status_element_2 = statusMaster.query.get(1)
    customer_element_2 = customerMaster.query.get(2)
    engineer_element_2 = engineerMaster.query.get(3)

    # items
    # 1
    project_element_1 = projectMaster.query.get(1)
    valve_series_element_1 = valveSeries.query.get(1)
    valve_size_element_1 = valveSize.query.get(1)
    model_element_1 = modelMaster.query.get(1)
    type_element_1 = valveStyle.query.get(1)
    rating_element_1 = rating.query.get(1)
    material_element_1 = materialMaster.query.get(2)
    # 2
    project_element_2 = projectMaster.query.get(2)
    valve_series_element_2 = valveSeries.query.get(2)
    valve_size_element_2 = valveSize.query.get(5)
    model_element_2 = modelMaster.query.get(3)
    type_element_2 = valveStyle.query.get(2)
    rating_element_2 = rating.query.get(3)
    material_element_2 = materialMaster.query.get(6)
    # 3
    valve_size_element_3 = valveSize.query.get(4)
    rating_element_3 = rating.query.get(2)
project2 = {"Industry": industry_element_1, "Region": region_element_1, "Qoute": 502, "Status": status_element_1,
            "Customer": customer_element_1, "Enquiry": 000,
            "received": datetime.datetime.today().date(), "Engineer": engineer_element_1,
            "Due Date": datetime.datetime.today().date(),
            "WorkOrder": 000}
project1 = {"Industry": industry_element_2, "Region": region_element_2, "Qoute": 501, "Status": status_element_2,
            "Customer": customer_element_2, "Enquiry": 000,
            "received": datetime.datetime.today().date(), "Engineer": engineer_element_2,
            "Due Date": datetime.datetime.today().date(),
            "WorkOrder": 000}
projectsList = [project1, project2]

# # add projects to db
# for i in projectsList:
#     new_project = projectMaster(industry=i['Industry'], region=i['Region'], quote=i['Qoute'], status=i['Status'],
#                                 customer=i['Customer'],
#                                 received_date=i['received'],
#                                 engineer=i['Engineer'],
#                                 work_order=i['WorkOrder'],
#                                 due_date=i['Due Date'])
#     with app.app_context():
#         db.session.add(new_project)
#         db.session.commit()


# add items in projects

item1 = {"alt": 'A', "tagNo": 101, "serial": valve_series_element_1, "size": valve_size_element_1,
         "model": model_element_1, "type": type_element_1, "rating": rating_element_1,
         "material": material_element_1, "unitPrice": 1, "Quantity": 2, "Project": project_element_1}
item2 = {"alt": 'A', "tagNo": 102, "serial": valve_series_element_2, "size": valve_size_element_2,
         "model": model_element_2, "type": type_element_2, "rating": rating_element_2,
         "material": material_element_2, "unitPrice": 3, "Quantity": 4, "Project": project_element_2}
item3 = {"alt": 'A', "tagNo": 102, "serial": valve_series_element_2, "size": valve_size_element_3,
         "model": model_element_2, "type": type_element_1, "rating": rating_element_3,
         "material": material_element_2, "unitPrice": 3, "Quantity": 4, "Project": project_element_2}

itemsList = [item3]
#
# for i in itemsList:
#     new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'], model=i['model'],
#                           type=i['type'], rating=i['rating'], material=i['material'], unit_price=i['unitPrice'],
#                           qty=i['Quantity'], project=i['Project'])
#     with app.app_context():
#         db.session.add(new_item)
#         db.session.commit()

# # add csv globe data to db
# filename = "valveTypeMaterials.csv"
# fields = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
# #
# for row in rows:
#     new_entry_globe = valveTypeMaterial(valveType=row[1], data=row[2], name=row[3])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# Add Fluid Properties
# filename = "fluid_properties.csv"
# fields = []
# rows = []
# #
# # # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
# #
# for row in rows:
#     new_entry_globe = fluidDetails(name=row[1], specific_gravity=row[2], vapour_pressure=row[3], viscosity=row[4],
#                                    critical_pressure=row[5], molecular_weight=row[6], specific_heat_ration=row[7],
#                                    compressibility_factor=row[8])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# add pipe data
# filename = "actuator_data_new.csv"
# fields_p = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_p = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = actuatorDataVol(acSize=row[4], travel=row[6], sMin=row[7], sMax=row[8],
#                                       failAction=row[1], rate=row[9], SFMin=row[0], SFMax=row[2], NATMax=row[3],
#                                       NATMin=row[5], VM=row[10], VO=row[11])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# with app.app_context():
#     act_data = actuatorData.query.all()
#     for i in act_data:
#         if i.id < 216:
#             i.SFMin = 'sd'
#             db.session.commit()
# filename = "valvearea.csv"
# fields_p = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_p = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = valveArea(rating=row[0], nominalPipeSize=row[1], inMM=row[2], inInch=row[3],
#                                area=row[4])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# seat load update:
# filename = "seat_force2.csv"
# fields_p = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_p = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = seatLoad(trimtype=row[0], seatBore=row[1], two=row[2], three=row[3],
#                                four=row[4], five=row[5], six=row[6])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# handwheel thrust

# filename = "handwheel.csv"
# fields_hw = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_hw = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = hwThrust(failAction=row[0], mount=row[1], ac_size=row[2], max_thrust=row[3],
#                                dia=row[4])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()
#
# # port _area
# filename = "port_area.csv"
# fields_pa = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_pa = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = portArea(model=row[0], v_size=row[1], seat_bore=row[2], travel=row[3],
#                                trim_type=row[4], flow_char=row[5], area=row[6])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# Add KC table
# filename = "kc_table.csv"
# fields_kc = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_kc = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = kcTable(valve_style=row[0], min_size=row[1], max_size=row[2], trim_material=row[3],
#                               trim_type=row[4], min_pres=row[5], max_pres=row[6], kc_formula=row[7],
#                               dummy1=None, dummy2=None)
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()


# KN Value for balanced under
# filename = "kn_value.csv"
# fields_kn = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_kn = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# for row in rows:
#     new_entry_globe = knValue(portDia=row[0], flowDir=row[1], flowCharac=row[2], trimType=row[3],
#                               kn=row[4])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()

# filename = "kc_table.csv"
# fields_kc = []
# rows = []
#
# # reading csv file
# with open(filename, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_kc = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows.append(row)
#
# kc_dict_list = []
# for row in rows:
#     new_entry_globe = kcTable(valve_style=row[0], min_size=row[1], max_size=row[2], trim_material=row[3],
#                               trim_type=row[4], min_pres=row[5], max_pres=row[6], kc_formula=row[7],
#                               dummy1=None, dummy2=None)
#     dict_1 = {'v_tye': row[0], 'size': (int(row[1]), int(row[2])), 'material': row[3], 'trim': row[4], 'pressure': (int(row[5]), int(row[6])), 'kc_formula': row[7]}
#     kc_dict_list.append(dict_1)
#
# print(kc_dict_list)
# # add csv globe data to db
# filename_c = "materials_meta.csv"
# fields_c = []
# rows_c = []
#
# # materials csv
# with open(filename_c, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_c = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows_c.append(row)
#
# # for row in rows_c:
# #     new_material = materialMaster(name=row[0], max_temp=row[1], min_temp=row[2])
# #
# #     with app.app_context():
# #         db.session.add(new_material)
# #         db.session.commit()


# # add globe new trim type data to db
# filename_c = "11_Series_Cv.csv"
# fields_c = []
# rows_c = []
#
# # materials csv
# with open(filename_c, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_c = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows_c.append(row)
#
# for row in rows_c:
#     new_material = globeTable(trimTypeID=row[0], charac=row[1], size=row[2], coeffID=row[3],
#                               one=row[4], two=row[5], three=row[6], four=row[7], five=row[8],
#                               six=row[9], seven=row[10], eight=row[11], nine=row[12], ten=row[13])
#
#     with app.app_context():
#         db.session.add(new_material)
#         db.session.commit()
#
# with app.app_context():
#     valve_data = globeTable.query.all()
#     for i in valve_data:
#         if i.id > 376:
#             db.session.delete(i)
#             db.session.commit()

seat_list = ['Water', 'Gas', 'Vapor']

# for seat in seat_list:
#     new_seat_data = seatLeakageClass(name='seat')
#     with app.app_context():
#         db.session.add(new_seat_data)
#         db.session.commit()

# add csv butterfly data to db
filename_b = "butterfly.csv"
fields_b = []
rows_b = []


# reading csv file
# with open(filename_b, 'r') as csvfile:
#     # creating a csv reader object
#     csvreader = csv.reader(csvfile)
#
#     # extracting field names through first row
#     fields_b = next(csvreader)
#
#     # extracting each data row one by one
#     for row in csvreader:
#         rows_b.append(row)


#
# for row in rows_b:
#     new_entry_butterfly = butterflyTable(typeID=row[0], ratingID=row[1], coeffID=row[2], size=row[3],
#                                          one=row[4],
#                                          two=row[5],
#                                          three=row[6],
#                                          four=row[7],
#                                          five=row[8],
#                                          six=row[9],
#                                          seven=row[10],
#                                          eight=row[11],
#                                          nine=row[12])
#     with app.app_context():
#         db.session.add(new_entry_butterfly)
#         db.session.commit()

# TODO - For Paandi - Write the python codes here

# Todo - 1 - Example code for you!
#
# seat_list = ['Water', 'Gas', 'Vapor']
#
# for seat in seat_list:
#     new_seat_data = seatLeakageClass(name=seat)
#     with app.app_context():
#         db.session.add(new_seat_data)
#         db.session.commit()
#
# # use the list here with the correct name convention: list_*the table name*
# list_industry = ['Agriculture', 'Chemical', 'Drink', 'Food', 'Gas Transport / Distribution', 'Heating and Ventilation',
#                  'Industrial Gas Production', 'Iron & Steel Production', 'Marine', 'Minig', 'Miscellaneous',
#                  'Oil & Gas Production Offshore', 'Oil & Gas Production Onshore', 'OEM', 'Paper & Board',
#                  'Petrochemical']
# # use the for loop given, the table name should match, other wise it is a waste. Comment after running the code.
# for i in list_industry:
#     new_industry = industryMaster(name=i)
#     with app.app_context():
#         db.session.add(new_industry)
#         db.session.commit()
#
# list_region = ['Europe', 'Asia', 'Middle East', 'Western Countries']
#
# for i in list_region:
#     new_region = regionMaster(name=i)
#     with app.app_context():
#         db.session.add(new_region)
#         db.session.commit()
#
# list_Status = ['Live', 'Own ', 'Lost', 'Dead', 'Declined', 'New', 'Quoted', 'Pending']
#
# for i in list_Status:
#     new_status = statusMaster(name=i)
#     with app.app_context():
#         db.session.add(new_status)
#         db.session.commit()
#
# list_Series = ['10000', '10000', '30000', '30000', '40000']
#
# for i in list_Series:
#     new_series = valveSeries(name=i)
#     with app.app_context():
#         db.session.add(new_series)
#         db.session.commit()
#
# list_Standard_Name = ['ASME', 'API']
#
# for i in list_Standard_Name:
#     new_standard = standardMaster(name=i)
#     with app.app_context():
#         db.session.add(new_standard)
#         db.session.commit()
#
# list_Fluid_Type = ['Water', 'Gas', 'Vapor']
#
# for i in list_Fluid_Type:
#     new_fluidtype = fluidType(name=i)
#     with app.app_context():
#         db.session.add(new_fluidtype)
#         db.session.commit()
#
# list_Application = ['Temperature Control ', 'Pressure Control', 'Flow Control', 'Level Control', 'Compressor Re-cycle',
#                     'Compressor Anti-Surge', 'Cold Box Service', 'Condenste Service', 'Cryogenic Service',
#                     'Desuperheater Service', 'Feedwater Service', 'Heater Drain', 'High P & T Steam',
#                     'Hydrogen / He. Service', 'Joule Thompson Valve', 'L.N.G Service', 'Soot Blower Valve',
#                     'Spraywater Valve', 'Switching Valve']
# for i in list_Application:
#     new_application = applicationMaster(name=i)
#     with app.app_context():
#         db.session.add(new_application)
#         db.session.commit()
#
# list_End_Connection_Option = ['None', 'Integral Flange', 'Loose Flange', 'Flange (Drilled ASME 150)', 'Screwed NPT',
#                               'Screwed BSPT', 'Screwed BSP', 'Socket Weld', 'Butt Weld', 'Grayloc Hub',
#                               'Vector / Techlok Hub', 'Destec Hub', 'Galperti Hub', 'BW Stubs', 'Plain Stubs',
#                               'Drilled Lug', 'Tapped Lug', 'BW Stubs Sch 10', 'BW Stubs Sch 40', 'BW Stubs Sch 80']
# for i in list_End_Connection_Option:
#     new_Connection = endConnection(name=i)
#     with app.app_context():
#         db.session.add(new_Connection)
#         db.session.commit()
#
# list_End_Finish = ['N/A', 'RF Serrated', 'RF (125 -250AARH) 3.2-6.3um', 'RF(63-125AARH)1.6-3.2um', 'FF Serrated',
#                    'FF (125 -250AARH) 3.2-6.3um', 'FF(63-125AARH)1.6-3.2um', 'RTJ', 'ASME B16.25 Fig.2a']
# #
# for i in list_End_Finish:
#     new_Finish = endFinish(name=i)
#     with app.app_context():
#         db.session.add(new_Finish)
#         db.session.commit()
#
# list_Bonnet_Type = ['Standard', 'Standard Extension', 'Normalized / Finned', 'Bellow Seal', 'Cyrogenic',
#                     'Cyrogenic +Drip Plate', 'Cyrogenic + Seal Boot', 'Cyrogenic + Cold Box Flange']
# for i in list_Bonnet_Type:
#     new_bonnetType = bonnetType(name=i)
#     with app.app_context():
#         db.session.add(new_bonnetType)
#         db.session.commit()
#
# list_Packing_Material = ['Graphite / Ceramic', 'Graphite / Ni-Resist', 'Graphite / DU Glacier',
#                          'Graphite / DUB Glacier', 'Graphite / MP2', 'Graphite / MP3', 'Graphite / 316-Armaloy',
#                          'Graphite / Stellite', 'Graphite / N.60-Armaloy', 'High Integrity Gland', 'HIG Supagraf',
#                          'PTFE Chevron', 'PTFE Braid', 'High Intensity Gland', 'Graphite']
# for i in list_Packing_Material:
#     new_packingMaterial = packingMaterial(name=i)
#     with app.app_context():
#         db.session.add(new_packingMaterial)
#         db.session.commit()
#
# list_Trim_Type = ['Modified', 'Microspline', 'Contoured', 'Ported', 'MHC-1']
# for i in list_Trim_Type:
#     new_trimTyp = trimType(name=i)
#     with app.app_context():
#         db.session.add(new_trimTyp)
#         db.session.commit()
#
# list_Flow_Direction = ['Seat Downstream''Seat Upstream']
#
# for i in list_Flow_Direction:
#     new_flowDirection = flowDirection(name=i)
#     with app.app_context():
#         db.session.add(new_flowDirection)
#         db.session.commit()
#
# List_Seat_Leakage_Class = ['ANSI Class III', 'ANSI Class IV', 'ANSI Class V', 'ANSI Class VI']
#
# for i in List_Seat_Leakage_Class:
#     new_seatLeakageClass = seatLeakageClass(name=i)
#     with app.app_context():
#         db.session.add(new_seatLeakageClass)
#         db.session.commit()
#
# list_Soft_Parts_Material = ['Standard for Service', 'PTFE', 'PCTFE (KEL-F)', 'Spiral Wound 316L/Graph',
#                             'Spiral Wound 316L/PTFE', 'Spiral Wound 31803/Graph', 'Spiral Wound 31803/PTFE',
#                             'Spiral Wound 32760/Graph', 'Spiral Wound 32760/PTFE', 'Spiral Wound 625/Graph',
#                             'Spiral Wound 625/PTFE', 'Graphite', 'Metal Seal', 'Double ABS (cryo)']
#
# for i in list_Soft_Parts_Material:
#     new_softPartsMaterial = softPartsMaterial(name=i)
#     with app.app_context():
#         db.session.add(new_softPartsMaterial)
#         db.session.commit()
#
# list_Fluid_Name = ['Acetic Acid', 'Acetic Anhydride', 'Acetone', 'Acetylene', 'Acrylic Acid', 'Air', 'Ammonia', 'Argon',
#                    'Benzene', 'Bromine', 'Butadiene 1,3', 'Butane', 'Butyl Alcohol', 'Carbon Dixide ',
#                    'Carbon monoxide', 'Carbon Tetrachloride', 'Chlorine Dry', 'chlorine Wet', 'Demin.Water',
#                    'Dowtherm A', 'Ethane', 'Ethyl Alcohol', 'Ethylene', 'Helium', 'Heptane', 'Hexane',
#                    'hydrocarbon Gas', 'Hydrocarbon Liquid', 'Hydrogen', 'hydrogen Chloride', 'Hydrogen Fluoride',
#                    'Hydrogen Sulphide', 'Isopropyl Alcohol', 'Methane', 'Methyle Alcohol', 'Methyle Chloride',
#                    'Natural Gas', 'Nitrogen', 'Octane', 'Oxygen', 'Pentance', 'Phenol', 'Propene', 'Propyl Alchohol',
#                    'Propyl Chloride', 'Propylene', 'Pyridine', 'Refrigerant 12', 'Refrigerant 22', 'Sea Water', 'Steam',
#                    'Sulphur Dioxide', 'Toluene', 'Water']
# for i in list_Fluid_Name:
#     new_fluidName = fluidName(name=i)
#     with app.app_context():
#         db.session.add(new_fluidName)
#         db.session.commit()
#
# list_Valve_Balancing = ['Unbalanced', 'PTFE Seal', 'Graphite']
# for i in list_Valve_Balancing:
#     new_valveBalancing = valveBalancing(name=i)
#     with app.app_context():
#         db.session.add(new_valveBalancing)
#         db.session.commit()
#
# list_Act_Series = ['N/A', 'Manual Gear Box', 'SD', 'PA', 'Scotch Yoke ', 'Electrical Actuator', 'Hydraulic Actuator',
#                    'Electro- Hydraulic Actuator']
# for i in list_Act_Series:
#     new_actuatorSeries = actuatorSeries(name=i)
#     with app.app_context():
#         db.session.add(new_actuatorSeries)
#         db.session.commit()
#
# list_Handwheel = ['None', 'Side Mounted Handwheel', 'Top Mounted Handwheel', 'Top Mtd. Jacking Screw',
#                   'Hydraulic Override']
# for i in list_Handwheel:
#     new_handweel = handweel(name=i)
#     with app.app_context():
#         db.session.add(new_handweel)
#         db.session.commit()
#
# list_Travel_Stops = ['None', 'Limit Opening', 'Limit Closing', 'Factory Standard']
#
# for i in list_Travel_Stops:
#     new_travelStops = travelStops(name=i)
#     with app.app_context():
#         db.session.add(new_travelStops)
#         db.session.commit()
#
# list_Schedule = ['5S', '10S', '40S', '80S', '10', '20', '30', '40', 'STD', '60', '80', 'XS', '100', '120', '140', '160',
#                  'XXS']
#
# for i in list_Schedule:
#     new_schedule = schedule(name=i)
#     with app.app_context():
#         db.session.add(new_schedule)
#         db.session.commit()
#
# list_Fail_Action = ['Modulating AFO', 'Modulating AFC', 'Modulating AFS', 'On/Off AFO', 'On/Off AFC', 'On/Off AFS']
#
# for i in list_Fail_Action:
#     new_failAction = failAction(name=i)
#     with app.app_context():
#         db.session.add(new_failAction)
#         db.session.commit()
#
# list_Positioner_make_model = ['None', 'Tissin ', 'Siemens Moore 760p', 'siemens PS2 HART', 'siemens PS2 F',
#                               'Metso ND9000 HART', 'Metso ND9000 F', 'Fisher DVC6200AC', 'Fisher DVC6200HC HART',
#                               'Fisher DVC6200AD HART', 'Fisher DVC6200PD HART', 'Fisher DVC 6200F-SCFD',
#                               'Fisher DVC 6200F-SCAD', 'Fisher DVC 6200F-SCPD', 'See Note']
#
# for i in list_Positioner_make_model:
#     new_positionerMakeModel = positionerMakeModel(name=i)
#     with app.app_context():
#         db.session.add(new_positionerMakeModel)
#         db.session.commit()
#
# # airset
# list_Airset = ['None', '1/4" NPT ControlAir 300', '1/4" NPT ControlAir 350 SS', '1/2" NPT ControlAir 350 SS',
#                '1/4"NPT AL.+SS Gauge', '1/2"NPT AL.+SS Gauge', '1/4"NPT 316SS + SS Gauge', '1/2"NPT 316SS + SS Gauge',
#                'See Note']
#
# for i in list_Airset:
#     new_airset = airset(name=i)
#     with app.app_context():
#         db.session.add(new_airset)
#         db.session.commit()
#
# list_Solenoid_Valve = ['None', '1/4" Asco 3/2 Br. IP66 Exd', '1/4" Asco 5/4 Br. IP66 Exd', '1/4" Asco 3/2 S/S IP66 Exd',
#                        '1/4" Asco 5/4 S/S IP66 Exd', '1/4" ICO4 3/2 S/S IP66 Exd', '1/4" ICO4  5/4 S/S IP66 Exd',
#                        '1/4" ICO3  3/2 S/S IP66 Exd', '1/4" ICO2  3/2 S/S IP66 Exi', '1/4" ICO2  5/4 S/S IP66 Exi']
#
# for i in list_Solenoid_Valve:
#     new_solenoidValve = solenoidValve(name=i)
#     with app.app_context():
#         db.session.add(new_solenoidValve)
#         db.session.commit()
#
# list_Lock_Valve = ['None', '164A AI.Alloy / Epoxy']
#
# for i in list_Lock_Valve:
#     new_lockValve = lockValve(name=i)
#     with app.app_context():
#         db.session.add(new_lockValve)
#         db.session.commit()
#
# list_Qev_Boosters = ['None', '1/4" NPT IB10 Al./Epoxy', '1/4"NPT IB10 S/S', '1/2" NPT IB10 Al./Epoxy',
#                      '1/2"NPT IB10 S/S', '3/4" NPT IB10 Al./Epoxy', '3/4"NPT IB10 S/S', '1/4"NPT.Q.E.AL/Epoxy',
#                      '1/4"NPT.Q.E. S/s', '1/2"NPT.Q.E.AL/Epoxy', '1/2"NPT.Q.E. S/s', '3/4"NPT.Q.E.AL/Epoxy',
#                      '3/4"NPT.Q.E. S/s']
#
# for i in list_Qev_Boosters:
#     new_qevBoosters = qevBoosters(name=i)
#     with app.app_context():
#         db.session.add(new_qevBoosters)
#         db.session.commit()
#
# list_Pilot_Valve = ['None', 'Versa 1/4" Brass', 'Versa 1/4" StSt', 'Versa 1/2" Brass', 'Versa 1/2" StSt',
#                     'Versa 3/4" brass', 'Mid.Pneu. 1/4" St.St.', 'Mid.Pneu. 1/2" St.St.', 'Mid.Pneu. 3/4" St.St.']
#
# for i in list_Pilot_Valve:
#     new_pilotValve = pilotValve(name=i)
#     with app.app_context():
#         db.session.add(new_pilotValve)
#         db.session.commit()
#
# list_Switch_Position = ['None', '4am=Closed, 20ma=Open', '4am=Open, 20ma=Close', 'Limit Switch Open&Closed',
#                         '4am=Closed. 20ma=Open', '4am=Open,.20ma=Close']
#
# for i in list_Switch_Position:
#     new_switchPosition = switchPosition(name=i)
#     with app.app_context():
#         db.session.add(new_switchPosition)
#         db.session.commit()
#
# list_IP_Converter = ['None', 'ABB AI.3-15psi IP65 Exia', 'ABB AI.0.2-1bar IP65 Exia', 'ABB AI.3-15psi IP65 Exd',
#                      'ABB AI.0.2-1bar IP65 Exd', 'ABB SS 3-15psi IP65 Exia', 'ABB SS 0.2-1psi IP65 Exia',
#                      'ABB SS 3-15psi IP65 Exd', 'ABB SS 0.2-1bar Ip65Exd']
#
# for i in list_IP_Converter:
#     new_IPConverter = IPConverter(name=i)
#     with app.app_context():
#         db.session.add(new_IPConverter)
#         db.session.commit()
#
# list_Air_Receiver = ['None', '113L ASME VIII St St Kit', '303L ASME VIII St St Kit', '50L BS EN286 Brass Kit',
#                      '113L BS EN286 Brass Kit', '50L BS EN286 St St Kit', '113L BS EN286 St St Kit', 'See note N7']
#
# for i in list_Air_Receiver:
#     new_airReceiver = airReceiver(name=i)
#     with app.app_context():
#         db.session.add(new_airReceiver)
#         db.session.commit()
#
# list_Tubing = ['None', 'Metric Copper', 'Metric PVC / Copper', 'metric 316L SS', 'Imperial Copper',
#                'Imperial PVC / Copper', 'Imperial 316L SS', 'Imperial 6Mo', 'Metric 6Mo', 'Imperial Super Duplex',
#                'Metric Super Duplex']
#
# for i in list_Tubing:
#     new_tubing = tubing(name=i)
#     with app.app_context():
#         db.session.add(new_tubing)
#         db.session.commit()
#
# list_Fittings = ['None', 'Wadelok Brass', 'Swagelok Brass', 'A-Lok SS', 'Swagelok SS', 'Gyrolok SS', 'Swagelok 6Mo',
#                  'Swagelok Super Dulex', 'Parker 6mo', 'Parker Super Duplex']
#
# for i in list_Fittings:
#     new_fittings = fittings(name=i)
#     with app.app_context():
#         db.session.add(new_fittings)
#         db.session.commit()
#
# list_Cleaning = ['Standard Workshop', 'Clean for Oxygen Service', 'Clean for Cryogenic', 'UHP(DS-153)']
#
# for i in list_Cleaning:
#     new_cleaning = cleaning(name=i)
#     with app.app_context():
#         db.session.add(new_cleaning)
#         db.session.commit()
#
# list_Certification = ['N/A', 'PED Mod H + ATEX', 'PED SEP H + ATEX', 'PED N/A + ATEX', 'PED Mod H + ATEX N?A',
#                       'PED SEP + ATEX N?A', 'See note ']
#
# for i in list_Certification:
#     new_certification = certification(name=i)
#     with app.app_context():
#         db.session.add(new_certification)
#         db.session.commit()
#
# list_Paint_Finish = ['None', 'Offshore', 'High Temp', 'Specification Standard', 'Colour Specification',
#                      'Customer Paint Spec.', 'See Note ']
#
# for i in list_Paint_Finish:
#     new_paintFinish = paintFinish(name=i)
#     with app.app_context():
#         db.session.add(new_paintFinish)
#         db.session.commit()
#
# list_Paint_Certs = ['None', 'Standard Mati Certs BFV', '3.1+NACE MR017/ISO15156', '3.1 Body,Disc,Shaft,Cover',
#                     'SHELL MESC SPE 77/302', 'NACE MR-01-75-2022, 3.1', 'NACE ISO 15156, 3.1',
#                     'MR-01-75+ISO 10204, 3.2', 'ISO 15156+ISO 10204 3.2', 'See note ']
#
# for i in list_Paint_Certs:
#     new_paintCerts = paintCerts(name=i)
#     with app.app_context():
#         db.session.add(new_paintCerts)
#         db.session.commit()
#
# eng_list = ['Divya', 'Nisha', 'Suraj', 'Veerapandi', 'Nishanth']
# for i in eng_list:
#     new_eng = engineerMaster(name=i)
#     with app.app_context():
#         db.session.add(new_eng)
#         db.session.commit()
#
# customer_list = ['Customer_1', 'Customer_2', 'Customer_3', 'Customer_4', 'Customer_5']
# for i in customer_list:
#     new_customer = customerMaster(name=i)
#     with app.app_context():
#         db.session.add(new_customer)
#         db.session.commit()
#
# valve_size_list = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30]
# model_list = ['Model_1', 'Model_2', 'Model_3']
#
# for i in valve_size_list:
#     new_size = valveSize(size=i)
#     with app.app_context():
#         db.session.add(new_size)
#         db.session.commit()
#
#
# for i in model_list:
#     new_model = modelMaster(name=i)
#     with app.app_context():
#         db.session.add(new_model)
#         db.session.commit()
#
# rating_list = [150, 300, 600, 900, 1500, 2500, 5000, 10000, 15000]
# for i in rating_list:
#     new_rating = rating(size=i)
#     with app.app_context():
#         db.session.add(new_rating)
#         db.session.commit()


# delete unwanted items
# with app.app_context():
#     items = itemMaster.query.all()
#     for i in items:
#         if i.id not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16, 17]:
#             db.session.delete(i)
#             db.session.commit()

def nothing():
    pass


# TODO ------------------------------------------ SIZING PYTHON CODE --------------------------------------- #


# Cv1 = Cv_butterfly_6
# FL1 = Fl_butterfly_6


# TODO - Liquid Sizing - fisher
def etaB(valveDia, pipeDia):
    return 1 - ((valveDia / pipeDia) ** 4)


def eta1(valveDia, pipeDia):
    return 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def eta2(valveDia, pipeDia):
    return 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def sigmaEta(valveDia, inletDia, outletDia):
    a_ = eta1(valveDia, inletDia) + eta2(valveDia, outletDia) + etaB(valveDia, inletDia) - etaB(valveDia, outletDia)
    print(
        f"sigma eta inputs: {eta1(valveDia, inletDia)}, {eta2(valveDia, outletDia)}, {etaB(valveDia, inletDia)}, {valveDia}, {outletDia}")
    return a_


def FF(vaporPressure, criticalPressure):
    a = 0.96 - 0.28 * math.sqrt(vaporPressure / criticalPressure)
    return a


def fP(C, valveDia, inletDia, outletDia, N2_value):
    a = (sigmaEta(valveDia, inletDia, outletDia) / N2_value) * ((C / valveDia ** 2) ** 2)
    # print(
    #     f"fp numerator: {a}, n2 value: {N2_value}, valveDia: {valveDia}, sigmaeta: {sigmaEta(valveDia, inletDia, outletDia)}, CV: {C}")
    print(f"Sigma eta: {sigmaEta(valveDia, inletDia, outletDia)}")
    b_ = 1 / math.sqrt(1 + a)
    # return 0.71
    return b_


def flP(C, valveDia, inletDia, N2_value, Fl):
    K1 = eta1(valveDia, inletDia) + etaB(valveDia, inletDia)
    print(f"k1, valvedia, inlet, C: {K1}, {valveDia}, {inletDia}, {N2_value}, {Fl}, {C}")
    a = (K1 / N2_value) * ((C / valveDia ** 2) ** 2)
    print(f"a for flp: {a}")
    b_ = 1 / math.sqrt((1 / (Fl * Fl)) + a)
    return b_


def delPMax(Fl, Ff, inletPressure, vaporPressure):
    a_ = Fl * Fl * (inletPressure - (Ff * vaporPressure))
    print(f"delpmax: {Fl}, {inletPressure}, {Ff}, {vaporPressure}")
    return round(a_, 3)


def selectDelP(Fl, criticalPressure, inletPressure, vaporPressure, outletPressure):
    Ff = FF(vaporPressure, criticalPressure)
    a_ = delPMax(Fl, Ff, inletPressure, vaporPressure)
    b_ = inletPressure - outletPressure
    return min(a_, b_)


def Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity):
    a_ = N1_value * math.sqrt((inletPressure - outletPressure) / sGravity)
    b_ = flowrate / a_
    print(f"CVt: {b_}")
    return round(b_, 3)


def reynoldsNumber(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure, outletPressure,
                   sGravity):
    Cv_1 = Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity)
    # print(Cv_1)
    a_ = (N4_value * Fd * flowrate) / (viscosity * math.sqrt(Fl * Cv_1))
    # print(a_)
    b_ = ((Fl * Cv_1) ** 2) / (N2_value * (pipeDia ** 4))
    c_ = (1 + b_) ** (1 / 4)
    d_ = a_ * c_
    return round(d_, 3)


def getFR(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure, outletPressure, sGravity):
    RE = reynoldsNumber(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure,
                        outletPressure, sGravity)
    print(RE)
    if 56 <= RE <= 40000:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if REv[a] == RE:
                return FR[a]
            elif REv[a] > RE:
                break
            else:
                a += 1

        fr = FR[a - 1] - (((REv[a - 1] - RE) / (REv[a - 1] - REv[a])) * (FR[a - 1] - FR[a]))

        return round(fr, 3)
    elif RE < 56:
        a = 0.019 * (RE ** 0.67)
        return a
    else:
        return 1


# print(7600, 1, 300, 8000, 0.68, 0.00214, 80, 0.865, 8.01, 6.01, 0.908)


def CV(flowrate, C, valveDia, inletDia, outletDia, N2_value, inletPressure, outletPressure, sGravity, N1_value, Fd,
       vaporPressure, Fl, criticalPressure, N4_value, viscosity, thickness):
    if valveDia != inletDia:
        FLP = flP(C, valveDia, inletDia + 2 * thickness, N2_value, Fl)
        FP = fP(C, valveDia, inletDia + 2 * thickness, outletDia + 2 * thickness, N2_value)
        # print(f"FP: {FP}")
        FL = FLP / FP
    else:
        FL = Fl
    delP = selectDelP(FL, criticalPressure, inletPressure, vaporPressure, outletPressure)
    Fr = getFR(N4_value, Fd, flowrate, viscosity, FL, N2_value, inletDia + 2 * thickness, N1_value, inletPressure,
               outletPressure,
               sGravity)
    # print(Fr)
    fp_val = fP(C, valveDia, inletDia + 2 * thickness, outletDia + 2 * thickness, N2_value)
    a_ = N1_value * fp_val * Fr * math.sqrt(delP / sGravity)
    b_ = flowrate / a_
    print(f"FR: {Fr}")
    return round(b_, 3)


# TODO - GAS SIZING


def x_gas(inletPressure, outletPressure):
    result = (inletPressure - outletPressure) / inletPressure
    # print(f"x value is: {round(result, 2)}")
    return round(result, 3)


def etaB_gas(valveDia, pipeDia):
    result = 1 - ((valveDia / pipeDia) ** 4)
    return round(result, 3)


def eta1_gas(valveDia, pipeDia):
    result = 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 3)


def eta2_gas(valveDia, pipeDia):
    result = 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 3)


def sigmaEta_gas(valveDia, inletDia, outletDia):
    result = eta1_gas(valveDia, inletDia) + eta2_gas(valveDia, outletDia) + etaB_gas(valveDia, inletDia) - etaB_gas(
        valveDia, outletDia)
    return round(result, 3)


def fP_gas(C, valveDia, inletDia, outletDia, N2_value):
    a = (sigmaEta_gas(valveDia, inletDia, outletDia) / N2_value) * ((C / valveDia ** 2) ** 2)
    # print(f"N2: {N2_value}, sigmaeta: {sigmaEta_gas(valveDia, inletDia, outletDia)}")
    result = 1 / math.sqrt(1 + a)
    # print(f"FP value is: {round(result, 2)}")
    return round(result, 2)


# specific heat ratio - gamma
def F_Gamma_gas(gamma):
    result = gamma / 1.4
    # print(f"F-Gamma: {round(result, 5)}")
    return round(result, 5)


def xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    f_gamma = F_Gamma_gas(gamma)
    if valveDia != inletDia:
        fp = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
        etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
        # print(f"etaI: {round(etaI, 2)}")
        a_ = xT / fp ** 2
        b_ = (xT * etaI * C * C) / (N5_in * (valveDia ** 4))
        xTP = a_ / (1 + b_)
        result = f_gamma * xTP
        # print(f"xChoked1: {round(result, 2)}")
    else:
        result = f_gamma * xT
        # print(f"xChoked2: {round(result, 3)}")
    return round(result, 4)


def xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    result = min(xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value),
                 x_gas(inletPressure, outletPressure))
    # print(f"xSizing: {round(result, 3)}")
    return round(result, 3)


def xTP_gas(xT, C, valveDia, inletDia, outletDia, N2_value):
    etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
    fp = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
    a_ = xT / fp ** 2
    b_ = xT * etaI * C * C / (N5_in * (valveDia ** 4))
    result = a_ / (1 + b_)
    return round(result, 3)


# Expansion factor
def Y_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    f_gamma = F_Gamma_gas(gamma)
    a = 1 - ((xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value) / (
            3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value))))
    # print(
    #     f"rhs for y: {(xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value) / (3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value)))}")
    result_ch = min(xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value),
                    x_gas(inletPressure, outletPressure))
    if result_ch == xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
        result = (2 / 3)
    else:
        result = a
    # result = a

    # print(f"Y value is: {round(result, 3)}")

    return round(result, 7)


def Cv_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, temp, compressibilityFactor,
           flowRate, sg, sg_, N2_value):
    # sg_ = int(input("Which value do you want to give? \nVolumetric Flow - Specific Gravity (1) \nVolumetric Flow - "
    #                 "Molecular Weight (2)\nMass Flow - Specific Weight (3)\nMass Flow - Molecular Weight (4)\nSelect "
    #                 "1 0r 2 0r 3 or 4: "))

    sg_ = sg_

    # if sg_ == 1:
    #     Gg = int(input("Give value of Gg: "))
    #     sg = 0.6
    # elif sg_ == 2:
    #     M = int(input("Give value of M: "))
    #     sg = M
    # elif sg_ == 3:
    #     gamma_1 = int(input("Give value of Gamma1: "))
    #     sg = gamma_1
    # else:
    #     M = int(input("Give value of M: "))
    #     sg = M

    # sg = 1.0434
    sg = sg

    a_ = inletPressure * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(inletPressure, outletPressure,
                                                                                    gamma, C,
                                                                                    valveDia,
                                                                                    inletDia, outletDia, xT, N2_value)
    b_ = temp * compressibilityFactor
    x_ = x_gas(inletPressure, outletPressure)
    x__ = xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    print(f'sg_ value: {sg_}')
    if sg_ == 1:
        A = flowRate / (
                N7_60_scfh_psi_F * inletPressure * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(
            inletPressure,
            outletPressure,
            gamma, C,
            valveDia,
            inletDia,
            outletDia,
            xT, N2_value) * math.sqrt(
            x__ / (sg * temp * compressibilityFactor)))
        # return round(A, 3)

    elif sg_ == 2:
        A = flowRate / (N9_O_m3hr_kPa_C * a_ * math.sqrt(x__ / (sg * b_)))
        print('gas sizing eq2 input in m3hr kpa and C:')
        print(flowRate, N9_O_m3hr_kPa_C, a_, x_, x__, sg, temp, compressibilityFactor)
        # return A

    elif sg_ == 3:
        A = flowRate / (
                N6_lbhr_psi_lbft3 * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(inletPressure,
                                                                                               outletPressure,
                                                                                               gamma, C, valveDia,
                                                                                               inletDia, outletDia,
                                                                                               xT,
                                                                                               N2_value) * math.sqrt(
            x__ * sg * inletPressure))
        # return A

    else:
        A = flowRate / (N8_kghr_bar_K * a_ * math.sqrt((x__ * sg) / b_))
        # return A
    fk = F_Gamma_gas(gamma)
    x_choked = xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    y = Y_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    xtp = xTP_gas(xT, C, valveDia, inletDia, outletDia, N2_value)
    fp__ = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
    output_list = [round(A, 3), x_, fk, x_choked, y, xT, xtp, fp__]
    return output_list


# TODO - New Trim Exit velocity formulae

def outletDensity(iPres, oPres, MW, R, iTemp):
    Pi = inletDensity(iPres, MW, R, iTemp)
    a = Pi * (oPres / iPres)
    return round(a, 2)


def tex_new(calculatedCV, ratedCV, port_area, flowrate, iPres, oPres, MW, R, iTemp, fluid_state):
    # density in kg/m3, fl in m3/hr, area in m2
    port_area = port_area * 0.000645
    tex_area = (calculatedCV / ratedCV) * port_area
    tex_vel = flowrate / tex_area
    oDensity = outletDensity(iPres, oPres, MW, R, iTemp)
    ke = (oDensity * tex_vel ** 2) / 19.62
    print(
        f"tex_new inputs: {calculatedCV}, {ratedCV}, {port_area}, {flowrate}, {iPres}, {oPres}, {MW}, {R}, {iTemp}, {fluid_state}, {tex_vel}, {oDensity}, {tex_area}")
    if fluid_state == 'Liquid':
        return round(tex_vel, 3)
    else:
        return round(ke * 0.001422, 3)


# TODO - Trim exit velocities and other velocities

def trimExitVelocity(inletPressure, outletPressure, density, trimType, numberOfTurns):
    a_ = math.sqrt(((inletPressure - outletPressure) * 201) / density)
    K1, K2 = getMultipliers(trimType, numberOfTurns)
    return a_ * K1 * K2


def getMultipliers(trimType, numberOfTurns):
    trimDict = {"Baffle Plate": 0.7, "Trickle": 0.92, "Contoured": 0.92, "Cage": 0.57, "MLT": 0.53}
    turnsDict = {2: 0.88, 4: 0.9, 6: 0.91, 8: 0.92, 10: 0.93, 12: 0.96, "other": 1}

    K1 = trimDict[trimType]
    K2 = turnsDict[numberOfTurns]

    return K1, K2


# pressure in psi
def trimExitVelocityGas(inletPressure, outletPressure):
    a__ = (inletPressure - outletPressure) / 0.0214
    a_ = math.sqrt(a__)
    return round(a_, 3)


def getVelocity(Flowrate, inletDia, outletDia, valveDia):
    # give values of Dias in, flow rate in m3/hr
    inletDia = inletDia * 0.0254
    outletDia = outletDia * 0.0254
    valveDia = valveDia * 0.0254
    # print(inletDia, outletDia, valveDia)
    inletVelocity = (Flowrate / (2827.44 * (inletDia ** 2)))
    outletVelocity = (Flowrate / (2827.44 * (outletDia ** 2)))
    valveVelocity = (Flowrate / (2827.44 * (valveDia ** 2)))

    return inletVelocity, outletVelocity, valveVelocity


# TODO - Power Level - Gas and Liquid
# pressure in psi, plevel in kw
def power_level_liquid(inletPressure, outletPressure, sGravity, Cv):
    a_ = ((inletPressure - outletPressure) ** 1.5) * Cv
    b_ = sGravity * 2300
    c_ = a_ / b_
    return round(c_, 3)


# flowrate in lb/s, pressure in psi
# def power_level_gas(specificHeatRatio, inletPressure, outletPressure, flowrate):
#     pressureRatio = outletPressure / inletPressure
#     specificVolume = 1 / pressureRatio
#     heatRatio = specificHeatRatio / (specificHeatRatio - 1)
#     a_ = heatRatio * inletPressure * specificVolume
#     b_ = (1 - pressureRatio ** (1 / heatRatio)) * flowrate / 5.12
#     c_ = a_ * b_
#     return round(c_, 3)


# flowrate in kg/hr, pressure in pa, density in kg/m3
def power_level_gas(specificHeatRatio, inletPressure, outletPressure, flowrate, density):
    pressureRatio = outletPressure / inletPressure
    specificVolume = 1 / density
    heatRatio = specificHeatRatio / (specificHeatRatio - 1)
    a_ = heatRatio * inletPressure * specificVolume
    b_ = (1 - pressureRatio ** (1 / heatRatio)) * flowrate / 36000000
    c_ = a_ * b_
    return round(c_, 3)


# TODO ----------------------------------------- Actuator Sizing -------------------------------------- #
valve_force_dict = [{'key': ('contour', 'unbalanced', 'under', 'shutoff'), 'formula': 1},
                    {'key': ('cage', 'unbalanced', 'under', 'shutoff'), 'formula': 2},
                    {'key': ('cage', 'unbalanced', 'over', 'shutoff'), 'formula': 3},
                    {'key': ('cage', 'balanced', 'under', 'shutoff'), 'formula': 4},
                    {'key': ('cage', 'balanced', 'over', 'shutoff'), 'formula': 5},
                    {'key': ('contour', 'unbalanced', 'under', 'shutoff+'), 'formula': 6},
                    {'key': ('cage', 'unbalanced', 'under', 'shutoff+'), 'formula': 7},
                    {'key': ('cage', 'unbalanced', 'over', 'shutoff+'), 'formula': 8},
                    {'key': ('cage', 'balanced', 'under', 'shutoff+'), 'formula': 9},
                    {'key': ('cage', 'balanced', 'over', 'shutoff+'), 'formula': 10},
                    {'key': ('contour', 'unbalanced', 'under', 'close'), 'formula': 11},
                    {'key': ('cage', 'unbalanced', 'under', 'close'), 'formula': 12},
                    {'key': ('cage', 'unbalanced', 'over', 'close'), 'formula': 13},
                    {'key': ('cage', 'balanced', 'under', 'close'), 'formula': 14},
                    {'key': ('cage', 'balanced', 'over', 'close'), 'formula': 15},
                    {'key': ('contour', 'unbalanced', 'under', 'open'), 'formula': 16},
                    {'key': ('cage', 'unbalanced', 'under', 'open'), 'formula': 17},
                    {'key': ('cage', 'unbalanced', 'over', 'open'), 'formula': 18},
                    {'key': ('cage', 'balanced', 'under', 'open'), 'formula': 19},
                    {'key': ('cage', 'balanced', 'over', 'open'), 'formula': 20},
                    ]


def valveForces(p1_, p2_, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                case, shutoffDelP):
    print('Valve forces inputs:')
    print(p1_, p2_, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
          case, shutoffDelP)
    num = 0
    if trimtype == 'contour':
        flow = 'under'
        balance = 'unbalanced'
    if d1 in [1, 3, 8, 11, 4]:
        d1 = round(d1)
    p1 = p1_
    p2 = p2_
    a1 = 0.785 * d1 * d1  # seat bore - seat dia
    a2 = 0.785 * d2 * d2  # plug dia
    a3 = 0.785 * d3 * d3  # stem dia
    shutoffDelP = shutoffDelP
    with app.app_context():
        friction_element = db.session.query(packingFriction).filter_by(stemDia=d3, pressure=rating).first()
        a_ = {'ptfe1': friction_element.ptfe1, 'ptfe2': friction_element.ptfe2, 'ptfer': friction_element.ptfer,
              'graphite': friction_element.graphite}
        # print(trimtype, d1)
        sf_element = db.session.query(seatLoad).filter_by(trimtype=trimtype, seatBore=d1).first()
        print(trimtype, d1)
        b_ = {'six': sf_element.six, 'two': sf_element.two, 'three': sf_element.three, 'four': sf_element.four,
              'five': sf_element.five}
        B = float(a_[material])
        C = math.pi * d1 * float(b_[leakageClass])
        # print(f"Packing friction: {B}, Seat Load Force: {C}")
    print((trimtype, balance, flow, case))
    for i in valve_force_dict:
        if i['key'] == (trimtype, balance, flow, case):
            num = int(i['formula'])
    print(f'num: {num}')
    if num == 1:
        a_ = shutoffDelP * a1
        UA = a1
    elif num == 2:
        a_ = shutoffDelP * a1
        UA = a1
    elif num == 3:
        a_ = shutoffDelP * (a3 - a1)
        UA = a3 - a1
    elif num == 4:
        a_ = shutoffDelP * (a3 - ua)
        UA = ua
    elif num == 5:
        a_ = shutoffDelP * ua
        UA = ua
    elif num == 6:
        a_ = (shutoffDelP * a1) + B + C
        UA = a1
        # print(a_, p1, a1)
    elif num == 7:
        a_ = (shutoffDelP * a1) + B + C
        UA = a1
        # print(a_, p1, a1)
    elif num == 8:
        a_ = (shutoffDelP * (a3 - a1)) + B + C
        UA = a3 - a1
    elif num == 9:
        a_ = shutoffDelP * (a3 - ua) + B + C
        UA = ua
        print(f"inputs for equation 9: {a3, ua, shutoffDelP, B, C}")
    elif num == 10:
        a_ = (shutoffDelP * ua) + B + C
        UA = ua
    elif num in [11, 12]:
        a_ = (p1 * a1) + (p2 * (a2 - a1)) - (p2 * (a2 - a3))
        print(f"eq 11 or 12 inputs: {p1}, {p2}, {a1}, {a2}, {a3}")
        UA = a2 - a1
    elif num == 13:
        a_ = p1 * (a2 - a1) + p2 * a1 - p1 * (a2 - a3)
        UA = a2 - a1
    elif num == 14:
        a_ = p1 * a1 + p2 * (a2 - a1) - p1 * (a2 - a3)
        UA = a2 - a1
    elif num == 15:
        a_ = p1 * (a2 - a1) + p2 * a1 - p2 * (a2 - a3)
        UA = a2 - a1
    elif num in [16, 17, 19]:
        a_ = (p1 * a2) - (p2 * (a2 - a3))
        print(f"eq 16 inputs: {p1}, {p2}, {a2}, {a3}")
        UA = a2 - a1
    elif num in [18, 20]:
        a_ = p2 * a2 - p1 * (a2 - a3)
        UA = a2 - a1
    else:
        a_ = 1
        UA = a2 - a1

    return_list = [round(a_, 3), UA, B, b_[leakageClass]]

    return return_list


def actuatorForce(size, stroke, r1, r2, setPressure):
    springRate = ((r2 - r1) / stroke) * size
    springForceMin = r1 * size
    springForceMax = r2 * size
    NATMax = size * setPressure - springForceMin
    NATMin = size * setPressure - springForceMax
    # print(
    #     f"act forces: spring rate: {round(springRate)}, spring force min: {round(springForceMin)}, spring force max: {round(springForceMax)}, Net Air Thrust Max: {round(NATMax)}, Net Air Thrust Min: {round(NATMin)}")
    return [round(springRate), round(springForceMin), round(springForceMax), round(NATMax), round(NATMin)]


def compareForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                  case, shutoffDelP, size, stroke, r1, r2, setPressure, failAction, valveTravel, flowChar):
    # if stroke > valveTravel:
    #     stroke = valveTravel

    vForce_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                          case, shutoffDelP)
    vForce_shutoff_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                                  'shutoff', shutoffDelP)
    vForce_open_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                               'open', shutoffDelP)
    vForce_close_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                                'close', shutoffDelP)

    vForce = vForce_[0]
    vForce_shutoff = vForce_shutoff_[0]
    vForce_open = vForce_open_[0]
    vForce_close = vForce_close_[0]

    aForce = actuatorForce(size, stroke, r1, r2, setPressure)
    springrate = aForce[0]
    sfMin = aForce[1]
    sfMax = aForce[2]
    natMax = aForce[3]
    natMin = aForce[4]
    with app.app_context():
        if d1 in [1, 3, 8, 11, 4]:
            d1 = round(d1)
        friction_element = db.session.query(packingFriction).filter_by(stemDia=d3, pressure=rating).first()
        a_ = {'ptfe1': friction_element.ptfe1, 'ptfe2': friction_element.ptfe2, 'ptfer': friction_element.ptfer,
              'graphite': friction_element.graphite}
        sf_element = db.session.query(seatLoad).filter_by(trimtype=trimtype, seatBore=d1).first()
        b_ = {'six': sf_element.six, 'two': sf_element.two, 'three': sf_element.three, 'four': sf_element.four,
              'five': sf_element.five}
        print(f"trimtype and d1: {trimtype}, {d1}")
        B = float(a_[material])
        C = math.pi * d1 * float(b_[leakageClass])
        # get kn value for balanced under case
        kn_element = db.session.query(knValue).filter_by(portDia=d1, flowDir=flow, flowCharac=flowChar,
                                                         trimType=trimtype).first()
        if kn_element:
            kn_value = float(kn_element.kn)
        else:
            kn_value = 0
        print(f"Packing friction: {B}, Seat Load Force: {round(C, 3)}, kn value: {kn_value}")
        print(f"Kn inputs: portDia: {d1}, flow direction: {flow}, flow character: {flowChar}, trim type: {trimtype}")
    # print(f"Valve Forces: Shutoff: {vForce_shutoff}, Shutoff+: {vForce}, Open: {vForce_open}, Close: {vForce_close}")
    result, comment1, comment2, comment3 = None, None, None, None
    if vForce < 0:
        del_P = (aForce[1] - B - C) / vForce_[1]
        if aForce[0] > (2 * vForce_[1] / valveTravel) * del_P:
            pass
    ks = springrate
    if balance == 'unbalanced' and flow == 'under':
        kn = 0
    elif balance == 'balanced' and flow == 'over':
        kn = 0
    elif balance == 'unbalanced' and flow == 'over':
        kn = (2 * vForce_[1] / valveTravel)
    else:
        if kn_value == 0:
            kn = (2 * vForce_[1] / valveTravel)
        else:
            kn = kn_value
    # print(f"Unbalanced area: {vForce_[1]}")
    if failAction == 'AFC':
        if natMin > B:
            case1 = True
            comment1 = f"natMin > Friction force: {natMin} > {B}"
        else:
            case1 = False
            comment1 = f"natMin < Friction force: {natMin} < {B}"

        if sfMin > vForce:
            comment2 = f'Spring Force Min: {sfMin}, valveForce: {vForce}'
            case2 = True
        else:
            comment2 = f'Spring Force Min: {sfMin}, valveForce: {vForce}'
            case2 = False

        if vForce:
            a_ = ((sfMin - B - C) / vForce_[1]) * kn

            if ks > a_:
                comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
            else:
                comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
        if case1 and case2:
            result = 'Pass'
        else:
            result = f"Fail{case1}, {case2}"
    else:
        if sfMin > B:
            case1 = True
            comment1 = f"sfMin > Friction force: {sfMin} > {B}"
        else:
            case1 = False
            comment1 = f"sfMin < Friction force: {sfMin} < {B}"

        if natMin > vForce:
            comment2 = f'Net Air Thrust Min: {natMin}, valveForce: {vForce}'
            case2 = True
        else:
            comment2 = f'Net Air Thrust Min: {natMin}, valveForce: {vForce}'
            case2 = False

        a_ = ((natMin - B - C) / vForce_[1]) * kn
        if ks > a_:
            comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"
        else:
            comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"

        if case1 and case2:
            result = 'Pass'
        else:
            result = f"Fail{case1}, {case2}"

    result_list = [result, springrate, sfMax, sfMin, natMax, natMin, B, C, vForce, vForce_shutoff, vForce_close,
                   vForce_open, comment1, comment2, comment3, kn, b_[leakageClass]]
    print(result_list)
    return result_list


test_case_a = {'inletPressure': 275.5, 'outletPressure': 0, 'seatDia': 1, 'plugDia': 1.25, 'stemDia': 0.5, 'ua': 0.785,
               'rating': 150, 'material': 'ptfe1', 'leakageClass': 'four', 'trimType': 'contour',
               'balance': 'unbalanced',
               'direction': 'under', 'case': 'shutoff+', 'shutoffDelP': 19, 'acSize': 38, 'stroke': 0.75, 'lower': 12,
               'higher': 24,
               'setPressure': 60,
               'failAction': 'AFC', 'valveTravel': 0.75}
test_case_b = {'inletPressure': 217.5, 'outletPressure': 72.5, 'seatDia': 4.375, 'plugDia': 4.449, 'stemDia': 0.75,
               'ua': 15.02,
               'rating': 150, 'material': 'ptfe1', 'leakageClass': 'four', 'trimType': 'cage', 'balance': 'unbalanced',
               'direction': 'under', 'case': 'shutoff+', 'acSize': 300, 'stroke': 2.25, 'lower': 27, 'higher': 40,
               'setPressure': 50,
               'failAction': 'AFC', 'valveTravel': 2.25}
test_case_c = {'inletPressure': 19, 'outletPressure': 0, 'seatDia': 4.375, 'plugDia': 4.449, 'stemDia': 0.75,
               'ua': 15.03,
               'rating': 150, 'material': 'ptfe1', 'leakageClass': 'four', 'trimType': 'cage', 'balance': 'unbalanced',
               'direction': 'under', 'case': 'shutoff+', 'acSize': 300, 'stroke': 2.25, 'lower': 27, 'higher': 40,
               'setPressure': 50,
               'failAction': 'AFC', 'valveTravel': 2.25}

test_case_1 = test_case_a
# print(compareForces(test_case_1['inletPressure'], test_case_1['outletPressure'], test_case_1['seatDia'],
#                     test_case_1['plugDia'],
#                     test_case_1['stemDia'], test_case_1['ua'], test_case_1['rating'], test_case_1['material'],
#                     test_case_1['leakageClass'],
#                     test_case_1['trimType'], test_case_1['balance'], test_case_1['direction'], test_case_1['case'], test_case_1['shutoffDelP'],
#                     test_case_1['acSize'],
#                     test_case_1['stroke'], test_case_1['lower'], test_case_1['higher'], test_case_1['setPressure'],
#                     test_case_1['failAction'], test_case_1['valveTravel']))
# TODO ------------------------------------------ FLASK ROUTING --------------------------------------- #
with app.app_context():
    item_all = itemMaster.query.all()
    selected_item = item_all[0]

# print(pressure_unit_list)

# dict for globe valve
globe_dict_list = [
    {'id': 1, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under', 'rating': '300',
     'valvesize': 3, 'seatbore': 4.437, 'travel': 1.5, 'coeff': 'cv',
     'one': 4.05, 'two': 6.84, 'three': 10, 'four': 15, 'five': 23.8, 'six': 37.8, 'seven': 59, 'eight': 87.1,
     'nine': 110, 'ten': 121, 'fl': 0.89},
    {'id': 2, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under',
     'rating': '300', 'valvesize': 4, 'seatbore': 4.375, 'travel': 2, 'coeff': 'cv',
     'one': 6.56, 'two': 11.4, 'three': 17.3, 'four': 27, 'five': 42.2, 'six': 66.4, 'seven': 103,
     'eight': 146, 'nine': 184, 'ten': 203, 'fl': 0.91},
    {'id': 3, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under', 'rating': '300',
     'valvesize': 6, 'seatbore': 7, 'travel': 2, 'coeff': 'cv',
     'one': 13.2, 'two': 24.6, 'three': 41.1, 'four': 62.2, 'five': 97.1, 'six': 155, 'seven': 223, 'eight': 286,
     'nine': 326, 'ten': 357, 'fl': 0.86}
]

table_data_render = [
    {'name': 'Project Data', 'db': projectMaster, 'id': 1},
    {'name': 'Industry Data', 'db': industryMaster, 'id': 2},
    {'name': 'Region Data', 'db': regionMaster, 'id': 3},
    {'name': 'Status', 'db': statusMaster, 'id': 4},
    {'name': 'Customer', 'db': customerMaster, 'id': 5},
    {'name': 'Engineer', 'db': engineerMaster, 'id': 6},
    {'name': 'Item', 'db': itemMaster, 'id': 7},
    {'name': 'Model', 'db': modelMaster, 'id': 8},
    {'name': 'Valve Series', 'db': valveSeries, 'id': 9},
    {'name': 'Valve Style', 'db': valveStyle, 'id': 10},
    {'name': 'Valve Size', 'db': valveSize, 'id': 11},
    {'name': 'Rating', 'db': rating, 'id': 12},
    {'name': 'Material', 'db': materialMaster, 'id': 13},
    {'name': 'Item Cases', 'db': itemCases, 'id': 14},
    {'name': 'Valve Details', 'db': valveDetails, 'id': 15},
    {'name': 'Standard Master', 'db': standardMaster, 'id': 16},
    {'name': 'Fluid Type', 'db': fluidType, 'id': 17},
    {'name': 'Application', 'db': applicationMaster, 'id': 18},
    {'name': 'End Connection', 'db': endConnection, 'id': 19},
    {'name': 'End Finish', 'db': endFinish, 'id': 20},
    {'name': 'Bonnet Type', 'db': bonnetType, 'id': 21},
    {'name': 'PackingT ype', 'db': packingType, 'id': 22},
    {'name': 'Packing Material', 'db': packingMaterial, 'id': 23},
    {'name': 'Trim Type', 'db': trimType, 'id': 24},
    {'name': 'Flow Direction', 'db': flowDirection, 'id': 25},
    {'name': 'Project Data', 'db': seatLeakageClass, 'id': 26},
    {'name': 'Body Bonnet', 'db': bodyBonnet, 'id': 27},
    {'name': 'Soft Parts Material', 'db': softPartsMaterial, 'id': 28},
    {'name': 'Fluid Name', 'db': fluidName, 'id': 29},
    {'name': 'Valve Balancing', 'db': valveBalancing, 'id': 30},
    {'name': 'Actuator Series', 'db': actuatorSeries, 'id': 31},
    {'name': 'Actuator Size', 'db': actuatorSize, 'id': 32},
    {'name': 'Handweel', 'db': handweel, 'id': 33},
    {'name': 'Travel Stops', 'db': travelStops, 'id': 34},
    {'name': 'Butterfly Table', 'db': butterflyTable, 'id': 35},
    {'name': 'Globe Table', 'db': globeTable, 'id': 36},
    {'name': 'Schedule', 'db': schedule, 'id': 37},
    {'name': 'Fail Action', 'db': failAction, 'id': 38},
    {'name': 'Positioner MakeModel', 'db': positionerMakeModel, 'id': 39},
    {'name': 'Airset', 'db': airset, 'id': 40},
    {'name': 'Solenoid Valve', 'db': solenoidValve, 'id': 41},
    {'name': 'Lock Valve', 'db': lockValve, 'id': 42},
    {'name': 'QevBoosters', 'db': qevBoosters, 'id': 43},
    {'name': 'Pilot Valve', 'db': pilotValve, 'id': 44},
    {'name': 'Switch Position', 'db': switchPosition, 'id': 45},
    {'name': 'IPConverter', 'db': IPConverter, 'id': 46},
    {'name': 'Air Receiver', 'db': airReceiver, 'id': 47},
    {'name': 'Tubing', 'db': tubing, 'id': 48},
    {'name': 'Fittings', 'db': fittings, 'id': 49},
    {'name': 'Cleaning', 'db': cleaning, 'id': 50},
    {'name': 'Certification', 'db': certification, 'id': 51},
    {'name': 'Paint Finish', 'db': paintFinish, 'id': 52},
    {'name': 'Paint Certs', 'db': paintCerts, 'id': 53},
]

globe_dict_list_id = {
    1: {'id': 1, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under',
        'rating': '300',
        'valvesize': 3, 'seatbore': 4.437, 'travel': 1.5, 'coeff': 'cv',
        'one': 4.05, 'two': 6.84, 'three': 10, 'four': 15, 'five': 23.8, 'six': 37.8, 'seven': 59, 'eight': 87.1,
        'nine': 110, 'ten': 121, 'fl': 0.89},
    2: {'id': 2, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under',
        'rating': '300', 'valvesize': 4, 'seatbore': 4.375, 'travel': 2, 'coeff': 'cv',
        'one': 6.56, 'two': 11.4, 'three': 17.3, 'four': 27, 'five': 42.2, 'six': 66.4, 'seven': 103,
        'eight': 146, 'nine': 184, 'ten': 203, 'fl': 0.91},
    3: {'id': 3, 'valvetype': 'globe', 'trimtype': 'contour', 'flowcharac': 'equal', 'flowdir': 'under',
        'rating': '300',
        'valvesize': 6, 'seatbore': 7, 'travel': 2, 'coeff': 'cv',
        'one': 13.2, 'two': 24.6, 'three': 41.1, 'four': 62.2, 'five': 97.1, 'six': 155, 'seven': 223, 'eight': 286,
        'nine': 326, 'ten': 357, 'fl': 0.86}
}


def convert_project_data(project_list):
    data_update_list2 = []

    with app.app_context():
        for i in project_list:
            industry_updated = db.session.query(industryMaster).filter_by(id=i.IndustryId).first()
            region_updated = db.session.query(regionMaster).filter_by(id=i.regionID).first()
            status_updated = db.session.query(statusMaster).filter_by(id=i.statusID).first()
            customer_updated = db.session.query(customerMaster).filter_by(id=i.customerID).first()
            engineer_updated = db.session.query(engineerMaster).filter_by(id=i.engineerID).first()

            if region_updated:
                region_updated = region_updated
            else:
                region_updated = db.session.query(regionMaster).filter_by(id=1).first()

            if industry_updated:
                industry_updated = industry_updated
            else:
                industry_updated = db.session.query(industryMaster).filter_by(id=1).first()

            if status_updated:
                status_updated = status_updated
            else:
                status_updated = db.session.query(statusMaster).filter_by(id=1).first()

            if customer_updated:
                customer_updated = customer_updated
            else:
                customer_updated = db.session.query(customerMaster).filter_by(id=1).first()

            if engineer_updated:
                engineer_updated = engineer_updated
            else:
                engineer_updated = db.session.query(engineerMaster).filter_by(id=1).first()

            project_updated = {"id": i.id, "quote": i.quote, "received_date": i.received_date.date(),
                               "work_order": i.work_order,
                               "due_date": i.due_date.date(), "IndustryID": industry_updated.name,
                               "regionID": region_updated.name,
                               "statusID": status_updated.name, "customerID": customer_updated.name,
                               "engineerID": engineer_updated.name}
            # print(type(i.received_date))

            data_update_list2.append(project_updated)
    return data_update_list2


def convert_item_data(list_item):
    data_list = []
    with app.app_context():
        for i in list_item:
            serial_updated = db.session.query(valveSeries).filter_by(id=i.serialID).first()
            size_updated = db.session.query(valveSize).filter_by(id=i.sizeID).first()
            model_updated = db.session.query(modelMaster).filter_by(id=i.modelID).first()
            type_updated = db.session.query(valveStyle).filter_by(id=i.typeID).first()
            rating_updated = db.session.query(rating).filter_by(id=i.ratingID).first()
            material_updated = db.session.query(materialMaster).filter_by(id=i.materialID).first()

            if serial_updated:
                serial_updated = serial_updated
            else:
                serial_updated = db.session.query(valveSeries).filter_by(id=1).first()

            if size_updated:
                size_updated = size_updated
            else:
                size_updated = db.session.query(valveSize).filter_by(id=5).first()

            if model_updated:
                model_updated = model_updated
            else:
                model_updated = db.session.query(modelMaster).filter_by(id=1).first()

            if type_updated:
                type_updated = type_updated
            else:
                type_updated = db.session.query(valveStyle).filter_by(id=1).first()

            if rating_updated:
                rating_updated = rating_updated
            else:
                rating_updated = db.session.query(rating).filter_by(id=1).first()

            if material_updated:
                material_updated = material_updated
            else:
                material_updated = db.session.query(materialMaster).filter_by(id=1).first()

            item_updated = {"id": i.id, "alt": i.alt, "tag_no": i.tag_no, "unit_price": i.unit_price,
                            "qty": 1, "projectID": i.projectID, "serialID": serial_updated.name,
                            "sizeID": size_updated.size, "modelID": model_updated.name, "typeID": type_updated.name,
                            "ratingID": rating_updated.size, "materialID": material_updated.name}
            data_list.append(item_updated)
    return data_list


# Website routes
@app.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()

        data = projectMaster.query.all()
        data2 = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = data2.index(item_details)

        data_update_list2 = convert_project_data(data)
        item_list = convert_item_data(data2)
        len_items = len(item_list)
        proj_id = 1

        if request.method == 'POST':
            projectId = int(request.form['projects'])
            # print(projectId)
            proj_id_2 = projectId
            data = projectMaster.query.all()
            data3 = db.session.query(itemMaster).filter_by(projectID=projectId).all()
            item_index = 1
            data_updated_list = convert_project_data(data)
            item_list = convert_item_data(data3)
            len_items = len(item_list)

            return render_template("dashboard_with_db.html", title='Dashboard', data=data_updated_list, data2=item_list,
                                   item_d=item_details, p_id=proj_id_2, page='home', item_index=item_index,
                                   len_items=len_items)

        return render_template("dashboard_with_db.html", title='Dashboard', data=data_update_list2, data2=item_list,
                               item_d=item_details, p_id=proj_id, page='home', item_index=item_index,
                               len_items=len_items)


# Website routes
@app.route('/get-proj/<proj_id>', methods=["GET", "POST"])
def getItemProject(proj_id):
    global selected_item
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        # print(projectId)
        proj_id_2 = int(proj_id)
        data = projectMaster.query.all()
        data3 = db.session.query(itemMaster).filter_by(projectID=proj_id).all()
        data_updated_list = convert_project_data(data)
        item_list = convert_item_data(data3)
        selected_item = data3[0]
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        item_index = data3.index(item_details)
        len_items = len(item_list)

        return render_template("dashboard_with_db.html", title='Dashboard', data=data_updated_list, data2=item_list,
                               item_d=item_details, p_id=proj_id_2, page='home', item_index=item_index,
                               len_items=len_items)


@app.route('/filter', methods=["GET", "POST"])
def filter_dashboard():
    with app.app_context():
        if request.method == "POST":
            filer_criter = request.form.get('filter_criteria')
            search_c = request.form.get('search')
            filter_list = {'IndustryId': industryMaster, 'regionID': regionMaster, 'engineerID': engineerMaster,
                           'statusID': statusMaster, 'quote': 0, 'work_order': 0, 'customerID': customerMaster}
            if filer_criter == 'IndustryId':
                industry_e = db.session.query(industryMaster).filter_by(name=search_c).first()
                if industry_e:
                    project_data = db.session.query(projectMaster).filter_by(IndustryId=industry_e.id).all()
                else:
                    project_data = projectMaster.query.all()

                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'regionID':
                region_e = db.session.query(regionMaster).filter_by(name=search_c).first()
                if region_e:
                    project_data = db.session.query(projectMaster).filter_by(regionID=region_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'engineerID':
                engineer_e = db.session.query(engineerMaster).filter_by(name=search_c).first()
                if engineer_e:
                    project_data = db.session.query(projectMaster).filter_by(engineerID=engineer_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'statusID':
                status_e = db.session.query(statusMaster).filter_by(name=search_c).first()
                if status_e:
                    project_data = db.session.query(projectMaster).filter_by(statusID=status_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'quote':
                project_data = db.session.query(projectMaster).filter_by(quote=search_c).all()
                if project_data:
                    data_update_list2 = convert_project_data(project_data)
                else:
                    project_data = projectMaster.query.all()
                    data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'work_order':
                project_data = db.session.query(projectMaster).filter_by(work_order=search_c).all()
                if project_data:
                    data_update_list2 = convert_project_data(project_data)
                else:
                    project_data = projectMaster.query.all()
                    data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'customerID':
                customer_e = db.session.query(customerMaster).filter_by(name=search_c).first()
                if customer_e:
                    project_data = db.session.query(projectMaster).filter_by(customerID=customer_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
            data2 = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
            item_index = data2.index(item_details)
            item_list = convert_item_data(data2)
            len_items = len(item_list)

            return render_template("dashboard_with_db.html", title='Dashboard', data=data_update_list2, data2=item_list,
                                   item_d=selected_item, page='home', item_index=item_index, len_items=len_items)


@app.route('/items/<item_id>', methods=["GET", "POST"])
def getItems(item_id):
    global selected_item
    with app.app_context():
        item_1 = db.session.query(itemMaster).filter_by(id=int(item_id)).first()
        selected_item = item_1

    return redirect(url_for('home'))


#
# @app.route('/select-item', methods=["GET", "POST"])
# def selectItem():
#     if request.method == "POST":
#         item_ = request.form.get('item')
#         print(item_)
#     with app.app_context():
#         data = projectMaster.query.all()
#         data2 = itemMaster.query.all()
#
#     return redirect(url_for('home'))
# #
# with app.app_context():
#     items_all = itemCases.query.all()
#     for i in items_all:
#         if i.valveSPL:
#             i.valveSPL = round(i.valveSPL, 2)
#         if i.iVelocity:
#             i.iVelocity = round(i.iVelocity, 2)
#         if i.oVelocity:
#             i.oVelocity = round(i.oVelocity, 2)
#         if i.pVelocity:
#             i.pVelocity = round(i.pVelocity, 2)
#         i.chokedDrop = round(i.chokedDrop, 2)
#         db.session.commit()


@app.route('/project-details', methods=["GET", "POST"])
def projectDetails():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = item_list.index(item_details)
    if request.method == 'POST':
        customer = request.form.get('customer')
        engRef = request.form.get('eRef')
        enqDate = request.form.get('eDate')
        recDate_1 = request.form.get('rDate')
        recDate = datetime.datetime.strptime(recDate_1, '%Y-%m-%d')
        aEng = request.form.get('aEng')
        bDate_1 = request.form.get('bDate')
        bDate = datetime.datetime.strptime(bDate_1, '%Y-%m-%d')
        purpose = request.form.get('purpose')
        industry = request.form.get('industry')
        region = request.form.get('region')
        projectRev = request.form.get('projectRev')
        cEng = request.form.get('cEng')
        cNo = request.form.get('cNo')
        wNo = request.form.get('wNo')
        with app.app_context():
            customer_element = db.session.query(customerMaster).filter_by(name=customer).first()
            engineer_element = db.session.query(engineerMaster).filter_by(name=aEng).first()
            industry_element = db.session.query(industryMaster).filter_by(name=industry).first()
            region_element = db.session.query(regionMaster).filter_by(name=region).first()

            # print(wNo)

            new_project = projectMaster(industry=industry_element, region=region_element, quote=purpose,
                                        customer=customer_element,
                                        received_date=recDate,
                                        engineer=engineer_element,
                                        work_order=wNo,
                                        due_date=bDate,
                                        status=status_element_1)

            # Add dummy new item
            model_element = db.session.query(modelMaster).filter_by(name='Model_1').first()
            serial_element = db.session.query(valveSeries).filter_by(id=1).first()
            size_element = db.session.query(valveSize).filter_by(id=1).first()
            rating_element = db.session.query(rating).filter_by(id=1).first()
            material_element = db.session.query(materialMaster).filter_by(id=1).first()
            type_element = db.session.query(valveStyle).filter_by(id=1).first()

            item4 = {"alt": 'A', "tagNo": 101, "serial": serial_element, "size": size_element,
                     "model": model_element, "type": type_element, "rating": rating_element,
                     "material": material_element, "unitPrice": 1, "Quantity": 13221, "Project": new_project}

            itemsList__ = [item4]

            for i in itemsList__:
                new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'],
                                      model=i['model'],
                                      type=i['type'], rating=i['rating'], material=i['material'],
                                      unit_price=i['unitPrice'],
                                      qty=i['Quantity'], project=i['Project'])

                db.session.add(new_item)
                db.session.commit()

                new_valve_details = valveDetails(tag=1, quantity=1,
                                                 application='None',
                                                 serial_no=1,
                                                 rating=1,
                                                 body_material=1,
                                                 shutOffDelP=1,
                                                 maxPressure=1,
                                                 maxTemp=1,
                                                 minTemp=1,
                                                 valve_series=1,
                                                 valve_size=1,
                                                 rating_v=1,
                                                 ratedCV='globe',
                                                 endConnection_v=1,
                                                 endFinish_v=1,
                                                 bonnetType_v=1,
                                                 bonnetExtDimension=1,
                                                 packingType_v='Liquid',
                                                 trimType_v=1,
                                                 flowCharacter_v=1,
                                                 flowDirection_v=1,
                                                 seatLeakageClass_v=1, body_v=1,
                                                 bonnet_v=1,
                                                 nde1=1, nde2=1, plug=1, stem=1, seat=1,
                                                 cage_clamp=None,
                                                 balanceScale=1, packing=1, stud_nut=1, gasket=1,
                                                 item=new_item)

                db.session.add(new_valve_details)
                db.session.commit()

            db.session.add(new_project)
            db.session.commit()

            return render_template("Project Details.html", title='Project Details', item_d=selected_item,
                                   page='projectDetails', item_index=item_index)

    return render_template("Project Details.html", title='Project Details', item_d=selected_item, page='projectDetails',
                           item_index=item_index)


# @app.route('/valve-selection', methods=["GET", "POST"])
# def valveSelection():
#     # get data from db to give in template
#     with app.app_context():
#         rating_list = rating.query.all()
#         material_list = materialMaster.query.all()
#         series_list = valveSeries.query.all()
#         size_list = valveSize.query.all()  # size
#         end_connection = endConnection.query.all()  # name
#         end_finish = endFinish.query.all()  # name
#         bonnet_type = bonnetType.query.all()  # name
#         packing_type = packingType.query.all()
#         trim_type = trimType.query.all()
#         flow_charac = [{"id": 1, "name": "Equal %"}, {"id": 2, "name": "Linear"}]
#         flow_direction = flowDirection.query.all()
#         seat_leakage = seatLeakageClass.query.all()
#
#     template_list = [rating_list, material_list, series_list, size_list, end_finish, end_connection, bonnet_type,
#                      packing_type, trim_type, flow_charac, flow_direction, seat_leakage]
#
#     if request.method == 'POST':
#         if request.form.get('update'):
#             with app.app_context():
#                 itemdetails = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
#                 valvesDetails = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).all()
#                 if len(valvesDetails) > 0:
#                     return f"Valve Details already exists"
#                 else:
#                     new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
#                                                      application=request.form.get('application'),
#                                                      serial_no=request.form.get('sNo'),
#                                                      rating=request.form.get('ratingP'),
#                                                      body_material=request.form.get('bMaterial'),
#                                                      shutOffDelP=request.form.get('shutOffP'),
#                                                      maxPressure=request.form.get('maxP'),
#                                                      maxTemp=request.form.get('maxT'),
#                                                      minTemp=request.form.get('minT'),
#                                                      valve_series=request.form.get('vSeries'),
#                                                      valve_size=request.form.get('vSize'),
#                                                      rating_v=request.form.get('ratingV'),
#                                                      ratedCV=request.form.get('cv'),
#                                                      endConnection_v=request.form.get('endConnection'),
#                                                      endFinish_v=request.form.get('endFinish'),
#                                                      bonnetType_v=request.form.get('bonnetType'),
#                                                      bonnetExtDimension=request.form.get('bed'),
#                                                      packingType_v=request.form.get('packingType'),
#                                                      trimType_v=request.form.get('trimType'),
#                                                      flowCharacter_v=request.form.get('flowCharacter'),
#                                                      flowDirection_v=request.form.get('flowDirection'),
#                                                      seatLeakageClass_v=request.form.get('SLClass'), body_v=None,
#                                                      bonnet_v=None,
#                                                      nde1=None, nde2=None, plug=None, stem=None, seat=None,
#                                                      cage_clamp=None,
#                                                      balanceScale=None, packing=None, stud_nut=None, gasket=None,
#                                                      item=itemdetails)
#
#                     db.session.add(new_valve_details)
#                     db.session.commit()
#
#             return f"Suceess"
#         elif request.form.get('new'):
#             pass
#
#     return render_template("Valve Selection.html", title='Valve Selection', data=template_list, item_d=selected_item)


def getValveDetailsData(valve_element):
    with app.app_context():
        #
        tag_no = valve_element.tag
        quantity = valve_element.quantity
        application = valve_element.application
        rating_id = int(valve_element.rating)
        bMaterial_id = int(valve_element.body_material)
        delP_shutoff = valve_element.shutOffDelP
        maxPressure = valve_element.maxPressure
        maxTemp = valve_element.maxTemp
        minTemp = valve_element.minTemp
        #
        valve_series = int(valve_element.valve_series)
        end_connection = int(valve_element.endConnection_v)
        end_finish = int(valve_element.endFinish_v)
        bonnet_type = int(valve_element.bonnetType_v)
        bonnet_ext_dimension = valve_element.bonnetExtDimension
        trim_type = int(valve_element.trimType_v)
        flow_character = int(valve_element.flowCharacter_v)
        flow_direction = int(valve_element.flowDirection_v)
        leakage_class = int(valve_element.seatLeakageClass_v)
        #
        bonnet = int(valve_element.bonnet_v)
        nde1 = int(valve_element.nde1)
        nde2 = int(valve_element.nde2)
        plug_trim_disc = int(valve_element.plug)
        seat_soft_seat = int(valve_element.seatLeakageClass_v)
        stem_shaft = int(valve_element.stem)
        packing = int(valve_element.packing)
        balance_seal = valve_element.balanceScale
        stud_nut = int(valve_element.stud_nut)
        gasket = int(valve_element.gasket)

        v_det_dict = {'tag_no': tag_no, 'quantity': quantity, 'application': application, 'rating_id': rating_id,
                      'body_material': bMaterial_id, 'shutoffDelP': delP_shutoff, 'maxPressure': maxPressure,
                      'maxTemp': maxTemp,
                      'minTemp': minTemp, 'valve_series': valve_series, 'end_connection': end_connection,
                      'end_finish': end_finish,
                      'bonnet_type': bonnet_type, 'bonnet_ext_dimension': bonnet_ext_dimension, 'trim_type': trim_type,
                      'flow_character': flow_character,
                      'flow_direction': flow_direction, 'leakage_class': leakage_class, 'bonnet': bonnet, 'nde1': nde1,
                      'nde2': nde2,
                      'plug': plug_trim_disc, 'seat': seat_soft_seat, 'stem': stem_shaft, 'packing': packing,
                      'balance_seal': balance_seal, 'stud_nut': stud_nut, 'gasket': gasket}

        return v_det_dict


def getValveDetailsAll():
    rating_list = rating.query.all()
    material_list = materialMaster.query.all()
    series_list = valveSeries.query.all()
    size_list = valveSize.query.all()  # size
    end_connection = endConnection.query.all()  # name
    end_finish = endFinish.query.all()  # name
    bonnet_type = bonnetType.query.all()  # name
    packing_type = packingType.query.all()
    trim_type = trimType.query.all()
    nde = bodyBonnet.query.all()
    flow_charac = [{"id": 1, "name": "Equal %"}, {"id": 2, "name": "Linear"}]
    flow_direction = flowDirection.query.all()
    seat_leakage = seatLeakageClass.query.all()
    applications_data = applicationMaster.query.all()
    # series = valveSeries.query.all()
    itemdetails = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
    valve_element_db = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).first()
    case_element_db_all = itemMaster.query.all()
    item_1_index = case_element_db_all.index(itemdetails)
    case_element_db = case_element_db_all[item_1_index]
    vType_db = valve_element_db.ratedCV
    fState_db = valve_element_db.packingType_v

    # get default Values from valveDetails
    if valve_element_db:
        v_dict = getValveDetailsData(valve_element_db)
    else:
        v_dict = {}
    print(v_dict)
    # get valve type material details
    b_stem_mat = db.session.query(valveTypeMaterial).filter_by(valveType='butterfly', data='shaft').all()
    b_disc_mat = db.session.query(valveTypeMaterial).filter_by(valveType='butterfly', data='disc').all()
    b_seat_mat = db.session.query(valveTypeMaterial).filter_by(valveType='butterfly', data='seat').all()
    b_packing_mat = db.session.query(valveTypeMaterial).filter_by(valveType='butterfly', data='packing').all()
    g_trim_mat = db.session.query(valveTypeMaterial).filter_by(valveType='globe', data='trim').all()
    g_seat_mat = db.session.query(valveTypeMaterial).filter_by(valveType='globe', data='seat').all()
    g_packing_mat = db.session.query(valveTypeMaterial).filter_by(valveType='globe', data='packing').all()
    g_stem_mat = db.session.query(valveTypeMaterial).filter_by(valveType='globe', data='stem').all()
    stud = db.session.query(valveTypeMaterial).filter_by(data='stud').all()
    gasket = db.session.query(valveTypeMaterial).filter_by(data='gasket').all()
    v_materials = [b_stem_mat, b_disc_mat, b_seat_mat, b_packing_mat, g_trim_mat, g_seat_mat, g_packing_mat,
                   g_stem_mat, stud, gasket]
    if vType_db == 'globe':
        type_list = ['Globe', 'Butterfly']
    else:
        type_list = ['Butterfly', 'Globe']

    if fState_db == 'Gas':
        state_list = ['Gas', 'Liquid', 'Two Phase']
    elif fState_db == 'Liquid':
        state_list = ['Liquid', 'Gas', 'Two Phase']
    else:
        state_list = ['Two Phase', 'Gas', 'Liquid']

    # print(state_list, type_list, vType_db, fState_db)

    template_list = [rating_list, material_list, series_list, size_list, end_finish, end_connection, bonnet_type,
                     packing_type, trim_type, flow_charac, flow_direction, seat_leakage, applications_data,
                     type_list, state_list, nde]
    return template_list, v_materials, vType_db, v_dict


@app.route('/valve-selection', methods=["GET", "POST"])
def valveSelection():
    # get data from db to give in template
    with app.app_context():
        template_list, v_materials, vType_db, v_dict = getValveDetailsAll()
        itemdetails = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        if request.method == 'POST':
            vstyle = request.form.get('vStyle')
            if vstyle == 'Globe':
                plug, stem, seat, packing = request.form.get('trim_g'), request.form.get('stem_g'), request.form.get(
                    'seat_g'), request.form.get('packing_g')
            else:
                plug, stem, seat, packing = request.form.get('disc_b'), request.form.get('shaft_b'), request.form.get(
                    'seat_b'), request.form.get('packing_b')

            if request.form.get('update'):
                valvesDetails = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).all()
                valve_element = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).first()
                template_list, v_materials, vType_db, v_dict = getValveDetailsAll()
                if len(valvesDetails) > 0:
                    valve_element.tag = request.form.get('tag')
                    valve_element.quantity = request.form.get('qty')
                    valve_element.application = request.form.get('application')
                    # valve_element.serial_no = request.form.get('sNo')
                    valve_element.rating = request.form.get('ratingP')
                    valve_element.body_material = request.form.get('bMaterial')
                    valve_element.shutOffDelP = request.form.get('shutOffP')
                    valve_element.maxPressure = request.form.get('maxP')
                    valve_element.maxTemp = request.form.get('maxT')
                    valve_element.minTemp = request.form.get('minT')
                    valve_element.valve_series = request.form.get('vSeries')
                    # valve_element.valve_size = request.form.get('vSize')
                    # valve_element.rating_v = request.form.get('ratingV')
                    valve_element.ratedCV = request.form.get('vStyle')
                    valve_element.endConnection_v = request.form.get('endConnection')
                    valve_element.endFinish_v = request.form.get('endFinish')
                    valve_element.bonnetType_v = request.form.get('bonnetType')
                    valve_element.bonnetExtDimension = request.form.get('bed')
                    valve_element.packingType_v = request.form.get('fState')
                    valve_element.trimType_v = request.form.get('trimType')
                    valve_element.flowCharacter_v = request.form.get('flowCharacter')
                    valve_element.flowDirection_v = request.form.get('flowDirection')
                    valve_element.seatLeakageClass_v = request.form.get('SLClass')
                    valve_element.body_v = 'ported'
                    valve_element.bonnet_v = request.form.get('bonnetMaterial')
                    valve_element.nde1 = request.form.get('nde1')
                    valve_element.nde2 = request.form.get('nde2')
                    valve_element.plug = plug
                    valve_element.stem = stem
                    valve_element.seat = seat
                    # valve_element.cage_clamp = None
                    valve_element.balanceScale = request.form.get('balance_seal')
                    valve_element.packing = packing
                    valve_element.stud_nut = request.form.get('stud')
                    valve_element.gasket = request.form.get('gasket')
                    valve_element.item = itemdetails
                    db.session.commit()
                else:
                    new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
                                                     application=request.form.get('application'),
                                                     serial_no=request.form.get('sNo'),
                                                     rating=request.form.get('ratingP'),
                                                     body_material=request.form.get('bMaterial'),
                                                     shutOffDelP=request.form.get('shutOffP'),
                                                     maxPressure=request.form.get('maxP'),
                                                     maxTemp=request.form.get('maxT'),
                                                     minTemp=request.form.get('minT'),
                                                     valve_series=request.form.get('vSeries'),
                                                     valve_size=request.form.get('vSize'),
                                                     rating_v=request.form.get('ratingV'),
                                                     ratedCV=request.form.get('vStyle'),
                                                     endConnection_v=request.form.get('endConnection'),
                                                     endFinish_v=request.form.get('endFinish'),
                                                     bonnetType_v=request.form.get('bonnetType'),
                                                     bonnetExtDimension=request.form.get('bed'),
                                                     packingType_v=request.form.get('fState'),
                                                     trimType_v=request.form.get('trimType'),
                                                     flowCharacter_v=request.form.get('flowCharacter'),
                                                     flowDirection_v=request.form.get('flowDirection'),
                                                     seatLeakageClass_v=request.form.get('SLClass'), body_v='ported',
                                                     bonnet_v=request.form.get('bonnetMaterial'),
                                                     nde1=request.form.get('nde1'), nde2=request.form.get('nde2'),
                                                     plug=plug, stem=stem, seat=seat,
                                                     balanceScale=request.form.get('balance_seal'), packing=packing,
                                                     stud_nut=request.form.get('stud'),
                                                     gasket=request.form.get('gasket'),
                                                     item=itemdetails)

                    db.session.add(new_valve_details)
                    db.session.commit()

                return redirect(url_for('valveSelection'))


            elif request.form.get('new'):
                valveType = request.form.get('vStyle')
                if valveType == 'Globe':
                    vtypeid = 1
                else:
                    vtypeid = 2

                # Add New Item first
                model_element = db.session.query(modelMaster).filter_by(name='Model_1').first()
                project_element = db.session.query(projectMaster).filter_by(id=1).first()
                serial_element = db.session.query(valveSeries).filter_by(id=int(request.form.get('vSeries'))).first()
                size_element = db.session.query(valveSize).filter_by(id=1).first()
                rating_element = db.session.query(rating).filter_by(id=1).first()
                material_element = db.session.query(materialMaster).filter_by(
                    id=int(request.form.get('bMaterial'))).first()
                type_element = db.session.query(valveStyle).filter_by(id=vtypeid).first()

                item4 = {"alt": 'A', "tagNo": request.form.get('tag'), "serial": serial_element, "size": size_element,
                         "model": model_element, "type": type_element, "rating": rating_element,
                         "material": material_element, "unitPrice": 1, "Quantity": 13221, "Project": project_element}

                itemsList = [item4]

                for i in itemsList:
                    new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'],
                                          model=i['model'],
                                          type=i['type'], rating=i['rating'], material=i['material'],
                                          unit_price=i['unitPrice'],
                                          qty=i['Quantity'], project=i['Project'])

                    db.session.add(new_item)
                    db.session.commit()

                # Add Valve Details Then
                new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
                                                 application=request.form.get('application'),
                                                 serial_no=request.form.get('sNo'),
                                                 rating=request.form.get('ratingP'),
                                                 body_material=request.form.get('bMaterial'),
                                                 shutOffDelP=request.form.get('shutOffP'),
                                                 maxPressure=request.form.get('maxP'),
                                                 maxTemp=request.form.get('maxT'),
                                                 minTemp=request.form.get('minT'),
                                                 valve_series=request.form.get('vSeries'),
                                                 valve_size=request.form.get('vSize'),
                                                 rating_v=request.form.get('vStyle'),
                                                 ratedCV=request.form.get('cv'),
                                                 endConnection_v=request.form.get('endConnection'),
                                                 endFinish_v=request.form.get('endFinish'),
                                                 bonnetType_v=request.form.get('bonnetType'),
                                                 bonnetExtDimension=request.form.get('bed'),
                                                 packingType_v=request.form.get('fState'),
                                                 trimType_v=request.form.get('trimType'),
                                                 flowCharacter_v=request.form.get('flowCharacter'),
                                                 flowDirection_v=request.form.get('flowDirection'),
                                                 seatLeakageClass_v=request.form.get('SLClass'), body_v='ported',
                                                 bonnet_v=request.form.get('bonnetMaterial'),
                                                 nde1=request.form.get('nde1'), nde2=request.form.get('nde2'),
                                                 plug=plug, stem=stem, seat=seat,
                                                 cage_clamp=None,
                                                 balanceScale=request.form.get('balance_seal'), packing=packing,
                                                 stud_nut=request.form.get('stud'), gasket=request.form.get('gasket'),
                                                 item=new_item)
                db.session.add(new_valve_details)
                db.session.commit()
                return redirect(url_for('valveSelection'))

        item_list = db.session.query(itemMaster).filter_by(projectID=itemdetails.projectID).all()
        item_index = item_list.index(itemdetails)
        return render_template("Valve Selection.html", title='Valve Selection', data=template_list,
                               item_d=selected_item, v_mat=v_materials, page='valveSelection',
                               item_index=item_index, style=vType_db, v_dict=v_dict)


def sort_list_latest(list_1, selected):
    for i in list_1:
        if i['id'] == selected:
            removing_element = i
            list_1.remove(removing_element)
            list_1.insert(0, removing_element)
            # print(f"from sort{list_1}")

    return list_1


def getPref(item):
    length_unit_list = [{'id': 'inch', 'name': 'inch'}, {'id': 'm', 'name': 'm'}, {'id': 'mm', 'name': 'mm'},
                        {'id': 'cm', 'name': 'cm'}]

    flowrate_unit_list = [{'id': 'm3/hr', 'name': 'm3/hr'}, {'id': 'scfh', 'name': 'scfh'},
                          {'id': 'gpm', 'name': 'gpm'},
                          {'id': 'lb/hr', 'name': 'lb/hr'}, {'id': 'kg/hr', 'name': 'kg/hr'}]

    pressure_unit_list = [{'id': 'bar', 'name': 'bar (a)'}, {'id': 'bar', 'name': 'bar (g)'},
                          {'id': 'kpa', 'name': 'kPa (a)'}, {'id': 'kpa', 'name': 'kPa (g)'},
                          {'id': 'mpa', 'name': 'MPa (a)'}, {'id': 'mpa', 'name': 'MPa (g)'},
                          {'id': 'pa', 'name': 'Pa (a)'}, {'id': 'pa', 'name': 'Pa (g)'},
                          {'id': 'inh20', 'name': 'in H2O (a)'}, {'id': 'inh20', 'name': 'in H2O (g)'},
                          {'id': 'inhg', 'name': 'in Hg (a)'}, {'id': 'inhg', 'name': 'in Hg (g)'},
                          {'id': 'kg/cm2', 'name': 'kg/cm2 (a)'}, {'id': 'kg/cm2', 'name': 'kg/cm2 (g)'},
                          {'id': 'mmh20', 'name': 'm H2O (a)'}, {'id': 'mmh20', 'name': 'm H2O (g)'},
                          {'id': 'mbar', 'name': 'mbar (a)'}, {'id': 'mbar', 'name': 'mbar (g)'},
                          {'id': 'mmhg', 'name': 'mm Hg (a)'}, {'id': 'mmhg', 'name': 'mm Hg (g)'},
                          {'id': 'psia', 'name': 'psi (g)'}, {'id': 'psia', 'name': 'psi (a)'}]

    pressure_unit_list2 = [{'id': 'bar', 'name': 'bar (a)'}]

    temp_unit_list = [{'id': 'C', 'name': '°C'}, {'id': 'F', 'name': '°F'}, {'id': 'K', 'name': 'K'},
                      {'id': 'R', 'name': 'R'}]

    units_pref = [length_unit_list, flowrate_unit_list, pressure_unit_list2, temp_unit_list]
    with app.app_context():
        list__ = units_pref
        item_selected = item
        a = str(item_selected.qty)  # list data
        l_unit, fr_unit, t_unit, p_unit = int(a[:1]), int(a[1:2]), int(a[2:3]), int(a[3:])
        # print(list__)
        # print(l_unit, fr_unit, t_unit, p_unit)

        return_list0 = sort_list_latest(list__[0], list__[0][l_unit - 1]['id'])  # length
        return_list1 = sort_list_latest(list__[1], list__[1][fr_unit - 1]['id'])  # flowrate
        # return_list2 = sort_list_latest(list__[2], list__[2][p_unit - 1]['id'])  # pressure
        return_list2 = pressure_unit_list2
        return_list3 = sort_list_latest(list__[3], list__[3][t_unit - 1]['id'])  # temp

        # return_list0 = sort_list_latest(list__[0], list__[0][0]['id'])  # length
        # return_list1 = sort_list_latest(list__[1], list__[1][1]['id'])  # flowrate
        # return_list2 = sort_list_latest(list__[2], list__[2][1]['id'])  # pressure
        # return_list3 = sort_list_latest(list__[3], list__[3][0]['id'])  # temp

        list_return = [return_list0, return_list1, return_list2, return_list3]
        # print(f"from getpref: {list__}")
        return list_return


def getCVresult(fl_unit_form, specificGravity, iPresUnit_form, inletPressure_form, flowrate_form, outletPressure_form,
                oPresUnit_form,
                vPresUnit_form, vaporPressure, cPresUnit_form, criticalPressure_form, inletPipeDia_form, iPipeUnit_form,
                outletPipeDia_form, oPipeUnit_form, valveSize_form, vSizeUnit_form, inletTemp_form, ratedCV, xt_fl, fd,
                viscosity, iTempUnit_form):
    # 1. flowrate
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
                                                 specificGravity * 1000)
        iPipe_unit = 'mm'
    else:
        iPipe_unit = iPipeUnit_form
        inletPipeDia_liq = inletPipeDia_form

    if oPipeUnit_form not in ['mm']:
        outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                                  'mm', specificGravity * 1000)
        oPipe_unit = 'mm'
    else:
        oPipe_unit = oPipeUnit_form
        outletPipeDia_liq = outletPipeDia_form

    if vSizeUnit_form not in ['mm']:
        vSize_liq = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)
        vSize_unit = 'mm'
    else:
        vSize_unit = vSizeUnit_form
        vSize_liq = valveSize_form

    service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                             'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                             'iPresUnit': iPres_unit,
                             'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                             'temp_unit': iTempUnit_form, 'sGravity': specificGravity,
                             'iPipeDia': inletPipeDia_liq,
                             'oPipeDia': outletPipeDia_liq,
                             'valveDia': vSize_liq, 'iPipeDiaUnit': iPipe_unit,
                             'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': vSize_unit,
                             'C': 0.075 * vSize_liq * vSize_liq, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': fd, 'viscosity': viscosity}

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
                  service_conditions_1['viscosity'], 0)

    result = CV(service_conditions_1['flowrate'], result_1,
                service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'],
                service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                service_conditions_1['oPres'],
                service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                service_conditions_1['vPres'],
                service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                service_conditions_1['viscosity'], 0)

    return result


def getCVGas(fl_unit_form, specificGravity, sg_choice, inletPressure_form, iPresUnit_form, outletPressure_form,
             oPresUnit_form, valveSize_form, vSizeUnit_form,
             flowrate_form, inletTemp_form, iTempUnit_form, ratedCV, inletPipeDia_form, iPipeUnit_form,
             outletPipeDia_form, oPipeUnit_form, xt_fl, z_factor,
             sg_vale):
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
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
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
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'kpa',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'kpa',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'C',
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
                                             1000)
        # print(iPipeUnit_form)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
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
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)

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

    # print(inputDict_4)

    inputDict = inputDict_4
    N2_val = N2['inch']

    Cv__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv_gas_final = Cv__[0]
    return Cv_gas_final


# getting kc value
def getKCValue(size__, t_type, pressure, v_type, fl):
    with app.app_context():
        kc_dict_1 = [{'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'}, {'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour',
                                           'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'}, {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour',
                                           'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (100, 9000),
                      'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (0, 75), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (75, 100), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 300),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 2), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (300, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (0, 300),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (300, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (0, 200),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '316 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 300), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '317 / Alloy 6', 'trim': 'ported',
                      'pressure': (300, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '318 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 200), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '319 / Alloy 6', 'trim': 'ported',
                      'pressure': (200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 12), 'material': '316 SST', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 12), 'material': '316 SST', 'trim': 'ported',
                                           'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (3, 4), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 200),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (3, 4), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (3, 4), 'material': '440C', 'trim': 'ported', 'pressure': (200, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (6, 12), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '440C', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '440C', 'trim': 'ported', 'pressure': (100, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '320 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 100), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '321 / Alloy 6', 'trim': 'ported',
                      'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 50),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (16, 24), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (50, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '440C', 'trim': 'ported', 'pressure': (0, 50),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '440C', 'trim': 'ported', 'pressure': (50, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '322 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 50), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '323 / Alloy 6', 'trim': 'ported',
                      'pressure': (50, 9000), 'kc_formula': '5'},
                     {'v_tye': 'butterfly', 'size': (2, 4), 'material': '-', 'trim': 'do', 'pressure': (0, 50),
                      'kc_formula': '2'},
                     {'v_tye': 'butterfly', 'size': (2, 4), 'material': '-', 'trim': 'do', 'pressure': (50, 9000),
                      'kc_formula': '3'},
                     {'v_tye': 'butterfly', 'size': (6, 36), 'material': '-', 'trim': 'do', 'pressure': (0, 9000),
                      'kc_formula': '3'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 600),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (600, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 500),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (500, 1440),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 400),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (400, 1440),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 2160),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (3, 6), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 1800),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (3, 6), 'material': '', 'trim': 'cavitrol_3_2',
                                           'pressure': (1800, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (8, 24), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 1200),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (8, 24), 'material': '', 'trim': 'cavitrol_3_2',
                                           'pressure': (1200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 24), 'material': '', 'trim': 'cavitrol_3_3', 'pressure': (0, 3000),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 12), 'material': '', 'trim': 'cavitrol_3_4', 'pressure': (0, 3000),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 12), 'material': '', 'trim': 'cavitrol_3_4',
                                           'pressure': (3000, 4000), 'kc_formula': '1'}]

        # kc = db.session.query(kcTable).filter(kcTable.min_size <= int(size__), kcTable.max_size >= int(size__),
        #                                       kcTable.trim_type == t_type,
        #                                       kcTable.min_pres <= float(pressure), kcTable.max_pres >= float(pressure),
        #                                       kcTable.valve_style == v_type).first()

        output_list_kc = []
        for kc in kc_dict_1:
            if kc['v_tye'] == v_type and (kc['size'][0] <= size__ <= kc['size'][1]) and (
                    kc['pressure'][0] <= pressure <= kc['pressure'][1]) and kc['trim'] == t_type:
                output_list_kc.append(kc)

        formula_dict = {1: 0.99, 2: 1, 3: 0.5 * fl * fl, 4: 0.85 * fl * fl, 5: fl * fl}
        print(f"output kc list: {output_list_kc}")
        print(v_type, size__, pressure, t_type)

        # print(formula_dict[int(kc.kc_formula)])
        if len(output_list_kc) >= 1:
            a__ = formula_dict[int(output_list_kc[0]['kc_formula'])]
            print(f"kc forumual: {a__}")
        else:
            print("Didn't get KC value")
            a__ = 1

        return round(a__, 3)


def liqSizing(flowrate_form, specificGravity, inletPressure_form, outletPressure_form, vaporPressure,
              criticalPressure_form, outletPipeDia_form, inletPipeDia_form, valveSize_form, inletTemp_form, ratedCV,
              xt_fl, viscosity, seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, item_selected, fl_unit_form,
              iPresUnit_form, oPresUnit_form, vPresUnit_form, cPresUnit_form, iPipeUnit_form, oPipeUnit_form,
              vSizeUnit_form,
              iSch, iPipeSchUnit_form, oSch, oPipeSchUnit_form, iTempUnit_form, open_percent, fd, travel, rated_cv_tex):
    # check whether flowrate, pres and l are in correct units
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()
    thickness_pipe = float(i_pipearea_element.thickness)
    print(f"thickness: {thickness_pipe}")
    # 1. flowrate
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
                             'C': 0.075 * vSize_liq * vSize_liq, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': fd, 'viscosity': viscosity}

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
    # if valveSize_form != inletPipeDia_form:
    #     FLP = flP(result, service_conditions_1['valveDia'], service_conditions_1['iPipeDia'], N2_value, service_conditions_1['Fl'])
    #     FP = fP(result, service_conditions_1['valveDia'], service_conditions_1['iPipeDia'], service_conditions_1['oPipeDia'], N2_value)
    #     # print(f"FP: {FP}")
    #     FL = FLP / FP
    # else:
    #     FL = service_conditions_1['Fl']
    chokedP = delPMax(service_conditions_1['Fl'], ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'])
    print("liq sizing function, delpMax")

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
    print(f"pipe dia: {inletPipeDia_v}, sch: {iSch}")

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
                     'FD': fd,
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

    # convert pressure for tex, p in bar, l in inch
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

    # tEX = trimExitVelocity(inletPressure_v, outletPressure_v, specificGravity * 1000, t_caps, 'other')

    if int(v_det_element.flowCharacter_v) == 1:
        flow_character = 'equal'
    else:
        flow_character = 'linear'
    # new trim exit velocity
    # for port area, travel filter not implemented
    # tex new
    if float(travel) in [2, 3, 8]:
        travel = int(travel)
    else:
        travel = float(travel)

    if float(seatDia) in [1, 11, 2, 3, 4, 7, 8]:
        seatDia = int(seatDia)
    else:
        seatDia = float(seatDia)
    port_area_ = db.session.query(portArea).filter_by(v_size=vSize_v, seat_bore=seatDia, trim_type=trimtype,
                                                      flow_char=flow_character, travel=travel).first()
    print(f"port area table inputs: {vSize_v}, {seatDia}, {trimtype}, {flow_character}, {travel}")
    if port_area_:
        port_area = float(port_area_.area)
        tex_ = tex_new(result, int(rated_cv_tex), port_area, flowrate_v / 3600, inletPressure_form, inletPressure_form,
                       1, 8314,
                       inletTemp_form, 'Liquid')
    else:
        port_area = 1
        tex_ = 'None'

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
    area_in22 = float(o_pipearea_element.area)
    a_o = 0.00064516 * area_in22
    oVelocity = flowrate_v / (3600 * a_o)

    valve_element_current = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    rating_current = db.session.query(rating).filter_by(id=valve_element_current.rating).first()
    valvearea_element = db.session.query(valveArea).filter_by(rating=rating_current.size,
                                                              nominalPipeSize=vSize_v).first()
    if valvearea_element:
        v_area_in = float(valvearea_element.area)
        v_area = 0.00064516 * v_area_in
    else:
        v_area = 0.00064516 * 1
    pVelocity = flowrate_v / (3600 * v_area)

    data = {'cv': round(result, 3),
            'percent': 80,
            'spl': round(summation, 3),
            'iVelocity': iVelocity,
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(chokedP, 3),
            'texVelocity': round(433.9764, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{rw_noise}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{vPresUnit_form}+{cPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+{iPipeSchUnit_form}+{oPipeSchUnit_form}+{iTempUnit_form}+sg"

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
    Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_liq = round(FF(service_conditions_1['vPres'], service_conditions_1['cPres']), 2)
    N2_fp = N2[vSizeUnit_form]
    Fd_liq = service_conditions_1['FD']
    FLP_liq = flP(result, valveSize_form, inletPipeDia_form, N2_fp,
                  service_conditions_1['Fl'])
    RE_number = reynoldsNumber(N4_val, service_conditions_1['FD'], service_conditions_1['flowrate'],
                               service_conditions_1['viscosity'], service_conditions_1['Fl'], N2_val,
                               service_conditions_1['iPipeDia'], N1_val, service_conditions_1['iPres'],
                               service_conditions_1['oPres'],
                               service_conditions_1['sGravity'])
    fp_liq = fP(result, valveSize_form, inletPipeDia_form,
                outletPipeDia_form, N2_fp)
    if valveSize_form != inletPipeDia_form:
        FL_ = (FLP_liq / fp_liq)
        print(f"FL is flp/fp: {FL_}")
    else:
        FL_ = service_conditions_1['Fl']
        print(f'fl is just fl: {FL_}')
    chokedP = delPMax(FL_, ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'])
    print(FL_, ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'], valveSize_form, inletPipeDia_form,
          FLP_liq, fp_liq)
    if chokedP == (service_conditions_1['iPres'] - service_conditions_1['oPres']):
        ff = 0.96
    else:
        ff = round(ff_liq, 3)

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, vPres_unit, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    other_factors_string = f"{ff}+{Kc}+{Fd_liq}+{round(FLP_liq, 3)}+{RE_number}+{round(fp_liq, 2)}+{round(application_ratio, 3)}+{rated_cv_tex}"

    new_case = itemCases(flowrate=flowrate_form, iPressure=inletPressure_form,
                         oPressure=outletPressure_form,
                         iTemp=inletTemp_form, sGravity=specificGravity,
                         vPressure=vaporPressure, viscosity=viscosity, vaporMW=None,
                         vaporInlet=valveSize_form, vaporOutlet=other_factors_string,
                         CV=round(result, 3), openPercent=round(open_percent),
                         valveSPL=round(summation, 3), iVelocity=round(iVelocity, 3),
                         oVelocity=round(oVelocity, 3), pVelocity=round(pVelocity, 3),
                         chokedDrop=chokedP,
                         Xt=xt_fl, warning=1, trimExVelocity=tex_,
                         sigmaMR=pLevel, reqStage=units_string, fluidName=None, fluidState="Liquid",
                         criticalPressure=criticalPressure_form, iPipeSize=inletPipeDia_form,
                         oPipeSize=outletPipeDia_form,
                         iPipeSizeSch=iSch, oPipeSizeSch=oSch,
                         item=item_selected)

    db.session.add(new_case)
    db.session.commit()

    # print(data)
    # print(f"The calculated Cv is: {result}")
    return redirect(url_for('valveSizing'))


def gasSizing(inletPressure_form, outletPressure_form, inletPipeDia_form, outletPipeDia_form, valveSize_form,
              specificGravity, flowrate_form, inletTemp_form, ratedCV, z_factor, vaporPressure, seatDia, seatDiaUnit,
              sosPipe, densityPipe, criticalPressure_form, viscosity, item_selected, fl_unit_form, iPresUnit_form,
              oPresUnit_form, vPresUnit_form, iPipeUnit_form, oPipeUnit_form, vSizeUnit_form, iSch,
              iPipeSchUnit_form, oSch, oPipeSchUnit_form, iTempUnit_form, xt_fl, sg_vale, sg_choice,
              open_percent, fd, travel, rated_cv_tex):
    # Unit Conversion
    # 1. Flowrate

    # 2. Pressure

    # logic to choose which formula to use - using units of flowrate and sg
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
                                                              schedule=iSch).first()
    thickness_pipe = float(i_pipearea_element.thickness)
    thickness_in = meta_convert_P_T_FR_L('L', thickness_pipe, 'mm', 'inch', 1000)
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
        # 3. Pressure
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
    inletPressure_gnoise = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                 'pa',
                                                 1000)
    outletPressure_gnoise = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                  'pa',
                                                  1000)
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
        mw = 28.96 * float(sg_vale)
    elif sg_unit == 'mw':
        mw = float(sg_vale)

    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)
    flp = fLP(Cv1, valveSize_form, inletPipeDia_form)
    fp = fP_gas(Cv1, valveSize_form, inletPipeDia_form, outletPipeDia_form, N2_val)
    sigmeta = sigmaEta_gas(valveSize_form, inletPipeDia_form, outletPipeDia_form)
    flowrate_gv = flowrate_form / 3600
    inlet_density = inletDensity(inletPressure_gnoise, mw, 8314, temp_gnoise)
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
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2, 'Fp': 0.98,
                    'massFlowrate': flowrate_gv, 'massFlowrateUnit': 'kg/s', 'iPres': inletPressure_gnoise,
                    'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': inlet_density,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw,
                    'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}
    # print(sc_initial)
    sc_initial = sc_initial_2

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
    print(f'gas summation noise: {summation1}')
    # summation1 = 97

    # convert flowrate and dias for velocities
    flowrate_v = round(meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                             mw / 22.4))
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))

    size_v = round(meta_convert_P_T_FR_L('L', valveSize_form, 'inch',
                                         'inch', specificGravity * 1000))
    print(f"vsize_form: {valveSize_form}, vsize_unit: {vSizeUnit_form}")
    #
    # iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v, inletPipeDia_v,
    #                                               outletPipeDia_v,
    #                                               size_v)
    # i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(inletPipeDia_v),
    #                                                           schedule=iSch).first()
    # print(f"pipesize: {inletPipeDia_v}, schedule: {iSch}")
    # area_in2 = float(i_pipearea_element.area)
    # a_i = 0.00064516 * area_in2
    # iVelocity = flowrate_v / (3600 * a_i)
    #
    # o_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=str(outletPipeDia_v),
    #                                                           schedule=oSch).first()
    # area_in22 = float(o_pipearea_element.area)
    # a_o = 0.00064516 * area_in22
    # oVelocity = flowrate_v / (3600 * a_o)
    #
    # valve_element_current = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
    # rating_current = db.session.query(rating).filter_by(id=valve_element_current.rating).first()
    # valvearea_element = db.session.query(valveArea).filter_by(rating=rating_current.size,
    #                                                           nominalPipeSize=size_v).first()
    # print(f"rating: {rating_current.size}, valve Size: {size_v}")
    # v_area_in = float(valvearea_element.area)
    # v_area = 0.00064516 * v_area_in
    # pVelocity = flowrate_v / (3600 * v_area)

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

    gas_vels = getGasVelocities(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
                                temp_gnoise, sc_initial['molecularMass'], flowrate_gv, size_gnoise,
                                inletPipeDia_gnoise, outletPipeDia_gnoise)

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
    print(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
          temp_gnoise, sc_initial['molecularMass'], flowrate_gv, size_gnoise,
          inletPipeDia_gnoise, outletPipeDia_gnoise)
    print(f"gas velocities: {gas_vels}")

    # endof get gas

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa',
                                             1000)
    # print(f"Outlet Pressure V{outletPressure_v}")

    # get tex pressure in psi
    inletPressure_tex = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'psia',
                                              1000)
    outletPressure_tex = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'psia',
                                               1000)

    tEX = trimExitVelocityGas(inletPressure_tex, outletPressure_tex) / 3.281
    print(f"tex: {tEX}, {inletPressure_tex}, {outletPressure_tex}, {inletPressure_tex - outletPressure_tex}")
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

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{z_factor}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+{iPipeSchUnit_form}+{oPipeSchUnit_form}+{iTempUnit_form}+{sg_choice}"
    # change valve in item
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
    Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number#####
    Ff_gas = 0.96
    Fd_gas = fd
    xtp = xTP_gas(inputDict['xT'], inputDict['C'], inputDict['valveDia'], inputDict['inletDia'], inputDict['outletDia'],
                  N2_val)
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
    if data['choked'] == (inputDict['inletPressure'] - inputDict['outletPressure']):
        ff = 0.96
    else:
        ff = round(Ff_gas, 3)
    mac_sonic_list = [gas_vels[0], gas_vels[1], gas_vels[2],
                      gas_vels[3], gas_vels[4], gas_vels[5], gas_vels[9]]
    other_factors_string = f"{Ff_gas}+{Kc}+{Fd_gas}+{xtp}+{RE_number}+{fpgas}"

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, iPresUnit_form, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    other_factors_string = f"{Cv__[1]}+{Cv__[2]}+{Cv__[3]}+{Cv__[4]}+{Cv__[5]}+{Cv__[6]}+{Cv__[7]}+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}+{ratedCV}"

    # tex new
    if int(v_det_element.flowCharacter_v) == 1:
        flow_character = 'equal'
    else:
        flow_character = 'linear'
        # new trim exit velocity
        # for port area, travel filter not implemented

    if float(travel) in [2, 3, 8]:
        travel = int(travel)
    else:
        travel = float(travel)

    if float(seatDia) in [1, 11, 2, 3, 4, 7, 8]:
        seatDia = int(seatDia)
    else:
        seatDia = float(seatDia)

    port_area_ = db.session.query(portArea).filter_by(v_size=size_in_in, seat_bore=seatDia, trim_type=trimtype,
                                                      flow_char=flow_character, travel=travel).first()
    print(f'port area inputs: {size_in_in}, {seatDia}, {trimtype}, {flow_character}, {travel}')

    if port_area_:
        port_area = float(port_area_.area)
        tex_ = tex_new(Cv1, int(rated_cv_tex), port_area, flowrate_re / 3600, inletPressure_v, outletPressure_v, mw,
                       8314, temp_gnoise, 'Gas')
    else:
        port_area = 1
        tex_ = 'None'

    new_case = itemCases(flowrate=flowrate_form, iPressure=inletPressure_form,
                         oPressure=outletPressure_form,
                         iTemp=inletTemp_form, sGravity=specificGravity,
                         vPressure=vaporPressure, viscosity=viscosity,
                         vaporMW=float(sg_vale), vaporInlet=valveSize_form, vaporOutlet=other_factors_string,
                         CV=round(Cv1, 3), openPercent=round(open_percent),
                         valveSPL=data['spl'], iVelocity=data['iVelocity'], oVelocity=data['oVelocity'],
                         pVelocity=data['pVelocity'],
                         chokedDrop=round((data['choked'] * inletPressure_form), 3),
                         Xt=float(xt_fl), warning=1, trimExVelocity=tex_,
                         sigmaMR=pLevel, reqStage=units_string, fluidName=None, fluidState="Gas",
                         criticalPressure=round(criticalPressure_form, 3), iPipeSize=inletPipeDia_form,
                         oPipeSize=outletPipeDia_form,
                         iPipeSizeSch=iSch, oPipeSizeSch=oSch,
                         item=item_selected)
    db.session.add(new_case)
    db.session.commit()

    # print(inletPressure_form, outletPressure_form, inletPipeDia_form, outletPipeDia_form, valveSize_form,
    #       specificGravity, flowrate_form, inletTemp_form, ratedCV, z_factor, vaporPressure, seatDia, seatDiaUnit,
    #       sosPipe, densityPipe, criticalPressure_form, viscosity, item_selected, fl_unit_form, iPresUnit_form,
    #       oPresUnit_form, vPresUnit_form, iPipeUnit_form, oPipeUnit_form, vSizeUnit_form, iPipeSch_form,
    #       iPipeSchUnit_form, oPipeSch_form, oPipeSchUnit_form, iTempUnit_form, xt_fl, sg_vale)

    return redirect(url_for('valveSizing'))


# liq sizing outputs
def getOutputs(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
               inletTemp_form,
               iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form,
               cPresUnit_form,
               inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe,
               valveSize_form, vSizeUnit_form,
               seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected):
    # change into float/ num
    flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form, inletTemp_form, iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form, cPresUnit_form, inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe, valveSize_form, vSizeUnit_form, seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected = float(
        flowrate_form), fl_unit_form, float(inletPressure_form), iPresUnit_form, float(
        outletPressure_form), oPresUnit_form, float(inletTemp_form), iTempUnit_form, float(
        vaporPressure), vPresUnit_form, float(specificGravity), float(viscosity), float(xt_fl), float(
        criticalPressure_form), cPresUnit_form, float(inletPipeDia_form), iPipeUnit_form, iSch, float(
        outletPipeDia_form), oPipeUnit_form, oSch, float(densityPipe), float(sosPipe), float(
        valveSize_form), vSizeUnit_form, float(seatDia), seatDiaUnit, float(ratedCV), float(rw_noise), item_selected

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
                             'C': 0.075 * vSize_liq * vSize_liq, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
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
    try:
        summation = Lpe1m(sc_1['fi'], sc_1['FD'], sc_1['reqCV'], sc_1['iPressure'], sc_1['oPressure'],
                          sc_1['vPressure'],
                          sc_1['densityLiq'], sc_1['speedSoundLiq'], sc_1['massFlowRate'], sc_1['rw'],
                          sc_1['FL'],
                          sc_1['seatDia'], sc_1['valveDia'], sc_1['densityPipe'], sc_1['pipeWallThickness'],
                          sc_1['speedSoundPipe'],
                          sc_1['densityAir'], sc_1['internalPipeDia'], sc_1['speedSoundAir'],
                          sc_1['speedSoundPipe'])
    except:
        summation = 56
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
    if valvearea_element:
        v_area_in = float(valvearea_element.area)
        v_area = 0.00064516 * v_area_in
    else:
        v_area = 0.00064516 * 1
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
    other_factors_string = f"{ff}+{Kc}+{Fd_liq}+{FLP_liq}+{RE_number}+{fp_liq}+{round(application_ratio, 3)}+{ratedCV}"

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


# Gas sizng outputs
def getOutputsGas(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
                  inletTemp_form,
                  iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl,
                  criticalPressure_form,
                  cPresUnit_form,
                  inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe,
                  sosPipe,
                  valveSize_form, vSizeUnit_form,
                  seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, sg_choice, z_factor, sg_vale):
    flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form, inletTemp_form, iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form, cPresUnit_form, inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe, valveSize_form, vSizeUnit_form, seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, z_factor, sg_vale = float(
        flowrate_form), fl_unit_form, float(inletPressure_form), iPresUnit_form, float(
        outletPressure_form), oPresUnit_form, float(inletTemp_form), iTempUnit_form, float(
        vaporPressure), vPresUnit_form, float(specificGravity), float(viscosity), float(xt_fl), float(
        criticalPressure_form), cPresUnit_form, float(inletPipeDia_form), iPipeUnit_form, iSch, float(
        outletPipeDia_form), oPipeUnit_form, oSch, float(densityPipe), float(sosPipe), float(
        valveSize_form), vSizeUnit_form, float(seatDia), seatDiaUnit, float(ratedCV), float(
        rw_noise), item_selected, float(z_factor), float(sg_vale)

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
    other_factors_string = f"{Cv__[1]}+{Cv__[2]}+{Cv__[3]}+{Cv__[4]}+{Cv__[5]}+{Cv__[6]}+{Cv__[7]}+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}+{z_factor}+{ratedCV}"
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


@app.route('/valve-sizing', methods=["GET", "POST"])
def valveSizing():
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        itemCases_1 = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        fluid_data = fluidDetails.query.all()
        pipe_schedule = ['std', 10, 20, 30, 40, 80, 120, 160, 'xs', 'xxs']
        case_len = len(itemCases_1)
        valveD = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
        if valveD:
            f_state = valveD.packingType_v
            v_style = valveD.ratedCV
        else:
            f_state = 'Liquid'
            v_style = 'globe'

        if request.method == 'POST':
            # get data from html
            data = request.form.to_dict(flat=False)
            a = jsonify(data).json
            print(f"jsoinified form data: {a}")

            state = request.form.get('fState')

            valveType = request.form.get('vType')
            trimtype = request.form.get('tType')
            valve_det_element = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
            valve_det_element.ratedCV = valveType
            valve_det_element.body_v = trimtype
            db.session.commit()

            if v_style == 'globe':
                rw_noise = 0.25
            else:
                rw_noise = 0.5

            if state == 'Liquid':
                len_cases_input = len(a['iPressure'])
                for i in itemCases_1:
                    db.session.delete(i)
                    db.session.commit()

                for k in range(len_cases_input):
                    # try:
                    output = getOutputs(a['flowrate'][k], a['flowrate_unit'][0], a['iPressure'][k],
                                        a['iPresUnit'][0],
                                        a['oPressure'][k], a['oPresUnit'][0],
                                        a['iTemp'][k], a['iTempUnit'][0], a['vPressure'][k], a['vPresUnit'][0],
                                        a['sGravity'][k], a['viscosity'][k],
                                        a['xt'][k], a['cPressure'][0], a['cPresUnit'][0], a['iPipeSize'][0],
                                        a['iPipeUnit'][0], a['iSch'][0],
                                        a['oPipeSize'][0], a['oPipeUnit'][0], a['oSch'][0], a['densityP'][0],
                                        a['sosPipe'][0], a['vSize'][0],
                                        a['vSizeUnit'][0], a['seatDia'][0], a['seatDiaUnit'][0], a['ratedCV'][0],
                                        rw_noise, item_selected)
                    print(a['flowrate'][k], a['flowrate_unit'][0], a['iPressure'][k],
                          a['iPresUnit'][0],
                          a['oPressure'][k], a['oPresUnit'][0],
                          a['iTemp'][k], a['iTempUnit'][0], a['vPressure'][k], a['vPresUnit'][0],
                          a['sGravity'][k], a['viscosity'][k],
                          a['xt'][k], a['cPressure'][0], a['cPresUnit'][0], a['iPipeSize'][0],
                          a['iPipeUnit'][0], a['iSch'][0],
                          a['oPipeSize'][0], a['oPipeUnit'][0], a['oSch'][0], a['densityP'][0],
                          a['sosPipe'][0], a['vSize'][0],
                          a['vSizeUnit'][0], a['seatDia'][0], a['seatDiaUnit'][0], a['ratedCV'][0],
                          rw_noise, item_selected)

                    new_case = itemCases(flowrate=output[0], iPressure=output[1],
                                         oPressure=output[2],
                                         iTemp=output[3], sGravity=output[4],
                                         vPressure=output[5], viscosity=output[6], vaporMW=output[7],
                                         vaporInlet=output[8], vaporOutlet=output[9],
                                         CV=output[10], openPercent=output[11],
                                         valveSPL=output[12], iVelocity=output[13],
                                         oVelocity=output[14], pVelocity=output[15],
                                         chokedDrop=output[16],
                                         Xt=output[17], warning=output[18], trimExVelocity=output[19],
                                         sigmaMR=output[20], reqStage=output[21], fluidName=output[22],
                                         fluidState=output[23],
                                         criticalPressure=output[24], iPipeSize=output[25],
                                         oPipeSize=output[26],
                                         iPipeSizeSch=output[27], oPipeSizeSch=output[28],
                                         item=output[29])

                    db.session.add(new_case)
                    db.session.commit()
                    # except ValueError:
                    #     pass

                # print(data)
                # print(f"The calculated Cv is: {result}")
                return redirect(url_for('valveSizing'))

            elif state == 'Gas':
                # logic to choose which formula to use - using units of flowrate and sg

                len_cases_input = len(a['iPressure'])
                for i in itemCases_1:
                    db.session.delete(i)
                    db.session.commit()

                for k in range(len_cases_input):
                    try:
                        output = getOutputsGas(a['flowrate'][k], a['flowrate_unit'][0], a['iPressure'][k],
                                               a['iPresUnit'][0],
                                               a['oPressure'][k], a['oPresUnit'][0],
                                               a['iTemp'][k], a['iTempUnit'][0], '1', 'pa',
                                               a['sGravity'][k], '1',
                                               a['xt'][k], a['cPressure'][0], a['cPresUnit'][0], a['iPipeSize'][0],
                                               a['iPipeUnit'][0], a['iSch'][0],
                                               a['oPipeSize'][0], a['oPipeUnit'][0], a['oSch'][0], a['densityP'][0],
                                               a['sosPipe'][0], a['vSize'][0],
                                               a['vSizeUnit'][0], a['seatDia'][0], a['seatDiaUnit'][0], a['ratedCV'][0],
                                               rw_noise, item_selected, a['sg'][0], a['z'][k], a['sg_value'][k])

                        new_case = itemCases(flowrate=output[0], iPressure=output[1],
                                             oPressure=output[2],
                                             iTemp=output[3], sGravity=output[4],
                                             vPressure=output[5], viscosity=output[6], vaporMW=output[7],
                                             vaporInlet=output[8], vaporOutlet=output[9],
                                             CV=output[10], openPercent=output[11],
                                             valveSPL=output[12], iVelocity=output[13],
                                             oVelocity=output[14], pVelocity=output[15],
                                             chokedDrop=output[16],
                                             Xt=output[17], warning=output[18], trimExVelocity=output[19],
                                             sigmaMR=output[20], reqStage=output[21], fluidName=output[22],
                                             fluidState=output[23],
                                             criticalPressure=output[24], iPipeSize=output[25],
                                             oPipeSize=output[26],
                                             iPipeSizeSch=output[27], oPipeSizeSch=output[28],
                                             item=output[29])

                        db.session.add(new_case)
                        db.session.commit()
                    except ValueError:
                        pass

                return redirect(url_for('valveSizing'))

            else:
                return redirect(url_for('valveSizing'))

        # to render other values
        o_val_list = []

        for i in itemCases_1:
            if i.vaporOutlet is None:
                o_values = ['-', '-', '-', '-', '-', '-']
            else:
                o_values = i.vaporOutlet.split('+')
            o_val_list.append(o_values)

        # print(o_val_list)
        item_list = db.session.query(itemMaster).filter_by(projectID=item_selected.projectID).all()
        item_index = item_list.index(item_selected)

        # fl xt default value
        flxt_dict = {('globe', 'Liquid'): 0.9, ('globe', 'Gas'): 0.65, ('butterfly', 'Liquid'): 0.55,
                     ('butterfly', 'Gas'): 0.200}
        flxt_def = flxt_dict[(v_style.lower(), f_state)]
        return render_template("Valve Sizing 2.html", title='Valve Sizing', cases=itemCases_1, item_d=item_selected,
                               fluid=fluid_data, len_c=range(case_len), length_unit=getPref(item_selected),
                               fState=f_state, o_val=o_val_list, len_s=case_len, ps=pipe_schedule, page='valveSizing',
                               item_index=item_index, flxt_def=flxt_def)


# @app.route('/actuator-sizing', methods=["GET", "POST"])
# def actuatorSizing():
#     with app.app_context():
#         item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
#         cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
#         last_case = cases[len(cases) - 1]
#         v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
#         rating_id = v_details.rating
#         trimtype_id = v_details.trimType_v
#         flowdirection_id = v_details.flowDirection_v
#         packing_id = v_details.packing
#         seat_leakage_id = v_details.seatLeakageClass_v
#         valve_size = last_case.vaporInlet
#         aaaaa = last_case.reqStage
#         aaaaa_list = aaaaa.split('+')
#         # print(aaaaa_list, len(aaaaa_list))
#         seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
#             float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
#                 aaaaa_list[4]), aaaaa_list[5], \
#             aaaaa_list[6], \
#             aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
#             aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]
#
#         leakage_dict = {1: 'two', 2: 'three', 3: 'four', 4: 'five', 5: 'six'}
#         trimtype_dict = {1: 'modified', 2: 'microspline', 3: 'contour', 4: 'cage', 5: 'MHC1'}
#
#         # inputs for actuator sizing:
#         iPressure = last_case.iPressure
#         oPressure = last_case.oPressure
#         iPressure = meta_convert_P_T_FR_L('P', iPressure, iPresUnit, 'psia', 1000)
#         oPressure = meta_convert_P_T_FR_L('P', oPressure, oPresUnit, 'psia', 1000)
#         seatDia_act = round(meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'inch', 1000), 2)
#         valveSize_act = round(meta_convert_P_T_FR_L('L', valve_size, vSizeUnit, 'inch', 1000))
#         rating_act = rating.query.get(rating_id).size
#         trimType_act = trimtype_dict[int(trimtype_id)]
#         fl_direction = flowDirection.query.get(flowdirection_id).name
#         packing_act = valveTypeMaterial.query.get(packing_id).name
#         sLeak_act = leakage_dict[int(seat_leakage_id)]
#         shutoffDelp = float(v_details.shutOffDelP)
#         data = [iPressure, oPressure, seatDia_act, valveSize_act, rating_act, trimType_act, fl_direction, packing_act,
#                 sLeak_act]
#
#         # get actuator sized data from v_detials.rating_v, valve data from v_details.valve_size
#         # if data is available, render it in acSizing, else, blank
#         if v_details.rating_v is None:
#             act_data_list = []
#         else:
#             act_data_string = v_details.rating_v
#             act_data_list = act_data_string.split('#')
#
#         if v_details.valve_size is None:
#             act_valve_data_list = []
#         else:
#             act_valve_string = v_details.valve_size
#             act_valve_data_list = act_valve_string.split('#')
#
#         if len(act_valve_data_list) > 0:
#             v_data_final = act_valve_data_list[6:]
#         else:
#             v_data_final = []
#
#         if request.method == 'POST':
#             if request.form.get('valve'):
#                 plugDia = float(request.form.get('plugDia'))
#                 stemDia = float(request.form.get('stemDia'))
#                 ua = float(request.form.get('ua'))
#                 seatDia = float(request.form.get('seatDia'))
#                 balance = request.form.get('balance')
#                 stroke = request.form.get('stroke')
#                 valve_forces = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                            sLeak_act, trimType_act, balance, fl_direction, 'shutoff+', shutoffDelp)
#                 vf_shutoff = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                          sLeak_act, trimType_act, balance, fl_direction, 'shutoff', shutoffDelp)
#                 vf_open = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                       sLeak_act, trimType_act, balance, fl_direction, 'open', shutoffDelp)
#                 vf_close = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                        sLeak_act, trimType_act, balance, fl_direction, 'close', shutoffDelp)
#                 v_shutoff, v_shutoff_plus, v_open, v_close = round(vf_shutoff[0]), round(valve_forces[0]), round(
#                     vf_open[0]), round(vf_close[0])
#
#                 # store data in v_details
#                 v_details.valve_size = f"{balance}#{stroke}#{round(seatDia, 2)}#{plugDia}#{stemDia}#{ua}#{v_shutoff}#{v_shutoff_plus}#{v_open}#{v_close}"
#                 db.session.commit()
#                 v_data = [v_shutoff, v_shutoff_plus, v_open, v_close]
#
#                 return render_template("Actuator Sizing.html", title='Actuator Sizing', item_d=selected_item, data=data,
#                                        v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list)
#             if request.form.get('actuator'):
#                 setPressure = int(request.form.get('setPressure'))
#                 shutoff_plus = float(request.form.get('shutoff+'))
#                 stem_dia = float(request.form.get('stemDia'))
#                 valveTravel = float(request.form.get('stroke'))
#                 actuator_data = db.session.query(actuatorData).filter_by(SFMax=stem_dia).all()
#                 print(f"actuator data lenght: {len(actuator_data)}")
#                 return_actuator_data = []
#                 for i in actuator_data:
#                     if float(valveTravel) <= float(i.travel):
#                         springRate = int(((int(i.sMax) - int(i.sMin)) / float(i.travel)) * int(i.NATMin))
#                         springForceMin = int(i.sMin) * int(i.NATMin)
#                         springForceMax = int(i.sMax) * int(i.NATMin)
#                         NATMax = (int(i.NATMin) * setPressure) - springForceMin
#                         NATMin = (int(i.NATMin) * setPressure) - springForceMax
#                         if i.failAction == 'AFO':
#                             if NATMin > shutoff_plus:
#                                 i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate, springForceMin,
#                                           springForceMax,
#                                           NATMax, NATMin, i.SFMax]
#                                 return_actuator_data.append(i_list)
#                         elif i.failAction == 'AFC':
#                             if springForceMin > shutoff_plus:
#                                 i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate, springForceMin,
#                                           springForceMax,
#                                           NATMax, NATMin, i.SFMax]
#                                 return_actuator_data.append(i_list)
#                 return render_template('select_actuator.html', data=return_actuator_data, item_d=selected_item,
#                                        setP=setPressure)
#
#         return render_template("Actuator Sizing.html", title='Actuator Sizing', item_d=selected_item, data=data,
#                                v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list)


@app.route('/actuator-sizing', methods=["GET", "POST"])
def actuatorSizing():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
        shutoffDelp = float(v_details.shutOffDelP)
        if request.method == 'POST':
            act_type = request.form.get('actType')
            failAct = request.form.get('failAction')
            mount = request.form.get('mount')
            orientation = request.form.get('orientation')
            airsupply_unit = request.form.get('airUnit')
            min_air = request.form.get('min')
            max_air = request.form.get('max')
            shutoffDel = request.form.get('shutoffDelP')
            act_data_string = f"{act_type}#{failAct}#{mount}#{orientation}#{airsupply_unit}#{min_air}#{max_air}#{shutoffDel}"
            v_details.serial_no = act_data_string
            db.session.commit()
            return redirect(url_for('actuator'))
        item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = item_list.index(item_details)
        return render_template("actuator1.html", title='Actuator Sizing', item_d=item_details, shutoff=shutoffDelp,
                               page='actuatorSizing', item_index=item_index)


@app.route('/actuator', methods=["GET", "POST"])
def actuator():
    trimtype_dict = {1: 'modified', 2: 'microspline', 3: 'contour', 4: 'cage', 5: 'MHC1'}
    leakage_dict = {1: 'two', 2: 'three', 3: 'four', 4: 'five', 5: 'six'}
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
        item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = item_list.index(item_details)
        last_case = cases[len(cases) - 1]
        v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()

        # get min air supply into act data
        act_data_prev = v_details.serial_no
        act_data_prev_list = act_data_prev.split('#')
        min_air = act_data_prev_list[5]

        trimType_act = trimtype_dict[int(v_details.trimType_v)]
        fl_direction = flowDirection.query.get(v_details.flowDirection_v).name
        valve_size = last_case.vaporInlet
        aaaaa = last_case.reqStage
        aaaaa_list = aaaaa.split('+')
        # print(aaaaa_list, len(aaaaa_list))
        seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
            float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
                aaaaa_list[4]), aaaaa_list[5], \
            aaaaa_list[6], \
            aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
            aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]

        iPressure = last_case.iPressure
        oPressure = last_case.oPressure
        iPressure = round(meta_convert_P_T_FR_L('P', iPressure, iPresUnit, 'psia', 1000))
        oPressure = round(meta_convert_P_T_FR_L('P', oPressure, oPresUnit, 'psia', 1000))
        seatDia_act = round(meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'inch', 1000), 2)
        act_data_new = v_details.serial_no
        act_data_new_list = act_data_new.split('#')
        shutoffDelP = float(act_data_new_list[7]) * 14.5
        sLeak_act = leakage_dict[int(v_details.seatLeakageClass_v)]
        rating_id = v_details.rating
        valveSize_act = round(meta_convert_P_T_FR_L('L', valve_size, vSizeUnit, 'inch', 1000))
        rating_act = rating.query.get(rating_id).size
        packing_id = v_details.packing
        packing_act = valveTypeMaterial.query.get(packing_id).name

        # get actuator sized data from v_detials.rating_v, valve data from v_details.valve_size
        # if data is available, render it in acSizing, else, blank
        if v_details.rating_v is None:
            act_data_list = []
        else:
            act_data_string = v_details.rating_v
            act_data_list = act_data_string.split('#')

        if v_details.valve_size is None:
            act_valve_data_list = []
        else:
            act_valve_string = v_details.valve_size
            act_valve_data_list = act_valve_string.split('#')

        if len(act_valve_data_list) > 0:
            v_data_final = act_valve_data_list[6:]
        else:
            v_data_final = []
        data__ = [trimType_act, fl_direction, valve_size, seatDia_act, iPressure, oPressure, shutoffDelP,
                  iPressure - oPressure]
        data = [iPressure, oPressure, seatDia_act, valveSize_act, rating_act, trimType_act, fl_direction, packing_act,
                sLeak_act]
        print(f"v_data_final: {v_data_final}")
        print(f"act_valve_dat_final:{act_valve_data_list}")
        print(f"act_data_list:{act_data_list}")
        # get fail action
        action_string = v_details.serial_no
        fail_action_string = action_string.split('#')[1]
        print(f"fail action: {fail_action_string}")
        if request.method == 'POST':
            if request.form.get('valve'):
                plugDia = float(request.form.get('plugDia'))
                stemDia = float(request.form.get('stemDia'))
                ua = float(request.form.get('ua'))
                seatDia = float(request.form.get('seatDia'))
                balance = request.form.get('balance')
                stroke = request.form.get('stroke')
                valve_forces = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
                                           sLeak_act, trimType_act, balance, fl_direction, 'shutoff+', shutoffDelP)
                vf_shutoff = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
                                         sLeak_act, trimType_act, balance, fl_direction, 'shutoff', shutoffDelP)
                vf_open = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
                                      sLeak_act, trimType_act, balance, fl_direction, 'open', shutoffDelP)
                vf_close = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
                                       sLeak_act, trimType_act, balance, fl_direction, 'close', shutoffDelP)
                v_shutoff, v_shutoff_plus, v_open, v_close = round(vf_shutoff[0]), round(valve_forces[0]), round(
                    vf_open[0]), round(vf_close[0])

                packing_fric = valve_forces[2]
                seatload_fact = valve_forces[3]
                # store data in v_details
                v_details.valve_size = f"{balance}#{stroke}#{round(seatDia, 3)}#{plugDia}#{stemDia}#{ua}#{v_shutoff}#{v_shutoff_plus}#{v_open}#{v_close}#{packing_fric}#{seatload_fact}"
                db.session.commit()
                v_data = [v_shutoff, v_shutoff_plus, v_open, v_close]

                # get data again
                data__ = [trimType_act, fl_direction, valve_size, seatDia_act, iPressure, oPressure, shutoffDelP,
                          iPressure - oPressure]
                if v_details.rating_v is None:
                    act_data_list = []
                else:
                    act_data_string = v_details.rating_v
                    act_data_list = act_data_string.split('#')

                if v_details.valve_size is None:
                    act_valve_data_list = []
                else:
                    act_valve_string = v_details.valve_size
                    act_valve_data_list = act_valve_string.split('#')

                if len(act_valve_data_list) > 0:
                    v_data_final = act_valve_data_list[6:]
                else:
                    v_data_final = []
                return render_template("actuator2.html", title='Actuator Sizing', item_d=item_details, data=data__,
                                       v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list,
                                       air=min_air, af=fail_action_string, page='actuator', item_index=item_index)
            if request.form.get('actuator'):
                setPressure = float(request.form.get('setPressure'))
                shutoff_plus = float(request.form.get('vClosed'))
                stem_dia = float(request.form.get('stemDia'))
                valveTravel = float(request.form.get('stroke'))
                act_dat_prev = v_details.serial_no
                fail_action_prev = act_dat_prev.split('#')[1]
                act_type = act_dat_prev.split('#')[0]
                actuator_data = db.session.query(actuatorDataVol).filter_by(SFMax=stem_dia,
                                                                            failAction=fail_action_prev,
                                                                            SFMin=act_type).all()
                print(f"actuator data lenght: {len(actuator_data)}")
                return_actuator_data = []
                for i in actuator_data:
                    if float(valveTravel) <= float(i.travel):
                        springRate = int(((int(i.sMax) - int(i.sMin)) / float(i.travel)) * int(i.NATMin))
                        springForceMin = int(i.sMin) * int(i.NATMin)
                        springForceMax = int(i.sMax) * int(i.NATMin)
                        NATMax = (int(i.NATMin) * setPressure) - springForceMin
                        NATMin = (int(i.NATMin) * setPressure) - springForceMax
                        if i.failAction == 'AFO':
                            if NATMin > shutoff_plus:
                                i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
                                          springForceMin,
                                          springForceMax,
                                          NATMax, NATMin, i.SFMax]
                                return_actuator_data.append(i_list)
                        elif i.failAction == 'AFC':
                            if springForceMin > shutoff_plus:
                                i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
                                          springForceMin,
                                          springForceMax,
                                          NATMax, NATMin, i.SFMax]
                                return_actuator_data.append(i_list)
                return render_template('select_actuator.html', data=return_actuator_data, item_d=item_details,
                                       setP=setPressure, page='selectActuator', item_index=item_index)

        return render_template("actuator2.html", title='Actuator Sizing', item_d=item_details, data=data__,
                               v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list, air=min_air,
                               af=fail_action_string, page='actuator', item_index=item_index)


@app.route('/stroke_speed', methods=["GET", "POST"])
def stroke_speed():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        # cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
        item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = item_list.index(item_details)
        # last_case = cases[len(cases) - 1]
        v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
        stroke_speed_data = v_details.cage_clamp
        vo, vm, vs, pi_fill, pf_fill, pi_exhaust, pf_exhaust = stroke_speed_data.split('+')[0], \
                                                               stroke_speed_data.split('+')[1], \
                                                               stroke_speed_data.split('+')[2], \
                                                               stroke_speed_data.split('+')[3], \
                                                               stroke_speed_data.split('+')[4], \
                                                               stroke_speed_data.split('+')[5], \
                                                               stroke_speed_data.split('+')[6]
        data = [vo, vm, vs, pi_fill, pf_fill, pi_exhaust, pf_exhaust]
        return render_template('stroke_speed_actuator.html', data=data, item_d=item_details, item_index=item_index)


# @app.route('/actuator-sizing2', methods=["GET", "POST"])
# def actuatorSizing2():
#     with app.app_context():
#         item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
#         cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
#         last_case = cases[len(cases) - 1]
#         v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
#         rating_id = v_details.rating
#         trimtype_id = v_details.trimType_v
#         flowdirection_id = v_details.flowDirection_v
#         packing_id = v_details.packing
#         seat_leakage_id = v_details.seatLeakageClass_v
#         valve_size = last_case.vaporInlet
#         aaaaa = last_case.reqStage
#         aaaaa_list = aaaaa.split('+')
#         # print(aaaaa_list, len(aaaaa_list))
#         seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
#             float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
#                 aaaaa_list[4]), aaaaa_list[5], \
#             aaaaa_list[6], \
#             aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
#             aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]
#
#         leakage_dict = {1: 'two', 2: 'three', 3: 'four', 4: 'five', 5: 'six'}
#         trimtype_dict = {1: 'modified', 2: 'microspline', 3: 'contour', 4: 'cage', 5: 'MHC1'}
#
#         # inputs for actuator sizing:
#         iPressure = last_case.iPressure
#         oPressure = last_case.oPressure
#         iPressure = meta_convert_P_T_FR_L('P', iPressure, iPresUnit, 'psia', 1000)
#         oPressure = meta_convert_P_T_FR_L('P', oPressure, oPresUnit, 'psia', 1000)
#         seatDia_act = round(meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'inch', 1000), 2)
#         valveSize_act = round(meta_convert_P_T_FR_L('L', valve_size, vSizeUnit, 'inch', 1000))
#         rating_act = rating.query.get(rating_id).size
#         trimType_act = trimtype_dict[int(trimtype_id)]
#         fl_direction = flowDirection.query.get(flowdirection_id).name
#         packing_act = valveTypeMaterial.query.get(packing_id).name
#         sLeak_act = leakage_dict[int(seat_leakage_id)]
#         shutoffDelp = float(v_details.shutOffDelP)
#         data = [iPressure, oPressure, seatDia_act, valveSize_act, rating_act, trimType_act, fl_direction, packing_act,
#                 sLeak_act]
#
#         # get actuator sized data from v_detials.rating_v, valve data from v_details.valve_size
#         # if data is available, render it in acSizing, else, blank
#         if v_details.rating_v is None:
#             act_data_list = []
#         else:
#             act_data_string = v_details.rating_v
#             act_data_list = act_data_string.split('#')
#
#         if v_details.valve_size is None:
#             act_valve_data_list = []
#         else:
#             act_valve_string = v_details.valve_size
#             act_valve_data_list = act_valve_string.split('#')
#
#         if len(act_valve_data_list) > 0:
#             v_data_final = act_valve_data_list[6:]
#         else:
#             v_data_final = []
#
#         if request.method == 'POST':
#             if request.form.get('valve'):
#                 plugDia = float(request.form.get('plugDia'))
#                 stemDia = float(request.form.get('stemDia'))
#                 ua = float(request.form.get('ua'))
#                 seatDia = float(request.form.get('seatDia'))
#                 balance = request.form.get('balance')
#                 stroke = request.form.get('stroke')
#                 valve_forces = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                            sLeak_act, trimType_act, balance, fl_direction, 'shutoff+', shutoffDelp)
#                 vf_shutoff = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                          sLeak_act, trimType_act, balance, fl_direction, 'shutoff', shutoffDelp)
#                 vf_open = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                       sLeak_act, trimType_act, balance, fl_direction, 'open', shutoffDelp)
#                 vf_close = valveForces(iPressure, oPressure, seatDia, plugDia, stemDia, ua, rating_act, 'ptfe1',
#                                        sLeak_act, trimType_act, balance, fl_direction, 'close', shutoffDelp)
#                 v_shutoff, v_shutoff_plus, v_open, v_close = round(vf_shutoff[0]), round(valve_forces[0]), round(
#                     vf_open[0]), round(vf_close[0])
#
#                 # store data in v_details
#                 v_details.valve_size = f"{balance}#{stroke}#{round(seatDia, 2)}#{plugDia}#{stemDia}#{ua}#{v_shutoff}#{v_shutoff_plus}#{v_open}#{v_close}"
#                 db.session.commit()
#                 v_data = [v_shutoff, v_shutoff_plus, v_open, v_close]
#
#                 return render_template("Actuator Sizing.html", title='Actuator Sizing', item_d=selected_item, data=data,
#                                        v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list)
#             if request.form.get('actuator'):
#                 setPressure = int(request.form.get('setPressure'))
#                 shutoff_plus = float(request.form.get('shutoff+'))
#                 stem_dia = float(request.form.get('stemDia'))
#                 valveTravel = float(request.form.get('stroke'))
#                 actuator_data = db.session.query(actuatorData).filter_by(SFMax=stem_dia).all()
#                 print(f"actuator data lenght: {len(actuator_data)}")
#                 return_actuator_data = []
#                 for i in actuator_data:
#                     if float(valveTravel) <= float(i.travel):
#                         springRate = int(((int(i.sMax) - int(i.sMin)) / float(i.travel)) * int(i.NATMin))
#                         springForceMin = int(i.sMin) * int(i.NATMin)
#                         springForceMax = int(i.sMax) * int(i.NATMin)
#                         NATMax = (int(i.NATMin) * setPressure) - springForceMin
#                         NATMin = (int(i.NATMin) * setPressure) - springForceMax
#                         if i.failAction == 'AFO':
#                             if NATMin > shutoff_plus:
#                                 i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
#                                           springForceMin,
#                                           springForceMax,
#                                           NATMax, NATMin, i.SFMax]
#                                 return_actuator_data.append(i_list)
#                         elif i.failAction == 'AFC':
#                             if springForceMin > shutoff_plus:
#                                 i_list = [i.id, i.acSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
#                                           springForceMin,
#                                           springForceMax,
#                                           NATMax, NATMin, i.SFMax]
#                                 return_actuator_data.append(i_list)
#                 return render_template('select_actuator.html', data=return_actuator_data, item_d=selected_item,
#                                        setP=setPressure)
#
#         return render_template("Actuator Sizing.html", title='Actuator Sizing', item_d=selected_item, data=data,
#                                v_data=v_data_final, act_list=act_data_list, v_list=act_valve_data_list)


@app.route('/select-actuator', methods=["GET", "POST"])
def selectActuator():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        v_details = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
        v_data = v_details.valve_size
        v_data_split = v_data.split('#')
        cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
        last_case = cases[len(cases) - 1]
        rating_id = v_details.rating
        trimtype_id = v_details.trimType_v
        flowdirection_id = v_details.flowDirection_v
        flowcharacter_id = v_details.flowCharacter_v
        packing_id = v_details.packing
        seat_leakage_id = v_details.seatLeakageClass_v
        valve_size = last_case.vaporInlet
        aaaaa = last_case.reqStage
        aaaaa_list = aaaaa.split('+')
        # print(aaaaa_list, len(aaaaa_list))
        seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
            float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
                aaaaa_list[4]), aaaaa_list[5], \
            aaaaa_list[6], \
            aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
            aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]

        leakage_dict = {1: 'two', 2: 'three', 3: 'four', 4: 'five', 5: 'six'}
        trimtype_dict = {1: 'modified', 2: 'microspline', 3: 'contour', 4: 'cage', 5: 'MHC1'}

        # inputs for actuator sizing:
        iPressure = last_case.iPressure
        oPressure = last_case.oPressure
        iPressure = meta_convert_P_T_FR_L('P', iPressure, iPresUnit, 'psia', 1000)
        oPressure = meta_convert_P_T_FR_L('P', oPressure, oPresUnit, 'psia', 1000)
        seatDia_act = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'inch', 1000)
        valveSize_act = meta_convert_P_T_FR_L('L', valve_size, vSizeUnit, 'inch', 1000)
        rating_act = rating.query.get(rating_id).size
        trimType_act = trimtype_dict[int(trimtype_id)]
        fl_direction = flowDirection.query.get(flowdirection_id).name
        packing_act = valveTypeMaterial.query.get(packing_id).name
        sLeak_act = leakage_dict[int(seat_leakage_id)]
        shutoffDelp = float(v_details.shutOffDelP) * 14.5
        print(f"flow character id: {flowcharacter_id}")
        if int(flowcharacter_id) == 1:
            flowCha = 'equal'
        else:
            flowCha = 'linear'
        if request.method == 'POST':
            act_id = request.form.get('valve')
            setP = float(request.form.get('setP'))
            act_data = actuatorDataVol.query.get(int(act_id))
            act_dat_prev = v_details.serial_no
            fail_action_prev = act_dat_prev.split('#')[1]
            act_type = act_dat_prev.split('#')[0]
            acSize, smin, smax, travel, fail_action = int(act_data.NATMin), int(act_data.sMin), int(
                act_data.sMax), float(act_data.travel), act_data.rate
            act_fun_output = compareForces(iPressure, oPressure, float(v_data_split[2]), float(v_data_split[3]),
                                           float(v_data_split[4]), float(v_data_split[5]), rating_act, 'ptfe1',
                                           sLeak_act, trimType_act, v_data_split[0], fl_direction,
                                           'shutoff+', shutoffDelp, acSize, travel, smin, smax, setP, failAction,
                                           float(v_data_split[1]), flowCha)

            # other inputs for page
            stemArea = round((math.pi * float(v_data_split[4]) * float(v_data_split[4]) / 4), 3)
            actuatorSize_ = act_data.acSize
            springRate = act_fun_output[1]
            springWindUp = round((act_fun_output[3] / springRate), 2)
            maxSpringLoad = act_fun_output[2]
            frictionBand = round((act_fun_output[6] / acSize), 3)
            reqHW = 'none'
            # v details serial no - act data
            act_initial = v_details.serial_no
            act_initial_list = act_initial.split('#')
            fa = act_initial_list[1]
            mount_ = act_initial_list[2]
            hw_thrust = db.session.query(hwThrust).filter_by(failAction=fa, mount=mount_, ac_size=actuatorSize_).first()
            sfMax, sfMin, natMax, natMin, comment1, comment2, comment3, packing_friction, seatload_force, kn, seatload_factor = \
                act_fun_output[2], act_fun_output[3], act_fun_output[4], act_fun_output[5], act_fun_output[12], \
                act_fun_output[13], act_fun_output[14], act_fun_output[6], act_fun_output[7], act_fun_output[15], \
                act_fun_output[16]
            if hw_thrust:
                maxHW = hw_thrust.max_thrust
            else:
                maxHW = 'none'

            v_details.rating_v = f"{acSize}#{travel}#{smin}#{smax}#{fail_action}#{setP}#{sfMax}#{sfMin}#{natMax}#{natMin}#{comment1}#{comment2}#{comment3}#{packing_friction}#{round(seatload_force, 2)}#{kn}" \
                                 f"#{stemArea}#{actuatorSize_}#{springRate}#{springWindUp}#{maxSpringLoad}#{frictionBand}#{reqHW}#{maxHW}#{seatload_factor}"
            print(
                f"{acSize}#{travel}#{smin}#{smax}#{fail_action}#{setP}#{act_fun_output[2]}#{act_fun_output[3]}#{act_fun_output[4]}#{act_fun_output[5]}#{act_fun_output[-1]}#{act_fun_output[-2]}#{act_fun_output[-3]}")
            # db.session.commit()
            print(
                f'Stroke Speed Data: VO: {act_data.VO}, VM: {act_data.VM}, VS: {int(act_data.VO) - int(act_data.VM)}, Pi Fill: {round(smin + (frictionBand / int(act_data.NATMin)))}, Pf fill: {round(smax + (frictionBand / int(act_data.NATMin)))}, Pi Exhaust: {round(smax - (frictionBand / int(act_data.NATMin)))}, Pf Exhaust: {round(smin - (frictionBand / int(act_data.NATMin)))}')

            stroke_string = f'{act_data.VO}+{act_data.VM}+{int(act_data.VO) - int(act_data.VM)}+{round(smin + (frictionBand / int(act_data.NATMin)))}+{round(smax + (frictionBand / int(act_data.NATMin)))}+{round(smax - (frictionBand / int(act_data.NATMin)))}+{round(smin - (frictionBand / int(act_data.NATMin)))}'
            v_details.cage_clamp = stroke_string
            db.session.commit()
            return redirect(url_for('actuator'))
            # get valve details from i.valve_size of v_details
            # use that data for acSizing, store the data in i.rating_v


@app.route('/accessories', methods=["GET", "POST"])
def accessories():
    item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
    item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
    item_index = item_list.index(item_details)
    return render_template("Accessories_Order_Processing_2.html", title='Accessories', item_d=selected_item,
                           page='accessories',
                           item_index=item_index)


@app.route('/item-notes', methods=["GET", "POST"])
def itemNotes():
    item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
    item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
    item_index = item_list.index(item_details)
    if request.method == 'POST':
        data = request.form.get('abc')
        return f"{data}"
    return render_template("Item Notes.html", title='Item Notes', item_d=selected_item, page='itemNotes',
                           item_index=item_index)


@app.route('/project-notes', methods=["GET", "POST"])
def projectNotes():
    item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
    item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
    item_index = item_list.index(item_details)
    # with app.app_context():
    #     Cv_value = db.session.query(globeTable).filter_by(trimTypeID=2, flow=0, charac=0,
    #                                                       size=6, coeffID=0)
    #     Fl_value = db.session.query(globeTable).filter_by(trimTypeID=2, flow=0, charac=0,
    #                                                       size=6, coeffID=1)

    return render_template("Project Notes.html", title='Project Notes', item_d=selected_item, page='projectNotes',
                           item_index=item_index)


@app.route('/delete-cases/<case_id>', methods=["GET", "POST"])
def deleteCase(case_id):
    with app.app_context():
        entry_to_delete = itemCases.query.get(case_id)
        db.session.delete(entry_to_delete)
        db.session.commit()
    return redirect(url_for("valveSizing"))


@app.route('/add-item/<page>/<alt>', methods=['GET', 'POST'])
def addItem(page, alt):
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        project_element = db.session.query(projectMaster).filter_by(id=item_selected.projectID).first()
        model_element = db.session.query(modelMaster).filter_by(name='Model_1').first()
        serial_element = db.session.query(valveSeries).filter_by(id=1).first()
        size_element = db.session.query(valveSize).filter_by(id=1).first()
        rating_element = db.session.query(rating).filter_by(id=1).first()
        material_element = db.session.query(materialMaster).filter_by(id=1).first()
        type_element = db.session.query(valveStyle).filter_by(id=1).first()

        item4 = {"alt": alt, "tagNo": 101, "serial": serial_element, "size": size_element,
                 "model": model_element, "type": type_element, "rating": rating_element,
                 "material": material_element, "unitPrice": 1, "Quantity": 11111, "Project": project_element}

        i = item4

        new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'],
                              model=i['model'],
                              type=i['type'], rating=i['rating'], material=i['material'],
                              unit_price=i['unitPrice'],
                              qty=i['Quantity'], project=i['Project'])

        db.session.add(new_item)
        db.session.commit()

        new_valve_details = valveDetails(tag=1, quantity=1,
                                         application='None',
                                         serial_no=1,
                                         rating=1,
                                         body_material=1,
                                         shutOffDelP=1,
                                         maxPressure=1,
                                         maxTemp=1,
                                         minTemp=1,
                                         valve_series=1,
                                         valve_size=1,
                                         rating_v=1,
                                         ratedCV='globe',
                                         endConnection_v=1,
                                         endFinish_v=1,
                                         bonnetType_v=1,
                                         bonnetExtDimension=1,
                                         packingType_v='Liquid',
                                         trimType_v=1,
                                         flowCharacter_v=1,
                                         flowDirection_v=1,
                                         seatLeakageClass_v=1, body_v=1,
                                         bonnet_v=1,
                                         nde1=1, nde2=1, plug=1, stem=1, seat=1,
                                         cage_clamp=None,
                                         balanceScale=1, packing=1, stud_nut=1, gasket=1,
                                         item=new_item)

        db.session.add(new_valve_details)
        db.session.commit()

        return redirect(url_for(page))


@app.route('/nextItem/<control>/<page>', methods=['GET', 'POST'])
def nextItem(control, page):
    global selected_item
    with app.app_context():
        item_1 = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        item_all = db.session.query(itemMaster).filter_by(projectID=item_1.projectID).all()
        len_items = len(item_all)
        item_1_index = item_all.index(item_1)
        if control == 'next':
            if selected_item.id < len_items:
                item_1 = db.session.query(itemMaster).filter_by(id=item_all[item_1_index + 1].id).first()
            else:
                item_1 = db.session.query(itemMaster).filter_by(id=len_items).first()
        elif control == 'prev':
            if selected_item.id > item_all[0].id:
                item_1 = db.session.query(itemMaster).filter_by(id=item_all[item_1_index - 1].id).first()
            else:
                item_1 = db.session.query(itemMaster).filter_by(id=item_all[0].id).first()
        elif control == 'first':
            item_1 = db.session.query(itemMaster).filter_by(id=item_all[0].id).first()
        elif control == 'last':
            item_1 = db.session.query(itemMaster).filter_by(id=len_items).first()

        selected_item = item_1

        return redirect(url_for(page))


@app.route('/export-case/<page>', methods=['GET', 'POST'])
def exportItem(page):
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        itemCases_1 = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")
        size__ = db.session.query(valveSize).filter_by(id=item_selected.sizeID).first().size
        rating__ = db.session.query(rating).filter_by(id=item_selected.ratingID).first().size
        project__ = db.session.query(projectMaster).filter_by(id=item_selected.projectID).first()
        customer__ = db.session.query(customerMaster).filter_by(id=project__.customerID).first().name

        fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                     'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                     'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                     'Critical Pressure',
                     'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                     'Customer']

        # other_fields_row = [item_selected.tag_no, item_selected.id, itemCases_1[0].fState,
        #                     itemCases_1[0].criticalPressure,
        #                     itemCases_1.iPipeSize, itemCases_1.oPipeSize, size__, rating__, project__.quote,
        #                     project__.work_order,
        #                     customer__]

        # data rows of csv file
        rows___ = []
        for i in itemCases_1[:6]:
            case_list = [i.flowrate, i.iPressure, i.oPressure, i.iTemp, i.sGravity, i.viscosity, i.vPressure, i.Xt,
                         i.CV, i.openPercent, i.valveSPL,
                         i.iVelocity, i.oVelocity, i.trimExVelocity, item_selected.tag_no, item_selected.id,
                         itemCases_1[0].fluidState, itemCases_1[0].criticalPressure,
                         itemCases_1[0].iPipeSize, itemCases_1[0].oPipeSize, size__, rating__, project__.quote,
                         project__.work_order,
                         customer__]
            rows___.append(case_list)
        #
        # pd = pandas.DataFrame(rows___, columns=fields___)
        # pd.to_csv(f"C:/Users/FCC/Desktop/case_data_{item_selected.id}-{len(itemCases_1)}-{date}.csv")

        return redirect(url_for(page))


#

@app.route('/generate-csv/<page>', methods=['GET', 'POST'])
def generate_csv(page):
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        v_details = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()

        # serial, quantity and project ID, material
        serial_ = db.session.query(valveSeries).filter_by(id=item_selected.serialID).first()
        material_updated = db.session.query(materialMaster).filter_by(id=item_selected.materialID).first()
        serial__ = serial_.name
        project_ = item_selected.projectID
        material_ = material_updated.name
        itemCases_1 = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")
        size__ = db.session.query(valveSize).filter_by(id=item_selected.sizeID).first().size
        rating__ = db.session.query(rating).filter_by(id=item_selected.ratingID).first().size
        project__ = db.session.query(projectMaster).filter_by(id=item_selected.projectID).first()
        customer__ = db.session.query(customerMaster).filter_by(id=project__.customerID).first().name

        fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                     'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                     'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                     'Critical Pressure',
                     'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                     'Customer']

        # other_fields_row = [item_selected.tag_no, item_selected.id, itemCases_1[0].fState,
        #                     itemCases_1[0].criticalPressure,
        #                     itemCases_1.iPipeSize, itemCases_1.oPipeSize, size__, rating__, project__.quote,
        #                     project__.work_order,
        #                     customer__]

        # data rows of csv file
        rows___ = []

        # get units
        cases = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        last_case = cases[len(cases) - 1]
        # cpressure, valveSize
        cPressure = last_case.criticalPressure
        vSize = last_case.vaporInlet

        # shutoffDelp, rating, endconnection, endfinish, bonnettype, nde1, nde2, gasketmaterial, trimtype, flowdirection, seat material, discMaterial, seatleakage class
        shutoffDelp = float(v_details.shutOffDelP) * 14.5
        rating_ = rating.query.get(v_details.rating).size
        end_connection = endConnection.query.get(v_details.endConnection_v).name
        end_finish = endFinish.query.get(v_details.endFinish_v).name
        bonnet_type = bonnetType.query.get(v_details.bonnetType_v).name
        nde1 = bodyBonnet.query.get(v_details.nde1).name
        nde2 = bodyBonnet.query.get(v_details.nde2).name
        gasket_mat = valveTypeMaterial.query.get(v_details.gasket).name
        trim_type = trimType.query.get(v_details.trimType_v).name
        flow_dir = flowDirection.query.get(v_details.flowDirection_v).name
        seat_mat = valveTypeMaterial.query.get(v_details.seat).name
        disc_mat = valveTypeMaterial.query.get(v_details.plug).name
        seat_leak = seatLeakageClass.query.get(v_details.seatLeakageClass_v).name

        # units
        aaaaa = last_case.reqStage
        aaaaa_list = aaaaa.split('+')
        # print(aaaaa_list, len(aaaaa_list))
        seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
            float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
                aaaaa_list[4]), aaaaa_list[5], \
            aaaaa_list[6], \
            aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
            aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]
        unit_list = [fl_unit, iPresUnit, oPresUnit, iTempUnit, '', 'centipose', vPresUnit, '', '', '%', 'dB', 'm/s',
                     'm/s', 'm/s', iPipeUnit, oPipeUnit]
        other_val_list = [serial__, 1, project_, cPressure, cPresUnit, shutoffDelp, vSize, vSizeUnit, rating_,
                          material_, bonnet_type, nde1, nde2, gasket_mat, trim_type, flow_dir, seat_mat, disc_mat,
                          seat_leak, end_connection, end_finish]
        for i in itemCases_1[:6]:
            case_list = [i.flowrate, i.iPressure, i.oPressure, i.iTemp, i.sGravity, i.viscosity, i.vPressure, i.Xt,
                         i.CV, i.openPercent, i.valveSPL,
                         i.iVelocity, i.oVelocity, i.trimExVelocity, item_selected.tag_no, item_selected.id,
                         itemCases_1[0].fluidState, itemCases_1[0].criticalPressure,
                         itemCases_1[0].iPipeSize, itemCases_1[0].oPipeSize, size__, rating__, project__.quote,
                         project__.work_order,
                         customer__]
            rows___.append(case_list)

        # print(rows___)
        createSpecSheet(rows___, unit_list, other_val_list)

        return redirect(url_for(page))


@app.route('/preferences/<page>', methods=['GET', 'POST'])
def preferences(page):
    length_unit_list = [{'id': 'inch', 'name': 'inch'}, {'id': 'm', 'name': 'm'}, {'id': 'mm', 'name': 'mm'},
                        {'id': 'cm', 'name': 'cm'}]

    flowrate_unit_list = [{'id': 'm3/hr', 'name': 'm3/hr'}, {'id': 'scfh', 'name': 'scfh'},
                          {'id': 'gpm', 'name': 'gpm'},
                          {'id': 'lb/hr', 'name': 'lb/hr'}, {'id': 'kg/hr', 'name': 'kg/hr'}]

    pressure_unit_list = [{'id': 'bar', 'name': 'bar (a)'}, {'id': 'bar', 'name': 'bar (g)'},
                          {'id': 'kpa', 'name': 'kPa (a)'}, {'id': 'kpa', 'name': 'kPa (g)'},
                          {'id': 'mpa', 'name': 'MPa (a)'}, {'id': 'mpa', 'name': 'MPa (g)'},
                          {'id': 'pa', 'name': 'Pa (a)'}, {'id': 'pa', 'name': 'Pa (g)'},
                          {'id': 'inh20', 'name': 'in H2O (a)'}, {'id': 'inh20', 'name': 'in H2O (g)'},
                          {'id': 'inhg', 'name': 'in Hg (a)'}, {'id': 'inhg', 'name': 'in Hg (g)'},
                          {'id': 'kg/cm2', 'name': 'kg/cm2 (a)'}, {'id': 'kg/cm2', 'name': 'kg/cm2 (g)'},
                          {'id': 'mmh20', 'name': 'm H2O (a)'}, {'id': 'mmh20', 'name': 'm H2O (g)'},
                          {'id': 'mbar', 'name': 'mbar (a)'}, {'id': 'mbar', 'name': 'mbar (g)'},
                          {'id': 'mmhg', 'name': 'mm Hg (a)'}, {'id': 'mmhg', 'name': 'mm Hg (g)'},
                          {'id': 'psia', 'name': 'psi (g)'}, {'id': 'psia', 'name': 'psi (a)'}]

    temp_unit_list = [{'id': 'C', 'name': '°C'}, {'id': 'F', 'name': '°F'}, {'id': 'K', 'name': 'K'},
                      {'id': 'R', 'name': 'R'}]

    units_pref = [length_unit_list, flowrate_unit_list, pressure_unit_list, temp_unit_list]
    with app.app_context():
        item_1 = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        item_list = db.session.query(itemMaster).filter_by(projectID=item_1.projectID).all()
        item_index = item_list.index(item_1)
        if request.method == "POST":
            pres = request.form.get('pres')
            fr = request.form.get('fr')
            length = request.form.get('length')
            temp = request.form.get('temp')
            for i in units_pref[0]:
                if i['id'] == length:
                    len_index = str(units_pref[0].index(i) + 1)
                    break

            for i in units_pref[1]:
                if i['id'] == fr:
                    fr_index = str(units_pref[1].index(i) + 1)
                    break

            for i in units_pref[2]:
                if i['id'] == pres:
                    pres_index = units_pref[2].index(i) + 1
                    if pres_index < 10:
                        pres_index = "0" + str(pres_index)
                    else:
                        pres_index = str(pres_index)
                    break

            for i in units_pref[3]:
                if i['id'] == temp:
                    temp_index = str(units_pref[3].index(i) + 1)
                    break

            qty_str = len_index + fr_index + temp_index + pres_index
            qty_int = int(qty_str)
            item_1.qty = qty_int
            # print(item_1.qty)
            db.session.commit()
            return redirect(url_for('valveSizing'))

        return render_template('preferences.html', title='Preferences', length_unit=units_pref, item_d=item_1,
                               page='preferences', item_index=item_index)


def interpolate(data, x_db, y_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    y_list = [y_db.one, y_db.two, y_db.three, y_db.four, y_db.five, y_db.six, y_db.seven, y_db.eight, y_db.nine,
              y_db.ten]
    opening = interpolate_percent(data, x_db, vtype)
    diff = opening - (opening // 10) * 10
    # print(f"FL list: {y_list}")
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list == data:
                return y_list[a]
            elif x_list[a] > data:
                break
            else:
                a += 1

        # value_interpolate = y_list[a - 1] - (
        #         ((x_list[a - 1] - data) / (x_list[a - 1] - x_list[a])) * (y_list[a - 1] - y_list[a]))
        if diff >= 5:
            value_interpolate = y_list[a]
        else:
            value_interpolate = y_list[a - 1]

        return round(value_interpolate, 4)
    else:
        return 0.5


def interpolate_fd(data, x_db, y_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    y_list = [y_db.one, y_db.two, y_db.three, y_db.four, y_db.five, y_db.six, y_db.seven, y_db.eight, y_db.nine,
              y_db.ten]
    # print(f"FL list: {y_list}")

    opening = interpolate_percent(data, x_db, vtype)
    diff = opening - (opening // 10) * 10
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list == data:
                return y_list[a]
            elif x_list[a] > data:
                break
            else:
                a += 1

        if diff >= 5:
            value_interpolate = y_list[a]
        else:
            value_interpolate = y_list[a - 1]
        # print(f"fd: {value_interpolate}, a: {a}")
        print(f"diff:{diff}, opening: {opening}, interpolates: {y_list[a]}, {y_list[a - 1]}")

        return round(value_interpolate, 3)
    else:
        return 0.5


def interpolate_percent(data, x_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    if vtype.lower() == 'globe':
        y_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    else:
        y_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list == data:
                break
            elif x_list[a] > data:
                break
            else:
                a += 1
        # print(f"percentage: {y_list[a - 1]}, a:{a}")

        value_interpolate = y_list[a - 1] - (
                ((x_list[a - 1] - data) / (x_list[a - 1] - x_list[a])) * (y_list[a - 1] - y_list[a]))

        print(y_list[a - 1], x_list[a - 1], x_list[a], y_list[a], data)

        return round(value_interpolate, 3)
    else:
        return 60


@app.route('/select-valve', methods=['GET', 'POST'])
def selectValve():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        item_list = db.session.query(itemMaster).filter_by(projectID=item_details.projectID).all()
        item_index = item_list.index(item_details)
        cases = db.session.query(itemCases).filter_by(itemID=item_details.id).all()
        cv_values = []
        for i in cases:
            cv_value = i.CV
            cv_values.append(cv_value)
        min_cv = min(cv_values)
        max_cv = max(cv_values)
        # last_case = cases[len(cases) - 1]
        if request.method == "POST":
            if request.form.get('getv'):
                vType = request.form.get('valveType')
                trimType = request.form.get('trimType')
                flowChara = request.form.get('flowChar')
                flowDirec = request.form.get('flowDir')
                rating_v = request.form.get('rating')
                # update trim type and flow direction and flow character
                valve_det = db.session.query(valveDetails).filter_by(itemID=item_details.id).first()
                if flowChara == 'equal':
                    fc = 1
                else:
                    fc = 2
                valve_det.body_v = trimType
                valve_det.flowCharacter_v = fc
                db.session.commit()
                return_globe_data = []
                if (vType == 'globe') and (rating_v in ['150', '300', '600']):
                    rating_v = '(150_300_600)'
                else:
                    rating_v = rating_v

                #  Create globe dict list
                filter_criter = f"{vType}#{trimType}#{flowChara}#{flowDirec}#{rating_v}"
                print(f"filter_criteria: {filter_criter}")
                cv_lists = db.session.query(globeTable).filter_by(trimTypeID=filter_criter, coeffID='Cv').all()
                for i in cv_lists:
                    seat_bore = i.charac.split('#')[7]
                    travel = i.charac.split('#')[6]
                    i_list = [i.one, i.two, i.three, i.four, i.five, i.six, i.seven,
                              i.eight,
                              i.nine, i.ten, 0.89, travel, seat_bore, i.id, i.size]
                    return_globe_data.append(i_list)
                print(return_globe_data)
                # cv_dummy = last_case.CV
                # print(cv_dummy)
                index_to_remove = []
                for i in return_globe_data:
                    if i[0] < min_cv < i[9]:
                        a = 0
                        while True:
                            if i[a] == min_cv:
                                break
                            elif i[a] > min_cv:
                                break
                            else:
                                a += 1
                        i.append(a)
                        # print(a)
                        # print('CV in Range')
                        # print(i)
                    if i[0] < max_cv < i[9]:
                        b = 0
                        while True:
                            if i[b] == max_cv:
                                break
                            elif i[b] > max_cv:
                                break
                            else:
                                b += 1
                        i.append(b)
                        # print(a)
                        # print('CV in Range')
                        # print(i)
                    else:
                        i.append(10)
                        i.append(10)
                        index_to_remove.append(return_globe_data.index(i))
                        # print(f"Index to remove: {index_to_remove}")
                        # print('CV not in range')

                print(f"Index to remove final: {index_to_remove}")
                for ele in sorted(index_to_remove, reverse=True):
                    del return_globe_data[ele]

                print(f'The final return globe is: {return_globe_data}')
                return render_template('select_valve_size.html', item_d=item_details, data=return_globe_data,
                                       page='selectValve', item_index=item_index)
            elif request.form.get('select'):
                for last_case in cases:
                    valve_d_id = request.form.get('valve')
                    aaaaa = last_case.reqStage
                    aaaaa_list = aaaaa.split('+')
                    # print(aaaaa_list, len(aaaaa_list))
                    seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = \
                        float(aaaaa_list[0]), aaaaa_list[1], float(aaaaa_list[2]), float(aaaaa_list[3]), float(
                            aaaaa_list[4]), aaaaa_list[5], \
                        aaaaa_list[6], \
                        aaaaa_list[7], aaaaa_list[8], aaaaa_list[9], aaaaa_list[10], aaaaa_list[11], aaaaa_list[12], \
                        aaaaa_list[13], aaaaa_list[14], aaaaa_list[15], aaaaa_list[16]
                    select_dict = db.session.query(globeTable).filter_by(id=int(valve_d_id)).first()
                    select_dict_fl = db.session.query(globeTable).filter_by(id=int(valve_d_id) + 1).first()
                    select_dict_xt = db.session.query(globeTable).filter_by(id=int(valve_d_id) + 2).first()
                    select_dict_fd = db.session.query(globeTable).filter_by(id=int(valve_d_id) + 3).first()

                    v_size = round(meta_convert_P_T_FR_L('L', select_dict.size, 'inch', 'inch', 1000))
                    # get cv for o_percent
                    # get valveType from valveDetails
                    v_det_element = db.session.query(valveDetails).filter_by(itemID=last_case.itemID).first()
                    valve_type_ = v_det_element.ratedCV

                    fl = interpolate(last_case.CV, select_dict, select_dict_fl, valve_type_)
                    xt = interpolate(last_case.CV, select_dict, select_dict_xt, valve_type_)
                    fd = interpolate_fd(last_case.CV, select_dict, select_dict_fd, valve_type_)
                    rated_cv_tex = select_dict.ten
                    if last_case.fluidState == 'Liquid':
                        final_cv = getCVresult(fl_unit, last_case.sGravity, iPresUnit, last_case.iPressure,
                                               last_case.flowrate,
                                               last_case.oPressure,
                                               oPresUnit, vPresUnit, last_case.vPressure, cPresUnit,
                                               last_case.criticalPressure,
                                               last_case.iPipeSize,
                                               iPipeUnit, last_case.oPipeSize, oPipeUnit, v_size, 'inch',
                                               last_case.iTemp,
                                               select_dict.ten, fl, fd,
                                               last_case.viscosity, iTempUnit)
                    else:
                        final_cv = getCVGas(fl_unit, last_case.sGravity, sg_choice, last_case.iPressure, iPresUnit,
                                            last_case.oPressure, oPresUnit, v_size, 'inch',
                                            last_case.flowrate, last_case.iTemp, iTempUnit, select_dict.ten,
                                            last_case.iPipeSize, iPipeUnit, last_case.oPipeSize, oPipeUnit, xt,
                                            rw_noise,
                                            last_case.vaporMW)
                    # print(f"last_cv: {final_cv}")
                    fl = interpolate(final_cv, select_dict, select_dict_fl, valve_type_)
                    xt = interpolate(final_cv, select_dict, select_dict_xt, valve_type_)
                    fd = interpolate_fd(final_cv, select_dict, select_dict_fd, valve_type_)

                    if last_case.fluidState == 'Liquid':
                        final_cv1 = getCVresult(fl_unit, last_case.sGravity, iPresUnit, last_case.iPressure,
                                                last_case.flowrate,
                                                last_case.oPressure,
                                                oPresUnit, vPresUnit, last_case.vPressure, cPresUnit,
                                                last_case.criticalPressure,
                                                last_case.iPipeSize,
                                                iPipeUnit, last_case.oPipeSize, oPipeUnit, v_size, 'inch',
                                                last_case.iTemp,
                                                final_cv, fl, fd,
                                                last_case.viscosity, iTempUnit)
                    else:
                        final_cv1 = getCVGas(fl_unit, last_case.sGravity, sg_choice, last_case.iPressure, iPresUnit,
                                             last_case.oPressure, oPresUnit, v_size, 'inch',
                                             last_case.flowrate, last_case.iTemp, iTempUnit, final_cv,
                                             last_case.iPipeSize, iPipeUnit, last_case.oPipeSize, oPipeUnit, xt,
                                             rw_noise,
                                             last_case.vaporMW)

                    o_percent = interpolate_percent(final_cv1, select_dict, valve_type_)
                    fl = interpolate(final_cv1, select_dict, select_dict_fl, valve_type_)
                    xt = interpolate(final_cv1, select_dict, select_dict_xt, valve_type_)
                    fd = interpolate_fd(final_cv1, select_dict, select_dict_fd, valve_type_)
                    print('final fl, xt, select dict')
                    print(fl, xt, select_dict_xt.id)

                    valve_data_ = db.session.query(globeTable).filter_by(id=valve_d_id).first()
                    seat_bore = float(valve_data_.charac.split('#')[7])
                    travel = valve_data_.charac.split('#')[6]

                    if last_case.fluidState == 'Liquid':
                        liqSizing(last_case.flowrate, last_case.sGravity, last_case.iPressure, last_case.oPressure,
                                  last_case.vPressure, last_case.criticalPressure, last_case.oPipeSize,
                                  last_case.iPipeSize,
                                  v_size, last_case.iTemp, final_cv1, fl,
                                  last_case.viscosity, seat_bore, 'inch', sosPipe, densityPipe, rw_noise,
                                  item_details,
                                  fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, 'inch',
                                  last_case.iPipeSizeSch, iPipeSchUnit, last_case.oPipeSizeSch, oPipeSchUnit, iTempUnit,
                                  o_percent, fd, travel, rated_cv_tex)
                        db.session.delete(last_case)
                        db.session.commit()
                    else:
                        gasSizing(last_case.iPressure, last_case.oPressure, last_case.iPipeSize, last_case.oPipeSize,
                                  v_size,
                                  last_case.sGravity, last_case.flowrate, last_case.iTemp, final_cv1, rw_noise,
                                  last_case.vPressure,
                                  seat_bore, 'inch',
                                  sosPipe, densityPipe, last_case.criticalPressure, last_case.viscosity, item_details,
                                  fl_unit,
                                  iPresUnit,
                                  oPresUnit, vPresUnit, iPipeUnit, oPipeUnit, 'inch',
                                  last_case.iPipeSizeSch,
                                  iPipeSchUnit, last_case.oPipeSizeSch, oPipeSchUnit, iTempUnit, xt, last_case.vaporMW,
                                  sg_choice, o_percent, fd, travel, rated_cv_tex)

                        db.session.delete(last_case)
                        db.session.commit()

                redirect(url_for('valveSizing', page='valveSizing'))

                return redirect(url_for('valveSizing', page='valveSizing'))

    return render_template('select_valve_size.html', item_d=item_details, data=[], page='selectValve',
                           item_index=item_index)


@app.route('/view-data', methods=['GET', 'POST'])
def viewData():
    data2 = table_data_render
    return render_template('view_data.html', data=data2, page='viewData')


@app.route('/render-data/<topic>', methods=['GET'])
def renderData(topic):
    table_ = table_data_render[int(topic) - 1]['db']
    table_data = table_.query.all()
    return render_template("render_data.html", data=table_data, topic=topic, page='renderData')


@app.route('/download-data/<topic>', methods=['GET'])
def downloadData(topic):
    table_ = table_data_render[int(topic) - 1]['db']
    table_name = table_data_render[int(topic) - 1]['name']
    table_data = table_.query.all()
    proj_row = ['Id', 'Data']
    final_row = []
    a = datetime.datetime.now()
    date = a.strftime("%a, %d %b %Y %H-%M-%S")
    for i in table_data:
        a_ = [i.id, i.name]
        final_row.append(a_)
    #
    # pd = pandas.DataFrame(final_row, columns=proj_row)
    # pd.to_csv(f"C:/Users/FCC/Desktop/{table_name} {topic}-{date}.csv")
    return redirect(url_for('renderData', topic=int(topic)))


@app.route('/upload-data/<topic>', methods=['GET', 'POST'])
def uploadData(topic):
    # reading csv file
    table_ = table_data_render[int(topic) - 1]['db']
    table_name = table_data_render[int(topic) - 1]['name']
    table_data = table_.query.all()
    if request.method == "POST":
        filename_c = request.form.get('directory_csv')
        # print(filename_c)
        with open(filename_c, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            # extracting field names through first row
            fields_c = next(csvreader)

            # extracting each data row one by one
            row_c = []
            for row in csvreader:
                row_c.append(row)
            # print(row_c)

        for i in table_data:
            db.session.delete(i)
            db.session.commit()
        for i in row_c:
            new_el_data = table_(name=i[2])
            db.session.add(new_el_data)
            db.session.commit()
        return redirect(url_for('renderData', topic=int(topic)))
    return render_template('importproject.html', topic=topic, route='uploadData', page='uploadData')


@app.route('/del-proj/<item_id>/<page>', methods=['GET', 'POST'])
def deleteProject(item_id, page):
    with app.app_context():
        item_element = db.session.query(itemMaster).filter_by(id=item_id).first()
        proj_id = item_element.projectID
        proj_to_del = projectMaster.query.get(proj_id)
        items_proj = db.session.query(itemMaster).filter_by(projectID=proj_id).all()
        len_items = len(items_proj)
        len_cases = 0
        for items in items_proj:
            cases = db.session.query(itemCases).filter_by(itemID=items.id).all()
            len_cas = len(cases)
            len_cases = len_cases + len_cas
        if request.method == 'POST':
            if request.form.get('confirm'):
                for items in items_proj:
                    valve_details = db.session.query(valveDetails).filter_by(itemID=items.id).first()
                    cases = db.session.query(itemCases).filter_by(itemID=items.id).all()
                    for case in cases:
                        # Del Item Cases
                        entry_to_delete_case = itemCases.query.get(case.id)
                        db.session.delete(entry_to_delete_case)
                        db.session.commit()
                    # Del Items
                    entry_to_delete_item = itemMaster.query.get(items.id)
                    if valve_details:
                        db.session.delete(valve_details)
                    db.session.delete(entry_to_delete_item)
                    db.session.commit()
                # Del Project
                db.session.delete(proj_to_del)
                db.session.commit()
            if request.form.get('cancel'):
                pass
            return redirect(url_for(page))
        data = f"You are about to delete 1 project, {len_items} Item(s) and {len_cases} Case(s)"
        return render_template('del_confirmation.html', route='deleteProject', data=data, page=page, item_id=item_id)


@app.route('/del-item/<item_id>/<page>', methods=['GET', 'POST'])
def deleteItem(item_id, page):
    with app.app_context():
        item_to_del = itemMaster.query.get(int(item_id))
        cases = db.session.query(itemCases).filter_by(itemID=item_to_del.id).all()
        len_cases = len(cases)
        valve_details = db.session.query(valveDetails).filter_by(itemID=item_to_del.id).first()
        if request.method == 'POST':
            if request.form.get('confirm'):
                for case in cases:
                    # Del Item Cases
                    entry_to_delete_case = itemCases.query.get(case.id)
                    db.session.delete(entry_to_delete_case)
                    db.session.commit()
                # Del Item
                if valve_details:
                    db.session.delete(valve_details)
                db.session.delete(item_to_del)
                db.session.commit()
            if request.form.get('cancel'):
                pass
            return redirect(url_for(page))
        data = f"You are about to delete 1 Item and {len_cases} Case(s)"
        return render_template('del_confirmation.html', route='deleteItem', data=data, page=page, item_id=item_id)


@app.route('/copy-proj/<proj_id>/<page>', methods=['GET'])
def copyProject(proj_id, page):
    return redirect(url_for(page))


@app.route('/copy-item/<item_id>/<page>', methods=['GET'])
def copyItem(item_id, page):
    return redirect(url_for(page))


@app.route('/import-proj/<page>', methods=['GET', 'POST'])
def importProject(page):
    if request.method == "POST":
        filename_c = request.form.get('directory_csv')
        # print(filename_c)
        with open(filename_c, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            # extracting field names through first row
            fields_c = next(csvreader)

            # extracting each data row one by one
            row_c = []
            for row in csvreader:
                row_c.append(row)
            print(row_c)

        part_list = []
        for i in row_c:
            if i[1] == 'Id':
                index_id = row_c.index(i)
                part_list.append(index_id)

        proj_list = row_c[0]
        item_list = row_c[part_list[0] + 1:part_list[1]]
        cases_list = row_c[part_list[1] + 1:]

        # Add Projects
        industry__ = db.session.query(industryMaster).filter_by(name=proj_list[6]).first()
        region__ = db.session.query(regionMaster).filter_by(name=proj_list[7]).first()
        quote__ = proj_list[2]
        status__ = db.session.query(statusMaster).filter_by(name=proj_list[8]).first()
        customer__ = db.session.query(customerMaster).filter_by(name=proj_list[9]).first()
        engineer__ = db.session.query(engineerMaster).filter_by(name=proj_list[10]).first()
        new_project = projectMaster(industry=industry__, region=region__, quote=quote__, status=status__,
                                    customer=customer__,
                                    received_date=datetime.datetime.now(),
                                    engineer=engineer__,
                                    work_order=proj_list[4],
                                    due_date=datetime.datetime.now())
        db.session.add(new_project)
        db.session.commit()
        # Add Items
        item3 = {"alt": 'A', "tagNo": 102, "serial": valve_series_element_2, "size": valve_size_element_3,
                 "model": model_element_2, "type": type_element_1, "rating": rating_element_3,
                 "material": material_element_2, "unitPrice": 3, "Quantity": 4, "Project": project_element_2}

        #
        for item__ in item_list:
            serial__ = db.session.query(valveSeries).filter_by(name=item__[7]).first()
            size__ = db.session.query(valveSize).filter_by(size=item__[8]).first()
            model__ = db.session.query(modelMaster).filter_by(name=item__[9]).first()
            valve_type__ = db.session.query(valveStyle).filter_by(name=item__[10]).first()
            rating__ = db.session.query(rating).filter_by(size=item__[11]).first()
            material__ = db.session.query(materialMaster).filter_by(name=item__[12]).first()
            new_item = itemMaster(alt=item__[2], tag_no=item__[3], serial=serial__, size=size__, model=model__,
                                  type=valve_type__, rating=rating__, material=material__, unit_price=item__[4],
                                  qty=11111, project=new_project)
            db.session.add(new_item)
            db.session.commit()
            # Add Cases
            for i in cases_list:
                if i[31] == item__[1]:
                    print(i[2])
                    new_case = itemCases(flowrate=i[2], iPressure=i[3],
                                         oPressure=i[4],
                                         iTemp=i[5], sGravity=i[6],
                                         vPressure=i[7], viscosity=i[8], vaporMW=i[9],
                                         vaporInlet=i[10], vaporOutlet=i[11],
                                         CV=i[12], openPercent=i[13],
                                         valveSPL=i[14], iVelocity=i[15],
                                         oVelocity=i[16], pVelocity=i[17],
                                         chokedDrop=i[18],
                                         Xt=i[19], warning=i[20], trimExVelocity=i[21],
                                         sigmaMR=i[22], reqStage=i[23], fluidName=i[24], fluidState=i[25],
                                         criticalPressure=i[26], iPipeSize=i[27],
                                         oPipeSize=i[29],
                                         iPipeSizeSch=i[28], oPipeSizeSch=i[30],
                                         item=new_item)
                    db.session.add(new_case)
                    db.session.commit()

        return redirect(url_for(page))
    return render_template('importproject2.html', page='importProject')


@app.route('/export-proj/<proj_id>/<page>', methods=['GET'])
def exportProject(proj_id, page):
    with app.app_context():
        proj_to_del = projectMaster.query.get(proj_id)
        proj_row = ["Id", "Quote", "Received Date", "Work Order No.", "Due Date", "Industry", "Region", "Status",
                    "Customer", "Engineer",
                    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        item_row = ["Id", "Alternate", "Tag No.", "Unit Price", "Quantity", "Project ID", "Serial", "Size", "Model",
                    "Type", "Rating", "Material", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                    "", ""]
        case_row = ['Id', 'Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                    'Vapor Pressure',
                    'Viscosity', 'Vapor MW', 'Vapor Inlet', 'Vapor Outlet', 'Calculated Cv', 'Open %',
                    'Valve SPL',
                    'Inlet Velocity',
                    'Outlet Velocity', 'Pipe Velocity', 'Choked Drop', 'Xt', 'Warning', 'Trim Exit Velocity',
                    'Sigma MR',
                    'Unit Data(reqStage)', 'Fluid Name', 'Fluid State',
                    'Critical Pressure', 'Inlet Pipe Size', 'Inlet Pipe Schedule', 'Outlet Pipe Size',
                    'Outlet Pipe Schedule', 'Item ID']
        proj_det = convert_project_data([proj_to_del])
        proj_list = [v for k, v in proj_det[0].items()]
        final_proj_list = proj_list + ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                                       ""]

        # items
        items_proj = db.session.query(itemMaster).filter_by(projectID=proj_id).all()
        item_det = convert_item_data(items_proj)
        item_rows = []
        for item in item_det:
            i_list = [v for k, v in item.items()]
            item_rows.append(i_list)

        # cases
        case_rows = []
        for items in items_proj:
            cases = db.session.query(itemCases).filter_by(itemID=items.id).all()
            for i in cases:
                case_list = [i.id, i.flowrate, i.iPressure, i.oPressure, i.iTemp, i.sGravity, i.vPressure, i.viscosity,
                             i.vaporMW, i.vaporInlet, i.vaporOutlet, i.CV, i.openPercent, i.valveSPL, i.iVelocity,
                             i.oVelocity, i.pVelocity, i.chokedDrop, i.Xt, i.warning, i.trimExVelocity, i.sigmaMR,
                             i.reqStage, i.fluidName,
                             i.fluidState, i.criticalPressure, i.iPipeSize, i.iPipeSizeSch, i.oPipeSize, i.oPipeSizeSch,
                             i.itemID]
                case_rows.append(case_list)

        final_row = [final_proj_list] + [item_row] + item_rows + [case_row] + case_rows
        print(final_row)
        print(proj_row)
        # pd = pandas.DataFrame(final_row, columns=proj_row)
        a = datetime.datetime.now()
        date = a.strftime("%a, %d %b %Y %H-%M-%S")
        # pd.to_csv(f"C:/Users/FCC/Desktop/Project Data {proj_id}-{date}.csv")

        return redirect(url_for(page))


@app.route('/download')
def downloadFile():
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = "./11_Series_Cv.csv"
    return send_file(path, as_attachment=True)


# getKCValue(8, 'ported', 130, 'globe', 0.9)
##############
# with app.app_context():
#     projects = projectMaster.query.all()
#     for i in projects:
#         if i.id not in [1, 2, 3]:
#             db.session.delete(i)
#             db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)

######################
