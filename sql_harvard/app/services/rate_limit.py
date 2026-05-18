import time
from collections import defaultdict

from fastapi import Request, HTTPException


class RateLimiter:
    def __init__(self, peticiones: int = 10, ventana: int = 60):
        self.peticiones = peticiones
        self.ventana = ventana
        self._registros: dict[str, list[float]] = defaultdict(list)

    def __call__(self, request: Request):
        ip = request.client.host if request.client else "unknown"
        ahora = time.time()
        corte = ahora - self.ventana

        self._registros[ip] = [t for t in self._registros[ip] if t > corte]

        if len(self._registros[ip]) >= self.peticiones:
            raise HTTPException(status_code=429, detail="Demasiadas consultas. Espera unos segundos.")

        self._registros[ip].append(ahora)


limitar_consulta = RateLimiter(peticiones=10, ventana=60)
