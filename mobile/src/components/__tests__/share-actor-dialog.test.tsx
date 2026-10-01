jest.mock('../../services', () => ({
  getActorShareToken: jest.fn().mockResolvedValue({ token: 'abc' }),
}));

import { render, screen } from '@testing-library/react-native';
import { ShareActorDialog } from '../share-actor-dialog';

test('monta o link web do ator com o token', async () => {
  await render(<ShareActorDialog visible actorId={7} onClose={() => {}} />);
  expect(await screen.findByText(/\/share\/actor\?token=abc/)).toBeTruthy();
});
