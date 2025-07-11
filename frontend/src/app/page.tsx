"use client";

import { useState, ChangeEvent } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [gptResponse, setGptResponse] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 임시 GPT 응답 함수 (실제 API 연동은 추후)
  const handleAsk = async () => {
    setIsLoading(true);
    // 실제 API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 2000));
    setGptResponse('세종대왕은 1392년에 조선을 세웠다. 그는 한글을 창제한 것으로도 유명하며, 조선의 제4대 왕이었다. 세종대왕은 1418년에 즉위하여 1450년까지 재위했다.');
    setAnalysis(""); // 분석 결과 초기화
    setIsLoading(false);
  };

  // 임시 환각 탐지 함수 (실제 로직/연동은 추후)
  const handleDetect = async () => {
    setIsAnalyzing(true);
    // 실제 분석 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1500));
    setAnalysis("• 문장 1: 환각 ❌ (1392년 → 실제로는 1397년)\n• 문장 2: 사실 ✅\n• 문장 3: 사실 ✅\n• 환각률: 33%");
    setIsAnalyzing(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-[480px] bg-white rounded-3xl shadow-2xl p-8 flex flex-col gap-6">
        {/* 헤더 */}
        <div className="flex flex-col items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xl font-bold">🤖</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">AI 환각 탐지기</h1>
          <p className="text-gray-600 text-sm text-center">GPT 응답의 사실 여부를 분석해드립니다</p>
        </div>

        {/* 입력 */}
        <div>
          <label className="block mb-3 text-gray-700 font-semibold text-base">질문을 입력하세요</label>
          <textarea
            className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-base focus:outline-none focus:border-blue-400 bg-gray-50 placeholder-gray-400 text-black transition resize-none"
            value={question}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setQuestion(e.target.value)}
            placeholder="예) 세종대왕은 언제 태어났어?"
            rows={3}
          />
        </div>

        {/* GPT 질문 버튼 */}
        <button
          className={`w-full py-4 text-lg rounded-xl font-semibold shadow-lg transition-all duration-200 flex items-center justify-center gap-2 ${
            isLoading 
              ? 'bg-gray-400 text-black cursor-not-allowed' 
              : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white hover:shadow-xl'
          } disabled:opacity-50`}
          onClick={handleAsk}
          disabled={!question.trim() || isLoading}
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              분석 중...
            </>
          ) : (
            <>
              <span>🤖</span>
              GPT에게 질문하기
            </>
          )}
        </button>

        {/* GPT 응답 */}
        {gptResponse && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="text-gray-700 font-semibold text-base">GPT 응답</div>
            </div>
            <div className="border-2 border-blue-100 rounded-xl p-4 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="text-gray-800 text-base leading-relaxed">
                {gptResponse.split('.').map((sentence: string, index: number) => (
                  sentence.trim() && (
                    <div key={index} className="mb-2 p-2 bg-white rounded-lg border border-blue-200">
                      <span className="text-sm text-blue-600 font-medium">문장 {index + 1}:</span>
                      <p className="mt-1">{sentence.trim()}</p>
                    </div>
                  )
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 환각 탐지 버튼 */}
        {gptResponse && (
          <button
            className={`w-full py-4 text-lg rounded-xl font-semibold shadow-lg transition-all duration-200 flex items-center justify-center gap-2 ${
              isAnalyzing 
                ? 'bg-gray-400 text-white cursor-not-allowed' 
                : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white hover:shadow-xl'
            } disabled:opacity-50`}
            onClick={handleDetect}
            disabled={!gptResponse || isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                분석 중...
              </>
            ) : (
              <>
                <span>🔍</span>
                환각 탐지하기
              </>
            )}
          </button>
        )}

        {/* 분석 결과 */}
        {analysis && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="text-gray-700 font-semibold text-base">분석 결과</div>
            </div>
            <div className="border-2 border-green-100 rounded-xl p-4 bg-gradient-to-r from-green-50 to-emerald-50">
              <div className="space-y-2">
                {analysis.split('\n').map((line: string, index: number) => {
                  if (line.includes('환각 ❌')) {
                    return (
                      <div key={index} className="flex items-center gap-2 p-2 bg-red-100 rounded-lg border border-red-200">
                        <span className="text-red-600">❌</span>
                        <span className="text-red-800 text-sm">{line}</span>
                      </div>
                    );
                  } else if (line.includes('사실 ✅')) {
                    return (
                      <div key={index} className="flex items-center gap-2 p-2 bg-green-100 rounded-lg border border-green-200">
                        <span className="text-green-600">✅</span>
                        <span className="text-green-800 text-sm">{line}</span>
                      </div>
                    );
                  } else if (line.includes('환각률')) {
                    return (
                      <div key={index} className="flex items-center gap-2 p-3 bg-blue-100 rounded-lg border border-blue-200">
                        <span className="text-blue-600">📊</span>
                        <span className="text-blue-800 font-semibold">{line}</span>
                      </div>
                    );
                  }
                  return (
                    <div key={index} className="text-gray-700 text-sm">{line}</div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
