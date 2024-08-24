/// <reference types="vite/client" />



interface ImportMetaEnv {
  readonly VITE_BACKEND_ADDRESS: string;
  readonly VITE_AUTH_DOMAIN: string;
  readonly VITE_AUTH_CALLBACK: string;
  readonly VITE_AUTH_LOGOUT_URL: string;
  readonly VITE_AUTH_CLIENT_ID: string;
  readonly VITE_AUTH_METHOD: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}