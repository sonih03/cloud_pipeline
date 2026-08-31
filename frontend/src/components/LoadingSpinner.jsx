import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
`;

const Spinner = styled.div`
  width: 44px;
  height: 44px;
  border: 4px solid #334155;
  border-top: 4px solid #38bdf8;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const LoadingText = styled.p`
  font-size: 15px;
  color: #94a3b8;
  font-weight: 500;
`;

export const LoadingSpinner = () => {
    return (
        <SpinnerContainer>
            <Spinner />
            <LoadingText>Gemini가 이미지를 분석하고 데이터셋과 대조하는 중입니다...</LoadingText>
        </SpinnerContainer>
    );
};