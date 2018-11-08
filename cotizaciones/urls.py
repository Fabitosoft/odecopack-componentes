from django.conf.urls import url

from .views import (
    AddItem,
    AddItemOtro,
    AddItemCantidad,
    CotizacionesListView,
    CambiarDiaEntregaView,
    TareaListView,
    RemisionListView,
    CotizacionEmailView,
    DescargarCotizacionView,
    CotizadorView,
    EditarCotizacion,
    CambiarPorcentajeDescuentoView,
    CotizacionView,
    AddImagenCotizacionView,
    EliminarImagenCotizacionView,
    CambiarCantidadVentaPerdidaView
)

urlpatterns = [
    url(
        r'^add/(?P<item_id>[0-9]+)/(?P<precio>[0-9]+)/(?P<forma_pago>[0-9]+)/(?P<cot_id>[0-9]+)/(?P<tipo>[0-9]+)/(?P<tras_tipo>[\w\-]+)$',
        AddItem.as_view(), name='add_item_cotizacion'),
    url(r'^add_qty/$', AddItemCantidad.as_view(), name='add_qty_item_cotizacion'),
    url(r'^cambiar_dias/$', CambiarDiaEntregaView.as_view(), name='cambiar_dias_item_cotizacion'),
    url(r'^cambiar_descuento/$', CambiarPorcentajeDescuentoView.as_view(), name='cambiar_descuento_item_cotizacion'),
    url(r'^cambiar_venta_perdida/$', CambiarCantidadVentaPerdidaView.as_view(),
        name='cambiar_venta_perdida_item_cotizacion'),
    url(r'^detalle/(?P<pk>[0-9]+)$', CotizacionView.as_view(), name='detalle_cotizacion'),
    url(r'^enviar/$', CotizacionEmailView.as_view(), name='enviar'),
    url(r'^descargar/$', DescargarCotizacionView.as_view(), name='descargar_cotizacion'),
    url(r'^list/$', CotizacionesListView.as_view(), name='listar_cotizaciones'),
    url(r'^list/(?P<tipo>[0-3]+)$', CotizacionesListView.as_view(), name='listar_cotizaciones'),
    url(r'^tareas/list/$', TareaListView.as_view(), name='listar_tareas'),
    url(r'^remisiones/list/$', RemisionListView.as_view(), name='listar_remisiones'),
    url(r'^buscar/$', CotizacionesListView.as_view(), name='buscar_cotizacion'),
    url(r'^editar_cotizacion/', EditarCotizacion.as_view(), name='editar_cotizacion'),
    url(r'^add_otro/', AddItemOtro.as_view(), name='add_item_otro_cotizacion'),
    url(r'^add_imagen_cotizacion/', AddImagenCotizacionView.as_view(), name='add_imagen_cotizacion'),
    url(r'^del_imagen_cotizacion/(?P<pk>[0-9]+)$', EliminarImagenCotizacionView.as_view(),
        name='del_imagen_cotizacion'),
    url(r'^cotizador/', CotizadorView.as_view(), name='cotizador'),

]
