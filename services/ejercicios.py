from dataclasses import dataclass, field
from typing import Any


@dataclass
class Ejercicio:
    id: str
    numero: int
    titulo: str
    enunciado: str
    dificultad: str  # 'basico', 'intermedio', 'avanzado'
    sql: str
    params: dict[str, Any] = field(default_factory=dict)
    orden_importa: bool = False
    modulo: str = ""  # slug del módulo al que pertenece (p.ej. "select-y-limit")
