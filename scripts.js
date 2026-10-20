/* MitoMapa canario · la versión de distribución procede de VERSION.json. */
const RESOURCE_VERSION=typeof window.MitoMapaVersion?.version==="string"?window.MitoMapaVersion.version:"sin identificar";
const EXPORT_SCHEMA_VERSION=1;
const ASSETS=Object.freeze({"mapa_canarias.webp":"assets/images/mapa_canarias.webp","pintadera_dentada.webp":"assets/images/pintadera_dentada.webp","pintadera_rombos.webp":"assets/images/pintadera_rombos.webp","pintadera_roseta.webp":"assets/images/pintadera_roseta.webp","pintadera_sol.webp":"assets/images/pintadera_sol.webp","pintadera_triangulo.webp":"assets/images/pintadera_triangulo.webp","scene_el-hierro.webp":"assets/images/scene_el-hierro.webp","scene_fuerteventura.webp":"assets/images/scene_fuerteventura.webp","scene_gran-canaria.webp":"assets/images/scene_gran-canaria.webp","scene_la-gomera.webp":"assets/images/scene_la-gomera.webp","scene_la-graciosa.webp":"assets/images/scene_la-graciosa.webp","scene_la-palma.webp":"assets/images/scene_la-palma.webp","scene_lanzarote.webp":"assets/images/scene_lanzarote.webp","scene_tenerife.webp":"assets/images/scene_tenerife.webp","pintadera_seis_triangulos.webp":"assets/images/pintadera_seis_triangulos.webp","pintadera_chevron.webp":"assets/images/pintadera_chevron.webp","pintadera_circulos.webp":"assets/images/pintadera_circulos.webp","pintadera_doble_triangulo.webp":"assets/images/pintadera_doble_triangulo.webp","pintadera_espiral_cuadrada.webp":"assets/images/pintadera_espiral_cuadrada.webp"});
function resolveAssetPaths(markup){return markup.replace(/content\/resources\/([A-Za-z0-9_.-]+\.webp)/g,(match,name)=>ASSETS[name]||match);}
const routes=[{"id":"tenerife","island":"Tenerife","title":"Dácil y el regreso de Magec","image":"scene_tenerife.webp","imageAlt":"Una joven y otras tres personas miran hacia la luz del cielo junto al Teide. Ilustración ficticia del cuento de Dácil y Magec; no es una reconstrucción histórica.","badge":"pintadera_sol.webp","badgeName":"Pintadera de la luz","quick":[{"q":"¿Quién había escondido a Magec dentro de Echeyde?","options":["Dácil","Guayota","Achamán","El rebaño"],"answer":1,"hit":"Guayota había encerrado a Magec, el Sol, según el mito.","error":"Recuerda quién vivía en las entrañas del volcán."},{"q":"¿A quién pidió ayuda la comunidad?","options":["A Acorán","A Abora","A Achamán","A Orahan"],"answer":2,"hit":"La comunidad pidió ayuda a Achamán, señor del cielo.","error":"Busca el nombre del ser que devolvió la luz."},{"q":"¿Cómo supo Dácil que Magec había regresado?","options":["Oyó una campana","Vio una línea dorada sobre Echeyde","Encontró una vasija","Llegó una embarcación"],"answer":1,"hit":"La línea dorada iluminó primero la cumbre y después las laderas.","error":"Fíjate en la última escena del cuento."}],"questions":[{"q":"Guayota ayudó a Magec a iluminar la isla.","answer":false,"feedback":"Guayota había atrapado a Magec y lo mantenía escondido en el volcán; quien lo libera es Achamán.","hint":"Busca quién provoca la oscuridad y quién devuelve la luz."},{"q":"Achamán cerró la entrada del volcán con una gran roca.","answer":true,"feedback":"Después de liberar a Magec, Achamán cierra la entrada con una enorme roca para impedir que Guayota escape.","hint":"Relee lo que hace Achamán después de vencer a Guayota."},{"q":"Dácil cuidaba cabras cerca de Echeyde.","answer":true,"feedback":"Al comienzo del cuento, Dácil cuida cabras cerca de Echeyde y espera el primer rayo del Sol.","hint":"Busca el lugar y la tarea de Dácil al inicio."}]},{"id":"gran-canaria","island":"Gran Canaria","title":"Guayarmina y el tibicena del barranco","image":"scene_gran-canaria.webp","imageAlt":"Una joven se agacha en un sendero de barranco mientras otras tres personas observan a su espalda. Ilustración ficticia del cuento de Guayarmina; no es una reconstrucción histórica.","badge":"pintadera_seis_triangulos.webp","badgeName":"Pintadera de la memoria","quick":[{"q":"¿Dónde apareció el tibicena?","options":["En el mar","Entre las tabaibas del barranco","Dentro del tagoror","Sobre una embarcación"],"answer":1,"hit":"La figura apareció entre las tabaibas, cerca del campamento.","error":"Recuerda el paisaje donde Guayarmina cuidaba las cabras."},{"q":"¿Qué hicieron Guayarmina y los demás pastores?","options":["Corrieron cada uno por su lado","Persiguieron a la criatura","Permanecieron juntos y levantaron las teas","Apagaron el fuego"],"answer":2,"hit":"Se protegieron permaneciendo juntos y con luz.","error":"El estribillo ofrece una pista."},{"q":"¿Qué encontraron al amanecer?","options":["Una corona","Huellas grandes mezcladas con las de las cabras","Una carta","La tea convertida en piedra"],"answer":1,"hit":"Las huellas quedaron mezcladas con las marcas del rebaño.","error":"Piensa en la pista que dejó la criatura."}],"questions":[{"q":"Guayarmina navegaba por el mar con un rebaño.","answer":false,"feedback":"Guayarmina guía un rebaño por un sendero de barranco de Gran Canaria; no navega por el mar.","hint":"Vuelve al primer párrafo y localiza el paisaje."},{"q":"Los pastores persiguieron solos al tibicena durante la noche.","answer":false,"feedback":"Los pastores permanecen juntos con el rebaño y levantan las teas; nadie se adentra solo en el barranco.","hint":"Observa qué hacen los pastores cuando Guayarmina los llama."},{"q":"Al amanecer encontraron huellas mezcladas con las de las cabras.","answer":true,"feedback":"Cuando la criatura desaparece al aclararse el cielo, quedan huellas grandes mezcladas con marcas de cabras.","hint":"Relee qué queda en el suelo al amanecer."}]},{"id":"la-palma","island":"La Palma","title":"Acerina y el roque que sostenía el cielo","image":"scene_la-palma.webp","imageAlt":"Una persona adulta y una niña contemplan un roque alto entre montañas y nubes. Ilustración ficticia del cuento de Acerina y el roque Idafe; no reproduce con exactitud el lugar.","badge":"pintadera_dentada.webp","badgeName":"Pintadera de Idafe","quick":[{"q":"¿Qué parecía sostener el roque de Idafe?","options":["El mar","El cielo","Una cueva","El poblado"],"answer":1,"hit":"Idafe parecía sostener el cielo sobre la Caldera.","error":"La respuesta aparece al comienzo del cuento."},{"q":"¿Por qué se alejó el grupo de la ladera?","options":["Comenzó a nevar","Llegó un barco","La tierra vibró y cayeron piedras","Se perdió una cabra"],"answer":2,"hit":"El grupo se puso a salvo cuando la tierra vibró.","error":"Recuerda qué hizo el abuelo al escuchar el ruido."},{"q":"¿Qué hizo Acerina cuando fue mayor?","options":["Olvidó la ceremonia","Se convirtió en narradora","Abandonó Benahoare","Derribó el roque"],"answer":1,"hit":"Acerina contó la historia para conservar la memoria del lugar.","error":"Busca cómo cumplió Acerina su promesa."}],"questions":[{"q":"Acerina vivía en Benahoare.","answer":true,"feedback":"El relato sitúa a Acerina en Benahoare, nombre con el que presenta a la isla de La Palma.","hint":"Relee la primera oración del cuento."},{"q":"Acerina conservó la historia convirtiéndose en narradora.","answer":true,"feedback":"Acerina se convierte en narradora y cuenta a los niños lo vivido para conservar la memoria de Idafe.","hint":"Busca qué hace Acerina cuando pasan los años."},{"q":"El grupo permaneció junto al risco mientras caían piedras.","answer":false,"feedback":"El abuelo toma a Acerina de la mano y el grupo se aleja del risco mientras bajan las piedras.","hint":"Busca cómo reaccionan al temblor y a la caída de piedras."}]},{"id":"la-gomera","island":"La Gomera","title":"Gara y Jonay, dos voces en la cumbre","image":"scene_la-gomera.webp","imageAlt":"Una joven con las manos abiertas se dirige a dos grupos situados a ambos lados de un barranco. Ilustración ficticia del cuento de Gara y Jonay; no es una reconstrucción histórica.","badge":"pintadera_triangulo.webp","badgeName":"Pintadera del encuentro","quick":[{"q":"¿Cómo llegó Jonay desde Tenerife?","options":["En una gran nave","Sobre odres de piel de cabra","Por un puente","Volando"],"answer":1,"hit":"La leyenda cuenta que cruzó el mar sobre odres de piel de cabra.","error":"Recuerda cómo se lanzó Jonay al agua."},{"q":"¿Por qué se oponían las familias?","options":["Temían la advertencia que unía el agua y el fuego","No conocían el camino","Habían perdido el rebaño","Querían viajar a otra isla"],"answer":0,"hit":"Las familias interpretaban el agua de Gara y el fuego de Jonay como un peligro.","error":"Vuelve a la advertencia del manantial."},{"q":"¿Qué enseñanza conserva el cuento?","options":["Que no debe escucharse a nadie","Que la enemistad y la falta de diálogo causan dolor","Que el mar siempre separa","Que las leyendas no cambian"],"answer":1,"hit":"El relato invita a dialogar antes de cerrar el camino a otras personas.","error":"Piensa en lo que comprendieron las comunidades."}],"questions":[{"q":"Jonay llegó a La Gomera desde Lanzarote.","answer":false,"feedback":"Jonay parte de Tenerife y cruza el mar sobre odres de piel de cabra para llegar a La Gomera.","hint":"Localiza la isla donde vive Jonay antes de cruzar el mar."},{"q":"La leyenda invita a reflexionar sobre la falta de diálogo.","answer":true,"feedback":"El final relaciona el dolor con la enemistad y la falta de escucha, e invita a abrir el diálogo.","hint":"Relee la reflexión de las comunidades al final."},{"q":"Las familias apoyaron la relación desde el primer momento.","answer":false,"feedback":"Las familias temen la advertencia y se oponen a que el agua de Gara y el fuego de Jonay se encuentren.","hint":"Busca la reacción de las familias antes de la huida."}]},{"id":"el-hierro","island":"El Hierro","title":"Agarfa y las gotas del Garoé","image":"scene_el-hierro.webp","imageAlt":"Una niña y dos personas adultas recogen agua bajo un árbol entre la niebla, usando recipientes de aspecto flexible. Ilustración ficticia del cuento de Agarfa y el Garoé; no es una reconstrucción histórica.","badge":"pintadera_circulos.webp","badgeName":"Pintadera de la niebla","quick":[{"q":"¿Cómo proporcionaba agua el Garoé?","options":["Convertía la niebla en gotas","Derretía la nieve","Sacaba agua del mar","Abría un pozo"],"answer":0,"hit":"La niebla se condensaba en sus ramas y caía a las piletas.","error":"El estribillo habla de ramas y gotas."},{"q":"¿Por qué ocultaron el sendero?","options":["Para jugar","Para proteger la fuente de agua","Porque estaba nevando","Para encontrar otro árbol"],"answer":1,"hit":"La comunidad temía perder la fuente que permitía vivir en la isla.","error":"Recuerda qué apareció en el horizonte."},{"q":"¿Qué ocurrió después de que una tormenta derribara el árbol?","options":["Su historia desapareció","La comunidad olvidó el agua","Su memoria continuó en los relatos","El mar cubrió la isla"],"answer":2,"hit":"Las familias continuaron narrando la historia del Garoé.","error":"El final explica qué no pudo derribar la tormenta."}],"questions":[{"q":"El Garoé recogía agua de la niebla.","answer":true,"feedback":"La niebla se enreda en las ramas del Garoé y forma gotas que se recogen en piletas de piedra.","hint":"Relee cómo llega el agua a las piletas."},{"q":"La comunidad desperdiciaba el agua de las piletas.","answer":false,"feedback":"Agarfa llena las vasijas despacio para no desperdiciar agua; la comunidad depende de ella.","hint":"Busca con qué cuidado Agarfa llena las vasijas."},{"q":"La memoria del árbol continuó después de la tormenta.","answer":true,"feedback":"Aunque una tormenta derriba el árbol, las familias siguen contando cómo recogía agua de la niebla.","hint":"Observa qué permanece después de la caída del árbol."}]},{"id":"fuerteventura","island":"Fuerteventura","title":"La luz de Mafasca en el camino","image":"scene_fuerteventura.webp","imageAlt":"Una mujer y una niña observan una pequeña luz en un paisaje pedregoso al anochecer. Ilustración ficticia del cuento de la Luz de Mafasca; no es una reconstrucción histórica.","badge":"pintadera_doble_triangulo.webp","badgeName":"Pintadera de Mafasca","quick":[{"q":"¿Qué utilizaron los pastores para encender la hoguera?","options":["Un trozo de una vieja cruz","Una vela del barco","Hojas del Garoé","Una pintadera"],"answer":0,"hit":"Arrancaron un trozo de madera de una cruz del camino.","error":"Busca el objeto al que no mostraron respeto."},{"q":"¿Cómo se comportaba la luz?","options":["Se quedó dentro del fuego","Los siguió y se detenía cuando ellos se detenían","Cayó al mar","Se convirtió en una cabra"],"answer":1,"hit":"La luz avanzaba o se detenía con los pastores.","error":"Recuerda por qué no consiguieron dejarla atrás."},{"q":"¿Cómo repararon su falta?","options":["Ocultaron lo ocurrido","Repararon la cruz y contaron la historia","Persiguieron la luz","Abandonaron el rebaño"],"answer":1,"hit":"Cumplieron su promesa y advirtieron a otros pastores.","error":"Piensa en lo que hicieron al amanecer."}],"questions":[{"q":"Guise y Ayose eran pastores.","answer":true,"feedback":"En esta recreación, Guise y Ayose son dos pastores que regresan con sus cabras; no representan a los dirigentes históricos.","hint":"Relee el comienzo y distingue los personajes del cuento de sus homónimos históricos."},{"q":"La luz desapareció en cuanto empezaron a caminar.","answer":false,"feedback":"La luz sigue a los pastores cuando caminan y se detiene cuando ellos se detienen; desaparece tras su promesa.","hint":"Compara qué hace la luz mientras caminan y cuándo desaparece."},{"q":"Los pastores decidieron dejar la cruz rota.","answer":false,"feedback":"Los pastores prometen reparar la cruz y cumplen su promesa al día siguiente.","hint":"Busca la promesa de Guise y Ayose y qué hacen al amanecer."}]},{"id":"lanzarote","island":"Lanzarote","title":"Ico y la prueba del humo","image":"scene_lanzarote.webp","imageAlt":"Una joven habla ante un grupo sentado en un paisaje volcánico, acompañada por una mujer mayor. Ilustración ficticia del cuento de Ico; no es una reconstrucción histórica.","badge":"pintadera_chevron.webp","badgeName":"Pintadera de Ico","quick":[{"q":"¿Por qué desconfiaban algunas personas de Ico?","options":["Porque no sabía caminar","Porque su piel era más clara","Porque perdió una vasija","Porque llegó en barco"],"answer":1,"hit":"El consejo convirtió una diferencia física en una sospecha injusta.","error":"La razón aparece en el primer párrafo."},{"q":"¿Qué le entregó la anciana?","options":["Una esponja mojada","Una tea","Una piedra","Una carta"],"answer":0,"hit":"La esponja húmeda ayudó a Ico a respirar durante la prueba.","error":"Recuerda el objeto que Ico colocó sobre su boca."},{"q":"¿Por qué cuestionó Ico la prueba?","options":["Era demasiado corta","Ponía a una persona en peligro para demostrar quién era","No había público","Se celebró de noche"],"answer":1,"hit":"Ico comprendió que ninguna prueba injusta debía decidir la pertenencia.","error":"Piensa en la pregunta que dejó al consejo sin respuesta."}],"questions":[{"q":"Ico consideró justa la decisión del consejo.","answer":false,"feedback":"Ico agradece la ayuda, pero cuestiona que alguien deba ponerse en peligro para demostrar quién es.","hint":"Relee la pregunta que Ico dirige al consejo."},{"q":"Una anciana ayudó a Ico antes de la prueba.","answer":true,"feedback":"Antes de la prueba, una anciana entrega a Ico una esponja mojada y le explica cómo usarla.","hint":"Busca quién ayuda a Ico y qué le entrega."},{"q":"La solidaridad ayudó a Ico a sobrevivir.","answer":true,"feedback":"La ayuda de la anciana y la inteligencia de Ico permiten que salga del recinto; el cuento destaca esa solidaridad.","hint":"Relaciona la ayuda recibida con el desenlace."}]},{"id":"la-graciosa","island":"La Graciosa","title":"Guadarfía y la isla de San Borondón","image":"scene_la-graciosa.webp","imageAlt":"Dos personas observan desde la costa una silueta de isla entre la bruma; una se protege los ojos con la mano. Ilustración ficticia de San Borondón, no de la época indígena.","badge":"pintadera_espiral_cuadrada.webp","badgeName":"Pintadera del horizonte","quick":[{"q":"¿Qué trabajo realizaba Guadarfía?","options":["Era pastor","Era grumete","Era agricultor","Era alfarero"],"answer":1,"hit":"Guadarfía era un joven grumete en una embarcación de vela.","error":"La respuesta aparece en la primera oración."},{"q":"¿Qué ocurrió al acercarse a la isla?","options":["La isla parecía alejarse y llegó la niebla","Encontraron un puerto","El mar se secó","La montaña habló"],"answer":0,"hit":"La isla se alejaba y una niebla espesa ocultó el horizonte.","error":"Recuerda por qué tuvieron que bajar las velas."},{"q":"¿Cómo llegó San Borondón a algunos mapas?","options":["Los navegantes contaron visiones y dibujaron lo recordado","La fotografiaron","La trasladaron","La vieron desde un avión"],"answer":0,"hit":"Los relatos y dibujos de navegantes llevaron la isla a algunas cartas.","error":"Piensa en lo que hicieron Guadarfía y el capitán."}],"questions":[{"q":"El capitán marcó el lugar en su carta.","answer":true,"feedback":"Tras retirarse la bruma, el capitán marca el lugar del avistamiento en su carta y Guadarfía dibuja la forma que recuerda.","hint":"Busca qué hace cada personaje al amanecer."},{"q":"La isla desapareció cuando se retiró la bruma.","answer":true,"feedback":"Cuando la bruma se marcha al amanecer, delante del barco solo queda el mar y ya no se ve la isla.","hint":"Relee el paisaje que encuentran después de la niebla."},{"q":"Guadarfía era el capitán de la embarcación.","answer":false,"feedback":"Guadarfía es grumete; el capitán es otro personaje de la tripulación.","hint":"Relee cómo se presenta a Guadarfía al principio."}]}];
const secondaryCreations=Object.freeze({"tenerife":{"route":1,"title":"Carta de Dácil a Achamán","prompt":"Ponte en la piel de Dácil y escríbele a Achamán una carta en agradecimiento por la liberación de Magec.","structure":["Lugar y fecha.","Saludo a Achamán.","Cuerpo: agradecimiento, recuerdo de lo ocurrido y explicación de lo que significa el regreso de Magec.","Despedida y firma de Dácil."],"criteria":["La carta está escrita en primera persona desde el punto de vista de Dácil.","Agradece a Achamán la liberación de Magec y mantiene la coherencia con el cuento.","Incluye lugar y fecha, saludo, cuerpo, despedida y firma.","Expresa emociones y argumentos con claridad y revisa la ortografía."],"placeholder":"Tenerife, …\n\nAchamán:\n\nTe escribo para…\n\n…\n\nDácil","lengthLabel":"Extensión orientativa: de 120 a 250 palabras.","minWords":20,"maxWords":0},"gran-canaria":{"route":2,"title":"Noticia desde el barranco","prompt":"Redacta una noticia sobre el acontecimiento narrado en el cuento «Guayarmina y el tibicena del barranco».","structure":["Título informativo.","Subtítulo, si ayuda a completar la información.","Entradilla: responde qué sucedió, quién participó, cuándo y dónde ocurrió, cómo sucedió y por qué.","Cuerpo: amplía los datos en orden de importancia."],"criteria":["La noticia mantiene un tono objetivo y un lenguaje claro.","Incluye título, entradilla y cuerpo; el subtítulo es opcional.","La entradilla responde qué, quién, cuándo, dónde, cómo y por qué.","Diferencia la información del cuento de cualquier detalle añadido para completar la noticia."],"placeholder":"TÍTULO\nSubtítulo opcional\n\nENTRADILLA\n¿Qué sucedió? ¿Quién? ¿Cuándo? ¿Dónde? ¿Cómo? ¿Por qué?\n\nCUERPO\n…","lengthLabel":"Extensión orientativa: de 180 a 350 palabras.","minWords":20,"maxWords":0},"la-palma":{"route":3,"title":"Un cuento para la voz de Acerina","prompt":"Acerina se convirtió en una gran narradora. Crea un cuento sobre el roque de Idafe para que Acerina se lo cuente a los niños y niñas de La Palma.","structure":["Título.","Inicio: presenta el roque, el lugar y los personajes.","Nudo: plantea un conflicto relacionado con la memoria o el cuidado de Idafe.","Desenlace: resuelve el conflicto y deja una enseñanza respetuosa con el patrimonio."],"criteria":["El cuento se sitúa en torno al roque de Idafe y conserva su relación con la memoria palmera.","Presenta un inicio, un nudo y un desenlace comprensibles.","El lenguaje resulta adecuado para un público infantil.","La creación propia no se presenta como un hecho histórico comprobado."],"placeholder":"TÍTULO\n\nINICIO\nCuentan que, cerca del roque de Idafe…\n\nNUDO\n…\n\nDESENLACE\n…","lengthLabel":"Extensión orientativa: de 250 a 500 palabras.","minWords":20,"maxWords":0},"la-gomera":{"route":4,"title":"Gara y Jonay suben a escena","prompt":"Crea el guion de una escena teatral inspirada en el mito de Gara y Jonay.","choices":["El encuentro y flechazo de los protagonistas.","La prohibición de la relación por parte de sus familiares.","Una conversación entre habitantes de La Gomera tras conocer el trágico desenlace."],"structure":["Título de la escena y lugar en el que ocurre.","Lista breve de personajes.","Acotaciones para indicar movimientos, gestos, tono o ambiente.","Diálogos con el nombre de cada personaje delante de su intervención."],"criteria":["El guion desarrolla una de las tres escenas propuestas.","Incluye personajes, acotaciones y diálogos claramente diferenciados.","Mantiene la coherencia con el mito y trata el desenlace con sensibilidad.","Propone una puesta en escena realizable y revisa la expresión escrita."],"placeholder":"TÍTULO DE LA ESCENA\nLugar: …\nPersonajes: …\n\n(Indicación de ambiente o movimiento)\nGARA: …\nJONAY: …","lengthLabel":"Extensión orientativa: de 180 a 350 palabras.","minWords":20,"maxWords":0},"el-hierro":{"route":5,"title":"Reportaje: cada gota cuenta","prompt":"Redacta un reportaje sobre la importancia del agua en Canarias.","structure":["Título y entradilla que presenten el tema y despierten interés.","Cuerpo organizado con subtítulos: disponibilidad del agua, usos, problemas y soluciones.","Una referencia al Garoé como elemento histórico y patrimonial de El Hierro.","Conclusión y relación de al menos dos fuentes consultadas."],"criteria":["El reportaje explica por qué el agua es esencial en Canarias y aporta información contrastada.","Incluye título, entradilla, subtítulos, desarrollo, conclusión y fuentes.","Relaciona el Garoé con el tema sin convertir la leyenda en una prueba científica.","Distingue datos, explicaciones y opiniones y utiliza un lenguaje divulgativo claro."],"placeholder":"TÍTULO\n\nENTRADILLA\n…\n\nDISPONIBILIDAD Y USOS\n…\n\nPROBLEMAS Y SOLUCIONES\n…\n\nEL GAROÉ\n…\n\nCONCLUSIÓN Y FUENTES\n…","lengthLabel":"Extensión orientativa: de 300 a 600 palabras.","minWords":20,"maxWords":0},"fuerteventura":{"route":6,"title":"Otro final responsable","prompt":"La ruta 6 conserva la propuesta anterior. Amplía el final alternativo para explicar cómo Guise y Ayose reparan el daño, asumen su responsabilidad y ayudan a otras personas.","structure":["Escribe entre 150 y 200 palabras.","Mantén a Guise y Ayose como protagonistas y sitúa la acción después del encuentro con Mafasca.","Incluye una acción concreta de reparación y una consecuencia para la comunidad.","Cierra con una enseñanza que se desprenda de los hechos, sin convertirla en un sermón."],"criteria":["El final es coherente con el cuento y no contradice los acontecimientos principales.","Los protagonistas reconocen el daño y realizan una acción concreta para repararlo.","La consecuencia y la enseñanza se integran de forma natural en la narración.","El texto tiene entre 150 y 200 palabras y está revisado."],"placeholder":"Al amanecer, Guise y Ayose…","lengthLabel":"Extensión requerida: entre 150 y 200 palabras.","minWords":150,"maxWords":200},"lanzarote":{"route":7,"title":"El diario de Ico","prompt":"Vuelve a leer el cuento y redacta una entrada del diario personal de Ico en la que cuente lo que le pasó, pensó y sintió durante la injusta experiencia vivida.","structure":["Fecha.","Título breve.","Cuerpo: hechos, pensamientos y sentimientos narrados en primera persona.","Cierre o despedida."],"criteria":["La entrada está escrita en primera persona desde el punto de vista de Ico.","Incluye fecha, título, cuerpo y cierre o despedida.","Integra lo que ocurrió, lo que Ico pensó y lo que sintió.","Mantiene la coherencia con el cuento y expresa una reflexión sobre la injusticia."],"placeholder":"FECHA\nTÍTULO BREVE\n\nHoy…\n\nCIERRE O DESPEDIDA\nIco","lengthLabel":"Extensión orientativa: de 180 a 350 palabras.","minWords":20,"maxWords":0},"la-graciosa":{"route":8,"title":"San Borondón en viñetas","prompt":"Convierte el cuento «Guadarfía y la isla de San Borondón» en un cómic.","structure":["Planifica entre seis y diez viñetas con inicio, desarrollo y desenlace.","Combina imágenes, cartelas de narración, bocadillos de diálogo y, si hace falta, onomatopeyas.","Incluye la aparición de la isla entre la bruma y la duda sobre lo observado.","Añade título, autoría y una nota que indique que se inspira en una leyenda."],"criteria":["La secuencia de viñetas permite comprender el cuento sin explicaciones externas.","Los textos son breves, legibles y están bien asociados a cada personaje o acción.","El cómic mantiene la incertidumbre propia de San Borondón y no la presenta como un hecho comprobado.","Incluye título, autoría y referencia a la leyenda que inspira la adaptación."],"placeholder":"TÍTULO Y AUTORÍA\n\nVIÑETA 1 · Imagen: … · Cartela: … · Diálogo: …\nVIÑETA 2 · Imagen: … · Cartela: … · Diálogo: …\n…\n\nNota: cómic inspirado en la leyenda de San Borondón.","lengthLabel":"Planifica entre seis y diez viñetas.","minWords":20,"maxWords":0}});
const workshopActivities=Object.freeze({"tenerife":{"words":{"title":"Vocabulario del mundo guanche","intro":"Relaciona los nombres y localiza en el cuento cuatro términos con significado parecido.","match":{"prompt":"Relaciona cada explicación con su nombre.","options":["Magec","Achamán","Guayota","Echeyde"],"items":[{"definition":"Divinidad solar que representa al Sol en el relato.","answer":"Magec"},{"definition":"Ser supremo celeste al que la comunidad pide ayuda.","answer":"Achamán"},{"definition":"Ser maligno que mantiene a Magec dentro del volcán.","answer":"Guayota"},{"definition":"Nombre con el que la tradición guanche identifica el Teide.","answer":"Echeyde"}]},"fillPrompt":"Busca en el cuento el sinónimo de cada verbo.","fills":[{"prompt":"habitaban","answers":["vivían","vivian"],"hint":"Aparece en la primera oración."},{"prompt":"iniciar","answers":["comenzar"],"hint":"Dácil esperaba la luz para hacerlo con el camino."},{"prompt":"narra","answers":["cuenta"],"hint":"La tradición lo hace en el quinto párrafo."},{"prompt":"finalizar","answers":["terminar"],"hint":"Aparece cerca del final."}]},"research":{"title":"Echeyde en una fuente oficial","intro":"Consulta la página del Parque Nacional del Teide y localiza dos datos que no aparecen en el cuento.","questions":[{"q":"Según la fuente, ¿qué significado se atribuye al nombre Echeyde?","options":["Montaña de la niebla.","Morada de Guayota, el Maligno.","Camino de Magec."],"answer":1,"feedback":"La página del parque atribuye a Echeyde el significado de «morada de Guayota, el Maligno»."},{"q":"¿Qué elemento de la cima identifica esa fuente con el tapón colocado por Achamán?","options":["Los Roques de García.","La Fortaleza.","El Pan de Azúcar."],"answer":2,"feedback":"La fuente identifica el Pan de Azúcar, último cono de la cima, con ese tapón legendario."}],"sources":[{"label":"Gobierno de Canarias: historia del Parque Nacional del Teide","url":"https://www.gobiernodecanarias.org/parquesnacionales/teide/el_parque/historia/"},{"label":"CanariWiki: antiguos canarios","url":"https://www3.gobiernodecanarias.org/medusa/wiki/index.php?title=Antiguos_canarios"}]},"creation":{"type":"text","title":"Un título nuevo","prompt":"Inventa otro título para el cuento. Intenta que mencione el conflicto o la luz.","placeholder":"Mi título para el cuento…","tip":"Ejemplo de inicio: «Dácil y…». El título debe ser tuyo."}},"gran-canaria":{"words":{"title":"Vocabulario: antónimos y canarismos","intro":"Busca antónimos en el cuento y relaciona dos voces del español de Canarias.","match":{"prompt":"Relaciona cada canarismo con una explicación breve.","options":["tabaiba","tea"],"items":[{"definition":"Arbusto que abunda en terrenos secos o volcánicos de Canarias y contiene un jugo lechoso.","answer":"tabaiba"},{"definition":"Madera resinosa y resistente que se obtiene de pinos canarios añosos.","answer":"tea"}]},"fillPrompt":"Escribe el antónimo que aparece en el cuento.","fills":[{"prompt":"grande","answers":["pequeño","pequeno"],"hint":"Está en el estribillo."},{"prompt":"apagó","answers":["encendió","encendio"],"hint":"Guayarmina lo hizo con una tea."},{"prompt":"oscuridad","answers":["luz"],"hint":"Protegió al grupo durante la noche."},{"prompt":"día","answers":["noche"],"hint":"Es el momento en el que aparece la criatura."}]},"research":{"title":"Rastrea una voz histórica","intro":"Consulta el diccionario histórico enlazado y localiza información que el cuento no proporciona.","questions":[{"q":"Además del perro lanudo, ¿qué otras formas recogen los testimonios del diccionario?","options":["Aves y un becerro.","Caballos marinos y delfines.","Lagartos y peces."],"answer":0,"feedback":"Los testimonios incluyen formas de ave —como pava o gallina con pollos— y también de becerro."},{"q":"Según los testimonios recogidos, ¿cuándo podían aparecer las tibicenas?","options":["Solo al mediodía.","Únicamente durante los eclipses.","De día y de noche."],"answer":2,"feedback":"Los testimonios históricos recopilados señalan apariciones tanto de día como de noche."}],"sources":[{"label":"RAE: Diccionario histórico del español de Canarias, tibicena","url":"https://www.rae.es/tdhle/tibicena"},{"label":"Academia Canaria de la Lengua: tabaiba","url":"https://www.academiacanarialengua.org/palabra/tabaiba/"},{"label":"Academia Canaria de la Lengua: tea","url":"https://www.academiacanarialengua.org/palabra/tea/"}]},"creation":{"type":"drawing","title":"Dibuja al tibicena","prompt":"Dibuja la criatura según el cuento: grande, cubierta de pelo negro y con ojos que parecen dos brasas.","placeholder":"Si prefieres no dibujar, describe aquí cómo imaginas al tibicena…","tip":"Puedes dibujar con el dedo o con el ratón, deshacer, borrar y guardar la imagen en tu dispositivo."}},"la-palma":{"words":{"title":"Vocabulario de Benahoare","intro":"Relaciona lugares, seres y objetos del relato.","match":{"prompt":"Relaciona cada término con su significado en el cuento.","options":["Benahoare","Idafe","Abora","vasija"],"items":[{"definition":"Nombre indígena de la isla que hoy llamamos La Palma.","answer":"Benahoare"},{"definition":"Gran roque de la Caldera que parecía sostener el cielo.","answer":"Idafe"},{"definition":"Nombre de una divinidad mencionada en la tradición palmera.","answer":"Abora"},{"definition":"Recipiente en el que el grupo llevaba alimentos.","answer":"vasija"}]},"fillPrompt":"Completa con la expresión del cuento que tiene un significado parecido.","fills":[{"prompt":"permanece erguido","answers":["sigue en pie","continuaba erguido"],"hint":"La primera opción aparece en el estribillo."},{"prompt":"conservar el recuerdo","answers":["guardar la memoria","conservar la memoria"],"hint":"Aparece en el estribillo y al final."}]},"research":{"title":"Investiga el paisaje de Aceró","intro":"Consulta la información arqueológica del parque y busca datos que no se cuentan en el relato.","questions":[{"q":"¿Cómo llamaban los benahoaritas al territorio de la Caldera de Taburiente?","options":["Erbania.","Aceró.","Echeyde."],"answer":1,"feedback":"La página del parque indica que la Caldera se encontraba en el territorio llamado Aceró."},{"q":"¿Qué restos arqueológicos enumera la página del parque?","options":["Cerámicas, petroglifos y útiles de piedra.","Pergaminos y libros encuadernados.","Monedas romanas y objetos de vidrio."],"answer":0,"feedback":"La fuente menciona cerámicas, petroglifos y útiles de piedra como huellas arqueológicas."}],"sources":[{"label":"Gobierno de Canarias: arqueología de la Caldera de Taburiente","url":"https://www.gobiernodecanarias.org/parquesnacionales/caldera_de_taburiente/el_parque/valores_naturales/"}]},"creation":{"type":"text","title":"Una voz para la memoria","prompt":"Escribe un estribillo nuevo, de una o dos oraciones, para recordar a Idafe.","placeholder":"Idafe…","tip":"Puedes repetir un término para darle ritmo."}},"la-gomera":{"words":{"title":"Vocabulario entre agua y cumbre","intro":"Relaciona cuatro términos que ayudan a comprender el viaje y el paisaje.","match":{"prompt":"Relaciona cada término con su explicación.","options":["manantial","odres","cumbre","eco"],"items":[{"definition":"Lugar del que brota agua de forma natural.","answer":"manantial"},{"definition":"Recipientes de piel que, según la leyenda, ayudaron a Jonay a cruzar el mar.","answer":"odres"},{"definition":"Zona más alta de una montaña.","answer":"cumbre"},{"definition":"Repetición de un sonido al rebotar en un lugar.","answer":"eco"}]},"fillPrompt":"Escribe un término con significado opuesto.","fills":[{"prompt":"enemistad","answers":["amistad"],"hint":"Piensa en una relación de afecto y apoyo."},{"prompt":"callar","answers":["hablar","decir"],"hint":"El cuento invita a escuchar y dialogar."}]},"research":{"title":"Investiga la arqueología gomera","intro":"Consulta la página de arqueología de la Reserva de la Biosfera y localiza información nueva.","questions":[{"q":"Según la fuente, ¿qué actividad sostuvo principalmente la economía de la antigua población gomera?","options":["La navegación de altura.","La minería de metales.","La ganadería."],"answer":2,"feedback":"La fuente describe una economía eminentemente ganadera, acompañada por agricultura y recolección."},{"q":"¿Qué enclave menciona la fuente por la presencia de aras de sacrificio?","options":["El Roque Nublo.","La Fortaleza de Chipude.","La Cueva de los Verdes."],"answer":1,"feedback":"La Fortaleza de Chipude aparece entre los yacimientos destacados por la presencia de aras de sacrificio."}],"sources":[{"label":"Reserva de la Biosfera de La Gomera: arqueología","url":"https://biosfera.lagomera.es/arqueologia/"},{"label":"Juan Francisco Navarro: investigaciones arqueológicas en La Gomera","url":"https://iehcan.com/wp-content/uploads/2016/12/1-Navarro-2016.pdf"}]},"creation":{"type":"text","title":"Una oración que abre el diálogo","prompt":"Escribe una oración que Gara o Jonay podrían decir a sus familias para pedir que se escuchen.","placeholder":"Necesitamos que…","tip":"Usa un tono respetuoso y una propuesta concreta."}},"el-hierro":{"words":{"title":"Vocabulario del agua","intro":"Relaciona los términos que explican cómo el Garoé ayudaba a la comunidad.","match":{"prompt":"Relaciona cada término con su explicación.","options":["Garoé","piletas","niebla","vasija"],"items":[{"definition":"Árbol relacionado con la captación de agua en El Hierro.","answer":"Garoé"},{"definition":"Huecos o depósitos de piedra en los que caían las gotas.","answer":"piletas"},{"definition":"Nube muy baja formada por pequeñas gotas de agua.","answer":"niebla"},{"definition":"Recipiente usado para transportar el agua.","answer":"vasija"}]},"fillPrompt":"Escribe el antónimo que aparece o se deduce del cuento.","fills":[{"prompt":"aparecieron","answers":["desaparecieron","desapareció","desaparecio"],"hint":"La historia del árbol no lo hizo."},{"prompt":"ocultar","answers":["mostrar","revelar","descubrir"],"hint":"Es lo contrario de guardar un secreto."}]},"research":{"title":"El Garoé histórico","intro":"Consulta la fuente oficial de El Hierro para descubrir dos datos que el cuento no incluye.","questions":[{"q":"¿A qué especie pertenecía el Garoé histórico según la fuente?","options":["A un til.","A un pino.","A una palmera."],"answer":0,"feedback":"La información oficial identifica el Garoé histórico como un til."},{"q":"¿En qué año se plantó el ejemplar que sustituyó al árbol histórico?","options":["En 1496.","En 1949.","En 2009."],"answer":1,"feedback":"El ejemplar actual se plantó en 1949, varios siglos después de la caída del árbol histórico."}],"sources":[{"label":"Portal oficial de turismo de El Hierro: Árbol Garoé","url":"https://elhierro.travel/museos-y-visitas-de-interes/el-hierro/arbol-garoe/"}]},"creation":{"type":"text","title":"Un lema para cuidar el agua","prompt":"Crea un lema breve que anime a no desperdiciar el agua.","placeholder":"Gota a gota…","tip":"Un buen lema es corto, claro y fácil de recordar."}},"fuerteventura":{"words":{"title":"Vocabulario del camino","intro":"Relaciona objetos del relato y encuentra antónimos.","match":{"prompt":"Relaciona cada término con su significado.","options":["hoguera","chispa","gofio","sendero"],"items":[{"definition":"Fuego encendido al aire libre.","answer":"hoguera"},{"definition":"Partícula encendida que salta del fuego.","answer":"chispa"},{"definition":"Alimento canario hecho con cereal tostado y molido.","answer":"gofio"},{"definition":"Camino estrecho por el que avanzan los pastores.","answer":"sendero"}]},"fillPrompt":"Escribe el antónimo que aparece en el cuento.","fills":[{"prompt":"apareció","answers":["desapareció","desaparecio"],"hint":"La claridad lo hizo al final de la noche."},{"prompt":"noche","answers":["día","dia","amanecer"],"hint":"Los pastores volvieron después."},{"prompt":"vieja","answers":["nueva","nuevo"],"hint":"Es su opuesto habitual."}]},"research":{"title":"Tradición y evidencia arqueológica","intro":"Consulta la declaración del Barranco del Cavadero e investiga una huella preeuropea que no aparece en el cuento.","questions":[{"q":"¿Sobre qué soporte se encuentran grabadas las inscripciones del Barranco del Cavadero?","options":["Sobre hojas de pergamino.","Sobre tablas de madera.","Sobre bloques basálticos de las paredes del barranco."],"answer":2,"feedback":"Las inscripciones se realizaron sobre bloques basálticos situados en las paredes del barranco."},{"q":"¿Qué dos tipos de grabados alfabetiformes señala el BOC en este yacimiento?","options":["Líbico-bereberes y pseudolatinos.","Jeroglíficos egipcios y latinos.","Griegos y fenicios."],"answer":0,"feedback":"El documento distingue caracteres líbico-bereberes y caracteres pseudolatinos."}],"sources":[{"label":"Museo Arqueológico de Fuerteventura","url":"https://museosfuerteventura.com/museos/museo-arqueologico-de-fuerteventura/"},{"label":"Gobierno de Canarias: Zona Arqueológica del Barranco del Cavadero","url":"https://www.gobiernodecanarias.org/boc/2008/078/003.html"}]},"creation":{"type":"text","title":"Otro final responsable","prompt":"Escribe dos o tres oraciones con otro final en el que los pastores reparen el daño y ayuden a otras personas.","placeholder":"Al amanecer, Guise y Ayose…","tip":"Incluye una acción de reparación y una enseñanza."}},"lanzarote":{"words":{"title":"Vocabulario para hablar de justicia","intro":"Relaciona cuatro términos importantes para comprender el conflicto de Ico.","match":{"prompt":"Relaciona cada término con su explicación.","options":["consejo","linaje","esponja","solidaridad"],"items":[{"definition":"Grupo de personas que toma una decisión en el relato.","answer":"consejo"},{"definition":"Conjunto de antepasados y descendientes de una familia.","answer":"linaje"},{"definition":"Objeto mojado que ayuda a Ico a respirar.","answer":"esponja"},{"definition":"Apoyo que una persona ofrece a otra cuando lo necesita.","answer":"solidaridad"}]},"fillPrompt":"Escribe un término de significado opuesto.","fills":[{"prompt":"entrar","answers":["salir"],"hint":"Ico lo hizo caminando al abrirse la puerta."},{"prompt":"húmeda","answers":["seca","seco"],"hint":"Describe algo que no tiene agua."}]},"research":{"title":"Sigue una interpretación histórica","intro":"Consulta el estudio enlazado y averigua cómo se ha interpretado la ayuda que recibió Ico.","questions":[{"q":"¿Qué apellido identifica al investigador que interpretó el consejo de la anciana como una práctica ya probada?","options":["Espinosa.","Álvarez Delgado.","Torriani."],"answer":1,"feedback":"El estudio atribuye esa interpretación a Álvarez Delgado."},{"q":"¿Con qué actividad relacionó ese investigador el procedimiento empleado?","options":["Con la caza de pardelas.","Con la elaboración de cerámica.","Con la navegación a vela."],"answer":0,"feedback":"Álvarez Delgado relacionó el procedimiento con una práctica conocida por quienes cazaban pardelas."}],"sources":[{"label":"Memoria Digital de Lanzarote: La aventura de Avendaño y la leyenda de Ico","url":"https://bk.memoriadelanzarote.com/media/docs/items/20110708111921AVENDAO-E-ICO.pdf"}]},"creation":{"type":"text","title":"Responder a Ico","prompt":"Responde a la pregunta de Ico: ¿por qué nadie debería ponerse en peligro para demostrar quién es?","placeholder":"Nadie debería ponerse en peligro porque…","tip":"Explica tu idea con respeto y una razón."}},"la-graciosa":{"words":{"title":"Vocabulario de navegación","intro":"Relaciona cuatro términos del viaje y localiza antónimos.","match":{"prompt":"Relaciona cada término con su explicación.","options":["grumete","pergamino","bruma","carta náutica"],"items":[{"definition":"Joven que aprende y trabaja en una embarcación.","answer":"grumete"},{"definition":"Material sobre el que se dibujaban algunos mapas antiguos.","answer":"pergamino"},{"definition":"Niebla ligera que dificulta ver el horizonte.","answer":"bruma"},{"definition":"Mapa utilizado para orientar la navegación.","answer":"carta náutica"}]},"fillPrompt":"Escribe el antónimo que aparece en el cuento.","fills":[{"prompt":"apareció","answers":["desapareció","desaparecio"],"hint":"La isla lo hacía según la leyenda."},{"prompt":"cerca","answers":["lejos","lejos de"],"hint":"Cuanto más avanzaban, así parecía estar la isla."}]},"research":{"title":"Busca el origen de San Borondón","intro":"Consulta el estudio académico y descubre dos datos sobre el origen y la difusión del mito.","questions":[{"q":"¿Qué figura está en el origen del mito geográfico según el estudio?","options":["Un navegante romano llamado Taro.","Un cartógrafo de La Graciosa.","El monje irlandés san Brandán."],"answer":2,"feedback":"El estudio sitúa el origen del mito en la tradición del monje irlandés san Brandán."},{"q":"¿Entre qué siglos contribuyeron especialmente los relatos de viajeros a consolidarlo?","options":["Entre los siglos XVI y XIX.","Entre los siglos IX y XII.","Entre los siglos XX y XXI."],"answer":0,"feedback":"El análisis destaca especialmente los relatos de viajeros producidos entre los siglos XVI y XIX."}],"sources":[{"label":"Universidad Complutense de Madrid: revisión del mito geográfico de San Borondón","url":"https://revistas.ucm.es/index.php/RFRM/article/download/45706/42966/73431"},{"label":"CanariWiki: isla de La Graciosa","url":"https://www3.gobiernodecanarias.org/medusa/wiki/index.php/Isla_de_La_Graciosa"}]},"creation":{"type":"text","title":"La nota del cartógrafo","prompt":"Escribe la nota breve que Guadarfía podría colocar junto a su dibujo de la isla que creyó ver.","placeholder":"Tras la bruma vimos…","tip":"Describe lo que recuerda sin afirmar que sea un hecho comprobado."}}});
const routeMarkup=["<section class=\"route\" id=\"route-tenerife\" aria-labelledby=\"title-tenerife\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Tenerife</p><h2 id=\"title-tenerife\">Dácil y el regreso de Magec</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_tenerife.webp\" alt=\"Una joven y otras tres personas miran hacia la luz del cielo junto al Teide. Ilustración ficticia del cuento de Dácil y Magec; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · Tenerife</p><p class=\"story-intro\">Cuento ambientado en el mundo guanche e inspirado en Echeyde, Guayota, Magec y Achamán.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Achamán, devuelve a Magec y trae de nuevo la luz»</div><p>Cuando los guanches vivían entre barrancos y cañadas, Dácil cuidaba cabras cerca de Echeyde. Cada amanecer esperaba el primer rayo de Magec, el Sol, para comenzar el camino.</p><p>Pero una mañana la luz no llegó. Una nube negra cubría la montaña y la tierra temblaba bajo los pies. Las personas mayores recordaron el relato de Guayota, el ser que vivía dentro del volcán. Según la tradición, había atrapado a Magec y lo mantenía escondido en la oscuridad.</p><p>El frío entró en las cuevas. Dácil reunió a los niños junto al fuego y todos repitieron: «Achamán, devuelve a Magec y trae de nuevo la luz».</p><p>Desde la cumbre llegó un ruido profundo. Las nubes se tiñeron de rojo y una gran piedra rodó hasta la boca de Echeyde. Dácil abrazó a su hermano pequeño mientras el poblado pedía ayuda a Achamán, señor del cielo.</p><p>La tradición cuenta que Achamán descendió desde lo alto, venció a Guayota y liberó a Magec. Después cerró la entrada del volcán con una enorme roca para que el ser de fuego no escapara.</p><p>Entonces una línea dorada apareció detrás de Echeyde. Primero iluminó la cumbre, después las laderas y, por último, el rostro de Dácil. Las cabras salieron de su refugio y el frío comenzó a marcharse.</p><p>Desde aquel día, Dácil contó la historia cada vez que el volcán parecía despertar. Y al terminar, todas las voces repetían: «Achamán, devuelve a Magec y trae de nuevo la luz».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>La relación entre Echeyde y Guayota aparece en fuentes históricas como Espinosa (1594), que deben leerse críticamente por haber sido escritas después de la conquista. La captura y liberación de Magec se ha difundido mediante recreaciones posteriores. Dácil es un antropónimo guanche difundido por la tradición literaria. En este cuento no representa al personaje de Antonio de Viana; sus acciones y los diálogos son una creación original.</p><section class=\"source-traceability\" data-source-route=\"tenerife\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> La liberación de Magec por Achamán frente a Guayota se cuenta en una versión divulgativa actual vinculada al Teide.</p><p><strong>Fuente identificada:</strong></p><ul><li>Gobierno de Canarias (s. f.). <a href=\"https://www.gobiernodecanarias.org/parquesnacionales/teide/el_parque/historia/\" target=\"_blank\" rel=\"noopener noreferrer\">Historia del Parque Nacional del Teide</a>. Apartado «La leyenda de Guayota y el Pan de Azúcar».</li></ul><p>La página presenta esa versión; no demuestra que todos sus episodios se narraran antes de la conquista. Las noticias antiguas sobre Echeyde y Guayota y las versiones posteriores requieren distinguirse.</p><p><strong>Nuestra adaptación:</strong> Dácil es un personaje literario de este cuento, no la Dácil del poema de Viana. El cuidado del rebaño, su hermano, los diálogos y el estribillo son creación del recurso.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-tenerife\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"tenerife\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-tenerife\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"tenerife\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_sol.webp\" alt=\"Pintadera de la luz\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de la luz</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-gran-canaria\" aria-labelledby=\"title-gran-canaria\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Gran Canaria</p><h2 id=\"title-gran-canaria\">Guayarmina y el tibicena del barranco</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_gran-canaria.webp\" alt=\"Una joven se agacha en un sendero de barranco mientras otras tres personas observan a su espalda. Ilustración ficticia del cuento de Guayarmina; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · Gran Canaria</p><p class=\"story-intro\">Cuento ambientado en la antigua Gran Canaria e inspirado en Acorán y los tibicenas.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Juntos y con luz, el miedo se hace pequeño»</div><p>En la antigua Gran Canaria, Guayarmina guiaba un pequeño rebaño por un sendero de barranco. Al ponerse el sol, reunió las cabras junto a una cueva y encendió una tea.</p><p>De pronto oyó un gruñido. Entre las tabaibas apareció una figura cubierta de pelo negro. Tenía forma de perro grande y sus ojos parecían dos brasas. Guayarmina recordó los relatos sobre los tibicenas, seres que caminaban por cuevas y lugares solitarios.</p><p>El miedo quiso empujarla a correr, pero ella llamó a los demás pastores. Juntos levantaron las teas y dijeron: «Juntos y con luz, el miedo se hace pequeño».</p><p>El tibicena dio una vuelta alrededor del fuego. Después dio otra. En la tercera se detuvo frente a Guayarmina. Ella pidió protección a Acorán y permaneció junto al rebaño.</p><p>Cuando el cielo comenzó a aclararse, la criatura retrocedió hasta desaparecer entre las rocas. En el suelo quedaron unas huellas grandes mezcladas con marcas de cabras.</p><p>Guayarmina contó lo ocurrido en el poblado. Las personas mayores no pudieron asegurar qué había visto, pero agradecieron que nadie se hubiera adentrado solo en el barranco.</p><p>Desde entonces, cuando la noche sorprendía a los pastores, reunían el rebaño, encendían una luz y recordaban: «Juntos y con luz, el miedo se hace pequeño».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>Acorán figura en testimonios históricos sobre Gran Canaria. Los tibicenas pertenecen al ámbito de las creencias y presentan descripciones diferentes, entre ellas la de un gran perro oscuro. Guayarmina fue un nombre de la tradición indígena de Gran Canaria. En este cuento no representa a la figura histórica; el campamento y las tres vueltas de la criatura son una recreación literaria original.</p><section class=\"source-traceability\" data-source-route=\"gran-canaria\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> Las tibicenas aparecen descritas con diversas formas de animales. La imagen de un gran perro procede de testimonios escritos posteriores a la conquista.</p><p><strong>Fuente identificada:</strong></p><ul><li>Corrales Zumbado, C., y Corbella Díaz, D. (2013). <a href=\"https://www.rae.es/tdhle/tibicena\" target=\"_blank\" rel=\"noopener noreferrer\">Diccionario histórico del español de Canarias: tibicena</a>. Entrada «tibicena»: Gómez Escudero, edición 1978, p. 439; Marín de Cubas, edición 1993, libro II, cap. 18, p. 204.</li></ul><p>Las palabras religiosas de los cronistas reflejan también su perspectiva cristiana; las fuentes no prueban que una criatura existiera. El cuento elige una de las formas transmitidas.</p><p><strong>Nuestra adaptación:</strong> Guayarmina no representa a la figura histórica de ese nombre. El rebaño, las tres vueltas, las huellas, su petición a Acorán y la respuesta de los pastores son escenas inventadas.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-gran-canaria\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"gran-canaria\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-gran-canaria\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"gran-canaria\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_seis_triangulos.webp\" alt=\"Pintadera de la memoria\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de la memoria</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-la-palma\" aria-labelledby=\"title-la-palma\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Palma</p><h2 id=\"title-la-palma\">Acerina y el roque que sostenía el cielo</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-palma.webp\" alt=\"Una persona adulta y una niña contemplan un roque alto entre montañas y nubes. Ilustración ficticia del cuento de Acerina y el roque Idafe; no reproduce con exactitud el lugar.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · La Palma</p><p class=\"story-intro\">Cuento ambientado en Benahoare e inspirado en Abora y el roque de Idafe.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Idafe sigue en pie; nosotros guardamos su memoria»</div><p>En Benahoare, la isla que hoy llamamos La Palma, Acerina levantaba la cabeza cada vez que entraba en la Caldera. Allí estaba Idafe, un gran roque que parecía sostener el cielo.</p><p>Una mañana acompañó a su abuelo y a otras personas del poblado. Llevaban pequeñas vasijas con alimentos para una ceremonia antigua. El abuelo explicó que aquel lugar estaba unido a Abora y a la memoria de sus antepasados.</p><p>Al llegar, todos pronunciaron: «Idafe sigue en pie; nosotros guardamos su memoria».</p><p>De pronto, la tierra vibró. Varias piedras bajaron por la ladera y Acerina creyó que el roque iba a caer. El abuelo la tomó de la mano y el grupo se alejó del risco.</p><p>El ruido terminó. Idafe continuaba erguido contra el cielo. Acerina dejó su vasija en el lugar indicado y prometió aprender las palabras de la ceremonia para que no se perdieran.</p><p>Pasaron los años. Acerina se convirtió en una gran narradora. Llevaba a los niños hasta un lugar seguro desde el que podían contemplar el roque y les contaba lo que había vivido.</p><p>Al final, todos miraban la piedra y repetían: «Idafe sigue en pie; nosotros guardamos su memoria».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>Las crónicas relacionan el roque de Idafe con prácticas rituales de la población indígena de La Palma y recogen el nombre de Abora. Acerina es un nombre vinculado a la tradición legendaria de La Palma. En este cuento no representa al personaje de otras versiones; su abuelo, el temblor y la promesa de convertirse en narradora son elementos creados para esta adaptación.</p><section class=\"source-traceability\" data-source-route=\"la-palma\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> Una crónica transmite el temor a la caída de Idafe y la entrega de ofrendas junto al roque. La fuente del parque sitúa ese patrimonio en la Caldera.</p><p><strong>Fuente identificada:</strong></p><ul><li>Trapero, M., y Santana Martel, E. (s. f.). <a href=\"https://guanchismos.ulpgc.es/item/12902\" target=\"_blank\" rel=\"noopener noreferrer\">Diccionario de toponimia de Canarias: Idafe</a>. Entrada «Idafe»: cita a Abreu Galindo, edición 1977, p. 270.</li><li>Gobierno de Canarias (s. f.). <a href=\"https://www.gobiernodecanarias.org/parquesnacionales/caldera_de_taburiente/el_parque/valores_naturales/arqueologia/index.html\" target=\"_blank\" rel=\"noopener noreferrer\">Caldera de Taburiente: Arqueología</a>. Apartados sobre la población benahoarita y los rituales junto a Idafe.</li></ul><p>El pasaje citado no documenta la ceremonia exacta ni su relación concreta con Abora; esos detalles no deben utilizarse como reconstrucción de un rito.</p><p><strong>Nuestra adaptación:</strong> Acerina no representa al personaje de otras versiones. El abuelo, las vasijas, el temblor, la promesa y el estribillo son inventados. «Sostener el cielo» es una imagen literaria del cuento.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-palma\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-palma\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-palma\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-palma\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_dentada.webp\" alt=\"Pintadera de Idafe\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de Idafe</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-la-gomera\" aria-labelledby=\"title-la-gomera\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Gomera</p><h2 id=\"title-la-gomera\">Gara y Jonay, dos voces en la cumbre</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-gomera.webp\" alt=\"Una joven con las manos abiertas se dirige a dos grupos situados a ambos lados de un barranco. Ilustración ficticia del cuento de Gara y Jonay; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · La Gomera</p><p class=\"story-intro\">Adaptación infantil de la leyenda gomera de Gara y Jonay.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Ni el mar ni el barranco pueden callar dos corazones»</div><p>Gara vivía en Agulo y conocía todos los sonidos de los barrancos. Un día miró su reflejo en un manantial y escuchó una advertencia: debía apartarse del fuego.</p><p>Al otro lado del mar, en Tenerife, vivía Jonay. Para llegar hasta La Gomera se lanzó al agua sobre odres hechos con piel de cabra. Nadó durante horas hasta alcanzar la orilla.</p><p>Cuando Gara y Jonay se conocieron, pasearon entre palmeras y hablaron hasta que la luna apareció. Los dos repetían: «Ni el mar ni el barranco pueden callar dos corazones».</p><p>Pero sus familias temían la antigua advertencia. Decían que el agua de Gara y el fuego de Jonay no debían encontrarse. Los jóvenes huyeron hacia la cumbre y pidieron ayuda a Orahan.</p><p>Las familias los buscaron entre la niebla. Cuando por fin los encontraron, la leyenda cuenta que la historia de Gara y Jonay terminó tristemente. Sus nombres quedaron unidos para siempre en la montaña de Garajonay.</p><p>Con el tiempo, las personas comprendieron que la enemistad y la falta de escucha habían causado mucho dolor. Desde entonces, cuando dos comunidades discutían, alguien recordaba a Gara y Jonay antes de cerrar el camino al diálogo.</p><p>Y la cumbre devolvía en forma de eco: «Ni el mar ni el barranco pueden callar dos corazones».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>Gara y Jonay es una leyenda con numerosas versiones. El cruce de Jonay desde Tenerife, la oposición familiar y el final trágico forman parte de versiones muy difundidas. Orahan aparece en testimonios sobre las creencias gomeras. La redacción y los detalles narrativos de este cuento son originales.</p><section class=\"source-traceability\" data-source-route=\"la-gomera\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> El viaje de Jonay sobre odres, el amor y el desenlace trágico aparecen en la versión oral de Virgilio Brito recogida por Maximiano Trapero en 1983.</p><p><strong>Fuente identificada:</strong></p><ul><li>Trapero, M. (1984). <a href=\"https://mdcs.ulpgc.es/files/original/a8601b5c5852953b6ae2c89a8016b0c6c2f7365a.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">La leyenda de Gara y Jonay en La Gomera</a>. Aguayro, 153, pp. 4–6; versión de Virgilio Brito en pp. 5–6.</li><li>Navarro Mederos, J. F. (2016). <a href=\"https://iehcan.com/wp-content/uploads/2016/12/1-Navarro-2016.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">Arqueología en La Gomera: lo que va de ayer a hoy</a>. pp. 13–38.</li></ul><p>La advertencia que une agua y fuego todavía no tiene aquí una versión concreta identificada. No afirmamos la antigüedad de ese motivo ni de toda la leyenda.</p><p><strong>Nuestra adaptación:</strong> El recurso simplifica episodios, evita describir el desenlace de forma explícita y añade el estribillo y la reflexión sobre el diálogo. La invocación a Orahan forma parte de esta escena literaria.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-gomera\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-gomera\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-gomera\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-gomera\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_triangulo.webp\" alt=\"Pintadera del encuentro\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera del encuentro</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-el-hierro\" aria-labelledby=\"title-el-hierro\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">El Hierro</p><h2 id=\"title-el-hierro\">Agarfa y las gotas del Garoé</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_el-hierro.webp\" alt=\"Una niña y dos personas adultas recogen agua bajo un árbol entre la niebla, usando recipientes de aspecto flexible. Ilustración ficticia del cuento de Agarfa y el Garoé; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · El Hierro</p><p class=\"story-intro\">Cuento ambientado entre la población indígena de El Hierro, los bimbapes, e inspirado en el árbol Garoé.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Rama a rama, gota a gota, el Garoé nos da su agua»</div><p>Cuando los bimbapes habitaban El Hierro, Agarfa caminaba cada mañana hasta el Garoé. La niebla se enredaba en sus ramas y se convertía en gotas que caían dentro de unas piletas de piedra.</p><p>Toda la comunidad dependía de aquella agua. Agarfa llenaba las vasijas despacio para no desperdiciar nada y repetía: «Rama a rama, gota a gota, el Garoé nos da su agua».</p><p>Un día aparecieron velas desconocidas en el horizonte. Las personas mayores temieron que los recién llegados encontraran el árbol y se apoderaran de la fuente.</p><p>Cubrieron el sendero con ramas y pidieron a Agarfa que llevara las vasijas por otro camino. La niña avanzó entre la niebla sin revelar dónde se encontraba el Garoé.</p><p>Durante muchas jornadas guardaron el secreto. La tradición cuenta distintas versiones sobre cómo fue descubierto después. También recuerda que una gran tormenta derribó el árbol muchos años más tarde.</p><p>Pero la historia del Garoé no desapareció. Las familias continuaron contando cómo un árbol podía peinar la niebla y convertirla en agua para una isla entera.</p><p>Al recordarlo, todas las voces decían: «Rama a rama, gota a gota, el Garoé nos da su agua».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>El Garoé fue un árbol real asociado a la captación de agua de la niebla. Las versiones sobre el secreto del árbol y su revelación pertenecen a la tradición histórica; también se recuerda su caída durante una tormenta. Agarfa es un nombre bimbape transmitido por la tradición de El Hierro. En este cuento no representa al personaje de otras versiones del Garoé; los recorridos para ocultar el sendero son ficción original.</p><section class=\"source-traceability\" data-source-route=\"el-hierro\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> El Garoé se asocia a la recogida de agua de la niebla. La ocultación del árbol y Agarfa aparecen en una versión divulgativa de su leyenda.</p><p><strong>Fuente identificada:</strong></p><ul><li>Gobierno de Canarias (s. f.). <a href=\"https://www3.gobiernodecanarias.org/medusa/wiki/index.php?title=Leyenda_del_garo%C3%A9\" target=\"_blank\" rel=\"noopener noreferrer\">Leyenda del garoé</a>. CanariWiki, apartado «Historia».</li><li>El Hierro Travel (s. f.). <a href=\"https://elhierro.travel/museos-y-visitas-de-interes/el-hierro/arbol-garoe/\" target=\"_blank\" rel=\"noopener noreferrer\">Árbol Garoé</a>. Apartado «El árbol sagrado de El Hierro».</li></ul><p>El fenómeno de captación de agua y los episodios legendarios no son la misma clase de información. Una versión actual de la leyenda no prueba por sí sola la antigüedad de cada detalle.</p><p><strong>Nuestra adaptación:</strong> Nuestra Agarfa es una niña que protege el sendero, no el personaje de la versión enlazada. Su recorrido, las conversaciones y el estribillo son inventados.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-el-hierro\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"el-hierro\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-el-hierro\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"el-hierro\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_circulos.webp\" alt=\"Pintadera de la niebla\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de la niebla</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-fuerteventura\" aria-labelledby=\"title-fuerteventura\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Fuerteventura</p><h2 id=\"title-fuerteventura\">La luz de Mafasca en el camino</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_fuerteventura.webp\" alt=\"Una mujer y una niña observan una pequeña luz en un paisaje pedregoso al anochecer. Ilustración ficticia del cuento de la Luz de Mafasca; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · Fuerteventura</p><p class=\"story-intro\">Cuento inspirado en una de las versiones de la luz de Mafasca, una tradición oral de Fuerteventura. Esta versión incluye una cruz cristiana; no permite fechar el origen de toda la leyenda.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Luz de Mafasca, no te sigo: regreso por el camino»</div><p>Hace mucho tiempo, dos pastores llamados Guise y Ayose regresaban con sus cabras por un camino de Fuerteventura. La noche era fría y el viento apagaba cada chispa.</p><p>Junto al sendero encontraron una vieja cruz de madera. Sin pensar, arrancaron un trozo y lo utilizaron para encender una hoguera. Calentaron el gofio y se prepararon para seguir.</p><p>Entonces una luz pálida salió de las llamas. No era grande, pero flotaba sobre las piedras. Los pastores recordaron los relatos de Mafasca y dijeron: «Luz de Mafasca, no te sigo: regreso por el camino».</p><p>Caminaron deprisa. La luz avanzó detrás de ellos. Se detuvieron y la luz también se detuvo. Guise y Ayose comprendieron que habían utilizado una cruz sin respetar lo que significaba.</p><p>Prometieron volver al amanecer, reparar la cruz y no arrancar de nuevo madera de aquel lugar. En ese instante, la claridad se hizo pequeña hasta desaparecer.</p><p>Al día siguiente cumplieron su promesa. Después contaron la historia a otros pastores para que nadie repitiera su acción.</p><p>Desde entonces, cuando una luz temblaba en la noche, recordaban: «Luz de Mafasca, no te sigo: regreso por el camino».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>La luz de Mafasca cuenta con versiones y testimonios diversos en Fuerteventura, incluidos relatos recogidos en Tindaya. La quema de una cruz pertenece a algunas versiones: ese motivo cristiano no demuestra cuándo nació el conjunto de la tradición. Tampoco la localización de un testimonio cerca de Tindaya demuestra por sí sola un origen indígena o una continuidad religiosa. Este cuento recrea la versión de la cruz; no establece una explicación histórica del fenómeno. Guise y Ayose fueron nombres de la población maho de Fuerteventura. En este cuento se reutilizan con intención literaria y no representan a los dirigentes históricos; el desarrollo exacto de la escena es una recreación original.</p><p><a href=\"https://www.cabildofuer.es/documentos/Patrimonio_cultural/jornadas_ftv_lzt/volumenes/15_jornadas_ftv_lzt_tomo2.pdf#page=285\" target=\"_blank\" rel=\"noopener\">Consulta: Carreras Navarro (2016), La Luz de Mafasca, pp. 285-310</a>.</p><section class=\"source-traceability\" data-source-route=\"fuerteventura\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> La quema de una cruz y la aparición de la luz se encuentran en testimonios orales sobre Mafasca. Hay versiones y explicaciones diferentes.</p><p><strong>Fuente identificada:</strong></p><ul><li>Carreras Navarro, J. (2016). <a href=\"https://www.cabildofuer.es/documentos/Patrimonio_cultural/jornadas_ftv_lzt/volumenes/15_jornadas_ftv_lzt_tomo2.pdf#page=293\" target=\"_blank\" rel=\"noopener noreferrer\">La Luz de Mafasca</a>. pp. 285–310; testimonios sobre la cruz en pp. 293 y 297–298.</li></ul><p>El motivo de la cruz no permite fechar toda la tradición. Que un testimonio se recoja cerca de Tindaya tampoco demuestra un origen indígena. El cuento no explica científicamente la luz.</p><p><strong>Nuestra adaptación:</strong> Guise y Ayose son pastores ficticios y no representan a los dirigentes históricos. El gofio, los diálogos, la promesa de reparar la cruz y el estribillo son decisiones de esta adaptación.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-fuerteventura\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"fuerteventura\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-fuerteventura\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"fuerteventura\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_doble_triangulo.webp\" alt=\"Pintadera de Mafasca\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de Mafasca</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-lanzarote\" aria-labelledby=\"title-lanzarote\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Lanzarote</p><h2 id=\"title-lanzarote\">Ico y la prueba del humo</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_lanzarote.webp\" alt=\"Una joven habla ante un grupo sentado en un paisaje volcánico, acompañada por una mujer mayor. Ilustración ficticia del cuento de Ico; no es una reconstrucción histórica.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · Lanzarote</p><p class=\"story-intro\">Adaptación infantil de la historia de la princesa Ico en la antigua Lanzarote.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «La verdad no necesita una prueba injusta»</div><p>En la antigua Lanzarote vivía Ico, hija de Zonzamas y Fayna. Algunas personas del consejo desconfiaban de ella porque su piel era más clara y decidieron someterla a una prueba.</p><p>Prepararon una habitación en la que arderían ramas verdes para llenarla de humo. Una anciana sabía que aquella decisión era injusta. Antes de la prueba entregó a Ico una esponja mojada y le explicó cómo respirar a través de ella.</p><p>Ico guardó la esponja y pensó: «La verdad no necesita una prueba injusta».</p><p>El humo comenzó a llenar el recinto. Ico se agachó, cubrió su boca con la esponja húmeda y esperó. Cuando abrieron la puerta, salió caminando.</p><p>El consejo aceptó entonces que pertenecía al linaje. Ico agradeció la ayuda de la anciana, pero no celebró la prueba. Miró a quienes la habían juzgado y preguntó por qué una persona debía ponerse en peligro para demostrar quién era.</p><p>Nadie supo responder. La inteligencia y la solidaridad habían salvado a Ico, pero su pregunta quedó en la memoria de la isla.</p><p>Desde entonces, al contar su historia, muchas voces repiten: «La verdad no necesita una prueba injusta».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>La historia de Ico fue recogida y reelaborada en crónicas y versiones posteriores. La prueba del humo y la ayuda de una mujer mayor forman parte del relato transmitido, aunque los detalles cambian. Las palabras de Ico y su pregunta final son creación original de este recurso.</p><section class=\"source-traceability\" data-source-route=\"lanzarote\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> La prueba del humo y la ayuda de una mujer mayor se transmiten en el relato de Ico. El estudio analiza también las diferencias entre versiones.</p><p><strong>Fuente identificada:</strong></p><ul><li>Pérez Saavedra, F. (1995). <a href=\"https://bk.memoriadelanzarote.com/media/docs/items/20110708111921AVENDAO-E-ICO.pdf#page=19\" target=\"_blank\" rel=\"noopener noreferrer\">La aventura de Avendaño y la leyenda de Ico</a>. Anuario de Estudios Atlánticos, 41, pp. 207–226; prueba y ayuda en pp. 223–224.</li></ul><p>Las interpretaciones de los cronistas y los investigadores deben distinguirse de hechos comprobados. El episodio de la esponja pertenece al relato transmitido.</p><p><strong>Nuestra adaptación:</strong> El recurso simplifica el conflicto y la filiación de Ico; los detalles genealógicos de las fuentes son discutidos. Sus palabras, la pregunta al consejo y el estribillo son creación contemporánea.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-lanzarote\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"lanzarote\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-lanzarote\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"lanzarote\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_chevron.webp\" alt=\"Pintadera de Ico\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera de Ico</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>","<section class=\"route\" id=\"route-la-graciosa\" aria-labelledby=\"title-la-graciosa\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Graciosa</p><h2 id=\"title-la-graciosa\">Guadarfía y la isla de San Borondón</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Progreso de la ruta\"><span class=\"route-step source-step\">1. Comprensión</span><span class=\"route-step truth-step\">2. Reto</span><span class=\"route-step badge-step\">3. Pintadera</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-graciosa.webp\" alt=\"Dos personas observan desde la costa una silueta de isla entre la bruma; una se protege los ojos con la mano. Ilustración ficticia de San Borondón, no de la época indígena.\"><figcaption>Imagen ilustrativa, no es una descripción histórica. Creada con IA para acompañar el cuento; no es una fotografía del pasado.</figcaption><details class=\"image-literacy\"><summary>Miramos la imagen con criterio</summary><p>¿Qué ves y qué necesitarías comprobar? Elige un detalle y contrástalo con una fuente. Un aspecto realista no garantiza exactitud histórica.</p><p>En Primaria, coméntalo con ayuda; en Secundaria, distingue dato, interpretación y ficción y revisa posibles estereotipos. Actividad opcional, oral o en el cuaderno.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Cuento legendario · La Graciosa</p><p class=\"story-intro\">Cuento ambientado en la navegación a vela e inspirado en la leyenda de San Borondón, una isla fantasma que cronistas y cartógrafos situaron al oeste de Canarias y que, según distintas versiones, podía avistarse desde La Palma, El Hierro o La Gomera. Durante siglos, fue conocida como «la octava isla». La Graciosa, en cambio, no tuvo población estable hasta finales del siglo XIX, por lo que no aparecía en los antiguos recuentos de islas habitadas.</p><div class=\"story-refrain\"><strong>Estribillo:</strong> «Isla de la bruma, apareces y te vas»</div><p>Cuando las embarcaciones navegaban a vela y los mapas se dibujaban sobre pergamino, Guadarfía era grumete en un pequeño barco. Una tarde cruzaban el mar cerca de la isla que hoy llamamos La Graciosa.</p><p>Detrás de una franja de bruma apareció una tierra desconocida. Tenía una montaña oscura, árboles y una playa brillante. El capitán recordó las historias sobre San Borondón, la isla que aparecía y desaparecía.</p><p>Guadarfía señaló el horizonte y dijo: «Isla de la bruma, apareces y te vas».</p><p>La tripulación cambió el rumbo, pero cuanto más avanzaba la nave, más lejos parecía estar la isla. Después llegó una niebla tan espesa que tuvieron que bajar las velas y esperar.</p><p>Al amanecer, la bruma se había marchado. Delante del barco solo quedaba el mar. El capitán marcó el lugar en su carta y Guadarfía dibujó la forma que recordaba.</p><p>Otros navegantes contaron visiones parecidas y algunos mapas incluyeron San Borondón. Sin embargo, nadie consiguió alcanzarla.</p><p>La isla continuó apareciendo en los relatos, siempre detrás de la niebla: «Isla de la bruma, apareces y te vas».</p><details class=\"radar\"><summary><strong>Para investigar: ¿cómo se fundamenta el cuento?</strong></summary><p>San Borondón es una leyenda compartida por Canarias. Cronistas y cartógrafos la situaron al oeste del archipiélago y durante siglos fue conocida como «la octava isla»; las versiones sobre sus avistamientos varían. La Graciosa no tuvo población estable hasta finales del siglo XIX. Situar a Guadarfía y su embarcación en estas aguas es una recreación literaria para vincular la leyenda con la ruta actual de La Graciosa; el personaje no representa al dirigente histórico del mismo nombre.</p><section class=\"source-traceability\" data-source-route=\"la-graciosa\" aria-label=\"Fuentes y adaptación del cuento\"><p><strong>Motivo tradicional o documentado:</strong> San Borondón aparece en relatos de viajeros y en mapas históricos. Su tradición está vinculada al viaje legendario de san Brandán.</p><p><strong>Fuente identificada:</strong></p><ul><li>Chaparro Domínguez, M. Á. (2013). <a href=\"https://revistas.ucm.es/index.php/RFRM/article/download/45706/42966/73431#page=4\" target=\"_blank\" rel=\"noopener noreferrer\">Revisión del mito geográfico de San Borondón y aproximación a su huella en la literatura y otras artes</a>. Revista de Filología Románica, 30(2), pp. 229–244; origen y viajeros en pp. 232–236.</li><li>Martínez Berriel, S. (2001–2002). <a href=\"https://revistavegueta.ulpgc.es/ojs/index.php/revistavegueta/article/view/225\" target=\"_blank\" rel=\"noopener noreferrer\">La isla de las buenas costumbres: cambio social y cultural en la isla de La Graciosa</a>. Vegueta, 6; resumen y contexto del poblamiento.</li></ul><p>La leyenda se sitúa habitualmente al oeste de Canarias. Nuestro episodio junto a La Graciosa no es un avistamiento documentado.</p><p><strong>Nuestra adaptación:</strong> Guadarfía es un grumete ficticio y no el dirigente histórico de Lanzarote. El barco junto a La Graciosa, el dibujo, los diálogos y el estribillo vinculan literariamente esta ruta a la leyenda.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-graciosa\"><p class=\"challenge-kicker\">Reto 1 de 2</p><h3>Comprendemos el cuento</h3><p>Elige la respuesta correcta. Necesitas 3 de 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-graciosa\">Comprobar la comprensión</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-graciosa\"><p class=\"challenge-kicker\">Reto 2 de 2</p><h3>Reto de la pintadera</h3><p>Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-graciosa\">Comprobar el reto</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/pintadera_espiral_cuadrada.webp\" alt=\"Pintadera del horizonte\"><div><span>Insignia añadida automáticamente</span><strong>Pintadera del horizonte</strong><p>Puedes verla en cualquier momento desde el botón «Pasaporte» de la barra superior.</p><button class=\"button open-passport\" type=\"button\">Ver mi pasaporte</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Elegir otra isla</button></div></section>"];
const storageKey="mitomapa-canario-v2";
const legacyKey="mitomapa-canario-v1";
const byId=id=>document.getElementById(id);
const validIds=new Set(routes.map(route=>route.id));
const normalize=values=>new Set((Array.isArray(values)?values:[]).filter(id=>validIds.has(id)));
const storageFailures=new Set();
let storageReadIssue=false;
function updateStorageNotice(){
 const notice=byId("storageNotice");if(!notice)return;
 notice.hidden=storageFailures.size===0&&!storageReadIssue;
}
function readJSON(key,fallback){
 try{const value=localStorage.getItem(key);return value?JSON.parse(value):fallback;}
 catch(error){storageReadIssue=true;updateStorageNotice();return fallback;}
}
function writeJSON(key,value){
 try{localStorage.setItem(key,JSON.stringify(value));storageFailures.delete(key);updateStorageNotice();return true;}
 catch(error){storageFailures.add(key);updateStorageNotice();return false;}
}
const legacy=normalize(readJSON(legacyKey,[]));
const stored=readJSON(storageKey,null);
let sourcePassed=normalize(stored?.sourcePassed||[...legacy]);
let truthPassed=normalize(stored?.truthPassed||[...legacy]);
let earned=normalize(stored?.earned||[...legacy]);
function save(){return writeJSON(storageKey,{sourcePassed:[...sourcePassed],truthPassed:[...truthPassed],earned:[...earned]});}
const preferencesKey="mitomapa-canario-preferencias-v3";
const savedPreferences=readJSON(preferencesKey,{});
let readerMode=savedPreferences.readerMode==="complete"?"complete":"guided";
let learningLevel=["early","middle","advanced","secondary"].includes(savedPreferences.learningLevel)?savedPreferences.learningLevel:"middle";
let learnerName=typeof savedPreferences.learnerName==="string"?savedPreferences.learnerName.slice(0,80):"";
let lastRouteId=validIds.has(savedPreferences.lastRouteId)?savedPreferences.lastRouteId:null;
let selectedVoiceURI=typeof savedPreferences.selectedVoiceURI==="string"?savedPreferences.selectedVoiceURI:"";

