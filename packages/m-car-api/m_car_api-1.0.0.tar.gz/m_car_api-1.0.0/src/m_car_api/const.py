OBSUFACTOR_TOKEN = 234
DEFAULT_ROOT_URL = bytes(
    i ^ OBSUFACTOR_TOKEN
    for i in (
        130,
        158,
        158,
        154,
        153,
        208,
        197,
        197,
        139,
        154,
        131,
        196,
        139,
        154,
        154,
        196,
        135,
        131,
        134,
        143,
        153,
        199,
        135,
        133,
        136,
        131,
        134,
        131,
        158,
        147,
        196,
        137,
        133,
        135,
        197,
    )
).decode("utf-8")
V_URL_PATH = bytes(
    i ^ OBSUFACTOR_TOKEN
    for i in (
        197,
        135,
        133,
        136,
        131,
        134,
        143,
        197,
        188,
        143,
        130,
        131,
        137,
        134,
        143,
        153,
    )
).decode("utf-8")
U_HEL_URL_PATH = bytes(
    i ^ OBSUFACTOR_TOKEN
    for i in (
        197,
        135,
        133,
        136,
        131,
        134,
        143,
        197,
        191,
        153,
        143,
        152,
        162,
        143,
        134,
        134,
        133,
    )
).decode("utf-8")
