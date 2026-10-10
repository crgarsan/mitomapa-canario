# Despliegue automático de MitoMapa

El repositorio contiene la web estática y el Worker existente se llama
`mitomapa-canario`. El flujo de GitHub Actions verifica `SHA256SUMS.txt`, prepara
solo los archivos públicos y los despliega con Wrangler. Mantiene la URL del
Worker de la cuenta configurada.

Cada push a `main` inicia el despliegue. Una persona con acceso a la cuenta de
Cloudflare debe comprobar que el Worker `mitomapa-canario` pertenece a esa cuenta
y crear un token de API limitado a la edición de Workers Scripts.
En **GitHub → Settings → Secrets and variables → Actions**, añade estos secretos:

- `CLOUDFLARE_API_TOKEN`: token de esa cuenta, sin incluirlo en archivos.
- `CLOUDFLARE_ACCOUNT_ID`: identificador de esa cuenta.

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

Para comprobar la preparación local sin credenciales, usa Node.js 22 o superior:

```sh
python3 tools/harden_jspdf_exports.py
python3 tools/update_release.py
python3 tools/harden_jspdf_exports.py --check
python3 tools/prepare_deploy.py
npm ci --ignore-scripts --no-audit --no-fund
python3 -m unittest discover -s tests -p 'test_deploy_policy.py'
python3 -m unittest discover -s tests -p 'test_jspdf_policy.py'
node --test tests/drawing-import.test.js
WRANGLER_SEND_METRICS=false ./node_modules/.bin/wrangler deploy --config wrangler.jsonc --dry-run
```

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
corrección al archivo resultante y compruébalo antes de incorporarlo al repositorio:

```sh
python3 tools/harden_jspdf_exports.py --artifact /ruta/al/recurso.elpx
python3 tools/harden_jspdf_exports.py --artifact /ruta/al/recurso.elpx --check
```

El generador `tools/build_elpx.py` aplica la misma protección. Para cambiar la
versión de jsPDF, verifica los bytes del paquete oficial y la URL exacta,
actualiza la versión, las huellas y el material de prueba, y repite las pruebas.
La biblioteca conserva su licencia MIT; las licencias de los iDevices no cambian.

Ejecuta `tools/update_release.py` antes de subir cambios de los archivos
públicos. Actualiza el ZIP editable y sus huellas. El flujo de GitHub comprueba
esas huellas y se detiene si faltan archivos o no coinciden.

`wrangler.jsonc` apunta a `.deploy/`, generado a partir de las huellas
verificadas. `.deploy/`, `.git/`, la configuración de GitHub y este documento
no se publican como recursos del sitio.
