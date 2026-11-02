"""Use the official browser's AAC decoder for real-media regression checks."""
import json


def launch_media_browser(playwright):
    browser = playwright.chromium.launch(
        channel="chrome", headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    try:
        context = browser.new_context()
        try:
            page = context.new_page()
            codecs = page.evaluate("""() => {
              const audio = new Audio();
              return {
                mp3: audio.canPlayType('audio/mpeg'),
                aac: audio.canPlayType('audio/mp4; codecs="mp4a.40.2"')
              };
            }""")
        finally:
            context.close()
        if not codecs.get("mp3") or not codecs.get("aac"):
            raise RuntimeError(
                "Media browser preflight failed: official Chrome must support "
                "the real MP3 and AAC/M4A recordings. Capabilities: " + json.dumps(codecs)
            )
        print("Media browser preflight: Chrome " + browser.version + " " + json.dumps(codecs), flush=True)
        return browser
    except BaseException:
        browser.close()
        raise
