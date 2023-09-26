@app.get("/get_tile")
async def get_tile():
    tile_url = config.tile_url
    # 使用 tile_url 进行操作
    return {"tile_url": tile_url}
