import json
from django.db.models import Case, CharField, Sum, Max, Count, When, F, Q, Value, IntegerField
from django.db.models.functions import Concat, Extract
from django.db.models.functions import Upper
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.utils import timezone

from braces.views import (
    JSONResponseMixin,
    AjaxResponseMixin,
    LoginRequiredMixin,
    SelectRelatedMixin,
    PrefetchRelatedMixin
)

from biable.models import (
    MovimientoVentaBiable,
    Actualizacion,
    Cartera,
    FacturasBiable
)

from usuarios.models import Colaborador
from cotizaciones.models import Cotizacion
from .mixins import (
    InformeVentasConAnoMixin,
    FechaActualizacionMovimientoVentasMixin,
    InformeVentasConLineaMixin
)


# Create your views here.

class VentasVendedor(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin,
                     InformeVentasConAnoMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxvendedor.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')

        qs = self.consulta(ano, mes)
        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        current_user = self.request.user
        qs = FacturasBiable.activas.all().values('vendedor__nombre').annotate(
            # vendedor_nombre=F('vendedor__nombre'),
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
            linea=F('vendedor__linea_ventas__nombre'),
        )

        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            qsFinal = qs.filter(
                (
                    Q(fecha_documento__year__in=list(map(lambda x: int(x), ano))) &
                    Q(fecha_documento__month__in=list(map(lambda x: int(x), mes)))
                ) &
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all()) |
                    Q(vendedor__colaborador=usuario)
                )
            ).distinct()
        else:
            qsFinal = qs.filter(
                Q(fecha_documento__year__in=list(map(lambda x: int(x), ano))) &
                Q(fecha_documento__month__in=list(map(lambda x: int(x), mes)))).order_by('-vendedor__activo', 'day')
        return qsFinal.order_by('-vendedor__activo')


class VentasVendedorConsola(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin,
                            InformeVentasConAnoMixin,
                            FechaActualizacionMovimientoVentasMixin,
                            TemplateView):
    template_name = 'reportes/venta/consolaxventasxvendedor.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        qs = self.consulta(ano, mes)
        lista = list(qs)

        for i in lista:
            i["v_neto"] = int(i["v_neto"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        current_user = self.request.user
        qs = FacturasBiable.activas.all().values('fecha_documento').annotate(
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            vendedor_nombre_real=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            cliente=F('cliente__nombre'),
            documento=Concat('tipo_documento', Value('-'), 'nro_documento'),
            tipo_documento=F('tipo_documento'),
            v_neto=Sum('venta_neto'),
            linea=F('vendedor__linea_ventas__nombre'),
            day=Extract('fecha_documento', 'day')
        )
        if not current_user.has_perm('biable.reporte_ventas_todos_vendedores'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            qsFinal = qs.filter(
                Q(fecha_documento__year__in=list(map(lambda x: int(x), ano))) &
                Q(fecha_documento__month__in=list(map(lambda x: int(x), mes))) &
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all())
                    | Q(vendedor__colaborador=usuario)
                    | Q(vendedor__activo=False)
                )
            ).distinct().order_by('-vendedor__activo', 'fecha_documento')
        else:
            qsFinal = qs.filter(
                Q(fecha_documento__year__in=list(map(lambda x: int(x), ano))) &
                Q(fecha_documento__month__in=list(map(lambda x: int(x), mes)))).order_by('-vendedor__activo',
                                                                                         'fecha_documento')
        return qsFinal


class VentasClientes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                     InformeVentasConLineaMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxcliente.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        total_fact = qs.aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('cliente__nit').annotate(fac=Sum('venta_neto')).order_by('-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['cliente__nit'])

        qs = qs.annotate(
            tipo=Case(
                When(cliente__nit__in=pareto,
                     then=Value('Pareto')),
                default=Value('Otros'),
                output_field=CharField(),
            )
        ).order_by('-v_neto')

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = FacturasBiable.activas.all().values('cliente__nombre').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano)),
            fecha_documento__month__in=list(map(lambda x: int(x), mes))
        )
        return qs


class VentasClientesAno(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                        InformeVentasConLineaMixin,
                        FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxclientexano.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion
        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        max_year = qs.aggregate(Max('year'))['year__max']
        total_fact = qs.filter(year=max_year).aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('cliente__nit').annotate(fac=Sum('venta_neto')).filter(year=max_year).order_by(
                '-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['cliente__nit'])

        qs = qs.annotate(tipo=Case(
            When(cliente__nit__in=pareto,
                 then=Value('Pareto')),
            default=Value('Otros'),
            output_field=CharField(),
        )).order_by('-v_neto')

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = FacturasBiable.activas.all().values('cliente__nombre').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
            year=Extract('fecha_documento', 'year')
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano)),
            fecha_documento__month__in=list(map(lambda x: int(x), mes))
        )
        return qs


