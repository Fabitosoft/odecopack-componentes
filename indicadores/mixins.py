import json

from braces.views import JSONResponseMixin
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils import timezone

from biable.models import VendedorBiable, FacturasBiable, SeguimientoCliente
from cotizaciones.models import Cotizacion
from usuarios.models import Colaborador


class IndicadorMesMixin(JSONResponseMixin, object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        if usuario.has_perm('trabajo_diario.ver_trabajo_diario'):
            if not usuario.has_perm('biable.reporte_ventas_todos_vendedores'):
                try:
                    subalternos = Colaborador.objects.get(usuario__user=usuario).subalternos.all()
                except Colaborador.DoesNotExist:
                    subalternos = None
            else:
                subalternos = Colaborador.objects.all()

            indicadores_vendedores = []
            fecha_hoy = timezone.localtime(timezone.now()).date()
            day = fecha_hoy.day
            year = fecha_hoy.year
            month = fecha_hoy.month

            mi_indicador = self.consulta(year, month, day, usuario_sesion=usuario)
            if mi_indicador:
                indicadores_vendedores.append(mi_indicador)

            if subalternos:
                vendedores_biable = VendedorBiable.objects.select_related('colaborador__usuario__user').filter(
                    Q(colaborador__in=subalternos) &
                    ~Q(colaborador__usuario__user=usuario)
                ).distinct()

                # Indicadores de Venta
                for vendedor in vendedores_biable:
                    indicador = self.consulta(year, month, day, vendedor_subalterno=vendedor)
                    if indicador:
                        indicadores_vendedores.append(indicador)

            context['indicadores_venta'] = indicadores_vendedores

        return context

    def consulta(self, year, month, day, vendedor_subalterno=None, usuario_sesion=None):

        vendedores_usuario = []  # Traemos vendedores biable relacionados al usuario actual
        if usuario_sesion:
            vendedores_usuario = VendedorBiable.objects.select_related('colaborador__usuario__user').filter(
                colaborador__usuario__user=usuario_sesion)

        facturacion_ventas_mes = 0
        cantidad_venta_mes = 0
        facturacion_ventas_dia = 0
        cantidad_venta_dia = 0

        # Indicadores Cotizaciones
        facturacion_cotizaciones_mes = 0
        cantidad_cotizaciones_mes = 0
        facturacion_cotizaciones_dia = 0
        cantidad_cotizaciones_dia = 0

        facturacion_linea_mes = 0
        mi_participacion_facturacion = 0

        qsVentasMes = FacturasBiable.activas.select_related(
            'vendedor__colaborador__usuario__user'
        ).values(
            'vendedor__colaborador__usuario__user'
        ).annotate(
            fact_neta=Sum('venta_neto'),
            cantidad=Count('nro_documento', 'tipo_documento')
        ).filter(
            fecha_documento__year=year,
            fecha_documento__month=month
        )

        if vendedor_subalterno:
            qsVentasMes = qsVentasMes.filter(
                vendedor=vendedor_subalterno
            )
        elif usuario_sesion:
            qsVentasMes = qsVentasMes.filter(
                vendedor__in=vendedores_usuario
            ).distinct()

        if qsVentasMes.exists():
            facturacion_ventas_mes = float(qsVentasMes[0]['fact_neta'])
            cantidad_venta_mes = float(qsVentasMes[0]['cantidad'])

        qsVentasDia = qsVentasMes.filter(fecha_documento__day=day)

        if qsVentasDia.exists():
            facturacion_ventas_dia = float(qsVentasDia[0]['fact_neta'])
            cantidad_venta_dia = float(qsVentasDia[0]['cantidad'])

        qsCotizacionesMes = Cotizacion.objects.values('usuario').annotate(
            valor=Sum('total'),
            cantidad=Count('id')
        ).filter(
            fecha_envio__month=month,
            fecha_envio__year=year
        )

        if vendedor_subalterno:
            qsCotizacionesMes = qsCotizacionesMes.filter(
                usuario__user_extendido__colaborador__mi_vendedor_biable=vendedor_subalterno
            )
        elif usuario_sesion:
            qsCotizacionesMes = qsCotizacionesMes.filter(
                usuario=usuario_sesion
            )

        if qsCotizacionesMes.exists():
            facturacion_cotizaciones_mes = float(qsCotizacionesMes[0]['valor'])
            cantidad_cotizaciones_mes = float(qsCotizacionesMes[0]['cantidad'])

        qsCotizacionesDia = qsCotizacionesMes.filter(fecha_envio__day=day)

        if qsCotizacionesDia.exists():
            facturacion_cotizaciones_dia = float(qsCotizacionesDia[0]['valor'])
            cantidad_cotizaciones_dia = float(qsCotizacionesDia[0]['cantidad'])

        if facturacion_cotizaciones_mes > 0:
            tasa_conversion_ventas_mes = (facturacion_ventas_mes / facturacion_cotizaciones_mes) * 100
        else:
            tasa_conversion_ventas_mes = 0

        if vendedor_subalterno:
            nombre = vendedor_subalterno.colaborador.usuario.user.get_full_name()
        else:
            nombre = "Mi Indicador"

        # obtenemos la facturacion total del mes
        total_linea = FacturasBiable.activas.filter(
            fecha_documento__year=year,
            fecha_documento__month=month,
        )

        if vendedor_subalterno:
            total_linea = total_linea.filter(vendedor__linea_ventas_id=vendedor_subalterno.linea_ventas_id)
        else:
            lineas = vendedores_usuario.values('linea_ventas_id').distinct()
            total_linea = total_linea.filter(vendedor__linea_ventas_id__in=lineas).distinct()

        total_linea = total_linea.aggregate(
            fact_neta=Sum('venta_neto')
        )
        if total_linea['fact_neta']:
            facturacion_linea_mes = total_linea['fact_neta']
            mi_participacion_facturacion = (facturacion_ventas_mes / float(total_linea['fact_neta'])) * 100

        # obtenemos las visitas al cliente
        qs_visitas = SeguimientoCliente.objects.filter(
            tipo='Visita',
            fecha_seguimiento__year=year,
            fecha_seguimiento__month=month,
        )

        if vendedor_subalterno:
            qs_visitas = qs_visitas.filter(
                creado_por__user_extendido__colaborador__mi_vendedor_biable=vendedor_subalterno
            )
        elif usuario_sesion:
            qs_visitas = qs_visitas.filter(
                creado_por=usuario_sesion
            )

        indicador = None

        if facturacion_ventas_mes > 0 or cantidad_cotizaciones_mes > 0:
            indicador = {
                'nombre': nombre,
                'facturacion_venta_mes': facturacion_ventas_mes,
                'facturacion_venta_dia': facturacion_ventas_dia,
                'cantidad_venta_mes': cantidad_venta_mes,
                'cantidad_venta_dia': cantidad_venta_dia,
                'valor_cotizacion_mes': facturacion_cotizaciones_mes,
                'valor_cotizacion_dia': facturacion_cotizaciones_dia,
                'cantidad_cotizaciones_mes': cantidad_cotizaciones_mes,
                'cantidad_cotizaciones_dia': cantidad_cotizaciones_dia,
                'tasa_conversion_ventas_mes': tasa_conversion_ventas_mes,
                'facturacion_linea_mes': facturacion_linea_mes,
                'mi_participacion_facturacion': mi_participacion_facturacion,
                'visitas_cliente_mes': qs_visitas.count(),
                'visitas_cliente_dia': qs_visitas.filter(fecha_seguimiento__day=day).count(),
            }

        return indicador
