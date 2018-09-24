from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.signals import post_save
from django.urls import reverse

from model_utils.models import TimeStampedModel
from cotizaciones.models import Cotizacion
from despachos_mercancias.models import EnvioTransportadoraTCC
from biable.models import FacturasBiable


# Create your models here.

class TrabajoDiario(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User)
    nro_tareas = models.PositiveIntegerField(default=0)
    nro_tareas_sin_atender = models.PositiveIntegerField(default=0)
    nro_tareas_atendidas = models.PositiveIntegerField(default=0)
    porcentaje_atendido = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    def get_absolute_url(self):
        return reverse("trabajo_diario:trabajo-detail", kwargs={"pk": self.pk})

    def set_actualizar_seguimiento_trabajo(self):
        nro_tareas_envio_tcc = self.tareas_envios_tcc.aggregate(Count('id'))['id__count']
        nro_tareas_cotizacion = self.tareas_cotizacion.aggregate(Count('id'))['id__count']
        nro_tareas_cartera = self.tareas_cartera.aggregate(Count('id'))['id__count']

        nro_tareas_envio_tcc_sin_antender = self.tareas_envios_tcc.filter(estado=0).aggregate(Count('id'))['id__count']
        nro_tareas_cotizacion_sin_antender = self.tareas_cotizacion.filter(estado=0).aggregate(Count('id'))['id__count']
        nro_tareas_cartera_sin_antender = self.tareas_cartera.filter(estado=0).aggregate(Count('id'))['id__count']

        self.nro_tareas = nro_tareas_envio_tcc + nro_tareas_cotizacion + nro_tareas_cartera
        self.nro_tareas_sin_atender = nro_tareas_envio_tcc_sin_antender + nro_tareas_cotizacion_sin_antender + nro_tareas_cartera_sin_antender
        self.nro_tareas_atendidas = self.nro_tareas - self.nro_tareas_sin_atender
        self.porcentaje_atendido = 0
        if self.nro_tareas > 0:
            self.porcentaje_atendido = (self.nro_tareas_atendidas / self.nro_tareas) * 100
        self.save()

    class Meta:
        permissions = (
            ('ver_trabajo_diario', 'Ver Trabajo Diario'),
        )


# region Bases Seguimiento Tareas
class Seguimiento(TimeStampedModel):
    observacion = models.TextField(max_length=300)
    usuario = models.ForeignKey(User)

    class Meta:
        abstract = True


class Tarea(TimeStampedModel):
    ESTADOS = (
        (0, 'Pendiente'),
        (1, 'Atendida en Proceso'),
        (2, 'Atendida Terminada'),
    )
    estado = models.PositiveIntegerField(choices=ESTADOS, default=0)
    descripcion = models.TextField(max_length=400, null=True, blank=True)

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# endregion

# region Tarea Cotizacion
class TareaCotizacion(Tarea):
    cotizacion = models.OneToOneField(Cotizacion, related_name='tarea_diaria_cotizacion', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    trabajo_diario = models.ForeignKey(TrabajoDiario, on_delete=models.PROTECT, related_name='tareas_cotizacion',
                                       null=True)

    def get_absolute_url(self):
        return reverse("trabajo_diario:tarea-cotizacion-detalle", kwargs={"pk": self.pk})

    def get_descripcion_tarea(self):
        nro_tareas = self.cotizacion.mis_tareas.filter(esta_finalizada=False).aggregate(Count('id'))['id__count']
        nro_seguimiento_remisiones = self.cotizacion.mis_remisiones.filter(entregado=False).aggregate(Count('id'))[
            'id__count']

        cliente = self.cotizacion.cliente_biable
        if cliente:
            nombre_cliente = cliente.nombre
        else:
            nombre_cliente = self.cotizacion.razon_social

        descripcion = "Cotizacion %s %s para %s con un valor de %s." % (
            self.cotizacion.nro_cotizacion,
            self.cotizacion.get_estado_display(),
            nombre_cliente,
            self.cotizacion.total
        )
        if nro_tareas:
            descripcion += " (Nro. Tareas: %s)." % (nro_tareas)
        if nro_seguimiento_remisiones:
            descripcion += " (Nro. Remisiones: %s)." % (nro_seguimiento_remisiones)

        return descripcion


class SeguimientoCotizacion(Seguimiento):
    tarea = models.ForeignKey(TareaCotizacion, related_name='seguimientos')


# endregion

# region EnvioTCC
class TareaEnvioTCC(Tarea):
    envio = models.OneToOneField(EnvioTransportadoraTCC, related_name='tarea_diaria_envio_tcc', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    trabajo_diario = models.ForeignKey(TrabajoDiario, on_delete=models.PROTECT, related_name='tareas_envios_tcc',
                                       null=True)

    def get_absolute_url(self):
        return reverse("trabajo_diario:tarea-enviotcc-detalle", kwargs={"pk": self.pk})

    def get_descripcion_tarea(self):
        facturas = ""
        for factura in self.envio.facturas.all():
            nro_factura = "(%s-%s)" % (factura.tipo_documento, factura.nro_documento)
            facturas += nro_factura
        descripcion = "%s con facturas: %s con estado %s. NRO Seguimiento: %s" % (
            self.envio.cliente.nombre, facturas, self.envio.get_estado_display(), self.envio.nro_tracking)
        return descripcion


class SeguimientoEnvioTCC(Seguimiento):
    tarea = models.ForeignKey(TareaEnvioTCC, related_name='seguimientos')


# endregion

# region TareaCartera
class TareaCartera(Tarea):
    factura = models.OneToOneField(FacturasBiable, related_name='tarea_diaria_cartera', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    trabajo_diario = models.ForeignKey(TrabajoDiario, on_delete=models.PROTECT, related_name='tareas_cartera',
                                       null=True)

    def get_absolute_url(self):
        return reverse("trabajo_diario:tarea-cartera-detalle", kwargs={"pk": self.pk})

    def get_descripcion_tarea(self):
        descripcion = "%s tiene la factura %s-%s" % (
            self.factura.cliente, self.factura.tipo_documento, self.factura.nro_documento)
        return descripcion


class SeguimientoCartera(Seguimiento):
    tarea = models.ForeignKey(TareaCartera, related_name='seguimientos')

# endregion
