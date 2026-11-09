"""Build release URLs from a dependency name, version, and native architecture."""


def tool_url(name, version, architecture):
    numeric = version.removeprefix("v")
    architecture = architecture.lower()
    if architecture not in ("amd64", "arm64"):
        raise ValueError("unsupported architecture: " + architecture)
    rust_arch = {"amd64": "x86_64", "arm64": "aarch64"}[architecture]
    if name in ("grype", "grant"):
        return (
            f"https://github.com/anchore/{name}/releases/download/v{numeric}/"
            f"{name}_{numeric}_linux_{architecture}.tar.gz"
        )
    templates = {
        "cargo-about": (
            "https://github.com/EmbarkStudios/cargo-about/releases/download/"
            f"{numeric}/cargo-about-{numeric}-{rust_arch}-unknown-linux-musl.tar.gz"
        ),
        "cosign": (
            "https://github.com/sigstore/cosign/releases/download/v{version}/"
            "cosign-linux-{architecture}"
        ),
        "actionlint": (
            "https://github.com/rhysd/actionlint/releases/download/v{version}/"
            "actionlint_{numeric}_linux_{architecture}.tar.gz"
        ),
        "rustup": (
            "https://static.rust-lang.org/rustup/archive/{numeric}/"
            "{rust_arch}-unknown-linux-gnu/rustup-init"
        ),
    }
    try:
        template = templates[name]
    except KeyError as error:
        raise ValueError("unsupported tool: " + name) from error
    return template.format(
        version=numeric,
        numeric=numeric,
        architecture=architecture,
        rust_arch=rust_arch,
    )
