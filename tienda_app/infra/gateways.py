import datetime
from pathlib import Path

from ..domain.interfaces import ProcesadorPago

# Raíz del proyecto (carpeta donde está manage.py) para que el .log siempre esté ahí
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_FILE = PROJECT_ROOT / "pagos_locales_MATIAS_MARTINEZ_MORENO.log"


class BancoNacionalProcesador(ProcesadorPago):
    """
    Implementación concreta de la infraestructura.
    Simula un banco local escribiendo en un log.
    """
    def pagar(self, monto: float) -> bool:
        # Simulamos una operación de red o persistencia externa
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] BANCO NACIONAL - Cobro procesado: ${monto}\n")
        return True