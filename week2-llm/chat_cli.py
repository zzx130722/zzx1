"""命令行聊天：多轮 + system 角色 + while True 循环（周五 + 周末的任务）。

「它记得上一句」不是服务器有记忆，而是我们把整段历史重新发回去。
看 main() 里两行 append 注释就懂了。

跑法（在 dev-basics 目录下）：
    .venv\\Scripts\\python.exe -X utf8 week2-llm\\chat_cli.py
"""
from client import chat

# system 只需要出现一次，放最前面，后面每轮都原样带着它
SYSTEM_PROMPT = "你是一个耐心的编程助教，回答保持简短，用中文。"


def main() -> None:
    print("多轮聊天（输入 q 退出）")
    # messages 就是这局对话的全部记忆，程序退出就没了——想持久化是以后的事
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_text = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break  # Ctrl+C / Ctrl+Z 也算正常退出
        if not user_text:
            continue
        if user_text.lower() in {"q", "quit", "exit"}:
            break

        messages.append({"role": "user", "content": user_text})
        try:
            reply = chat(messages)
        except (RuntimeError, ValueError) as e:
            print(f"[出错了] {e}")
            messages.pop()  # 这轮失败了，别把发不出去的话留在历史里
            continue

        print(f"AI: {reply}")
        # 关键一行：把模型的回答也放回历史。
        # 不放的话，下一轮它就「忘了」自己刚说过什么——模型没有记忆，
        # 所谓记忆就是这个列表越来越长
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
