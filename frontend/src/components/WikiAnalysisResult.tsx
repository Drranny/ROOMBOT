import React, { useState } from 'react';

export interface WikiAnalysisResultItem {
  sentence: string;
  original_sentence?: string; // 원본 문장 (요약된 문장과 구분)
  matched_keywords: string[];
  url: string;
  similarity: number;
  nli_label: string;
  nli_score: number;
  final_score?: number; // 백엔드에서 올 수도 있으니 optional
  summary_method?: string; // 요약 방식 (GPT-4o-mini, 키워드 요약, 원본 등)
}

interface WikiAnalysisResultProps {
  results: WikiAnalysisResultItem[];
  calcFinalScore: (item: WikiAnalysisResultItem) => number;
}

const labelColor = (label: string) => {
  switch (label) {
    case 'entailment':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'contradiction':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'neutral':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

const WikiAnalysisResult: React.FC<WikiAnalysisResultProps> = ({
  results,
  calcFinalScore,
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  console.log('WikiAnalysisResult 렌더링:', {
    results,
    resultsLength: results?.length,
  });

  const toggleRow = (index: number) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(index)) {
      newExpandedRows.delete(index);
    } else {
      newExpandedRows.add(index);
    }
    setExpandedRows(newExpandedRows);
  };

  if (!results || results.length === 0)
    return <div className="mt-6 text-center text-gray-500">검색결과 없음</div>;

  return (
    <div className="mt-6">
      <div className="text-black font-medium mb-3 flex items-center gap-2">
        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
        Wikipedia+SBERT+NLI 분석 결과
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border text-sm rounded-xl overflow-hidden">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-3 py-2 border">포함 키워드</th>
              <th className="px-3 py-2 border">유사도</th>
              <th className="px-3 py-2 border">NLI</th>
              <th className="px-3 py-2 border">NLI 점수</th>
              <th className="px-3 py-2 border">최종 점수</th>
              <th className="px-3 py-2 border">요약 방식</th>
              <th className="px-3 py-2 border">위키 링크</th>
              <th className="px-3 py-2 border">문장</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item, idx) => (
              <tr key={idx} className="border-b">
                <td className="px-3 py-2 border">
                  {item.matched_keywords.join(', ')}
                </td>
                <td className="px-3 py-2 border">
                  {Math.round(item.similarity * 1000) / 1000}
                </td>
                <td
                  className={`px-3 py-2 border font-bold ${labelColor(
                    item.nli_label
                  )}`}
                >
                  {item.nli_label}
                </td>
                <td className="px-3 py-2 border">
                  {Math.round(item.nli_score * 1000) / 1000}
                </td>
                <td className="px-3 py-2 border">
                  {Math.round(calcFinalScore(item) * 1000) / 1000}
                </td>
                <td className="px-3 py-2 border">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      item.summary_method === 'GPT-4o-mini'
                        ? 'bg-blue-100 text-blue-700 border border-blue-200'
                        : item.summary_method === '키워드 요약'
                        ? 'bg-green-100 text-green-700 border border-green-200'
                        : 'bg-gray-100 text-gray-700 border border-gray-200'
                    }`}
                  >
                    {item.summary_method || '원본'}
                  </span>
                </td>
                <td className="px-3 py-2 border">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline"
                  >
                    위키
                  </a>
                </td>
                <td className="px-2 py-1 border text-left min-w-[120px] max-w-[260px]">
                  <button
                    onClick={() => toggleRow(idx)}
                    className="text-blue-600 hover:text-blue-800 font-medium mb-1 text-xs px-1 py-0.5 border border-blue-200 rounded"
                  >
                    {expandedRows.has(idx) ? '문장 숨기기' : '문장 보기'}
                  </button>
                  {expandedRows.has(idx) && (
                    <div className="break-words whitespace-pre-line bg-gray-50 p-1 rounded border mt-1 text-xs">
                      <div className="mb-2">
                        <strong className="text-blue-600">요약된 문장:</strong>
                        <div className="mt-1">{item.sentence}</div>
                      </div>
                      {item.original_sentence &&
                        item.original_sentence !== item.sentence && (
                          <div>
                            <strong className="text-gray-600">
                              원본 문장:
                            </strong>
                            <div className="mt-1 text-gray-500">
                              {item.original_sentence}
                            </div>
                          </div>
                        )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default WikiAnalysisResult;
