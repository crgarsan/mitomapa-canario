# Despliegue automático de MitoMapa

El repositorio contiene la web estática y el Worker existente se llama
`mitomapa-canario`. El flujo de GitHub Actions verifica `SHA256SUMS.txt`, prepara
solo los archivos públicos y los despliega con Wrangler. Mantiene la URL del
Worker de la cuenta configurada.

Cada push a `main` inicia el despliegue. Una persona con acceso a la cuenta de
Cloudflare debe comprobar que el Worker `mitomapa-canario` pertenece a esa cuenta
y crear un token de API limitado a la edición de Workers Scripts.
En **GitHub → Settings → Environments → production → Environment secrets**,
añade estos secretos:

- `CLOUDFLARE_API_TOKEN`: token de esa cuenta, sin incluirlo en archivos.
- `CLOUDFLARE_ACCOUNT_ID`: identificador de esa cuenta.

El entorno `production` debe permitir despliegues únicamente desde `main`.
El flujo ya separa las comprobaciones sin secretos del trabajo de despliegue;
solo el paso final necesita el token. Los secretos se deben guardar en ese
entorno, para que otros flujos o ramas no puedan obtenerlos como secretos
generales del repositorio. La declaración `environment: production` por sí sola
no demuestra que se haya hecho esa migración.

Si existen copias en **Settings → Secrets and variables → Actions**, crea
primero los secretos de entorno y comprueba un despliegue desde `main`.
Después elimina las copias generales. GitHub no permite recuperar el valor de
un secreto guardado: si no se conserva el token, crea uno nuevo limitado a la
cuenta y a los permisos necesarios para Workers Scripts. Comprueba el nombre
del Worker destino en `wrangler.jsonc` y revoca el token anterior tras validar
el despliegue.
No copies credenciales a incidencias, comentarios, capturas ni archivos del
repositorio. Añade revisores de despliegue solo si se desea un paso manual: no
son necesarios para el flujo automático actual.

Después de configurar los secretos, comprueba la ejecución de **Deploy MitoMapa
to Cloudflare** en Actions. También puedes iniciarla manualmente con **Run
workflow**. Comprueba en la URL pública la autoría, las ocho rutas, el pasaporte,
la guía y la descarga del REA. Un error de credenciales aparece como un fallo del
despliegue en Actions y puede consultarse en el paso **Deploy existing Worker**.

Los cambios hechos directamente en el panel de Cloudflare no vuelven a GitHub y
el siguiente despliegue desde `main` puede reemplazarlos. Conserva en el
repositorio los cambios destinados a la web. El seguimiento del alumnado
permanece en su navegador mientras se mantenga el mismo origen; antes de cambiar
de dominio, exporta el seguimiento desde Docente.

El dominio personalizado `mitomapacanario.org` se declara en `wrangler.jsonc`.
`workers_dev: true` conserva el acceso anterior y los enlaces ya distribuidos.
Antes de publicar, `tools/check_custom_domain.py` consulta la propuesta de
cambios de Cloudflare y detiene el despliegue si falta acceso o si se eliminaría
otro dominio, se modificaría la vinculación de otro dominio o se reemplazaría
un registro DNS. Se permite actualizar la vinculación del dominio solicitado.
El dominio debe estar activo en la cuenta de Cloudflare del
despliegue. Esta primera vinculación no redirige automáticamente el progreso
guardado en la dirección anterior.

## Mantenimiento de seguridad

Las acciones oficiales se fijan por SHA y mantienen Node 22 para el proyecto,
sin activar la caché automática de paquetes. La validación consulta los avisos
de npm antes de acceder a las credenciales. Mientras el Wrangler fijado incluya
Miniflare 5.20261019.2-beta, un override limitado a esa versión resuelve Undici
7.30.1. Debe revisarse al actualizar Wrangler; no se aplica un retroceso de la
CLI. Pillow 13.0.0 se utiliza únicamente en validación y preparación local.

El encabezado HSTS se limita al host que responde, sin `includeSubDomains` ni
`preload`. Después del despliegue, `tools/ensure_https_redirect.py` intenta
configurar una regla de borde para las solicitudes HTTP de
`mitomapacanario.org`, conservando ruta, consulta y reglas ajenas. No añade
código Worker ni cambia las cuotas del alojamiento estático. La API necesita
Zone Read y Single Redirect Edit. Si faltan permisos, cuota o una respuesta
verificable, genera una advertencia y mantiene la web publicada; en ese caso
la redirección queda pendiente de configuración por el titular y de comprobación
pública. El script no sigue redirecciones autenticadas ni imprime credenciales.

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
