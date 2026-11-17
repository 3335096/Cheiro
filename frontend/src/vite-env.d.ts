/// <reference types="vite/client" />

interface TelegramWebApp {
  initData: string;
  ready: () => void;
  expand: () => void;
  colorScheme?: "light" | "dark";
}

interface TelegramNamespace {
  WebApp?: TelegramWebApp;
}

interface Window {
  Telegram?: TelegramNamespace;
}
