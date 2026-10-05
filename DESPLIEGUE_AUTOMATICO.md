# Despliegue automático de MitoMapa

El repositorio contiene la web estática y el Worker existente se llama
`mitomapa-canario`. El flujo de GitHub Actions verifica `SHA256SUMS.txt`, prepara
solo los archivos públicos y los despliega con Wrangler. Mantiene la URL del
Worker de la cuenta configurada.

El flujo está desactivado inicialmente. Para activarlo, una persona con acceso a
la cuenta de Cloudflare debe comprobar que el Worker `mitomapa-canario` pertenece
a esa cuenta y crear un token de API limitado a la edición de Workers Scripts.
En **GitHub → Settings → Secrets and variables → Actions**, añade estos secretos:

- `CLOUDFLARE_API_TOKEN`: token de esa cuenta, sin incluirlo en archivos.
- `CLOUDFLARE_ACCOUNT_ID`: identificador de esa cuenta.

Después, añade la variable de repositorio
`MITOMAPA_CLOUDFLARE_AUTODEPLOY_20261005` con valor `enabled` y ejecuta
manualmente **Deploy MitoMapa to Cloudflare** una vez desde
Actions. Comprueba en la URL pública la versión, las ocho rutas, el pasaporte,
la guía y la descarga del REA. Desde entonces, cada push a `main` iniciará el
mismo flujo automáticamente. Si la variable falta o tiene otro valor, el trabajo
de despliegue se omite.

Los cambios hechos directamente en el panel de Cloudflare no vuelven a GitHub y
el siguiente despliegue desde `main` puede reemplazarlos. Conserva en el
repositorio los cambios destinados a la web. El seguimiento del alumnado
permanece en su navegador mientras se mantenga el mismo origen; antes de cambiar
de dominio, exporta el seguimiento desde Docente.

Para comprobar la preparación local sin credenciales:

```sh
python3 tools/update_release.py
python3 tools/prepare_deploy.py
npx wrangler@4.147.0 deploy --config wrangler.jsonc --dry-run
```

Ejecuta `tools/update_release.py` antes de subir cambios de los archivos
públicos. Actualiza el ZIP editable y sus huellas. El flujo de GitHub comprueba
esas huellas y se detiene si faltan archivos o no coinciden.

`wrangler.jsonc` apunta a `.deploy/`, generado a partir de las huellas
verificadas. `.deploy/`, `.git/`, la configuración de GitHub y este documento
no se publican como recursos del sitio.
