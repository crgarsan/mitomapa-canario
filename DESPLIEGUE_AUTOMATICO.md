# Despliegue automático de MitoMapa

El repositorio contiene la web estática y el Worker existente se llama
`mitomapa-canario`. El flujo de GitHub Actions verifica `SHA256SUMS.txt`, prepara
solo los archivos públicos y los despliega con Wrangler. Mantiene la URL del
Worker de la cuenta configurada.

Cada push a `main` inicia el flujo. El trabajo de despliegue usa el entorno
`production` y solo se ejecuta para `refs/heads/main` de este repositorio.
La condición del flujo evita ejecuciones accidentales. GitHub debe proteger
los secretos frente a ramas que modifiquen su propio archivo de flujo.

Antes de fusionar un cambio que utilice las credenciales de producción,
configura **GitHub → Settings → Environments → production**:

1. En **Deployment branches and tags**, selecciona **Selected branches and
   tags** y añade una regla de tipo **Branch** con el nombre exacto `main`.
   La lista debe contener esa regla, sin etiquetas ni comodines.
2. Una persona con acceso a Cloudflare debe comprobar que el Worker
   `mitomapa-canario` pertenece a la cuenta prevista y crear un token limitado
   a esa cuenta y a la edición de Workers Scripts. Guarda como
   **Environment secrets** de `production`:
   - `CLOUDFLARE_PRODUCTION_API_TOKEN`: token de esa cuenta.
   - `CLOUDFLARE_PRODUCTION_ACCOUNT_ID`: identificador de esa cuenta.
3. Comprueba que esos dos nombres estén únicamente en los secretos del entorno.
   Si hay copias en repositorio u organización, identifica sus consumidores y
   acuerda su retirada. El nombre exclusivo por sí solo no demuestra el
   aislamiento del secreto.
4. Mientras `main` use los nombres antiguos, crea también como secretos del
   entorno `production` los alias temporales `CLOUDFLARE_API_TOKEN` y
   `CLOUDFLARE_ACCOUNT_ID`, con los mismos valores del token nuevo y de su cuenta.
   Son valores guardados, no referencias a otros secretos. No copies el token
   antiguo de los secretos generales. GitHub da prioridad al secreto del entorno
   sobre el del repositorio cuando tienen el mismo nombre: el `main` actual ya
   solicita `production` y puede resolver allí sus nombres antiguos.
5. Antes de retirar nada, verifica los cuatro nombres en `production`, la regla
   exacta de rama `main` y la ausencia de workflows o despliegues concurrentes
   de `main`. Repite esta comprobación si transcurre tiempo o aparece otro push.
6. Con confirmación expresa de la eliminación, retira únicamente las copias
   `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID` de **Repository secrets**.
   Mantén los alias del entorno: eliminarlos ahora dejaría al `main` actual sin
   sus credenciales. GitHub no permite recuperar el valor de un secreto borrado.
   Una copia general activa permitiría a otro flujo obtener el token sin pasar
   por `production`.
7. Sólo después de integrar la PR #1 y validar su uso de los nombres exclusivos,
   en un paso futuro autorizado, retira los dos alias antiguos del entorno.

