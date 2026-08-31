import React from 'react';
import styled from 'styled-components';
import { Database } from 'lucide-react';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const SectionTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
`;

const ImageCard = styled.div`
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const MatchedImage = styled.img`
  width: 100%;
  height: 140px;
  object-fit: cover;
`;

const FileInfo = styled.div`
  padding: 8px 12px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

export const MatchedGallery = ({ matchedImages = [] }) => {
    if (!matchedImages.length) return null;

    return (
        <Container>
            <SectionTitle>
                <Database size={16} />
                로컬 데이터셋 검색 이미지 ({matchedImages.length}건)
            </SectionTitle>
            <Grid>
                {matchedImages.map((item, index) => {
                    // 백엔드 static 마운트 경로 조합
                    const imageUrl = `/static/images/${item.category}/${item.file_name}`;
                    return (
                        <ImageCard key={index}>
                            <MatchedImage
                                src={imageUrl}
                                alt={`${item.category} ${index + 1}`}
                                onError={(e) => {
                                    e.currentTarget.src = 'https://via.placeholder.com/180x140?text=No+Image';
                                }}
                            />
                            <FileInfo title={item.file_name}>{item.file_name}</FileInfo>
                        </ImageCard>
                    );
                })}
            </Grid>
        </Container>
    );
};