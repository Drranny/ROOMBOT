from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import logging

logger = logging.getLogger(__name__)

class TextSummarizer:
    def __init__(self, model_name="t5-small"):
        """
        T5 모델을 사용한 텍스트 요약기 초기화
        
        Args:
            model_name: 사용할 T5 모델명 (기본값: t5-small)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """모델과 토크나이저를 로드합니다."""
        try:
            logger.info(f"Loading T5 model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
            logger.info(f"T5 model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load T5 model: {str(e)}")
            raise
    
    def summarize_text(self, text, max_length=50, min_length=10):
        """
        텍스트를 요약합니다.
        
        Args:
            text: 요약할 텍스트
            max_length: 최대 요약 길이
            min_length: 최소 요약 길이
            
        Returns:
            요약된 텍스트
        """
        if not self.model or not self.tokenizer:
            self.load_model()
        
        try:
            # 입력 텍스트를 토큰화
            inputs = self.tokenizer.encode(
                f"summarize: {text}",
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # 요약 생성
            summary_ids = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            # 토큰을 텍스트로 디코딩
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            return text  # 실패시 원본 텍스트 반환
    
    def summarize_sentences(self, sentences, max_length=50, min_length=10):
        """
        여러 문장들을 요약합니다.
        
        Args:
            sentences: 요약할 문장들의 리스트
            max_length: 최대 요약 길이
            min_length: 최소 요약 길이
            
        Returns:
            요약된 문장들의 리스트
        """
        if not self.model or not self.tokenizer:
            self.load_model()
        
        summarized_sentences = []
        
        for i, sentence in enumerate(sentences):
            try:
                # 문장이 너무 짧으면 요약하지 않음
                if len(sentence.split()) < 10:
                    summarized_sentences.append(sentence)
                    continue
                
                summary = self.summarize_text(sentence, max_length, min_length)
                summarized_sentences.append(summary)
                
                logger.info(f"Summarized sentence {i+1}/{len(sentences)}: {sentence[:100]}... -> {summary}")
                
            except Exception as e:
                logger.error(f"Error summarizing sentence {i+1}: {str(e)}")
                summarized_sentences.append(sentence)  # 실패시 원본 문장 사용
        
        return summarized_sentences 