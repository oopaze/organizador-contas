import { fireEvent, render, screen } from '@testing-library/react-native';
import { SafeAreaInsetsContext } from 'react-native-safe-area-context';
import { Sheet } from '../sheet';

function withInsets(children: React.ReactNode, bottom: number) {
  return (
    <SafeAreaInsetsContext.Provider value={{ top: 0, right: 0, bottom, left: 0 }}>
      {children}
    </SafeAreaInsetsContext.Provider>
  );
}

test('renderiza conteúdo quando visível e fecha no requestClose do Android', async () => {
  const onClose = jest.fn();
  await render(
    <Sheet visible onClose={onClose} title="Conversas">
      <></>
    </Sheet>
  );

  expect(screen.getByText('Conversas')).toBeTruthy();

  fireEvent(screen.getByTestId('sheet-modal'), 'requestClose');
  expect(onClose).toHaveBeenCalled();
});

test('não renderiza conteúdo quando fechado', async () => {
  await render(
    <Sheet visible={false} onClose={() => {}} title="Conversas">
      <></>
    </Sheet>
  );

  expect(screen.queryByText('Conversas')).toBeNull();
});

test('afasta o painel da barra de navegação do Android (edge-to-edge)', async () => {
  await render(
    withInsets(
      <Sheet visible onClose={() => {}} title="Ações">
        <></>
      </Sheet>,
      34
    )
  );

  expect(screen.getByTestId('sheet-panel')).toHaveStyle({ paddingBottom: 34 });
});
