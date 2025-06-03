from language_tool_python import LanguageTool

def check_test(text):
    # 创建语言工具对象
    tool = LanguageTool('en-US')
    # 检查文本
    matches = tool.check(text)

    # 输出错误信息
    for match in matches:
        err_txt = text[match.offset : match.offset + match.errorLength]
        print(f"{match.context} 错误: {match.ruleId}, 位置: {match.offset}:{match.offset + match.errorLength}: {err_txt}, 建议: {match.replacements}")

    # 修正文本
    corrected_text = tool.correct(text)
    print("修正后的文本:", corrected_text)

if __name__=="__main__":
    # 待检查的文本
    text = "This are incorrect sentence."
    text = "Hello, I is a good man, you know..."
    # text = "You is good boy"

    check_test(text)

# export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
# echo 'export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"' >> /Users/ron/.zshrc
# export CPPFLAGS="-I/opt/homebrew/opt/openjdk/include"