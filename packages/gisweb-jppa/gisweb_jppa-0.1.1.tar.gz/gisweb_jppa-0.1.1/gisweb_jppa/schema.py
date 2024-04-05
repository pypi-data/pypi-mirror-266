from typing import Any, List, Dict
from pydantic import BaseModel, EmailStr, HttpUrl, PrivateAttr
from enum import Enum


class ITipoEnum(str, Enum):
    FISICA = "F"
    GIURIDICA = "G"

class IPersona(BaseModel):
    tipo: str
    codice: str
    nome: str | None
    cognome: str | None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    localita: str | None = None
    provincia: str | None = None
    nazione: str | None = None
    email: str | None
    
class IImporto(BaseModel):
    codice: str
    descrizione: str | None = None
    importo: float
    capitolo: str | None = None
    
class IDebito(BaseModel):
    idpos: str #max 256
    codice: str | None = None
    dettaglio: str #max 1000
    iddeb: str #univoco max 256
    iuv: str | None = None
    gruppo: str | None = None
    ordinamento: int | None = None
    data_inizio: str
    data_fine: str | None = None
    data_limite: str | None = None
    importo: float
    causale: str # max 140 
    importi: list[IImporto]
    
class IPagoPa(BaseModel):
    soggetto: IPersona
    debito: IDebito

class IEsito(BaseModel):
    esito: str
    errore: str | None = None
    descrizione: str | None = None

class IConfig(BaseModel):
    wsUrl: str
    wsUser: str
    wsPassword: str
    wsPrintUrl: str
    codiceIpa: str
    codiceServizio: str
    notificaOK: str
    notificaKO: str
    notificaPagamento: str



