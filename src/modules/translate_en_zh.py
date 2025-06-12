import asyncio
from googletrans import Translator
from translate import Translator as OfflineTranslator

async def translate4google(
    english_text: str,
    timeout: int = 5
):
    """
    使用Google翻译API翻译英文文本为中文
    
    参数:
        english_text: 要翻译的英文文本
        timeout: Google翻译API的超时时间（秒）
    
    返回:
        str: Google翻译的结果
    """
    try:
        translator = Translator(timeout=timeout)
        result = await translator.translate(english_text, src='en', dest='zh-cn')
        return result.text
    except Exception as e:
        return None


def offline_translate(english_text: str) -> str:
    try:
        offline_translator = OfflineTranslator(from_lang="en", to_lang="zh")
        return offline_translator.translate(english_text)
    except Exception as e:
        return f"离线翻译失败: {str(e)}"

# 使用示例
if __name__ == "__main__":
    text_to_translate = "Hello, how are you today?"
    
    # 测试独立的Google翻译函数
    print("Google翻译:")
    google_trans = asyncio.run(translate4google(text_to_translate, 1))
    print(google_trans)
    
    # 测试独立的离线翻译函数
    print("离线翻译:",)
    offline_trans = offline_translate(text_to_translate)
    print(offline_trans)