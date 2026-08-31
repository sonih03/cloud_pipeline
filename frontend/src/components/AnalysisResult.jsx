import React from 'react';
import styled from 'styled-components';
import { Sparkles, Utensils } from 'lucide-react';

const Card = styled.div`
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #334155;
  padding-bottom: 12px;
`;

const TitleBox = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #38bdf8;
`;

const CategoryBadge = styled.span`
  background-color: #0369a1;
  color: #e0f2fe;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const AnalysisText = styled.p`
  font-size: 15px;
  line-height: 1.7;
  color: #cbd5e1;
  white-space: pre-wrap;
`;

export const AnalysisResult = ({ predictedCategory, similarityAnalysis }) => {
    return (
        <Card>
            <Header>
                <TitleBox>
                    <Sparkles size={20} />
                    Gemini RAG 멀티모달 판별 결과
                </TitleBox>
                <CategoryBadge>
                    <Utensils size={14} />
                    {predictedCategory}
                </CategoryBadge>
            </Header>
            <AnalysisText>{similarityAnalysis}</AnalysisText>
        </Card>
    );
};