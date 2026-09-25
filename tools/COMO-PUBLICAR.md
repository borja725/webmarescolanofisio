# Publicar un artículo del blog

Manual operativo. Lo que hace Borja desde que Mar manda el audio hasta que el
artículo está en la web.

La guía de Mar es el documento 3 de la carpeta `Docs`. Este es el otro lado del
proceso: el de quien lo ejecuta.

---

## Antes de la primera vez

Necesitas tres cosas instaladas y una comprobación hecha.

| Qué | Para qué | Comprobar con |
|---|---|---|
| Git | bajar y subir cambios | `git --version` |
| Python 3 | ejecutar el generador | `python --version` |
| Claude Code | el agente | `claude --version` |

Y el repositorio clonado:

```bash
git clone https://github.com/borja725/webmarescolanofisio.git
cd webmarescolanofisio
```

**La comprobación pendiente:** hay que confirmar en el panel de Cloudflare que
están activadas las **vistas previa por rama** (*preview deployments*). Sin eso
el paso 5 no funciona y Mar no puede revisar nada antes de publicar. Se
comprueba subiendo una rama cualquiera y mirando si el check verde de GitHub
lleva a una dirección de previsualización.

---

## El ciclo, de principio a fin

### 1. Llega el audio de Mar

Por WhatsApp, en la conversación de siempre. No tiene que estar ordenado ni ser
largo: dos o tres minutos hablando como hablaría en consulta.

Transcríbelo o quédate con las ideas. Da igual el formato: lo que importa es que
llegue **entero**, con sus ejemplos y sus matices, porque eso es exactamente lo
que el agente no puede inventar.

### 2. Prepara la rama

```bash
cd ruta/a/webmarescolanofisio
git checkout master
git pull
git checkout -b post/nombre-corto-del-tema
```

El nombre de la rama da igual mientras empiece por `post/` y se entienda.

### 3. Arranca el agente

```bash
claude
```

Y le pasas el encargo. Puedes copiar esto tal cual y rellenar las dos partes de
abajo:

```
Escribe un artículo nuevo para el blog siguiendo el proceso que ya está montado
en este repositorio.

Lo que ha contado Mar (fisioterapeuta, es quien firma el artículo):

    [PEGA AQUÍ EL AUDIO TRANSCRITO O LAS IDEAS]

Instrucciones:
- Lee tools/publicar-articulo.py para el formato exacto del JSON.
- Mira articulos/*.json como ejemplo del tono y la estructura.
- Escribe el artículo en castellano, valenciano e inglés.
- NO inventes número de sesiones, duración ni precios: eso no lo sabemos.
- Las contraindicaciones nunca como lista cerrada: nombra los casos claros y
  remite a la valoración previa.
- Usa lo que ha contado Mar como eje del artículo, no como adorno.
- Elige una foto que ya exista en images/ y comprueba sus dimensiones reales.
- Cuando termines, ejecuta el generador y su comprobación.
```

El agente creará `articulos/<slug>.json` y ejecutará por su cuenta:

```bash
python tools/publicar-articulo.py articulos/<slug>.json
python tools/publicar-articulo.py --comprobar
```

**La comprobación tiene que decir `problemas: 0`.** Si dice otra cosa, no sigas:
pídele que lo arregle.

### 4. Míralo tú antes que Mar

```bash
python serve.py
```

Y abre en el navegador:

```
http://localhost:8000/blog.html
http://localhost:8000/blog/<slug>.html
```

Aquí no revisas lo clínico —eso es de Mar— sino que **la página esté bien**: que
la foto cargue, que el texto no se corte, que los tres idiomas existan.

Para parar el servidor, `Ctrl+C`.

### 5. Sube la rama y consigue el enlace

```bash
git add -A
git commit -m "post: título del artículo"
git push -u origin post/nombre-corto-del-tema
```

Ahora ve a GitHub, a la pestaña **Branches**, y busca tu rama. Al lado aparece
un **check verde**: pulsa en él y ahí está la dirección de la vista previa.

Esa dirección muestra el artículo tal y como quedaría publicado, pero **la web
pública sigue sin tocar**.

### 6. Mándale el enlace a Mar

Por WhatsApp, la misma conversación. Con eso ya puede leerlo en el móvil.

A partir de aquí decide ella.

---

## Si Mar pide cambios

Vuelve al paso 3 **sin crear rama nueva**: ya estás en ella.

```bash
claude
```

```
Mar ha revisado el artículo y pide estos cambios:

    [LO QUE HA DICHO, CON SUS PALABRAS]

Ajústalo, vuelve a generar las páginas y comprueba.
```

Después repite el paso 5. El enlace de la vista previa **es el mismo**: se
actualiza solo. No hace falta mandarle uno nuevo, aunque avisarla ayuda.

---

## Si Mar dice que sí

```bash
git checkout master
git merge --no-ff post/nombre-corto-del-tema
git push origin master
```

En dos o tres minutos está publicado. Compruébalo:

```
https://marescolanofisioterapia.com/blog
```

Y borra la rama, que ya no hace falta:

```bash
git branch -d post/nombre-corto-del-tema
git push origin --delete post/nombre-corto-del-tema
```

---

## Si algo va mal

**El artículo ya está publicado y hay que quitarlo.**

```bash
git revert -m 1 HEAD
git push origin master
```

Eso deshace la publicación dejando constancia de lo que pasó. En dos minutos ha
desaparecido de la web.

**La comprobación da problemas.** Léelos: dicen exactamente qué falta. Suele ser
una imagen que no existe o un idioma incompleto. Pásaselos al agente.

**El despliegue no termina.** Mira en el panel de Cloudflare si el build ha
fallado o si os habéis quedado sin minutos de compilación. Ya pasó una vez.

**No aparece la vista previa.** Es lo que hay que confirmar antes de empezar
(arriba del todo). Mientras no esté, Mar no puede revisar y no se debe publicar.

---

## Referencia rápida

```bash
# empezar
git checkout master && git pull
git checkout -b post/tema

# el agente hace su trabajo, y luego
python tools/publicar-articulo.py --comprobar   # tiene que decir: problemas: 0
python serve.py                                  # mirar en localhost:8000

# subir para que Mar lo vea
git add -A && git commit -m "post: título" && git push -u origin post/tema

# publicar, cuando Mar diga que sí
git checkout master && git merge --no-ff post/tema && git push origin master

# deshacer, si hiciera falta
git revert -m 1 HEAD && git push origin master
```

---

## Lo único que no se puede saltar

El artículo **no se publica sin que Mar lo haya leído y lo haya dicho**. No es
burocracia: sale firmado con su nombre y su número de colegiada, y si hay algo
impreciso responde ella.

El resto del proceso se puede improvisar. Esto no.
