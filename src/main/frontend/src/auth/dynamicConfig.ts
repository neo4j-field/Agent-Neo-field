declare global {
  interface Window {
    _dynamicEnv_?: Record<string, string>;
  }
}


export const getDynamicConfigValue = (envKey: string): string | undefined => {
    let value: string | undefined;

    if (window._dynamicEnv_ && typeof window._dynamicEnv_[envKey] !== 'undefined') {
        value = window._dynamicEnv_[envKey];
    } else {
        value = process.env[envKey];
    }

    return value;
}