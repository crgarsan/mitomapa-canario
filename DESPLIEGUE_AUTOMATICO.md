# Despliegue automático de MitoMapa

El repositorio contiene la web estática y el Worker existente se llama
`mitomapa-canario`. El flujo de GitHub Actions verifica `SHA256SUMS.txt`, prepara
solo los archivos públicos y los despliega con Wrangler. Mantiene la URL del
Worker de la cuenta configurada.

Cada push a `main` inicia el flujo. El trabajo de despliegue usa el entorno
`production` y solo se ejecuta para `refs/heads/main` de este repositorio.
La condición del flujo evita ejecuciones accidentales, pero una rama puede
modificar su propio YAML: la protección de los secretos debe aplicarla GitHub.

Antes de habilitar las credenciales, configura **GitHub → Settings →
Environments → production**:

1. En **Deployment branches and tags**, selecciona **Selected branches and
   tags** y añade una regla de tipo **Branch** con el nombre exacto `main`.
   No añadas reglas de etiquetas ni patrones como `*`. Seleccionar el modo sin
   añadir la regla todavía permite todas las ramas y etiquetas.
2. Si el plan de GitHub lo permite, configura **Required reviewers** con las
   personas responsables de producción, **Prevent self-review** y sin bypass
   de administradores. En repositorios privados, esta aprobación puede requerir
   GitHub Enterprise; si no está disponible, usa una protección equivalente
   para `main` con revisión obligatoria por las personas responsables de
   producción antes de entregar el token al flujo.
3. Una persona con acceso a Cloudflare debe comprobar que el Worker
   `mitomapa-canario` pertenece a la cuenta prevista y crear un token limitado
   a esa cuenta y a la edición de Workers Scripts. Guarda únicamente como
   **Environment secrets** de `production`:
   - `CLOUDFLARE_PRODUCTION_API_TOKEN`: token de esa cuenta.
   - `CLOUDFLARE_PRODUCTION_ACCOUNT_ID`: identificador de esa cuenta.
   No guardes estos nombres como secretos de repositorio u organización.
4. Si antes existían `CLOUDFLARE_API_TOKEN` o `CLOUDFLARE_ACCOUNT_ID` como
   secretos de repositorio u organización, retira su acceso a este repositorio
   y revoca el token antiguo en Cloudflare. GitHub no permite recuperar el
   valor de un secreto guardado: vuelve a introducir las credenciales o crea
   un token nuevo desde la cuenta de Cloudflare. Dejar el token antiguo
   accesible permite que una rama con un flujo modificado eluda el entorno.

Los nuevos nombres evitan que el flujo use por accidente los secretos globales
anteriores. Si falta cualquiera de las credenciales, **Deploy existing Worker**
falla antes de iniciar Wrangler. El flujo usa la instalación local de Wrangler
fijada en el paso anterior y no inicia un login interactivo.

Después de configurar el entorno, comprueba **Deploy MitoMapa to Cloudflare**
en Actions. **Run workflow** solo debe usarse seleccionando `main`. Si hay
revisores del entorno, el trabajo espera su aprobación antes de iniciarse.
Comprueba en la URL pública la autoría, las ocho rutas, el pasaporte, la guía y
la descarga del REA.

Para verificar la protección en GitHub, usa un flujo de prueba sin credenciales
que solicite `environment: production` desde una rama distinta de `main` y desde
una etiqueta: GitHub debe rechazar ambos trabajos por la política del entorno.
Comprueba también que un trabajo en `main` espera a los revisores configurados.
El flujo normal omite las ramas distintas de `main`; ese resultado, por sí solo,
no demuestra que el entorno impida el acceso a un YAML modificado.

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

Para probar el rechazo de credenciales ausentes y la propagación de errores sin
acceder a Cloudflare:

```sh
python3 -m unittest discover -s tests -v
```

Ejecuta `tools/update_release.py` antes de subir cambios de los archivos
públicos. Actualiza el ZIP editable y sus huellas. El flujo de GitHub comprueba
esas huellas y se detiene si faltan archivos o no coinciden.

`wrangler.jsonc` apunta a `.deploy/`, generado a partir de las huellas
verificadas. `.deploy/`, `.git/`, la configuración de GitHub y este documento
no se publican como recursos del sitio.
