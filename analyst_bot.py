from transformers import pipeline

class SecurityAnalyst:
    def __init__(self):
        print("Loading SIYAJ Intelligent Analyst (DistilGPT2)...")
        # أضفنا جهاز التشغيل (device) للتأكد من السرعة
        self.generator = pipeline('text-generation', model='distilgpt2')

    def explain_attack(self, attack_type, confidence_score):
        # حسنّا الـ Prompt عشان يجبر الموديل يعطينا حلول تقنية (Mitigation)
        prompt = (f"System Alert: {attack_type} attack detected with {confidence_score}% confidence. "
                  f"As a security expert, the technical explanation and mitigation steps are:")
        
        # أضفنا باراميترات لتحسين جودة النص المولّد
        result = self.generator(
            prompt, 
            max_new_tokens=60,    # نخليه يكتب كلام جديد أكثر
            num_return_sequences=1, 
            temperature=0.7,      # يخليه أكثر إبداعاً ودقة في الشرح
            truncation=True,
            pad_token_id=50256    # ضروري لتجنب التحذيرات في الماك
        )
        
        return result[0]['generated_text']

if __name__ == "__main__":
    analyst = SecurityAnalyst()
    # تجربة هجوم حقيقي
    report = analyst.explain_attack("DoS (Denial of Service)", 98.5)
    print("\n" + "="*30)
    print("🛡️ SIYAJ AI ANALYST REPORT")
    print("="*30)
    print(report)

