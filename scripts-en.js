/* MitoMapa canario · la versión de distribución procede de VERSION.json. */
const RESOURCE_VERSION=typeof window.MitoMapaVersion?.version==="string"?window.MitoMapaVersion.version:"unidentified";
const EXPORT_SCHEMA_VERSION=1;
const ASSETS=Object.freeze({"mapa_canarias.webp":"assets/images/mapa_canarias.webp","pintadera_dentada.webp":"assets/images/pintadera_dentada.webp","pintadera_rombos.webp":"assets/images/pintadera_rombos.webp","pintadera_roseta.webp":"assets/images/pintadera_roseta.webp","pintadera_sol.webp":"assets/images/pintadera_sol.webp","pintadera_triangulo.webp":"assets/images/pintadera_triangulo.webp","scene_el-hierro.webp":"assets/images/scene_el-hierro.webp","scene_fuerteventura.webp":"assets/images/scene_fuerteventura.webp","scene_gran-canaria.webp":"assets/images/scene_gran-canaria.webp","scene_la-gomera.webp":"assets/images/scene_la-gomera.webp","scene_la-graciosa.webp":"assets/images/carabela-san-borondon.png","scene_la-palma.webp":"assets/images/scene_la-palma.webp","scene_lanzarote.webp":"assets/images/scene_lanzarote.webp","scene_tenerife.webp":"assets/images/scene_tenerife.webp","pintadera_seis_triangulos.webp":"assets/images/pintadera_seis_triangulos.webp","pintadera_chevron.webp":"assets/images/pintadera_chevron.webp","pintadera_circulos.webp":"assets/images/pintadera_circulos.webp","pintadera_doble_triangulo.webp":"assets/images/pintadera_doble_triangulo.webp","pintadera_espiral_cuadrada.webp":"assets/images/pintadera_espiral_cuadrada.webp","insignia_tenerife.webp":"assets/images/insignia_tenerife.webp","insignia_gran_canaria.webp":"assets/images/insignia_gran_canaria.webp","insignia_la_palma.webp":"assets/images/insignia_la_palma.webp","insignia_la_gomera.webp":"assets/images/insignia_la_gomera.webp","insignia_el_hierro.webp":"assets/images/insignia_el_hierro.webp?v=4.8.3","insignia_fuerteventura.webp":"assets/images/insignia_fuerteventura.webp","insignia_lanzarote.webp":"assets/images/insignia_lanzarote.webp","insignia_la_graciosa.webp":"assets/images/insignia_la_graciosa.webp"});
function resolveAssetPaths(markup){return markup.replace(/content\/resources\/([A-Za-z0-9_.-]+\.webp)/g,(match,name)=>ASSETS[name]||match);}
const routes=[{"id":"tenerife","island":"Tenerife","title":"Dácil and the Return of Magec","image":"scene_tenerife.webp","imageAlt":"A young woman and three other people look towards a light in the sky near Mount Teide. Fictional scene from the story of Dácil and Magec.","badge":"insignia_tenerife.webp","badgeName":"Light piece","quick":[{"q":"Who had hidden Magec inside Echeyde?","options":["Dácil","Guayota","Achamán","The herd"],"answer":1,"hit":"In the story, Guayota held Magec, the Sun, captive in the volcano.","error":"Remember who lived inside the volcano."},{"q":"Who did the community ask for help?","options":["Acorán","Abora","Achamán","Orahan"],"answer":2,"hit":"The community asked Achamán, lord of the sky, for help.","error":"Find the name of the being who brought back the light."},{"q":"How did Dácil know Magec had returned?","options":["She heard a bell","She saw a golden line above Echeyde","She found a pot","A ship arrived"],"answer":1,"hit":"The golden line lit up the summit, then the slopes.","error":"Look at the last scene of the story."}],"questions":[{"q":"Guayota helped Magec light up the island.","answer":false,"feedback":"Guayota kept Magec hidden in the volcano. Achamán freed him.","hint":"Find out who caused the darkness and who brought back the light."},{"q":"Achamán sealed the entrance to the volcano with a great rock.","answer":true,"feedback":"After freeing Magec, Achamán sealed the entrance with an enormous rock to keep Guayota inside.","hint":"Read what Achamán did after defeating Guayota."},{"q":"Dácil looked after goats near Echeyde.","answer":true,"feedback":"At the start of the story, Dácil looks after goats near Echeyde and waits for the first ray of the Sun.","hint":"Find where Dácil is and what she is doing at the start."}],"badgeAlt":"Clay vessel from Tenerife"},{"id":"gran-canaria","island":"Gran Canaria","title":"Guayarmina and the Tibicena of the Ravine","image":"scene_gran-canaria.webp","imageAlt":"A young woman crouches on a path through a ravine. Three people watch behind her. Fictional scene from the story of Guayarmina.","badge":"insignia_gran_canaria.webp","badgeName":"Memory piece","quick":[{"q":"Where did the tibicena appear?","options":["In the sea","Among the tabaibas in the ravine","Inside the tagoror","On a ship"],"answer":1,"hit":"The figure appeared among the tabaibas in the ravine.","error":"Think of the landscape where Guayarmina looked after the goats."},{"q":"What did Guayarmina and the other goatherds do?","options":["They ran in different directions","They chased the creature","They stayed together and raised their torches","They put out the fire"],"answer":2,"hit":"They stayed safe by keeping together and holding up their torches.","error":"The refrain gives you a clue."},{"q":"What did they find at dawn?","options":["A crown","Large footprints mixed with goat tracks","A letter","A torch that had turned to stone"],"answer":1,"hit":"The creature’s footprints were mixed with the goat tracks.","error":"Think about the clues the creature left behind."}],"questions":[{"q":"Guayarmina sailed on the sea with a herd.","answer":false,"feedback":"Guayarmina leads a herd along a path through a ravine in Gran Canaria.","hint":"Read the first paragraph again and look for the setting."},{"q":"The goatherds chased the tibicena alone at night.","answer":false,"feedback":"The goatherds stayed together with the herd and raised their torches. No one went into the ravine alone.","hint":"Look at what the goatherds do when Guayarmina calls them."},{"q":"At dawn they found footprints mixed with goat tracks.","answer":true,"feedback":"When the creature disappears as the sky grows light, it leaves large footprints mixed with goat tracks.","hint":"Read what is still on the ground at dawn."}],"badgeAlt":"Clay vessel from Gran Canaria"},{"id":"la-palma","island":"La Palma","title":"Acerina and the Rock That Held Up the Sky","image":"scene_la-palma.webp","imageAlt":"An adult and a girl look at a tall rock formation among mountains and clouds. An imagined view of Roque Idafe from Acerina’s story.","badge":"insignia_la_palma.webp","badgeName":"Idafe piece","quick":[{"q":"What did the rock of Idafe seem to hold up?","options":["The sea","The sky","A cave","The village"],"answer":1,"hit":"Idafe seemed to hold up the sky above the Caldera.","error":"The answer is at the beginning of the story."},{"q":"Why did the group move away from the slope?","options":["It began to snow","A ship arrived","The ground shook and stones fell","A goat went missing"],"answer":2,"hit":"The group moved to safety when the ground shook.","error":"Remember what the grandfather did when he heard the noise."},{"q":"What did Acerina do when she grew up?","options":["She forgot the ceremony","She became a storyteller","She left Benahoare","She knocked down the rock"],"answer":1,"hit":"Acerina told the story to keep the memory of the place alive.","error":"Find out how Acerina kept her promise."}],"questions":[{"q":"Acerina lived in Benahoare.","answer":true,"feedback":"The story places Acerina in Benahoare, the island we now call La Palma.","hint":"Read the first sentence of the story again."},{"q":"Acerina kept the story alive by becoming a storyteller.","answer":true,"feedback":"Acerina becomes a storyteller and tells the children what she experienced to keep the memory of Idafe alive.","hint":"Look at what Acerina does as the years pass."},{"q":"The group stayed by the cliff while stones were falling.","answer":false,"feedback":"The grandfather takes Acerina’s hand and the group moves away from the cliff as the stones tumble down.","hint":"Find out how they react when the ground shakes and the stones fall."}],"badgeAlt":"Clay vessel from La Palma"},{"id":"la-gomera","island":"La Gomera","title":"Gara and Jonay, Two Voices on the Summit","image":"scene_la-gomera.webp","imageAlt":"A young woman holds her hands open as she speaks to two groups on opposite sides of a ravine. Fictional scene from the story of Gara and Jonay.","badge":"insignia_la_gomera.webp","badgeName":"Meeting piece","quick":[{"q":"How did Jonay get there from Tenerife?","options":["On a large ship","On bags made from goatskin","By a bridge","By flying"],"answer":1,"hit":"The legend says Jonay used goatskin bags to help him float as he swam across the sea.","error":"Remember what Jonay used to help him float."},{"q":"Why did their families object?","options":["They feared the warning about water and fire","They did not know the way","They had lost the herd","They wanted to visit another island"],"answer":0,"hit":"The families feared what would happen if Gara’s water and Jonay’s fire met.","error":"Read the warning at the spring again."},{"q":"What lesson does the story pass on?","options":["You should never listen to anyone","Hostility and failing to listen cause pain","The sea always keeps people apart","Legends never change"],"answer":1,"hit":"The story invites us to listen and talk before closing the door to dialogue.","error":"Think about what the communities came to understand."}],"questions":[{"q":"Jonay arrived in La Gomera from Lanzarote.","answer":false,"feedback":"Jonay sets out from Tenerife and uses goatskin bags to help him float as he swims to La Gomera.","hint":"Find the island where Jonay lives before he crosses the sea."},{"q":"The legend invites us to think about what happens when people do not listen.","answer":true,"feedback":"The ending links pain to hostility and failing to listen. It invites us to talk.","hint":"Read what the communities come to understand at the end."},{"q":"The families supported the relationship from the start.","answer":false,"feedback":"The families fear the warning and object to Gara’s water meeting Jonay’s fire.","hint":"Find out how the families react before Gara and Jonay leave."}],"badgeAlt":"Clay vessel from La Gomera"},{"id":"el-hierro","island":"El Hierro","title":"Agarfa and the Drops of the Garoé","image":"scene_el-hierro.webp","imageAlt":"A girl and two adults collect water in soft-sided containers under a tree in the mist. Fictional scene from the story of Agarfa and the Garoé.","badge":"insignia_el_hierro.webp","badgeName":"Mist piece","quick":[{"q":"How did the Garoé provide water?","options":["It turned the mist into drops","It melted the snow","It drew water from the sea","It opened a well"],"answer":0,"hit":"The mist formed drops on the branches. The drops fell into the stone basins.","error":"The refrain mentions branches and drops."},{"q":"Why did they hide the path?","options":["To play a game","To protect the water source","Because it was snowing","To find another tree"],"answer":1,"hit":"The community feared losing the water source it depended on.","error":"Remember what appeared on the horizon."},{"q":"What happened after a storm brought down the tree?","options":["Its story disappeared","The community forgot about the water","Its memory lived on in stories","The sea covered the island"],"answer":2,"hit":"Families kept telling the story of the Garoé.","error":"The ending tells you what survived the storm."}],"questions":[{"q":"The Garoé collected water from the mist.","answer":true,"feedback":"Mist gathers in the Garoé’s branches and forms drops that fall into stone basins.","hint":"Read how the water reaches the basins."},{"q":"The community wasted the water in the basins.","answer":false,"feedback":"Agarfa fills the jars slowly to avoid wasting the water the community depends on.","hint":"Look at how carefully Agarfa fills the jars."},{"q":"The memory of the tree lived on after the storm.","answer":true,"feedback":"A storm brings down the tree. Families keep telling the story of how it collected water from the mist.","hint":"Notice what remains after the tree falls."}],"badgeAlt":"Clay vessel from El Hierro"},{"id":"fuerteventura","island":"Fuerteventura","title":"The Light of Mafasca on the Path","image":"scene_fuerteventura.webp","imageAlt":"A woman and a girl watch a small light in a rocky landscape at dusk. Fictional scene from the story of the light of Mafasca.","badge":"insignia_fuerteventura.webp","badgeName":"Mafasca piece","quick":[{"q":"What did the goatherds use to light a fire?","options":["A piece of an old cross","A sail from a ship","Leaves from the Garoé","A pintadera stamp"],"answer":0,"hit":"They broke off a piece of wood from the cross beside the path.","error":"Look for the object they used without respecting what it meant."},{"q":"How did the light move?","options":["It stayed in the fire","It followed them and stopped when they stopped","It fell into the sea","It turned into a goat"],"answer":1,"hit":"The light moved when the goatherds walked and stopped when they stopped.","error":"Remember why they could not leave it behind."},{"q":"How did they put things right?","options":["They hid what had happened","They repaired the cross and told the story","They chased the light","They left the herd behind"],"answer":1,"hit":"They kept their promise and told the other goatherds what had happened.","error":"Think about what they did at dawn the next day."}],"questions":[{"q":"Guise and Ayose were goatherds.","answer":true,"feedback":"Guise and Ayose are fictional goatherds returning with their goats. The story uses names also associated with historical leaders.","hint":"Read the opening and identify the roles of the two characters in this story."},{"q":"The light disappeared as soon as they started walking.","answer":false,"feedback":"The light follows the goatherds as they walk and stops when they stop. It disappears after they make their promise.","hint":"Compare what the light does as they walk and when it disappears."},{"q":"The goatherds decided to leave the cross broken.","answer":false,"feedback":"The goatherds promise to repair the cross and keep their promise the next day.","hint":"Find what Guise and Ayose promise and what they do the next morning."}],"badgeAlt":"Clay vessel from Fuerteventura"},{"id":"lanzarote","island":"Lanzarote","title":"Ico and the Trial by Smoke","image":"scene_lanzarote.webp","imageAlt":"A young woman speaks to a seated group in a volcanic landscape. An older woman stands beside her. Fictional scene from Ico’s story.","badge":"insignia_lanzarote.webp","badgeName":"Ico piece","quick":[{"q":"Why did some people distrust Ico?","options":["She could not walk","Her skin was lighter","She had lost a pot","She arrived by ship"],"answer":1,"hit":"The council treated a difference in appearance as a reason for unfair suspicion.","error":"The first paragraph gives the reason."},{"q":"What did the old woman give her?","options":["A wet sponge","A torch","A stone","A letter"],"answer":0,"hit":"The damp sponge helped Ico breathe during the test.","error":"Remember what Ico held over her mouth."},{"q":"Why did Ico question the test?","options":["It was too short","It put someone in danger to prove who they were","There was no audience","It took place at night"],"answer":1,"hit":"Ico questioned whether anyone should be put in danger to prove who they were.","error":"Think about the question the council could not answer."}],"questions":[{"q":"Ico thought the council’s decision was fair.","answer":false,"feedback":"Ico thanks the old woman for her help and asks why anyone should have to put themselves in danger to prove who they are.","hint":"Read the question Ico asks the council."},{"q":"An old woman helped Ico before the test.","answer":true,"feedback":"Before the test, an old woman gives Ico a wet sponge and explains how to breathe through it.","hint":"Find out who helps Ico and what she gives her."},{"q":"Solidarity helped Ico survive.","answer":true,"feedback":"The old woman’s help and Ico’s intelligence enable Ico to get out of the room. The story draws attention to that act of solidarity.","hint":"Think about how the help Ico receives affects the outcome."}],"badgeAlt":"Clay vessel from Lanzarote"},{"id":"la-graciosa","island":"La Graciosa","title":"Guadarfía and the Island of San Borondón","image":"scene_la-graciosa.webp","imageAlt":"A small wooden caravel with two masts and triangular sails travels at sunset, with several crew members on deck. An imagined early 16th-century voyage.","badge":"insignia_la_graciosa.webp","badgeName":"Horizon piece","quick":[{"q":"What was Guadarfía’s job?","options":["Goatherd","Apprentice sailor","Farmer","Potter"],"answer":1,"hit":"Guadarfía was an apprentice sailor on a small sailing ship.","error":"The answer is in the first sentence."},{"q":"What happened as they approached the island?","options":["The island seemed to move away and the fog rolled in","They found a port","The sea dried up","The mountain spoke"],"answer":0,"hit":"The island seemed to move further away, then a thick fog rolled in.","error":"Remember why the crew had to lower the sails."},{"q":"How did San Borondón appear on some maps?","options":["Sailors reported sightings and drew what they remembered","They photographed it","They moved it","They saw it from a plane"],"answer":0,"hit":"Sailors reported sightings. The captain marked the place on his chart and Guadarfía drew what he remembered.","error":"Think about what Guadarfía and the captain did."}],"questions":[{"q":"The captain marked the place on his chart.","answer":true,"feedback":"After the mist clears, the captain marks the place on his chart and Guadarfía draws the shape he remembers.","hint":"Find out what each character does at dawn."},{"q":"The island was gone when the mist cleared.","answer":true,"feedback":"When the mist clears at dawn, there is only sea in front of the ship.","hint":"Look at what the crew sees after the fog lifts."},{"q":"Guadarfía was the captain of the ship.","answer":false,"feedback":"Guadarfía is the apprentice sailor. The captain is another member of the crew.","hint":"Read how the story introduces Guadarfía."}],"badgeAlt":"Clay shell, a contemporary symbol of La Graciosa"}];
const secondaryCreations=Object.freeze({"tenerife":{"route":1,"title":"Dácil’s letter to Achamán","prompt":"Imagine you are Dácil. Write a letter thanking Achamán for freeing Magec.","structure":["Place and date.","Greet Achamán.","Thank Achamán, recall what happened and explain what Magec’s return means.","Close the letter and sign as Dácil."],"criteria":["Write the letter in the first person from Dácil’s point of view.","Thank Achamán for freeing Magec and stay consistent with the story.","Include the place and date, greeting, body, closing and signature.","Express feelings and reasons clearly, and check your spelling."],"placeholder":"Tenerife, …\n\nDear Achamán,\n\nI am writing to …\n\n…\n\nDácil","lengthLabel":"Suggested length: 120 to 250 words.","minWords":20,"maxWords":0},"gran-canaria":{"route":2,"title":"News from the ravine","prompt":"Write a news report about the events in “Guayarmina and the Tibicena of the Ravine”.","structure":["An informative headline.","A subheading, if it adds useful information.","Opening paragraph: what happened, who was involved, when and where it happened, and how and why it happened.","Main text: explain the events in order of importance."],"criteria":["Use a neutral tone and clear language.","Include a headline, opening paragraph and main text. A subheading is optional.","In the opening, answer what, who, when, where, how and why.","Make clear which details come from the story and which you have added."],"placeholder":"HEADLINE\nOptional subheading\n\nOPENING PARAGRAPH\nWhat happened? Who? When? Where? How? Why?\n\nMAIN TEXT\n…","lengthLabel":"Suggested length: 180 to 350 words.","minWords":20,"maxWords":0},"la-palma":{"route":3,"title":"A story for Acerina to tell","prompt":"Acerina grew into a gifted storyteller. Write a story about Roque Idafe that she could tell to the children of La Palma.","structure":["Title.","Opening: introduce the rock, the setting and the characters.","Conflict: create a problem about remembering or caring for Idafe.","Ending: resolve the conflict and leave readers with a thoughtful message about looking after this heritage."],"criteria":["Set the story around Roque Idafe and keep its connection to the memory of La Palma.","Give the story a clear opening, conflict and ending.","Use language that children can understand.","Present your own story as fiction."],"placeholder":"TITLE\n\nOPENING\nPeople say that, near Roque Idafe…\n\nCONFLICT\n…\n\nENDING\n…","lengthLabel":"Suggested length: 250 to 500 words.","minWords":20,"maxWords":0},"la-gomera":{"route":4,"title":"Gara and Jonay take the stage","prompt":"Write a script for a scene inspired by the legend of Gara and Jonay.","choices":["Gara and Jonay meet and fall in love.","Their families forbid them from seeing each other.","People on La Gomera talk after learning about the tragic ending."],"structure":["Give the scene a title and a setting.","List the characters.","Use stage directions to show movements, gestures, tone or atmosphere.","Put each character’s name before their dialogue."],"criteria":["Develop one of the three suggested scenes.","Make the characters, stage directions and dialogue easy to distinguish.","Stay consistent with the legend and treat the ending sensitively.","Make the scene practical to perform, and revise your writing."],"placeholder":"SCENE TITLE\nSetting: …\nCharacters: …\n\n(Stage directions)\nGARA: …\nJONAY: …","lengthLabel":"Suggested length: 180 to 350 words.","minWords":20,"maxWords":0},"el-hierro":{"route":5,"title":"Feature article: Every drop counts","prompt":"Write a feature article about the importance of water in the Canary Islands.","structure":["Use a headline and opening paragraph to introduce the topic and interest the reader.","Use subheadings to organise the main text: water availability, uses, problems and solutions.","Include the Garoé as part of the history and heritage of El Hierro.","Finish with a conclusion and list at least two sources you used."],"criteria":["Explain why water matters in the Canary Islands, and use information you have checked.","Include a headline, opening paragraph, subheadings, main text, conclusion and sources.","Connect the Garoé to the topic and use suitable sources for scientific claims.","Distinguish facts, explanations and opinions. Write clearly for a general audience."],"placeholder":"HEADLINE\n\nOPENING PARAGRAPH\n…\n\nAVAILABILITY AND USES\n…\n\nPROBLEMS AND SOLUTIONS\n…\n\nTHE GAROÉ\n…\n\nCONCLUSION AND SOURCES\n…","lengthLabel":"Suggested length: 300 to 600 words.","minWords":20,"maxWords":0},"fuerteventura":{"route":6,"title":"A different ending: Making amends","prompt":"Develop an alternative ending. Show how Guise and Ayose put things right, take responsibility and help others.","structure":["Write 150 to 200 words.","Keep Guise and Ayose as the main characters and set the action after their encounter with Mafasca.","Show what the characters do to repair the damage and how it affects their community.","Let the ending’s message emerge naturally from the events."],"criteria":["Keep the ending consistent with the main events of the story.","Show the goatherds acknowledging the damage and doing something to repair it.","Let the consequence and the message follow naturally from the events.","Write 150 to 200 words and check your draft."],"placeholder":"At dawn, Guise and Ayose…","lengthLabel":"Required length: 150 to 200 words.","minWords":150,"maxWords":200},"lanzarote":{"route":7,"title":"Ico’s diary","prompt":"Reread the story and write a diary entry in Ico’s voice. Tell what happened and what she thought and felt during the unfair test.","structure":["Date.","A short title.","Main text: describe events, thoughts and feelings in the first person.","An ending or a closing line."],"criteria":["Write in the first person, from Ico’s point of view.","Include a date, title, main text and closing lines.","Show what happened and what Ico thought and felt.","Stay consistent with the story and reflect on why the test was unfair."],"placeholder":"DATE\nSHORT TITLE\n\nToday …\n\nCLOSING LINES\nIco","lengthLabel":"Suggested length: 180 to 350 words.","minWords":20,"maxWords":0},"la-graciosa":{"route":8,"title":"San Borondón in comic panels","prompt":"Turn “Guadarfía and the Island of San Borondón” into a comic.","structure":["Plan six to ten panels with a beginning, middle and ending.","Combine pictures, narrative captions, speech bubbles and sound effects where helpful.","Show the island appearing through the mist and convey the crew’s uncertainty about what they saw.","Add a title, your name and a note saying which legend inspired the comic."],"criteria":["Make the story clear through the sequence of panels.","Use short, legible text and make clear which character or action it goes with.","Keep the mystery of San Borondón and leave the sighting open to doubt.","Include a title, your name and the legend that inspired the comic."],"placeholder":"TITLE AND AUTHOR\n\nPANEL 1 · Picture: … · Caption: … · Dialogue: …\nPANEL 2 · Picture: … · Caption: … · Dialogue: …\n…\n\nNote: A comic inspired by the legend of San Borondón.","lengthLabel":"Plan six to ten panels.","minWords":20,"maxWords":0}});
const workshopActivities=Object.freeze({"tenerife":{"words":{"title":"Words from the world of the Guanches","intro":"Match the names and find four words or phrases with a similar meaning in the story.","match":{"prompt":"Match each description to a name.","options":["Magec","Achamán","Guayota","Echeyde"],"labels":{"Magec":"Magec","Achamán":"Achamán","Guayota":"Guayota","Echeyde":"Echeyde"},"items":[{"definition":"The deity who represents the Sun in the story.","answer":"Magec"},{"definition":"The lord of the sky whom the community asks for help.","answer":"Achamán"},{"definition":"The being who holds Magec captive inside the volcano.","answer":"Guayota"},{"definition":"The name for Mount Teide in Guanche tradition.","answer":"Echeyde"}]},"fillPrompt":"Find a word or phrase with a similar meaning in the story.","fills":[{"prompt":"dwelt","answers":["lived","vivían","vivian"],"hint":"Look in the first sentence."},{"prompt":"starting a journey","answers":["setting out","set out","comenzar"],"hint":"Look at what Dácil waits to do each morning."},{"prompt":"narrates","answers":["tells","tells us","cuenta"],"hint":"Look at what tradition does in paragraph 5."},{"prompt":"came to the end","answers":["finished","terminar"],"hint":"Look at the last sentence."}]},"research":{"title":"Echeyde in an official source","intro":"Consult the Teide National Park page and find two details that add to the story.","questions":[{"q":"According to the source, what meaning is given to the name Echeyde?","options":["Mountain of mist.","Home of Guayota, the Evil One.","Magec’s path."],"answer":1,"feedback":"The park’s page gives “home of Guayota, the Evil One” as the meaning of Echeyde."},{"q":"According to the source, which feature of the summit represents the plug placed by Achamán?","options":["Los Roques de García.","La Fortaleza.","El Pan de Azúcar."],"answer":2,"feedback":"The source identifies the summit’s final cone, El Pan de Azúcar, as the legendary plug."}],"sources":[{"label":"Government of the Canary Islands: History of Teide National Park","url":"https://www.gobiernodecanarias.org/parquesnacionales/teide/el_parque/historia/"},{"label":"CanariWiki: The early inhabitants of the Canary Islands","url":"https://www3.gobiernodecanarias.org/medusa/wiki/index.php?title=Antiguos_canarios"}]},"creation":{"type":"text","title":"A new title","prompt":"Think of a new title for the story. Try to include the conflict or the return of the light.","placeholder":"My title for the story…","tip":"You could begin with “Dácil and…”. Make the title your own."}},"gran-canaria":{"words":{"title":"Opposites and Canarian words","intro":"Find opposites in the story and match two words used in the Canary Islands.","match":{"prompt":"Match each Canarian word to its definition.","options":["tabaiba","tea"],"labels":{"tabaiba":"tabaiba","tea":"tea"},"items":[{"definition":"A shrub with milky sap that grows in dry or volcanic parts of the Canary Islands.","answer":"tabaiba"},{"definition":"Hard, resin-rich wood from old Canary Island pines, used to make torches.","answer":"tea"}]},"fillPrompt":"Find the opposite in the story.","fills":[{"prompt":"large","answers":["small","pequeño","pequeno"],"hint":"Look at the refrain."},{"prompt":"put out","answers":["lit","lit a torch","encendió","encendio"],"hint":"Look at what Guayarmina did beside the cave."},{"prompt":"darkness","answers":["light","luz"],"hint":"Look at the refrain."},{"prompt":"day","answers":["night","noche"],"hint":"Look in the last paragraph."}]},"research":{"title":"Trace a word through historical sources","intro":"Use the linked historical dictionary to find details that add to the story.","questions":[{"q":"Besides a shaggy dog, which other forms appear in the accounts quoted by the dictionary?","options":["Birds and a calf.","Seahorses and dolphins.","Lizards and fish."],"answer":0,"feedback":"The accounts describe bird forms, including a turkey hen or a hen with chicks, and a calf."},{"q":"According to the accounts, when could tibicenas appear?","options":["Only at midday.","Only during eclipses.","By day and by night."],"answer":2,"feedback":"The historical accounts record appearances both by day and by night."}],"sources":[{"label":"RAE: Historical Dictionary of Canarian Spanish, entry “tibicena”","url":"https://www.rae.es/tdhle/tibicena","originalTitle":"Diccionario histórico del español de Canarias"},{"label":"Academia Canaria de la Lengua: entry “tabaiba”","url":"https://www.academiacanarialengua.org/palabra/tabaiba/","spanishTitle":"“tabaiba”"},{"label":"Academia Canaria de la Lengua: entry “tea”","url":"https://www.academiacanarialengua.org/palabra/tea/","spanishTitle":"“tea”"}]},"creation":{"type":"drawing","title":"Draw the tibicena","prompt":"Draw the creature as described in the story: large, with black fur and eyes like glowing embers.","placeholder":"You can also use this space to describe how you imagine the tibicena…","tip":"Draw with your finger or mouse. You can undo a change, clear the drawing or save it to your device."}},"la-palma":{"words":{"title":"Words from Benahoare","intro":"Match places, people and objects from the story to their meanings.","match":{"prompt":"Match each word to its meaning in the story.","options":["Benahoare","Idafe","Abora","vasija"],"labels":{"Benahoare":"Benahoare","Idafe":"Idafe","Abora":"Abora","vasija":"pot"},"items":[{"definition":"An Indigenous name for the island we now call La Palma.","answer":"Benahoare"},{"definition":"The great rock in the Caldera that seemed to hold up the sky.","answer":"Idafe"},{"definition":"A deity mentioned in the traditions of La Palma.","answer":"Abora"},{"definition":"A container in which the group carried food.","answer":"vasija"}]},"fillPrompt":"Find a phrase in the story with a similar meaning.","fills":[{"prompt":"remains upright","answers":["still stands","still stood tall","Idafe still stands","sigue en pie","continuaba erguido"],"hint":"The refrain tells you what Idafe is doing."},{"prompt":"remember it so it is not forgotten","answers":["keep its memory alive","we keep its memory alive","guardamos su memoria","guardar la memoria","conservar la memoria"],"hint":"Look at the second part of the refrain."}]},"research":{"title":"Investigate the landscape of Aceró","intro":"Consult the park’s archaeology page and look for details that add to the story.","questions":[{"q":"What did the Benahoarita people call the territory of the Caldera de Taburiente?","options":["Erbania.","Aceró.","Echeyde."],"answer":1,"feedback":"The park’s page says the Caldera lay in the territory known as Aceró."},{"q":"Which archaeological remains does the park’s page list?","options":["Pottery, rock engravings and stone tools.","Parchment and bound books.","Roman coins and glass objects."],"answer":0,"feedback":"The source mentions pottery, rock engravings and stone tools as archaeological evidence."}],"sources":[{"label":"Government of the Canary Islands: Archaeology of the Caldera de Taburiente","url":"https://www.gobiernodecanarias.org/parquesnacionales/caldera_de_taburiente/el_parque/valores_naturales/"}]},"creation":{"type":"text","title":"A voice to keep the memory alive","prompt":"Write a new refrain of one or two sentences to remember Idafe.","placeholder":"Idafe…","tip":"Repeat a word if you want to give the refrain a rhythm."}},"la-gomera":{"words":{"title":"From the spring to the summit","intro":"Match four words from the voyage and landscape.","match":{"prompt":"Match each word or phrase to its definition.","options":["manantial","odres","cumbre","eco"],"labels":{"manantial":"spring","odres":"goatskin bags","cumbre":"summit","eco":"echo"},"items":[{"definition":"A place where water naturally comes out of the ground.","answer":"manantial"},{"definition":"Containers made from animal skin that help Jonay float in the legend.","answer":"odres"},{"definition":"The highest part of a mountain.","answer":"cumbre"},{"definition":"A sound you hear again after it bounces off a surface.","answer":"eco"}]},"fillPrompt":"Write a word with the opposite meaning.","fills":[{"prompt":"hostility","answers":["friendship","goodwill","affection","amistad"],"hint":"Think of a relationship built on care and support."},{"prompt":"stay silent","answers":["speak","talk","speak up","hablar","decir"],"hint":"Think of what people do in a conversation."}]},"research":{"title":"Investigate the archaeology of La Gomera","intro":"Use the biosphere reserve’s archaeology page to find two details that add to the story.","questions":[{"q":"According to the source, what was the main economic activity of La Gomera’s early inhabitants?","options":["Ocean-going navigation.","Metal mining.","Keeping livestock."],"answer":2,"feedback":"The source describes an economy based mainly on keeping livestock, alongside farming and gathering."},{"q":"Which site does the source mention for its sacrificial altars?","options":["El Roque Nublo.","La Fortaleza de Chipude.","La Cueva de los Verdes."],"answer":1,"feedback":"La Fortaleza de Chipude is listed among sites with sacrificial altars."}],"sources":[{"label":"La Gomera Biosphere Reserve: Archaeology","url":"https://biosfera.lagomera.es/arqueologia/"},{"label":"Juan Francisco Navarro: Archaeological research on La Gomera","url":"https://iehcan.com/wp-content/uploads/2016/12/1-Navarro-2016.pdf"}]},"creation":{"type":"text","title":"A sentence to start a conversation","prompt":"Write a sentence that Gara or Jonay could say to ask their families to listen to one another.","placeholder":"We need you to…","tip":"Use a respectful tone and make a specific suggestion."}},"el-hierro":{"words":{"title":"Words about water","intro":"Find out how the Garoé helped the community.","match":{"prompt":"Match each word or phrase to its definition.","options":["Garoé","piletas","niebla","vasija"],"labels":{"Garoé":"Garoé","piletas":"stone basins","niebla":"mist","vasija":"jar"},"items":[{"definition":"The tree associated with collecting water on El Hierro.","answer":"Garoé"},{"definition":"Hollows in the rock where drops of water collected.","answer":"piletas"},{"definition":"A low cloud formed by tiny drops of water.","answer":"niebla"},{"definition":"A container used to carry water.","answer":"vasija"}]},"fillPrompt":"Write an opposite from the story or work one out.","fills":[{"prompt":"appear","answers":["disappear","disappeared","vanish","desaparecieron","desapareció","desaparecio"],"hint":"The story of the Garoé never did this."},{"prompt":"hide","answers":["reveal","show","uncover","revealing","mostrar","revelar","descubrir"],"hint":"This is the opposite of keeping something secret."}]},"research":{"title":"The historic Garoé tree","intro":"Use the official El Hierro source to find two details that add to the story.","questions":[{"q":"According to the source, what kind of tree was the historic Garoé?","options":["A til (Canary laurel).","A pine.","A palm."],"answer":0,"feedback":"The official account identifies the historic Garoé as a til, a Canary laurel."},{"q":"In which year was the tree that replaced the historic Garoé planted?","options":["In 1496.","In 1949.","In 2009."],"answer":1,"feedback":"The present tree was planted in 1949, several centuries after the historic tree fell."}],"sources":[{"label":"El Hierro official tourism website: The Garoé Tree","url":"https://elhierro.travel/museos-y-visitas-de-interes/el-hierro/arbol-garoe/","originalTitle":"Árbol Garoé"}]},"creation":{"type":"text","title":"A slogan to save water","prompt":"Write a short slogan that encourages people to save water.","placeholder":"Drop by drop…","tip":"A good slogan is short, clear and easy to remember."}},"fuerteventura":{"words":{"title":"Words from the path","intro":"Match words from the story to their meanings and find their opposites.","match":{"prompt":"Match each word to its definition.","options":["hoguera","chispa","gofio","sendero"],"labels":{"hoguera":"campfire","chispa":"spark","gofio":"gofio","sendero":"path"},"items":[{"definition":"A fire lit outdoors.","answer":"hoguera"},{"definition":"A tiny glowing particle that jumps from a fire.","answer":"chispa"},{"definition":"A Canarian food made from roasted and ground grain.","answer":"gofio"},{"definition":"A narrow way the goatherds walk along.","answer":"sendero"}]},"fillPrompt":"Write an opposite. You can work it out even if it is not written in the story.","fills":[{"prompt":"appeared","answers":["disappeared","vanished","went away","desapareció","desaparecio"],"hint":"The light faded until it did this."},{"prompt":"night","answers":["day","daytime","dawn","día","dia","amanecer"],"hint":"The goatherds returned at this time."},{"prompt":"old","answers":["new","nueva","nuevo"],"hint":"Think of the opposite of something that has been around a long time."}]},"research":{"title":"Tradition and archaeological evidence","intro":"Read the archaeological designation for Barranco del Cavadero. Investigate one example of pre-European evidence that adds to what you know from the story.","questions":[{"q":"What material were the inscriptions at Barranco del Cavadero carved into?","options":["Sheets of parchment.","Wooden boards.","Basalt blocks on the ravine walls."],"answer":2,"feedback":"The inscriptions were carved into basalt blocks on the walls of the ravine."},{"q":"Which two kinds of letter-like engravings does the official gazette identify at this site?","options":["Libyco-Berber and pseudo-Latin.","Egyptian and Latin hieroglyphs.","Greeks and Phoenicians."],"answer":0,"feedback":"The document identifies Libyco-Berber and pseudo-Latin characters."}],"sources":[{"label":"Archaeological Museum of Fuerteventura","url":"https://museosfuerteventura.com/museos/museo-arqueologico-de-fuerteventura/"},{"label":"Government of the Canary Islands: Archaeological site of Barranco del Cavadero","url":"https://www.gobiernodecanarias.org/boc/2008/078/003.html"}]},"creation":{"type":"text","title":"A different ending: Making amends","prompt":"Write two or three sentences for an alternative ending in which the goatherds repair the damage and help others.","placeholder":"At dawn, Guise and Ayose…","tip":"Show what they do to repair the damage and what they learn from it."}},"lanzarote":{"words":{"title":"Words for talking about fairness","intro":"Match four words that help explain Ico’s situation.","match":{"prompt":"Match each word or phrase to its definition.","options":["consejo","linaje","esponja","solidaridad"],"labels":{"consejo":"council","linaje":"family line","esponja":"sponge","solidaridad":"solidarity"},"items":[{"definition":"A group that makes decisions in the story.","answer":"consejo"},{"definition":"The generations of people in a family.","answer":"linaje"},{"definition":"An object that helps Ico breathe when it is wet.","answer":"esponja"},{"definition":"The support people give one another when they need help.","answer":"solidaridad"}]},"fillPrompt":"Write a word or phrase with the opposite meaning.","fills":[{"prompt":"enter","answers":["leave","go out","exit","walk out","walked out","salir"],"hint":"What did Ico do when the door opened?"},{"prompt":"damp","answers":["dry","seca","seco"],"hint":"Think of something that has no moisture in it."}]},"research":{"title":"Follow a historical interpretation","intro":"Read the linked study to find out how researchers have interpreted the help Ico received.","questions":[{"q":"Which researcher interpreted the older woman’s advice as an established practice?","options":["Espinosa.","Álvarez Delgado.","Torriani."],"answer":1,"feedback":"The study attributes this interpretation to Álvarez Delgado."},{"q":"Which activity did the researcher associate with the method?","options":["Hunting shearwaters.","Making pottery.","Sailing."],"answer":0,"feedback":"Álvarez Delgado connected the method with a practice known to people who hunted shearwaters."}],"sources":[{"label":"Lanzarote Digital Archive: Avendaño’s Adventure and the Legend of Ico","url":"https://bk.memoriadelanzarote.com/media/docs/items/20110708111921AVENDAO-E-ICO.pdf","originalTitle":"La aventura de Avendaño y la leyenda de Ico"}]},"creation":{"type":"text","title":"Answer Ico","prompt":"Answer Ico’s question. Why should anyone have to put themselves in danger to prove who they are?","placeholder":"Nobody should have to put themselves in danger because…","tip":"Give a reason for your view and express it respectfully."}},"la-graciosa":{"words":{"title":"Words from the voyage","intro":"Match four words from the voyage and find opposites in the story.","match":{"prompt":"Match each word or phrase to its definition.","options":["grumete","pergamino","bruma","carta náutica"],"labels":{"grumete":"apprentice sailor","pergamino":"parchment","bruma":"mist","carta náutica":"chart"},"items":[{"definition":"A young person who works and learns on a ship.","answer":"grumete"},{"definition":"A material that people used to draw maps on.","answer":"pergamino"},{"definition":"Thin fog that makes it difficult to see the horizon.","answer":"bruma"},{"definition":"A map used to guide a ship's course.","answer":"carta náutica"}]},"fillPrompt":"Find the opposite in the story.","fills":[{"prompt":"appear","answers":["disappear","disappeared","desaparecía","desapareció","desaparecio"],"hint":"Listen to the end of the refrain."},{"prompt":"near","answers":["far away","further away","far","further","lejos","lejos de"],"hint":"The island seemed to move this way as the ship sailed on."}]},"research":{"title":"Explore the origins of San Borondón","intro":"Read the study to find two details about how the legend began and spread.","questions":[{"q":"According to the study, which figure is linked to the origins of this geographical myth?","options":["A Roman sailor called Taro.","A mapmaker from La Graciosa.","The Irish monk Saint Brendan."],"answer":2,"feedback":"The study traces the geographical myth to the tradition about the Irish monk Saint Brendan."},{"q":"Between which centuries did travellers’ accounts play a particular role in spreading the myth?","options":["Between the 16th and 19th centuries.","Between the 9th and 12th centuries.","Between the 20th and 21st centuries."],"answer":0,"feedback":"The study highlights travellers’ accounts from the 16th to the 19th century."}],"sources":[{"label":"Universidad Complutense de Madrid: Revisiting the Geographical Myth of San Borondón","url":"https://revistas.ucm.es/index.php/RFRM/article/download/45706/42966/73431","originalTitle":"Revisión del mito geográfico de San Borondón"},{"label":"CanariWiki: The Island of La Graciosa","url":"https://www3.gobiernodecanarias.org/medusa/wiki/index.php/Isla_de_La_Graciosa","originalTitle":"Isla de La Graciosa"}]},"creation":{"type":"text","title":"The mapmaker’s note","prompt":"Write a short note that Guadarfía could place beside his drawing of the island he thought he saw.","placeholder":"Through the mist we saw…","tip":"Describe what he remembers and make clear what remains uncertain."}}});
const routeMarkup=["<section class=\"route\" id=\"route-tenerife\" aria-labelledby=\"title-tenerife\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Tenerife</p><h2 id=\"title-tenerife\">Dácil and the Return of Magec</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_tenerife.webp\" alt=\"A young woman and three other people look towards a light in the sky near Mount Teide. Fictional scene from the story of Dácil and Magec.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · Tenerife</p><p class=\"story-intro\">A story set in the world of the Guanches, inspired by Echeyde, Guayota, Magec and Achamán.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Achamán, bring back Magec and bring back the light”</div><p>When the Guanches lived among ravines and valleys, Dácil looked after goats near Echeyde. Each dawn she waited for the first ray of Magec, the Sun, before setting out.</p><p>But one morning, the light did not come. A black cloud covered the mountain, and the ground shook beneath their feet. The elders remembered the story of Guayota, the being who lived inside the volcano. According to tradition, he had captured Magec and was keeping him hidden in the darkness.</p><p>The cold crept into the caves. Dácil gathered the children beside the fire, and they all repeated: “Achamán, bring back Magec and bring back the light.”</p><p>A deep rumbling came from the summit. The clouds turned red, and a great stone rolled down to the mouth of Echeyde. Dácil held her little brother close while the people of the village called for help from Achamán, lord of the sky.</p><p>Tradition tells us that Achamán came down from above, defeated Guayota and freed Magec. Then he sealed the entrance to the volcano with an enormous rock so that the being of fire could not escape.</p><p>Then a golden line appeared behind Echeyde. First it lit up the summit, then the slopes and, last of all, Dácil’s face. The goats came out of their shelter, and the cold began to fade.</p><p>From that day on, Dácil told the story whenever the volcano seemed to be waking. And when she finished, every voice repeated: “Achamán, bring back Magec and bring back the light.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>Historical sources such as Espinosa (1594) link Echeyde with Guayota. Read these accounts critically because they were written after the conquest. The story of Magec’s capture and release became widely known through later retellings. Dácil is a Guanche name passed down through literature. The Dácil in this story is an original character. Her actions and dialogue were written for MitoMapa.</p><section class=\"source-traceability\" data-source-route=\"tenerife\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> A modern account of the legend associated with Mount Teide tells how Achamán freed Magec from Guayota.</p><p><strong>Source:</strong></p><ul><li>Government of the Canary Islands (n.d.). <a href=\"https://www.gobiernodecanarias.org/parquesnacionales/teide/el_parque/historia/\" target=\"_blank\" rel=\"noopener noreferrer\">History of Teide National Park</a> <small class=\"source-original\">[<span lang=\"es\">Historia del Parque Nacional del Teide</span>]</small>. See “The Legend of Guayota and the Sugar Loaf” <small class=\"source-original\">[<span lang=\"es\">La leyenda de Guayota y el Pan de Azúcar</span>]</small>.</li></ul><p>This page records a modern version. The date of individual episodes remains uncertain. Distinguish the earliest accounts of Echeyde and Guayota from later retellings.</p><p><strong>About this version:</strong> This story’s Dácil is an original character distinct from the Dácil in Antonio de Viana’s poem. Her work with the herd, her brother, the dialogue and the refrain were created for MitoMapa.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-tenerife\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"tenerife\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-tenerife\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"tenerife\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_tenerife.webp\" alt=\"Clay vessel from Tenerife\"><div><span>Piece added to your passport</span><strong>Light piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-gran-canaria\" aria-labelledby=\"title-gran-canaria\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Gran Canaria</p><h2 id=\"title-gran-canaria\">Guayarmina and the Tibicena of the Ravine</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_gran-canaria.webp\" alt=\"A young woman crouches on a path through a ravine. Three people watch behind her. Fictional scene from the story of Guayarmina.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">legendary tale · Gran Canaria</p><p class=\"story-intro\">A story set in ancient Gran Canaria, inspired by Acorán and the tibicenas.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Together in the light, fear grows small”</div><p>In ancient Gran Canaria, Guayarmina led a small herd along a path through a ravine. As the sun set, she gathered the goats beside a cave and lit a torch.</p><p>Suddenly, she heard a growl. A figure covered in black fur appeared among the tabaibas. It had the shape of a large dog, and its eyes looked like two glowing embers. Guayarmina remembered the stories of the tibicenas, beings who wandered through caves and lonely places.</p><p>Fear urged her to run, but she called to the other goatherds. Together they raised their torches and said: “Together in the light, fear grows small.”</p><p>The tibicena circled the fire once. Then it went round again. The third time round, it stopped in front of Guayarmina. She asked Acorán for protection and stayed beside the herd.</p><p>When the sky began to grow light, the creature backed away until it disappeared among the rocks. Large footprints remained on the ground, mixed with the tracks of goats.</p><p>Guayarmina told the people of the village what had happened. The elders could not say for certain what she had seen, but they were thankful that no one had ventured into the ravine alone.</p><p>From then on, whenever night caught the goatherds by surprise, they gathered the herd, lit the torch and remembered: “Together in the light, fear grows small.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>Acorán appears in historical accounts of Gran Canaria. Tibicenas are figures from traditional beliefs and have been described in different ways, including as a large dark dog. Guayarmina is an Indigenous name from Gran Canaria. The protagonist is a fictional character. The camp and the creature’s three circuits were created for this story.</p><section class=\"source-traceability\" data-source-route=\"gran-canaria\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> Accounts describe tibicenas in a variety of animal forms. Written accounts from after the conquest describe one form as a large dog.</p><p><strong>Source:</strong></p><ul><li>Corrales Zumbado, C., and Corbella Díaz, D. (2013). <a href=\"https://www.rae.es/tdhle/tibicena\" target=\"_blank\" rel=\"noopener noreferrer\">Historical Dictionary of Canarian Spanish: tibicena</a> <small class=\"source-original\">[<span lang=\"es\">Diccionario histórico del español de Canarias: tibicena</span>]</small>. The entry “tibicena” cites Gómez Escudero, 1978 edition, p. 439, and Marín de Cubas, 1993 edition, book II, ch. 18, p. 204.</li></ul><p>The chroniclers’ religious language also reflects their Christian perspective. These sources record beliefs about the creature. The story uses one of the forms described in those accounts.</p><p><strong>About this version:</strong> The story’s Guayarmina is fictional and shares her name with a historical figure. The herd, the creature’s three circuits, the footprints, Guayarmina’s appeal to Acorán and the goatherds’ response were written for the story.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-gran-canaria\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"gran-canaria\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-gran-canaria\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"gran-canaria\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_gran_canaria.webp\" alt=\"Clay vessel from Gran Canaria\"><div><span>Piece added to your passport</span><strong>Memory piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-la-palma\" aria-labelledby=\"title-la-palma\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Palma</p><h2 id=\"title-la-palma\">Acerina and the Rock That Held Up the Sky</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-palma.webp\" alt=\"An adult and a girl look at a tall rock formation among mountains and clouds. An imagined view of Roque Idafe from Acerina’s story.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · La Palma</p><p class=\"story-intro\">A story set in Benahoare, inspired by Abora and the rock of Idafe.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Idafe still stands; we keep its memory alive”</div><p>In Benahoare, the island we now call La Palma, Acerina looked up whenever she entered the Caldera. There stood Idafe, a great rock that seemed to hold up the sky.</p><p>One morning, she went with her grandfather and other people from the village. They carried small pots of food for an ancient ceremony. Her grandfather explained that this place was connected with Abora and the memory of their ancestors.</p><p>When they arrived, they all said: “Idafe still stands; we keep its memory alive.”</p><p>Suddenly, the ground trembled. Several stones tumbled down the slope, and Acerina thought the rock was going to fall. Her grandfather took her hand, and the group moved away from the cliff.</p><p>The noise stopped. Idafe still stood tall against the sky. Acerina left her pot in the place she was shown and promised to learn the words of the ceremony so that they would not be forgotten.</p><p>The years passed. Acerina became a gifted storyteller. She took the children to a safe spot where they could look at the rock, and told them what she had experienced.</p><p>At the end, they all looked at the stone and repeated: “Idafe still stands; we keep its memory alive.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>The chronicles connect Roque Idafe with ritual practices of the Indigenous people of La Palma and record the name Abora. The name Acerina appears in La Palma’s legends. This story presents its own Acerina. Her grandfather, the tremor and her promise to become a storyteller were created for this version.</p><section class=\"source-traceability\" data-source-route=\"la-palma\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> A chronicle records fears that Idafe might fall and describes offerings left by the rock. The park’s account places these traditions in the Caldera.</p><p><strong>Source:</strong></p><ul><li>Trapero, M., and Santana Martel, E. (n.d.). <a href=\"https://guanchismos.ulpgc.es/item/12902\" target=\"_blank\" rel=\"noopener noreferrer\">Dictionary of Canary Islands Place Names: Idafe</a> <small class=\"source-original\">[<span lang=\"es\">Diccionario de toponimia de Canarias: Idafe</span>]</small>. The entry “Idafe” cites Abreu Galindo, 1977 edition, p. 270.</li><li>Government of the Canary Islands (n.d.). <a href=\"https://www.gobiernodecanarias.org/parquesnacionales/caldera_de_taburiente/el_parque/valores_naturales/arqueologia/index.html\" target=\"_blank\" rel=\"noopener noreferrer\">Caldera de Taburiente: Archaeology</a> <small class=\"source-original\">[<span lang=\"es\">Caldera de Taburiente: Arqueología</span>]</small>. See the sections on the Benahoarita people and rituals at Idafe.</li></ul><p>The cited passage leaves the details of the ceremony and its possible connection to Abora unverified. Treat the ceremony in the story as fiction.</p><p><strong>About this version:</strong> This Acerina differs from the character in other versions. Her grandfather, the pots, the tremor, the promise and the refrain are fictional. “Holding up the sky” is an image created for the story.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-palma\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-palma\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-palma\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-palma\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_la_palma.webp\" alt=\"Clay vessel from La Palma\"><div><span>Piece added to your passport</span><strong>Idafe piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-la-gomera\" aria-labelledby=\"title-la-gomera\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Gomera</p><h2 id=\"title-la-gomera\">Gara and Jonay, Two Voices on the Summit</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-gomera.webp\" alt=\"A young woman holds her hands open as she speaks to two groups on opposite sides of a ravine. Fictional scene from the story of Gara and Jonay.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · La Gomera</p><p class=\"story-intro\">A children’s adaptation of the legend of Gara and Jonay from La Gomera.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Neither the sea nor the ravine can silence two hearts”</div><p>Gara lived in Agulo and knew every sound of the ravines. One day, she looked at her reflection in the spring and heard a warning: she must keep away from fire.</p><p>Across the sea, in Tenerife, lived Jonay. To reach La Gomera, he used goatskin bags to help him float. He swam for hours until he reached the shore.</p><p>When Gara and Jonay met, they walked among the palm trees and talked until the moon appeared. The two of them repeated: “Neither the sea nor the ravine can silence two hearts.”</p><p>But the families feared the old warning. They said that Gara’s water and Jonay’s fire must never meet. The young pair fled towards the summit and asked Orahan for help.</p><p>Their families searched for them in the mist. When at last they found them, the legend tells us that Gara and Jonay’s story came to a sad end. Their names were joined for ever in the mountain’s name: Garajonay.</p><p>In time, people came to understand that hostility and failing to listen had caused great pain. From then on, whenever two communities argued, someone remembered Gara and Jonay before closing the door to dialogue.</p><p>And the summit echoed back: “Neither the sea nor the ravine can silence two hearts.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>The legend of Gara and Jonay has many versions. In widely told versions, Jonay crosses from Tenerife, their families oppose them and their story ends tragically. Orahan appears in accounts of beliefs on La Gomera. The wording and narrative details of this story were written for MitoMapa.</p><section class=\"source-traceability\" data-source-route=\"la-gomera\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> Virgilio Brito’s version, recorded by Trapero, includes Jonay’s journey using skins to stay afloat, the couple’s love and their tragic end. Gara’s reflection and the contrast between water and fire also appear in Los Chorros de Epina, published by Spain’s Ministry of Agriculture, Fisheries and Food.</p><p><strong>Sources:</strong></p><ul><li>Trapero, M. (1984). <a href=\"https://mdcs.ulpgc.es/files/original/a8601b5c5852953b6ae2c89a8016b0c6c2f7365a.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">The Legend of Gara and Jonay on La Gomera</a> <small class=\"source-original\">[<span lang=\"es\">La leyenda de Gara y Jonay en La Gomera</span>]</small>. Aguayro, 153, pp. 4–6. Virgilio Brito’s version appears on pp. 5–6.</li><li>Navarro Mederos, J. F. (2016). <a href=\"https://iehcan.com/wp-content/uploads/2016/12/1-Navarro-2016.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">Archaeology on La Gomera: From Past to Present</a> <small class=\"source-original\">[<span lang=\"es\">Arqueología en La Gomera: lo que va de ayer a hoy</span>]</small>. pp. 13–38.</li><li>Ministry of Agriculture, Fisheries and Food (n.d.). <a href=\"https://caminosnaturales.es/es/red-de-caminos-naturales/poi-detalle/ID.07.06.03.15/733f2db0-312c-4386-aec1-d79cf82d3ab6\" target=\"_blank\" rel=\"noopener noreferrer\">The Epina Springs</a> <small class=\"source-original\">[<span lang=\"es\">Los Chorros de Epina</span>]</small>. Caminos Naturales. See the section on the legend of Gara and Jonay. <small class=\"source-consultation\">Identified during the supplementary review on 1 November 2026. Consultation during the writing of the story is unconfirmed.</small></li></ul><p>The cited version by Brito omits the water and fire motif. Other publications include it, but the motif’s origin, age and direct source in this story remain unconfirmed.</p><p><strong>About this version:</strong> This version simplifies the events and leaves the tragic ending implicit. The refrain, the reflection on dialogue and the appeal to Orahan were written for this retelling.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-gomera\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-gomera\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-gomera\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-gomera\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_la_gomera.webp\" alt=\"Clay vessel from La Gomera\"><div><span>Piece added to your passport</span><strong>Meeting piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-el-hierro\" aria-labelledby=\"title-el-hierro\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">El Hierro</p><h2 id=\"title-el-hierro\">Agarfa and the Drops of the Garoé</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_el-hierro.webp\" alt=\"A girl and two adults collect water in soft-sided containers under a tree in the mist. Fictional scene from the story of Agarfa and the Garoé.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · El Hierro</p><p class=\"story-intro\">A story set among the indigenous people of El Hierro, the Bimbapes, and inspired by the Garoé tree.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Branch by branch, drop by drop, the Garoé gives us its water”</div><p>When the Bimbapes lived on El Hierro, Agarfa walked to the Garoé every morning. The mist became tangled in its branches and turned into drops that fell into stone basins.</p><p>The whole community depended on that water. Agarfa filled the jars slowly so as not to waste any, repeating: “Branch by branch, drop by drop, the Garoé gives us its water.”</p><p>One day, unfamiliar sails appeared on the horizon. The older people feared that the newcomers would find the tree and take control of the water source.</p><p>They covered the path with branches and asked Agarfa to carry the jars along another route. The girl made her way through the mist without revealing where the Garoé stood.</p><p>For many days, they kept the secret. Traditional stories give different accounts of how the tree was later discovered. They also tell of a great storm that brought it down many years later.</p><p>But the story of the Garoé did not disappear. Families kept telling how a tree could comb the mist and turn it into water for a whole island.</p><p>When they remembered it, everyone would say: “Branch by branch, drop by drop, the Garoé gives us its water.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>The Garoé was a real tree associated with collecting water from mist. Traditional accounts tell how people kept the tree a secret and how the secret was revealed. They also remember the tree falling in a storm. Agarfa is a Bimbape name passed down in El Hierro’s traditions. The story presents its own Agarfa and invents the routes she uses to conceal the path.</p><section class=\"source-traceability\" data-source-route=\"el-hierro\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> The Garoé is associated with collecting water from mist. A modern account of the legend includes Agarfa and the concealment of the tree.</p><p><strong>Source:</strong></p><ul><li>Government of the Canary Islands (n.d.). <a href=\"https://www3.gobiernodecanarias.org/medusa/wiki/index.php?title=Leyenda_del_garo%C3%A9\" target=\"_blank\" rel=\"noopener noreferrer\">The Legend of the Garoé</a> <small class=\"source-original\">[<span lang=\"es\">Leyenda del garoé</span>]</small>. CanariWiki. See “Historia”.</li><li>El Hierro Travel (n.d.). <a href=\"https://elhierro.travel/museos-y-visitas-de-interes/el-hierro/arbol-garoe/\" target=\"_blank\" rel=\"noopener noreferrer\">The Garoé Tree</a> <small class=\"source-original\">[<span lang=\"es\">Árbol Garoé</span>]</small>. See “The Sacred Tree of El Hierro” <small class=\"source-original\">[<span lang=\"es\">El árbol sagrado de El Hierro</span>]</small>.</li></ul><p>Separate the natural process of collecting water from mist from the events told in the legend. The age of those details remains uncertain.</p><p><strong>About this version:</strong> Agarfa is portrayed here as a child who protects the path, a different character from the Agarfa in the linked account. Her route, the conversations and the refrain were created for this story.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-el-hierro\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"el-hierro\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-el-hierro\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"el-hierro\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_el_hierro.webp\" alt=\"Clay vessel from El Hierro\"><div><span>Piece added to your passport</span><strong>Mist piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-fuerteventura\" aria-labelledby=\"title-fuerteventura\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Fuerteventura</p><h2 id=\"title-fuerteventura\">The Light of Mafasca on the Path</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_fuerteventura.webp\" alt=\"A woman and a girl watch a small light in a rocky landscape at dusk. Fictional scene from the story of the light of Mafasca.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · Fuerteventura</p><p class=\"story-intro\">A story inspired by one version of the light of Mafasca, an oral tradition from Fuerteventura. This version includes a Christian cross; it does not establish when the legend as a whole began.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Light of Mafasca, I won’t follow you: I’m going back along the path”</div><p>Long ago, two goatherds called Guise and Ayose were returning with their goats along a path on Fuerteventura. The night was cold, and the wind blew out every spark.</p><p>Beside the path, they found an old wooden cross. Without thinking, they broke off a piece and used it to light a fire. They warmed the gofio and prepared to carry on.</p><p>Then a pale light came out of the flames. It was not large, but it floated above the stones. The goatherds remembered the tales of Mafasca and said: “Light of Mafasca, I won’t follow you: I’m going back along the path.”</p><p>They walked quickly. The light followed them. They stopped, and the light stopped too. Guise and Ayose realised that they had used a cross without respecting what it meant.</p><p>They promised to return at dawn, repair the cross and never break off any more wood from that place. At that moment, the light grew smaller until it disappeared.</p><p>The next day, they kept their promise. Afterwards, they told the story to other goatherds so that no one would do the same thing.</p><p>From then on, whenever a light flickered in the night, they remembered: “Light of Mafasca, I won’t follow you: I’m going back along the path.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>Fuerteventura has several versions and accounts of the light of Mafasca, including stories collected in Tindaya. Some versions include the burning of a cross. This Christian motif tells us little about when the wider tradition began. The location of an account near Tindaya is insufficient evidence of Indigenous origins or continuity of religious practice. This story retells the version involving a cross and leaves historical explanations for the light open. Guise and Ayose were names used by the Maho people of Fuerteventura. Here, they name fictional goatherds distinct from the historical leaders.</p><p><a href=\"https://www.cabildofuer.es/documentos/Patrimonio_cultural/jornadas_ftv_lzt/volumenes/15_jornadas_ftv_lzt_tomo2.pdf#page=285\" target=\"_blank\" rel=\"noopener\">See Carreras Navarro (2016), <span lang=\"es\">La Luz de Mafasca</span>, pp. 285–310</a>.</p><section class=\"source-traceability\" data-source-route=\"fuerteventura\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> Oral accounts of Mafasca describe the burning of a cross and the appearance of the light. Versions and explanations vary.</p><p><strong>Source:</strong></p><ul><li>Carreras Navarro, J. (2016). <a href=\"https://www.cabildofuer.es/documentos/Patrimonio_cultural/jornadas_ftv_lzt/volumenes/15_jornadas_ftv_lzt_tomo2.pdf#page=293\" target=\"_blank\" rel=\"noopener noreferrer\">The Light of Mafasca</a> <small class=\"source-original\">[<span lang=\"es\">La Luz de Mafasca</span>]</small>. pp. 285–310. Accounts involving a cross appear on pp. 293 and 297–298.</li></ul><p>The cross offers insufficient evidence to date the whole tradition. The accounts collected near Tindaya leave its possible Indigenous origins unverified. The cause of the light remains open in the story.</p><p><strong>About this version:</strong> Guise and Ayose are fictional goatherds who share their names with historical leaders. The gofio, the dialogue, the promise to repair the cross and the refrain were chosen for this retelling.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-fuerteventura\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"fuerteventura\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-fuerteventura\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"fuerteventura\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_fuerteventura.webp\" alt=\"Clay vessel from Fuerteventura\"><div><span>Piece added to your passport</span><strong>Mafasca piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-lanzarote\" aria-labelledby=\"title-lanzarote\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">Lanzarote</p><h2 id=\"title-lanzarote\">Ico and the Trial by Smoke</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_lanzarote.webp\" alt=\"A young woman speaks to a seated group in a volcanic landscape. An older woman stands beside her. Fictional scene from Ico’s story.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">legendary tale · Lanzarote</p><p class=\"story-intro\">A children’s adaptation of the story of Princess Ico in ancient Lanzarote.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“The truth does not need an unfair test”</div><p>Ico lived in ancient Lanzarote. She was the daughter of Zonzamas and Fayna. Some members of the council distrusted her because her skin was lighter, and they decided to put her on the test.</p><p>They prepared a room where green branches would be burnt to fill it with smoke. An old woman knew that this decision was unfair. Before the test, she gave Ico a wet sponge and explained how to breathe through it.</p><p>Ico put the sponge away and thought: “The truth does not need an unfair test.”</p><p>The smoke began to fill the room. Ico crouched down, covered her mouth with the damp sponge and waited. When they opened the door, she walked out.</p><p>The council then recognised her place in the family line. Ico thanked the old woman for her help, but she did not celebrate the test. She looked at those who had judged her and asked why anyone should have to put themselves in danger to prove who they were.</p><p>No one knew how to answer. Intelligence and solidarity had saved Ico, but her question stayed in the island’s memory.</p><p>Since then, whenever her story is told, many voices repeat: “The truth does not need an unfair test.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>Chroniclers recorded the story of Ico, and later versions retold it. The trial by smoke and the help of an older woman recur, though the details vary. Ico’s words and her final question were written for MitoMapa.</p><section class=\"source-traceability\" data-source-route=\"lanzarote\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> Abreu Galindo’s account includes the trial by smoke, the help of an older woman and the sponge. Pérez Saavedra reproduces and studies this account.</p><p><strong>Sources:</strong></p><ul><li>Pérez Saavedra, F. (1995). <a href=\"https://bk.memoriadelanzarote.com/media/docs/items/20110708111921AVENDAO-E-ICO.pdf#page=19\" target=\"_blank\" rel=\"noopener noreferrer\">Avendaño’s Adventure and the Legend of Ico</a> <small class=\"source-original\">[<span lang=\"es\">La aventura de Avendaño y la leyenda de Ico</span>]</small>. Yearbook of Atlantic Studies <small class=\"source-original\">[<span lang=\"es\">Anuario de Estudios Atlánticos</span>]</small>, 41, pp. 207–226. The trial and the older woman’s help are discussed on pp. 223–224.</li></ul><p>The study discusses Ico’s parentage and records the claim that Avendaño was her biological father. The story simplifies her parentage by calling her the daughter of Zonzamas and Fayna. Her genealogy remains unverified.</p><p><strong>About this version:</strong> This retelling simplifies the conflict and places Ico at the centre. Her words, her question to the council and the refrain were written for this version.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-lanzarote\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"lanzarote\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-lanzarote\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"lanzarote\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_lanzarote.webp\" alt=\"Clay vessel from Lanzarote\"><div><span>Piece added to your passport</span><strong>Ico piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>","<section class=\"route\" id=\"route-la-graciosa\" aria-labelledby=\"title-la-graciosa\">\n<div class=\"route-head\"><div><p class=\"eyebrow\" style=\"color:#865000;margin:0\">La Graciosa</p><h2 id=\"title-la-graciosa\">Guadarfía and the Island of San Borondón</h2></div></div>\n<div class=\"route-steps\" aria-label=\"Route progress\"><span class=\"route-step source-step\">1. Understanding</span><span class=\"route-step truth-step\">2. True or false</span><span class=\"route-step badge-step\">3. Piece</span></div>\n<div class=\"route-grid\"><figure class=\"route-figure\"><img src=\"content/resources/scene_la-graciosa.webp\" alt=\"A small wooden caravel with two masts and triangular sails travels at sunset, with several crew members on deck. An imagined early 16th-century voyage.\"><figcaption>AI-generated illustration for the story. It depicts a fictional scene.</figcaption><details class=\"image-literacy\"><summary>Look closely at the image</summary><p>What can you see? What would you need to check? Choose one detail and check it against a source. A realistic image can still contain historical errors.</p><p>In primary school, discuss the image with support. In secondary school, distinguish fact, interpretation and fiction, and look for stereotypes. You can do this optional activity aloud or in your notebook.</p></details></figure><article class=\"story\"><p class=\"route-meta\">Legendary tale · La Graciosa</p><p class=\"story-intro\">A story set in the days of sailing ships and inspired by the legend of San Borondón, a phantom island that chroniclers and mapmakers placed to the west of Canarias and which, according to different versions, could be seen from La Palma, El Hierro or La Gomera. For centuries, it was known as “the eighth island”. La Graciosa, by contrast, had no permanent population until the late nineteenth century, so it did not appear in the old counts of inhabited islands.</p><div class=\"story-refrain\"><strong>Refrain: </strong>“Island of mist, you appear and then you disappear”</div><p>When boats travelled under sail and maps were drawn on parchment, Guadarfía was an apprentice sailor on a small ship. One afternoon, the ship was crossing the sea near the island we now call La Graciosa.</p><p>An unknown land appeared behind the band of mist. It had a dark mountain, trees and a gleaming beach. The captain remembered the stories of San Borondón, the island that appeared and disappeared.</p><p>Guadarfía pointed to the horizon and said: “Island of mist, you appear and then you disappear.”</p><p>The crew changed course, but the further the ship sailed, the further away the island seemed. Then a fog came in so thick that they had to lower the sails and wait.</p><p>By dawn, the mist had gone. There was only sea in front of the ship. The captain marked the spot on his chart, and Guadarfía drew the shape he remembered.</p><p>Other sailors told of similar sights, and some maps included San Borondón. Yet no one managed to reach it.</p><p>The island kept appearing in stories, always behind the mist: “Island of mist, you appear and then you disappear.”</p><details class=\"radar\"><summary><strong>Investigate the sources behind the story</strong></summary><p>The legend of San Borondón is shared across the Canary Islands. Chroniclers and mapmakers placed the island west of the archipelago. For centuries it was known as “the eighth island”, and accounts of sightings vary. Permanent settlement on La Graciosa began in the late 19th century. Placing Guadarfía and his ship in these waters is a literary choice linking the legend to the La Graciosa route. The fictional sailor shares his name with a historical leader.</p><section class=\"source-traceability\" data-source-route=\"la-graciosa\" aria-label=\"Story sources\"><p><strong>Traditional or documented element:</strong> San Borondón appears on historical maps and in travellers’ accounts. Chaparro records some claims of landings, all of which remain unverified. The tradition is linked to the legendary voyage of Saint Brendan.</p><p><strong>Sources:</strong></p><ul><li>Chaparro Domínguez, M. Á. (2013). <a href=\"https://revistas.ucm.es/index.php/RFRM/article/download/45706/42966/73431#page=4\" target=\"_blank\" rel=\"noopener noreferrer\">Revisiting the Geographical Myth of San Borondón and Tracing Its Legacy in Literature and Other Arts</a> <small class=\"source-original\">[<span lang=\"es\">Revisión del mito geográfico de San Borondón y aproximación a su huella en la literatura y otras artes</span>]</small>. Journal of Romance Philology <small class=\"source-original\">[<span lang=\"es\">Revista de Filología Románica</span>]</small>, 30(2), pp. 229–244. Origins and travellers’ accounts are discussed on pp. 232–236.</li><li>Martínez Berriel, S. (2001–2002). <a href=\"https://revistavegueta.ulpgc.es/ojs/index.php/revistavegueta/article/view/225\" target=\"_blank\" rel=\"noopener noreferrer\">The Island of Good Customs: Social and Cultural Change on La Graciosa</a> <small class=\"source-original\">[<span lang=\"es\">La isla de las buenas costumbres: cambio social y cultural en la isla de La Graciosa</span>]</small>. Vegueta, 6. See the abstract and the discussion of settlement.</li><li>William Turpin, Dickinson College Commentaries. <a href=\"https://dcc.dickinson.edu/navigatio-brendani/intro/introduction\" target=\"_blank\" rel=\"noopener noreferrer\">Introduction — The Voyage of Saint Brendan the Abbot</a>. <small class=\"source-consultation\">Consulted for the editorial review on 1 November 2026.</small></li><li>Dickinson College Commentaries, edited by William Turpin. <a href=\"https://dcc.dickinson.edu/navigatio-brendani/intro/latin-text-whole\" target=\"_blank\" rel=\"noopener noreferrer\">Latin Text of Navigatio Brendani</a>. <small class=\"source-consultation\">Consulted for the editorial review on 1 November 2026.</small></li><li>Luis Regueira Benítez (El Museo Canario) and Manuel Poggio Capote (Real Sociedad Cosmológica). <a href=\"https://dialnet.unirioja.es/descarga/articulo/5759160.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">The Chaplain Juan Díaz, ‘Bishop of San Borondón’. New Evidence on Atlantic Exploration (1526–1529)</a> <small class=\"source-original\">[<span lang=\"es\">El capellán Juan Díaz, «obispo de San Borondón». Nuevas noticias sobre la exploración del Atlántico (1526–1529)</span>]</small>. <small class=\"source-consultation\">Consulted for the editorial review on 1 November 2026.</small></li><li>Direção Cultural da Marinha, Museu de Marinha. <a href=\"https://cultura.marinha.pt/pt/museumarinha_web/colecoes_web/pecasemdestaque_web/Paginas/caravela-latina.aspx\" target=\"_blank\" rel=\"noopener noreferrer\">Lateen-rigged Caravel — Model MM.05724</a> <small class=\"source-original\">[<span lang=\"pt\">Caravela latina — modelo MM.05724</span>]</small>. <small class=\"source-consultation\">Consulted for the editorial review on 1 November 2026.</small></li><li>Armada Española. <a href=\"https://armada.defensa.gob.es/archivo/ohycn/navegaciones/comun/Buques%20epoca%20descubrimiento%20y%20exploracion%20Rev.pdf\" target=\"_blank\" rel=\"noopener noreferrer\">Types of Ships in the Age of Discovery and Exploration, 15th–17th Centuries</a> <small class=\"source-original\">[<span lang=\"es\">Los tipos de naos en la época de los descubrimientos y exploraciones, siglos XV–XVII</span>]</small>. <small class=\"source-consultation\">Consulted for the editorial review on 1 November 2026.</small></li></ul><p>The story’s line “no one managed to reach it” simplifies the reports of searches and alleged landings. None of the landings has been verified. The episode near La Graciosa is fictional. Accounts usually place San Borondón west of the Canary Islands.</p><p><strong>About this version:</strong> This version retains the original story and narration. Guadarfía is a fictional apprentice sailor distinct from the historical leader of Lanzarote. The illustrations show a small two-masted caravel with lateen sails, a plausible vessel for the early 16th century. The captain, the drawing, the dialogue and the refrain were created for this story.</p></section></details></article></div>\n<div class=\"quiz source-quiz\" id=\"source-la-graciosa\"><p class=\"challenge-kicker\">Challenge 1 of 2</p><h3>Comprehension challenge</h3><p>Choose the right answer. You need 3 out of 3.</p><div class=\"source-questions\"></div><button class=\"button check-source\" type=\"button\" data-route=\"la-graciosa\">Check understanding</button><div class=\"source-status\" role=\"status\"></div></div>\n<div class=\"quiz\" id=\"quiz-la-graciosa\"><p class=\"challenge-kicker\">Challenge 2 of 2</p><h3>True-or-false challenge</h3><p>Choose true or false for each statement. Complete both challenges to earn the piece.</p><div class=\"questions\"></div><button class=\"button check-quiz\" type=\"button\" data-route=\"la-graciosa\">Check the challenge</button><div class=\"quiz-status\" role=\"status\"></div><div class=\"reward\"><img src=\"content/resources/insignia_la_graciosa.webp\" alt=\"Clay shell, a contemporary symbol of La Graciosa\"><div><span>Piece added to your passport</span><strong>Horizon piece</strong><p>Open Passport at the top of the page to see your collection.</p><button class=\"button open-passport\" type=\"button\">View my passport</button></div></div></div>\n<div class=\"route-nav\"><button class=\"button secondary back-map choose-island\" type=\"button\">Choose another island</button></div></section>"];
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
function isRecordValue(value){return value!==null&&typeof value==="object"&&!Array.isArray(value);}
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
const rawPreferences=readJSON(preferencesKey,{});
const savedPreferences=isRecordValue(rawPreferences)?rawPreferences:{};
let readerMode=savedPreferences.readerMode==="complete"?"complete":"guided";
let learningLevel=["early","middle","advanced","secondary"].includes(savedPreferences.learningLevel)?savedPreferences.learningLevel:"middle";
let learnerName=typeof savedPreferences.learnerName==="string"?savedPreferences.learnerName.slice(0,80):"";
let lastRouteId=validIds.has(savedPreferences.lastRouteId)?savedPreferences.lastRouteId:null;
let selectedVoiceURI=typeof savedPreferences.selectedVoiceURI==="string"?savedPreferences.selectedVoiceURI:"";
let narrationAmbient=savedPreferences.narrationAmbient!==false;

