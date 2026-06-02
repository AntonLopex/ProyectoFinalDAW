import enum


class RolEnum(enum.Enum):
    admin     = "admin"
    cliente   = "cliente"
    control   = "control"
    comercial = "comercial"
    proveedor = "proveedor"
    invitado   = "invitado"


class TipoAccesoEnum(enum.Enum):
    qr     = "QR"
    manual = "Manual"
    
class TipoVCEnum(enum.Enum):
    V = "V"
    C = "C"
     

class EstadoStandEnum(enum.Enum):
    disponible = "disponible"
    pre_reservado = "pre_reservado"
    ocupado = "ocupado"
    no_disponible = "no_disponible"