// La revisión es una anotación local de acompañamiento, no una certificación.
const itineraryKey="mitomapa-canario-itinerarios-v1";
const itineraryLevels=["early","middle","advanced","secondary"];
const notebookTaskNames={words:"Vocabulario",research:"Investiga",creation:"Crea"};
const notebookDefaults={early:[],middle:["words"],advanced:["words","research","creation"],secondary:["words","research","creation"]};
function sanitizeItineraries(raw){
 const clean={};
 for(const level of itineraryLevels){
  clean[level]={};
  for(const route of routes){
   const item=raw?.[level]?.[route.id];
   clean[level][route.id]={reviewed:item?.reviewed===true,tasks:typeof item?.tasks==="string"?item.tasks.slice(0,240):"",
 selectedTasks:Array.isArray(item?.selectedTasks)?Object.keys(notebookTaskNames).filter(key=>item.selectedTasks.includes(key)):[...notebookDefaults[level]],
 evidenceMode:item?.evidenceMode==="external"?"external":"web",externalCreation:item?.externalCreation===true,flexibleLength:item?.flexibleLength===true};
  }
 }
 return clean;
}
let itineraries=sanitizeItineraries(readJSON(itineraryKey,{}));
function itineraryFor(id){return itineraries[learningLevel][id];}
function saveItineraries(){return writeJSON(itineraryKey,itineraries);}
function selectedNotebookTasks(id){return itineraryFor(id).selectedTasks;}
function invalidateItineraryTask(id,task,track=null){
 let changed=false;
 for(const level of itineraryLevels){
  if(track==="secondary"&&level!=="secondary"||track==="primary"&&level==="secondary")continue;
  const item=itineraries[level][id];
  if(item.reviewed&&item.selectedTasks.includes(task)&&(task!=="creation"||item.evidenceMode!=="external")){item.reviewed=false;changed=true;}
 }
 if(changed)saveItineraries();updateItineraryUI();
}
function notebookCompletion(id){const state=getWorkshopRouteState(id);return {words:state.words,research:state.research,creation:workshopCreationComplete(state,id)};}
function applyNotebookAssignment(id){
 const workshop=byId(`activity-${id}`);if(!workshop)return;
 const selected=selectedNotebookTasks(id);workshop.hidden=!selected.length;
 workshop.querySelectorAll("[data-activity-tab]").forEach(tab=>tab.hidden=!selected.includes(tab.dataset.activityTab));
 const current=workshop.querySelector('[data-activity-tab][aria-selected="true"]');
 const active=current&&!current.hidden?current.dataset.activityTab:(learningLevel==="secondary"&&selected.includes("creation")?"creation":selected[0]);
 activateWorkshopPanel(workshop,active);
 const item=itineraryFor(id),external=item.evidenceMode==="external";
 workshop.querySelectorAll(".creation-version").forEach(zone=>zone.hidden=external);
 workshop.querySelectorAll(".activity-save-creation").forEach(button=>{button.hidden=external;button.dataset.creationTrack=learningLevel==="secondary"?"secondary":"primary";button.textContent=learningLevel==="secondary"?"Marcar propuesta como preparada":"Marcar creación como preparada";});
 refreshCreationReview(workshop,id);
 const note=workshop.querySelector(".external-creation-note");if(note){note.hidden=!external;note.textContent=item.externalCreation?"Tu docente ha registrado la revisión de tu producción realizada fuera de la web.":"Tu producción se realizará fuera de la web: puede ser oral, en papel, en audio o en otra herramienta, según lo acordado. Comparte la evidencia con tu docente para que registre su revisión.";}
 const length=workshop.querySelector(".secondary-length-note");if(length)length.textContent=secondaryCreations[id].lengthLabel+(item.flexibleLength?" Extensión adaptada: aplica lo acordado con tu docente; esta orientación no bloquea la entrega.":" Tu docente puede adaptar esta extensión desde el modo docente.");
 updateWorkshopSummary(id);
}
function updateItineraryUI(){
 const count=routes.filter(route=>itineraryFor(route.id).reviewed).length;
 const summary=byId("itinerarySummary");
 if(summary)summary.textContent=`${currentBadgeCount()}/8 pintaderas conseguidas · ${count}/8 itinerarios revisados en ${learningLevelLabel()}.`;
 document.querySelectorAll(".route").forEach(section=>{
  const id=section.id.replace("route-","");
  const status=section.querySelector(".itinerary-status");
  if(status)status.textContent=itineraryFor(id).reviewed?"Itinerario revisado manualmente con tu docente":"Itinerario pendiente de revisión con tu docente";
  const tasks=section.querySelector(".assigned-tasks");
  if(tasks){tasks.textContent=itineraryFor(id).tasks;tasks.hidden=!itineraryFor(id).tasks;}
 });
 window.MitoMapaJourney?.refresh();
}
const itinerarySteps={
 early:["Escucha o lee el cuento con ayuda y repite el estribillo.","Responde las tres preguntas de comprensión para conseguir la pintadera.","Realiza la actividad oral, el dibujo u otra tarea que te indique tu docente.","Comparte tu trabajo y revisa con tu docente el itinerario acordado."],
 middle:["Lee el cuento y observa su ilustración.","Supera la comprensión y el verdadero o falso para conseguir la pintadera.","Trabaja el vocabulario y realiza las demás tareas acordadas con tu docente.","Revisa el trabajo con tu docente: la pintadera no sustituye esta revisión."],
 advanced:["Lee el cuento y distingue la leyenda de la recreación literaria.","Supera la comprensión y el verdadero o falso para conseguir la pintadera.","Elige con tu docente las tareas de vocabulario, investigación o creación que vas a realizar.","Crea tu producción y revisa con tu docente las tareas acordadas."],
 secondary:["Lee el cuento e identifica la tradición y la recreación literaria.","Supera los dos retos de comprensión para conseguir la pintadera.","Contrasta fuentes y prepara la producción de Secundaria propuesta para esta isla.","Revisa tu texto con la lista de cotejo y comparte las evidencias con tu docente."]
};
const speechSupported="speechSynthesis" in window&&"SpeechSynthesisUtterance" in window;
let availableVoices=[];
let narrationToken=0;
let narrationState={routeId:null,index:0,chunks:[],paused:false,token:0,audio:null};
let recordingPlayRequest=0;
function routeRecording(routeId){
 const recording=window.MitoMapaRecordings?.[routeId];
 return recording&&typeof recording.src==="string"&&recording.src.trim()?recording:null;
}
function narrationLabel(text){return String(text).replace(/[&<>"']/g,character=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character]));}
function savePreferences(){return writeJSON(preferencesKey,{readerMode,learningLevel,learnerName,lastRouteId,selectedVoiceURI});}
function setReaderMode(mode){
 readerMode=mode==="complete"?"complete":"guided";
 document.body.classList.toggle("mode-guided",readerMode==="guided");
 document.body.classList.toggle("mode-complete",readerMode==="complete");
 if(readerMode==="guided")document.querySelectorAll(".radar").forEach(radar=>{radar.open=false;});
 document.querySelectorAll("[data-reader-mode]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.readerMode===readerMode)));
 const status=byId("readerModeStatus");
 if(status)status.textContent=readerMode==="guided"?"Lectura acompañada: letra mayor, una columna y fuentes que puedes desplegar.":"Exploración completa: diseño compacto y radar de fuentes disponible.";
 savePreferences();
}
function injectExperienceTools(){
 const legend=document.querySelector(".hero .legend");
 if(!legend)return;
 const chips=[...legend.querySelectorAll(".chip")];
 const offlineChip=chips.find(chip=>chip.textContent.trim()==="Sin conexión");
 if(offlineChip)offlineChip.textContent="Sin registro";
 const panel=document.createElement("section");
 panel.className="experience-tools";
 panel.setAttribute("aria-labelledby","experienceToolsTitle");
 panel.innerHTML=`<h2 id="experienceToolsTitle">Prepara tu expedición</h2><p>Elige la etapa y la presentación. Puedes cambiarlas cuando quieras.</p><div class="learning-level-block"><h3>Etapa recomendada</h3><div class="learning-level-switch" role="group" aria-label="Etapa educativa"><button type="button" data-learning-level="early">Infantil y 1.º ciclo</button><button type="button" data-learning-level="middle">2.º ciclo</button><button type="button" data-learning-level="advanced">3.º ciclo</button><button type="button" data-learning-level="secondary">Secundaria</button></div><p class="mode-status" id="learningLevelStatus" role="status"></p></div><div class="learning-level-block"><h3>Presentación del texto</h3><div class="mode-switch" role="group" aria-label="Modo de lectura"><button type="button" data-reader-mode="guided">Lectura acompañada</button><button type="button" data-reader-mode="complete">Explora a fondo</button></div><p class="mode-status" id="readerModeStatus" role="status"></p></div><div class="experience-actions"><button class="text-button" id="resumeRoute" type="button">Continuar última isla</button><button class="text-button" id="printResource" type="button">Imprimir cuentos</button></div>`;
 const hero=legend.closest(".hero");if(hero)hero.append(panel);else legend.after(panel);
 panel.querySelectorAll("[data-reader-mode]").forEach(button=>button.addEventListener("click",()=>setReaderMode(button.dataset.readerMode)));
 panel.querySelectorAll("[data-learning-level]").forEach(button=>button.addEventListener("click",()=>setLearningLevel(button.dataset.learningLevel)));
 byId("resumeRoute").addEventListener("click",()=>{if(lastRouteId)showRoute(lastRouteId);});
 byId("printResource").addEventListener("click",()=>{routes.forEach(route=>ensureRoute(route.id));window.setTimeout(()=>window.print(),80);});
 byId("resumeRoute").disabled=!lastRouteId;
 const passportKicker=document.querySelector("#passportDialog .challenge-kicker");
 if(passportKicker)passportKicker.textContent="Guardado en este navegador";
 const puzzleLead=byId("missionTitle")?.closest("section")?.querySelector(".lead");
 if(puzzleLead)puzzleLead.textContent="Reconstruye el mapa observando sus formas y colores. Arrastra una pieza sobre otra o selecciona dos para intercambiarlas. Con el teclado, usa Tab para recorrer las piezas y Enter o espacio para seleccionarlas. Puedes utilizar «Mostrar solución» como apoyo.";
 const footer=document.querySelector(".footer-inner");
 if(footer)footer.insertAdjacentHTML("beforeend",`<details class="footer-privacy"><summary>Privacidad y guardado</summary><p>No necesitas una cuenta. El progreso se guarda solo en este navegador. El nombre o equipo es opcional y se utiliza en el seguimiento y el diploma. Los cuentos con grabación reproducen el audio indicado junto al reproductor; los demás usan las voces disponibles en el dispositivo. El sonido comienza cuando pulsas Reproducir. Para cambiar de navegador, guarda el seguimiento desde Docente.</p></details>`);
 setReaderMode(readerMode);
 setLearningLevel(learningLevel,false);
}
function voiceScore(voice){
 const lang=(voice.lang||"").replace("_","-").toLowerCase();
 const name=(voice.name||"").toLowerCase();
 let score=0;
 if(lang==="es-ic")score+=120;
 else if(lang==="es-es")score+=80;
 else if(lang.startsWith("es-"))score+=60;
 else if(lang==="es")score+=50;
 if(name.includes("canar"))score+=100;
 if(voice.localService)score+=5;
 return score;
}
function preferredVoice(){return [...availableVoices].filter(voice=>voiceScore(voice)>0).sort((a,b)=>voiceScore(b)-voiceScore(a))[0]||null;}
function selectedVoice(){
 if(selectedVoiceURI){
  const chosen=availableVoices.find(voice=>voice.voiceURI===selectedVoiceURI);
  if(chosen)return chosen;
 }
 return preferredVoice();
}
function spanishVoices(){
 return [...availableVoices].filter(voice=>(voice.lang||"").replace("_","-").toLowerCase().startsWith("es"))
  .sort((a,b)=>voiceScore(b)-voiceScore(a)||(a.name||"").localeCompare(b.name||"","es"));
}
function voiceDescription(){
 if(!speechSupported)return"Este navegador no ofrece lectura automática. El cuento sigue disponible como texto.";
 const voice=selectedVoice();
 if(!voice)return"No se ha encontrado una voz española instalada. El cuento sigue disponible como texto.";
 const canarian=(voice.lang||"").replace("_","-").toLowerCase()==="es-ic"||/canar/i.test(voice.name||"");
 return canarian?`Voz canaria seleccionada: ${voice.name}.`:`Voz seleccionada: ${voice.name} (${voice.lang||"español"}). La pronunciación depende del dispositivo.`;
}
function refreshVoices(){
 if(!speechSupported)return;
 availableVoices=window.speechSynthesis.getVoices();
 const voices=spanishVoices();
 if(voices.length&&selectedVoiceURI&&!voices.some(voice=>voice.voiceURI===selectedVoiceURI))selectedVoiceURI="";
 document.querySelectorAll(".narration-voice").forEach(select=>{
  const automatic=document.createElement("option");
  automatic.value="";automatic.textContent="Automática (recomendada)";
  select.replaceChildren(automatic);
  voices.forEach(voice=>{
   const option=document.createElement("option");
   option.value=voice.voiceURI;option.textContent=`${voice.name} · ${voice.lang||"es"}`;
   select.append(option);
  });
  select.value=voices.some(voice=>voice.voiceURI===selectedVoiceURI)?selectedVoiceURI:"";
  select.disabled=!voices.length;
 });
 document.querySelectorAll(".voice-note[data-device-voice]").forEach(note=>note.textContent=voiceDescription());
}
function narrationMarkup(route){
 const recording=routeRecording(route.id);
 const note=recording?`Narración: ${narrationLabel(recording.narrator||"grabación del cuento")}.`:speechSupported?"Comprobando las voces del dispositivo…":voiceDescription();
 const voice=recording?"":`<label class="narration-setting">Voz <select class="narration-voice" aria-label="Voz para la lectura"><option value="">Automática (recomendada)</option></select></label>`;
 const ambient=recording?.ambientSrc?`<label class="narration-setting narration-ambient-label"><input class="narration-ambient" type="checkbox" checked> Ambiente suave</label>`:"";
 const timeline=recording?`<div class="narration-timeline"><button class="text-button narration-back" type="button" aria-label="Retroceder diez segundos" disabled>−10 s</button><div class="narration-position"><label for="narration-position-${route.id}">Posición de la narración</label><input class="narration-seek" id="narration-position-${route.id}" type="range" min="0" max="0" step="1" value="0" aria-valuetext="Duración pendiente" disabled><p class="narration-time"><span class="narration-current">0:00</span> / <span class="narration-duration">--:--</span></p></div><button class="text-button narration-forward" type="button" aria-label="Avanzar diez segundos" disabled>+10 s</button></div>`:"";
 return `<section class="narrator" data-narration-source="${recording?"recording":"device"}" aria-labelledby="narrator-title-${route.id}"><div class="narrator-copy"><p class="narrator-kicker">Escucha el cuento</p><h3 id="narrator-title-${route.id}">${recording?"Narración grabada":"Lectura en voz alta"}</h3><p class="voice-note"${recording?"":" data-device-voice"}>${note}</p></div><div class="narrator-controls"><button class="button narration-play" type="button" data-route="${route.id}">▶ Reproducir</button><button class="button secondary narration-pause" type="button" data-route="${route.id}" disabled>⏸ Pausar</button><button class="button secondary narration-stop" type="button" data-route="${route.id}" disabled>■ Detener</button>${timeline}${voice}<label class="narration-setting">Velocidad <select class="narration-rate" aria-label="Velocidad de lectura"><option value="0.82">Lenta</option><option value="${recording?"1":"0.94"}" selected>Normal</option><option value="1.08">Ágil</option></select></label>${ambient}<p class="narration-status" role="status" aria-live="polite">Lista para comenzar.</p></div></section>`;
}
function narrationTime(value){
 const seconds=Math.max(0,Math.floor(Number(value)||0));
 return `${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,"0")}`;
}
function recordingIsSeekable(audio){
 if(!audio||audio.readyState<1||!Number.isFinite(audio.duration)||audio.duration<=0)return false;
 for(let index=0;index<audio.seekable.length;index++)if(audio.seekable.end(index)>audio.seekable.start(index))return true;
 return false;
}
function syncRecordingTimeline(routeId,finished=null){
 const section=byId(`route-${routeId}`),slider=section?.querySelector(".narration-seek");if(!slider)return;
 const audio=narrationState.routeId===routeId?narrationState.audio:null;
 const duration=finished?.duration??audio?.duration;
 const available=recordingIsSeekable(audio);
 const known=Number.isFinite(duration)&&duration>0;
 const position=known?Math.min(duration,Math.max(0,finished?.position??audio?.currentTime??0)):0;
 slider.disabled=!available;slider.max=known?String(duration):"0";slider.value=String(position);
 slider.setAttribute("aria-valuetext",known?`${narrationTime(position)} de ${narrationTime(duration)}`:"Duración pendiente");
 section.querySelector(".narration-current").textContent=narrationTime(position);
 section.querySelector(".narration-duration").textContent=known?narrationTime(duration):"--:--";
 section.querySelectorAll(".narration-back,.narration-forward").forEach(button=>{button.disabled=!available;});
}
function seekNarration(routeId,value,{relative=false}={}){
 if(narrationState.routeId!==routeId)return;
 const audio=narrationState.audio,duration=audio?.duration;
 if(!recordingIsSeekable(audio))return;
 const requested=Number(value);if(!Number.isFinite(requested))return;
 try{audio.currentTime=Math.max(0,Math.min(duration,relative?audio.currentTime+requested:requested));}
 catch(error){return;}
 syncRecordingTimeline(routeId);
}
function splitSpeechText(text,maxLength=230){
 const sentences=text.match(/[^.!?…]+[.!?…]+|[^.!?…]+$/g)||[text];
 const chunks=[];let current="";
 sentences.forEach(sentence=>{
  const clean=sentence.trim();
  if(!clean)return;
  if((current+" "+clean).trim().length<=maxLength)current=(current+" "+clean).trim();
  else{if(current)chunks.push(current);if(clean.length<=maxLength)current=clean;else{for(let start=0;start<clean.length;start+=maxLength)chunks.push(clean.slice(start,start+maxLength));current="";}}
 });
 if(current)chunks.push(current);
 return chunks;
}
function clearNarrationHighlight(routeId){
 const scope=routeId?byId(`route-${routeId}`):document;
 scope?.querySelectorAll(".is-reading").forEach(element=>element.classList.remove("is-reading"));
}
function storySpeechChunks(section){
 const entries=[];
 const title=section.querySelector("h2");
 if(title)entries.push({element:title,text:title.textContent.trim()});
 const story=section.querySelector(".story");
 if(story)Array.from(story.children).forEach(element=>{
  if(element.matches("p:not(.route-meta):not(.story-intro)")||element.classList.contains("story-refrain")){
   const text=element.textContent.trim();if(text)entries.push({element,text});
  }
 });
 return entries.flatMap(entry=>splitSpeechText(entry.text).map(text=>({text,element:entry.element})));
}
function updateNarrationUi(routeId,state,message){
 const section=byId(`route-${routeId}`);if(!section)return;
 const play=section.querySelector(".narration-play"),pause=section.querySelector(".narration-pause"),stop=section.querySelector(".narration-stop"),status=section.querySelector(".narration-status");
 const active=state==="playing"||state==="paused";
 play.disabled=(!routeRecording(routeId)&&!speechSupported)||state==="playing";
 play.textContent=state==="finished"?"↻ Escuchar de nuevo":"▶ Reproducir";
 pause.disabled=!active;
 pause.textContent=state==="paused"?"▶ Continuar":"⏸ Pausar";
 stop.disabled=!active;
 if(status&&message)status.textContent=message;
 section.querySelector(".narrator")?.classList.toggle("is-speaking",state==="playing");
}
function stopNarration(message="Lectura detenida."){
 const previous=narrationState.routeId,audio=narrationState.audio,controller=narrationState.blobController,objectUrl=narrationState.objectUrl;
 narrationToken++;
 recordingPlayRequest++;
 narrationState={routeId:null,index:0,chunks:[],paused:false,token:narrationToken,audio:null};
 controller?.abort();
 if(audio){
  audio.onplaying=null;audio.onended=null;audio.onerror=null;
  audio.onloadedmetadata=null;audio.ondurationchange=null;audio.ontimeupdate=null;audio.oncanplay=null;audio.onseeked=null;audio.onprogress=null;
  audio.pause();audio.removeAttribute("src");audio.load();
 }
 if(objectUrl)URL.revokeObjectURL(objectUrl);
 if(speechSupported)window.speechSynthesis.cancel();
 if(previous){clearNarrationHighlight(previous);updateNarrationUi(previous,"idle",message);syncRecordingTimeline(previous);}
}
function playRecording(audio,routeId,token){
 const request=++recordingPlayRequest;
 const current=()=>token===narrationToken&&narrationState.audio===audio&&narrationState.routeId===routeId;
 const failed=error=>{
  if(!current()||request!==recordingPlayRequest||narrationState.paused)return;
  if(error?.name==="NotAllowedError"){
   narrationState.paused=true;narrationState.awaitingGesture=true;recordingPlayRequest++;audio.pause();
   updateNarrationUi(routeId,"paused","Narración lista. Pulsa Reproducir o Continuar para escuchar.");
   return;
  }
  stopNarration("No se pudo reproducir la grabación. Puedes volver a intentarlo o leer el texto.");
 };
 let pending;
 try{pending=audio.play();}
 catch(error){failed(error);return;}
 Promise.resolve(pending).then(()=>{
  if(!current()){audio.pause();return;}
  if(narrationState.paused){audio.pause();return;}
  if(request===recordingPlayRequest){narrationState.awaitingGesture=false;updateNarrationUi(routeId,"playing","Reproduciendo la narración grabada.");}
 }).catch(failed);
}
function prepareRecordingSeek(audio,routeId,token,source){
 const state=narrationState;
 const current=()=>token===narrationToken&&narrationState===state&&narrationState.audio===audio;
 // Un audio HTTP ya iniciado puede reproducirse, pero algunos servidores no
 // permiten buscar aunque el MP3 esté entero en el búfer. Solo en ese caso
 // se prepara una URL local; los servidores con rangos conservan su flujo.
 if(!current()||state.seekFallbackAttempted||state.objectUrl||recordingIsSeekable(audio))return;
 if(!/^https?:$/.test(location.protocol)||typeof fetch!=="function"||typeof AbortController!=="function")return;
 if(audio.readyState<3||!Number.isFinite(audio.duration)||audio.duration<=0||!audio.buffered.length)return;
 if(audio.buffered.end(audio.buffered.length-1)<audio.duration-.25)return;
 state.seekFallbackAttempted=true;
 const controller=new AbortController();state.blobController=controller;
 fetch(source,{signal:controller.signal,cache:"force-cache"}).then(response=>{
  if(!response.ok)throw new Error("AUDIO_HTTP");
  return response.blob();
 }).then(blob=>{
  if(!current())return;
  if(!blob.size)throw new Error("AUDIO_EMPTY");
  state.blobController=null;
  state.objectUrl=URL.createObjectURL(blob);
  state.blobResumePosition=Math.max(0,audio.currentTime||0);state.sourceLoading=true;
  recordingPlayRequest++;audio.pause();
  audio.src=state.objectUrl;audio.load();
  syncRecordingTimeline(routeId);
  updateNarrationUi(routeId,state.paused?"paused":"playing",state.paused?"Narración en pausa. Preparando el avance…":"Preparando el avance de la narración…");
 }).catch(error=>{
  if(!current())return;
  state.blobController=null;
  // La descarga auxiliar no sustituye el audio hasta completarse: si falla,
  // la reproducción directa sigue disponible, también en aplicaciones locales.
  updateNarrationUi(routeId,state.paused?"paused":"playing","Puedes seguir escuchando. No se ha podido preparar el avance; vuelve a intentarlo desde el principio si lo necesitas.");
 });
}
function startRecording(routeId,recording){
 const section=byId(`route-${routeId}`);if(!section)return;
 stopNarration();
 const ambient=section.querySelector(".narration-ambient")?.checked;
 const audio=new Audio();
 const token=++narrationToken;
 narrationState={routeId,index:0,chunks:[],paused:false,token,audio,blobController:null,objectUrl:null,blobResumePosition:null,sourceLoading:false,seekFallbackAttempted:false,awaitingGesture:false};
 audio.preload="none";
 audio.defaultPlaybackRate=Number(section.querySelector(".narration-rate")?.value)||1;
 audio.playbackRate=audio.defaultPlaybackRate;
 const source=ambient&&recording.ambientSrc?recording.ambientSrc:recording.src;
 audio.src=source;
 const current=()=>token===narrationToken&&narrationState.audio===audio;
 const sync=()=>{
  if(!current())return;
  if(narrationState.sourceLoading&&audio.readyState>=1&&Number.isFinite(audio.duration)){
   const position=narrationState.blobResumePosition;
   narrationState.sourceLoading=false;narrationState.blobResumePosition=null;
   try{audio.currentTime=Math.min(audio.duration,position||0);}catch(error){}
   if(narrationState.paused)updateNarrationUi(routeId,"paused","Narración preparada, en pausa.");
   else playRecording(audio,routeId,token);
  }
  syncRecordingTimeline(routeId);
  prepareRecordingSeek(audio,routeId,token,source);
 };
 audio.onloadedmetadata=sync;audio.ondurationchange=sync;audio.ontimeupdate=sync;audio.oncanplay=sync;audio.onseeked=sync;audio.onprogress=sync;
 audio.onplaying=()=>{
  if(!current()||narrationState.paused){audio.pause();return;}
  sync();
  updateNarrationUi(routeId,"playing","Reproduciendo la narración grabada.");
 };
 audio.onended=()=>{
  if(!current())return;
  const duration=audio.duration;
  stopNarration();updateNarrationUi(routeId,"finished","Cuento terminado. Puedes escucharlo de nuevo.");
  syncRecordingTimeline(routeId,{duration,position:duration});
 };
 audio.onerror=()=>{if(current())stopNarration("No se pudo cargar la grabación. Puedes volver a intentarlo o leer el texto.");};
 updateNarrationUi(routeId,"playing","Cargando la narración grabada…");
 playRecording(audio,routeId,token);
}
function speakNextChunk(){
 if(!speechSupported||!narrationState.routeId)return;
 if(narrationState.index>=narrationState.chunks.length){
  const completedRoute=narrationState.routeId;
  narrationState={routeId:null,index:0,chunks:[],paused:false,token:narrationToken};
  clearNarrationHighlight(completedRoute);updateNarrationUi(completedRoute,"finished","Cuento terminado. Puedes escucharlo de nuevo.");
  return;
 }
 const routeId=narrationState.routeId,token=narrationState.token;
 const chunk=narrationState.chunks[narrationState.index];clearNarrationHighlight(routeId);chunk.element?.classList.add("is-reading");
 const utterance=new SpeechSynthesisUtterance(chunk.text);
 const voice=selectedVoice();if(voice)utterance.voice=voice;
 utterance.lang=voice?.lang||"es-IC";
 const rate=byId(`route-${routeId}`)?.querySelector(".narration-rate")?.value;
 utterance.rate=Number(rate)||0.94;utterance.pitch=1;utterance.volume=1;
 utterance.onstart=()=>{if(token===narrationToken)updateNarrationUi(routeId,"playing",`Leyendo fragmento ${narrationState.index+1} de ${narrationState.chunks.length}.`);};
 utterance.onend=()=>{if(token!==narrationToken||narrationState.routeId!==routeId)return;narrationState.index++;speakNextChunk();};
 utterance.onerror=event=>{if(token!==narrationToken||event.error==="canceled"||event.error==="interrupted")return;stopNarration("No se pudo iniciar la voz del dispositivo. Puedes continuar leyendo el texto.");};
 window.speechSynthesis.speak(utterance);
}
function startNarration(routeId){
 if(narrationState.routeId===routeId&&narrationState.audio&&narrationState.awaitingGesture){
  narrationState.paused=false;narrationState.awaitingGesture=false;
  updateNarrationUi(routeId,"playing","Reanudando la narración…");
  if(!narrationState.sourceLoading)playRecording(narrationState.audio,routeId,narrationState.token);
  return;
 }
 const recording=routeRecording(routeId);
 if(recording){startRecording(routeId,recording);return;}
 if(!speechSupported){updateNarrationUi(routeId,"idle","Este navegador no ofrece lectura automática.");return;}
 const section=byId(`route-${routeId}`);if(!section)return;
 stopNarration();
 const chunks=storySpeechChunks(section);narrationToken++;
 narrationState={routeId,index:0,chunks,paused:false,token:narrationToken};
 updateNarrationUi(routeId,"playing","Preparando la voz del dispositivo…");
 speakNextChunk();
}
function toggleNarrationPause(routeId){
 if(narrationState.routeId!==routeId)return;
 if(narrationState.audio){
  if(narrationState.paused){
   narrationState.paused=false;narrationState.awaitingGesture=false;updateNarrationUi(routeId,"playing","Reanudando la narración…");
   if(!narrationState.sourceLoading)playRecording(narrationState.audio,routeId,narrationState.token);
  }else{
   narrationState.paused=true;recordingPlayRequest++;narrationState.audio.pause();
   updateNarrationUi(routeId,"paused","Narración en pausa.");
  }
  return;
 }
 if(!speechSupported)return;
 if(narrationState.paused){window.speechSynthesis.resume();narrationState.paused=false;updateNarrationUi(routeId,"playing","Lectura reanudada.");}
 else{window.speechSynthesis.pause();narrationState.paused=true;updateNarrationUi(routeId,"paused","Lectura en pausa.");}
}
function openDialog(dialog){if(typeof dialog.showModal==="function")dialog.showModal();else dialog.setAttribute("open","");}
function closeDialog(dialog){if(typeof dialog.close==="function")dialog.close();else dialog.removeAttribute("open");}
function badgeSlotMarkup(route){
 const obtained=badgeCountsForLevel(route.id);
 const retained=earned.has(route.id)&&!obtained;
 return `<button class="badge-slot ${obtained?"earned":""}" type="button" data-passport-route="${route.id}" aria-label="${route.island}: ${obtained?route.badgeName+", conseguida en la etapa seleccionada":retained?"pintadera histórica; requisitos de esta etapa pendientes":"pintadera pendiente"}"><img src="${ASSETS[route.badge]}" alt=""><strong>${route.island}</strong><small>${obtained?route.badgeName:retained?"Conseguida en otra etapa":"Pintadera por descubrir"}</small><span class="badge-state">${obtained?"Conseguida":retained?"Completa esta etapa":"Pendiente"}</span></button>`;
}
function bindPassportRoutes(scope){
 scope.querySelectorAll("[data-passport-route]").forEach(button=>button.addEventListener("click",()=>{
  if(byId("passportDialog").open)closeDialog(byId("passportDialog"));
  showRoute(button.dataset.passportRoute);
 }));
}
function updateProgress(){
 const count=currentBadgeCount();
 byId("progressText").textContent=`${count}/8`;
 byId("passportCount").textContent=`${count}/8`;
 byId("progressBar").style.width=`${count/routes.length*100}%`;
 byId("badgeShelf").innerHTML=routes.map(badgeSlotMarkup).join("");
 byId("passportDialogGrid").innerHTML=routes.map(badgeSlotMarkup).join("");
 bindPassportRoutes(byId("badgeShelf"));
 bindPassportRoutes(byId("passportDialogGrid"));
 const routeRequirement=learningLevel==="early"?"la comprensión de cada cuento":"los dos retos de cada isla";
 byId("passportDialogStatus").textContent=count===routes.length?"¡Pasaporte completo! Has reunido las ocho pintaderas.":`Has reunido ${count} de 8 pintaderas. Supera ${routeRequirement} para completar la colección.`;
 const historical=historicalBadgeCount();
 const stageNote=` Etapa seleccionada: ${learningLevelLabel()}.`+(historical?` Conservas ${historical} ${historical===1?"pintadera histórica que todavía no cumple":"pintaderas históricas que todavía no cumplen"} los requisitos de esta etapa.`:"");
 byId("passportDialogStatus").textContent+=stageNote;
 const notice=byId("badgeStageNotice");if(notice){notice.textContent=stageNote.trim();notice.hidden=false;}
 document.querySelectorAll(".island-card").forEach(card=>card.classList.toggle("done",badgeCountsForLevel(card.dataset.route)));
 document.querySelectorAll(".route").forEach(section=>{
  const id=section.id.replace("route-","");
  section.querySelector(".source-step")?.classList.toggle("complete",sourcePassed.has(id));
  section.querySelector(".truth-step")?.classList.toggle("complete",truthPassed.has(id));
  section.querySelector(".badge-step")?.classList.toggle("complete",badgeCountsForLevel(id));
  section.querySelector(".reward")?.classList.toggle("show",badgeCountsForLevel(id));
  const sourceStatus=section.querySelector(".source-status");
  const truthStatus=section.querySelector(".quiz-status");
  if(sourcePassed.has(id)&&sourceStatus&&!sourceStatus.textContent)sourceStatus.textContent="Reto superado en esta sesión.";
  if(truthPassed.has(id)&&truthStatus&&!truthStatus.textContent)truthStatus.textContent="Reto superado en esta sesión.";
 });
 const unlocked=count===routes.length;
 byId("finalContent").classList.toggle("unlocked",unlocked);
 byId("finalLock").hidden=unlocked;
 updateFinalExperience();updateItineraryUI();window.MitoMapaExplorer?.refresh();window.MitoMapaRouteFlow?.refresh();
}
function showRoute(id,options={}){
 if(!validIds.has(id))return;
 if(narrationState.routeId&&narrationState.routeId!==id)stopNarration("Lectura detenida al cambiar de isla.");
 document.querySelectorAll(".route").forEach(element=>element.classList.remove("active"));
 const step=window.MitoMapaNavigation?.activateRoute(id,options);
 const section=ensureRoute(id);if(!section)return;
 section.classList.add("active");
 window.MitoMapaRouteFlow?.showStep(section,step||"cuento",{focus:false,notify:false});
 lastRouteId=id;savePreferences();
 const resume=byId("resumeRoute");if(resume)resume.disabled=false;
 const reduced=window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
 section.scrollIntoView({behavior:reduced?"auto":"smooth",block:"start"});
 const heading=section.querySelector("h2");if(heading){heading.setAttribute("tabindex","-1");heading.focus({preventScroll:true});}
}
function showPassport(){updateProgress();openDialog(byId("passportDialog"));}
function returnToExploreMap(){
 if(window.MitoMapaNavigation){window.MitoMapaNavigation.go("islas");return;}
 stopNarration();
 const map=byId("exploreMap")||byId("islandGrid");if(!map)return;
 const reduced=window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
 map.scrollIntoView({behavior:reduced?"auto":"smooth",block:"start"});
 const heading=map.querySelector("h2")||map;heading.setAttribute("tabindex","-1");heading.focus({preventScroll:true});
}
function tryAward(id){
 if(!badgeRequirementsMet(id))return false;
 const wasNew=!earned.has(id);
 earned.add(id);save();updateProgress();
 if(wasNew){
  const route=routes.find(item=>item.id===id);
  byId("dialogBadge").src=`${ASSETS[route.badge]}`;
  byId("dialogBadge").alt=route.badgeName;
  byId("dialogTitle").textContent=route.badgeName;
  byId("dialogText").textContent=`La insignia de ${route.island} se ha añadido automáticamente a tu pasaporte. Llevas ${currentBadgeCount()} de 8. Recuerda completar también las actividades que te haya indicado tu docente.`;
  openDialog(byId("badgeDialog"));
 }
 return true;
}
function enhanceQuizStepper(quiz){
 const questions=[...quiz.querySelectorAll(".question")];if(!questions.length)return;
 quiz.classList.add("quiz-stepper");
 const checkButton=quiz.querySelector(".check-source,.check-quiz");
 const nav=document.createElement("div");nav.className="question-nav";
 nav.innerHTML=`<button class="text-button question-prev" type="button">← Anterior</button><span class="question-counter" aria-live="polite"></span><button class="text-button question-next" type="button">Siguiente →</button><span class="question-dots" aria-hidden="true"></span>`;
 checkButton.before(nav);let current=0;
 const show=(index,{focus=false}={})=>{
  current=Math.max(0,Math.min(index,questions.length-1));
  questions.forEach((question,questionIndex)=>question.classList.toggle("current",questionIndex===current));
  nav.querySelector(".question-prev").disabled=current===0;
  nav.querySelector(".question-next").disabled=current===questions.length-1;
  nav.querySelector(".question-counter").textContent=`Pregunta ${current+1} de ${questions.length}`;
  nav.querySelector(".question-dots").innerHTML=questions.map((question,questionIndex)=>`<span class="${question.querySelector("input:checked")?"answered":""} ${questionIndex===current?"current":""}"></span>`).join("");
  if(focus){
   const question=questions[current],target=question.querySelector("legend")||question.querySelector("input");
   if(target){if(target.tagName==="LEGEND")target.tabIndex=-1;target.focus({preventScroll:true});}
   question.scrollIntoView({block:"nearest",behavior:"auto"});
  }
 };
 quiz._showQuestion=show;
 nav.querySelector(".question-prev").addEventListener("click",()=>show(current-1,{focus:true}));
 nav.querySelector(".question-next").addEventListener("click",()=>show(current+1,{focus:true}));
 quiz.querySelectorAll("input").forEach(input=>input.addEventListener("change",()=>show(current)));
 show(0);
}
// Comprueba los contenedores completos antes de que el navegador decodifique un dibujo.
const drawingLimits=Object.freeze({width:900,height:520,pixels:900*520,characters:2500000});
function drawingImageSize(value){
 if(typeof value!=="string"||value.length>drawingLimits.characters)return null;
 const prefix=/^data:image\/(png|webp);base64,/i.exec(value);if(!prefix)return null;
 const encoded=value.slice(prefix[0].length);
 if(!encoded.length||encoded.length%4||!/^[A-Za-z0-9+/]+={0,2}$/.test(encoded))return null;
 let bytes;try{bytes=Uint8Array.from(atob(encoded),character=>character.charCodeAt(0));}catch(error){return null;}
 const view=new DataView(bytes.buffer),tag=offset=>String.fromCharCode(...bytes.subarray(offset,offset+4));
 const bounded=(width,height)=>width>0&&height>0&&width<=drawingLimits.width&&height<=drawingLimits.height&&width*height<=drawingLimits.pixels;
 if(prefix[1].toLowerCase()==="png"){
  if(bytes.length<45||![137,80,78,71,13,10,26,10].every((byte,i)=>bytes[i]===byte))return null;
  let offset=8,width=0,height=0,hasData=false,dataEnded=false,chunks=0;
  const allowed=new Set(["IHDR","PLTE","tRNS","IDAT","IEND","gAMA","cHRM","sRGB","pHYs"]);
  while(offset<bytes.length){
   if(++chunks>4096||bytes.length-offset<12)return null;
   const size=view.getUint32(offset),type=tag(offset+4),end=offset+12+size;
   if(end>bytes.length||!allowed.has(type))return null;
   // Una cabecera con CRC incorrecto tampoco puede llegar al decodificador.
   let crc=0xffffffff;
   for(let i=offset+4;i<offset+8+size;i++){crc^=bytes[i];for(let bit=0;bit<8;bit++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}
   if(((crc^0xffffffff)>>>0)!==view.getUint32(offset+8+size))return null;
   if(type==="IHDR"){
    if(offset!==8||size!==13)return null;
    width=view.getUint32(offset+8);height=view.getUint32(offset+12);
    const depth=bytes[offset+16],color=bytes[offset+17],depths={0:[1,2,4,8,16],2:[8,16],3:[1,2,4,8],4:[8,16],6:[8,16]};
    if(!bounded(width,height)||!depths[color]?.includes(depth)||bytes[offset+18]||bytes[offset+19]||bytes[offset+20]>1)return null;
   }else if(!width)return null;
   if(type==="IDAT"){if(dataEnded)return null;hasData=hasData||size>0;}
   else if(hasData)dataEnded=true;
   if(type==="IEND")return size===0&&hasData&&end===bytes.length?{width,height}:null;
   offset=end;
  }
  return null;
 }
 if(bytes.length<20||tag(0)!=="RIFF"||tag(8)!=="WEBP"||view.getUint32(4,true)+8!==bytes.length)return null;
 let offset=12,extended=null,raster=null,alpha=false,profile=false,chunks=0;
 while(offset<bytes.length){
  if(++chunks>16||bytes.length-offset<8)return null;
  const type=tag(offset),size=view.getUint32(offset+4,true),start=offset+8,end=start+size,next=end+(size&1);
  if(next>bytes.length||(size&1)&&bytes[end]!==0)return null;
  if(type==="VP8X"){
   if(offset!==12||size!==10||extended||bytes[start]&~0x30||bytes[start+1]||bytes[start+2]||bytes[start+3])return null;
   const width=1+bytes[start+4]+bytes[start+5]*256+bytes[start+6]*65536,height=1+bytes[start+7]+bytes[start+8]*256+bytes[start+9]*65536;
   if(!bounded(width,height))return null;
   extended={width,height,alpha:Boolean(bytes[start]&0x10),profile:Boolean(bytes[start]&0x20)};
  }else if(type==="ICCP"){
   // Chromium incluye este perfil sin compresión en sus propios lienzos WebP.
   if(!extended?.profile||profile||alpha||raster||size<132||size>4096||view.getUint32(start)!==size||tag(start+36)!=="acsp")return null;
   const entries=view.getUint32(start+128),tableEnd=132+entries*12;
   if(entries>64||tableEnd>size)return null;
   for(let i=0;i<entries;i++){
    const entry=start+132+i*12,position=view.getUint32(entry+4),length=view.getUint32(entry+8);
    if(position<tableEnd||length<8||position+length>size)return null;
   }
   profile=true;
  }else if(type==="ALPH"){
   if(!extended?.alpha||alpha||raster||size<1||(bytes[start]&3)>1||bytes[start]>>>6||(bytes[start]>>4&3)>1)return null;
   if((bytes[start]&3)===0&&size!==1+extended.width*extended.height)return null;
   alpha=true;
  }else if(type==="VP8 "||type==="VP8L"){
   if(raster||size<(type==="VP8 "?10:5))return null;
   let width,height;
   if(type==="VP8 "){
    if(bytes[start]&1||bytes[start+3]!==157||bytes[start+4]!==1||bytes[start+5]!==42)return null;
    width=view.getUint16(start+6,true)&0x3fff;height=view.getUint16(start+8,true)&0x3fff;
    if(extended&&extended.alpha!==alpha)return null;
   }else{
    if(alpha||bytes[start]!==47)return null;
    const bits=view.getUint32(start+1,true);if(bits>>>29)return null;
    width=1+(bits&0x3fff);height=1+(bits>>>14&0x3fff);
   }
   if(!bounded(width,height)||extended&&(width!==extended.width||height!==extended.height))return null;
   raster={width,height};
  }else return null; // Animaciones y metadatos ajenos al lienzo no se aceptan.
  offset=next;
 }
 return profile===Boolean(extended?.profile)?raster:null;
}
function safeWorkshopDrawing(value){return drawingImageSize(value)?value:null;}
function removeUnsafeWorkshopDrawings(state){
 let changed=false;
 for(const item of Object.values(state.routes)){
  if(!item||typeof item!=="object"||item.drawing==null)continue;
  const drawing=safeWorkshopDrawing(item.drawing);
  if(drawing!==item.drawing){item.drawing=drawing;item.drawingHasInk=false;if(String(item.text||"").trim().length<3)item.creation=false;changed=true;}
 }
 return changed;
}
function loadWorkshopDrawing(value){
 const size=drawingImageSize(value);if(!size)return Promise.resolve(null);
 return new Promise(resolve=>{
  const image=new Image();
  image.onload=async()=>{try{if(typeof image.decode==="function")await image.decode();resolve(image.naturalWidth===size.width&&image.naturalHeight===size.height?image:null);}catch(error){resolve(null);}};
  image.onerror=()=>resolve(null);
  image.src=value;
 });
}
async function normalizeImportedDrawings(clean){
 for(const item of Object.values(clean.routes)){
  if(!item.drawing)continue;
  const image=await loadWorkshopDrawing(item.drawing);if(!image)throw new Error("DRAWING_INVALID");
  const canvas=document.createElement("canvas");canvas.width=drawingLimits.width;canvas.height=drawingLimits.height;
  const context=canvas.getContext("2d");if(!context)throw new Error("DRAWING_INVALID");
  context.fillStyle="#fffdf7";context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0,canvas.width,canvas.height);
  item.drawing=safeWorkshopDrawing(canvas.toDataURL("image/webp",.82));
  if(!item.drawing)throw new Error("DRAWING_INVALID");
 }
 return clean;
}
const workshopStorageKey="mitomapa-canario-cuaderno-v1";
let workshopState=readJSON(workshopStorageKey,{routes:{}});
if(!workshopState||typeof workshopState!=="object")workshopState={routes:{}};
if(!workshopState.routes||typeof workshopState.routes!=="object")workshopState.routes={};
if(removeUnsafeWorkshopDrawings(workshopState))writeJSON(workshopStorageKey,workshopState);

function activityEscape(value){
 return String(value??"").replace(/[&<>"']/g,character=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[character]);
}
function activityNormalize(value){
 return String(value??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[¿?¡!.,;:«»"']/g,"").replace(/\s+/g," ").trim();
}
const creationReviewCommon=Object.freeze([
 {id:"relation",text:"Se relaciona con el cuento"},
 {id:"communication",text:"Comunica una idea en el formato acordado"},
 {id:"improvement",text:"He revisado una mejora con ayuda"}
]);
const creationReviewOptions=Object.freeze([
 ["pending","Pendiente"],["reviewed","Revisado"],["in_progress","En proceso"],["not_applicable","No procede"]
]);
const creationReviewIds=new Set([...creationReviewCommon.map(item=>item.id),"genre_0","genre_1","genre_2","genre_3"]);
function sanitizeCreationReview(raw){
 const clean={};
 for(const level of itineraryLevels){
  clean[level]={};
  for(const [id,value] of Object.entries(raw?.[level]&&typeof raw[level]==="object"?raw[level]:{})){
   if(creationReviewIds.has(id)&&creationReviewOptions.some(option=>option[0]===value))clean[level][id]=value;
  }
 }
 return clean;
}
function creationReviewCriteria(routeId,level=learningLevel){
 const common=creationReviewCommon.map(item=>({...item}));
 if(level!=="secondary")return common;
 const genre=(secondaryCreations[routeId]?.criteria||[]).map((text,index)=>({id:`genre_${index}`,text:routeId==="fuerteventura"&&index===3?"Si se acordó un texto escrito, respeta la extensión pactada y está revisado.":text}));
 return common.concat(genre);
}
function creationReviewResult(state,routeId,level=learningLevel){
 const values=state.creationReviewV1?.[level]||{},criteria=creationReviewCriteria(routeId,level);
 const applicable=criteria.filter(item=>values[item.id]!=="not_applicable");
 const reviewed=applicable.filter(item=>values[item.id]==="reviewed").length;
 return{total:applicable.length,reviewed,excluded:criteria.length-applicable.length,complete:applicable.length>0&&reviewed===applicable.length};
}
function creationReviewSummaryText(result){
 return result.total?`${result.reviewed}/${result.total} criterios revisados${result.excluded?`; ${result.excluded} no procede`:""}. La lista orienta la revisión; no genera puntos ni una calificación.`:"No hay criterios aplicables en esta lista. Confirma con tu docente qué revisión se ha acordado; no genera puntos ni una calificación.";
}
function workshopCreationReviewMarkup(routeId,state){
 const criteria=creationReviewCriteria(routeId),values=state.creationReviewV1?.[learningLevel]||{};
 const row=item=>{
  const labelId=`creation-review-label-${routeId}-${learningLevel}-${item.id}`,value=values[item.id]||"pending";
  return `<label class="creation-review-row"><span id="${labelId}">${activityEscape(item.text)}</span><select data-creation-review="${item.id}" data-creation-review-level="${learningLevel}" aria-labelledby="${labelId}">${creationReviewOptions.map(([key,label])=>`<option value="${key}"${key===value?" selected":""}>${label}</option>`).join("")}</select></label>`;
 };
 const genre=learningLevel==="secondary"?`<div class="creation-review-genre"><h5>SOLO Secundaria · Género acordado</h5><p>Marca «No procede» cuando el criterio no corresponde al formato oral, gráfico u otro formato acordado.</p>${criteria.slice(3).map(row).join("")}</div>`:"";
 const optional=learningLevel==="early"?"En Infantil y 1.º ciclo, esta lista es opcional: puedes conversar sobre tu creación con ayuda. No añade un requisito para participar.":"Esta lista es opcional: elige con tu docente los criterios que vas a revisar. Puedes compartir una creación «En proceso» para recibir ayuda. La preparación y la revisión se registran por separado; usa «No procede» cuando un criterio no se haya acordado.";
 const previousPrepared=itineraryFor(routeId).evidenceMode==="external"?itineraryFor(routeId).externalCreation:learningLevel==="secondary"?state.secondaryCreation:state.creation;
 const previous=previousPrepared&&!Object.keys(values).length?"<p class=\"creation-review-prior\">Tu borrador y la preparación anterior se conservan. Los estados de esta lista nueva empiezan pendientes y no sustituyen esa preparación. Revísalos con ayuda cuando se acuerde.</p>":"";
 return `<fieldset class="creation-review"><legend>Revisión de la creación · ${learningLevel==="secondary"?"Secundaria":learningLevel==="early"?"Infantil y 1.º ciclo":"Primaria"}</legend><p>${optional}</p>${criteria.slice(0,3).map(row).join("")}${genre}${previous}<p class="creation-review-summary" role="status" aria-live="polite" aria-atomic="true">${creationReviewSummaryText(creationReviewResult(state,routeId))}</p></fieldset>`;
}
function refreshCreationReview(workshop,routeId){
 const container=workshop.querySelector("[data-creation-review-container]");
 if(container)container.innerHTML=workshopCreationReviewMarkup(routeId,getWorkshopRouteState(routeId));
}
function updateCreationReviewSummary(workshop,routeId){
 const summary=workshop.querySelector(".creation-review-summary");
 if(summary)summary.textContent=creationReviewSummaryText(creationReviewResult(getWorkshopRouteState(routeId),routeId));
}
function invalidateCreationReview(state,track){
 let changed=false;
 for(const level of itineraryLevels){
  if((level==="secondary")!==(track==="secondary"))continue;
  for(const id of Object.keys(state.creationReviewV1?.[level]||{})){
   if(state.creationReviewV1[level][id]==="reviewed"){state.creationReviewV1[level][id]="in_progress";changed=true;}
  }
 }
 return changed;
}
function refreshCreationReviewAfterEdit(workshop,routeId,state,track){
 if(invalidateCreationReview(state,track))refreshCreationReview(workshop,routeId);
}
function getWorkshopRouteState(routeId){
 if(!workshopState.routes[routeId]||typeof workshopState.routes[routeId]!=="object")workshopState.routes[routeId]={};
 const state=workshopState.routes[routeId];
 state.words=Boolean(state.words);state.research=Boolean(state.research);state.creation=Boolean(state.creation);
 state.text=String(state.text||"").slice(0,500);
 state.wordResponses=state.wordResponses&&typeof state.wordResponses==="object"?state.wordResponses:{match:[],fill:[]};
 state.researchResponses=Array.isArray(state.researchResponses)?state.researchResponses:[];
 state.researchEvidence=String(state.researchEvidence||"").slice(0,600);
 state.drawing=safeWorkshopDrawing(state.drawing);state.drawingHasInk=Boolean(state.drawingHasInk&&state.drawing);
 state.secondaryCreation=Boolean(state.secondaryCreation);
 state.secondaryText=String(state.secondaryText||"").slice(0,5000);
 state.secondaryChoice=String(state.secondaryChoice||"").slice(0,180);
 state.secondaryChecks=Array.isArray(state.secondaryChecks)?state.secondaryChecks.slice(0,4).map(Boolean):[];
 while(state.secondaryChecks.length<4)state.secondaryChecks.push(false);
 state.creationReviewV1=sanitizeCreationReview(state.creationReviewV1);
 return state;
}
function saveWorkshopState(){
 return writeJSON(workshopStorageKey,workshopState);
}
function workshopMatchMarkup(routeId,match){
 if(!match?.items?.length)return"";
 const options=match.options.map(option=>`<option value="${activityEscape(option)}">${activityEscape(option)}</option>`).join("");
 return `<div class="activity-block"><h5>${activityEscape(match.prompt)}</h5><div class="activity-match-grid">${match.items.map((item,index)=>`<label class="activity-match-row"><span id="activity-match-label-${routeId}-${index}">${activityEscape(item.definition)}</span><select data-activity-match data-answer="${activityEscape(item.answer)}" aria-labelledby="activity-match-label-${routeId}-${index}"><option value="">Elige un término</option>${options}</select><small class="activity-item-feedback" aria-live="polite"></small></label>`).join("")}</div></div>`;
}
function workshopFillMarkup(words){
 if(!words.fills?.length)return"";
 return `<div class="activity-block"><h5>${activityEscape(words.fillPrompt)}</h5><div class="activity-fill-grid">${words.fills.map((item,index)=>`<label class="activity-fill-row"><span><strong>${index+1}.</strong> ${activityEscape(item.prompt)}</span><input type="text" autocomplete="off" spellcheck="false" data-activity-fill data-answers="${activityEscape(item.answers.join("|"))}" data-hint="${activityEscape(item.hint||"")}" aria-label="Respuesta para ${activityEscape(item.prompt)}"><small class="activity-item-feedback" aria-live="polite"></small></label>`).join("")}</div></div>`;
}
function workshopResearchMarkup(routeId,research){
 const questions=research.questions.map((question,index)=>`<fieldset class="activity-research-question" data-answer="${question.answer}"><legend>${index+1}. ${activityEscape(question.q)}</legend><div class="activity-choice-grid">${question.options.map((option,optionIndex)=>`<label><input type="radio" name="activity-${routeId}-research-${index}" value="${optionIndex}"><span>${activityEscape(option)}</span></label>`).join("")}</div><p class="activity-item-feedback" aria-live="polite"></p><p class="activity-answer-note" hidden>${activityEscape(question.feedback)}</p></fieldset>`).join("");
 const sources=research.sources?.length?`<details class="activity-sources"><summary>Fuentes para seguir investigando</summary><ul>${research.sources.map(source=>`<li><a href="${activityEscape(source.url)}" target="_blank" rel="noopener noreferrer">${activityEscape(source.label)}</a></li>`).join("")}</ul></details>`:"";
 return `<div class="activity-panel" id="activity-${routeId}-research" role="tabpanel" aria-labelledby="activity-tab-${routeId}-research" data-activity-panel="research" hidden><h4>${activityEscape(research.title)}</h4><p>${activityEscape(research.intro)}</p>${questions}<button class="button activity-check-research" type="button">Comprobar la investigación</button><p class="activity-panel-status" role="status" aria-live="polite"></p>${sources}<p class="activity-tip">La comprobación reconoce estas dos respuestas. Completa además la investigación y el contraste de fuentes que te haya indicado tu docente.</p><label class="activity-text-label"><span>Mi fuente y lo que he comprobado (opcional)</span><textarea rows="3" maxlength="600" data-research-evidence placeholder="Anota el título o enlace de una fuente y un dato que hayas contrastado."></textarea></label><p class="research-draft-status" role="status"></p></div>`;
}
function workshopPrimaryCreationMarkup(routeId,creation,state){
 const textValue=activityEscape(state.text||"");
 if(creation.type==="drawing"){
  return `<div class="creation-version creation-primary" data-creation-version="primary"><p class="creation-stage-label">Propuesta para Primaria</p><h4>${activityEscape(creation.title)}</h4><p>${activityEscape(creation.prompt)}</p><p class="activity-tip">${activityEscape(creation.tip)}</p><div class="drawing-toolbar" aria-label="Herramientas de dibujo"><span>Color</span><button type="button" class="draw-color is-selected" data-draw-color="#2f2b26" style="--draw-color:#2f2b26" aria-label="Negro" aria-pressed="true"></button><button type="button" class="draw-color" data-draw-color="#9b5738" style="--draw-color:#9b5738" aria-label="Barro" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#dfb94f" style="--draw-color:#dfb94f" aria-label="Amarillo" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#72a4aa" style="--draw-color:#72a4aa" aria-label="Azul claro" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#829276" style="--draw-color:#829276" aria-label="Verde" aria-pressed="false"></button><label>Grosor <input class="draw-size" type="range" min="2" max="24" value="7" aria-label="Grosor del trazo"></label></div><div class="drawing-frame"><canvas class="activity-canvas" width="900" height="520" role="img" aria-label="Lienzo para dibujar al tibicena. Hay una alternativa de descripción escrita bajo el lienzo."></canvas></div><div class="drawing-actions"><button class="text-button draw-undo" type="button">Deshacer</button><button class="text-button draw-clear" type="button">Borrar dibujo</button><button class="text-button draw-download" type="button">Guardar imagen</button></div><label class="activity-text-label"><span>Alternativa escrita</span><textarea maxlength="500" rows="4" data-primary-text placeholder="${activityEscape(creation.placeholder)}">${textValue}</textarea><small><span class="activity-character-count">${textValue.length}</span>/500 caracteres</small></label></div>`;
 }
 return `<div class="creation-version creation-primary" data-creation-version="primary"><p class="creation-stage-label">Propuesta para Primaria</p><h4>${activityEscape(creation.title)}</h4><p>${activityEscape(creation.prompt)}</p><p class="activity-tip">${activityEscape(creation.tip)}</p><label class="activity-text-label"><span>Tu creación</span><textarea maxlength="500" rows="4" data-primary-text placeholder="${activityEscape(creation.placeholder)}">${textValue}</textarea><small><span class="activity-character-count">${textValue.length}</span>/500 caracteres</small></label></div>`;
}
function workshopSecondaryCreationMarkup(routeId,secondary,state){
 const textValue=activityEscape(state.secondaryText||"");
 const choices=secondary.choices?.length?`<fieldset class="secondary-scene-choice"><legend>Elige una escena</legend>${secondary.choices.map((choice,index)=>`<label><input type="radio" name="secondary-scene-${routeId}" data-secondary-choice value="${activityEscape(choice)}" ${state.secondaryChoice===choice?"checked":""}><span>${index+1}. ${activityEscape(choice)}</span></label>`).join("")}</fieldset>`:"";
 const structure=`<section class="secondary-brief" aria-labelledby="secondary-structure-${routeId}"><h5 id="secondary-structure-${routeId}">Estructura de apoyo</h5><ol>${secondary.structure.map(item=>`<li>${activityEscape(item)}</li>`).join("")}</ol></section>`;
 const words=workshopWordCount(state.secondaryText||"");
 return `<div class="creation-version creation-secondary" data-creation-version="secondary"><p class="creation-stage-label">Crea · Ruta ${secondary.route} · Secundaria</p><h4>${activityEscape(secondary.title)}</h4><p>${activityEscape(secondary.prompt)}</p>${choices}${structure}<label class="activity-text-label secondary-text-label"><span>Tu producción</span><textarea maxlength="5000" rows="12" data-secondary-text placeholder="${activityEscape(secondary.placeholder)}">${textValue}</textarea><small><span class="activity-word-count">${words}</span> palabras · <span class="activity-character-count">${textValue.length}</span>/5000 caracteres</small></label><p class="secondary-length-note">${activityEscape(secondary.lengthLabel)}</p></div>`;
}
function workshopCreationMarkup(routeId,creation,secondary,state){
 return `<div class="activity-panel" id="activity-${routeId}-creation" role="tabpanel" aria-labelledby="activity-tab-${routeId}-creation" data-activity-panel="creation" hidden>${workshopPrimaryCreationMarkup(routeId,creation,state)}${workshopSecondaryCreationMarkup(routeId,secondary,state)}<p class="external-creation-note" hidden></p><div data-creation-review-container>${workshopCreationReviewMarkup(routeId,state)}</div><button class="button activity-save-creation" data-creation-track="${learningLevel==="secondary"?"secondary":"primary"}" type="button">${learningLevel==="secondary"?"Marcar propuesta como preparada":"Marcar creación como preparada"}</button><p class="draft-status" role="status" aria-live="polite"></p><div class="drawing-actions"><button class="text-button activity-download-draft" type="button">Descargar mi borrador</button></div><p class="activity-panel-status" role="status" aria-live="polite"></p></div>`;
}
function workshopMarkup(route,activity){
 const state=getWorkshopRouteState(route.id);
 return `<section class="activity-workshop" id="activity-${route.id}" aria-labelledby="activity-title-${route.id}"><div class="activity-workshop-head"><div><p class="challenge-kicker">Actividad complementaria · Infantil, Primaria y Secundaria</p><h3 id="activity-title-${route.id}">Cuaderno activo de ${activityEscape(route.island)}</h3><p>Explora vocabulario, contrasta información y crea. En Secundaria, el apartado «Crea» propone un género discursivo diferente en cada ruta. Esta parte no bloquea la pintadera.</p></div><span class="activity-workshop-progress" role="status" aria-live="polite">0/3</span></div><div class="activity-tabs" role="tablist" aria-label="Apartados del cuaderno"><button id="activity-tab-${route.id}-words" type="button" role="tab" aria-selected="true" aria-controls="activity-${route.id}-words" data-activity-tab="words">1. Vocabulario</button><button id="activity-tab-${route.id}-research" type="button" role="tab" aria-selected="false" aria-controls="activity-${route.id}-research" data-activity-tab="research" tabindex="-1">2. Investiga</button><button id="activity-tab-${route.id}-creation" type="button" role="tab" aria-selected="false" aria-controls="activity-${route.id}-creation" data-activity-tab="creation" tabindex="-1">3. Crea</button></div><div class="activity-panel" id="activity-${route.id}-words" role="tabpanel" aria-labelledby="activity-tab-${route.id}-words" data-activity-panel="words"><h4>${activityEscape(activity.words.title)}</h4><p>${activityEscape(activity.words.intro)}</p>${workshopMatchMarkup(route.id,activity.words.match)}${workshopFillMarkup(activity.words)}<button class="button activity-check-words" type="button">Comprobar el vocabulario</button><p class="activity-panel-status" role="status" aria-live="polite"></p></div>${workshopResearchMarkup(route.id,activity.research)}${workshopCreationMarkup(route.id,activity.creation,secondaryCreations[route.id],state)}</section>`;
}
function activateWorkshopPanel(workshop,name,focus=false){
 const tabs=[...workshop.querySelectorAll("[data-activity-tab]")];
 if(!tabs.some(tab=>!tab.hidden&&tab.dataset.activityTab===name))name=tabs.find(tab=>!tab.hidden)?.dataset.activityTab;
 tabs.forEach(tab=>{const active=!tab.hidden&&tab.dataset.activityTab===name;tab.setAttribute("aria-selected",String(active));tab.tabIndex=active?0:-1;if(active&&focus)tab.focus();});
 workshop.querySelectorAll("[data-activity-panel]").forEach(panel=>panel.hidden=panel.dataset.activityPanel!==name);
}
function setActivityItemResult(container,kind,message){
 container.classList.remove("is-correct","is-wrong","is-missing");
 if(kind)container.classList.add(`is-${kind}`);
 const feedback=container.querySelector(".activity-item-feedback");
 if(feedback)feedback.textContent=message;
}
function workshopCreationComplete(state,id){
 const prepared=id&&itineraryFor(id).evidenceMode==="external"?Boolean(itineraryFor(id).externalCreation):learningLevel==="secondary"?Boolean(state.secondaryCreation):Boolean(state.creation);
 return prepared;
}
function showDraftStatus(id,ok,zone="creation"){
 const workshop=byId(`activity-${id}`),status=workshop?.querySelector(zone==="research"?".research-draft-status":".draft-status");
 if(status)status.textContent=ok?"Borrador guardado automáticamente en este navegador.":"El borrador sigue en pantalla, pero no se ha podido guardar. Descarga una copia antes de salir.";
}
function downloadWorkshopDraft(id){
 const state=getWorkshopRouteState(id),route=routes.find(r=>r.id===id);
 const text=`MitoMapa ${RESOURCE_VERSION} · ${route.island} · ${learningLevelLabel()}\nVersión del esquema de exportación: ${EXPORT_SCHEMA_VERSION}\n\nCREACIÓN\n${learningLevel==="secondary"?state.secondaryText:state.text}\n\nFUENTE Y CONTRASTE\n${state.researchEvidence}\n\nBorrador personal; requiere revisión con el docente.`;
 downloadLocalText(text,`borrador-mitomapa-${id}.txt`,"text/plain");
}
function downloadLocalText(content,filename,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function updateWorkshopSummary(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const state=getWorkshopRouteState(routeId),creationDone=workshopCreationComplete(state,routeId),selected=selectedNotebookTasks(routeId),completion=notebookCompletion(routeId);
 const completed=selected.filter(key=>completion[key]).length,total=selected.length;
 const progress=workshop.querySelector(".activity-workshop-progress");
 progress.textContent=total?`${completed}/${total} tareas asignadas`:"Sin tareas de cuaderno asignadas";
 progress.classList.toggle("is-complete",total>0&&completed===total);
 updateCreationReviewSummary(workshop,routeId);
 Object.keys(completion).forEach(key=>workshop.querySelector(`[data-activity-tab="${key}"]`)?.classList.toggle("is-complete",completion[key]));
 if(state.words)workshop.querySelector('[data-activity-panel="words"] .activity-panel-status').textContent="Comprobación de vocabulario superada.";
 if(state.research)workshop.querySelector('[data-activity-panel="research"] .activity-panel-status').textContent="Comprobación de investigación superada. Revisa también las fuentes y las tareas acordadas.";
 const status=workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status');
 if(status)status.textContent=creationDone?(itineraryFor(routeId).evidenceMode==="external"?"Producción externa revisada y registrada manualmente por tu docente.":"Creación marcada como preparada para compartir con tu docente. No es una calificación automática."):"Creación pendiente de preparar y revisar.";
}
function checkWorkshopWords(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const panel=workshop.querySelector('[data-activity-panel="words"]');
 let total=0,correct=0,missing=0;
 panel.querySelectorAll(".activity-match-row").forEach(row=>{
  total++;const select=row.querySelector("select"),value=select.value;
  if(!value){missing++;setActivityItemResult(row,"missing","Elige un término.");return;}
  const ok=value===select.dataset.answer;if(ok)correct++;
  setActivityItemResult(row,ok?"correct":"wrong",ok?"¡Bien!":"Revisa el cuento y prueba otra vez.");
 });
 panel.querySelectorAll(".activity-fill-row").forEach(row=>{
  total++;const input=row.querySelector("input"),value=activityNormalize(input.value);
  if(!value){missing++;input.setAttribute("aria-invalid","true");setActivityItemResult(row,"missing","Escribe una respuesta.");return;}
  const accepted=input.dataset.answers.split("|").map(activityNormalize),ok=accepted.includes(value);
  input.setAttribute("aria-invalid",String(!ok));if(ok)correct++;
  setActivityItemResult(row,ok?"correct":"wrong",ok?"¡Encontrada!":input.dataset.hint||"Vuelve al cuento y busca una pista.");
 });
 const status=panel.querySelector(".activity-panel-status");
 if(missing){status.textContent=`Faltan ${missing} ${missing===1?"respuesta":"respuestas"}.`;return;}
 if(correct===total){const state=getWorkshopRouteState(routeId);state.words=true;const ok=saveWorkshopState();if(!ok)status.textContent="Actividad superada en pantalla; descarga el seguimiento para conservarla.";status.textContent=`Resultado: ${correct} de ${total}. Actividad superada.`;updateWorkshopSummary(routeId);}
 else status.textContent=`Resultado: ${correct} de ${total}. Revisa las pistas e inténtalo de nuevo.`;
}
function checkWorkshopResearch(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const panel=workshop.querySelector('[data-activity-panel="research"]');
 const questions=[...panel.querySelectorAll(".activity-research-question")];
 let correct=0,missing=0;
 questions.forEach(question=>{
  const checked=question.querySelector("input:checked");
  if(!checked){missing++;setActivityItemResult(question,"missing","Selecciona una respuesta.");return;}
  const ok=Number(checked.value)===Number(question.dataset.answer);if(ok)correct++;
  const explanation=question.querySelector(".activity-answer-note").textContent;
  setActivityItemResult(question,ok?"correct":"wrong",`${ok?"¡Bien!":"Todavía no."} ${explanation}`);
 });
 const status=panel.querySelector(".activity-panel-status");
 if(missing){status.textContent=`Faltan ${missing} ${missing===1?"respuesta":"respuestas"}.`;return;}
 if(correct===questions.length){const state=getWorkshopRouteState(routeId);state.research=true;const ok=saveWorkshopState();if(!ok)status.textContent="Comprobación superada en pantalla; descarga el seguimiento para conservarla.";status.textContent=`Resultado: ${correct} de ${questions.length}. Investigación superada.`;updateWorkshopSummary(routeId);}
 else status.textContent=`Resultado: ${correct} de ${questions.length}. Lee la explicación y vuelve a intentarlo.`;
}
function workshopWordCount(value){const clean=String(value||"").trim();return clean?clean.split(/\s+/).length:0;}
function updateCreationCounter(container){
 container?.querySelectorAll("textarea").forEach(textarea=>{
  const label=textarea.closest(".activity-text-label"),characters=label?.querySelector(".activity-character-count"),words=label?.querySelector(".activity-word-count");
  if(characters)characters.textContent=textarea.value.length;if(words)words.textContent=workshopWordCount(textarea.value);
 });
}
function saveWorkshopCreation(routeId,track="primary"){
 const activity=workshopActivities[routeId],secondary=secondaryCreations[routeId],workshop=byId(`activity-${routeId}`);if(!activity||!secondary||!workshop)return;
 const panel=workshop.querySelector('[data-activity-panel="creation"]'),state=getWorkshopRouteState(routeId),status=panel.querySelector(".activity-panel-status");
 if(track==="secondary"){
  const zone=panel.querySelector(".creation-secondary"),textarea=zone.querySelector("textarea");
  state.secondaryText=String(textarea?.value||"").trim().slice(0,5000);
  const words=workshopWordCount(state.secondaryText);
  if(words===0){status.textContent="Escribe tu producción o acuerda una alternativa fuera de la web con tu docente.";return;}
  if(secondary.choices?.length&&!state.secondaryChoice){status.textContent="Elige una de las escenas antes de guardar.";return;}
  if(!itineraryFor(routeId).flexibleLength&&words<secondary.minWords){status.textContent=secondary.minWords>=100?`Tu producción tiene ${words} palabras y necesita al menos ${secondary.minWords}.`:`Desarrolla un poco más tu producción: ahora tiene ${words} palabras.`;return;}
  if(!itineraryFor(routeId).flexibleLength&&secondary.maxWords&&words>secondary.maxWords){status.textContent=`Tu producción tiene ${words} palabras y el máximo es ${secondary.maxWords}. Revisa y sintetiza.`;return;}
  state.secondaryCreation=true;showDraftStatus(routeId,saveWorkshopState());status.textContent=`Propuesta de Secundaria preparada para compartir: ${words} palabras. La revisión de la lista se registra por separado.`;updateWorkshopSummary(routeId);return;
 }
 const zone=panel.querySelector(".creation-primary"),textarea=zone.querySelector("textarea");
 state.text=textarea?.value.trim()||"";
 const hasContent=activity.creation.type==="drawing"?Boolean(state.drawingHasInk||state.text.length>=3):state.text.length>=3;
 if(!hasContent){status.textContent=activity.creation.type==="drawing"?"Haz un dibujo o escribe una descripción antes de guardar.":"Escribe al menos una idea breve antes de guardar.";return;}
 state.creation=true;showDraftStatus(routeId,saveWorkshopState());status.textContent="Creación guardada en este navegador.";updateWorkshopSummary(routeId);
}
function setupWorkshopCanvas(workshop,routeId){
 const canvas=workshop.querySelector(".activity-canvas");if(!canvas)return;
 const context=canvas.getContext("2d");if(!context)return;
 const state=getWorkshopRouteState(routeId),baseColor="#fffdf7";
 let drawing=false,lastPoint=null,currentColor="#2f2b26",history=[];
 const clearSurface=()=>{context.save();context.fillStyle=baseColor;context.fillRect(0,0,canvas.width,canvas.height);context.restore();};
 const restore=async imageData=>{const image=await loadWorkshopDrawing(imageData);clearSurface();if(image)context.drawImage(image,0,0,canvas.width,canvas.height);};
 clearSurface();if(state.drawing)restore(state.drawing);
 const pointFromEvent=event=>{const box=canvas.getBoundingClientRect();return{x:(event.clientX-box.left)*canvas.width/box.width,y:(event.clientY-box.top)*canvas.height/box.height};};
 const snapshot=()=>({image:canvas.toDataURL("image/webp",.82),hasInk:Boolean(state.drawingHasInk)});
 const commitDrawing=()=>{state.drawing=canvas.toDataURL("image/webp",.82);state.drawingHasInk=true;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);};
 canvas.addEventListener("pointerdown",event=>{event.preventDefault();history.push(snapshot());if(history.length>18)history.shift();drawing=true;lastPoint=pointFromEvent(event);canvas.setPointerCapture?.(event.pointerId);context.beginPath();context.moveTo(lastPoint.x,lastPoint.y);});
 canvas.addEventListener("pointermove",event=>{if(!drawing)return;event.preventDefault();const next=pointFromEvent(event);context.strokeStyle=currentColor;context.lineWidth=Number(workshop.querySelector(".draw-size")?.value)||7;context.lineCap="round";context.lineJoin="round";context.lineTo(next.x,next.y);context.stroke();lastPoint=next;});
 const finish=event=>{if(!drawing)return;drawing=false;lastPoint=null;try{canvas.releasePointerCapture?.(event.pointerId);}catch(error){}commitDrawing();};
 canvas.addEventListener("pointerup",finish);canvas.addEventListener("pointercancel",finish);canvas.addEventListener("pointerleave",event=>{if(event.buttons===0)finish(event);});
 workshop.querySelectorAll(".draw-color").forEach(button=>button.addEventListener("click",()=>{currentColor=button.dataset.drawColor;workshop.querySelectorAll(".draw-color").forEach(item=>{const selected=item===button;item.classList.toggle("is-selected",selected);item.setAttribute("aria-pressed",String(selected));});}));
 workshop.querySelector(".draw-undo")?.addEventListener("click",async()=>{const previous=history.pop();if(!previous)return;await restore(previous.image);state.drawing=previous.image;state.drawingHasInk=previous.hasInk;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);});
 workshop.querySelector(".draw-clear")?.addEventListener("click",()=>{history.push(snapshot());clearSurface();state.drawing=null;state.drawingHasInk=false;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status').textContent="Lienzo borrado.";});
 workshop.querySelector(".draw-download")?.addEventListener("click",()=>{const link=document.createElement("a");link.download="tibicena-de-gran-canaria.png";link.href=canvas.toDataURL("image/png");link.click();workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status').textContent="La imagen se ha preparado para guardarla en tu dispositivo.";});
}
function bindWorkshop(section,route){
 const workshop=section.querySelector(`#activity-${route.id}`);if(!workshop)return;
 const tabs=[...workshop.querySelectorAll("[data-activity-tab]")];
 tabs.forEach(tab=>{
  tab.addEventListener("click",()=>activateWorkshopPanel(workshop,tab.dataset.activityTab));
  tab.addEventListener("keydown",event=>{const visible=tabs.filter(t=>!t.hidden),index=visible.indexOf(tab);let next=index;
   if(event.key==="ArrowRight")next=(index+1)%visible.length;else if(event.key==="ArrowLeft")next=(index-1+visible.length)%visible.length;else if(event.key==="Home")next=0;else if(event.key==="End")next=visible.length-1;else return;
   event.preventDefault();activateWorkshopPanel(workshop,visible[next].dataset.activityTab,true);
  });
 });
 workshop.querySelector(".activity-check-words")?.addEventListener("click",()=>checkWorkshopWords(route.id));
 workshop.querySelector(".activity-check-research")?.addEventListener("click",()=>checkWorkshopResearch(route.id));
 workshop.querySelectorAll(".activity-save-creation").forEach(button=>button.addEventListener("click",()=>saveWorkshopCreation(route.id,button.dataset.creationTrack)));
 workshop.querySelector(".activity-download-draft")?.addEventListener("click",()=>downloadWorkshopDraft(route.id));
 const state=getWorkshopRouteState(route.id),panel=workshop.querySelector('[data-activity-panel="creation"]');
 workshop.addEventListener("change",event=>{
  const select=event.target.closest("select[data-creation-review]");
  if(!select||select.dataset.creationReviewLevel!==learningLevel||!creationReviewCriteria(route.id).some(item=>item.id===select.dataset.creationReview)||!creationReviewOptions.some(option=>option[0]===select.value))return;
  state.creationReviewV1[learningLevel][select.dataset.creationReview]=select.value;
  const track=learningLevel==="secondary"?"secondary":"primary";
  invalidateItineraryTask(route.id,"creation",track);
  showDraftStatus(route.id,saveWorkshopState());updateWorkshopSummary(route.id);
 });
 workshop.querySelectorAll("[data-activity-match]").forEach((input,i)=>input.value=String(state.wordResponses.match?.[i]||""));
 workshop.querySelectorAll("[data-activity-fill]").forEach((input,i)=>input.value=String(state.wordResponses.fill?.[i]||""));
 workshop.querySelectorAll(".activity-research-question").forEach((question,i)=>{const value=state.researchResponses[i];if(Number.isInteger(value))question.querySelector(`input[value="${value}"]`)?.setAttribute("checked","");});
 const evidence=workshop.querySelector("[data-research-evidence]");if(evidence)evidence.value=state.researchEvidence;
 workshop.querySelectorAll("textarea").forEach(textarea=>textarea.addEventListener("input",()=>{
  if(textarea.matches("[data-research-evidence]")){state.researchEvidence=textarea.value.slice(0,600);invalidateItineraryTask(route.id,"research");showDraftStatus(route.id,saveWorkshopState(),"research");return;}
  updateCreationCounter(panel);
  if(textarea.matches("[data-secondary-text]")){state.secondaryText=textarea.value.slice(0,5000);state.secondaryCreation=false;refreshCreationReviewAfterEdit(workshop,route.id,state,"secondary");invalidateItineraryTask(route.id,"creation","secondary");}
  if(textarea.matches("[data-primary-text]")){state.text=textarea.value.slice(0,500);state.creation=false;refreshCreationReviewAfterEdit(workshop,route.id,state,"primary");invalidateItineraryTask(route.id,"creation","primary");}
  showDraftStatus(route.id,saveWorkshopState());updateWorkshopSummary(route.id);
 }));
 workshop.querySelectorAll("[data-secondary-choice]").forEach(input=>input.addEventListener("change",()=>{
  if(input.checked)state.secondaryChoice=input.value;
  state.secondaryCreation=false;refreshCreationReviewAfterEdit(workshop,route.id,state,"secondary");invalidateItineraryTask(route.id,"creation","secondary");showDraftStatus(route.id,saveWorkshopState());updateWorkshopSummary(route.id);
 }));
 workshop.querySelectorAll('[data-activity-panel="words"] input,[data-activity-panel="words"] select').forEach(input=>input.addEventListener(input.tagName==="SELECT"?"change":"input",()=>{
  state.wordResponses={match:[...workshop.querySelectorAll("[data-activity-match]")].map(el=>el.value),fill:[...workshop.querySelectorAll("[data-activity-fill]")].map(el=>el.value.slice(0,120))};state.words=false;invalidateItineraryTask(route.id,"words");saveWorkshopState();updateWorkshopSummary(route.id);
  workshop.querySelector('[data-activity-panel="words"] .activity-panel-status').textContent="Respuestas modificadas: vuelve a comprobar el vocabulario.";
 }));
 workshop.querySelectorAll('.activity-research-question input').forEach(input=>input.addEventListener("change",()=>{
  state.researchResponses=[...workshop.querySelectorAll('.activity-research-question')].map(q=>{const chosen=q.querySelector('input:checked');return chosen?Number(chosen.value):null;});state.research=false;invalidateItineraryTask(route.id,"research");saveWorkshopState();updateWorkshopSummary(route.id);
  workshop.querySelector('[data-activity-panel="research"] .activity-panel-status').textContent="Respuestas modificadas: vuelve a comprobar la investigación.";
 }));
 setupWorkshopCanvas(workshop,route.id);updateCreationCounter(panel);updateWorkshopSummary(route.id);
}
function injectWorkshop(section,route){
 const activity=workshopActivities[route.id];if(!activity||section.querySelector(`#activity-${route.id}`))return;
 const template=document.createElement("template");template.innerHTML=workshopMarkup(route,activity).trim();
 const workshop=template.content.firstElementChild;
 section.querySelector(".route-grid")?.after(workshop);bindWorkshop(section,route);
}
function resetAllWorkshops(){
 workshopState={routes:{}};
 saveWorkshopState();
 document.querySelectorAll(".route").forEach(section=>{const route=routes.find(item=>section.id===`route-${item.id}`);if(!route)return;section.querySelector(".activity-workshop")?.remove();injectWorkshop(section,route);window.MitoMapaRouteFlow?.enhance(section,route);});
}
/* Versión 3.6: opción de Secundaria y producciones discursivas por ruta. */
const learningLevelCopy=Object.freeze({
 early:{label:"Infantil y 1.º ciclo",short:"Inicio",guide:"Cuento, lectura acompañada y tres preguntas de comprensión. La pintadera se consigue con este reto."},
 middle:{label:"2.º ciclo",short:"Avanza",guide:"Cuento, comprensión, verdadero o falso y actividad de vocabulario."},
 advanced:{label:"3.º ciclo",short:"Investiga",guide:"Comprensión y verdadero/falso; tareas de vocabulario, fuentes y creación acordadas con tu docente."},
 secondary:{label:"Secundaria",short:"Secundaria",guide:"Cuento, contraste de fuentes y una producción propia con los apoyos y la extensión acordados."}
});

function badgeCountsForLevel(routeId){
 return earned.has(routeId)&&badgeRequirementsMet(routeId);
}
function currentBadgeCount(){return routes.filter(route=>badgeCountsForLevel(route.id)).length;}
function historicalBadgeCount(){return routes.filter(route=>earned.has(route.id)&&!badgeCountsForLevel(route.id)).length;}
function badgeRequirementsMet(routeId){
 return sourcePassed.has(routeId)&&(learningLevel==="early"||truthPassed.has(routeId));
}

function learningLevelLabel(){
 return learningLevelCopy[learningLevel]?.label||learningLevelCopy.middle.label;
}

function applyLearningLevelToRoute(section){
 if(!section)return;
 const routeId=section.id.replace("route-","");
 const early=learningLevel==="early";
 const advanced=learningLevel==="advanced";
 const secondary=learningLevel==="secondary";
 const truthBox=section.querySelector(`#quiz-${routeId}`);
 const truthStep=section.querySelector(".truth-step");
 const badgeStep=section.querySelector(".badge-step");
 const workshop=section.querySelector(".activity-workshop");
 if(truthBox)truthBox.hidden=early;
 if(truthStep)truthStep.hidden=early;
 if(badgeStep)badgeStep.textContent=early?"2. Pintadera":"3. Pintadera";
 if(workshop){
  workshop.dataset.level=learningLevel;
  applyNotebookAssignment(routeId);
 }
 let note=section.querySelector(".level-route-note");
 if(!note){
  note=document.createElement("div");
  note.className="level-route-note";
  section.querySelector(".route-steps")?.after(note);
 }
 note.innerHTML=`<h3>Tu itinerario en ${activityEscape(learningLevelLabel())}</h3><ol>${itinerarySteps[learningLevel].map(step=>`<li>${activityEscape(step)}</li>`).join("")}</ol><p class="assigned-tasks" hidden></p><p class="itinerary-status" role="status"></p><p class="itinerary-footnote">La guía es orientativa: tu docente decide qué tareas realizar. La revisión se registra por separado para cada etapa.</p>`;
 updateItineraryUI();
 const sourceKicker=section.querySelector(".source-quiz .challenge-kicker");
 if(sourceKicker)sourceKicker.textContent=early?"Reto de la pintadera":"Reto 1 de 2";
 const truthKicker=section.querySelector(`#quiz-${routeId} .challenge-kicker`);
 if(truthKicker)truthKicker.textContent="Reto 2 de 2";
 const truthLead=section.querySelector(`#quiz-${routeId}>p:not(.challenge-kicker)`);
 if(truthLead)truthLead.textContent="Marca verdadero o falso. La pintadera se obtiene al completar los dos retos.";
}

function setLearningLevel(level,persist=true){
 learningLevel=Object.prototype.hasOwnProperty.call(learningLevelCopy,level)?level:"middle";
 document.body.dataset.learningLevel=learningLevel;
 document.querySelectorAll(".learning-level-switch button[data-learning-level]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.learningLevel===learningLevel)));
 const status=byId("learningLevelStatus");
 if(status)status.textContent=`Nivel seleccionado: ${learningLevelLabel()}. ${learningLevelCopy[learningLevel].guide}`;
 document.querySelectorAll(".route").forEach(applyLearningLevelToRoute);
 if(learningLevel==="early"){const before=earned.size;sourcePassed.forEach(routeId=>earned.add(routeId));if(earned.size!==before)save();}
 if(persist)savePreferences();
 window.MitoMapaStories?.setLevel(learningLevel);
 window.MitoMapaCompare?.setLevel(learningLevel);
 updateProgress();
}

const finalChallengeData=Object.freeze([
 {clue:"Magec vuelve a iluminar Echeyde",answer:"tenerife"},
 {clue:"Un tibicena aparece en el barranco",answer:"gran-canaria"},
 {clue:"Idafe parece sostener el cielo",answer:"la-palma"},
 {clue:"El agua y el fuego separan a Gara y Jonay",answer:"la-gomera"},
 {clue:"El Garoé convierte la niebla en gotas",answer:"el-hierro"},
 {clue:"La luz de Mafasca sigue a los caminantes",answer:"fuerteventura"},
 {clue:"Ico supera una prueba de humo",answer:"lanzarote"},
 {clue:"San Borondón aparece detrás de la bruma",answer:"la-graciosa"}
]);
const finalStorageKey="mitomapa-canario-final-v1";
let finalState=readJSON(finalStorageKey,{passed:false});
if(!finalState||typeof finalState!=="object")finalState={passed:false};
finalState.passed=Boolean(finalState.passed);

function saveFinalState(){
 return writeJSON(finalStorageKey,finalState);
}

function renderFinalChallenge(){
 const grid=byId("finalMatchGrid");
 if(!grid||grid.children.length)return;
 const options=routes.map(route=>`<option value="${route.id}">${activityEscape(route.island)}</option>`).join("");
 grid.innerHTML=finalChallengeData.map((item,index)=>`<label class="final-match-item"><span id="final-match-label-${index}"><strong>${index+1}.</strong> ${activityEscape(item.clue)}</span><select data-final-answer="${item.answer}" aria-labelledby="final-match-label-${index}"><option value="">Elige una isla</option>${options}</select><small class="final-match-feedback" aria-live="polite"></small></label>`).join("");
}

function updateFinalExperience(){
 const unlocked=currentBadgeCount()===routes.length;
 const challenge=byId("finalChallengeBox");
 const celebration=byId("finalCelebration");
 const diplomaButton=byId("printDiploma");
 if(challenge)challenge.hidden=!unlocked;
 if(celebration)celebration.hidden=!(unlocked&&finalState.passed);
 if(diplomaButton)diplomaButton.disabled=!(unlocked&&finalState.passed);
 const nameInput=byId("diplomaName");
 if(nameInput&&nameInput.value!==learnerName)nameInput.value=learnerName;
}

function checkFinalChallenge(){
 const box=byId("finalChallengeBox");
 if(!box||currentBadgeCount()!==routes.length)return;
 const items=[...box.querySelectorAll(".final-match-item")];
 let correct=0,missing=0;
 items.forEach(item=>{
  const select=item.querySelector("select"),feedback=item.querySelector("small");
  const value=select.value,ok=value===select.dataset.finalAnswer;
  if(!value){missing++;feedback.textContent="Elige una isla.";item.dataset.result="missing";return;}
  if(ok)correct++;
  item.dataset.result=ok?"correct":"wrong";
  feedback.textContent=ok?"Correcto.":"Revisa la pista y vuelve a intentarlo.";
 });
 const status=byId("finalChallengeStatus");
 if(missing){status.textContent=`Faltan ${missing} ${missing===1?"respuesta":"respuestas"}.`;return;}
 if(correct===items.length){
  finalState.passed=true;saveFinalState();status.textContent="¡Gran reto superado! Las ocho historias ya están conectadas.";updateFinalExperience();
 }else status.textContent=`Resultado: ${correct} de ${items.length}. Revisa las pistas marcadas.`;
}

function syncLearnerName(value){
 learnerName=String(value||"").replace(/\s+/g," ").trim().slice(0,80);
 [byId("teacherLearnerName"),byId("diplomaName")].forEach(input=>{if(input&&input.value!==learnerName)input.value=learnerName;});
 savePreferences();
}

function workshopStageCount(routeId){const completion=notebookCompletion(routeId);return selectedNotebookTasks(routeId).filter(key=>completion[key]).length;}
function teacherTaskMarkup(route){
 const item=itineraryFor(route.id),id=route.id;
 return `<fieldset class="teacher-assignment"><legend>Cuaderno asignado</legend>${Object.entries(notebookTaskNames).map(([key,label])=>`<label><input type="checkbox" data-assign-route="${id}" data-assign-task="${key}" ${item.selectedTasks.includes(key)?"checked":""}> ${label}</label>`).join("")}</fieldset><label class="assigned-label">Producción de ${activityEscape(route.island)}<select data-evidence-route="${id}"><option value="web" ${item.evidenceMode==="web"?"selected":""}>En la web</option><option value="external" ${item.evidenceMode==="external"?"selected":""}>Oral o fuera de la web</option></select></label><label class="external-review" ${item.evidenceMode!=="external"||!item.selectedTasks.includes("creation")?"hidden":""}><input type="checkbox" data-external-route="${id}" ${item.externalCreation?"checked":""}> Producción externa revisada</label>${learningLevel==="secondary"?`<label class="assigned-label"><span><input type="checkbox" data-flexible-route="${id}" ${item.flexibleLength?"checked":""}> Adaptar la extensión escrita</span></label>`:""}`;
}
function teacherStatusWord(done){return done?"Superado":"Pendiente";}

function updateTeacherDialog(){
 const tbody=byId("teacherProgressBody");
 if(!tbody)return;
 tbody.innerHTML=routes.map(route=>`<tr><th scope="row">${activityEscape(route.island)}</th><td>${teacherStatusWord(sourcePassed.has(route.id))}</td><td>${learningLevel==="early"?"Opcional":teacherStatusWord(truthPassed.has(route.id))}</td><td>${selectedNotebookTasks(route.id).length?`${workshopStageCount(route.id)}/${selectedNotebookTasks(route.id).length}`:"Sin tareas"}</td><td>${teacherStatusWord(badgeCountsForLevel(route.id))}</td><td>${teacherTaskMarkup(route)}<label class="review-toggle"><input type="checkbox" data-review-route="${route.id}" ${itineraryFor(route.id).reviewed?"checked":""} aria-label="Itinerario revisado de ${activityEscape(route.island)} en ${activityEscape(learningLevelLabel())}"> Revisado con el alumnado</label><label class="assigned-label">Tareas acordadas para ${activityEscape(route.island)}<textarea data-task-route="${route.id}" rows="2" maxlength="240">${activityEscape(itineraryFor(route.id).tasks)}</textarea></label></td></tr>`).join("");
 byId("teacherLevelSummary").textContent=learningLevelLabel();
 byId("teacherOverallSummary").textContent=`${currentBadgeCount()}/8 pintaderas · ${sourcePassed.size}/8 comprensiones · ${truthPassed.size}/8 retos · ${finalState.passed?(currentBadgeCount()===routes.length?"gran reto superado":"gran reto conservado; faltan requisitos de esta etapa"):"gran reto pendiente"}.`;
 const input=byId("teacherLearnerName");if(input)input.value=learnerName;
}

function exportProgress(){
 const payload={
  app:"mitomapa-canario",version:RESOURCE_VERSION,schemaVersion:EXPORT_SCHEMA_VERSION,exportedAt:new Date().toISOString(),learningLevel,learnerName,
  progress:{sourcePassed:[...sourcePassed],truthPassed:[...truthPassed],earned:[...earned]},
  workshop:workshopState,
  itineraries,
  journey:window.MitoMapaJourney?.exportState(),
  final:{passed:Boolean(finalState.passed)},
  interactive:{stories:window.MitoMapaStories?.exportState(),comparison:window.MitoMapaCompare?.exportState()}
 };
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
 const link=document.createElement("a"),url=URL.createObjectURL(blob);
 link.href=url;link.download=`seguimiento-mitomapa-${new Date().toISOString().slice(0,10)}.json`;link.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 byId("teacherImportStatus").textContent="Seguimiento preparado para guardarlo en el dispositivo.";
}

function sanitizeImportedWorkshop(raw){
 const clean={routes:{}};
 for(const route of routes){
  const source=raw?.routes?.[route.id];if(!source||typeof source!=="object")continue;
  const drawing=safeWorkshopDrawing(source.drawing);
  if(source.drawing!=null&&source.drawing!==""&&!drawing)throw new Error("DRAWING_INVALID");
  clean.routes[route.id]={words:Boolean(source.words),research:Boolean(source.research),creation:Boolean(source.creation),text:String(source.text||"").slice(0,500),wordResponses:{match:Array.isArray(source.wordResponses?.match)?source.wordResponses.match.slice(0,12).map(v=>String(v).slice(0,120)):[],fill:Array.isArray(source.wordResponses?.fill)?source.wordResponses.fill.slice(0,12).map(v=>String(v).slice(0,120)):[]},researchResponses:Array.isArray(source.researchResponses)?source.researchResponses.slice(0,2).map(v=>Number.isInteger(v)&&v>=0&&v<3?v:null):[],researchEvidence:String(source.researchEvidence||"").slice(0,600),drawing,drawingHasInk:Boolean(source.drawingHasInk&&drawing),secondaryCreation:Boolean(source.secondaryCreation),secondaryText:String(source.secondaryText||"").slice(0,5000),secondaryChoice:String(source.secondaryChoice||"").slice(0,180),secondaryChecks:Array.isArray(source.secondaryChecks)?source.secondaryChecks.slice(0,4).map(Boolean):[],creationReviewV1:sanitizeCreationReview(source.creationReviewV1)};
 }
 return clean;
}

async function importProgressFile(file){
 const status=byId("teacherImportStatus");
 if(!file)return;
 if(file.size>5000000){status.textContent="El archivo supera el límite de 5 MB.";return;}
 try{
  const payload=JSON.parse(await file.text());
  if(payload?.app!=="mitomapa-canario"||!payload.progress)throw new Error("Formato no reconocido");
  if(!confirm("¿Quieres sustituir el progreso de este navegador por el del archivo seleccionado?")){status.textContent="Importación cancelada.";return;}
  const importedWorkshop=await normalizeImportedDrawings(sanitizeImportedWorkshop(payload.workshop));
  clearLearnerResponses();
  sourcePassed=normalize(payload.progress.sourcePassed);truthPassed=normalize(payload.progress.truthPassed);earned=normalize(payload.progress.earned);
  learningLevel=Object.prototype.hasOwnProperty.call(learningLevelCopy,payload.learningLevel)?payload.learningLevel:"middle";
  learnerName=String(payload.learnerName||"").replace(/\s+/g," ").trim().slice(0,80);
  workshopState=importedWorkshop;
  finalState={passed:Boolean(payload.final?.passed)};
  itineraries=sanitizeItineraries(payload.itineraries);saveItineraries();
  window.MitoMapaJourney?.importState(payload.journey);
  window.MitoMapaStories?.importState(payload.interactive?.stories);
  window.MitoMapaCompare?.importState(payload.interactive?.comparison);
  window.MitoMapaExplorer?.reset();
  window.MitoMapaNames?.reset();
  save();savePreferences();saveWorkshopState();saveFinalState();
  renderRoutes();setLearningLevel(learningLevel,false);updateTeacherDialog();updateFinalExperience();
  window.MitoMapaNavigation?.refresh();
  status.textContent="Seguimiento cargado correctamente.";
 }catch(error){status.textContent=error.message==="DRAWING_INVALID"?"No se pudo cargar: contiene un dibujo dañado, animado o demasiado grande. Se conserva el progreso anterior.":"No se pudo cargar: el archivo no tiene un formato válido del MitoMapa.";}
}

function clearPrintMode(){
 document.body.classList.remove("print-diploma","print-passport");
}

function printDiploma(){
 if(currentBadgeCount()!==routes.length||!finalState.passed)return;
 const name=learnerName||"Explorador o exploradora del MitoMapa";
 byId("diplomaPrintName").textContent=name;
 byId("diplomaPrintDate").textContent=new Intl.DateTimeFormat("es-ES",{dateStyle:"long"}).format(new Date());
 byId("diplomaPrintBadges").innerHTML=routes.map(route=>`<img src="${ASSETS[route.badge]}" alt="">`).join("");
 document.body.classList.add("print-diploma");
 requestAnimationFrame(()=>window.print());
}

function printPassport(){
 const grid=byId("passportPrintGrid");
 grid.innerHTML=routes.map(route=>`<article class="passport-print-slot ${badgeCountsForLevel(route.id)?"earned":""}"><img src="${ASSETS[route.badge]}" alt=""><h3>${activityEscape(route.island)}</h3><p>${badgeCountsForLevel(route.id)?activityEscape(route.badgeName):"Pintadera pendiente"}</p></article>`).join("");
 byId("passportPrintName").textContent=(learnerName?`de ${learnerName}`:"del MitoMapa")+` · ${learningLevelLabel()} · requisitos de la etapa seleccionada`;
 document.body.classList.add("print-passport");
 requestAnimationFrame(()=>window.print());
}

function resetV34State(){
 finalState={passed:false};learnerName="";
 itineraries=sanitizeItineraries({});saveItineraries();
 saveFinalState();
 byId("finalMatchGrid")?.querySelectorAll("select").forEach(select=>{select.value="";select.closest(".final-match-item")?.removeAttribute("data-result");});
 byId("finalMatchGrid")?.querySelectorAll(".final-match-feedback").forEach(feedback=>{feedback.textContent="";});
 if(byId("finalChallengeStatus"))byId("finalChallengeStatus").textContent="";
 savePreferences();renderFinalChallenge();updateFinalExperience();
}

// Los aciertos guardados y las respuestas visibles son estados diferentes.
// Al reiniciar o importar otro seguimiento, no deben sobrevivir respuestas de
// la persona anterior, ni siquiera en actividades que no se exportan.
function clearLearnerResponses(){
 stopNarration();
 document.querySelectorAll(".route .quiz").forEach(quiz=>{
  quiz.querySelectorAll("input[type=radio]").forEach(input=>{input.checked=false;});
  quiz.querySelectorAll(".feedback").forEach(feedback=>{feedback.className="feedback";feedback.textContent="";});
  quiz.querySelectorAll(".source-status,.quiz-status").forEach(status=>{status.textContent="";});
  quiz._showQuestion?.(0);
 });
 document.querySelectorAll(".route-step.complete").forEach(step=>step.classList.remove("complete"));
 document.querySelectorAll(".reward.show").forEach(reward=>reward.classList.remove("show"));
 document.querySelectorAll(".route").forEach(section=>{section.dataset.routeFlowQuiz="comprension";});
 byId("finalMatchGrid")?.querySelectorAll("select").forEach(select=>{select.value="";select.closest(".final-match-item")?.removeAttribute("data-result");});
 byId("finalMatchGrid")?.querySelectorAll(".final-match-feedback").forEach(feedback=>{feedback.textContent="";});
 if(byId("finalChallengeStatus"))byId("finalChallengeStatus").textContent="";
 document.querySelectorAll("[data-feedback-rating]").forEach(select=>{select.value="";});
 document.querySelectorAll("[data-feedback-open]").forEach(textarea=>{textarea.value="";});
 if(byId("feedbackStatus"))byId("feedbackStatus").textContent="";
}

function resetProgress(){
 if(!confirm("¿Quieres borrar los retos, las pintaderas, el gran reto, el cuaderno y las nuevas actividades guardadas en este navegador?"))return;
 sourcePassed.clear();truthPassed.clear();earned.clear();
 try{localStorage.removeItem(legacyKey);}catch(error){}
 clearLearnerResponses();resetV34State();window.MitoMapaJourney?.reset();resetAllWorkshops();
 document.querySelectorAll(".route").forEach(applyLearningLevelToRoute);
 window.MitoMapaStories?.reset();window.MitoMapaCompare?.reset();window.MitoMapaExplorer?.reset();window.MitoMapaNames?.reset();
 shuffle();save();updateProgress();updateTeacherDialog();syncTeacherScroll();
 if(byId("teacherImportStatus"))byId("teacherImportStatus").textContent="Progreso reiniciado. No quedan respuestas de la sesión anterior.";
}

function setupV34Features(){
 byId("storageExportHelp")?.addEventListener("click",()=>{updateTeacherDialog();window.MitoMapaTeacher?.show("tools",{focus:false});openDialog(byId("teacherDialog"));byId("exportProgress")?.focus();});
 byId("teacherProgressBody")?.addEventListener("change",event=>{
  const input=event.target,d=input.dataset,id=d.reviewRoute||d.taskRoute||d.assignRoute||d.evidenceRoute||d.externalRoute||d.flexibleRoute;
  if(!validIds.has(id))return;
  const item=itineraryFor(id),row=input.closest("tr");
  if(d.reviewRoute)item.reviewed=input.checked;
  else{
   item.reviewed=false;
   if(d.taskRoute)item.tasks=input.value.slice(0,240);
   if(d.assignRoute)item.selectedTasks=[...row.querySelectorAll("[data-assign-task]:checked")].map(el=>el.dataset.assignTask);
   if(d.evidenceRoute){item.evidenceMode=input.value==="external"?"external":"web";item.externalCreation=false;}
   if(d.externalRoute)item.externalCreation=input.checked;
   if(d.flexibleRoute){item.flexibleLength=input.checked;getWorkshopRouteState(id).secondaryCreation=false;saveWorkshopState();}
   row.querySelector("[data-review-route]").checked=false;
  }
  row.querySelector(".external-review").hidden=item.evidenceMode!=="external"||!item.selectedTasks.includes("creation");
  row.querySelector("[data-external-route]").checked=item.externalCreation;
  row.children[3].textContent=item.selectedTasks.length?`${workshopStageCount(id)}/${item.selectedTasks.length}`:"Sin tareas";
  saveItineraries();applyNotebookAssignment(id);updateItineraryUI();syncTeacherScroll();
 });
 renderFinalChallenge();
 byId("checkFinalChallenge")?.addEventListener("click",checkFinalChallenge);
 byId("diplomaName")?.addEventListener("change",event=>syncLearnerName(event.target.value));
 byId("printDiploma")?.addEventListener("click",printDiploma);
 byId("openTeacher")?.addEventListener("click",()=>{updateTeacherDialog();window.MitoMapaTeacher?.show("guide",{focus:false});openDialog(byId("teacherDialog"));window.MitoMapaTeacher?.show("guide");});
 byId("closeTeacher")?.addEventListener("click",()=>closeDialog(byId("teacherDialog")));
 byId("teacherLearnerName")?.addEventListener("change",event=>syncLearnerName(event.target.value));
 byId("exportProgress")?.addEventListener("click",exportProgress);
 byId("importProgress")?.addEventListener("click",()=>byId("importProgressFile")?.click());
 byId("importProgressFile")?.addEventListener("change",event=>{importProgressFile(event.target.files?.[0]);event.target.value="";});
 byId("printPassport")?.addEventListener("click",printPassport);
 window.addEventListener("afterprint",clearPrintMode);
 setLearningLevel(learningLevel,false);updateFinalExperience();
}
function enhanceRoute(section,route){
 section.querySelectorAll("img").forEach(image=>{image.loading="lazy";image.decoding="async";});
 const story=section.querySelector(".story"),intro=story?.querySelector(".story-intro");
 if(story&&!story.querySelector(".narrator")){
  const template=document.createElement("template");template.innerHTML=narrationMarkup(route).trim();
  (intro||story.firstElementChild)?.after(template.content.firstElementChild);
 }
 injectWorkshop(section,route);
 window.MitoMapaStories?.enhanceRoute(section,route,learningLevel);
 applyLearningLevelToRoute(section);
 const sourceBox=section.querySelector(`#source-${route.id}`);
 sourceBox.querySelector(".source-questions").innerHTML=route.quick.map((question,index)=>`<fieldset class="question"><legend>${index+1}. ${question.q}</legend><div class="source-options">${question.options.map((option,optionIndex)=>`<label><input type="radio" name="source-${route.id}-${index}" value="${optionIndex}"><span>${option}</span></label>`).join("")}</div><div class="feedback" aria-live="polite"></div></fieldset>`).join("");
 const truthBox=section.querySelector(`#quiz-${route.id}`);
 truthBox.querySelector(".questions").innerHTML=route.questions.map((question,index)=>`<fieldset class="question"><legend>${index+1}. ${question.q}</legend><div class="choices"><label><input type="radio" name="truth-${route.id}-${index}" value="true"> Verdadero</label><label><input type="radio" name="truth-${route.id}-${index}" value="false"> Falso</label></div><div class="feedback" aria-live="polite"></div></fieldset>`).join("");
 enhanceQuizStepper(sourceBox);enhanceQuizStepper(truthBox);
 section.querySelector(".check-source").addEventListener("click",()=>checkSource(route.id));
 section.querySelector(".check-quiz").addEventListener("click",()=>checkQuiz(route.id));
 section.querySelectorAll(".back-map").forEach(button=>{button.textContent="Elegir otra isla";button.addEventListener("click",returnToExploreMap);});
 section.querySelectorAll(".open-passport").forEach(button=>button.addEventListener("click",showPassport));
 section.querySelector(".narration-play")?.addEventListener("click",()=>startNarration(route.id));
 section.querySelector(".narration-pause")?.addEventListener("click",()=>toggleNarrationPause(route.id));
 section.querySelector(".narration-stop")?.addEventListener("click",()=>stopNarration());
 section.querySelector(".narration-back")?.addEventListener("click",()=>seekNarration(route.id,-10,{relative:true}));
 section.querySelector(".narration-forward")?.addEventListener("click",()=>seekNarration(route.id,10,{relative:true}));
 section.querySelector(".narration-seek")?.addEventListener("input",event=>seekNarration(route.id,event.currentTarget.value));
 section.querySelector(".narration-voice")?.addEventListener("change",event=>{
  selectedVoiceURI=event.currentTarget.value;savePreferences();
  document.querySelectorAll(".narration-voice").forEach(select=>{if([...select.options].some(option=>option.value===selectedVoiceURI))select.value=selectedVoiceURI;});
  document.querySelectorAll(".voice-note[data-device-voice]").forEach(note=>note.textContent=voiceDescription());
  if(narrationState.routeId&&!narrationState.audio)stopNarration("Voz actualizada. Pulsa Reproducir para comenzar de nuevo.");
 });
 section.querySelector(".narration-rate")?.addEventListener("change",event=>{
  if(narrationState.routeId===route.id&&narrationState.audio){
   narrationState.audio.defaultPlaybackRate=Number(event.currentTarget.value)||1;
   narrationState.audio.playbackRate=narrationState.audio.defaultPlaybackRate;
  }
 });
 section.querySelector(".narration-ambient")?.addEventListener("change",()=>{
  if(narrationState.routeId===route.id)stopNarration("Ambiente actualizado. Pulsa Reproducir para comenzar de nuevo.");
 });
 if(!speechSupported&&!routeRecording(route.id))updateNarrationUi(route.id,"idle","Este navegador no ofrece lectura automática.");
 refreshVoices();updateProgress();
 window.MitoMapaRouteFlow?.enhance(section,route);
}
function ensureRoute(id){
 const existing=byId(`route-${id}`);if(existing)return existing;
 const index=routes.findIndex(route=>route.id===id);if(index<0)return null;
 const template=document.createElement("template");template.innerHTML=resolveAssetPaths(routeMarkup[index]).trim();
 const section=template.content.firstElementChild;byId("routes").appendChild(section);
 enhanceRoute(section,routes[index]);return section;
}
function renderRoutes(){
 byId("routes").innerHTML="";
 byId("islandGrid").innerHTML=routes.map(route=>`<button class="island-card" type="button" data-route="${route.id}" aria-label="Abrir ${route.island}: ${route.title}" style="text-align:center"><img src="${ASSETS[route.image]}" alt="${route.imageAlt}" loading="lazy" decoding="async"><span class="card-body" style="display:grid;grid-template-rows:auto minmax(44px,auto) auto;align-content:start;justify-items:center;gap:.35rem;width:100%;box-sizing:border-box;padding:1rem 1.15rem 1.2rem;text-align:center"><strong>${route.island}</strong><span>${route.title}</span><small>${route.badgeName}</small><span class="card-action">Abrir cuento →</span></span></button>`).join("");
 document.querySelectorAll(".island-card").forEach(card=>card.addEventListener("click",()=>showRoute(card.dataset.route,{step:"cuento"})));
 updateProgress();refreshVoices();
}
function checkSource(id){
 const route=routes.find(item=>item.id===id),box=byId(`source-${id}`);let correct=0,complete=true,firstIncomplete=-1,firstIncorrect=-1;
 route.quick.forEach((question,index)=>{
  const choice=box.querySelector(`input[name="source-${id}-${index}"]:checked`),feedback=box.querySelectorAll(".feedback")[index];
  if(!choice){complete=false;if(firstIncomplete<0)firstIncomplete=index;feedback.className="feedback ko";feedback.textContent="Selecciona una respuesta.";return;}
  const ok=Number(choice.value)===question.answer;if(ok)correct++;
  if(!ok&&firstIncorrect<0)firstIncorrect=index;
  feedback.className=`feedback ${ok?"ok":"ko"}`;feedback.textContent=ok?question.hit:question.error;
 });
 const status=box.querySelector(".source-status");
 if(!complete){status.textContent="Completa las tres preguntas antes de comprobar.";box._showQuestion?.(firstIncomplete,{focus:true});return;}
 if(correct===route.quick.length){sourcePassed.add(id);save();status.textContent=`Resultado: ${correct} de ${route.quick.length}. Comprensión superada.`;}
 else{status.textContent=`Resultado: ${correct} de ${route.quick.length}. Revisa las pistas e inténtalo de nuevo.`;box._showQuestion?.(firstIncorrect,{focus:true});}
 updateProgress();
 if(badgeRequirementsMet(id))tryAward(id);
 else if(sourcePassed.has(id))status.textContent+=" Ahora supera «Reto de la pintadera».";
}
function checkQuiz(id){
 const route=routes.find(item=>item.id===id),box=byId(`quiz-${id}`);let correct=0,complete=true,firstIncomplete=-1,firstIncorrect=-1;
 route.questions.forEach((question,index)=>{
  const choice=box.querySelector(`input[name="truth-${id}-${index}"]:checked`),feedback=box.querySelectorAll(".feedback")[index];
  if(!choice){complete=false;if(firstIncomplete<0)firstIncomplete=index;feedback.className="feedback ko";feedback.textContent="Selecciona una respuesta.";return;}
  const ok=(choice.value==="true")===question.answer;if(ok)correct++;
  if(!ok&&firstIncorrect<0)firstIncorrect=index;
  feedback.className=`feedback ${ok?"ok":"ko"}`;feedback.textContent=`${ok?"Correcto.":"Revisa tu respuesta."} ${question.feedback}`;
 });
 const status=box.querySelector(".quiz-status");
 if(!complete){status.textContent="Completa las tres afirmaciones antes de comprobar.";box._showQuestion?.(firstIncomplete,{focus:true});return;}
 if(correct===route.questions.length){truthPassed.add(id);save();status.textContent="Resultado: 3 de 3. Reto superado.";}
 else{status.textContent=`Resultado: ${correct} de 3. Revisa las pistas e inténtalo de nuevo.`;box._showQuestion?.(firstIncorrect,{focus:true});}
 updateProgress();
 if(badgeRequirementsMet(id))tryAward(id);
 else if(truthPassed.has(id))status.textContent+=" Ahora supera «Comprendemos el cuento».";
}
const cols=4,rows=3;let order=[],selected=null,dragPosition=null;
function piecePosition(tile){const x=tile%cols,y=Math.floor(tile/cols);return `${x/(cols-1)*100}% ${y/(rows-1)*100}%`;}
function puzzleSolved(){return order.every((value,index)=>value===index);}
function announcePuzzleChange(){
 if(puzzleSolved()){byId("puzzleStatus").className="status success";byId("puzzleStatus").textContent="¡Mapa reconstruido! Ya puedes comenzar las rutas.";}
 else{byId("puzzleStatus").className="status";byId("puzzleStatus").textContent="Piezas intercambiadas. Continúa.";}
}
function swapPuzzlePieces(first,second){if(first===second)return;[order[first],order[second]]=[order[second],order[first]];selected=null;renderPuzzle();announcePuzzleChange();}
function renderPuzzle(){
 const board=byId("puzzleBoard");const focusIndex=[...board.children].indexOf(document.activeElement);board.innerHTML="";
 order.forEach((tile,position)=>{
  const button=document.createElement("button");button.type="button";button.draggable=true;
  button.setAttribute("aria-pressed",String(selected===position));
  button.className="puzzle-piece"+(selected===position?" selected":"");button.style.backgroundPosition=piecePosition(tile);
  button.setAttribute("aria-label",`Pieza ${tile+1} en posición ${position+1}. Arrastra o selecciona para intercambiar.`);
  button.addEventListener("click",()=>pickPiece(position));
  button.addEventListener("dragstart",event=>{dragPosition=position;button.classList.add("dragging");event.dataTransfer.effectAllowed="move";event.dataTransfer.setData("text/plain",String(position));});
  button.addEventListener("dragover",event=>{event.preventDefault();event.dataTransfer.dropEffect="move";button.classList.add("drag-over");});
  button.addEventListener("dragleave",()=>button.classList.remove("drag-over"));
  button.addEventListener("drop",event=>{event.preventDefault();button.classList.remove("drag-over");const source=dragPosition??Number(event.dataTransfer.getData("text/plain"));dragPosition=null;swapPuzzlePieces(source,position);});
  button.addEventListener("dragend",()=>{dragPosition=null;document.querySelectorAll(".puzzle-piece").forEach(piece=>piece.classList.remove("dragging","drag-over"));});
  board.appendChild(button);
 });
 if(focusIndex>=0)board.children[focusIndex]?.focus({preventScroll:true});
}
function shuffle(){
 order=[...Array(cols*rows).keys()];for(let index=order.length-1;index>0;index--){const other=Math.floor(Math.random()*(index+1));[order[index],order[other]]=[order[other],order[index]];}
 if(order.every((value,index)=>value===index))[order[0],order[1]]=[order[1],order[0]];
 selected=null;renderPuzzle();byId("puzzleStatus").className="status";byId("puzzleStatus").textContent="Mapa mezclado. Selecciona dos piezas para intercambiarlas.";
}
function pickPiece(position){
 if(selected===null){selected=position;renderPuzzle();byId("puzzleStatus").textContent="Pieza seleccionada. Elige otra para intercambiarlas.";return;}
 if(selected===position){selected=null;renderPuzzle();return;}
 swapPuzzlePieces(selected,position);
}
byId("shufflePuzzle").addEventListener("click",shuffle);
byId("solvePuzzle").addEventListener("click",()=>{order=[...Array(cols*rows).keys()];selected=null;renderPuzzle();byId("puzzleStatus").className="status success";byId("puzzleStatus").textContent="Solución mostrada. Usa esta alternativa si el puzle supone una barrera.";});
byId("openPassport").addEventListener("click",showPassport);
byId("closePassport").addEventListener("click",()=>closeDialog(byId("passportDialog")));
byId("viewPassport").addEventListener("click",()=>{closeDialog(byId("badgeDialog"));showPassport();});
byId("dismissBadge").addEventListener("click",()=>closeDialog(byId("badgeDialog")));
byId("resetProgress").addEventListener("click",resetProgress);
if(speechSupported){window.speechSynthesis.addEventListener?.("voiceschanged",refreshVoices);refreshVoices();}
document.addEventListener("visibilitychange",()=>{if(document.hidden&&narrationState.routeId&&!narrationState.paused)toggleNarrationPause(narrationState.routeId);});
window.addEventListener("pagehide",()=>stopNarration());
window.MitoMapaStories?.init({readJSON,writeJSON,level:learningLevel});
window.MitoMapaExplorer?.init({routes,assets:ASSETS,openRoute:showRoute,isEarned:badgeCountsForLevel});
window.MitoMapaCompare?.init({routes,assets:ASSETS,openRoute:id=>showRoute(id,{step:"cuento"}),eventsFor:id=>window.MitoMapaStories?.eventsFor(id)||[],readJSON,writeJSON,downloadText:downloadLocalText,level:learningLevel});
injectExperienceTools();renderRoutes();setupV34Features();shuffle();
updateHeaderOffset();
window.MitoMapaNames?.mount();
window.MitoMapaNavigation?.mount({routes,openRoute:showRoute,stopNarration,lastRoute:()=>lastRouteId});
window.MitoMapaTeacher?.init({setLevel:level=>{setLearningLevel(level);updateTeacherDialog();},refresh:syncTeacherScroll});
window.MitoMapaJourney?.init({routes,getLevel:()=>learningLevel,isReviewed:id=>itineraryFor(id).reviewed,badgeCount:currentBadgeCount,readJSON,writeJSON,onChange:()=>updateItineraryUI()});

// Ajustar el salto a la altura real de la cabecera, también al ampliar el texto.
function updateHeaderOffset(){const header=document.querySelector("header"),navigation=document.querySelector(".main-navigation");if(header){const height=Math.ceil(header.getBoundingClientRect().height);document.documentElement.style.setProperty("--topbar-height",`${height}px`);document.documentElement.style.setProperty("--header-offset",`${height+Math.ceil(navigation?.getBoundingClientRect().height||0)+24}px`);}}
if(typeof ResizeObserver!=="undefined"){const header=document.querySelector("header");if(header)new ResizeObserver(updateHeaderOffset).observe(header);}
window.addEventListener("resize",updateHeaderOffset);updateHeaderOffset();updateStorageNotice();

// Controles alternativos para barras horizontales ocultas por el sistema.
function syncTeacherScroll(){
 const box=byId("teacherTableViewport"),controls=byId("teacherScrollControls");if(!box||!controls)return;
 const remaining=box.scrollWidth-box.clientWidth;
 controls.hidden=remaining<=1;
 byId("teacherScrollLeft").disabled=box.scrollLeft<=1;
 byId("teacherScrollRight").disabled=remaining-box.scrollLeft<=1;
}
function moveTeacherColumns(direction){
 const box=byId("teacherTableViewport");if(!box)return;
 box.scrollBy({left:direction*Math.max(180,box.clientWidth*.7),behavior:window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches?"auto":"smooth"});
}
byId("teacherScrollLeft")?.addEventListener("click",()=>moveTeacherColumns(-1));
byId("teacherScrollRight")?.addEventListener("click",()=>moveTeacherColumns(1));
byId("teacherTableViewport")?.addEventListener("scroll",syncTeacherScroll);
byId("openTeacher")?.addEventListener("click",()=>requestAnimationFrame(syncTeacherScroll));
window.addEventListener("resize",syncTeacherScroll);
if(typeof ResizeObserver!=="undefined"&&byId("teacherTableViewport"))new ResizeObserver(syncTeacherScroll).observe(byId("teacherTableViewport"));

/* Opinión voluntaria: no recoge nombres ni envía respuestas automáticamente. */
const feedbackConfigKey="mitomapa-canario-formulario-web-v1";
const feedbackLabels=["Me ha resultado fácil usar la herramienta.","Las instrucciones y las explicaciones me han ayudado.","Las imágenes y los textos se han visto con claridad.","La actividad me ha ayudado a comprender los cuentos y el patrimonio.","He disfrutado la actividad y estoy satisfecho/a con la experiencia."];
function validFeedbackURL(value){try{const u=new URL(String(value).trim());return u.protocol==="https:"&&(u.hostname==="forms.gle"||u.hostname==="docs.google.com"&&/^\/forms\/(?:d\/e\/[^/]+\/viewform|d\/[^/]+\/viewform)/.test(u.pathname))?u.href:"";}catch(error){return "";}}
function applyFeedbackURL(value){const url=validFeedbackURL(value),link=byId("openWebFeedback");if(link){link.hidden=!url;if(url)link.href=url;else link.removeAttribute("href");}const input=byId("webFeedbackURL");if(input)input.value=url;}
byId("feedbackQuestions").innerHTML=feedbackLabels.map((label,i)=>`<label><span>${activityEscape(label)}</span><select data-feedback-rating="${i}"><option value="">Elige una respuesta</option>${[1,2,3,4,5].map(n=>`<option value="${n}">${n}</option>`).join("")}<option value="na">No puedo valorarlo</option></select></label>`).join("")+`<label><span>¿Qué te ha gustado más? (opcional)</span><textarea data-feedback-open="liked" maxlength="1000" rows="3"></textarea></label><label><span>¿Qué cambiarías o qué dificultad has tenido? (opcional)</span><textarea data-feedback-open="improve" maxlength="1000" rows="3"></textarea></label>`;
const savedFeedbackConfig=readJSON(feedbackConfigKey,null);
applyFeedbackURL(savedFeedbackConfig?.url??window.MitoMapaConfig?.feedbackFormURL??"");
byId("webFeedbackURL").addEventListener("change",event=>{const value=event.target.value.trim(),url=validFeedbackURL(value);if(value&&!url){byId("feedbackURLStatus").textContent="Utiliza un enlace público de respuesta de Google Forms (viewform o forms.gle), no el enlace de edición.";return;}const ok=writeJSON(feedbackConfigKey,{url});applyFeedbackURL(url);byId("feedbackURLStatus").textContent=ok?"Enlace actualizado en este navegador.":"No se ha podido guardar el enlace en este navegador.";});
byId("downloadFeedback").addEventListener("click",()=>{
 const ratings=[...document.querySelectorAll("[data-feedback-rating]")].map((select,i)=>({question:feedbackLabels[i],response:select.value||null}));
 const liked=document.querySelector('[data-feedback-open="liked"]').value.trim(),improve=document.querySelector('[data-feedback-open="improve"]').value.trim();
 if(ratings.every(r=>r.response===null)&&!liked&&!improve){byId("feedbackStatus").textContent="Responde al menos una pregunta de la escala o escribe un comentario antes de descargar tu valoración.";return;}
 const response={resource:"MitoMapa web",version:RESOURCE_VERSION,schemaVersion:EXPORT_SCHEMA_VERSION,stage:learningLevelLabel(),ratings,liked,improve};
 downloadLocalText(JSON.stringify(response,null,2),"valoracion-mitomapa-web.json","application/json");
 byId("feedbackStatus").textContent="Valoración preparada para descargar. Si quieres compartirla con MitoMapa, abre «Enviar valoración por correo» y adjunta manualmente el archivo descargado.";
});
