import { describe, it, expect } from 'vitest';
import { NAV_ITEMS, visibleNavItems } from './nav-items';

describe('visibleNavItems', () => {
  it('mostra todos os destinos no navegador', () => {
    expect(visibleNavItems(false)).toHaveLength(NAV_ITEMS.length);
  });

  it('esconde chat, ai-insights e integrations no app instalado', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    expect(rotas).toEqual(['/', '/loans', '/actors']);
  });

  it('nunca esconde as telas de dinheiro', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    for (const r of ['/', '/loans', '/actors']) {
      expect(rotas).toContain(r);
    }
  });

  it('não perde nenhum destino que existia no menu do web', () => {
    const rotas = NAV_ITEMS.map((i) => i.to);
    expect(rotas).toEqual([
      '/', '/loans', '/actors', '/chat', '/integrations', '/ai-insights',
    ]);
  });
});
