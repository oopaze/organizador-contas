import { describe, it, expect } from 'vitest';
import { NAV_ITEMS, visibleNavItems } from './nav-items';

describe('visibleNavItems', () => {
  it('mostra todos os destinos no navegador', () => {
    expect(visibleNavItems(false)).toHaveLength(NAV_ITEMS.length);
  });

  it('esconde apenas integrations no app instalado', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    expect(rotas).toEqual(['/', '/planning', '/loans', '/actors']);
  });

  it('nunca esconde as telas de dinheiro', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    for (const r of ['/', '/planning', '/loans', '/actors']) {
      expect(rotas).toContain(r);
    }
  });

  it('não expõe mais os destinos de IA no menu (só integrations)', () => {
    const rotas = NAV_ITEMS.map((i) => i.to);
    expect(rotas).toEqual([
      '/', '/planning', '/loans', '/actors', '/integrations',
    ]);
    expect(rotas).not.toContain('/chat');
    expect(rotas).not.toContain('/ai-insights');
  });
});
