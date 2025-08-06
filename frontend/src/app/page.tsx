'use client';

import { useState } from 'react';
import Image from 'next/image';
import LoginButton from '@/components/LoginButton';
import { useAuthContext } from '@/contexts/AuthContext';
import WikiAnalysisResult, {
  WikiAnalysisResultItem,
} from '@/components/WikiAnalysisResult';

export default function Home() {
  const { user, loading } = useAuthContext();
  const [question, setQuestion] = useState('');
  const [gptResponse, setGptResponse] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [sentences, setSentences] = useState<string[]>([]);
  const [hallucinationResults, setHallucinationResults] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showKeywords, setShowKeywords] = useState(false);
  const [keywordResults, setKeywordResults] = useState<any[]>([]);
  const [isKeywordAnalyzing, setIsKeywordAnalyzing] = useState(false);

  // Wikipedia+SBERT+NLI 분석 state
  const [wikiQuery, setWikiQuery] = useState(
    '이성계는 1392년에 조선을 세웠다.'
  );
  const [wikiKeywords, setWikiKeywords] = useState('');
  const [wikiMainKeyword, setWikiMainKeyword] = useState('');
  const [wikiTopK, setWikiTopK] = useState(5);
  const [wikiResults, setWikiResults] = useState<WikiAnalysisResultItem[]>([]);
  const [showWikiResult, setShowWikiResult] = useState(false);
  const [isWikiAnalyzing, setIsWikiAnalyzing] = useState(false);
  const [wikiError, setWikiError] = useState('');
  const [contradictionPenalty, setContradictionPenalty] = useState(0.5);
  const [neutralPenalty, setNeutralPenalty] = useState(0.25);
  const [saveExcel, setSaveExcel] = useState(true);
  const [expandedKeywords, setExpandedKeywords] = useState<string[]>([]);
  const [originalKeywords, setOriginalKeywords] = useState<string[]>([]);

  // 모달 상태 추가
  const [showDetailModal, setShowDetailModal] = useState(false);

  // GPT API 호출 함수
  const handleAsk = async () => {
    try {
      setGptResponse('응답을 생성하고 있습니다...');
      setAnalysis(''); // 분석 결과 초기화

      // 인증 토큰 가져오기
      const idToken = user ? await user.getIdToken() : null;

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (idToken) {
        headers['Authorization'] = `Bearer ${idToken}`;
      }

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify({ prompt: question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setGptResponse(data.response);

      // GPT 응답을 받으면 문장으로 분리
      const sentenceList = splitIntoSentences(data.response);
      setSentences(sentenceList);

      // GPT 응답을 Wikipedia 분석 섹션으로 자동 이동
      setWikiQuery(data.response);

      // 키워드 추출도 자동으로 실행
      if (sentenceList.length > 0) {
        const keywordResults = await handleKeywordAnalysis();
        // 키워드 추출이 완료되면 Wikipedia 분석 섹션에 자동으로 채우기
        if (keywordResults && keywordResults.length > 0) {
          const allKeywords = keywordResults.flatMap(
            (result) => result.keywords?.map((kw: any) => kw.word) || []
          );
          const uniqueKeywords = [...new Set(allKeywords)];
          setWikiKeywords(uniqueKeywords.join(', '));

          // 가장 긴 키워드를 대표 키워드로 설정
          if (uniqueKeywords.length > 0) {
            const mainKeyword = await selectMainKeyword(
              uniqueKeywords,
              data.response
            );
            setWikiMainKeyword(mainKeyword);
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : '알 수 없는 오류가 발생했습니다';
      setGptResponse(`오류가 발생했습니다: ${errorMessage}`);
    }
  };

  // 문장 분리 함수
  const splitIntoSentences = (text: string) => {
    return text
      .split(/[.!?]+/)
      .filter((sentence) => sentence.trim().length > 0);
  };

  // 가장 긴 키워드를 메인 키워드로 선택하는 함수
  const selectMainKeyword = async (keywords: string[], sentence: string) => {
    if (keywords.length === 0) return '';

    try {
      // GPT에게 핵심 키워드 추출 요청
      const response = await fetch('http://localhost:8000/gpt-keywords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sentence,
          language: 'auto',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('GPT 키워드 추출 결과:', result);

      return result.main_keyword || '';
    } catch (error) {
      console.error('GPT 키워드 추출 오류:', error);

      // GPT 실패 시 기존 로직으로 폴백
      const validKeywords = keywords.filter((keyword) => {
        const cleanKeyword = keyword.replace(/[0-9\s\-_]/g, '');
        return cleanKeyword.length > 0;
      });

      if (validKeywords.length === 0) return keywords[0] || '';

      return validKeywords.reduce((longest, current) =>
        current.length > longest.length ? current : longest
      );
    }
  };

  // 키워드 추출 함수 (실제 ai-engine 연결)
  const handleKeywordAnalysis = async () => {
    console.log('키워드 추출 시작, 문장들:', sentences);

    if (sentences.length === 0) {
      console.log('분석할 문장이 없습니다.');
      return;
    }

    setIsKeywordAnalyzing(true);

    try {
      const keywordPromises = sentences.map(async (sentence) => {
        console.log('분석할 문장:', sentence);

        if (!sentence.trim()) {
          console.log('빈 문장 건너뛰기');
          return null;
        }

        const response = await fetch('http://localhost:8000/keywords', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: sentence.trim(),
            language: 'auto',
          }),
        });

        console.log('API 응답 상태:', response.status);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('키워드 추출 결과:', result);

        // 키워드 결과를 데이터베이스에 저장
        try {
          const saveResponse = await fetch(
            'http://localhost:8000/save_keywords',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                text: sentence.trim(),
                language: result.language || 'auto',
                result: JSON.stringify(result),
              }),
            }
          );
          console.log('키워드 저장 결과:', await saveResponse.json());
        } catch (saveError) {
          console.error('키워드 저장 오류:', saveError);
        }

        return result;
      });

      const results = await Promise.all(keywordPromises);
      const validResults = results.filter((result) => result !== null);
      console.log('전체 키워드 결과:', validResults);
      setKeywordResults(validResults);

      return validResults; // Promise를 반환하도록 수정
    } catch (error) {
      console.error('키워드 추출 오류:', error);
      // 오류 시 기본값으로 폴백
      const fallbackResults = sentences.map((sentence) => {
        const isKorean = /[가-힣]/.test(sentence);
        return {
          sentence: sentence.trim(),
          language: isKorean ? 'ko' : 'en',
          keywords: [],
        };
      });
      setKeywordResults(fallbackResults);
      return fallbackResults; // Promise를 반환하도록 수정
    } finally {
      setIsKeywordAnalyzing(false);
    }
  };

  // 환각 탐지 함수 (테스트 케이스)
  const handleDetect = async () => {
    setIsAnalyzing(true);
    setHallucinationResults([]);
    setAnalysis('');

    try {
      // Wikipedia 분석 호출 (실제 분석은 실행)
      const response = await fetch('http://localhost:8000/analyze/wikipedia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: gptResponse,
          keywords: wikiKeywords
            .split(',')
            .map((k) => k.trim())
            .filter(Boolean),
          main_keyword: wikiMainKeyword,
          top_k: wikiTopK,
          save_excel: saveExcel,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || '분석 실패');
      }

      const data = await response.json();
      console.log('할루시네이션 분석 결과:', data);

      // 결과 처리
      let results = data;
      if (data && typeof data === 'object' && 'candidates' in data) {
        results = data.candidates;
      }

      // 첫 번째 결과만 간단하게 표시
      if (results.length > 0) {
        const firstResult = results[0];
        const isHallucination =
          firstResult.hallucination_judgment === '할루시네이션일 가능성 있음';

        const simpleResult = {
          sentence: gptResponse,
          isHallucination,
          reason: firstResult.hallucination_judgment || '판단 불가',
          similarity: firstResult.similarity,
          nli_label: firstResult.nli_label,
          nli_score: firstResult.nli_score,
        };

        setHallucinationResults([simpleResult]);
        setAnalysis(`할루시네이션률: ${isHallucination ? 100 : 0}%`);

        // 상세 결과는 별도로 저장 (Wikipedia 상세 분석 버튼에서 사용)
        setWikiResults(results);
        setShowWikiResult(false); // 상세 결과는 숨김
      }
    } catch (error) {
      console.error('할루시네이션 분석 오류:', error);
      setAnalysis('분석 실패');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Wikipedia+SBERT+NLI 분석 요청 함수
  const handleWikiAnalyze = async () => {
    setIsWikiAnalyzing(true);
    setWikiResults([]);
    setWikiError('');
    setShowWikiResult(false);
    try {
      console.log('Wikipedia 분석 요청:', {
        query: wikiQuery,
        keywords: wikiKeywords
          .split(',')
          .map((k) => k.trim())
          .filter(Boolean),
        main_keyword: wikiMainKeyword,
        top_k: wikiTopK,
      });

      const response = await fetch('http://localhost:8000/analyze/wikipedia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: wikiQuery,
          keywords: wikiKeywords
            .split(',')
            .map((k) => k.trim())
            .filter(Boolean),
          main_keyword: wikiMainKeyword,
          top_k: wikiTopK,
          save_excel: saveExcel,
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || '분석 실패');
      }
      const data = await response.json();
      console.log('Wikipedia 분석 결과:', data);

      // 백엔드에서 딕셔너리 형태로 반환하는 경우 처리
      let results = data;
      if (data && typeof data === 'object' && 'candidates' in data) {
        results = data.candidates;
        console.log('확장된 키워드 정보:', data.expanded_keywords);
        console.log('원본 키워드 정보:', data.original_keywords);

        // 확장된 키워드 정보 설정
        if (data.expanded_keywords) {
          setExpandedKeywords(data.expanded_keywords);
          setOriginalKeywords(data.original_keywords || []);
        }
      } else {
        // 기존 리스트 형태인 경우
        const keywords = wikiKeywords
          .split(',')
          .map((k) => k.trim())
          .filter(Boolean);
        setExpandedKeywords(keywords);
        setOriginalKeywords(keywords);
      }

      console.log('최종 결과 개수:', results.length);
      setWikiResults(results);
      setShowWikiResult(true);
      console.log('showWikiResult 설정됨:', true);
    } catch (e: any) {
      console.error('Wikipedia 분석 오류:', e);
      setWikiError(e.message || '분석 실패');
    } finally {
      setIsWikiAnalyzing(false);
    }
  };

  // WikiAnalysisResult에 전달할 점수 계산 함수
  const calcFinalScore = (item: WikiAnalysisResultItem) => {
    let penalty = 0;
    if (item.nli_label === 'contradiction') penalty = contradictionPenalty;
    else if (item.nli_label === 'neutral') penalty = neutralPenalty;
    return Math.max(0, item.similarity - penalty);
  };

  const renderMainContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      );
    }

    if (!user) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-600 mb-4">
            서비스를 이용하려면 로그인이 필요합니다.
          </div>
          <div className="text-sm text-gray-500">
            위의 Google 로그인 버튼을 클릭하여 로그인해주세요.
          </div>
        </div>
      );
    }

    return (
      <>
        {/* 입력 */}
        <div>
          <label className="block mb-2 text-black font-medium text-base">
            질문을 입력하세요
          </label>
          <input
            className="w-full border border-black rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-black text-black transition"
            value={question}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setQuestion(e.target.value)
            }
            placeholder="예) 세종대왕은 언제 태어났어?"
          />
        </div>
        {/* GPT 질문 버튼 */}
        <button
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-gray-300 disabled:text-gray-500"
          onClick={handleAsk}
          disabled={!question.trim()}
        >
          GPT에게 질문하기
        </button>

        {/* GPT 응답 - 문장별로 표시 */}
        {gptResponse && (
          <div>
            <div className="text-black font-medium mb-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              GPT 응답
            </div>
            <div className="space-y-3">
              {sentences.length > 0 ? (
                sentences.map((sentence, index) => (
                  <div
                    key={index}
                    className="bg-gray-50 border border-gray-100 rounded-xl p-4"
                  >
                    <div className="text-sm text-gray-500 mb-1">
                      문장 {index + 1}
                    </div>
                    <div className="text-gray-800">{sentence.trim()}</div>
                  </div>
                ))
              ) : (
                <div className="bg-gray-50 border border-gray-100 rounded-xl p-4 text-gray-800">
                  {gptResponse}
                </div>
              )}
            </div>

            {/* 키워드 추출 토글 버튼 */}
            <button
              onClick={async () => {
                if (!showKeywords && sentences.length > 0) {
                  const results = await handleKeywordAnalysis();
                  // 키워드 추출이 완료되면 Wikipedia 분석 섹션에 자동으로 채우기
                  if (results && results.length > 0) {
                    const allKeywords = results.flatMap(
                      (result) =>
                        result.keywords?.map((kw: any) => kw.word) || []
                    );
                    const uniqueKeywords = [...new Set(allKeywords)];
                    setWikiKeywords(uniqueKeywords.join(', '));

                    // 가장 긴 키워드를 대표 키워드로 설정
                    if (uniqueKeywords.length > 0) {
                      const mainKeyword = await selectMainKeyword(
                        uniqueKeywords,
                        gptResponse
                      );
                      setWikiMainKeyword(mainKeyword);
                    }
                  }
                }
                setShowKeywords(!showKeywords);
              }}
              className="w-full bg-purple-500 hover:bg-purple-600 text-white py-2 text-sm rounded-lg font-medium transition flex items-center justify-center gap-2"
            >
              {isKeywordAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  키워드 추출 중...
                </>
              ) : (
                <>
                  🔍 {showKeywords ? '키워드 추출 숨기기' : '키워드 추출 보기'}
                </>
              )}
            </button>

            {/* 키워드 추출 결과 */}
            {showKeywords && keywordResults.length > 0 && (
              <div className="mt-4">
                <div className="text-black font-medium mb-3 flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  키워드 추출 결과
                </div>
                <div className="space-y-3">
                  {keywordResults.map((result, index) => (
                    <div
                      key={index}
                      className="bg-purple-50 border border-purple-200 rounded-xl p-4"
                    >
                      <div className="text-sm text-purple-600 mb-2 font-medium">
                        문장 {index + 1} (
                        {result.language === 'ko' ? '🇰🇷 한국어' : '🇺🇸 영어'})
                      </div>
                      <div className="text-gray-800 mb-3">
                        {result.sentence}
                      </div>
                      <div className="text-sm">
                        <div className="text-purple-700 font-medium mb-2">
                          추출된 키워드 ({result.keywords?.length || 0}개):
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {result.keywords?.map(
                            (keyword: any, keywordIndex: number) => (
                              <span
                                key={keywordIndex}
                                className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs"
                              >
                                {keyword.word} ({keyword.pos})
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 환각 탐지 버튼 */}
        <button
          className="w-full bg-green-500 hover:bg-green-600 text-white py-3 text-lg rounded-xl font-semibold shadow transition disabled:bg-gray-300 disabled:text-gray-500 flex items-center justify-center gap-2"
          onClick={handleDetect}
          disabled={!gptResponse || isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              분석 중...
            </>
          ) : (
            <>🔍 환각 탐지하기</>
          )}
        </button>

        {/* 분석 결과 - 문장별 환각 판정 */}
        {hallucinationResults.length > 0 && (
          <div>
            <div className="text-black font-medium mb-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              {hallucinationResults.length === 1
                ? '할루시네이션 분석 결과'
                : 'Wikipedia 상세 분석 결과'}
            </div>
            <div className="space-y-3">
              {hallucinationResults.map((result, index) => (
                <div
                  key={index}
                  className={`border rounded-xl p-4 ${
                    result.isHallucination
                      ? 'bg-red-50 border-red-200'
                      : 'bg-green-50 border-green-200'
                  }`}
                >
                  <div className="text-sm text-gray-600 mb-3">
                    {result.sentence}
                  </div>
                  <div className="flex items-center gap-2 mb-3">
                    {result.isHallucination ? (
                      <>
                        <span className="text-red-500 text-xl">❌</span>
                        <span className="text-red-700 font-medium">
                          할루시네이션 가능성 있음
                        </span>
                        <span className="text-red-500 text-xl">❌</span>
                      </>
                    ) : (
                      <>
                        <span className="text-green-500 text-xl">✓</span>
                        <span className="text-green-700 font-medium">
                          할루시네이션 가능성이 낮습니다
                        </span>
                        <span className="text-green-500 text-xl">✓</span>
                      </>
                    )}
                  </div>
                  {/* Wikipedia 상세 분석 버튼은 첫 번째 결과에만 표시 */}
                  {hallucinationResults.length === 1 && (
                    <button
                      onClick={() => {
                        // 모달 열기
                        setShowDetailModal(true);
                      }}
                      className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 text-sm rounded-lg font-medium transition flex items-center justify-center gap-2"
                    >
                      📚 Wikipedia 상세 분석
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 상세 분석 모달 */}
        {showDetailModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">
                  Wikipedia 상세 분석 결과
                </h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-3">
                {wikiResults.slice(0, 5).map((result: any, index: number) => (
                  <div
                    key={index}
                    className={`border rounded-xl p-4 ${
                      result.hallucination_judgment ===
                      '할루시네이션일 가능성 있음'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-green-50 border-green-200'
                    }`}
                  >
                    <div className="text-sm text-gray-600 mb-3">
                      {result.sentence}
                    </div>
                    <div className="flex items-center gap-2 mb-3">
                      {result.hallucination_judgment ===
                      '할루시네이션일 가능성 있음' ? (
                        <>
                          <span className="text-red-500 text-xl">❌</span>
                          <span className="text-red-700 font-medium">
                            할루시네이션 가능성 있음
                          </span>
                          <span className="text-red-500 text-xl">❌</span>
                        </>
                      ) : (
                        <>
                          <span className="text-green-500 text-xl">✓</span>
                          <span className="text-green-700 font-medium">
                            할루시네이션 가능성이 낮습니다
                          </span>
                          <span className="text-green-500 text-xl">✓</span>
                        </>
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      <div>판단: {result.hallucination_judgment || 'N/A'}</div>
                      <div>
                        유사도: {Math.round(result.similarity * 1000) / 1000}
                      </div>
                      <div>
                        NLI: {result.nli_label} (
                        {Math.round(result.nli_score * 1000) / 1000})
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </>
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="w-full max-w-[480px] bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-6">
        {/* 헤더 */}
        <div className="flex flex-col items-center gap-3 mb-4">
          <div className="w-16 h-16 flex items-center justify-center">
            <Image
              src="/ai-logo.jpg"
              alt="AI Logo"
              width={64}
              height={64}
              className="w-16 h-16"
            />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">AI 환각 탐지기</h1>
          <p className="text-gray-600 text-center text-sm">
            GPT 응답의 사실 여부를 분석해드립니다
          </p>
          <div className="mt-2">
            <LoginButton />
          </div>
        </div>
        {renderMainContent()}
      </div>
    </div>
  );
}