class VentasMes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConLineaMixin,
                InformeVentasConAnoMixin,
                FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.get('ano')
        linea = self.request.POST.get('linea')
        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = FacturasBiable.activas.values('fecha_documento').annotate(
            mes=Extract('fecha_documento', 'month'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100)
        ).filter(fecha_documento__year=ano).order_by('fecha_documento')
        return qs


class VentasLineaAno(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                     InformeVentasConLineaMixin,
                     FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxlineaxano.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano, mes)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qs = FacturasBiable.activas.all().values('vendedor__linea_ventas_id').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            year=Extract('fecha_documento', 'month'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano)),
            fecha_documento__month__in=list(map(lambda x: int(x), mes))
        ).order_by('-v_bruta')
        return qs


class VentasVendedorMes(JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin,
                        FechaActualizacionMovimientoVentasMixin, InformeVentasConLineaMixin, TemplateView):
    template_name = 'reportes/venta/ventasxvendedorxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista

        return self.render_json_response(context)

    def consulta(self, ano):
        qs = FacturasBiable.activas.all().values('vendedor_id').annotate(
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            month=Extract('fecha_documento', 'month'),
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano))
        )
        return qs


class VentasLineaAnoMes(JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin, InformeVentasConLineaMixin,
                        FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxlineaxanoxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        lista = list(qs)
        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = FacturasBiable.activas.all().values('vendedor__linea_ventas_id').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            renta=Sum('rentabilidad'),
            year=Extract('fecha_documento', 'year'),
            month=Extract('fecha_documento', 'month'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano))
        ).order_by('month')
        return qs


class VentasClienteMes(JSONResponseMixin, AjaxResponseMixin, InformeVentasConAnoMixin, InformeVentasConLineaMixin,
                       FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventasxclientexmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('ano')
        linea = self.request.POST.get('linea')

        qs = self.consulta(ano)

        if not linea == "0":
            qs = qs.filter(vendedor__linea_ventas_id=linea)

        total_fact = qs.aggregate(Sum('venta_neto'))["venta_neto__sum"]

        pareto = []
        sum = 0
        for cli in qs.values('cliente__nit').annotate(fac=Sum('venta_neto')).order_by('-fac').all():
            sum += (int(cli['fac']) / total_fact) * 100
            if sum <= 80:
                pareto.append(cli['cliente__nit'])

        qs = qs.annotate(tipo=Case(
            When(cliente__nit__in=pareto,
                 then=Value('Pareto')),
            default=Value('Otros'),
            output_field=CharField(),
        )).order_by('month', 'cliente')

        lista = list(qs)

        for i in lista:
            i["v_bruta"] = int(i["v_bruta"])
            i["Costo"] = int(i["Costo"])
            i["v_neto"] = int(i["v_neto"])
            i["renta"] = int(i["renta"])
            i["Descuentos"] = int(i["Descuentos"])
        context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano):
        qs = FacturasBiable.activas.all().values('cliente__nombre').annotate(
            v_bruta=Sum('venta_bruta'),
            v_neto=Sum('venta_neto'),
            Descuentos=Sum('dscto_netos'),
            Costo=Sum('costo_total'),
            month=Extract('fecha_documento', 'month'),
            renta=Sum('rentabilidad'),
            Margen=(Sum('rentabilidad') / Sum('venta_neto') * 100),
        ).filter(
            fecha_documento__year__in=list(map(lambda x: int(x), ano))
        )
        return qs


