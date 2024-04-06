from enum import Enum


class DocumentStatus(Enum):
    INTEGRATED = 'INTEGRADO'
    PENDING_INTEGRATION = 'PENDENTE_INTEGRACAO'
    ERROR_INTEGRATION = 'ERRO_INTEGRACAO'


class DocumentMovementType(Enum):
    INPUT = 'E',
    OUTPUT = 'S'

