import { createGlobalStyle } from 'styled-components';

export const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif;
    background-color: #0f172a;
    color: #f8fafc;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  button {
    font-family: inherit;
    cursor: pointer;
    border: none;
    outline: none;
  }
`;