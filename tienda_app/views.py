import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View

from .models import Libro, Inventario, Orden
from .infra.factories import PaymentFactory
from .services import CompraService, CompraRapidaService


def home(request):
    """Redirige a la compra rápida del primer libro (para probar el tutorial)."""
    primer_libro = Libro.objects.first()
    if primer_libro:
        return redirect('compra_rapida_fbv', libro_id=primer_libro.id)
    return HttpResponse("No hay libros. Crea uno desde: python manage.py shell", status=404)


def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        # VIOLACION SRP: Logica de inventario en la vista
        inventario = Inventario.objects.get(libro=libro)
        if inventario.cantidad > 0:
            # VIOLACION OCP: Calculo de negocio hardcoded
            total = float(libro.precio) * 1.19

            # VIOLACION DIP: Proceso de pago acoplado al file system
            with open("pagos_manuales.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Pago FBV: ${total}\n")

            inventario.cantidad -= 1
            inventario.save()
            Orden.objects.create(libro=libro, total=total)

            return HttpResponse(f"Compra exitosa: {libro.titulo}")
        else:
            return HttpResponse("Sin stock", status=400)

    total_estimado = float(libro.precio) * 1.19
    return render(request, 'tienda_app/compra_rapida.html', {
        'libro': libro,
        'total': total_estimado
    })


class CompraRapidaView(View):  # delega todo en CompraRapidaService
    template_name = 'tienda_app/compra_rapida.html'

    def _servicio(self): return CompraRapidaService(procesador_pago=PaymentFactory.get_processor())

    def get(self, request, libro_id): return render(request, self.template_name, self._servicio().obtener_detalle(libro_id))

    def post(self, request, libro_id):
        try: total = self._servicio().procesar(libro_id); return HttpResponse(f"Compra exitosa: {get_object_or_404(Libro, id=libro_id).titulo}") if total else HttpResponse("Error en el pago", status=400)
        except ValueError as e: return HttpResponse(str(e), status=400)


class CompraView(View):
    
    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${float(total):.2f} USD",
                    'total': total,
                },
            )
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)
