"""Exercise the task-owned official shell with synthetic data, never real keys."""
import argparse
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

APP = Path(__file__).resolve().parents[1]


class UI:
    def __init__(self, port, profile):
        self.base = f"http://127.0.0.1:{port}/"
        self.profile = profile
        self.checks = []

    def get(self, route, **params):
        with urllib.request.urlopen(self.base + route + "?" + urllib.parse.urlencode(params), timeout=15) as response:
            return json.loads(response.read())

    def snap(self):
        return [w for w in self.get("snap")["s"] if w["ty"] not in ("Splash", "Window", "KeyboardView")]

    def click(self, text=None, name=None, index=0):
        for _ in range(9):
            candidates = [w for w in self.snap() if (w.get("t") == text if text else w.get("i") == name)
                          and w.get("enabled", True) and w["r"][2] > 0 and w["r"][3] > 0]
            if len(candidates) <= index:
                card = next(w for w in self.get("snap")["s"] if w.get("i") == "card" and w["ty"] == "Splash")
                left, top, cw, ch = card["r"]
                self.get("m", k="scroll", x=left + cw * 0.6, y=top + ch * 0.6, dy=240, wait=1)
                continue
            widget = candidates[index]
            x, y, width, height = widget["r"]
            card = next(w for w in self.get("snap")["s"] if w.get("i") == "card" and w["ty"] == "Splash")
            left, top, cw, ch = card["r"]
            if top <= y + height / 2 < top + ch:
                self.get("click", x=x + width / 2, y=y + height / 2, wait=1)
                time.sleep(0.15)
                return
            self.get("m", k="scroll", x=left + cw * 0.6, y=top + ch * 0.6, dy=240, wait=1)
        raise AssertionError(f"cannot reach {text or name}")

    def fill(self, text, index=0, name=None):
        inputs = [w for w in self.snap() if w["ty"] == "TextInput" and w["r"][2] > 0]
        field = next(w for w in inputs if w.get("i") == name) if name else inputs[index]
        x, y, width, height = field["r"]
        self.get("click", x=x + width / 2, y=y + height / 2, wait=1)
        self.get("k", k="down", c="KeyA", ctrl=1, wait=1)
        self.get("k", k="up", c="KeyA", ctrl=1, wait=1)
        self.get("t", t=text, wait=1)

    def state_path(self):
        files = list((self.profile / "apps/pantry-steward").rglob("pantry.json"))
        assert len(files) == 1, files
        return files[0]

    def state(self):
        return json.loads(self.state_path().read_text(encoding="utf-8"))

    def check(self, name, condition):
        if not condition:
            self.shot("failure.png")
            raise AssertionError(name)
        print("PASS " + name, flush=True)
        self.checks.append(name)

    def shot(self, name):
        path = self.profile / name
        with urllib.request.urlopen(self.base + "g?raw=1", timeout=15) as response:
            data = response.read()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        path.write_bytes(data)

    def text(self):
        return "\n".join(w.get("t", "") for w in self.snap())


def exercise(ui):
    ui.check("官方宿主显示首次建档", "首次建档" in ui.text())
    if "首次建档  1 / 3" in ui.text():
        ui.click("选择", index=1)
    for index, text in enumerate(("30", "170", "65", "清淡", "无")):
        ui.fill(text, index)
    ui.click("下一步 · 建立冰箱档案  →")
    ui.check("档案保存并进入入库页", ui.state()["profile"]["scene"] == "日常健康")
    ui.fill("豆腐", name="food_name")
    ui.fill("abc", name="food_grams")
    ui.fill("2", name="food_days")
    ui.click("预览并确认入库  →")
    ui.check("非法数量不写库存", not ui.state()["foods"])
    ui.fill("250", name="food_grams")
    ui.click("预览并确认入库  →")
    ui.check("预览不写库存", not ui.state()["foods"])
    ui.click("确认入库")
    ui.check("确认才写库存", ui.state()["foods"][0]["grams"] == 250)
    ui.click("完成建档 · 开始托管  →")
    ui.check("首页完整显示", "今天想吃点什么？" in ui.text() and ui.state()["profile"]["done"])
    ui.click(name="voice_button")
    ui.check("麦克风明确说明不支持，不启动录音", "语音识别服务" in ui.text())
    ui.click("⚙  设置")
    ui.check("预算不冒充模型已配置", "宿主服务可用" in ui.text() and "在线 AI 已配置" not in ui.text())
    ui.click("改用本地规则")
    ui.check("本地规则开关持久化", ui.state()["model_enabled"] is False)
    ui.click("载入演示数据…")
    before = ui.state_path().read_bytes()
    ui.check("演示替换需要确认", "确认替换并开始演示" in ui.text())
    ui.click("确认替换并开始演示")
    ui.check("演示库存建立且正式菜单保留", ui.state()["active"] == 5 and len(ui.state()["foods"]) == 4)
    ui.shot("01-main.png")
    ui.click("⚙  设置")
    ui.click("时间 +12 小时")
    ui.check("临期推进生成候选，不自动替换菜单", len(ui.state()["plans"]) >= 2 and ui.state()["active"] == 5)
    ui.click("✦  方案")
    ui.shot("02-plan.png")
    ui.click("就吃这套 · 设为今晚方案  →")
    ui.check("用户接受候选成为正式菜单", ui.state()["active"] != 5)
    ui.click("我吃完了 · 核对实际用量")
    before = ui.state_path().read_bytes()
    ui.fill("999999", 0)
    ui.click(name="confirm_consumption")
    ui.check("超库存扣减被拒绝", ui.state_path().read_bytes() == before and "不能超出库存" in ui.text())
    ui.click("取消")
    ui.check("取消不改库存", ui.state_path().read_bytes() == before)
    ui.click("我吃完了 · 核对实际用量")
    ui.shot("03-confirm.png")
    prior = sum(f["grams"] for f in ui.state()["foods"])
    ui.click(name="confirm_consumption")
    ui.check("确认扣减并记录用餐", sum(f["grams"] for f in ui.state()["foods"]) < prior and ui.state()["meal_count"] == 2)
    ui.click("▣  冰箱")
    ui.shot("04-updated.png")
    ui.click("⚙  设置")
    ui.click("重新设置用户画像")
    ui.check("可返回资料页且库存保留", "首次建档" in ui.text() and len(ui.state()["foods"]) == 4)
    (ui.profile / "expected-state.json").write_text(json.dumps(ui.state(), ensure_ascii=False), encoding="utf-8")
    (ui.profile / "checks.json").write_text(json.dumps(ui.checks, ensure_ascii=False), encoding="utf-8")
    ui.shot("return-profile.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18442)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()
    ui = UI(args.port, args.profile.resolve())
    if args.restart:
        expected = json.loads((ui.profile / "expected-state.json").read_text(encoding="utf-8"))
        ui.check("重启保留档案、库存、菜单与选项", ui.state() == expected)
    else:
        exercise(ui)


if __name__ == "__main__":
    main()