Los tokens anteriores de Cloudflare se conservan por decisión de la autoría.
Retirar copias de GitHub no revoca esos tokens ni modifica otras automatizaciones
que los utilicen fuera de este repositorio. Su posible revocación queda fuera
de esta transición y exige revisar sus consumidores y obtener autorización
específica. La precedencia de secretos se documenta en la
[referencia de GitHub](https://docs.github.com/en/actions/reference/security/secrets).

El paso final convierte los nombres exclusivos en las variables
`CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID` que necesita Wrangler.
`tools/deploy_cloudflare.py` exige ambas antes de escribir la configuración
temporal o iniciar la CLI. Si faltan, están vacías o solo contienen espacios,
la publicación falla con un mensaje que no muestra sus valores. Las variables
alternativas de Cloudflare no sustituyen las dos credenciales requeridas.

No copies credenciales a incidencias, comentarios, capturas ni archivos del
repositorio. Añade revisores de despliegue solo si se desea un paso manual.
El flujo conserva el despliegue automático desde `main`. Si se configuran
revisores del entorno, el trabajo espera su aprobación antes de iniciarse.

Para comprobar la protección real, utiliza trabajos sin credenciales que
soliciten el entorno `production` desde una rama distinta de `main` y desde una
etiqueta. GitHub debe rechazarlos por la política del entorno. La omisión de un
trabajo por la condición del flujo no comprueba por sí sola esa protección.
El cierre administrativo incluye verificar ubicación de los secretos, reglas
del entorno, permisos del nuevo token y retirada de las copias generales
accesibles. Las pruebas locales con datos ficticios no comprueban esos ajustes
privados. La comprobación manual aportada por la autoría el 18/11/2026 obtuvo
HTTP 200, `success: true` y estado `active` para el token en Cloudflare, además
de HTTP 200 al consultar el Worker. No demuestra que el valor almacenado en
GitHub sea idéntico ni que se haya autenticado una ejecución de Actions.

La fusión de la PR #1 produce un push a `main` que inicia el flujo y puede
desplegar automáticamente. En un paso posterior que autorice expresamente la
integración y la publicación, comprueba la ejecución de **Deploy MitoMapa to
Cloudflare** en Actions y, en la URL pública, la autoría, las ocho rutas, el
pasaporte, la guía y la descarga del REA. **Run workflow** también puede publicar:
no lo utilices como comprobación de autenticación sin despliegue. Un error de
credenciales aparece como un fallo del despliegue en Actions y puede consultarse
en el paso **Deploy existing Worker**.

Los cambios hechos directamente en el panel de Cloudflare no vuelven a GitHub y
el siguiente despliegue desde `main` puede reemplazarlos. Conserva en el
repositorio los cambios destinados a la web. El seguimiento del alumnado
permanece en su navegador mientras se mantenga el mismo origen; antes de cambiar
de dominio, exporta el seguimiento desde Docente.

Cuando se publique la actualización que separa el seguimiento por sesión,
cierra o recarga todas las pestañas de MitoMapa en los navegadores compartidos
antes de pasar al siguiente grupo. Una pestaña que sigue ejecutando la edición
anterior puede mostrar el trabajo que tenía abierto.

Si hay que volver a una edición anterior a este cambio, exporta primero el
seguimiento vigente desde **Docente → Guardar seguimiento** en los perfiles
que necesiten conservarlo. Tras el cambio de edición, reinicia el progreso de
esa edición e importa la copia que corresponda. Las ediciones anteriores
utilizan otras claves de almacenamiento y requieren esa importación para
recuperar el trabajo guardado con la sesión nueva.

`wrangler.jsonc` conserva la referencia a los dominios personalizados y a
`workers_dev`, pero la publicación automática utiliza una configuración temporal
limitada al Worker, su fecha de compatibilidad y sus activos. Subir y activar una
versión no modifica DNS, rutas, dominios ni `workers_dev`; sus vínculos deben
estar configurados previamente. `tools/check_custom_domain.py` queda como
consulta opcional de la propuesta de cambios, sin aplicarla, y no se invoca
en la publicación automática. El progreso guardado permanece en su origen.

## Mantenimiento de seguridad

Las acciones oficiales se fijan por SHA y mantienen Node 22 para el proyecto,
sin activar la caché automática de paquetes. La validación consulta los avisos
de npm antes de acceder a las credenciales. Mientras el Wrangler fijado incluya
Miniflare 5.20261019.2-beta, un override limitado a esa versión resuelve Undici
7.30.1. Debe revisarse al actualizar Wrangler; no se aplica un retroceso de la
CLI. Pillow 13.0.0 se utiliza únicamente en validación y preparación local.

El encabezado HSTS se limita al host que responde, sin `includeSubDomains` ni
`preload`. La publicación usa `wrangler versions upload` y activa únicamente
la versión identificada por su salida estructurada con `wrangler versions deploy`.
El wrapper conserva `--keep-vars`, la configuración reducida y la validación
del UUID devuelto. Conserva las variables y los secretos existentes; no configura reglas HTTPS ni
cambia DNS o rutas. `tools/check_public_transport.py` se ejecuta antes de publicar
y después de terminar, sin credenciales ni redirecciones automáticas. Exige
301/308 al host HTTPS exacto, conserva ruta y consulta, y comprueba respuestas
HTTPS 200 con HSTS de al menos un año. Si la protección pública falla o no se
puede verificar, el paso falla; el control previo impide iniciar la publicación.
El control posterior detecta una regresión tras la publicación. No se amplían
los permisos del token.

### Visibilidad de la versión recién subida

La subida se realiza una sola vez. Si Wrangler devuelve el error 100146 al
consultar la UUID aprobada antes de activar, el wrapper permite hasta nueve
intentos (el inicial y ocho reintentos) con esa misma UUID al 100 %. Las pausas
son de 2, 4, 8, 16, 30, 30, 30 y 30 segundos, con un plazo compartido de
180 segundos para la fase de activación, incluidos los procesos de Wrangler
y las pausas. Las pausas suman 150 segundos; el coste de las consultas puede
reducir el número de intentos. No se inicia una pausa ni otro proceso si ya no
queda tiempo suficiente. Se registra la UUID, el intento y el presupuesto
restante, sin volcar la salida capturada de la CLI. Sólo acepta un diagnóstico
inequívoco de stderr para la cuenta, el Worker y la UUID exactos; no utiliza
`latest` ni selecciona otra versión. El error de consulta se produce antes del
POST de activación en el Wrangler fijado, 4.152.0. Al actualizar esa dependencia,
revisa también este contrato y las pruebas del wrapper.

La política anterior se agotaba con cinco intentos y sólo 15 segundos de
pausas, aunque su techo nominal fuera de 60 segundos. En la ejecución #219, la
subida tuvo éxito y esos intentos terminaron unos 20 segundos después con
100146; una activación manual posterior de la misma UUID funcionó. La nueva
ventana tolera una consulta que sólo tenga éxito después de 90 segundos,
comprobada con reloj simulado y una CLI local ficticia. No se ha medido un máximo
de propagación del proveedor: si los nueve intentos o los 180 segundos se
agotan, la publicación sigue fallando y requiere comprobar el estado antes de
una nueva acción. Subir una versión no acredita que esté activa.

Otros códigos, rutas, diagnósticos ambiguos y errores del POST no se reintentan.
Un timeout detiene el grupo completo de procesos de la CLI y aborta sin repetir
la operación; si la petición ya llegó al servidor, comprueba el estado de
Cloudflare antes de una nueva acción. Las salidas capturadas no se vuelcan al
registro: pueden incluir anotaciones o datos de la cuenta. Al agotarse el plazo
o los intentos, la publicación conserva su resultado de fallo.

Dependabot incluye npm, Actions y Python. Sus alertas se activan en los ajustes
del repositorio. Antes de fusionar una actualización de infraestructura o
dependencias, ejecutar `python3 tools/update_release.py` para sincronizar el
paquete vigente de fuentes y sus huellas; las comprobaciones rechazan un paquete
desactualizado. Estos cambios administrativos no requieren alterar el contenido
educativo, los ELPX ni sus versiones.

Para comprobar la preparación local sin credenciales, usa Python 3.11 o superior
y Node.js 22 o superior. Conserva primero una copia de los archivos editables y
sincroniza los paquetes vigentes; los verificadores globales son de solo lectura:

```sh
python3 tools/update_release.py
python3 tools/harden_jspdf_exports.py --check
python3 tools/harden_drawing_archives.py --check
python3 tools/prepare_deploy.py
npm ci --ignore-scripts --no-audit --no-fund
python3 -m unittest discover -s tests -p 'test_deploy_policy.py'
python3 -m unittest discover -s tests -p 'test_deploy_cloudflare.py'
python3 -m unittest discover -s tests -p 'test_jspdf_policy.py'
python3 -m unittest discover -s tests -p 'test_maintenance_tools.py'
node --test tests/drawing-import.test.js
WRANGLER_SEND_METRICS=false ./node_modules/.bin/wrangler deploy --config wrangler.jsonc --dry-run
```

Los dos comandos globales `--check` derivan los ZIP y ELPX del inventario
`SHA256SUMS.txt`, comprueban sus huellas y revisan también los paquetes anidados.
No dependen del número de archivos de una edición anterior ni modifican las
descargas históricas. La comprobación de dibujos conserva las guardas de formato,
tamaño y normalización previa a la importación, sin exigir que toda la interfaz
coincida con una migración antigua o que se conserve el historial Git.

Wrangler está fijado a una versión exacta en `package.json`. `package-lock.json`
fija también sus dependencias y sus integridades; `npm ci` falla si ambos archivos
no coinciden. La instalación no ejecuta scripts de los paquetes y el despliegue
usa el ejecutable local. Las acciones de GitHub están fijadas a commits completos.

Para actualizar Wrangler, cambia su versión exacta en `package.json` y ejecuta
`npm install --package-lock-only --ignore-scripts --no-audit --no-fund`. Revisa en
el diff las versiones, los orígenes del registro y las integridades del lockfile;
después repite las comprobaciones anteriores y sube ambos archivos juntos. Para
actualizar una acción, verifica el commit de su versión oficial y sustituye el
SHA completo y el comentario de versión en el flujo.

Los informes PDF nativos de los ELPX cargan jsPDF 4.2.1 con la integridad
registrada en `JSPDF_DEPENDENCY.json` y CORS anónimo. Una respuesta con bytes
distintos se rechaza y conserva la alternativa PNG del editor. La generación de
PDF mantiene su requisito de conexión; el cambio no añade envío de respuestas.
Las pruebas de archivos de Actions comprueban esta política antes de publicar.

Al guardar o exportar de nuevo con eXeLearning, el editor puede sustituir los
archivos de sus iDevices por los de su instalación. Vuelve a aplicar la
corrección **a una copia nueva del archivo resultante** y compruébala antes de
incorporarla al repositorio. El modo `--artifact` es la operación explícita de
edición; no se debe utilizar para reescribir las ediciones históricas publicadas:

```sh
python3 tools/harden_jspdf_exports.py --artifact /ruta/al/recurso.elpx
python3 tools/harden_jspdf_exports.py --artifact /ruta/al/recurso.elpx --check
```

`tools/build_elpx.py` y las funciones de migración conservadas en
`tools/harden_drawing_archives.py` corresponden al mantenimiento histórico;
no reconstruyen la distribución nativa actual. Para sincronizar la edición
vigente, usa `tools/sync_current_elpx.py` y su opción `--check` según el README.
Para cambiar la
versión de jsPDF, verifica los bytes del paquete oficial y la URL exacta,
actualiza la versión, las huellas y el material de prueba, y repite las pruebas.
La biblioteca conserva su licencia MIT; las licencias de los iDevices no cambian.

Ejecuta `tools/update_release.py` antes de subir cambios de los archivos
públicos. Actualiza el ZIP editable y sus huellas. El flujo de GitHub comprueba
esas huellas y se detiene si faltan archivos o no coinciden.

`wrangler.jsonc` apunta a `.deploy/`, generado a partir de las huellas
verificadas. `.deploy/`, `.git/`, la configuración de GitHub y los manifiestos de npm no se
sirven como archivos sueltos. El inventario puede incluir documentación de
reutilización y código público: nunca deben contener credenciales.

## Seguridad de la cuenta y mantenimiento

Activa la autenticación en dos pasos de Cloudflare en **Perfil → Autenticación**.
Necesita la intervención de la persona titular y su dispositivo. Guarda los
códigos de recuperación en un lugar seguro. Esta protección del inicio de
sesión no cambia la web ni sustituye el token limitado de GitHub Actions.

El aviso «No Turnstile enabled» es una sugerencia de configuración de cuenta.
La web actual es estática, no tiene una API propia de recepción de formularios
y guarda las actividades localmente. Añadir solo el componente Turnstile, sin
validación de su resultado en un servidor, no protegería esos datos. Si se
incorpora una recepción de envíos en el futuro, habrá que revisar esa función
y su protección en el servidor antes de decidir si corresponde usarlo.

`.github/dependabot.yml` propone mensualmente actualizaciones de npm y de las
acciones. Crea pull requests para revisión; no activa su fusión automática.
Las alertas de Dependabot son un ajuste adicional de GitHub: en **Settings →
Advanced Security** (o **Code security**, según la interfaz), comprueba que estén
activadas. Añadir el archivo de configuración no demuestra que esas alertas se
hayan habilitado. Las credenciales de la integración de edición pueden permitir
cambiar código sin permitir administrar esas opciones o los secretos.

Usa el `package-lock.json` de la edición vigente para preparar despliegues.
Las fuentes históricas se mantienen para reproducibilidad y pueden contener
versiones antiguas de herramientas; no son la configuración de mantenimiento
recomendada. Las dependencias de Wrangler no se sirven al navegador del alumnado.

La instalación de las pruebas utiliza Python 3.12, `pip --require-hashes
--only-binary=:all:` y el cierre completo de dependencias de
`requirements-browser-tests.txt`. `actions/setup-python` también está fijada
por commit. Las nuevas pruebas de transporte, bloqueo, ZIP y WAV se ejecutan
antes del acceso a los secretos de producción.
