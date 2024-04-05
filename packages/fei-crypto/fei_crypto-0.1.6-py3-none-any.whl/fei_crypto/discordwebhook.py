import os

from discord_webhook import DiscordWebhook, DiscordEmbed


def send(webhook_url: str, text: str = "", file_paths: str = "", proxy: str = None) -> None:
    proxies = None
    if proxy is not None:
        proxies = {
            "http": proxy,
            "https": proxy,
        }

    webhook = DiscordWebhook(url=webhook_url, content=text, proxies=proxies)
    for fi_path in str.split(file_paths, ",", -1):
        fi_path = str.strip(fi_path)
        if fi_path == "":
            continue
        with open(fi_path, "rb") as f:
            webhook.add_file(file=f.read(), filename=os.path.basename(fi_path))

    print(webhook.execute())


if __name__ == "__main__":
    send(
        "",
        "交易方向:平多🚀\n平仓均价:0.8605197740112994\n已实现收益率:📉-35.74%\n识别ID:2DEB3930217A4ECAB35A3BDBDB14D96B\n"
        "触发时间:2024-03-29 15:09:45\n\n⬆️   🔴🟠🟤🟣🔵🟢🟡   ⬆️",
        "e:/github/feicrypto/fei-crypto-python/media/videos/360p15/btc.mp4,"
        "e:/github/feicrypto/fei-crypto-python/media/videos/360p15/people.mp4,"
        "e:/github/feicrypto/fei-crypto-python/media/videos/360p15/pepe.mp4",
    )
