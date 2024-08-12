import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter  # 避免重复命名
from nonebot.adapters.feishu import Adapter as FeishuAdapter
from nonebot.adapters.telegram import Adapter as TelegramAdapter

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(FeishuAdapter)
driver.register_adapter(TelegramAdapter)


# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_plugins("nonebot_bridge/plugins")  # 本地插件

app = nonebot.get_app()

if __name__ == "__main__":
    # 本地调试
    driver.register_adapter(ConsoleAdapter)
    nonebot.run()