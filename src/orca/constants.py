from dataclasses import dataclass


@dataclass(frozen=True)
class OrcaConstants:
    #########
    # Modes #
    #########
    MODE_SLEEP = 1
    MODE_FORCE = 2
    MODE_POSITION = 3
    MODE_HAPTIC = 4
    MODE_KINEMATIC = 5
    MODE_AUTO_ZERO = 55
    MODE_OF_OPERATION = 317
    #####################
    # Control Registers #
    #####################
    CTRL_REG_0 = 0  # System info.
    CTRL_REG_0_FULL_RESET = 1
    CTRL_REG_0_CLEAR_ERRORS = 2
    CTRL_REG_0_ZERO_POSITION = 4
    CTRL_REG_0_INVERT_POSITION = 8
    CTRL_REG_1 = 1  # System flags & calibration.
    CTRL_REG_1_SET_POSITION_CONTROLLER_GAIN = 1024
    CTRL_REG_2 = 2  # Write to permenant memory.
    CTRL_REG_2_SAVE_PARAMS = 1
    CTRL_REG_2_SAVE_TUNING = 32
    CTRL_REG_2_SAVE_USER_OPTS = 64
    CTRL_REG_2_SAVE_KINEMATIC_CONFIG = 128
    CTRL_REG_2_SAVE_HAPTIC_CONFIG = 512
    CTRL_REG_3 = 3  # Configure mode.
    CTRL_REG_4 = 4  # Configure defaults.
    CTRL_REG_4_SET_DEFAULT_PARAMS = 1
    CTRL_REG_4_SET_DEFAULT_TUNING = 2
    CTRL_REG_4_SET_DEFAULT_MOTOR_USER_OPTS = 4
    CTRL_REG_4_SET_DEFAULT_MODBUS_USER_OPTS = 8
    CTRL_REG_4_SET_DEFAULT_KINEMATIC_CONFIG = 16
    CTRL_REG_4_SET_DEFAULT_HAPTIC_CONFIG = 32
    #############
    # Kinematic #
    #############
    KIN_SW_TRIGGER = 9
    KIN_MOTION_0 = 780
    KIN_MOTION_1 = 786
    KIN_MOTION_2 = 792
    KIN_MOTION_3 = 798
    KIN_MOTION_4 = 804
    KIN_MOTION_5 = 810
    KIN_MOTION_6 = 816
    KIN_MOTION_7 = 822
    KIN_MOTION_8 = 828
    KIN_MOTION_9 = 834
    KIN_MOTION_10 = 840
    KIN_MOTION_11 = 846
    KIN_MOTION_12 = 852
    KIN_MOTION_13 = 858
    KIN_MOTION_14 = 864
    KIN_MOTION_15 = 870
    KIN_MOTION_16 = 876
    KIN_MOTION_17 = 882
    KIN_MOTION_18 = 888
    KIN_MOTION_19 = 894
    KIN_MOTION_20 = 900
    KIN_MOTION_21 = 906
    KIN_MOTION_22 = 912
    KIN_MOTION_23 = 918
    KIN_MOTION_24 = 924
    KIN_MOTION_25 = 930
    KIN_MOTION_26 = 936
    KIN_MOTION_27 = 942
    KIN_MOTION_28 = 948
    KIN_MOTION_29 = 954
    KIN_MOTION_30 = 960
    KIN_MOTION_31 = 966
    KIN_HOME_ID = 972
    KINEMATIC_STATUS = 319
    ##################
    # Haptic Effects #
    ##################
    # Constant Force.
    CONSTANT_FORCE_MN = 642
    CONSTANT_FORCE_MN_H = 643
    CONST_FORCE_FILTER = 672
    # Spring 0.
    S0_GAIN_N_MM = 644
    S0_CENTER_UM = 645
    S0_CENTER_UM_H = 646
    S0_COUPLING = 647
    S0_DEAD_ZONE_MM = 648
    S0_FORCE_SAT_N = 649
    # Spring 1.
    S1_GAIN_N_MM = 650
    S1_CENTER_UM = 651
    S1_CENTER_UM_H = 652
    S1_COUPLING = 653
    S1_DEAD_ZONE_MM = 654
    S1_FORCE_SAT_N = 655
    # Spring 2.
    S1_GAIN_N_MM = 656
    S1_CENTER_UM = 657
    S1_CENTER_UM_H = 658
    S1_COUPLING = 659
    S1_DEAD_ZONE_MM = 660
    S1_FORCE_SAT_N = 661
    # Damper.
    D0_GAIN_NS_MM = 662
    # Inertia.
    I0_GAIN_NS2_MM = 663
    # Oscillator 0.
    O0_GAIN_N = 664
    O0_TYPE = 665
    O0_FREQ_DHZ = 666
    O0_DUTY = 667
    # Oscillator 1.
    O0_GAIN_N = 668
    O0_TYPE = 669
    O0_FREQ_DHZ = 670
    O0_DUTY = 671
    #######################
    # Position Controller #
    #######################
    PC_PGAIN = 133
    PC_IGAIN = 134
    PC_DVGAIN = 135
    PC_DEGAIN = 136
    PC_FSATU = 137
    PC_FSATU_H = 138
    #############
    # Auto Zero #
    #############
    ZERO_MODE = 171
    AUTO_ZERO_FORCE_N = 172
    AUTO_ZERO_EXIT_MODE = 173
    AUTO_ZERO_MODE_NEGATIVE = 0
    AUTO_ZERO_MODE_MANUAL = 1
    AUTO_ZERO_MODE_ENABLED = 2
    AUTO_ZERO_MODE_ON_BOOT = 3
    ###########
    # Sensors #
    ###########
    STATOR_TEMP = 336
    DRIVER_TEMP = 337
    VDD_FINAL = 338
    SHAFT_POS_UM = 342
    SHAFT_POSITION_H = 343
    SHAFT_SPEED_MMPS = 344
    SHAFT_SHEED_H = 345
    SHAFT_ACCEL_MMPSS = 346
    SHAFT_ACCEL_H = 347
    FORCE = 348
    FORCE_H = 349
    POWER = 350
    AVG_POWER = 355
    COIL_TEMP = 356
    ##########
    # Limits #
    ##########
    # Actuator.
    MAX_TEMP = 401
    MIN_VOLTAGE = 402
    MAX_VOLTAGE = 403
    MAX_CURRENT = 404
    MAX_POWER = 405
    # User.
    USER_MAX_TEMP = 139
    USER_MAX_FORCE = 140
    USER_MAX_FORCE_H = 141
    USER_MAX_POWER = 142
    SAFETY_DGAIN = 143
    #################
    # Actuator Info #
    #################
    SERIAL_NUMBER_LOW = 406
    SERIAL_NUMBER_HIGH = 407
    MAJOR_VERSION = 408
    RELEASE_STATE = 409
    REVISION_NUMBER = 410
    COMMIT_ID_LO = 411
    COMMIT_ID_HI = 412
    HW_VERSION = 414
    COMMS_TIMEOUT = 417
    STATOR_CONFIG = 418
    ##########
    # Errors #
    ##########
    ERROR_0 = 432
    ERROR_1 = 433
