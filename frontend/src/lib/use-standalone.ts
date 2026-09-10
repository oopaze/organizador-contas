import { useEffect, useState } from 'react';

const QUERY = '(display-mode: standalone)';

function detect(): boolean {
  if (typeof window === 'undefined') return false;
  // navigator.standalone é o caminho do Safari iOS legado, sem tipo padrão.
  const iosLegacy = (window.navigator as Navigator & { standalone?: boolean }).standalone;
  return window.matchMedia(QUERY).matches || iosLegacy === true;
}

/** true quando rodando como app instalado, não numa aba do navegador. */
export function useStandalone(): boolean {
  const [standalone, setStandalone] = useState(detect);

  useEffect(() => {
    const mql = window.matchMedia(QUERY);
    const onChange = () => setStandalone(detect());
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  return standalone;
}
