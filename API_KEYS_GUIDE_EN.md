# API Keys Acquisition Guide

To ensure the **LangMeta** project functions correctly, you need to configure two types of keys in your `.env` file.

## 1. Local Access Key (API_KEY)

This key protects your FastAPI server. Any person or application wishing to query your endpoints (such as `/posts` or `/logs`) must include this key in the `X-API-Key` header.

**How to generate it:**
You can use any secure string. A quick way to generate a random key on Linux/macOS is:
```bash
openssl rand -hex 32
```
Copy the result and paste it into your `.env` file:
```env
API_KEY=your_generated_key_here
```

---

## 2. Meta Keys (Facebook/Instagram)

To interact with the Meta Graph API, follow these steps:

### Step 1: Create an Application in Meta for Developers
1. Go to [Meta for Developers](https://developers.facebook.com/).
2. Log in and go to **My Apps** -> **Create App**.
3. Select the app type (usually **Business** or **Consumer**).
4. Give it a name and complete the process.

### Step 2: Obtain the Access Token (META_ACCESS_TOKEN)
1. In your app dashboard, go to **Tools** -> **Graph API Explorer**.
2. In the "Meta App" dropdown, select the app you just created.
3. In "User or Page", select the page or Instagram account you want to manage.
4. **Required Permissions:** Make sure to add at least:
   - `instagram_basic`
   - `instagram_manage_comments`
   - `pages_show_list`
   - `pages_read_engagement`
5. Click **Generate Access Token**.
6. Copy this token into your `.env`: `META_ACCESS_TOKEN=...`

*Note: This token is temporary (lasts 1-2 hours). For production, you should use the "Access Token Tool" to get a long-lived token (60 days).*

### Step 3: Obtain the Account ID (META_ACCOUNT_ID)
This is the numerical ID of your Instagram Business account or Facebook Page.
- In the **Graph API Explorer**, you can get it by typing `me?fields=id,name` in the search bar and clicking **Submit**.

### Step 4: Obtain the App Secret (META_APP_SECRET)
1. In the side panel of your app in Meta, go to **Settings** -> **Basic**.
2. Look for the **App Secret** field. Click "Show" (it will ask for your Facebook password).
3. Copy it into your `.env`: `META_APP_SECRET=...`

### Step 5: Define the Webhook Verify Token (META_WEBHOOK_VERIFY_TOKEN)
This token is **made up by you**. It's a random string you'll use to tell Meta: "It's me, trust my server."
- Example: `META_WEBHOOK_VERIFY_TOKEN=my_secret_token_123`

---

## .env File Summary
Your `.env` file should look like this:

```env
META_ACCESS_TOKEN=EAAb... (long token)
META_ACCOUNT_ID=1234567890
META_API_VERSION=v19.0
META_WEBHOOK_VERIFY_TOKEN=your_invented_token
META_APP_SECRET=your_meta_app_secret
API_KEY=your_secure_local_key
```
