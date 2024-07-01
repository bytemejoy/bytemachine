from enum import Enum


class Constants:
    class Modbus(Enum):
        READ = 3
        WRITE = 6
        WRITE_MULTI = 16
        MOTOR_COMMAND = 100
        MOTOR_READ = 104
        MOTOR_WRITE = 105

    class Mode(Enum):
        SLEEP_MODE     = 1
        FORCE_MODE     = 2
        POSITION_MODE  = 3
        HAPTIC_MODE    = 4
        KINEMATIC_MODE = 5

    class HapticEffect(Enum):
        CONST_F  = 0b1
        SPRING_0 = 0b10
        SPRING_1 = 0b100
        SPRING_2 = 0b1000
        DAMPER   = 0b10000
        INERTIA  = 0b100000
        OSC_0    = 0b1000000
        OSC_1    = 0b10000000

    class ControlRegister(Enum):
        CTRL_REG_0 = 0
        CTRL_REG_1 = 1
        CTRL_REG_2 = 2
        CTRL_REG_3 = 3
