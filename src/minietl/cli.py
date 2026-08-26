from pathlib import Path
from typing import Any

import typer
import yaml

from minietl.core import Pipeline, Sink, Source
from minietl.sinks import CsvSink, StdoutSink
from minietl.sources import CsvSource, JsonlSource

app = typer.Typer(help="Mini-ETL CLI Runner")


@app.command()
def run(
    config: Path = typer.Option(
        ..., "--config", "-c", help="Pipeline YAML yapılandırma dosyası"
    ),
) -> None:
    """Belirtilen YAML dosyasına göre ETL pipeline'ını çalıştırır."""
    if not config.exists():
        typer.secho(
            f"Hata: Yapılandırma dosyası bulunamadı: {config}",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    with open(config, encoding="utf-8") as f:
        cfg: dict[str, Any] = yaml.safe_load(f)

    # Source yükleme (Protocol tipi ile polimorfik)
    src_cfg: dict[str, Any] = cfg.get("source", {})
    src_type = src_cfg.get("type")
    src_path = src_cfg.get("path", "")
    source: Source[dict[str, Any]]

    if src_type == "csv":
        source = CsvSource(src_path)
    elif src_type == "jsonl":
        source = JsonlSource(src_path)
    else:
        typer.secho(f"Desteklenmeyen source tipi: {src_type}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Sink yükleme (Protocol listesi)
    sink_cfg: dict[str, Any] = cfg.get("sink", {})
    sink_type = sink_cfg.get("type")
    sinks: list[Sink[dict[str, Any]]] = []

    if sink_type == "stdout":
        sinks.append(StdoutSink())
    elif sink_type == "csv":
        sinks.append(CsvSink(sink_cfg["path"], fieldnames=sink_cfg.get("fields", [])))

    pipeline: Pipeline[dict[str, Any], dict[str, Any]] = Pipeline(
        source=source, sinks=sinks
    )
    metrics = pipeline.run()

    typer.secho("\n--- Pipeline Tamamlandı ---", fg=typer.colors.GREEN)
    typer.echo(f"Okunan: {metrics.read_count}")
    typer.echo(f"Yazılan: {metrics.written_count}")
    typer.echo(f"Hatalı: {metrics.error_count}")
    typer.echo(f"Süre: {metrics.duration_seconds:.4f} sn")


if __name__ == "__main__":
    app()
