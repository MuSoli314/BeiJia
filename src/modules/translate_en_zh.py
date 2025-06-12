# from googletrans import Translator
# from translate import Translator as OfflineTranslator
# from typing import Tuple

# def dual_translate_english_to_chinese(
#     english_text: str,
#     google_timeout: int = 5
# ) -> Tuple[str, str]:
#     """
#     同时使用Google翻译API和离线翻译库翻译英文文本为中文
    
#     参数:
#         english_text: 要翻译的英文文本
#         google_timeout: Google翻译API的超时时间（秒）
    
#     返回:
#         Tuple[google_translation, offline_translation]
#         其中：
#         - google_translation: Google翻译的结果
#         - offline_translation: 离线翻译的结果
#     """
#     # Google翻译（在线）
#     google_result = None
#     try:
#         translator = Translator(timeout=google_timeout)
#         google_result = translator.translate(english_text, src='en', dest='zh-cn').text
#     except Exception as e:
#         google_result = f"Google翻译失败: {str(e)}"
    
#     # 离线翻译
#     offline_result = None
#     try:
#         offline_translator = OfflineTranslator(from_lang="en", to_lang="zh")
#         offline_result = offline_translator.translate(english_text)
#     except Exception as e:
#         offline_result = f"离线翻译失败: {str(e)}"
    
#     return google_result, offline_result


# # 使用示例
# if __name__ == "__main__":
#     text_to_translate = "Hello, how are you today?"
#     google_trans, offline_trans = dual_translate_english_to_chinese(text_to_translate)
    
#     print("原始英文:", text_to_translate)
#     print("Google翻译:", google_trans)    # 输出示例: "你好，你今天好吗？"
#     print("离线翻译:", offline_trans)    # 输出示例: "你好，你今天好吗？"