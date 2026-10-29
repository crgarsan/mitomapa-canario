# MitoMapa canario · Objeto de Aprendizaje 4.8.8

29/10/2026 · Renderizado de metadatos en componentes nativos.

Se revisan las bibliotecas incluidas de informe de progreso y listas de cotejo.
Los nombres, mensajes y atributos se codifican al entrar en HTML; los ítems y
pies que admiten formato usan una lista de HTML pasivo saneada con una instancia
privada de DOMPurify 3.4.17. Se conservan negritas, énfasis, enlaces y el estado
original. Las direcciones de imágenes procedentes de enlaces ocultos también se
validan antes de utilizarlas en estilos.
Se incluyen los mensajes del contador y del estado vacío del informe, aunque
el contador no esté presente en la página de progreso actual.

La transformación parte de dos fuentes fijadas por hash. El constructor permite
solo sus cambios reproducibles y una licencia de dependencia; mantiene la
protección del resto de bibliotecas, actividades y medios. La licencia de
DOMPurify se distribuye en `libs/mitomapa-native-runtime-LICENSE.txt`, bajo su
opción Apache-2.0. Los materiales propios mantienen CC BY-SA 4.0.

Se conservan 34 páginas, 118 identidades de iDevice, 42 juegos nativos, 16 MP3,
cuentos, escenas, mapas e imágenes de piezas. Se actualizan la identificación
de la edición y su trazabilidad. La web sigue siendo un extra enlazado.

Alcance: se cierra la interpretación de metadatos como código en esos dos
renderizadores incluidos. La previsualización de autor de eXe 4.0.5 permite
contenido ejecutable del proyecto; este parche no hace seguro abrir cualquier
ELPX hostil ni modifica un editor o LMS externo. Si el editor sustituye las
bibliotecas al guardar/exportar, debe validarse otra vez el resultado.
Las copias históricas se conservan sin modificar.

Las pruebas reproducen los campos del informe en una previsualización aislada
con los atributos de sandbox documentados, sin datos reales ni red externa;
incluyen texto, atributos, URLs, protocolos codificados y HTML SVG/MathML. Se
comprueban además formato legítimo, almacenamiento y los controles nativos.
Las comprobaciones técnicas no acreditan eficacia educativa ni conformidad WCAG
global. Los hallazgos de diseño de la auditoría anterior tienen seguimiento
independiente.