// La revisión es una anotación local de acompañamiento, no una certificación.
const itineraryKey="mitomapa-canario-itinerarios-v1";
const itineraryLevels=["early","middle","advanced","secondary"];
const notebookTaskNames={words:"Vocabulary",research:"Investigate",creation:"Create"};
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
function invalidateItineraryTask(id,task,track=null,levelRestriction=null){
 let changed=false;
 for(const level of itineraryLevels){
  if(levelRestriction&&level!==levelRestriction)continue;
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
 workshop.querySelectorAll(".activity-save-creation").forEach(button=>{button.hidden=external;button.dataset.creationTrack=learningLevel==="secondary"?"secondary":"primary";button.textContent=learningLevel==="secondary"?"Mark the proposal as ready":"Mark my work as ready";});
 refreshCreationReview(workshop,id);
 const note=workshop.querySelector(".external-creation-note");if(note){note.hidden=!external;note.textContent=item.externalCreation?"Your teacher has recorded the review of your work completed outside the website.":"Complete your work outside the website in the format agreed with your teacher. You could speak, work on paper, record audio or use another tool. Share your work with your teacher so they can record their review.";}
 const length=workshop.querySelector(".secondary-length-note");if(length)length.textContent=secondaryCreations[id].lengthLabel+(item.flexibleLength?" Follow the length agreed with your teacher. You can still submit your work.":" Your teacher can adjust the length in the teacher space.");
 updateWorkshopSummary(id);
}
function updateItineraryUI(){
 const count=routes.filter(route=>itineraryFor(route.id).reviewed).length;
 const summary=byId("itinerarySummary");
 if(summary)summary.textContent=`${currentBadgeCount()}/8 pieces collected · ${count}/8 routes reviewed at ${learningLevelLabel()}.`;
 document.querySelectorAll(".route").forEach(section=>{
  const id=section.id.replace("route-","");
  const status=section.querySelector(".itinerary-status");
  if(status)status.textContent=itineraryFor(id).reviewed?"Route reviewed with your teacher":"Route awaiting review with your teacher";
  const tasks=section.querySelector(".assigned-tasks");
  if(tasks){tasks.textContent=itineraryFor(id).tasks;tasks.hidden=!itineraryFor(id).tasks;}
 });
 window.MitoMapaJourney?.refresh();
}
const itinerarySteps={
 early:["Listen to or read the story with help, and repeat the refrain.","Answer the three comprehension questions to earn the piece.","Complete the speaking activity, drawing or other task your teacher sets.","Share your work and review your agreed route with your teacher."],
 middle:["Read the story and look closely at its illustration.","Complete the comprehension and true-or-false challenges to earn the piece.","Practise the vocabulary and complete the other tasks agreed with your teacher.","Review your work with your teacher. The piece records completion of the challenges."],
 advanced:["Read the story and distinguish the legend from the details written for MitoMapa.","Complete the comprehension and true-or-false challenges to earn the piece.","Choose your vocabulary, research or creative tasks with your teacher.","Create something to share and review the agreed tasks with your teacher."],
 secondary:["Read the story. Identify which elements come from tradition and which were written for MitoMapa.","Complete both comprehension challenges to earn the piece.","Compare sources and complete the secondary school activity for this island.","Review your text using the checklist and share your work with your teacher."]
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
function savePreferences(){return writeJSON(preferencesKey,{readerMode,learningLevel,learnerName,lastRouteId,selectedVoiceURI,narrationAmbient});}
function setReaderMode(mode){
 readerMode=mode==="complete"?"complete":"guided";
 document.body.classList.toggle("mode-guided",readerMode==="guided");
 document.body.classList.toggle("mode-complete",readerMode==="complete");
 if(readerMode==="guided")document.querySelectorAll(".radar").forEach(radar=>{radar.open=false;});
 document.querySelectorAll("[data-reader-mode]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.readerMode===readerMode)));
 const status=byId("readerModeStatus");
 if(status)status.textContent=readerMode==="guided"?"Supported reading uses larger text and one column, with sources you can open.":"Explore in depth uses a compact layout and keeps source notes available.";
 savePreferences();
}
function injectExperienceTools(){
 const legend=document.querySelector(".hero .legend");
 if(!legend)return;
 const chips=[...legend.querySelectorAll(".chip")];
 const offlineChip=chips.find(chip=>chip.textContent.trim()==="Offline");
 if(offlineChip)offlineChip.textContent="No sign-up required";
 const panel=document.createElement("section");
 panel.className="experience-tools";
 panel.setAttribute("aria-labelledby","experienceToolsTitle");
 panel.innerHTML=`<h2 id="experienceToolsTitle">Prepare your expedition</h2><p>Choose your learning stage and reading layout. You can change either later.</p><div class="learning-level-block"><h3>Suggested learning stage</h3><div class="learning-level-switch" role="group" aria-label="Learning stage"><button type="button" data-learning-level="early">Early years and first primary cycle</button><button type="button" data-learning-level="middle">Second primary cycle</button><button type="button" data-learning-level="advanced">Third primary cycle</button><button type="button" data-learning-level="secondary">Secondary</button></div><p class="mode-status" id="learningLevelStatus" role="status"></p></div><div class="learning-level-block"><h3>Reading layout</h3><div class="mode-switch" role="group" aria-label="Reading mode"><button type="button" data-reader-mode="guided">Supported reading</button><button type="button" data-reader-mode="complete">Explore in depth</button></div><p class="mode-status" id="readerModeStatus" role="status"></p></div><div class="experience-actions"><button class="text-button" id="resumeRoute" type="button">Return to the last island</button></div>`;
 const hero=legend.closest(".hero");if(hero)hero.append(panel);else legend.after(panel);
 panel.querySelectorAll("[data-reader-mode]").forEach(button=>button.addEventListener("click",()=>setReaderMode(button.dataset.readerMode)));
 panel.querySelectorAll("[data-learning-level]").forEach(button=>button.addEventListener("click",()=>setLearningLevel(button.dataset.learningLevel)));
  byId("resumeRoute").addEventListener("click",()=>{if(!window.MitoMapaNavigation?.resume?.()&&lastRouteId)showRoute(lastRouteId);});
 byId("resumeRoute").disabled=!lastRouteId;
 const passportKicker=document.querySelector("#passportDialog .challenge-kicker");
 if(passportKicker)passportKicker.textContent="Saved in this browser";
 const puzzleLead=byId("missionTitle")?.closest("section")?.querySelector(".lead");
 if(puzzleLead)puzzleLead.textContent="Look at the shapes and colours to rebuild the map. Drag a piece onto another or select two pieces to swap them. On the keyboard, press Tab to move between pieces and Enter or Space to select them. Choose “Show solution” if you need help.";
 const footer=document.querySelector(".footer-inner");
 if(footer)footer.insertAdjacentHTML("beforeend",`<details class="footer-privacy"><summary>Privacy and saved progress</summary><p>You can use MitoMapa without an account. This browser saves your progress. You can enter a name or a team name for teacher review. The diploma leaves out personal names. When a story has a recording, the player uses the recording it names. Other stories use a voice available on your device.</p></details>`);
 setReaderMode(readerMode);
 setLearningLevel(learningLevel,false);
}
function voiceScore(voice){
 const lang=(voice.lang||"").replace("_","-").toLowerCase();
 if(lang!=="en"&&!lang.startsWith("en-"))return 0;
 return (lang==="en-gb"?10:1)+(voice.localService?5:0);
}
function englishVoices(){
 return availableVoices.filter(voice=>voiceScore(voice)>0)
  .sort((a,b)=>voiceScore(b)-voiceScore(a)||(a.name||"").localeCompare(b.name||"","en"));
}
function selectedVoice(){
 const voices=englishVoices();
 return voices.find(voice=>voice.voiceURI===selectedVoiceURI)||voices[0]||null;
}
function voiceDescription(){
 if(!speechSupported)return"This browser cannot read the story aloud. You can still read the text.";
 const voice=selectedVoice();
 if(!voice)return"An English voice is unavailable on this device. You can still read the story.";
 return `Selected voice: ${voice.name} (${voice.lang||"English"}). Pronunciation depends on the device.`;
}
function refreshVoices(){
 if(!speechSupported)return;
 availableVoices=window.speechSynthesis.getVoices();
 const voices=englishVoices();
 document.querySelectorAll(".narration-voice").forEach(select=>{
  const automatic=document.createElement("option");
  automatic.value="";automatic.textContent="Automatic (recommended)";
  select.replaceChildren(automatic);
  voices.forEach(voice=>{
   const option=document.createElement("option");
   option.value=voice.voiceURI;option.textContent=`${voice.name} · ${voice.lang||"en"}`;
   select.append(option);
  });
  select.value=voices.some(voice=>voice.voiceURI===selectedVoiceURI)?selectedVoiceURI:"";
  select.disabled=!voices.length;
 });
 document.querySelectorAll(".voice-note[data-device-voice]").forEach(note=>note.textContent=voiceDescription());
}
function narrationMarkup(route){
 const recording=routeRecording(route.id);
 const note=recording?`Narration: ${narrationLabel(recording.narrator||"recorded narration")}.`:speechSupported?"Checking the device’s voices…":voiceDescription();
 const voice=recording?"":`<label class="narration-setting">Voice <select class="narration-voice" aria-label="Reading voice"><option value="">Automatic (recommended)</option></select></label>`;
 const ambient=recording?.ambientSrc?`<label class="narration-setting narration-ambient-label"><input class="narration-ambient" type="checkbox"${narrationAmbient?" checked":""}> Quiet background sounds</label>`:"";
 const timeline=recording?`<div class="narration-timeline"><button class="text-button narration-back" type="button" aria-label="Go back ten seconds" disabled>−10 s</button><div class="narration-position"><label for="narration-position-${route.id}">Playback position</label><input class="narration-seek" id="narration-position-${route.id}" type="range" min="0" max="0" step="1" value="0" aria-valuetext="Duration unavailable" disabled><p class="narration-time"><span class="narration-current">0:00</span> / <span class="narration-duration">--:--</span></p></div><button class="text-button narration-forward" type="button" aria-label="Go forward ten seconds" disabled>+10 s</button></div>`:"";
 return `<section class="narrator" data-narration-source="${recording?"recording":"device"}" aria-labelledby="narrator-title-${route.id}"><div class="narrator-copy"><p class="narrator-kicker">Listen to the story</p><h3 id="narrator-title-${route.id}">${recording?"Recorded narration":"Read aloud"}</h3><p class="voice-note"${recording?"":" data-device-voice"}>${note}</p></div><div class="narrator-controls"><button class="button narration-play" type="button" data-route="${route.id}">▶ Play</button><button class="button secondary narration-pause" type="button" data-route="${route.id}" disabled>⏸ Pause</button><button class="button secondary narration-stop" type="button" data-route="${route.id}" disabled>■ Stop</button>${timeline}${voice}<label class="narration-setting">Speed <select class="narration-rate" aria-label="Playback speed"><option value="0.82">Slow</option><option value="${recording?"1":"0.94"}" selected>Normal</option><option value="1.08">Faster</option></select></label>${ambient}<p class="narration-status" role="status" aria-live="polite">Ready to play.</p></div></section>`;
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
 slider.setAttribute("aria-valuetext",known?`${narrationTime(position)} of ${narrationTime(duration)}`:"Duration unavailable");
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
 play.textContent=state==="finished"?"↻ Listen again":"▶ Play";
 pause.disabled=!active;
 pause.textContent=state==="paused"?"▶ Resume":"⏸ Pause";
 stop.disabled=!active;
 if(status&&message)status.textContent=message;
 section.querySelector(".narrator")?.classList.toggle("is-speaking",state==="playing");
}
function stopNarration(message="Reading stopped.",{keepFormats=false}={}){
 if(!keepFormats)window.MitoMapaFormats?.stopOwnedMedia();
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
   updateNarrationUi(routeId,"paused","Narration ready. Choose Play or Resume to listen.");
   return;
  }
  stopNarration("The recording could not play. Try again or read the story.");
 };
 let pending;
 try{pending=audio.play();}
 catch(error){failed(error);return;}
 Promise.resolve(pending).then(()=>{
  if(!current()){audio.pause();return;}
  if(narrationState.paused){audio.pause();return;}
  if(request===recordingPlayRequest){narrationState.awaitingGesture=false;updateNarrationUi(routeId,"playing","Playing the recorded narration.");}
 }).catch(failed);
}
function prepareRecordingSeek(audio,routeId,token,source){
 const state=narrationState;
 const sourceVersion=state.sourceVersion;
 const current=()=>token===narrationToken&&narrationState===state&&narrationState.audio===audio&&state.sourceVersion===sourceVersion;
 // Un audio HTTP ya iniciado puede reproducirse, pero algunos servidores no
 // permiten buscar aunque el MP3 esté entero en el búfer. Solo en ese caso
 // se prepara una URL local; los servidores con rangos conservan su flujo.
 if(!current()||state.seekFallbackAttempted||state.objectUrl||recordingIsSeekable(audio))return;
 if(!/^https?:$/.test(location.protocol)||typeof fetch!=="function"||typeof AbortController!=="function")return;
 if(audio.readyState<1||!Number.isFinite(audio.duration)||audio.duration<=0)return;
 // En pausa, preload="auto" puede detenerse con solo unos segundos en búfer.
 // Un cambio pendiente necesita preparar el avance sin esperar al MP3 entero.
 if(!state.sourceLoading){
  if(audio.readyState<3||!audio.buffered.length)return;
  if(audio.buffered.end(audio.buffered.length-1)<audio.duration-.25)return;
 }
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
  state.blobResumePosition=Math.max(0,state.blobResumePosition??audio.currentTime??0);state.sourceLoading=true;
  recordingPlayRequest++;audio.pause();
  audio.src=state.objectUrl;audio.load();
  syncRecordingTimeline(routeId);
  updateNarrationUi(routeId,state.paused?"paused":"playing",state.paused?"Narration paused. Preparing to seek…":"Preparing to seek in the narration…");
 }).catch(error=>{
  if(!current())return;
  state.blobController=null;
  if(state.sourceLoading&&!state.objectUrl){
   // Si el servidor no permite buscar y falla la copia local, la nueva pista
   // sigue siendo utilizable. Se explica la pérdida de posición sin bloquearla.
   state.sourceLoading=false;state.blobResumePosition=null;
   try{audio.currentTime=0;}catch(seekError){}
   if(!state.paused)playRecording(audio,routeId,token);
   syncRecordingTimeline(routeId);
   updateNarrationUi(routeId,state.paused?"paused":"playing","Playback has restarted because the previous position could not be restored.");
   return;
  }
  // La descarga auxiliar no sustituye el audio hasta completarse: si falla,
  // la reproducción directa sigue disponible, también en aplicaciones locales.
  updateNarrationUi(routeId,state.paused?"paused":"playing","You can still listen. Seeking is unavailable for now. Restart playback and try again if you need it.");
 });
}
function startRecording(routeId,recording){
 const section=byId(`route-${routeId}`);if(!section)return;
 stopNarration();
 const ambient=section.querySelector(".narration-ambient")?.checked;
 const audio=new Audio();
 const token=++narrationToken;
 narrationState={routeId,index:0,chunks:[],paused:false,token,audio,blobController:null,objectUrl:null,blobResumePosition:null,sourceLoading:false,seekFallbackAttempted:false,awaitingGesture:false,sourceVersion:0,source:ambient&&recording.ambientSrc?recording.ambientSrc:recording.src};
 audio.preload="none";
 audio.defaultPlaybackRate=Number(section.querySelector(".narration-rate")?.value)||1;
 audio.playbackRate=audio.defaultPlaybackRate;
 audio.src=narrationState.source;
 const current=()=>token===narrationToken&&narrationState.audio===audio;
 const sync=()=>{
  if(!current())return;
  if(narrationState.sourceLoading&&audio.readyState>=1&&Number.isFinite(audio.duration)){
   const position=narrationState.blobResumePosition;
   if(position>0&&!recordingIsSeekable(audio)){
    syncRecordingTimeline(routeId);prepareRecordingSeek(audio,routeId,token,narrationState.source);return;
   }
   narrationState.sourceLoading=false;narrationState.blobResumePosition=null;
   try{audio.currentTime=Math.min(audio.duration,position||0);}catch(error){}
   if(narrationState.paused)updateNarrationUi(routeId,"paused","Narration ready and paused.");
   else playRecording(audio,routeId,token);
  }
  syncRecordingTimeline(routeId);
  prepareRecordingSeek(audio,routeId,token,narrationState.source);
 };
 audio.onloadedmetadata=sync;audio.ondurationchange=sync;audio.ontimeupdate=sync;audio.oncanplay=sync;audio.onseeked=sync;audio.onprogress=sync;
 audio.onplaying=()=>{
  if(!current()||narrationState.paused){audio.pause();return;}
  sync();
  updateNarrationUi(routeId,"playing","Playing the recorded narration.");
 };
 audio.onended=()=>{
  if(!current())return;
  const duration=audio.duration;
  stopNarration();updateNarrationUi(routeId,"finished","Story finished. You can listen again.");
  syncRecordingTimeline(routeId,{duration,position:duration});
 };
 audio.onerror=()=>{if(current())stopNarration("The recording could not load. Try again or read the story.");};
 updateNarrationUi(routeId,"playing","Loading the recorded narration…");
 playRecording(audio,routeId,token);
}
function changeRecordingAmbient(routeId){
 if(narrationState.routeId!==routeId||!narrationState.audio)return;
 const state=narrationState,audio=state.audio,recording=routeRecording(routeId);if(!recording)return;
 const source=narrationAmbient&&recording.ambientSrc?recording.ambientSrc:recording.src;
 if(source===state.source)return;
 const position=Math.max(0,state.blobResumePosition??audio.currentTime??0);
 state.sourceVersion++;state.blobController?.abort();state.blobController=null;
 recordingPlayRequest++;audio.pause();
 if(state.objectUrl)URL.revokeObjectURL(state.objectUrl);
 state.objectUrl=null;state.source=source;state.blobResumePosition=position;
 state.sourceLoading=true;state.seekFallbackAttempted=false;state.awaitingGesture=false;
 // También se necesita cargar la nueva pista si el cambio se hace en pausa.
 audio.preload="auto";audio.src=source;audio.load();
 audio.playbackRate=audio.defaultPlaybackRate;
 syncRecordingTimeline(routeId);
 updateNarrationUi(routeId,state.paused?"paused":"playing",state.paused?"Changing background sounds. Playback will stay paused at the same position…":"Changing background sounds. Playback will continue from the same position…");
}
function speakNextChunk(){
 if(!speechSupported||!narrationState.routeId)return;
 if(narrationState.index>=narrationState.chunks.length){
  const completedRoute=narrationState.routeId;
  narrationState={routeId:null,index:0,chunks:[],paused:false,token:narrationToken};
  clearNarrationHighlight(completedRoute);updateNarrationUi(completedRoute,"finished","Story finished. You can listen again.");
  return;
 }
 const routeId=narrationState.routeId,token=narrationState.token;
 const chunk=narrationState.chunks[narrationState.index];clearNarrationHighlight(routeId);chunk.element?.classList.add("is-reading");
 const utterance=new SpeechSynthesisUtterance(chunk.text);
 const voice=selectedVoice();if(voice)utterance.voice=voice;
 utterance.lang=voice?.lang||"en-GB";
 const rate=byId(`route-${routeId}`)?.querySelector(".narration-rate")?.value;
 utterance.rate=Number(rate)||0.94;utterance.pitch=1;utterance.volume=1;
 utterance.onstart=()=>{if(token===narrationToken)updateNarrationUi(routeId,"playing",`Reading passage ${narrationState.index+1} of ${narrationState.chunks.length}.`);};
 utterance.onend=()=>{if(token!==narrationToken||narrationState.routeId!==routeId)return;narrationState.index++;speakNextChunk();};
 utterance.onerror=event=>{if(token!==narrationToken||event.error==="canceled"||event.error==="interrupted")return;stopNarration("The device could not start reading aloud. You can continue reading the text.");};
 window.speechSynthesis.speak(utterance);
}
function startNarration(routeId){
 if(narrationState.routeId===routeId&&narrationState.audio&&(narrationState.awaitingGesture||narrationState.paused)){
  narrationState.paused=false;narrationState.awaitingGesture=false;
  updateNarrationUi(routeId,"playing","Resuming narration…");
  if(!narrationState.sourceLoading)playRecording(narrationState.audio,routeId,narrationState.token);
  return;
 }
 const recording=routeRecording(routeId);
 if(recording){startRecording(routeId,recording);return;}
 if(!speechSupported){updateNarrationUi(routeId,"idle","This browser cannot read aloud.");return;}
 const section=byId(`route-${routeId}`);if(!section)return;
 stopNarration();
 const chunks=storySpeechChunks(section);narrationToken++;
 narrationState={routeId,index:0,chunks,paused:false,token:narrationToken};
 updateNarrationUi(routeId,"playing","Preparing the device’s reading voice…");
 speakNextChunk();
}
function toggleNarrationPause(routeId){
 if(narrationState.routeId!==routeId)return;
 if(narrationState.audio){
  if(narrationState.paused){
   narrationState.paused=false;narrationState.awaitingGesture=false;updateNarrationUi(routeId,"playing","Resuming narration…");
   if(!narrationState.sourceLoading)playRecording(narrationState.audio,routeId,narrationState.token);
  }else{
   narrationState.paused=true;recordingPlayRequest++;narrationState.audio.pause();
   updateNarrationUi(routeId,"paused","Narration paused.");
  }
  return;
 }
 if(!speechSupported)return;
 if(narrationState.paused){window.speechSynthesis.resume();narrationState.paused=false;updateNarrationUi(routeId,"playing","Reading resumed.");}
 else{window.speechSynthesis.pause();narrationState.paused=true;updateNarrationUi(routeId,"paused","Reading paused.");}
}
function openDialog(dialog){if(typeof dialog.showModal==="function")dialog.showModal();else dialog.setAttribute("open","");}
function closeDialog(dialog){if(typeof dialog.close==="function")dialog.close();else dialog.removeAttribute("open");}
function badgeSlotMarkup(route){
 const obtained=badgeCountsForLevel(route.id);
 const retained=earned.has(route.id)&&!obtained;
 return `<button class="badge-slot ${obtained?"earned":""}" type="button" data-passport-route="${route.id}" aria-label="${route.island}: ${obtained?route.badgeName+", earned at the selected learning stage":retained?"earned at another stage; requirements for this stage are still pending":"piece still to earn"}"><img src="${ASSETS[route.badge]}" alt=""><strong>${route.island}</strong><small>${obtained?route.badgeName:retained?"Earned at another stage":"Piece to discover"}</small><span class="badge-state">${obtained?"Earned":retained?"Complete this stage":"Pending"}</span></button>`;
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
 const routeRequirement=learningLevel==="early"?"the comprehension challenge for each story":"both challenges on each island";
 byId("passportDialogStatus").textContent=count===routes.length?"Passport complete! You have collected all eight pieces.":`You have collected ${count} of 8 pieces. Complete ${routeRequirement} to finish the collection.`;
 const historical=historicalBadgeCount();
 const stageNote=` Selected learning stage: ${learningLevelLabel()}.`+(historical?` Your passport retains ${historical} ${historical===1?"piece":"pieces"} earned at another stage. Complete the challenges at this stage to count them here.`:"");
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
  if(sourcePassed.has(id)&&sourceStatus&&!sourceStatus.textContent)sourceStatus.textContent="Challenge complete.";
  if(truthPassed.has(id)&&truthStatus&&!truthStatus.textContent)truthStatus.textContent="Challenge complete.";
 });
 const unlocked=count===routes.length;
 byId("finalContent").classList.toggle("unlocked",unlocked);
 byId("finalLock").hidden=unlocked;
 updateFinalExperience();updateItineraryUI();window.MitoMapaExplorer?.refresh();window.MitoMapaRouteFlow?.refresh();
}
function showRoute(id,options={}){
 if(!validIds.has(id))return;
 const step=window.MitoMapaNavigation?.activateRoute(id,options);
 if(lastRouteId!==id||(step&&step!=="cuento"))window.MitoMapaFormats?.stopOwnedMedia();
 if(narrationState.routeId&&narrationState.routeId!==id)stopNarration("Narration stopped when you changed islands.");
 document.querySelectorAll(".route").forEach(element=>element.classList.remove("active"));
 const section=ensureRoute(id);if(!section)return;
 section.classList.add("active");
 window.MitoMapaRouteFlow?.showStep(section,step||"cuento",{focus:false,notify:false});
 lastRouteId=id;savePreferences();
 const resume=byId("resumeRoute");if(resume)resume.disabled=false;
 window.MitoMapaNavigation?.refreshResume?.();
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
function tryAward(id,previousCount=currentBadgeCount()){
 if(!badgeRequirementsMet(id))return false;
 const wasNew=!earned.has(id);
 earned.add(id);save();updateProgress();
 if(previousCount<routes.length&&currentBadgeCount()===routes.length){
  showDiplomaPreview();
 }else if(wasNew){
  const route=routes.find(item=>item.id===id);
  byId("dialogBadge").src=`${ASSETS[route.badge]}`;
  byId("dialogBadge").alt=route.badgeAlt;
  byId("dialogTitle").textContent=route.badgeName;
  byId("dialogText").textContent=`The badge for ${route.island} has been added to your passport. You now have ${currentBadgeCount()} out of 8. Remember to complete the tasks set by your teacher.`;
   let next=byId("badgeContinueWorkshop");
   if(!next){
    next=document.createElement("button");next.id="badgeContinueWorkshop";next.type="button";next.className="button badge-workshop-next";
    byId("viewPassport").before(next);byId("viewPassport").classList.add("secondary");
    next.addEventListener("click",()=>{const target=next.dataset.route;if(!validIds.has(target))return;closeDialog(byId("badgeDialog"));if(selectedNotebookTasks(target).length)showRoute(target,{step:"taller"});else window.MitoMapaNavigation?.go("crear");});
   }
   next.dataset.route=id;next.textContent=selectedNotebookTasks(id).length?"Continue to my workshop →":"Plan something to share →";
  openDialog(byId("badgeDialog"));
 }
 return true;
}
function enhanceQuizStepper(quiz){
 const questions=[...quiz.querySelectorAll(".question")];if(!questions.length)return;
 quiz.classList.add("quiz-stepper");
 const checkButton=quiz.querySelector(".check-source,.check-quiz");
 const nav=document.createElement("div");nav.className="question-nav";
 nav.innerHTML=`<button class="text-button question-prev" type="button">← Previous</button><span class="question-counter" aria-live="polite"></span><button class="text-button question-next" type="button">Next →</button><span class="question-dots" aria-hidden="true"></span>`;
 checkButton.before(nav);let current=0;
 const show=(index,{focus=false}={})=>{
  current=Math.max(0,Math.min(index,questions.length-1));
  questions.forEach((question,questionIndex)=>question.classList.toggle("current",questionIndex===current));
  nav.querySelector(".question-prev").disabled=current===0;
  nav.querySelector(".question-next").disabled=current===questions.length-1;
  nav.querySelector(".question-counter").textContent=`Question ${current+1} of ${questions.length}`;
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
 {id:"relation",text:"Connects with the story"},
 {id:"communication",text:"Communicates an idea in the agreed format"},
 {id:"improvement",text:"I have reviewed one improvement with support"}
]);
const creationReviewOptions=Object.freeze([
 ["pending","Pending"],["reviewed","Reviewed"],["in_progress","In progress"],["not_applicable","Not applicable"]
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
 const genre=(secondaryCreations[routeId]?.criteria||[]).map((text,index)=>({id:`genre_${index}`,text:routeId==="fuerteventura"&&index===3?"Where a written text was agreed, it meets the agreed length and has been reviewed.":text}));
 return common.concat(genre);
}
function creationReviewResult(state,routeId,level=learningLevel){
 const values=state.creationReviewV1?.[level]||{},criteria=creationReviewCriteria(routeId,level);
 const applicable=criteria.filter(item=>values[item.id]!=="not_applicable");
 const reviewed=applicable.filter(item=>values[item.id]==="reviewed").length;
 return{total:applicable.length,reviewed,excluded:criteria.length-applicable.length,complete:applicable.length>0&&reviewed===applicable.length};
}
function creationReviewSummaryText(result){
 return result.total?`${result.reviewed}/${result.total} criteria reviewed${result.excluded?`; ${result.excluded} not applicable`:""}. Use this checklist for feedback. It does not give a score or grade.`:"No criteria apply to this work. Check the agreed review with your teacher. This checklist is for discussion and feedback.";
}
function refreshCreationReview(workshop,routeId){
 const container=workshop.querySelector("[data-creation-review-container]");
 if(!container)return;
 const state=getWorkshopRouteState(routeId);
 const criteria=creationReviewCriteria(routeId),values=state.creationReviewV1?.[learningLevel]||{};
 const fieldset=document.createElement("fieldset");
 fieldset.className="creation-review";
 const legend=document.createElement("legend");
 legend.textContent=`Review your work · ${learningLevel==="secondary"?"Secondary":learningLevel==="early"?"Early years and first primary cycle":"Primary school"}`;
 const guidance=document.createElement("p");
 guidance.textContent=learningLevel==="early"?"In Early Years and first cycle, you can use this optional list to talk about your work with support.":"Choose which criteria to review with your teacher. You can share work marked “In progress” for help. Preparation and review are recorded separately. Choose “Not applicable” for criteria you did not agree to use.";
 fieldset.append(legend,guidance);

 function reviewRow(item){
  const label=document.createElement("label");
  label.className="creation-review-row";
  const caption=document.createElement("span");
  caption.id=`creation-review-label-${routeId}-${learningLevel}-${item.id}`;
  caption.textContent=item.text;
  const select=document.createElement("select");
  select.dataset.creationReview=item.id;
  select.dataset.creationReviewLevel=learningLevel;
  select.setAttribute("aria-labelledby",caption.id);
  for(const [value,text] of creationReviewOptions)select.add(new Option(text,value));
  select.value=values[item.id]||"pending";
  label.append(caption,select);
  return label;
 }

 fieldset.append(...criteria.slice(0,3).map(reviewRow));
 if(learningLevel==="secondary"){
  const genre=document.createElement("div");
  genre.className="creation-review-genre";
  const heading=document.createElement("h5");
  heading.textContent="Secondary school only · Agreed form of writing";
  const hint=document.createElement("p");
  hint.textContent="Choose “Not applicable” when a criterion does not suit your agreed format, such as a spoken or visual piece.";
  genre.append(heading,hint,...criteria.slice(3).map(reviewRow));
  fieldset.append(genre);
 }
 const itinerary=itineraryFor(routeId);
 const previousPrepared=itinerary.evidenceMode==="external"?itinerary.externalCreation:learningLevel==="secondary"?state.secondaryCreation:state.creation;
 if(previousPrepared&&!Object.keys(values).length){
  const previous=document.createElement("p");
  previous.className="creation-review-prior";
  previous.textContent="Your draft and earlier preparation are saved. The new checklist starts with all items awaiting review. Review them with support when agreed.";
  fieldset.append(previous);
 }
 const summary=document.createElement("p");
 summary.className="creation-review-summary";
 summary.setAttribute("role","status");
 summary.setAttribute("aria-live","polite");
 summary.setAttribute("aria-atomic","true");
 summary.textContent=creationReviewSummaryText(creationReviewResult(state,routeId));
 fieldset.append(summary);
 container.replaceChildren(fieldset);
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
 const options=match.options.map(option=>`<option value="${activityEscape(option)}">${activityEscape(match.labels?.[option] || option)}</option>`).join("");
 return `<div class="activity-block"><h5>${activityEscape(match.prompt)}</h5><div class="activity-match-grid">${match.items.map((item,index)=>`<label class="activity-match-row"><span id="activity-match-label-${routeId}-${index}">${activityEscape(item.definition)}</span><select data-activity-match data-answer="${activityEscape(item.answer)}" aria-labelledby="activity-match-label-${routeId}-${index}"><option value="">Choose a term</option>${options}</select><small class="activity-item-feedback" aria-live="polite"></small></label>`).join("")}</div></div>`;
}
function workshopFillMarkup(words){
 if(!words.fills?.length)return"";
 return `<div class="activity-block"><h5>${activityEscape(words.fillPrompt)}</h5><div class="activity-fill-grid">${words.fills.map((item,index)=>`<label class="activity-fill-row"><span><strong>${index+1}.</strong> ${activityEscape(item.prompt)}</span><input type="text" autocomplete="off" spellcheck="false" data-activity-fill data-answers="${activityEscape(item.answers.join("|"))}" data-hint="${activityEscape(item.hint||"")}" aria-label="Answer for ${activityEscape(item.prompt)}"><small class="activity-item-feedback" aria-live="polite"></small></label>`).join("")}</div></div>`;
}
function workshopSourceMarkup(source){
 let label=activityEscape(source.label);
 const title=activityEscape(source.spanishTitle);
 const language=title&&title===label?' lang="es"':"";
 if(title&&!language)label=label.replace(title,`<span lang="es">${title}</span>`);
 const original=source.originalTitle? ` <small class="source-original">[<span lang="es">${activityEscape(source.originalTitle)}</span>]</small>` : "";
 return `<li><a href="${activityEscape(source.url)}" target="_blank" rel="noopener noreferrer"${language}>${label}</a>${original}</li>`;
}
function workshopResearchMarkup(routeId,research){
 const questions=research.questions.map((question,index)=>`<fieldset class="activity-research-question" data-answer="${question.answer}"><legend>${index+1}. ${activityEscape(question.q)}</legend><div class="activity-choice-grid">${question.options.map((option,optionIndex)=>`<label><input type="radio" name="activity-${routeId}-research-${index}" value="${optionIndex}"><span>${activityEscape(option)}</span></label>`).join("")}</div><p class="activity-item-feedback" aria-live="polite"></p><p class="activity-answer-note" hidden>${activityEscape(question.feedback)}</p></fieldset>`).join("");
 const sources=research.sources?.length?`<details class="activity-sources"><summary>Sources for further research</summary><ul>${research.sources.map(workshopSourceMarkup).join("")}</ul></details>`:"";
 return `<div class="activity-panel" id="activity-${routeId}-research" role="tabpanel" aria-labelledby="activity-tab-${routeId}-research" data-activity-panel="research" hidden><h4>${activityEscape(research.title)}</h4><p>${activityEscape(research.intro)}</p>${questions}<button class="button activity-check-research" type="button">Check your research answers</button><p class="activity-panel-status" role="status" aria-live="polite"></p>${sources}<p class="activity-tip">This checks your answers to the two questions. Also complete the research and source comparison agreed with your teacher.</p><label class="activity-text-label"><span>My source and what I checked (optional)</span><textarea rows="3" maxlength="600" data-research-evidence placeholder="Write the title or link of a source and one detail you checked."></textarea></label><p class="research-draft-status" role="status"></p></div>`;
}
function workshopPrimaryCreationMarkup(creation){
 if(creation.type==="drawing"){
  return `<div class="creation-version creation-primary" data-creation-version="primary"><p class="creation-stage-label">Primary school activity</p><h4>${activityEscape(creation.title)}</h4><p>${activityEscape(creation.prompt)}</p><p class="activity-tip">${activityEscape(creation.tip)}</p><div class="drawing-toolbar" aria-label="Drawing tools"><span>Colour</span><button type="button" class="draw-color is-selected" data-draw-color="#2f2b26" style="--draw-color:#2f2b26" aria-label="Black" aria-pressed="true"></button><button type="button" class="draw-color" data-draw-color="#9b5738" style="--draw-color:#9b5738" aria-label="Clay" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#dfb94f" style="--draw-color:#dfb94f" aria-label="Yellow" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#72a4aa" style="--draw-color:#72a4aa" aria-label="Light blue" aria-pressed="false"></button><button type="button" class="draw-color" data-draw-color="#829276" style="--draw-color:#829276" aria-label="Green" aria-pressed="false"></button><label>Line width <input class="draw-size" type="range" min="2" max="24" value="7" aria-label="Drawing line width"></label></div><div class="drawing-frame"><canvas class="activity-canvas" width="900" height="520" role="img" aria-label="Canvas for drawing the tibicena. You can write a description below instead."></canvas></div><div class="drawing-actions"><button class="text-button draw-undo" type="button">Undo</button><button class="text-button draw-clear" type="button">Clear drawing</button><button class="text-button draw-download" type="button">Save image</button></div><label class="activity-text-label"><span>Written description</span><textarea maxlength="500" rows="4" data-primary-text placeholder="${activityEscape(creation.placeholder)}"></textarea><small><span class="activity-character-count">0</span>/500 characters</small></label></div>`;
 }
 return `<div class="creation-version creation-primary" data-creation-version="primary"><p class="creation-stage-label">Primary school activity</p><h4>${activityEscape(creation.title)}</h4><p>${activityEscape(creation.prompt)}</p><p class="activity-tip">${activityEscape(creation.tip)}</p><label class="activity-text-label"><span>Your work</span><textarea maxlength="500" rows="4" data-primary-text placeholder="${activityEscape(creation.placeholder)}"></textarea><small><span class="activity-character-count">0</span>/500 characters</small></label></div>`;
}
function workshopSecondaryCreationMarkup(routeId,secondary){
 const choices=secondary.choices?.length?`<fieldset class="secondary-scene-choice"><legend>Choose a scene</legend>${secondary.choices.map((choice,index)=>`<label><input type="radio" name="secondary-scene-${routeId}" data-secondary-choice value="${activityEscape(choice)}"><span>${index+1}. ${activityEscape(choice)}</span></label>`).join("")}</fieldset>`:"";
 const structure=`<section class="secondary-brief" aria-labelledby="secondary-structure-${routeId}"><h5 id="secondary-structure-${routeId}">Suggested structure</h5><ol>${secondary.structure.map(item=>`<li>${activityEscape(item)}</li>`).join("")}</ol></section>`;
 return `<div class="creation-version creation-secondary" data-creation-version="secondary"><p class="creation-stage-label">Create · ${activityEscape(routes.find(route=>route.id===routeId)?.island||"")} · Secondary school</p><h4>${activityEscape(secondary.title)}</h4><p>${activityEscape(secondary.prompt)}</p>${choices}${structure}<label class="activity-text-label secondary-text-label"><span>Your work</span><textarea maxlength="5000" rows="12" data-secondary-text placeholder="${activityEscape(secondary.placeholder)}"></textarea><small><span class="activity-word-count">0</span> words · <span class="activity-character-count">0</span>/5,000 characters</small></label><p class="secondary-length-note">${activityEscape(secondary.lengthLabel)}</p></div>`;
}
function workshopCreationMarkup(routeId,creation,secondary){
 return `<div class="activity-panel" id="activity-${routeId}-creation" role="tabpanel" aria-labelledby="activity-tab-${routeId}-creation" data-activity-panel="creation" hidden>${workshopPrimaryCreationMarkup(creation)}${workshopSecondaryCreationMarkup(routeId,secondary)}<p class="external-creation-note" hidden></p><div data-creation-review-container></div><button class="button activity-save-creation" data-creation-track="${learningLevel==="secondary"?"secondary":"primary"}" type="button">${learningLevel==="secondary"?"Mark the proposal as ready":"Mark my work as ready"}</button><p class="draft-status" role="status" aria-live="polite"></p><div class="drawing-actions"><button class="text-button activity-download-draft" type="button">Download my draft</button></div><p class="activity-panel-status" role="status" aria-live="polite"></p></div>`;
}
function workshopMarkup(route,activity){
 return `<section class="activity-workshop" id="activity-${route.id}" aria-labelledby="activity-title-${route.id}"><div class="activity-workshop-head"><div><p class="challenge-kicker">Optional activity · Early Years, primary and secondary school</p><h3 id="activity-title-${route.id}">${activityEscape(route.island)} workbook</h3><p>Practise vocabulary, compare information and create something to share. At secondary level, each island suggests a different form of writing. You can earn the piece independently of the workshop.</p></div><span class="activity-workshop-progress" role="status" aria-live="polite">0/3</span></div><div class="activity-tabs" role="tablist" aria-label="Workbook sections"><button id="activity-tab-${route.id}-words" type="button" role="tab" aria-selected="true" aria-controls="activity-${route.id}-words" data-activity-tab="words">1. Vocabulary</button><button id="activity-tab-${route.id}-research" type="button" role="tab" aria-selected="false" aria-controls="activity-${route.id}-research" data-activity-tab="research" tabindex="-1">2. Investigate</button><button id="activity-tab-${route.id}-creation" type="button" role="tab" aria-selected="false" aria-controls="activity-${route.id}-creation" data-activity-tab="creation" tabindex="-1">3. Create</button></div><div class="activity-panel" id="activity-${route.id}-words" role="tabpanel" aria-labelledby="activity-tab-${route.id}-words" data-activity-panel="words"><h4>${activityEscape(activity.words.title)}</h4><p>${activityEscape(activity.words.intro)}</p>${workshopMatchMarkup(route.id,activity.words.match)}${workshopFillMarkup(activity.words)}<button class="button activity-check-words" type="button">Check vocabulary</button><p class="activity-panel-status" role="status" aria-live="polite"></p></div>${workshopResearchMarkup(route.id,activity.research)}${workshopCreationMarkup(route.id,activity.creation,secondaryCreations[route.id])}</section>`;
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
 if(status)status.textContent=ok?"Your draft was saved automatically in this browser.":"Your draft is still on screen. Download a copy before leaving, as saving in this browser failed.";
}
function downloadWorkshopDraft(id){
 const state=getWorkshopRouteState(id),route=routes.find(r=>r.id===id);
 const text=`MitoMapa ${RESOURCE_VERSION} · ${route.island} · ${learningLevelLabel()}
Export format version: ${EXPORT_SCHEMA_VERSION}

CREATIVE WORK
${learningLevel==="secondary"?state.secondaryText:state.text}\n\nSOURCE AND COMPARISON\n${state.researchEvidence}

Personal draft for review with your teacher.`;
 downloadLocalText(text,`mitomapa-draft-${id}.txt`,"text/plain");
}
function downloadLocalText(content,filename,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function updateWorkshopSummary(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const state=getWorkshopRouteState(routeId),creationDone=workshopCreationComplete(state,routeId),selected=selectedNotebookTasks(routeId),completion=notebookCompletion(routeId);
 const completed=selected.filter(key=>completion[key]).length,total=selected.length;
 const progress=workshop.querySelector(".activity-workshop-progress");
 progress.textContent=total?`${completed}/${total} assigned tasks`:"No workbook tasks assigned";
 progress.classList.toggle("is-complete",total>0&&completed===total);
 updateCreationReviewSummary(workshop,routeId);
 Object.keys(completion).forEach(key=>workshop.querySelector(`[data-activity-tab="${key}"]`)?.classList.toggle("is-complete",completion[key]));
 if(state.words)workshop.querySelector('[data-activity-panel="words"] .activity-panel-status').textContent="Vocabulary check complete.";
 if(state.research)workshop.querySelector('[data-activity-panel="research"] .activity-panel-status').textContent="The two questions are complete. Discuss with your teacher what the source supports and what remains uncertain.";
 const status=workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status');
 if(status)status.textContent=creationDone?(itineraryFor(routeId).evidenceMode==="external"?"Your teacher has recorded the review of the work you completed outside the website.":"Your work is marked ready to share with your teacher for review."):"Your work is still being prepared and reviewed.";
}
function checkWorkshopWords(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const panel=workshop.querySelector('[data-activity-panel="words"]');
 let total=0,correct=0,missing=0;
 panel.querySelectorAll(".activity-match-row").forEach(row=>{
  total++;const select=row.querySelector("select"),value=select.value;
  if(!value){missing++;setActivityItemResult(row,"missing","Choose a term.");return;}
  const ok=value===select.dataset.answer;if(ok)correct++;
  setActivityItemResult(row,ok?"correct":"wrong",ok?"Well done!":"Check the story and try again.");
 });
 panel.querySelectorAll(".activity-fill-row").forEach(row=>{
  total++;const input=row.querySelector("input"),value=activityNormalize(input.value);
  if(!value){missing++;input.setAttribute("aria-invalid","true");setActivityItemResult(row,"missing","Enter an answer.");return;}
  const accepted=input.dataset.answers.split("|").map(activityNormalize),ok=accepted.includes(value);
  input.setAttribute("aria-invalid",String(!ok));if(ok)correct++;
  setActivityItemResult(row,ok?"correct":"wrong",ok?"You found it!":input.dataset.hint||"Return to the story and look for a clue.");
 });
 const status=panel.querySelector(".activity-panel-status");
 if(missing){status.textContent=`Please answer the remaining ${missing} ${missing===1?"question":"questions"}.`;return;}
 if(correct===total){const state=getWorkshopRouteState(routeId);state.words=true;const ok=saveWorkshopState();if(!ok)status.textContent="Activity complete on screen. Download your progress to keep a copy.";status.textContent=`Result: ${correct} of ${total}. Activity complete.`;updateWorkshopSummary(routeId);}
 else status.textContent=`Result: ${correct} of ${total}. Check the clues and try again.`;
}
function checkWorkshopResearch(routeId){
 const workshop=byId(`activity-${routeId}`);if(!workshop)return;
 const panel=workshop.querySelector('[data-activity-panel="research"]');
 const questions=[...panel.querySelectorAll(".activity-research-question")];
 let correct=0,missing=0;
 questions.forEach(question=>{
  const checked=question.querySelector("input:checked");
  if(!checked){missing++;setActivityItemResult(question,"missing","Select an answer.");return;}
  const ok=Number(checked.value)===Number(question.dataset.answer);if(ok)correct++;
  const explanation=question.querySelector(".activity-answer-note").textContent;
  setActivityItemResult(question,ok?"correct":"wrong",`${ok?"Well done!":"Try again."} ${explanation}`);
 });
 const status=panel.querySelector(".activity-panel-status");
 if(missing){status.textContent=`Please answer the remaining ${missing} ${missing===1?"question":"questions"}.`;return;}
  if(correct===questions.length){const state=getWorkshopRouteState(routeId);state.research=true;const ok=saveWorkshopState();updateWorkshopSummary(routeId);status.textContent=`Research questions checked: ${correct} of ${questions.length}. Discuss with your teacher what the source supports and what remains uncertain.${ok?"":" Download your progress to keep the work from this visit."}`;}
 else status.textContent=`Result: ${correct} of ${questions.length}. Read the explanation and try again.`;
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
  if(words===0){status.textContent="Write your response or agree an alternative outside the website with your teacher.";return;}
  if(secondary.choices?.length&&!state.secondaryChoice){status.textContent="Choose a scene before saving.";return;}
  if(!itineraryFor(routeId).flexibleLength&&words<secondary.minWords){status.textContent=secondary.minWords>=100?`Your work has ${words} words. Write at least ${secondary.minWords} words.`:`Develop your work a little further. It currently has ${words} ${words===1?"word":"words"}.`;return;}
  if(!itineraryFor(routeId).flexibleLength&&secondary.maxWords&&words>secondary.maxWords){status.textContent=`Your work has ${words} words. The limit is ${secondary.maxWords}. Revise your work to make it shorter.`;return;}
  state.secondaryCreation=true;showDraftStatus(routeId,saveWorkshopState());status.textContent=`Secondary school work ready to share: ${words} words. Your checklist review is saved separately.`;updateWorkshopSummary(routeId);return;
 }
 const zone=panel.querySelector(".creation-primary"),textarea=zone.querySelector("textarea");
 state.text=textarea?.value.trim()||"";
 const hasContent=activity.creation.type==="drawing"?Boolean(state.drawingHasInk||state.text.length>=3):state.text.length>=3;
 if(!hasContent){status.textContent=activity.creation.type==="drawing"?"Draw something or write a description before saving.":"Write at least one short idea before saving.";return;}
 state.creation=true;showDraftStatus(routeId,saveWorkshopState());status.textContent="Your work was saved in this browser.";updateWorkshopSummary(routeId);
}
function setupWorkshopCanvas(workshop,routeId){
 const canvas=workshop.querySelector(".activity-canvas");if(!canvas)return;
 const context=canvas.getContext("2d");if(!context)return;
 const state=getWorkshopRouteState(routeId),baseColor="#fffdf7";
 let drawing=false,lastPoint=null,pendingSnapshot=null,strokeStartPixels=null,currentColor="#2f2b26",history=[];
 const clearSurface=()=>{context.save();context.fillStyle=baseColor;context.fillRect(0,0,canvas.width,canvas.height);context.restore();};
 const restore=async imageData=>{const image=await loadWorkshopDrawing(imageData);clearSurface();if(image)context.drawImage(image,0,0,canvas.width,canvas.height);};
 clearSurface();if(state.drawing)restore(state.drawing);
 const pointFromEvent=event=>{const box=canvas.getBoundingClientRect();return{x:(event.clientX-box.left)*canvas.width/box.width,y:(event.clientY-box.top)*canvas.height/box.height};};
 const snapshot=()=>({image:canvas.toDataURL("image/webp",.82),hasInk:Boolean(state.drawingHasInk)});
 const commitDrawing=()=>{state.drawing=canvas.toDataURL("image/webp",.82);state.drawingHasInk=true;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);};
 // El PNG sin pérdida compara píxeles; el WebP del historial solo se prepara cuando empieza un trazo.
 canvas.addEventListener("pointerdown",event=>{event.preventDefault();pendingSnapshot=null;strokeStartPixels=null;drawing=true;lastPoint=pointFromEvent(event);canvas.setPointerCapture?.(event.pointerId);context.beginPath();context.moveTo(lastPoint.x,lastPoint.y);});
 canvas.addEventListener("pointermove",event=>{if(!drawing)return;event.preventDefault();const next=pointFromEvent(event);if(next.x===lastPoint.x&&next.y===lastPoint.y)return;if(!pendingSnapshot){pendingSnapshot=snapshot();strokeStartPixels=canvas.toDataURL("image/png");}context.strokeStyle=currentColor;context.lineWidth=Number(workshop.querySelector(".draw-size")?.value)||7;context.lineCap="round";context.lineJoin="round";context.lineTo(next.x,next.y);context.stroke();lastPoint=next;});
 const finish=event=>{if(!drawing)return;drawing=false;lastPoint=null;try{canvas.releasePointerCapture?.(event.pointerId);}catch(error){}if(pendingSnapshot&&strokeStartPixels!==canvas.toDataURL("image/png")){history.push(pendingSnapshot);if(history.length>18)history.shift();commitDrawing();}pendingSnapshot=null;strokeStartPixels=null;};
 canvas.addEventListener("pointerup",finish);canvas.addEventListener("pointercancel",finish);canvas.addEventListener("pointerleave",event=>{if(event.buttons===0)finish(event);});
 workshop.querySelectorAll(".draw-color").forEach(button=>button.addEventListener("click",()=>{currentColor=button.dataset.drawColor;workshop.querySelectorAll(".draw-color").forEach(item=>{const selected=item===button;item.classList.toggle("is-selected",selected);item.setAttribute("aria-pressed",String(selected));});}));
 workshop.querySelector(".draw-undo")?.addEventListener("click",async()=>{const previous=history.pop();if(!previous)return;await restore(previous.image);state.drawing=previous.image;state.drawingHasInk=previous.hasInk;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);});
 workshop.querySelector(".draw-clear")?.addEventListener("click",()=>{history.push(snapshot());clearSurface();state.drawing=null;state.drawingHasInk=false;state.creation=false;refreshCreationReviewAfterEdit(workshop,routeId,state,"primary");invalidateItineraryTask(routeId,"creation","primary");showDraftStatus(routeId,saveWorkshopState());updateWorkshopSummary(routeId);workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status').textContent="Drawing cleared.";});
 workshop.querySelector(".draw-download")?.addEventListener("click",()=>{const link=document.createElement("a");link.download="gran-canaria-tibicena.png";link.href=canvas.toDataURL("image/png");link.click();workshop.querySelector('[data-activity-panel="creation"] .activity-panel-status').textContent="Your image is ready to save on this device.";});
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
 const primaryText=panel.querySelector("[data-primary-text]");
 const secondaryText=panel.querySelector("[data-secondary-text]");
 primaryText.value=state.text;
 secondaryText.value=state.secondaryText;
 panel.querySelectorAll("[data-secondary-choice]").forEach(input=>input.checked=input.value===state.secondaryChoice);
 refreshCreationReview(workshop,route.id);
 workshop.addEventListener("change",event=>{
  const select=event.target.closest("select[data-creation-review]");
  if(!select||select.dataset.creationReviewLevel!==learningLevel||!creationReviewCriteria(route.id).some(item=>item.id===select.dataset.creationReview)||!creationReviewOptions.some(option=>option[0]===select.value))return;
  state.creationReviewV1[learningLevel][select.dataset.creationReview]=select.value;
  const track=learningLevel==="secondary"?"secondary":"primary";
  invalidateItineraryTask(route.id,"creation",track,learningLevel);
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
  workshop.querySelector('[data-activity-panel="words"] .activity-panel-status').textContent="Answers changed. Check the vocabulary again.";
 }));
 workshop.querySelectorAll('.activity-research-question input').forEach(input=>input.addEventListener("change",()=>{
  state.researchResponses=[...workshop.querySelectorAll('.activity-research-question')].map(q=>{const chosen=q.querySelector('input:checked');return chosen?Number(chosen.value):null;});state.research=false;invalidateItineraryTask(route.id,"research");saveWorkshopState();updateWorkshopSummary(route.id);
  workshop.querySelector('[data-activity-panel="research"] .activity-panel-status').textContent="Answers changed. Check the research again.";
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
 document.querySelectorAll(".route").forEach(section=>{const route=routes.find(item=>section.id===`route-${item.id}`);if(!route)return;section.querySelector(".activity-workshop")?.remove();injectWorkshop(section,route);window.MitoMapaLearning?.enhance(section,route);window.MitoMapaRouteFlow?.enhance(section,route);});
}
/* Versión 3.6: opción de Secundaria y producciones discursivas por ruta. */
const learningLevelCopy=Object.freeze({
 early:{label:"Early years and first primary cycle",short:"Home",guide:"Story, supported reading and three comprehension questions. Completing the comprehension task earns a piece."},
 middle:{label:"Second primary cycle",short:"Go further",guide:"Story, comprehension, true or false and vocabulary."},
 advanced:{label:"Third primary cycle",short:"Investigate",guide:"Comprehension and true or false, with vocabulary, research and creative tasks agreed with your teacher."},
 secondary:{label:"Secondary",short:"Secondary",guide:"Story, checking sources and a response of your own with the agreed length and support."}
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
 if(badgeStep)badgeStep.textContent=early?"2. Piece":"3. Piece";
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
 note.innerHTML=`<h3>Your route on ${activityEscape(learningLevelLabel())}</h3><ol>${itinerarySteps[learningLevel].map(step=>`<li>${activityEscape(step)}</li>`).join("")}</ol><p class="assigned-tasks" hidden></p><p class="itinerary-status" role="status"></p><p class="itinerary-footnote">Your teacher chooses the tasks. Each learning stage keeps its own record of the review.</p>`;
 updateItineraryUI();
 const sourceKicker=section.querySelector(".source-quiz .challenge-kicker");
 if(sourceKicker)sourceKicker.textContent=early?"True-or-false challenge":"Challenge 1 of 2";
 const truthKicker=section.querySelector(`#quiz-${routeId} .challenge-kicker`);
 if(truthKicker)truthKicker.textContent="Challenge 2 of 2";
 const truthLead=section.querySelector(`#quiz-${routeId}>p:not(.challenge-kicker)`);
 if(truthLead)truthLead.textContent="Choose true or false for each statement. Complete both challenges to earn the piece.";
}

function setLearningLevel(level,persist=true){
 learningLevel=Object.prototype.hasOwnProperty.call(learningLevelCopy,level)?level:"middle";
 document.body.dataset.learningLevel=learningLevel;
 document.querySelectorAll(".learning-level-switch button[data-learning-level]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.learningLevel===learningLevel)));
 const status=byId("learningLevelStatus");
 if(status)status.textContent=`Selected learning stage: ${learningLevelLabel()}. ${learningLevelCopy[learningLevel].guide}`;
 document.querySelectorAll(".route").forEach(applyLearningLevelToRoute);
 if(learningLevel==="early"){const before=earned.size;sourcePassed.forEach(routeId=>earned.add(routeId));if(earned.size!==before)save();}
 if(persist)savePreferences();
 window.MitoMapaStories?.setLevel(learningLevel);
 window.MitoMapaCompare?.setLevel(learningLevel);
 updateProgress();
}

const finalChallengeData=Object.freeze([
 {clue:"Magec lights up Echeyde again",answer:"tenerife"},
 {clue:"A tibicena appears in the ravine",answer:"gran-canaria"},
 {clue:"Idafe seems to hold up the sky",answer:"la-palma"},
 {clue:"Water and fire separate Gara and Jonay",answer:"la-gomera"},
 {clue:"The Garoé turns mist into drops of water",answer:"el-hierro"},
 {clue:"The light of Mafasca follows the goatherds",answer:"fuerteventura"},
 {clue:"Ico passes the trial by smoke",answer:"lanzarote"},
 {clue:"San Borondón appears through the mist",answer:"la-graciosa"}
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
 grid.innerHTML=finalChallengeData.map((item,index)=>`<label class="final-match-item"><span id="final-match-label-${index}"><strong>${index+1}.</strong> ${activityEscape(item.clue)}</span><select data-final-answer="${item.answer}" aria-labelledby="final-match-label-${index}"><option value="">Choose an island</option>${options}</select><small class="final-match-feedback" aria-live="polite"></small></label>`).join("");
}

function updateFinalExperience(){
 const unlocked=currentBadgeCount()===routes.length;
 const challenge=byId("finalChallengeBox");
 const diplomaButton=byId("printDiploma");
 if(challenge)challenge.hidden=!unlocked;
 if(diplomaButton)diplomaButton.disabled=!unlocked;
}

function checkFinalChallenge(){
 const box=byId("finalChallengeBox");
 if(!box||currentBadgeCount()!==routes.length)return;
 const items=[...box.querySelectorAll(".final-match-item")];
 let correct=0,missing=0;
 items.forEach(item=>{
  const select=item.querySelector("select"),feedback=item.querySelector("small");
  const value=select.value,ok=value===select.dataset.finalAnswer;
  if(!value){missing++;feedback.textContent="Choose an island.";item.dataset.result="missing";return;}
  if(ok)correct++;
  item.dataset.result=ok?"correct":"wrong";
  feedback.textContent=ok?"Correct.":"Read the clue and try again.";
 });
 const status=byId("finalChallengeStatus");
 if(missing){status.textContent=`Please answer the remaining ${missing} ${missing===1?"question":"questions"}.`;return;}
 if(correct===items.length){
  finalState.passed=true;saveFinalState();status.textContent="Final challenge complete! You have connected all eight stories.";updateFinalExperience();
 }else status.textContent=`Result: ${correct} of ${items.length}. Check the marked clues.`;
}

function syncLearnerName(value){
 learnerName=String(value||"").replace(/\s+/g," ").trim().slice(0,80);
 const input=byId("teacherLearnerName");
 if(input&&input.value!==learnerName)input.value=learnerName;
 savePreferences();
}

function workshopStageCount(routeId){const completion=notebookCompletion(routeId);return selectedNotebookTasks(routeId).filter(key=>completion[key]).length;}
function teacherTaskMarkup(route){
 const item=itineraryFor(route.id),id=route.id;
 return `<fieldset class="teacher-assignment"><legend>Assigned workbook tasks</legend>${Object.entries(notebookTaskNames).map(([key,label])=>`<label><input type="checkbox" data-assign-route="${id}" data-assign-task="${key}" ${item.selectedTasks.includes(key)?"checked":""}> ${label}</label>`).join("")}</fieldset><label class="assigned-label">Creative work for ${activityEscape(route.island)}<select data-evidence-route="${id}"><option value="web" ${item.evidenceMode==="web"?"selected":""}>On the website</option><option value="external" ${item.evidenceMode==="external"?"selected":""}>Spoken or completed away from the website</option></select></label><label class="external-review" ${item.evidenceMode!=="external"||!item.selectedTasks.includes("creation")?"hidden":""}><input type="checkbox" data-external-route="${id}" ${item.externalCreation?"checked":""}> Work completed away from the website has been reviewed</label>${learningLevel==="secondary"?`<label class="assigned-label"><span><input type="checkbox" data-flexible-route="${id}" ${item.flexibleLength?"checked":""}> Allow a different length for written work</span></label>`:""}`;
}
function teacherStatusWord(done){return done?"Completed":"Pending";}

function updateTeacherDialog(){
 const tbody=byId("teacherProgressBody");
 if(!tbody)return;
 tbody.innerHTML=routes.map(route=>`<tr role="row" data-teacher-island="${route.id}"><th scope="row" role="rowheader">${activityEscape(route.island)}</th><td role="cell" data-label="Comprehension">${teacherStatusWord(sourcePassed.has(route.id))}</td><td role="cell" data-label="Challenge">${learningLevel==="early"?"Optional":teacherStatusWord(truthPassed.has(route.id))}</td><td role="cell" data-label="Workbook">${selectedNotebookTasks(route.id).length?`${workshopStageCount(route.id)}/${selectedNotebookTasks(route.id).length}`:"No tasks"}</td><td role="cell" data-label="Piece">${teacherStatusWord(badgeCountsForLevel(route.id))}</td><td role="cell" data-label="Tasks and review">${teacherTaskMarkup(route)}<label class="review-toggle"><input type="checkbox" data-review-route="${route.id}" ${itineraryFor(route.id).reviewed?"checked":""} aria-label="${activityEscape(route.island)} reviewed with learners at ${activityEscape(learningLevelLabel())}"> Reviewed with learners</label><label class="assigned-label">Agreed tasks for ${activityEscape(route.island)}<textarea data-task-route="${route.id}" rows="2" maxlength="240">${activityEscape(itineraryFor(route.id).tasks)}</textarea></label></td></tr>`).join("");
 window.MitoMapaTeacher?.filterIslands();
 byId("teacherLevelSummary").textContent=learningLevelLabel();
 byId("teacherOverallSummary").textContent=`${currentBadgeCount()}/8 pieces · ${sourcePassed.size}/8 comprehension tasks · ${truthPassed.size}/8 challenges · ${finalState.passed?(currentBadgeCount()===routes.length?"final challenge completed":"final challenge saved. Some requirements for this stage are still pending"):"final challenge pending"}.`;
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
 link.href=url;link.download=`mitomapa-progress-${new Date().toISOString().slice(0,10)}.json`;link.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 byId("teacherImportStatus").textContent="Your progress file is ready to save on this device.";
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

function validateImportFields(value,fields){
 if(value==null)return;
 if(!isRecordValue(value))throw new Error("IMPORT_INVALID");
 for(const [key,accept] of Object.entries(fields))if(value[key]!=null&&!accept(value[key]))throw new Error("IMPORT_INVALID");
}
function validateImportedProgress(payload){
 if(!isRecordValue(payload)||payload.app!=="mitomapa-canario"||!isRecordValue(payload.progress))throw new Error("IMPORT_INVALID");
 const text=value=>typeof value==="string",flag=value=>typeof value==="boolean";
 const strings=value=>Array.isArray(value)&&value.every(text);
 const flags=value=>Array.isArray(value)&&value.every(flag);
 const version=value=>value===1;
 validateImportFields(payload,{schemaVersion:version,version:text,exportedAt:text,learningLevel:text,learnerName:text,
  workshop:isRecordValue,itineraries:isRecordValue,journey:isRecordValue,final:isRecordValue,interactive:isRecordValue});
 validateImportFields(payload.progress,{sourcePassed:strings,truthPassed:strings,earned:strings});
 validateImportFields(payload.final,{passed:flag});
 validateImportFields(payload.workshop,{routes:isRecordValue});
 for(const route of routes){
  const entry=payload.workshop?.routes?.[route.id];
  validateImportFields(entry,{words:flag,research:flag,creation:flag,text,researchEvidence:text,drawing:text,drawingHasInk:flag,
   secondaryCreation:flag,secondaryText:text,secondaryChoice:text,secondaryChecks:flags,wordResponses:isRecordValue,
   researchResponses:value=>Array.isArray(value)&&value.every(item=>item==null||Number.isInteger(item)&&item>=0&&item<3),creationReviewV1:isRecordValue});
  validateImportFields(entry?.wordResponses,{match:strings,fill:strings});
  for(const level of itineraryLevels){
   const review=entry?.creationReviewV1?.[level];
   if(review!=null&&(!isRecordValue(review)||Object.values(review).some(value=>!text(value))))throw new Error("IMPORT_INVALID");
  }
 }
 for(const level of itineraryLevels){
  const entries=payload.itineraries?.[level];
  if(entries!=null&&!isRecordValue(entries))throw new Error("IMPORT_INVALID");
  for(const route of routes)validateImportFields(entries?.[route.id],{reviewed:flag,tasks:text,selectedTasks:strings,evidenceMode:text,externalCreation:flag,flexibleLength:flag});
 }
 validateImportFields(payload.journey,{version,levels:isRecordValue});
 validateImportFields(payload.journey?.levels,Object.fromEntries(itineraryLevels.map(level=>[level,strings])));
 validateImportFields(payload.interactive,{stories:isRecordValue,comparison:isRecordValue});
 validateImportFields(payload.interactive?.stories,{version,routes:isRecordValue});
 for(const route of routes)validateImportFields(payload.interactive?.stories?.routes?.[route.id],{
  order:value=>Array.isArray(value)&&value.length===4&&new Set(value).size===4&&value.every(index=>Number.isInteger(index)&&index>=0&&index<4),
  checked:flag,hint:flag,support:flag});
 const comparison=payload.interactive?.comparison;
 validateImportFields(comparison,{pair:value=>strings(value)&&value.length===2&&value[0]!==value[1]&&value.every(id=>validIds.has(id)),notes:isRecordValue});
 if(comparison?.notes&&Object.values(comparison.notes).some(value=>!text(value)))throw new Error("IMPORT_INVALID");
}
function prepareImportedActivityState(payload){
 const journey={version:1,levels:{}},stories={version:1,routes:{}};
 for(const level of itineraryLevels)journey.levels[level]=[...normalize(payload.journey?.levels?.[level])];
 for(const route of routes){
  const entry=payload.interactive?.stories?.routes?.[route.id];
  if(entry?.order)stories.routes[route.id]={order:[...entry.order],checked:entry.checked===true,hint:entry.hint===true,support:entry.support===true};
 }
 const rawComparison=payload.interactive?.comparison,notes=Object.create(null);
 for(const [key,value] of Object.entries(rawComparison?.notes||{}).slice(0,64)){
  const pair=key.split("|");
  if(pair.length===2&&pair[0]!==pair[1]&&pair.every(id=>validIds.has(id))&&value.slice(0,700))notes[[...pair].sort().join("|")]=value.slice(0,700);
 }
 return {journey,stories,comparison:{pair:rawComparison?.pair?[...rawComparison.pair]:["tenerife","el-hierro"],notes}};
}

async function importProgressFile(file){
 const status=byId("teacherImportStatus");
 if(!file)return;
 if(file.size>5000000){status.textContent="The file is larger than the 5 MB limit.";return;}
 try{
  const payload=JSON.parse(await file.text());
  validateImportedProgress(payload);
  const importedWorkshop=await normalizeImportedDrawings(sanitizeImportedWorkshop(payload.workshop));
  const importedProgress={
   sourcePassed:normalize(payload.progress.sourcePassed),truthPassed:normalize(payload.progress.truthPassed),earned:normalize(payload.progress.earned),
   learningLevel:typeof payload.learningLevel==="string"&&Object.prototype.hasOwnProperty.call(learningLevelCopy,payload.learningLevel)?payload.learningLevel:"middle",
   learnerName:(payload.learnerName||"").replace(/\s+/g," ").trim().slice(0,80),
   final:{passed:payload.final?.passed===true},itineraries:sanitizeItineraries(payload.itineraries),activities:prepareImportedActivityState(payload)
  };
  if(!confirm("Replace the progress in this browser with the progress in the selected file?")){status.textContent="Restore cancelled.";return;}
  // El estado anterior solo se sustituye después de preparar todo el archivo.
  clearLearnerResponses();
  sourcePassed=importedProgress.sourcePassed;truthPassed=importedProgress.truthPassed;earned=importedProgress.earned;
  learningLevel=importedProgress.learningLevel;learnerName=importedProgress.learnerName;
  workshopState=importedWorkshop;
  finalState=importedProgress.final;
  itineraries=importedProgress.itineraries;saveItineraries();
  window.MitoMapaJourney?.importState(importedProgress.activities.journey);
  window.MitoMapaStories?.importState(importedProgress.activities.stories);
  window.MitoMapaCompare?.importState(importedProgress.activities.comparison);
  window.MitoMapaExplorer?.reset();
  window.MitoMapaNames?.reset();window.MitoMapaPieces?.reset();
  save();savePreferences();saveWorkshopState();saveFinalState();
  renderRoutes();setLearningLevel(learningLevel,false);updateTeacherDialog();updateFinalExperience();
  window.MitoMapaNavigation?.refresh();
  status.textContent="Progress restored.";
 }catch(error){status.textContent=error.message==="DRAWING_INVALID"?"The file contains a drawing that is damaged, animated or too large. Your previous progress is still available.":"Choose a valid MitoMapa progress file.";}
}

function clearPrintMode(){
 document.body.classList.remove("print-diploma","print-passport");
}

function prepareDiploma(){
 byId("diplomaPrintDate").textContent=new Intl.DateTimeFormat("en-GB",{dateStyle:"long"}).format(new Date());
 byId("diplomaPrintBadges").innerHTML=routes.map(route=>`<img src="${ASSETS[route.badge]}" alt="">`).join("");
}

function showDiplomaPreview(){
 if(currentBadgeCount()!==routes.length)return;
 prepareDiploma();
 const sheet=byId("diplomaPrint").querySelector(".diploma-sheet").cloneNode(true);
 sheet.querySelectorAll("[id]").forEach(element=>element.removeAttribute("id"));
 byId("diplomaPreview").replaceChildren(sheet);
 ["passportDialog","badgeDialog"].forEach(id=>{const dialog=byId(id);if(dialog?.open)closeDialog(dialog);});
 openDialog(byId("diplomaDialog"));
}

function printDiploma(){
 if(currentBadgeCount()!==routes.length)return;
 ["passportDialog","diplomaDialog"].forEach(id=>{const dialog=byId(id);if(dialog?.open)closeDialog(dialog);});
 prepareDiploma();
 document.body.classList.add("print-diploma");
 requestAnimationFrame(()=>window.print());
}

function printPassport(){
 const grid=byId("passportPrintGrid");
 grid.innerHTML=routes.map(route=>`<article class="passport-print-slot ${badgeCountsForLevel(route.id)?"earned":""}"><img src="${ASSETS[route.badge]}" alt=""><h3>${activityEscape(route.island)}</h3><p>${badgeCountsForLevel(route.id)?activityEscape(route.badgeName):"Piece still to earn"}</p></article>`).join("");
 byId("passportPrintName").textContent=(learnerName?`of ${learnerName}`:"from MitoMapa")+` · ${learningLevelLabel()} · requirements for the selected learning stage`;
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
 window.MitoMapaLearning?.reset?.();
 window.MitoMapaNavigation?.resetResume?.();
 document.querySelectorAll(".route .quiz").forEach(quiz=>{
  quiz.querySelectorAll("input[type=radio]").forEach(input=>{input.checked=false;});
  quiz.querySelectorAll(".feedback").forEach(feedback=>{feedback.className="feedback";feedback.textContent="";});
  quiz.querySelectorAll("fieldset[aria-invalid]").forEach(field=>field.removeAttribute("aria-invalid"));
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
 if(!confirm("Clear the challenges, pieces, final challenge, workbook and additional activities saved in this browser?"))return;
 sourcePassed.clear();truthPassed.clear();earned.clear();
 try{localStorage.removeItem(legacyKey);}catch(error){}
 clearLearnerResponses();resetV34State();window.MitoMapaJourney?.reset();resetAllWorkshops();
 document.querySelectorAll(".route").forEach(applyLearningLevelToRoute);
 window.MitoMapaStories?.reset();window.MitoMapaCompare?.reset();window.MitoMapaExplorer?.reset();window.MitoMapaNames?.reset();window.MitoMapaPieces?.reset();
 shuffle();save();updateProgress();updateTeacherDialog();syncTeacherScroll();
 if(byId("teacherImportStatus"))byId("teacherImportStatus").textContent="Progress reset. The previous session’s answers have been cleared.";
}

function setupV34Features(){
 const teacherDialog=byId("teacherDialog");
 let teacherOpener;
 function openTeacherSpace(panel, control, opener){
  if(!teacherDialog.open){
   teacherOpener=opener;
   updateTeacherDialog();
   window.MitoMapaTeacher?.show(panel,{focus:false});
   openDialog(teacherDialog);
  }
  window.MitoMapaTeacher?.show(panel,{focus:!control});
  if(control)window.MitoMapaTeacher?.focusControl(byId(control));
 }
 teacherDialog.addEventListener("close",()=>{
  const opener=teacherOpener?.getClientRects().length ? teacherOpener : byId("openTeacher");
  opener?.focus({preventScroll:true});
  teacherOpener=null;
 });
 byId("storageExportHelp")?.addEventListener("click",event=>openTeacherSpace("tools","exportProgress",event.currentTarget));
 byId("teacherSaveHelp")?.addEventListener("click",()=>openTeacherSpace("tools","exportProgress"));
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
  row.children[3].textContent=item.selectedTasks.length?`${workshopStageCount(id)}/${item.selectedTasks.length}`:"No tasks";
  saveItineraries();applyNotebookAssignment(id);updateItineraryUI();syncTeacherScroll();
 });
 renderFinalChallenge();
 byId("checkFinalChallenge")?.addEventListener("click",checkFinalChallenge);
 byId("printDiploma")?.addEventListener("click",printDiploma);
 byId("printDiplomaPreview")?.addEventListener("click",printDiploma);
 byId("closeDiploma")?.addEventListener("click",()=>closeDialog(byId("diplomaDialog")));
 byId("openTeacher")?.addEventListener("click",event=>openTeacherSpace("guide",null,event.currentTarget));
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
 if(story&&!section.querySelector(".narrator")){
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
  [sourceBox,truthBox].forEach(box=>box.querySelectorAll(".question").forEach((group,index)=>{
   const feedback=group.querySelector(".feedback");feedback.id=`${box.id}-feedback-${index}`;feedback.removeAttribute("aria-live");group.setAttribute("aria-describedby",feedback.id);
  }));
  enhanceQuizStepper(sourceBox);enhanceQuizStepper(truthBox);
 section.querySelector(".check-source").addEventListener("click",()=>checkSource(route.id));
 section.querySelector(".check-quiz").addEventListener("click",()=>checkQuiz(route.id));
 section.querySelectorAll(".back-map").forEach(button=>{button.textContent="Choose another island";button.addEventListener("click",returnToExploreMap);});
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
  if(narrationState.routeId&&!narrationState.audio)stopNarration("Voice updated. Choose Play to start again.");
 });
 section.querySelector(".narration-rate")?.addEventListener("change",event=>{
  if(narrationState.routeId===route.id&&narrationState.audio){
   narrationState.audio.defaultPlaybackRate=Number(event.currentTarget.value)||1;
   narrationState.audio.playbackRate=narrationState.audio.defaultPlaybackRate;
  }
 });
 section.querySelector(".narration-ambient")?.addEventListener("change",event=>{
  narrationAmbient=event.currentTarget.checked;savePreferences();
  document.querySelectorAll(".narration-ambient").forEach(input=>{input.checked=narrationAmbient;});
  if(narrationState.routeId)changeRecordingAmbient(narrationState.routeId);
 });
 if(!speechSupported&&!routeRecording(route.id))updateNarrationUi(route.id,"idle","This browser cannot read aloud.");
 refreshVoices();updateProgress();
 window.MitoMapaLearning?.enhance(section,route);
 window.MitoMapaReading?.enhance(section,route);
 window.MitoMapaFormats?.enhance(section,route,{stopBase:()=>stopNarration(undefined,{keepFormats:true}),getBaseAudio:()=>narrationState.routeId===route.id?narrationState.audio:null,pauseBase:()=>{if(narrationState.routeId&&!narrationState.paused)toggleNarrationPause(narrationState.routeId);}});
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
 byId("islandGrid").innerHTML=routes.map(route=>`<button class="island-card" type="button" data-route="${route.id}" aria-label="Open the story for ${route.island}: ${route.title}" style="text-align:center"><img src="${ASSETS[route.image]}" alt="${route.imageAlt}" loading="lazy" decoding="async"><span class="card-body" style="display:grid;grid-template-rows:auto minmax(44px,auto) auto;align-content:start;justify-items:center;gap:.35rem;width:100%;box-sizing:border-box;padding:1rem 1.15rem 1.2rem;text-align:center"><strong>${route.island}</strong><span>${route.title}</span><small>${route.badgeName}</small><span class="card-action">Open the story →</span></span></button>`).join("");
 document.querySelectorAll(".island-card").forEach(card=>card.addEventListener("click",()=>showRoute(card.dataset.route,{step:"cuento"})));
 updateProgress();refreshVoices();
}
function checkSource(id){
 const previousCount=currentBadgeCount();
 const route=routes.find(item=>item.id===id),box=byId(`source-${id}`);let correct=0,complete=true,firstIncomplete=-1,firstIncorrect=-1;
 route.quick.forEach((question,index)=>{
  const choice=box.querySelector(`input[name="source-${id}-${index}"]:checked`),feedback=box.querySelectorAll(".feedback")[index];
  if(!choice){complete=false;if(firstIncomplete<0)firstIncomplete=index;feedback.className="feedback ko";feedback.textContent="Select an answer.";return;}
  const ok=Number(choice.value)===question.answer;if(ok)correct++;
  if(!ok&&firstIncorrect<0)firstIncorrect=index;
   feedback.className=`feedback ${ok?"ok":"ko"}`;feedback.textContent=window.MitoMapaLearning?.feedback(id,"source",index,ok,question.hit,question.error)||(ok?question.hit:question.error);
   const group=feedback.closest("fieldset");group?.setAttribute("aria-invalid",String(!ok));
 });
 const status=box.querySelector(".source-status");
 if(!complete){status.textContent="Answer all three questions before checking.";box._showQuestion?.(firstIncomplete,{focus:true});return;}
 if(correct===route.quick.length){sourcePassed.add(id);save();status.textContent=`Result: ${correct} of ${route.quick.length}. Comprehension complete.`;}
 else{status.textContent=`Result: ${correct} of ${route.quick.length}. Check the clues and try again.`;box._showQuestion?.(firstIncorrect,{focus:true});}
 updateProgress();
 if(badgeRequirementsMet(id))tryAward(id,previousCount);
 else if(sourcePassed.has(id))status.textContent+=" Now complete the true-or-false challenge.";
}
function checkQuiz(id){
 const previousCount=currentBadgeCount();
 const route=routes.find(item=>item.id===id),box=byId(`quiz-${id}`);let correct=0,complete=true,firstIncomplete=-1,firstIncorrect=-1;
 route.questions.forEach((question,index)=>{
  const choice=box.querySelector(`input[name="truth-${id}-${index}"]:checked`),feedback=box.querySelectorAll(".feedback")[index];
  if(!choice){complete=false;if(firstIncomplete<0)firstIncomplete=index;feedback.className="feedback ko";feedback.textContent="Select an answer.";return;}
  const ok=(choice.value==="true")===question.answer;if(ok)correct++;
  if(!ok&&firstIncorrect<0)firstIncorrect=index;
   feedback.className=`feedback ${ok?"ok":"ko"}`;feedback.textContent=window.MitoMapaLearning?.feedback(id,"quiz",index,ok,question.feedback,question.hint)||`${ok?"Correct.":"Check your answer."} ${question.feedback}`;
   const group=feedback.closest("fieldset");group?.setAttribute("aria-invalid",String(!ok));
 });
 const status=box.querySelector(".quiz-status");
 if(!complete){status.textContent="Answer all three statements before checking.";box._showQuestion?.(firstIncomplete,{focus:true});return;}
 if(correct===route.questions.length){truthPassed.add(id);save();status.textContent="Result: 3 out of 3. Challenge complete.";}
 else{status.textContent=`Result: ${correct} out of 3. Check the hints and try again.`;box._showQuestion?.(firstIncorrect,{focus:true});}
 updateProgress();
 if(badgeRequirementsMet(id))tryAward(id,previousCount);
 else if(truthPassed.has(id))status.textContent+=" Now complete the comprehension challenge.";
}
const cols=4,rows=3;let order=[],selected=null,dragPosition=null;
function piecePosition(tile){const x=tile%cols,y=Math.floor(tile/cols);return `${x/(cols-1)*100}% ${y/(rows-1)*100}%`;}
function puzzleSolved(){return order.every((value,index)=>value===index);}
function announcePuzzleChange(){
 if(puzzleSolved()){byId("puzzleStatus").className="status success";byId("puzzleStatus").textContent="Map complete! You can start exploring the islands.";}
 else{byId("puzzleStatus").className="status";byId("puzzleStatus").textContent="Pieces swapped. Keep going.";}
}
function swapPuzzlePieces(first,second){if(first===second)return;[order[first],order[second]]=[order[second],order[first]];selected=null;renderPuzzle();announcePuzzleChange();}
function renderPuzzle(){
 const board=byId("puzzleBoard");const focusIndex=[...board.children].indexOf(document.activeElement);board.innerHTML="";
 order.forEach((tile,position)=>{
  const button=document.createElement("button");button.type="button";button.draggable=true;
  button.setAttribute("aria-pressed",String(selected===position));
  button.className="puzzle-piece"+(selected===position?" selected":"");button.style.backgroundPosition=piecePosition(tile);
  button.setAttribute("aria-label",`Piece ${tile+1} at position ${position+1}. Drag or select to exchange.`);
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
 selected=null;renderPuzzle();byId("puzzleStatus").className="status";byId("puzzleStatus").textContent="Map shuffled. Choose two pieces to swap.";
}
function pickPiece(position){
 if(selected===null){selected=position;renderPuzzle();byId("puzzleStatus").textContent="Piece selected. Choose another to swap them.";return;}
 if(selected===position){selected=null;renderPuzzle();return;}
 swapPuzzlePieces(selected,position);
}
byId("shufflePuzzle").addEventListener("click",shuffle);
byId("solvePuzzle").addEventListener("click",()=>{order=[...Array(cols*rows).keys()];selected=null;renderPuzzle();byId("puzzleStatus").className="status success";byId("puzzleStatus").textContent="Solution shown. You can use it to explore the map.";});
byId("openPassport").addEventListener("click",showPassport);
byId("closePassport").addEventListener("click",()=>closeDialog(byId("passportDialog")));
byId("viewPassport").addEventListener("click",()=>{closeDialog(byId("badgeDialog"));showPassport();});
byId("dismissBadge").addEventListener("click",()=>closeDialog(byId("badgeDialog")));
byId("resetProgress").addEventListener("click",resetProgress);
if(speechSupported){window.speechSynthesis.addEventListener?.("voiceschanged",refreshVoices);refreshVoices();}
document.addEventListener("visibilitychange",()=>{if(document.hidden&&narrationState.routeId&&!narrationState.paused)toggleNarrationPause(narrationState.routeId);});
window.addEventListener("pagehide",()=>stopNarration());
window.MitoMapaReading?.init({readJSON,writeJSON});
window.MitoMapaLearning?.init({openStory:(id,options={})=>{
 if(!validIds.has(id))return;
 showRoute(id,{step:"cuento"});
 const section=byId(`route-${id}`),target=typeof options.paragraphId==="string"?byId(options.paragraphId):null;
 if(target&&section?.contains(target)&&target.matches("[data-learning-fragment]")){
  section.querySelector('.format-options input[value="audio-text"]')?.click();
  target.scrollIntoView({block:"center",behavior:"auto"});target.focus({preventScroll:true});
 }
}});
window.MitoMapaStories?.init({readJSON,writeJSON,level:learningLevel});
window.MitoMapaExplorer?.init({routes,assets:ASSETS,openRoute:showRoute,isEarned:badgeCountsForLevel});
window.MitoMapaCompare?.init({routes,assets:ASSETS,openRoute:id=>showRoute(id,{step:"cuento"}),eventsFor:id=>window.MitoMapaStories?.eventsFor(id)||[],readJSON,writeJSON,downloadText:downloadLocalText,level:learningLevel});
injectExperienceTools();renderRoutes();setupV34Features();shuffle();
updateHeaderOffset();
window.MitoMapaNames?.mount();
window.MitoMapaPieces?.mount({routes,assets:ASSETS});
// Recuperar la ruta acordada antes de resolver un enlace directo a Crear.
window.MitoMapaJourney?.init({routes,getLevel:()=>learningLevel,isReviewed:id=>itineraryFor(id).reviewed,assignment:id=>itineraryFor(id),badgeCount:currentBadgeCount,readJSON,writeJSON,onChange:()=>updateItineraryUI()});
window.MitoMapaNavigation?.mount({routes,openRoute:showRoute,stopNarration,lastRoute:()=>lastRouteId,readJSON,writeJSON});
window.MitoMapaTeacher?.init({routes,setLevel:level=>{setLearningLevel(level);updateTeacherDialog();},refresh:syncTeacherScroll});
window.MitoMapaJourney?.refresh();

// Ajustar el salto a la altura real de la cabecera, también al ampliar el texto.
function updateHeaderOffset(){const header=document.querySelector("header"),navigation=document.querySelector(".main-navigation");if(header){const height=Math.ceil(header.getBoundingClientRect().height);document.documentElement.style.setProperty("--topbar-height",`${height}px`);document.documentElement.style.setProperty("--header-offset",`${height+Math.ceil(navigation?.getBoundingClientRect().height||0)+24}px`);}}
if(typeof ResizeObserver!=="undefined"){
  const headerResizeObserver=new ResizeObserver(updateHeaderOffset);
  document.querySelectorAll("header.topbar,.main-navigation").forEach(element=>headerResizeObserver.observe(element));
}
window.addEventListener("resize",updateHeaderOffset);updateHeaderOffset();updateStorageNotice();

// Controles alternativos para barras horizontales ocultas por el sistema.
function syncTeacherScroll(){
 const box=byId("teacherTableViewport"),controls=byId("teacherScrollControls");if(!box||!controls)return;
 const remaining=box.scrollWidth-box.clientWidth;
 controls.hidden=remaining<=1;
 byId("teacherScrollLeft").setAttribute("aria-disabled",String(box.scrollLeft<=1));
 byId("teacherScrollRight").setAttribute("aria-disabled",String(remaining-box.scrollLeft<=1));
}
function moveTeacherColumns(direction){
 const box=byId("teacherTableViewport");
 const control=byId(direction<0?"teacherScrollLeft":"teacherScrollRight");
 if(!box||control?.getAttribute("aria-disabled")==="true")return;
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
const feedbackLabels=["I found the resource easy to use.","The instructions and explanations helped me.","The images and text were clear.","The activity helped me understand the stories and heritage.","I enjoyed the activity and was satisfied with the experience."];
function validFeedbackURL(value){try{const u=new URL(String(value).trim());return u.protocol==="https:"&&(u.hostname==="forms.gle"||u.hostname==="docs.google.com"&&/^\/forms\/(?:d\/e\/[^/]+\/viewform|d\/[^/]+\/viewform)/.test(u.pathname))?u.href:"";}catch(error){return "";}}
function applyFeedbackURL(value){const url=validFeedbackURL(value),link=byId("openWebFeedback");if(link){link.hidden=!url;if(url)link.href=url;else link.removeAttribute("href");}const input=byId("webFeedbackURL");if(input)input.value=url;}
byId("feedbackQuestions").innerHTML=feedbackLabels.map((label,i)=>`<label><span>${activityEscape(label)}</span><select data-feedback-rating="${i}"><option value="">Choose an answer</option>${[1,2,3,4,5].map(n=>`<option value="${n}">${n}</option>`).join("")}<option value="na">I cannot say</option></select></label>`).join("")+`<label><span>What did you like most? (optional)</span><textarea data-feedback-open="liked" maxlength="1000" rows="3"></textarea></label><label><span>What would you change, or what did you find difficult? (optional)</span><textarea data-feedback-open="improve" maxlength="1000" rows="3"></textarea></label>`;
const savedFeedbackConfig=readJSON(feedbackConfigKey,null);
applyFeedbackURL(savedFeedbackConfig?.url??window.MitoMapaConfig?.feedbackFormURL??"");
byId("webFeedbackURL").addEventListener("change",event=>{const value=event.target.value.trim(),url=validFeedbackURL(value);if(value&&!url){byId("feedbackURLStatus").textContent="Use a public Google Forms response link with viewform or forms.gle.";return;}const ok=writeJSON(feedbackConfigKey,{url});applyFeedbackURL(url);byId("feedbackURLStatus").textContent=ok?"Link saved in this browser.":"This browser could not save the link.";});
byId("downloadFeedback").addEventListener("click",()=>{
 const ratings=[...document.querySelectorAll("[data-feedback-rating]")].map((select,i)=>({question:feedbackLabels[i],response:select.value||null}));
 const liked=document.querySelector('[data-feedback-open="liked"]').value.trim(),improve=document.querySelector('[data-feedback-open="improve"]').value.trim();
 if(ratings.every(r=>r.response===null)&&!liked&&!improve){byId("feedbackStatus").textContent="Answer at least one question or leave a comment before downloading your feedback.";return;}
 const response={resource:"MitoMapa web",version:RESOURCE_VERSION,schemaVersion:EXPORT_SCHEMA_VERSION,stage:learningLevelLabel(),ratings,liked,improve};
 downloadLocalText(JSON.stringify(response,null,2),"mitomapa-feedback.json","application/json");
 byId("feedbackStatus").textContent="Your feedback is ready to download. To share it with MitoMapa, choose “Send feedback by email” and attach the file.";
});
