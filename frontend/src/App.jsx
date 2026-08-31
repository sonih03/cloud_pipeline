import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GlobalStyle } from './styles/GlobalStyle';
import { ImageRagPage } from './pages/ImageRagPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
      <QueryClientProvider client={queryClient}>
        <GlobalStyle />
        <ImageRagPage />
      </QueryClientProvider>
  );
}

export default App;