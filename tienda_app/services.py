from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro, Orden


class CompraRapidaService:
    """
    Paso 3: Service Layer para Compra Rápida.
    Orquesta: inventario, impuestos, pago (inyectado) y creación de Orden.
    """
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def obtener_detalle(self, libro_id):
        """Contexto para el GET: libro y total con IVA."""
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id):
        """
        Ejecuta la compra rápida: valida stock, cobra vía procesador, descuenta y crea Orden.
        Returns: total si OK.
        Raises: ValueError si no hay existencias o pago falla.
        """
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            raise ValueError("El libro no existe.")

        try:
            inv = Inventario.objects.get(libro=libro)
        except Inventario.DoesNotExist:
            raise ValueError("No hay inventario para este producto. Crea uno desde el shell.")

        if inv.cantidad <= 0:
            raise ValueError("No hay existencias.")

        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)

        if not self.procesador_pago.pagar(total):
            return None

        inv.cantidad -= 1
        inv.save()
        Orden.objects.create(libro=libro, total=total)
        return total


class CompraService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = get_object_or_404(Inventario, libro=libro)

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        # Uso del Builder: Semantica clara y validacion interna
        orden = (
            self.builder
            .con_usuario(usuario)
            .con_libro(libro)
            .con_cantidad(cantidad)
            .para_envio(direccion)
            .build()
        )

        # Uso del Factory (inyectado): Cambio de comportamiento sin cambio de codigo
        pago_exitoso = self.procesador_pago.pagar(orden.total)
        if not pago_exitoso:
            orden.delete()
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= cantidad
        inv.save()

        return orden.total
