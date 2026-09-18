# Website Sale Hide Public Prices

Módulo para Odoo 19. Oculta los precios de la ficha y del listado de productos
a visitantes que no han iniciado sesión.

Al pulsar **Agregar al carrito** o **Comprar ahora**, un visitante es enviado a
`/web/signup?redirect=/shop` antes de abrir configuradores o agregar productos.
Después de registrarse o iniciar sesión vuelve a la tienda y puede elegir si
agrega el producto. No se guarda ni se reproduce automáticamente la compra.

La protección también se aplica en el servidor: un visitante no puede crear,
actualizar ni vaciar un carrito mediante solicitudes directas. La página del
carrito y la validación del checkout redirigen al registro, incluso cuando
existe un carrito anterior. Los usuarios de portal e internos mantienen el
comportamiento habitual de Odoo.

## Configuración y actualización

1. En los ajustes del sitio web, habilitar **Cuenta de cliente → Registro
   gratuito** para permitir que nuevos clientes creen su cuenta. Si el sitio
   solo permite altas por invitación, Odoo no habilita `/web/signup` sin token.
2. Actualizar este módulo a `19.0.1.1.0` y reiniciar Odoo para cargar los
   controladores y los nuevos recursos del navegador.
3. Si se instala mediante un submódulo Git, actualizar también la referencia
   del submódulo en el repositorio de Odoo.sh.

## Verificación

- Sin sesión, pulsar Agregar al carrito desde la ficha, el listado y un bloque
  de productos: debe abrir el registro sin crear pedido ni líneas.
- Repetir con Comprar ahora y un producto con variantes u opciones: el registro
  debe abrirse antes del configurador y no deben aparecer precios del carrito.
- Abrir `/shop/cart` y `/shop/checkout` con una sesión pública que conserve un
  carrito anterior: debe redirigir al registro.
- Registrarse o usar el enlace de inicio de sesión: debe volver a `/shop` sin
  agregar el producto automáticamente. Agregarlo después debe funcionar y
  mostrar precios.
- Repetir con una cuenta de portal y una interna; probar también cerrar sesión
  en otra pestaña antes de agregar un producto desde una página ya abierta.

Pruebas de Odoo: ejecutar las pruebas del módulo con
`--test-tags /website_sale_hide_public_price`. Las pruebas de navegador están
en `web.assets_unit_tests` y cubren la redirección y el servicio de carrito.