class CarteraVencimientos(JSONResponseMixin, ListView):
    template_name = 'reportes/cartera/vencimientos.html'
    model = Cartera
    context_object_name = 'cartera_list'

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        context = super().get_context_data(**kwargs)
        ultima_actualizacion = Actualizacion.tipos.cartera_vencimiento()
        if ultima_actualizacion:
            ultima_actualizacion = ultima_actualizacion.latest('fecha')
            context = {"fecha_actualizacion": ultima_actualizacion.fecha_formateada()}

        qsFinal = None

        qs = self.get_queryset()
        qs = qs.values(
            'nro_documento',
            'tipo_documento',
            'forma_pago',
            'dias_vencido',
            'dias_para_vencido',
            'fecha_ultimo_pago',
            'fecha_documento',
            'fecha_vencimiento',
            'debe',
            'recaudado',
            'a_recaudar',
            'cliente',
            'client_id',
        ).annotate(
            tipo=Case(
                When(esta_vencido=True,
                     then=Value('Vencido')),
                default=Value('Corriente'),
                output_field=CharField(),
            ),
            vendedor_nombre=Case(
                When(vendedor__activo=False, then=Value('VENDEDORES INACTIVOS')),
                default=F('vendedor__nombre'),
                output_field=CharField(),
            ),
            forma_pago_tipo=Case(
                When(forma_pago__lte=30, then=Value('0-30')),
                When(forma_pago__lte=60, then=Value('31-60')),
                When(forma_pago__lte=90, then=Value('61-90')),
                default=Value('Más de 90'),
                output_field=CharField(),
            ),
        ).order_by('-dias_vencido', '-debe')

        if not current_user.has_perm('biable.ver_carteras_todos'):
            usuario = get_object_or_404(Colaborador, usuario__user=current_user)
            clientes = Cartera.objects.values_list('client_id').filter(vendedor__colaborador=usuario,
                                                                       esta_vencido=True).distinct()
            clientes_subalternos = Cartera.objects.values_list('client_id').filter(
                vendedor__colaborador__in=usuario.subalternos.all()).distinct()
            qsFinal = qs.filter(
                (
                    Q(vendedor__colaborador__in=usuario.subalternos.all())
                    | Q(vendedor__colaborador=usuario)
                    | Q(vendedor__activo=False)
                    | Q(client_id__in=clientes, esta_vencido=True)
                    | Q(client_id__in=clientes_subalternos)
                )
            ).distinct()
        else:
            qsFinal = qs

        lista = list(qsFinal)

        for i in lista:
            i["debe"] = int(i["debe"])
            i["recaudado"] = int(i["recaudado"])
            i["a_recaudar"] = int(i["a_recaudar"])

        context['datos'] = json.dumps(lista,
                                      cls=self.json_encoder_class,
                                      **self.get_json_dumps_kwargs()).encode('utf-8')
        return context


class TrabajoCotizacionVentaVendedorAnoMes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin,
                                           InformeVentasConAnoMixin,
                                           FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/trabajo/cotizacionesyventasxanoxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')

        if usuario.has_perm('biable.reporte_ventas_todos_vendedores'):
            qs = self.consulta(ano, mes)
            lista = qs
            for i in lista:
                i["nro_cotizaciones"] = int(i["nro_cotizaciones"])
                i["total_cotizaciones"] = int(i["total_cotizaciones"])
                i["descuentos_cotizaciones"] = int(i["descuentos_cotizaciones"])
                i["facturacion"] = int(i["facturacion"])
                i["nro_ventas"] = int(i["nro_ventas"])
            context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qsCotizacion = Cotizacion.objects.values('usuario').annotate(
            vendedor=Upper(Concat('usuario__first_name', Value(' '), 'usuario__last_name')),
            ano_consulta=Extract('fecha_envio', 'year'),
            mes_consulta=Extract('fecha_envio', 'month'),
            dia_consulta=Extract('fecha_envio', 'day'),
            dia_semana_consulta=Extract('fecha_envio', 'week_day'),
            hora_consulta=Extract('fecha_envio', 'hour'),
            nro_cotizaciones=Count('id'),
            total_cotizaciones=Sum('total'),
            descuentos_cotizaciones=Sum('descuento'),
            nro_ventas=Value(0, output_field=IntegerField()),
            facturacion=Value(0, output_field=IntegerField()),
            vendedor__colaborador__usuario=Value(0, output_field=IntegerField()),

        ).filter(fecha_envio__month__in=mes, fecha_envio__year__in=ano).order_by('fecha_envio', 'dia_semana_consulta')

        qsFacturacion = FacturasBiable.activas.values('vendedor__colaborador__usuario').annotate(
            vendedor=Upper(Case(
                When(vendedor__colaborador__isnull=True, then=F('vendedor__nombre')),
                default=Concat('vendedor__colaborador__usuario__user__first_name', Value(' '),
                               'vendedor__colaborador__usuario__user__last_name'),
                output_field=CharField(),
            )),
            ano_consulta=Extract('fecha_documento', 'year'),
            mes_consulta=Extract('fecha_documento', 'month'),
            dia_consulta=Extract('fecha_documento', 'day'),
            dia_semana_consulta=Extract('fecha_documento', 'week_day'),
            nro_cotizaciones=Value(0, output_field=IntegerField()),
            nro_ventas=Count('id'),
            total_cotizaciones=Value(0, output_field=IntegerField()),
            descuentos_cotizaciones=Value(0, output_field=IntegerField()),
            facturacion=Sum('venta_neto'),
        ).filter(fecha_documento__month__in=mes, fecha_documento__year__in=ano)

        uno = list(qsCotizacion)
        dos = list(qsFacturacion)
        tres = []
        tres.extend(uno)
        tres.extend(dos)
        return tres


