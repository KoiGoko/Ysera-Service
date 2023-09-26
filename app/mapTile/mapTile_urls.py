class TileConfig:
    def __init__(self):
        self.tile_url = "https://example.com/tiles/{z}/{x}/{y}.png"  # 默认瓦片URL

    def load_from_env(self, env):
        # 从环境变量加载配置
        self.tile_url = env.str("TILE_URL", default=self.tile_url)


config = TileConfig()
