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
  background-color: #0f172a;
`;

const FileInfo = styled.div`
  padding: 8px 12px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

// 외부 접속 없이 즉시 렌더링되는 안전한 대체 이미지 (SVG Data URL)
const FALLBACK_IMAGE = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='140' viewBox='0 0 180 140'%3E%3Crect width='180' height='140' fill='%231e293b'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2364748b' font-size='12'%3EImage Not Found%3C/text%3E%3C/svg%3E";

export const MatchedGallery = ({ matchedImages = [] }) => {
    if (!matchedImages.length) return null;

    return (
        <Container>
            <SectionTitle>
                <Database size={16} />
                S3 매칭 데이터셋 ({matchedImages.length}건)
            </SectionTitle>
            <Grid>
                {matchedImages.map((item, index) => (
                    <ImageCard key={index}>
                        <MatchedImage
                            src={item.image_url}
                            alt={`${item.category} ${index + 1}`}
                            onError={(e) => {
                                // 무한 루프 방지: 한 번 에러 나면 더 이상 onError 실행 안 함
                                e.currentTarget.onerror = null;
                                e.currentTarget.src = FALLBACK_IMAGE;
                            }}
                        />
                        <FileInfo title={item.file_name}>{item.file_name}</FileInfo>
                    </ImageCard>
                ))}
            </Grid>
        </Container>
    );
};