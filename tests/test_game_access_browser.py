"""Keyboard access to the existing games and shared focus styles in Chromium.

The tests serve only the local web resource with its published CSP. They do not
claim usability findings from learners or assistive-technology participants.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CSP = next(
    line.split(":", 1)[1].strip()
    for line in (ROOT / "_headers").read_text().splitlines()
    if line.strip().startswith("Content-Security-Policy:")
)
GAMES = (
    ("nombres-islas", "names", "name", "namesNameSelect"),
    ("piezas-islas", "pieces", "piece", "piecesPieceSelect"),
)


class QuietCspHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()


class GameAccessBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietCspHandler, directory=str(ROOT))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=shutil.which("chromium"),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 390, "height": 900})
        self.context.route(
            "**/*",
            lambda route: route.continue_()
            if urlsplit(route.request.url).hostname in ("127.0.0.1", None)
            else route.abort(),
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(10000)
        self.page.set_default_navigation_timeout(30000)
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open_game(self, route, prefix):
        self.page.goto(self.base + "#" + route, wait_until="networkidle")
        expect(self.page.locator(f"#{prefix}MapGame")).to_be_visible()
        return self.page.locator(f"#{prefix}WithoutDrag")

    def test_keyboard_entry_precedes_cards_and_map_at_narrow_and_large_text_sizes(self):
        # Removing the shortcut, placing it after the board, or dropping its
        # focus transfer makes the alternative undiscoverable by this route.
        for route, prefix, _, select_id in GAMES:
            for width, scale in ((320, 1), (390, 1), (320, 2), (1280, 1)):
                with self.subTest(route=route, width=width, scale=scale):
                    self.page.set_viewport_size({"width": width, "height": 900})
                    access = self.open_game(route, prefix)
                    self.page.evaluate("scale=>document.documentElement.style.fontSize=`${scale * 100}%`", scale)
                    expect(access).to_have_accessible_name("Sin arrastrar", timeout=1000)
                    expect(access).to_have_attribute("aria-expanded", "false")
                    for suffix in ("CardBank", "MapViewport"):
                        self.assertTrue(access.evaluate("(node,id)=>Boolean(node.compareDocumentPosition(document.getElementById(id)) & Node.DOCUMENT_POSITION_FOLLOWING)", prefix + suffix))
                    bounds = access.bounding_box()
                    self.assertGreaterEqual(bounds["height"], 44)
                    access.focus()
                    access.press("Enter")
                    select = self.page.locator("#" + select_id)
                    expect(select).to_be_focused()
                    expect(access).to_have_attribute("aria-expanded", "true")
                    disclosure = select.locator("xpath=ancestor::details[1]")
                    expect(disclosure).to_have_attribute("id", access.get_attribute("aria-controls"))
                    self.assertEqual(self.page.locator("#" + select_id).count(), 1)
                    for control in (access, select, self.page.locator(f"#{prefix}IslandSelect"), self.page.locator(f"#{prefix}PlaceButton")):
                        box = control.bounding_box()
                        self.assertGreaterEqual(box["x"], -1)
                        self.assertLessEqual(box["x"] + box["width"], width + 1)
                    self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), width + 1)
                    summary = disclosure.locator(":scope > summary")
                    summary.focus()
                    summary.press("Enter")
                    expect(access).to_have_attribute("aria-expanded", "false")

    def test_keyboard_placement_shares_state_with_cards_and_reference(self):
        # Separate placement state, a focus trap or rewards added by this mode
        # would break this uninterrupted keyboard placement and return trip.
        for route, prefix, item, select_id in GAMES:
            with self.subTest(route=route):
                access = self.open_game(route, prefix)
                storage = self.page.evaluate("()=>({...localStorage})")
                access.focus()
                access.press("Space")
                select = self.page.locator("#" + select_id)
                expect(select).to_be_focused()
                select.press("Home")
                select.press("ArrowDown")
                self.page.keyboard.press("Tab")
                island_select = self.page.locator(f"#{prefix}IslandSelect")
                expect(island_select).to_be_focused()
                island_select.press("Home")
                island_select.press("ArrowDown")
                self.page.keyboard.press("Tab")
                place = self.page.locator(f"#{prefix}PlaceButton")
                expect(place).to_be_focused()
                place.press("Enter")
                expect(self.page.locator(f'[data-{item}-island="el-hierro"]')).to_have_attribute("data-placed", "true")
                expect(place).to_be_focused()
                self.page.locator(f'[data-{item}-card="tenerife"]').focus()
                self.page.keyboard.press("Space")
                access.focus()
                access.press("Enter")
                expect(select).to_have_value("tenerife")
                self.page.locator(f'[data-{item}-island="tenerife"]').focus()
                self.page.keyboard.press("Enter")
                expect(self.page.locator(f"#{prefix}Progress")).to_contain_text("2 de 8")
                select.focus()
                select.press("Home")
                select.press("ArrowDown")
                expect(select).to_have_value("la-palma")
                reference = self.page.locator(f"#{prefix}Reference")
                reference.click()
                access.focus()
                access.press("Enter")
                expect(select).to_be_disabled()
                expect(select.locator("xpath=ancestor::details[1]").locator(":scope > summary")).to_be_focused()
                reference.click()
                expect(select).to_be_enabled()
                self.assertEqual(self.page.locator(f'[data-{item}-island][data-placed="true"]').count(), 2)
                self.assertEqual(self.page.locator("#passportCount").text_content(), "0/8")
                self.assertEqual(self.page.evaluate("()=>({...localStorage})"), storage)

    def test_piece_descriptions_and_empty_placed_states_remain_accessible_without_captions(self):
        # Hiding or dropping the state from the accessible name would make
        # visually identical piece buttons ambiguous to a screen reader.
        self.open_game("piezas-islas", "pieces")
        card = self.page.locator('[data-piece-card="el-hierro"]')
        target = self.page.locator('[data-piece-island="el-hierro"]')
        expect(card).to_have_accessible_name(re.compile(r"Vasija redondeada.*Sin colocar"))
        expect(target).to_have_accessible_name(re.compile(r"El Hierro.*Vacía"))
        card.focus()
        card.press("Space")
        target.focus()
        target.press("Enter")
        expect(card).to_have_accessible_name(re.compile(r"Vasija redondeada.*Colocada.*El Hierro"))
        expect(target).to_have_accessible_name(re.compile(r"El Hierro.*Vasija redondeada.*colocada", re.IGNORECASE))
        for span in card.locator(".pieces-card-name,.pieces-card-state").all():
            bounds = span.bounding_box()
            self.assertLessEqual(bounds["width"], 1)
            self.assertLessEqual(bounds["height"], 1)
        expect(card.locator("img")).to_be_visible()

    def test_names_category_keeps_its_documentary_caution_in_the_accessible_name(self):
        self.open_game("nombres-islas", "names")
        expect(self.page.locator('[data-name-card="la-graciosa"]')).to_have_accessible_name(
            re.compile(r"Sin nombre documentado.*Categoría, no un nombre antiguo")
        )

    def test_alternative_feedback_stays_with_controls_and_shares_the_maps_placement_state(self):
        # Returning the only feedback below the board would hide an incomplete,
        # wrong or successful answer from the learner using this narrow form.
        self.page.set_viewport_size({"width": 320, "height": 800})
        for route, prefix, item, select_id in GAMES:
            with self.subTest(route=route):
                access = self.open_game(route, prefix)
                self.page.evaluate("document.documentElement.style.fontSize='100%'")
                access.focus()
                access.press("Enter")
                select = self.page.locator("#" + select_id)
                island_select = self.page.locator(f"#{prefix}IslandSelect")
                place = self.page.locator(f"#{prefix}PlaceButton")
                source = self.page.locator(f"#{prefix}Feedback")
                feedback = self.page.locator(f"#{prefix}AlternativeFeedback")

                def assert_contextual_response(kind):
                    frames = self.page.evaluate("""async prefix=>{
                        const frames=[];
                        const box=node=>{
                            const r=node.getBoundingClientRect();
                            return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};
                        };
                        for(let i=0;i<8;i++){
                            await new Promise(requestAnimationFrame);
                            frames.push({
                                message:box(document.getElementById(prefix+'AlternativeFeedback')),
                                button:box(document.getElementById(prefix+'PlaceButton')),
                                active:document.activeElement.id,scrollY,scrollX,
                                covered:Math.max(0,...[...document.querySelectorAll('.topbar,.main-navigation')]
                                    .filter(node=>['sticky','fixed'].includes(getComputedStyle(node).position))
                                    .map(node=>node.getBoundingClientRect().bottom)),
                                height:innerHeight,width:innerWidth
                            });
                        }
                        return frames;
                    }""", prefix)
                    if os.environ.get("MITOMAPA_GAME_FRAMES"):
                        print("response-frames", prefix, kind, json.dumps(frames))
                    for frame in frames[-3:]:
                        self.assertEqual(frame["active"], prefix + "PlaceButton", frames)
                        for key in ("button", "message"):
                            self.assertGreaterEqual(frame[key]["top"], frame["covered"] - 1, frames)
                            self.assertLessEqual(frame[key]["bottom"], frame["height"] + 1, frames)
                            self.assertGreaterEqual(frame[key]["left"], -1, frames)
                            self.assertLessEqual(frame[key]["right"], frame["width"] + 1, frames)
                    expect(feedback).to_be_visible()
                    # Chromium can report 0.99957 for a fully scrolled element
                    # due to subpixel rounding. Exact geometry below still
                    # rejects any meaningful clipping or header occlusion.
                    expect(feedback).to_be_in_viewport(ratio=.99)
                    expect(place).to_be_in_viewport(ratio=.99)
                    expect(source).to_have_attribute("data-kind", kind)
                    expect(feedback).to_have_text(source.text_content())
                    for control in (select, island_select):
                        self.assertIn(feedback.get_attribute("id"), (control.get_attribute("aria-describedby") or "").split())
                    self.assertIsNone(feedback.get_attribute("aria-live"))
                    self.assertIsNone(feedback.get_attribute("role"))
                    self.assertEqual(self.page.locator(f"#{prefix}MapGame").locator('[role="status"],[aria-live]:not([aria-live="off"])').count(), 1)
                    bounds = feedback.bounding_box()
                    button_bounds = place.bounding_box()
                    for box in (bounds,button_bounds):
                        self.assertGreaterEqual(box["x"], -1)
                        self.assertLessEqual(box["x"] + box["width"], 321)
                    covered = self.page.evaluate("()=>Math.max(0,...[...document.querySelectorAll('.topbar,.main-navigation')].filter(node=>['sticky','fixed'].includes(getComputedStyle(node).position)).map(node=>node.getBoundingClientRect().bottom))")
                    self.assertGreaterEqual(bounds["y"], covered - 1)
                    self.assertLessEqual(bounds["y"] + bounds["height"], 801)
                    self.assertGreaterEqual(button_bounds["y"], covered - 1)
                    self.assertLessEqual(button_bounds["y"] + button_bounds["height"], 801)
                    self.assertLessEqual(bounds["y"] - (button_bounds["y"] + button_bounds["height"]), 40)
                    expect(place).to_be_focused()

                place.focus()
                place.press("Enter")
                assert_contextual_response("note")
                expect(feedback).to_contain_text("Elige")
                select.select_option("tenerife")
                island_select.select_option("el-hierro")
                place.focus()
                place.press("Enter")
                assert_contextual_response("retry")
                self.assertEqual(self.page.locator(f'[data-{item}-island][data-placed="true"]').count(), 0)
                island_select.select_option("tenerife")
                place.focus()
                place.press("Enter")
                assert_contextual_response("success")
                # Text enlargement can finish changing the form and sticky
                # header after the placement event has already returned.
                self.page.evaluate("document.documentElement.style.fontSize='125%'")
                assert_contextual_response("success")
                self.page.evaluate("document.documentElement.style.fontSize='100%'")
                assert_contextual_response("success")
                expect(self.page.locator(f'[data-{item}-card="tenerife"]')).to_have_attribute("data-placed", "true")
                expect(self.page.locator(f'[data-{item}-island="tenerife"]')).to_have_attribute("data-placed", "true")
                self.page.locator(f'[data-{item}-card="la-palma"]').focus()
                self.page.keyboard.press("Space")
                self.page.locator(f'[data-{item}-island="la-palma"]').focus()
                self.page.keyboard.press("Enter")
                access.focus()
                access.press("Enter")
                expect(feedback).to_have_text(source.text_content())
                expect(feedback).to_contain_text("La Palma")
                expect(self.page.locator(f"#{prefix}Progress")).to_contain_text("2 de 8")

    def test_escape_cancels_drag_and_keeps_origin_focus_then_alternative_works(self):
        for route, prefix, item, select_id in GAMES:
            with self.subTest(route=route):
                self.page.set_viewport_size({"width": 1280, "height": 900})
                access = self.open_game(route, prefix)
                card = self.page.locator(f'[data-{item}-card="tenerife"]')
                card.focus()
                box = card.bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                self.page.mouse.move(x, y)
                self.page.mouse.down()
                self.page.mouse.move(x + 25, y + 25, steps=3)
                expect(self.page.locator(f".{prefix}-drag-ghost")).to_be_visible()
                self.page.keyboard.press("Escape")
                self.page.mouse.up()
                expect(self.page.locator(f".{prefix}-drag-ghost")).to_have_count(0)
                expect(card).to_be_focused()
                expect(card).to_have_attribute("aria-pressed", "false")
                access.focus()
                access.press("Enter")
                expect(self.page.locator("#" + select_id)).to_be_focused()
                self.assertEqual(self.page.locator(f'[data-{item}-island][data-placed="true"]').count(), 0)

    def test_header_focus_has_two_contrast_rings_and_honours_user_display_preferences(self):
        self.page.goto(self.base, wait_until="networkidle")
        self.page.keyboard.press("Tab")
        for selector in (".topbar .brand", "#openTeacher", "#openPassport"):
            control = self.page.locator(selector)
            control.focus()
            ring = control.evaluate("node=>{const s=getComputedStyle(node);return {style:s.outlineStyle,width:s.outlineWidth,color:s.outlineColor,shadow:s.boxShadow}}")
            self.assertEqual(ring["style"], "solid")
            self.assertGreaterEqual(float(ring["width"].removesuffix("px")), 3)
            self.assertEqual(ring["color"], "rgb(255, 255, 255)")
            self.assertIn("rgb(24, 36, 44)", ring["shadow"])
        self.page.emulate_media(reduced_motion="reduce")
        self.assertEqual(self.page.locator("html").evaluate("node=>getComputedStyle(node).scrollBehavior"), "auto")
        self.page.emulate_media(forced_colors="active")
        for selector in (".topbar .brand", "#openTeacher", "#openPassport"):
            control = self.page.locator(selector)
            control.focus()
            self.assertEqual(control.evaluate("node=>getComputedStyle(node).outlineStyle"), "solid")
            self.assertEqual(control.evaluate("node=>getComputedStyle(node).forcedColorAdjust"), "auto")


if __name__ == "__main__":
    unittest.main()
