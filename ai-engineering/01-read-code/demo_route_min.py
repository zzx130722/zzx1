"""迷你实验：不用 Flask，亲手复刻 @app.route 的原理。

用法（在 dev-basics 目录下）：
    .venv\\Scripts\\python.exe -X utf8 ai-engineering/01-read-code/demo_route_min.py

只有 20 行有效代码。跑完你就明白 @app.route 一点都不神秘。
"""

# 第 1 步：先准备一个"登记本"，假装它是 Flask 内部的路由表
route_table = {}


# 第 2 步：亲手写一个"最简版 route"。
# 注意它的用法一定是 @route("/") 带括号 —— 括号里是网址，网址是参数。
def route(url):
    print(f"[第1步] 有人调用了 route('{url}')，我先造一个装饰器出来")

    def decorator(func):
        # func 就是写在 @下面的那个函数
        print(f"[第2步] 装饰器拿到函数 {func.__name__}，登记：'{url}' -> {func.__name__}")
        route_table[url] = func  # 登记到本子上（Flask 里这一步叫 add_url_rule）
        return func              # 把函数原样还回去，什么都不改

    print(f"[第1步] route('{url}') 结束，返回了 decorator")
    return decorator


# 第 3 步：使用它。这两行代码的真实执行顺序，看运行输出就懂了。
@route("/home")
def hello():
    return "你好！"


print()
print("=" * 40)
print("登记本里现在有什么：", route_table)
print("hello 被改动了吗？没有，照样能调：", hello())
print("假装用户访问了 /home，查登记本，调函数：", route_table["/home"]())
