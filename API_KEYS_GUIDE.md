# Guía para la Obtención de API Keys

Para que el proyecto **LangMeta** funcione correctamente, necesitas configurar dos tipos de claves en tu archivo `.env`.

## 1. Clave de Acceso Local (API_KEY)

Esta clave protege tu servidor FastAPI. Cualquier persona o aplicación que quiera consultar tus endpoints (como `/posts` o `/logs`) deberá incluir esta clave en el encabezado `X-API-Key`.

**Cómo generarla:**
Puedes usar cualquier cadena de texto segura. Una forma rápida de generar una clave aleatoria en Linux/macOS es:
```bash
openssl rand -hex 32
```
Copia el resultado y pégalo en tu archivo `.env`:
```env
API_KEY=tu_clave_generada_aqui
```

---

## 2. Claves de Meta (Facebook/Instagram)

Para interactuar con la Graph API de Meta, debes seguir estos pasos:

### Paso 1: Crear una Aplicación en Meta for Developers
1. Ve a [Meta for Developers](https://developers.facebook.com/).
2. Inicia sesión y ve a **Mis apps** -> **Crear app**.
3. Selecciona el tipo de app (usualmente **Negocios** o **Consumidor**).
4. Dale un nombre y completa el proceso.

### Paso 2: Obtener el Access Token (META_ACCESS_TOKEN)
1. En el panel de tu app, ve a **Herramientas** -> **Graph API Explorer**.
2. En el menú desplegable "Meta App", selecciona la app que acabas de crear.
3. En "User or Page", selecciona la página o cuenta de Instagram que quieres gestionar.
4. **Permisos necesarios:** Asegúrate de agregar al menos:
   - `instagram_basic`
   - `instagram_manage_comments`
   - `pages_show_list`
   - `pages_read_engagement`
5. Haz clic en **Generate Access Token**.
6. Copia este token en tu `.env`: `META_ACCESS_TOKEN=...`

*Nota: Este token es temporal (dura 1-2 horas). Para producción, deberás usar el "Access Token Tool" para obtener un token de larga duración (60 días).*

### Paso 3: Obtener el Account ID (META_ACCOUNT_ID)
Es el ID numérico de tu cuenta de Instagram Business o Página de Facebook.
- En el **Graph API Explorer**, puedes obtenerlo escribiendo `me?fields=id,name` en la barra de búsqueda y dándole a **Submit**.

### Paso 4: Obtener el App Secret (META_APP_SECRET)
1. En el panel lateral de tu app en Meta, ve a **Configuración** -> **Básica**.
2. Busca el campo **Clave secreta de la aplicación**. Haz clic en "Mostrar" (te pedirá tu contraseña de Facebook).
3. Cópialo en tu `.env`: `META_APP_SECRET=...`

### Paso 5: Definir el Webhook Verify Token (META_WEBHOOK_VERIFY_TOKEN)
Este token **lo inventas tú**. Es una cadena de texto aleatoria que usarás para decirle a Meta: "Soy yo, confía en mi servidor".
- Ejemplo: `META_WEBHOOK_VERIFY_TOKEN=mi_token_secreto_123`

---

## Resumen del archivo .env
Tu archivo `.env` debería verse así:

```env
META_ACCESS_TOKEN=EAAb... (token largo)
META_ACCOUNT_ID=1234567890
META_API_VERSION=v19.0
META_WEBHOOK_VERIFY_TOKEN=tu_token_inventado
META_APP_SECRET=tu_app_secret_de_meta
API_KEY=tu_clave_local_segura
```