class VentasProductoAnoMes(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin,
                           InformeVentasConAnoMixin,
                           FechaActualizacionMovimientoVentasMixin, TemplateView):
    template_name = 'reportes/venta/ventaxproductoxanoxmes.html'

    def post_ajax(self, request, *args, **kwargs):
        context = {}
        usuario = self.request.user
        ultima_actualizacion = self.get_ultima_actualizacion()
        if ultima_actualizacion:
            context["fecha_actualizacion"] = ultima_actualizacion

        ano = self.request.POST.getlist('anos[]')
        mes = self.request.POST.getlist('meses[]')

        if usuario.has_perm('biable.reporte_ventas_todos_vendedores'):
            qs = self.consulta(ano, mes)
            lista = list(qs)
            for i in lista:
                i["venta_neta"] = int(i["venta_neta"])
                i["cantidad_neta"] = int(i["cantidad_neta"])
            context["lista"] = lista
        return self.render_json_response(context)

    def consulta(self, ano, mes):
        qFinal = MovimientoVentaBiable.objects.values(
            'item_biable__descripcion',
            'item_biable__descripcion_dos',
            'item_biable__categoria_mercadeo',
            'item_biable__categoria_mercadeo_dos',
            'item_biable__categoria_mercadeo_tres',
            'item_biable__serie',
            'item_biable__id_item',
            'factura__vendedor__linea_ventas__nombre',
            'factura__cliente__nombre'
        ).annotate(
            year=Extract('factura__fecha_documento', 'year'),
            month=Extract('factura__fecha_documento', 'month'),
            vendedor=Upper(Case(
                When(factura__vendedor__colaborador__isnull=True, then=F('factura__vendedor__nombre')),
                default=Concat('factura__vendedor__colaborador__usuario__user__first_name', Value(' '),
                               'factura__vendedor__colaborador__usuario__user__last_name'),
                output_field=CharField(),
            )),
            venta_neta=Sum('venta_neto'),
            cantidad_neta=Sum('cantidad'),
        ).filter(factura__fecha_documento__year__in=ano, month__in=mes, factura__activa=True)
        return qFinal


class MargenesFacturaView(LoginRequiredMixin,
                          PrefetchRelatedMixin,
                          InformeVentasConAnoMixin,
                          InformeVentasConLineaMixin,
                          FechaActualizacionMovimientoVentasMixin,

                          ListView):
    queryset = FacturasBiable.activas.all()
    context_object_name = 'facturas_list'
    template_name = 'reportes/margenes/margenxfactura.html'
    prefetch_related = ['vendedor', 'cliente']

    def get_queryset(self):
        linea = self.request.GET.getlist('linea')
        ano = self.request.GET.getlist('ano')
        mes = self.request.GET.getlist('mes')
        qs = super().get_queryset()
        qs = qs.annotate(
            margen=(F('rentabilidad') / F('venta_neto')) * 100
        ).filter(
            fecha_documento__year__in=ano,
            fecha_documento__month__in=mes,
            vendedor__linea_ventas_id__in=linea
        ).order_by('margen')
        return qs


class MargenesItemView(LoginRequiredMixin,
                       PrefetchRelatedMixin,
                       InformeVentasConAnoMixin,
                       InformeVentasConLineaMixin,
                       FechaActualizacionMovimientoVentasMixin,

                       ListView):
    queryset = MovimientoVentaBiable.objects.all()
    context_object_name = 'movimientos_list'
    template_name = 'reportes/margenes/margenxitem.html'
    prefetch_related = [
        'factura',
        'factura__vendedor',
        'factura__cliente',
        'item_biable'
    ]

    def get_queryset(self):
        linea = self.request.GET.getlist('linea')
        ano = self.request.GET.getlist('ano')
        mes = self.request.GET.getlist('mes')
        qs = super().get_queryset()
        qs = qs.annotate(
            margen=(F('rentabilidad') / F('venta_neto')) * 100
        ).filter(
            factura__fecha_documento__year__in=ano,
            factura__fecha_documento__month__in=mes,
            factura__vendedor__linea_ventas_id__in=linea,
            factura__activa=True
        ).order_by('margen')
        return qs


class RevisionVendedoresRealesVsCguno(LoginRequiredMixin, SelectRelatedMixin, ListView):
    now = timezone.now()
    queryset = FacturasBiable.objects.filter(
        Q(fecha_documento__month=now.month) &
        Q(fecha_documento__year=now.year) &
        ~Q(vendedor_id=1) &
        ~Q(vendedor=F('sucursal__vendedor_real')) &
        Q(activa=True)
    )
    context_object_name = 'vendedores_diferentes_list'
    template_name = 'reportes/venta/vendedores_diferentes_facturacion.html'
    select_related = [
        'vendedor',
        'sucursal__vendedor_real',
        'cliente'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['fecha_actual'] = now
        return context
