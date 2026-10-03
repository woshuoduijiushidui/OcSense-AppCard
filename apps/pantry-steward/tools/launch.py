"""Run Pantry Steward on unmodified official OctoSense, with isolated test data.

Only the existing pinned App Hub sources are copied into target for CLI builds.
No model/voice services are injected. Keys are outside the repository and are
generated only with --prepare-local-test (explicit human consent).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[1]
BUILD = ROOT / "target" / "pantry-official-tools"
STATE = APP / ".local-state"
EXE = ".exe" if os.name == "nt" else ""


def run(command, capture=False, **kwargs):
    result = subprocess.run([str(x) for x in command], check=True, text=True,
                            encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE if capture else None, **kwargs)
    return result.stdout.strip() if capture else None


def hub_source():
    spec = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))
    revision = spec["workspace"]["dependencies"]["octosense-app-hub-app"]["rev"]
    cargo_home = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo"))
    matches = list((cargo_home / "git/checkouts").glob(f"octosense-app-hub-*/*/Cargo.toml"))
    for manifest in matches:
        source = manifest.parent
        head = run(["git", "-c", f"safe.directory={source.as_posix()}", "-C", source,
                    "rev-parse", "HEAD"], capture=True)
        if head == revision:
            return source, revision
    raise RuntimeError("未找到官方固定版本的 App Hub。请先在官方仓库运行 cargo fetch --locked。")


def prepare_tools(offline=False):
    source, revision = hub_source()
    workspace = BUILD / "hub"
    marker = BUILD / "source.json"
    fingerprint = {"revision": revision,
                   "installer": hashlib.sha256((APP / "tools/install_local.rs").read_bytes()).hexdigest(),
                   "runtime": hashlib.sha256(b"".join((ROOT / name).read_bytes() for name in
                       ("native-runtime.lock.json", "runtime-patches.lock.json"))).hexdigest(),
                   "root": str(ROOT)}
    ready = marker.exists() and json.loads(marker.read_text(encoding="utf-8")) == fingerprint
    if not ready:
        workspace.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source / "crates", workspace / "crates", dirs_exist_ok=True)
        manifest = (source / "Cargo.toml").read_text(encoding="utf-8")
        for name in ("makepad", "octoscript", "octoscript-makepad"):
            dependency = ROOT / ".sources" / name
            if not dependency.is_dir():
                raise RuntimeError("官方依赖未准备，请先运行 python -X utf8 tools/setup.py --hub <已有依赖目录>。")
            manifest = manifest.replace(f'path = "../{name}/', f'path = "{dependency.as_posix()}/')
        (workspace / "Cargo.toml").write_text(manifest, encoding="utf-8")
        if (source / "Cargo.lock").exists():
            shutil.copy2(source / "Cargo.lock", workspace / "Cargo.lock")
        shutil.copy2(APP / "tools/install_local.rs", workspace / "crates/app-hub/src/bin/pantry-local-install.rs")
    target = ROOT / "target"
    hub = target / "release" / ("hub" + EXE)
    host = target / "release" / ("card-host" + EXE)
    installer = target / "release" / ("pantry-local-install" + EXE)
    if not ready or not all(p.is_file() for p in (hub, host, installer)):
        command = ["cargo", "build", "--release", "--manifest-path", workspace / "Cargo.toml",
                   "--target-dir", target, "-p", "octosense-card-host", "-p", "octosense-app-hub",
                   "--bin", "card-host", "--bin", "hub", "--bin", "pantry-local-install"]
        if offline:
            command.append("--offline")
        run(command, cwd=ROOT)
        marker.write_text(json.dumps(fingerprint), encoding="utf-8")
    return hub, host, installer


def key_dir():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share"))
    return base / "OctoSense" / "pantry-steward-local-test-keys"


def local_install(hub, installer, allow_keygen, profile=STATE):
    keys = key_dir()
    files = [keys / f"{name}.key" for name in ("anchor", "working", "publisher")]
    if not all(path.is_file() for path in files):
        if not allow_keygen:
            raise RuntimeError("本机测试密钥尚未准备。得到本人许可后运行 run.cmd --prepare-local-test。")
        keys.mkdir(parents=True, exist_ok=True)
        for path in files:
            if not path.exists():
                run([hub, "keygen", path], capture=True)
    anchor, working, publisher = files
    anchor_public = run([hub, "pubkey", anchor], capture=True)
    publisher_public = run([hub, "pubkey", publisher], capture=True)
    # The bundle digest excludes manifest.json. Manifest-only changes (such as
    # storage grants or version) must still produce a new local signed snapshot.
    manifest_bytes = (APP / "bundle/manifest.json").read_bytes()
    digest = json.loads(manifest_bytes)["integrity"]["bundle_blake3"]
    snapshot_id = hashlib.sha256(manifest_bytes + digest.encode("ascii")).hexdigest()
    mirror = profile / "mirrors" / snapshot_id
    catalog = mirror / "catalog.json"
    if not catalog.exists():
        snapshot = mirror / "source/bundle"
        shutil.copytree(APP / "bundle", snapshot, dirs_exist_ok=True)
        run([hub, "sign-manifest", snapshot, "--key", publisher, "--key-id", "pantry-local-test"])
        certificate = run([hub, "certify", "--anchor", anchor, "--working", working], capture=True)
        run([hub, "publish", snapshot, "--catalog", catalog, "--key", working,
             "--anchor-cert", certificate, "--publisher", "pantry-local-test",
             "--publisher-key", f"pantry-local-test={publisher_public}", "--out", mirror])
    run([hub, "verify", catalog, "--anchor", anchor_public])
    data = profile / "apps"
    run([installer, mirror, data, anchor_public, publisher_public])
    return mirror, data, anchor_public


def main():
    parser = argparse.ArgumentParser(description="冰箱管家：官方 OctoSense 本地测试")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--prepare-local-test", action="store_true", help="本人许可后生成本地测试密钥并安装")
    parser.add_argument("--standalone", action="store_true", help="官方 card-host；无模型服务")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--hidden", action="store_true")
    parser.add_argument("--remote", type=int)
    parser.add_argument("--size", default="1200x800")
    parser.add_argument("--app-data", type=Path)
    parser.add_argument("--no-ai", action="store_true", help="兼容旧测试命令；单独 card-host 不提供 AI")
    args = parser.parse_args()
    hub, host, installer = prepare_tools(args.offline)
    run([hub, "stamp", APP / "bundle"])
    run([hub, "check", APP / "bundle", "--allow-unsigned"])
    if args.check or args.build:
        return
    env = os.environ.copy()
    if args.hidden:
        env["MAKEPAD_HIDE_WINDOWS"] = "1"
    else:
        env.pop("MAKEPAD_HIDE_WINDOWS", None)
    if args.remote:
        env["MAKEPAD_REMOTE"] = str(args.remote)
    if args.standalone:
        command = [host, "--bundle", APP / "bundle", "--allow-unsigned",
                   "--app-data", args.app_data or STATE / "standalone", "--size", args.size]
    else:
        profile = (args.app_data or STATE).resolve()
        mirror, data, anchor = local_install(hub, installer, args.prepare_local_test, profile)
        env.update(OCTOSENSE_HUB=str(mirror), OCTOSENSE_HUB_ANCHOR=anchor,
                   OCTOSENSE_APP_DATA=str(data), OCTOSENSE_HOME=str(profile / "desktop-home"))
        desktop = ROOT / "target/release" / ("octosense" + EXE)
        command_build = ["cargo", "build", "--release", "--locked", "-p", "octosense"]
        if args.offline:
            command_build.append("--offline")
        run(command_build, cwd=ROOT)
        command = [desktop, "--test-action", "launch-hub:pantry-steward"]
    run(command, cwd=ROOT, env=env)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as problem:
        print(f"启动失败：{problem}", file=sys.stderr)
        sys.exit(1)
