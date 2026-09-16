import { en } from "./locales/en.js";
import { it } from "./locales/it.js";
import { es } from "./locales/es.js";
import { fr } from "./locales/fr.js";
import { tr } from "./locales/tr.js";

const translations = { en, it, es, fr, tr };

export const supportedLocales = [
    { code: "en", label: "English", flag: "🇺🇸", nativeName: "English" },
    { code: "it", label: "Italiano", flag: "🇮🇹", nativeName: "Italiano" },
    { code: "tr", label: "Türkçe", flag: "🇹🇷", nativeName: "Türkçe" },
    { code: "es", label: "Español", flag: "🇪🇸", nativeName: "Español" },
    { code: "fr", label: "Français", flag: "🇫🇷", nativeName: "Français" },

];

function getInitialLocale() {
    if (typeof window === "undefined" || !window.localStorage) {
        return "en";
    }
    try {
        const saved = localStorage.getItem("vetsentinel-lang");
        if (saved && translations[saved]) {
            return saved;
        }
        const navLang = window.navigator?.language?.slice(0, 2);
        if (navLang && translations[navLang]) {
            return navLang;
        }
    } catch {
        // Ignore storage restrictions
    }
    return "en";
}

export const i18nState = $state({
    locale: getInitialLocale(),
});

export function setLocale(lang) {
    if (!translations[lang]) return;
    i18nState.locale = lang;
    if (typeof window !== "undefined") {
        try {
            localStorage.setItem("vetsentinel-lang", lang);
            document.documentElement.setAttribute("lang", lang);
        } catch {
            // Ignore
        }
    }
}

export function t(path, params = null) {
    const current = i18nState.locale;
    const dict = translations[current] || translations.en;

    const parts = path.split(".");
    let val = parts.reduce(
        (acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined),
        dict,
    );

    // Fallback to English if translation is missing in current locale
    if (val === undefined && current !== "en") {
        val = parts.reduce(
            (acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined),
            translations.en,
        );
    }

    if (val === undefined) {
        return path;
    }

    if (typeof val === "string" && params) {
        let result = val;
        for (const [key, replacement] of Object.entries(params)) {
            result = result.replaceAll(`{${key}}`, replacement);
        }
        return result;
    }

    return val;
}
